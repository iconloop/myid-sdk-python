from didsdk.core.did_key_holder import DidKeyHolder
from didsdk.jwt.elements import Header, Payload
from didsdk.jwt.jwt import Jwt

from myid.core.property_name import PropertyName
from myid.credential.revoke_credential_info import RevokeCredentialInfo


class RevokeCredentialInfoScoreParameter:
    @staticmethod
    def revoke_credential_info_param(did_key_holder: DidKeyHolder, revoke_credential_info: RevokeCredentialInfo):
        header: Header = Header(alg=did_key_holder.type.name, kid=did_key_holder.kid)

        contents = {
            PropertyName.CREDENTIAL_INFO_ISSUER_DID: revoke_credential_info.issuer_did,
            PropertyName.CREDENTIAL_INFO_SIGNATURE: revoke_credential_info.signature,
            PropertyName.CREDENTIAL_INFO_REVOKE_DATE: (
                revoke_credential_info.revoke_date if revoke_credential_info.revoke_date else 0
            ),
        }
        payload: Payload = Payload(contents=contents)

        return Jwt(header=header, payload=payload)
