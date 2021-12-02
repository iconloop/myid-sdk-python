import time

from iconsdk.builder.call_builder import Call, CallBuilder
from iconsdk.builder.transaction_builder import CallTransaction, CallTransactionBuilder
from iconsdk.icon_service import IconService


class CredentialInfoScore:
    """access Credential info Score"""

    def __init__(self, icon_service: IconService, network_id: int, score_address: str):
        """Create CredentialInfoScore object.

        :param icon_service: the IconService object
        :param network_id: networkId the network ID of the blockchain
        :param score_address: the credentialInfo score address deployed to the blockchain
        """
        self._icon_service: IconService = icon_service
        self._network_id: int = network_id
        self._score_address: str = score_address

    def _build_transaction(self, from_address: str, method: str, params: dict) -> CallTransaction:
        timestamp = int(time.time() * 1_000_000)
        builder = CallTransactionBuilder(nid=self._network_id,
                                         from_=from_address,
                                         to=self._score_address,
                                         step_limit=5_000_000,
                                         timestamp=timestamp,
                                         method=method,
                                         params=params)
        return builder.build()

    def _build_call(self, method: str, params: dict = None) -> Call:
        builder = CallBuilder(to=self._score_address, method=method, params=params)
        return builder.build()

    def get(self, signature: str) -> str:
        params = {'sig': signature}
        call: Call = self._build_call(method='get', params=params)
        return self._icon_service.call(call)

    def get_reject_history(self, vc_id: str):
        params = {'vcId': vc_id}
        call: Call = self._build_call(method='getRejectHistory', params=params)
        return self._icon_service.call(call)

    def get_under_taker_list(self):
        call: Call = self._build_call(method='getUndertakerList')
        return self._icon_service.call(call)

    def is_valid(self, signature: str) -> str:
        params = {'sig': signature}
        call: Call = self._build_call(method='isValid', params=params)
        return self._icon_service.call(call)

    def jwt_method(self, from_address: str, jwt: str, method: str) -> CallTransaction:
        """send transaction for several purpose(add, revoke, revoke did, revoke vc and did) about the credential info

        :param from_address: the sender address that created the transaction
        :param jwt: credential info jwt
        :param method: score method (add, revoke, revokeDid, revokeVCAndDid)
        :return: Transaction object
        """
        params = {'credentialJwt': jwt}
        return self._build_transaction(from_address, method=method, params=params)

    def jwt_list_method(self, from_address: str, jwt_list: str, method: str) -> CallTransaction:
        """send transaction for several purpose(add, revoke, revoke did, revoke vc and did) about the credential info

        :param from_address: the sender address that created the transaction
        :param jwt_list: credential info jwt list
        :param method: score method (add, revoke, revokeDid, revokeVCAndDid)
        :return: Transaction object
        """
        params = {'credentialJwtList': jwt_list}
        return self._build_transaction(from_address, method=method, params=params)

    def reject_history_jwt_method(self, from_address: str, jwt: str, method: str) -> CallTransaction:
        """send transaction for rejection history about the credential info

        :param from_address: the sender address that created the transaction
        :param jwt: rejection credential info jwt
        :param method: score method (add, revoke, revokeDid, revokeVCAndDid)
        :return: Transaction object
        """
        params = {'rejectJwt': jwt}
        return self._build_transaction(from_address, method=method, params=params)
