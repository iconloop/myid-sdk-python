import dataclasses
import json
from dataclasses import dataclass
from typing import List


@dataclass
class IssuedRegRequest:
    vcSig: str
    issuerDid: str
    holderDid: str
    issueDate: int = None
    expiryDate: int = None
    vcType: List[str] = None

    def to_string(self) -> str:
        return json.dumps(dataclasses.asdict(self))
