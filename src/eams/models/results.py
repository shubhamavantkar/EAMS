from dataclasses import dataclass


@dataclass
class SendResult:
    success: bool
    attempts: int
    error_message: str | None = None


@dataclass
class HealthStatus:
    module: str
    is_healthy: bool
    details: str = ""
