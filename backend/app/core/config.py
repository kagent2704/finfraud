from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "3306"))
    db_name: str = os.getenv("DB_NAME", "frauddb")
    db_user: str = os.getenv("DB_USER", "frauduser")
    db_password: str = os.getenv("DB_PASSWORD", "fraudpass")
    app_env: str = os.getenv("APP_ENV", "dev")
    app_port: int = int(os.getenv("APP_PORT", "8000"))
    ledger_hmac_key: str = os.getenv("LEDGER_HMAC_KEY", "")
    # auth
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


    @property
    def async_mysql_url(self) -> str:
        return (
            f"mysql+aiomysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

settings = Settings()

# --- DEBUG PRINTS ---
masked_pw = "*" * len(settings.db_password) if settings.db_password else "(empty)"
print(
    f"🔧 Loaded DB Config -> host={settings.db_host}, port={settings.db_port}, "
    f"user={settings.db_user}, password={masked_pw}, db={settings.db_name}"
)
print(f"🔧 Full async_mysql_url: {settings.async_mysql_url.replace(settings.db_password, '****')}")
