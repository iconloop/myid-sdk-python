from coincurve import PublicKey
from didsdk.core.did_key_holder import DidKeyHolder
from didsdk.credential import Credential
from didsdk.document.document import Document
from didsdk.document.publickey_property import PublicKeyProperty
from didsdk.exceptions import JweException
from didsdk.jwe.ecdhkey import ECDHKey
from didsdk.jwt.jwt import VerifyResult
from didsdk.presentation import Presentation
from didsdk.protocol.protocol_message import ProtocolMessage, SignResult
from didsdk.protocol.protocol_type import ProtocolType
from jwcrypto.jwe import JWE

from myid.base_service import BaseService, ServiceResult
from myid.core.api_path import APIPath
from myid.utils import HttpUtil
from myid.vo.result_response import ResultResponse
from myid.vo.vc_request import VCRequest


class VerifierService(BaseService):
    def __init__(self, url: str):
        super().__init__(url=url)

    def _decrypt(self, protocol_message: ProtocolMessage):
        kid: str = protocol_message.jwe_kid
        ecdh_key: ECDHKey = self._ecdh_keys.get(kid)
        if not ecdh_key:
            raise JweException(f"Not exist ECDHKey kid({kid})")

        protocol_message.decrypt_jwe(ecdh_key)

    def _verified_credential_result(self, credential: Credential, holder_did: str) -> ServiceResult:
        issuer_document: Document = self.get_did(credential.did)
        issuer_key_property: PublicKeyProperty = issuer_document.get_public_key_property(credential.key_id)
        if issuer_key_property.is_revoked():
            return ServiceResult.from_fail_message("The Issuer's did is revoked.")

        issuer_public_key: PublicKey = issuer_key_property.public_key
        credential_verify_result: VerifyResult = credential.jwt.verify(issuer_public_key)
        if not credential_verify_result.success:
            return ServiceResult.from_verify_result(credential_verify_result)

        if holder_did != credential.target_did:
            return ServiceResult.from_fail_message("The Holder's did is not matched with target did.")

        request: VCRequest = VCRequest(nid=self.get_decimal_nid_from_did(credential.did), sig=credential.jwt.signature)
        request_url: str = self._url + APIPath.IS_VALID_VC + request.to_query_param()
        result_response: ResultResponse = HttpUtil.get(request_url)

        return ServiceResult.from_result(result_response)

    @staticmethod
    def create(url: str) -> "VerifierService":
        """Create a `VerifierService` instance that can use methods for Verifier.

        :param url: A Verifier WAS endpoint
        :return: VerifierService instance
        """
        return VerifierService(url=url)

    def decrypt_presentation(self, jwe_token: str) -> Presentation:
        protocol_message: ProtocolMessage = ProtocolMessage.from_(
            type_=ProtocolType.RESPONSE_PROTECTED_PRESENTATION.value,
            message=JWE().deserialize(jwe_token),
            is_protected=True,
        )
        self._decrypt(protocol_message)

        return protocol_message.presentation

    def sign_encrypt_request_presentation(
        self, protocol_message: ProtocolMessage, verifier_key_holder: DidKeyHolder
    ) -> ServiceResult:
        result: SignResult = protocol_message.sign_encrypt(verifier_key_holder)
        return ServiceResult.from_signed_object(result)
