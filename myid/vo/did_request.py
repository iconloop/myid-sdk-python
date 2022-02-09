from dataclasses import dataclass


@dataclass
class DIDRequest:
    keyId: str
    nid: str
    publicKey: str

    def __str__(self) -> str:
        text: str = ''
        if self.keyId:
            text += f'"keyId":"{self.keyId}",'
        if self.nid:
            text += f'"nid":"{self.nid}",'
        if self.publicKey:
            text += f'"publicKey":"{self.publicKey}",'

        return f'{{{text[:-1]}}}'
