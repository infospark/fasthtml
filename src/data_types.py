from dataclasses import dataclass
from datetime import datetime


@dataclass
class Failure:
    message: str

    def __bool__(self) -> bool:
        return False


@dataclass
class Success:
    message: str = ""

    def __bool__(self) -> bool:
        return True


@dataclass
class ManifestEntry:
    filename: str
    added_at: datetime
    size_bytes: int


@dataclass
class Manifest:
    entries: list[ManifestEntry]
