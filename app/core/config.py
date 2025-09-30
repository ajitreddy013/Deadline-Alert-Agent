from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List


class Settings(BaseSettings):
    app_name: str = "Deadline Reminder"
    database_url: str = "sqlite:///./data/app.db"

    desktop_notifications_enabled: bool = True

    onesignal_enabled: bool = False
    onesignal_app_id: Optional[str] = None
    onesignal_rest_api_key: Optional[str] = None

    twilio_whatsapp_enabled: bool = False
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_whatsapp_from: Optional[str] = None

    whatsapp_headless: bool = False
    whatsapp_user_data_dir: str = "~/.deadline_reminder/whatsapp"

    default_reminder_offsets: List[int] = [-86400, 0]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)


settings = Settings()
