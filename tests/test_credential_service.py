import os
import time

import pytest
from didsdk.core.did_key_holder import DidKeyHolder
from didsdk.core.key_store import DidKeyStore
from didsdk.jwt.elements import Header, Payload
from didsdk.jwt.jwt import Jwt
from iconsdk.wallet.wallet import KeyWallet

from myid.core.property_name import PropertyName
from myid.credential.credential_info import CredentialInfo
from myid.credential.credential_score_parameter import CredentialInfoScoreParameter
from myid.credential.revoke_credential_info import RevokeCredentialInfo
from myid.credential.revoke_score_parameter import RevokeCredentialInfoScoreParameter
from myid.credential_service import CredentialService
from tests.utils.icon_service_factory import IconServiceFactory


class TestCredentialService:
    @pytest.fixture
    def credential_service(self) -> CredentialService:
        return CredentialService(
            icon_service=IconServiceFactory.create_testnet(),
            network_id=2,
            score_address="cxeb26d9ecbfcf5fea0c2dcaf2f843d5ae93cbe84d",
        )

    @pytest.fixture
    def did_key_holder(self) -> DidKeyHolder:
        test_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
        return DidKeyStore.load_did_key_holder(f"{test_path}/test_did_key.json", "P@ssw0rd")

    @pytest.fixture
    def holder_did(self, did_key_holder) -> str:
        return did_key_holder.did

    @pytest.fixture
    def wallet(self, test_wallet_keys) -> KeyWallet:
        return KeyWallet.load(bytes.fromhex(test_wallet_keys["private"]))

    @pytest.mark.asyncio
    async def test_register_get_revoke(
        self, credential_service: CredentialService, did_key_holder: DidKeyHolder, wallet: KeyWallet
    ):
        # GIVEN data to register a VC
        issue_date: int = int(time.time())
        expiry_date: int = issue_date + (60 * 60 * 24)
        header: Header = Header(alg=did_key_holder.type.name, kid=did_key_holder.kid)
        contents: dict = {
            Payload.ISSUER: did_key_holder.did,
            Payload.ISSUED_AT: issue_date,
            Payload.EXPIRATION: expiry_date,
        }
        payload: Payload = Payload(contents)
        signed_jwt: str = did_key_holder.sign(Jwt(header, payload))
        signature: str = signed_jwt.split(".")[2]
        credential_info: CredentialInfo = CredentialInfo(
            type_=PropertyName.CREDENTIAL_INFO_TYPE_REGIST,
            issuer_did=did_key_holder.did,
            signature=signature,
            issue_date=issue_date,
            expiry_date=expiry_date,
        )
        jwt: Jwt = CredentialInfoScoreParameter.credential_info_param(did_key_holder, credential_info)

        # WHEN try to register a VC
        tx_result: dict = await credential_service.register(wallet, did_key_holder.sign(jwt))

        # THEN success to get status as success
        assert tx_result["status"] == 1

        # WHEN try to query a VC by signature
        tx_result = credential_service.get(signature)

        # THEN success
        assert tx_result["sig"] == signature

        # WHEN try to revoke a VC
        revoke_credential_info: RevokeCredentialInfo = RevokeCredentialInfo(
            type_=PropertyName.CREDENTIAL_INFO_TYPE_REVOKE,
            issuer_did=did_key_holder.did,
            signature=signature,
            revoke_date=int(time.time()),
        )
        revoke_jwt: Jwt = RevokeCredentialInfoScoreParameter.revoke_credential_info_param(
            did_key_holder, revoke_credential_info
        )
        # WHEN try to revoke a VC
        tx_result: dict = await credential_service.revoke(wallet, did_key_holder.sign(revoke_jwt))

        # THEN success to get status as success
        assert tx_result["status"] == 1
