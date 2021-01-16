import datetime
from dataclasses import dataclass


@dataclass
class ApacheLog:
    ip_address: str
    date: datetime
    method: str
    uri: str
    status_code: int
    size: int
