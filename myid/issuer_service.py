import dataclasses
import json
import time
from typing import Optional, List

from didsdk.core.did_key_holder import DidKeyHolder
from didsdk.core.property_name import PropertyName as DIDPropertyName
from didsdk.credential import Credential
from didsdk.jwt.elements import Payload
from didsdk.jwt.jwt import Jwt
from didsdk.protocol.claim_request import ClaimRequest
from didsdk.protocol.protocol_message import ProtocolMessage, SignResult
from didsdk.protocol.protocol_type import ProtocolType
from iconsdk.exception import JSONRPCException
from jwcrypto.jwe import JWE
from loguru import logger

from myid.base_service import BaseService, ServiceResult
from myid.core.api_path import APIPath
from myid.core.property_name import PropertyName
from myid.credential.credential_info import CredentialInfo
from myid.credential.credential_score_parameter import CredentialInfoScoreParameter
from myid.credential.revoke_credential_info import RevokeCredentialInfo
from myid.credential.revoke_score_parameter import RevokeCredentialInfoScoreParameter
from myid.utils import HttpUtil
from myid.vo.issued_register_request import IssuedRegRequest
from myid.vo.result_response import ResultResponse
from myid.vo.vc_request import VCRequest


class IssuerService(BaseService):
    """This class is implemented some methods for Issuer."""

    def __init__(self, url: str):
        super().__init__(url=url)

    @staticmethod
    def create(url: str) -> "IssuerService":
        """Create a `IssuerService` instance that can use methods for Issuer.

        :param url: A Issuer WAS endpoint
        :return: IssuerService instance
        """
        return IssuerService(url=url)

    def decode_protocol_message(self, message: str) -> ClaimRequest:
        protocol_message: ProtocolMessage = ProtocolMessage.from_json(json.loads(message))
        return protocol_message.claim_request

    def decode_request_credential(self, jwt_token: str) -> ClaimRequest:
        protocol_message: ProtocolMessage = ProtocolMessage.from_(
            ProtocolType.REQUEST_CREDENTIAL.value, JWE().deserialize(raw_jwe=jwt_token)
        )
        return protocol_message.claim_request

    def get_request(self, credential_info: CredentialInfo, key_holder: DidKeyHolder) -> VCRequest:
        revoke_jwt: Jwt = CredentialInfoScoreParameter.credential_info_param(
            did_key_holder=key_holder, credential_info=credential_info
        )
        return VCRequest(jwt=key_holder.sign(revoke_jwt), nid=self.get_decimal_nid_from_did(key_holder.did))

    def get_vc(self, issuer_did: str, signature: str) -> Optional[CredentialInfo]:
        request: VCRequest = VCRequest(nid=self.get_decimal_nid_from_did(issuer_did), sig=signature)
        request_url: str = self._url + APIPath.GET_VC + request.to_query_param()
        result_response: ResultResponse = HttpUtil.get(request_url)

        logger.debug(f"get_vc request: {request_url}")
        logger.debug(f"get_vc result: {result_response}")
        if result_response.status:
            return CredentialInfo.from_json(result_response.result)
        else:
            raise JSONRPCException(result_response.result)

    def register_vc(self, credential: Credential, issuer_key_holder: DidKeyHolder) -> ServiceResult:
        """Register a VC via myid Server.

        :param credential:
        :param issuer_key_holder:
        :return:
        """
        request_url: str = self._url + APIPath.REG_VC
        payload: Payload = credential.jwt.payload
        credential_info: CredentialInfo = CredentialInfo(
            type_=PropertyName.CREDENTIAL_INFO_TYPE_REGIST,
            issuer_did=credential.did,
            holder_did=credential.target_did,
            signature=credential.jwt.signature,
            issue_date=int(time.time()),
            expiry_date=payload.exp,
        )
        vc_request: VCRequest = self.get_request(credential_info=credential_info, key_holder=issuer_key_holder)
        result_response: ResultResponse = HttpUtil.post(url=request_url, json=dataclasses.asdict(vc_request))
        if result_response.status:
            types: List[str] = credential.vc.type
            types.remove(DIDPropertyName.JL_TYPE_VERIFIABLE_CREDENTIAL)
            issued_register_request: IssuedRegRequest = IssuedRegRequest(
                vcSig=credential.jwt.signature,
                vcType=[types[0]] if len(types) > 0 else None,
                issuerDid=payload.iss,
                holderDid=payload.sub,
                issueDate=payload.iat,
                expiryDate=payload.exp,
            )
            request_url = self._url + APIPath.ISS_VC_LOG
            HttpUtil.post(url=request_url, json=dataclasses.asdict(issued_register_request))

        return ServiceResult.from_result(result_response)

    def revoke_vc(self, credential: Credential, issuer_key_holder: DidKeyHolder) -> ServiceResult:
        return self.revoke_vc_with_signature(
            signature=credential.jwt.signature, issuer_did=credential.did, issuer_key_holder=issuer_key_holder
        )

    def revoke_vc_with_signature(
        self, signature: str, issuer_did: str, issuer_key_holder: DidKeyHolder
    ) -> ServiceResult:
        request_url: str = self._url + APIPath.REV_VC
        revoke_credential_info: RevokeCredentialInfo = RevokeCredentialInfo(
            type_=PropertyName.CREDENTIAL_INFO_TYPE_REVOKE,
            issuer_did=issuer_did,
            signature=signature,
            revoke_date=int(time.time()),
        )
        jwt: Jwt = RevokeCredentialInfoScoreParameter.revoke_credential_info_param(
            did_key_holder=issuer_key_holder, revoke_credential_info=revoke_credential_info
        )
        vc_request: VCRequest = VCRequest(
            jwt=issuer_key_holder.sign(jwt), nid=self.get_decimal_nid_from_did(issuer_key_holder.did)
        )
        result_response: ResultResponse = HttpUtil.post(url=request_url, json=dataclasses.asdict(vc_request))
        return ServiceResult.from_result(result_response)

    def sign_encrypt_credential(
        self, protocol_message: ProtocolMessage, issuer_key_holder: DidKeyHolder, kid: str
    ) -> ServiceResult:
        sign_result: SignResult = protocol_message.sign_encrypt(
            did_key_holder=issuer_key_holder, ecdh_key=self._ecdh_keys.get(kid)
        )
        if sign_result.success:
            credential: Credential = Credential.from_jwt(json.loads(protocol_message.message))
            self.register_vc(credential, issuer_key_holder)

        return ServiceResult.from_signed_object(sign_result)
