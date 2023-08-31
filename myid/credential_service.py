import asyncio
import json
from typing import List

from didsdk.exceptions import TransactionException
from didsdk.jwt.jwt import Jwt
from iconsdk.builder.transaction_builder import Transaction
from iconsdk.exception import JSONRPCException
from iconsdk.icon_service import IconService
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.wallet.wallet import KeyWallet, Wallet
from loguru import logger

from myid.score.credential_info_score import CredentialInfoScore


class CredentialService:
    """This is the class for credential service that provides management (query, regist, revoke, etc.)."""

    def __init__(self, icon_service: IconService, network_id: int, score_address: str, timeout: int = 15_000):
        """Create the instance for using the blockchain.

        :param icon_service: the IconService object
        :param network_id: the network ID of the blockchain
        :param score_address: the credentialInfo score address deployed to the blockchain
        :param timeout: the specified timeout, in milliseconds.
        """
        self._icon_service: IconService = icon_service
        self._credential_score: CredentialInfoScore = CredentialInfoScore(self._icon_service, network_id, score_address)
        self._timeout: int = timeout

    async def _get_transaction_result(self, tx_hash: str) -> dict:
        """Get the transaction result that matches the hash of transaction.

        This method calls `iconsdk.icon_service.IconService.get_transaction_result` every 1 second
        until the transaction is confirmed.

        :param tx_hash:
        :return:
        """
        response = None
        retry_times = 5
        while response is None and retry_times > 0:
            try:
                tx_result = self._icon_service.get_transaction_result(tx_hash)
                if not tx_result:
                    raise JSONRPCException("transaction result is None.")
            except JSONRPCException as e:
                logger.debug(f"{e}")

                if retry_times == 0:
                    raise TransactionException(e)

                retry_times -= 1
                logger.debug(f"Remain to retry request for getting transaction result: {retry_times}")

                await asyncio.sleep(2)
                continue

            return tx_result

    async def _send_jwt(self, wallet: KeyWallet, signed_jwt: str, method: str) -> dict:
        """Sends a transaction with a json web token string.

        :param wallet: the wallet for transaction
        :param signed_jwt: the string that signed the object returned from `CredentialInfoScoreParameter`.
        :param method: the name of score function
        :return: the TransactionResult object
        """
        if not Jwt.decode(signed_jwt).signature:
            raise Exception("JWT string must contain signature to send a transaction.")

        transaction = self._credential_score.jwt_method(
            from_address=wallet.get_address(), jwt=signed_jwt, method=method
        )
        tx_hash: str = self._send_transaction(transaction, wallet)

        return await self._get_transaction_result(tx_hash)

    async def _send_jwt_list(self, wallet: KeyWallet, signed_jwt_list: List[str], method: str) -> dict:
        """Sends a transaction with a json web token list.

        :param wallet: the wallet for transaction
        :param signed_jwt_list: the string list that signed the object returned from `CredentialInfoScoreParameter`.
        :param method: the name of score function
        :return: the result of transaction
        """
        for jwt in signed_jwt_list:
            if not Jwt.decode(jwt).signature:
                raise Exception("JWT string must contain signature to send a transaction.")

        transaction = self._credential_score.jwt_method(
            from_address=wallet.get_address(), jwt=",".join(signed_jwt_list), method=method
        )
        tx_hash: str = self._send_transaction(transaction, wallet)

        return await self._get_transaction_result(tx_hash)

    async def _send_reject_history_jwt(self, wallet: KeyWallet, signed_jwt: str, method: str):
        """Sends a transaction with a json web token string about rejection history.

        :param wallet: the wallet for transaction
        :param signed_jwt: the string that signed the object returned from `CredentialInfoScoreParameter`.
        :param method: the name of score function
        :return: the TransactionResult object
        """
        if not Jwt.decode(signed_jwt).signature:
            raise Exception("JWT string must contain signature to send a transaction.")

        transaction = self._credential_score.reject_history_jwt_method(
            from_address=wallet.get_address(), jwt=signed_jwt, method=method
        )
        tx_hash: str = self._send_transaction(transaction, wallet)

        return await self._get_transaction_result(tx_hash)

    def _send_transaction(self, transaction: Transaction, wallet: Wallet) -> str:
        """Sends a transaction.

        :param transaction: the Transaction object.
        :param wallet: the wallet for transaction.
        :return: the hash of transaction.
        """
        signed_tx = SignedTransaction(transaction, wallet)
        return self._icon_service.send_transaction(signed_tx)

    def get(self, signature: str) -> dict:
        """get the Credential info that matches the issuer DID and credential signature.

        :param signature: the string that credential signature
        :return: the result of transaction
        """
        if not signature:
            raise ValueError("signature cannot be None.")

        return json.loads(self._credential_score.get(signature))

    def is_valid(self, signature: str) -> dict:
        """check validation of the Credential info that matches the issuer DID and credential signature.

        :param signature: the string that credential signature
        :return: status json
        """
        if not signature:
            raise ValueError("signature cannot be None.")

        return json.loads(self._credential_score.is_valid(signature))

    async def register(self, wallet: KeyWallet, signed_jwt: str) -> dict:
        """register the Credential info.

        :param wallet: the wallet for transaction
        :param signed_jwt: the string that signed the object returned by calling `CredentialInfoParam`
        :return: the result of transaction
        """
        return await self._send_jwt(wallet, signed_jwt, "register")

    async def register_credential_list(self, wallet: KeyWallet, signed_jwt: List[str]) -> dict:
        """register the Credential info list.

        :param wallet: the wallet for transaction
        :param signed_jwt: the string that signed the object returned by calling `CredentialInfoParam`
        :return: the result of transaction
        """
        return await self._send_jwt_list(wallet, signed_jwt, "registerList")

    async def revoke(self, wallet: KeyWallet, signed_jwt: str) -> dict:
        """revoke the Credential info.

        :param wallet: the wallet for transaction
        :param signed_jwt: the string that signed the object returned by calling `CredentialInfoParam`
        :return: the result of transaction
        """
        return await self._send_jwt(wallet, signed_jwt, "revoke")

    async def revoke_did(self, wallet: KeyWallet, signed_jwt: str) -> dict:
        """revoke the DID by Credential info.

        :param wallet: the wallet for transaction
        :param signed_jwt: the string that signed the object returned by calling `CredentialInfoParam`
        :return: the result of transaction
        """
        return await self._send_jwt(wallet, signed_jwt, "revokeDid")

    async def revoke_vc_and_did(self, wallet: KeyWallet, signed_jwt: str) -> dict:
        """revoke the VC and DID by Credential info.

        :param wallet: the wallet for transaction
        :param signed_jwt: the string that signed the object returned by calling `CredentialInfoParam`
        :return: the result of transaction
        """
        return await self._send_jwt(wallet, signed_jwt, "revokeVCAndDid")

    async def register_reject_history(self, wallet: KeyWallet, signed_jwt: str) -> dict:
        """register reject by Credential info.

        :param wallet: the wallet for transaction
        :param signed_jwt: the string that signed the object returned by calling `CredentialInfoParam`
        :return: the result of transaction
        """
        return await self._send_reject_history_jwt(wallet, signed_jwt, "registerRejectHistory")
