from myid.core.property_name import PropertyName


class CredentialInfo:
    """Represents a credential info"""

    def __init__(self, type_: str,
                 issuer_did: str,
                 signature: str,
                 is_revoke: bool = False,
                 holder_did: str = None,
                 issue_date: int = None,
                 revoke_date: int = None,
                 expiry_date: int = None,
                 creation_block: int = None,
                 revocation_block: int = None):
        """create credential info object
        :param type_: a string CredentialInfo type
        :param issuer_did: a string issuer DID
        :param holder_did: a string holder DID
        :param signature: a string credential signature
        :param is_revoke: isRevoke
        :param issue_date: credential issued date
        :param revoke_date: credential revoked date
        :param expiry_date: credential expired date
        :param creation_block: Block Height With issued Credential on blockchain
        :param revocation_block: Block Height With revoked Credential on blockchain
        """
        if type_ == PropertyName.CREDENTIAL_INFO_TYPE_REGIST:
            if not issue_date:
                raise ValueError('issue_date cannot be None.')
            if not expiry_date:
                raise ValueError('expiry_date cannot be None.')

        if type_ == PropertyName.CREDENTIAL_INFO_TYPE_REVOKE and not revoke_date:
            raise ValueError('revoke_date cannot be None.')

        self._type: str = type_
        self._issuer_did: str = issuer_did
        self._holder_did: str = holder_did
        self._signature: str = signature
        self._is_revoke: bool = is_revoke
        self._creation_block: int = creation_block
        self._revocation_block: int = revocation_block
        self._issue_date: int = issue_date
        self._revoke_date: int = revoke_date
        self._expiry_date: int = expiry_date

    @property
    def type(self) -> str:
        return self._type

    @property
    def issuer_did(self) -> str:
        return self._issuer_did

    @property
    def holder_did(self) -> str:
        return self._holder_did

    @property
    def signature(self) -> str:
        return self._signature

    @property
    def is_revoke(self) -> bool:
        return self._is_revoke

    @property
    def creation_block(self) -> int:
        return self._creation_block

    @property
    def revocation_block(self) -> int:
        return self._revocation_block

    @property
    def issue_date(self) -> int:
        return self._issue_date

    @property
    def revoke_date(self) -> int:
        return self._revoke_date

    @property
    def expiry_date(self) -> int:
        return self._expiry_date

    def to_json(self) -> dict:
        return {
            'type': self._type,
            'issuerDid': self._issuer_did,
            'holderDid': self._holder_did,
            'sig': self._signature,
            'isRevoke': self._is_revoke,
            'issueDate': self._issue_date,
            'revokeDate': self._revoke_date,
            'expiryDate': self._expiry_date,
            'created': self._creation_block,
            'revoked': self._revocation_block
        }
