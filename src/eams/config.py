from __future__ import annotations

from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="EAMS_", extra="ignore")

    mode: str = "development"
    endpoint_id: str = "endpoint-001"
    recipient_email: str

    smtp_host: str
    smtp_port: int = 587
    smtp_username: str
    smtp_password: str
    smtp_use_tls: bool = True

    storage_key: str
    data_dir: Path = Field(default=Path("./data"))

    report_hour: int = 18
    idle_threshold_seconds: int = 300
    poll_seconds: int = 5
    retention_days: int = 14


settings = Settings()
