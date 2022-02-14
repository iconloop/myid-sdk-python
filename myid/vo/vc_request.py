from dataclasses import dataclass


@dataclass
class VCRequest:
    jwt: str = None
    nid: str = None
    status: int = None
    sig: str = None

    def __str__(self) -> str:
        text: str = ''
        if self.jwt:
            text += f'"jwt":"{self.jwt}",'
        if self.nid:
            text += f'"nid":"{self.nid}",'
        if self.sig:
            text += f'"sig":"{self.sig}",'
        if self.status:
            text += f'"status":"{self.status}",'

        return f'{{{text[:-1]}}}'

    def to_query_param(self) -> str:
        query: str = '?'
        if self.jwt:
            query += f'jwt={self.jwt}&'
        if self.nid:
            query += f'nid={self.nid}&'
        if self.sig:
            query += f'sig={self.sig}&'
        if self.status:
            query += f'status="{self.status}&'

        return f'{query[:-1]}'
