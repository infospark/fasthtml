from dataclasses import dataclass


@dataclass
class Failure:
    message: str

    def __bool__(self) -> bool:
        return False
