class RevokeCredentialInfo:
    """Represents a credential info when revoke the vc"""

    def __init__(self, type_: str, issuer_did: str, signature: str, revoke_date: int):
        """create revoke credential info object

        :param type_: type of credential info
        :param issuer_did: the did of issuer
        :param signature: the credential signature
        :param revoke_date: the revoked date
        """
        self._type: str = type_
        self._issuer_did: str = issuer_did
        self._signature: str = signature
        self._revoke_date: int = revoke_date

    @property
    def type(self) -> str:
        return self._type

    @property
    def issuer_did(self) -> str:
        return self._issuer_did

    @property
    def signature(self) -> str:
        return self._signature

    @property
    def revoke_date(self) -> int:
        return self._revoke_date
