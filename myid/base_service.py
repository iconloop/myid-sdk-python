import dataclasses
from typing import Any, Dict, Optional

from didsdk.document.document import Document
from didsdk.jwe.ecdhkey import ECDHKey
from didsdk.jwt.jwt import Jwt, VerifyResult
from didsdk.protocol.protocol_message import SignResult
from loguru import logger

from myid.core.api_path import APIPath
from myid.utils import HttpUtil
from myid.vo.did_request import DIDRequest
from myid.vo.result_response import ResultResponse
from myid.vo.vc_request import VCRequest


class BaseService:
    def __init__(self, url: str):
        self._url: str = url
        self._ecdh_keys: Dict[str, ECDHKey] = {}

    def add_ecdh_key(self, kid: str, key: ECDHKey):
        self._ecdh_keys[kid] = key

    def add_public_key(self, signed_jwt: str) -> Optional[Document]:
        jwt: Jwt = Jwt.decode(signed_jwt)
        request_url: str = self._url + APIPath.U_DID
        request: VCRequest = VCRequest(jwt=signed_jwt, nid=self.get_decimal_nid_from_did(jwt.header.kid), status=1)
        result_response: ResultResponse = HttpUtil.post(request_url, json=dataclasses.asdict(request))

        return Document.deserialize(result_response.result) if result_response.status else None

    def create_did(self, kid: str, publickey_base64: str, decimal_nid: str) -> Optional[Document]:
        request_url: str = self._url + APIPath.C_DID
        request: DIDRequest = DIDRequest(keyId=kid, nid=decimal_nid, publicKey=publickey_base64)
        result_response: ResultResponse = HttpUtil.post(url=request_url, json=dataclasses.asdict(request))

        return Document.deserialize(result_response.result) if result_response.status else None

    def delete_all_ecdh_key(self):
        self._ecdh_keys = {}

    def delete_ecdh_key(self, kid: str):
        del self._ecdh_keys[kid]

    def get_decimal_nid_from_did(self, did: str) -> str:
        hex_nid: str = did.split(":")[2]
        return str(int(hex_nid, 10))

    def get_did(self, did: str) -> Optional[Document]:
        request_url: str = self._url + APIPath.R_DID + did
        logger.debug(f"get_did: {request_url}")
        result_response: ResultResponse = HttpUtil.get(request_url)
        logger.debug(f"response: {result_response}")

        return Document.deserialize(result_response.result) if result_response.status else None

    def get_ecdh_key(self, kid: str) -> ECDHKey:
        return self._ecdh_keys.get(kid)

    def revoke_key(self, signed_jwt: str) -> Optional[Document]:
        jwt: Jwt = Jwt.decode(signed_jwt)
        request_url: str = self._url + APIPath.U_DID
        request: VCRequest = VCRequest(jwt=signed_jwt, nid=self.get_decimal_nid_from_did(jwt.header.kid), status=0)
        result_response: ResultResponse = HttpUtil.post(request_url, json=dataclasses.asdict(request))

        return Document.deserialize(result_response.result) if result_response.status else None


class ServiceResult:
    def __init__(self, success: bool, result: Any, signed_object: dict = None):
        self._success: bool = success
        self._signed_object: dict = signed_object
        self._result: Any = result
        self._fail_message: str = str(result) if not success and result else None

    @property
    def success(self) -> bool:
        return self._success

    @property
    def signed_object(self) -> dict:
        return self._signed_object

    @property
    def result(self):
        return self._result

    @property
    def fail_message(self) -> str:
        return self._fail_message

    @staticmethod
    def from_fail_message(message: str) -> "ServiceResult":
        return ServiceResult(success=False, result=message)

    @staticmethod
    def from_result(result: ResultResponse) -> "ServiceResult":
        return ServiceResult(success=result.status, result=result.result)

    @staticmethod
    def from_signed_object(signed_object: SignResult) -> "ServiceResult":
        return ServiceResult(
            success=signed_object.success, signed_object=signed_object.result, result=signed_object.fail_message
        )

    @staticmethod
    def from_verify_result(verify_result: VerifyResult) -> "ServiceResult":
        return ServiceResult(
            success=verify_result.success, result=None if verify_result.success else verify_result.fail_message
        )
