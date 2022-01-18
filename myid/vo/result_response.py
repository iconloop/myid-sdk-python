from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ResultResponse:
    status: bool
    result: Any

    def __str__(self) -> str:
        return f'{{"status":{self.status},"result":"{self.get_result_string()}"}}'

    def get_result_string(self) -> Optional[str]:
        return str(self.result) if self.result else None

    def is_success(self) -> bool:
        return self.status
