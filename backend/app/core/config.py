from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "CertiCE Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "SUPER_SECRET_CERTICE_KEY_2026_COMPLIANCE_KEY"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    DATABASE_URL: str = "sqlite:///certice.db"

settings = Settings()
