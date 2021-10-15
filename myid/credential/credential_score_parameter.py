from didsdk.core.did_key_holder import DidKeyHolder
from didsdk.jwt.elements import Header, Payload
from didsdk.jwt.jwt import Jwt

from myid.core.property_name import PropertyName
from myid.credential.credential_info import CredentialInfo


class CredentialInfoScoreParameter:
    @staticmethod
    def credential_info_param(did_key_holder: DidKeyHolder, credential_info: CredentialInfo):
        header: Header = Header(alg=did_key_holder.type.name, kid=did_key_holder.kid)

        contents = {
            PropertyName.CREDENTIAL_INFO_ISSUER_DID: credential_info.issuer_did,
            PropertyName.CREDENTIAL_INFO_SIGNATURE: credential_info.signature,
            PropertyName.CREDENTIAL_INFO_ISSUE_DATE: credential_info.issue_date if credential_info.issue_date else 0,
            PropertyName.CREDENTIAL_INFO_REVOKE_DATE: credential_info.revoke_date if credential_info.revoke_date else 0,
            PropertyName.CREDENTIAL_INFO_EXPIRY_DATE: credential_info.expiry_date if credential_info.expiry_date else 0,
        }

        if credential_info.holder_did:
            contents[PropertyName.CREDENTIAL_INFO_HOLDER_DID] = credential_info.holder_did
        payload: Payload = Payload(contents=contents)

        return Jwt(header=header, payload=payload)
