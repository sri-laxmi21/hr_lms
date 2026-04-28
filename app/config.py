import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from fastapi_mail import ConnectionConfig
from pydantic import EmailStr, ConfigDict

load_dotenv()

# -------------------------------
# AUTH CONFIGS
# -------------------------------
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

DEBUG = os.getenv("DEBUG", "False").lower() == "true"


# -------------------------------
# PYDANTIC SETTINGS (Pydantic v2)
# -------------------------------
class Settings(BaseSettings):

    # Database
    DATABASE_URL: str

    # Email
    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str
    EMAIL_FROM: EmailStr

    # S3 – Resume Bucket
    AWS_ACCESS_KEY_ID_RESUME: str
    AWS_SECRET_ACCESS_KEY_RESUME: str
    AWS_REGION_RESUME: str
    BUCKET_NAME_RESUME: str

    # S3 – LMS Video Bucket
    AWS_ACCESS_KEY_ID_VIDEO: str
    AWS_SECRET_ACCESS_KEY_VIDEO: str
    AWS_REGION_VIDEO: str
    AWS_S3_BUCKET_VIDEO: str
    
    # Payment Gateway Settings
    PAYMENT_GATEWAY: str = "razorpay"  # razorpay or stripe
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    RAZORPAY_WEBHOOK_SECRET: str = ""
    STRIPE_PUBLIC_KEY: str = ""
    STRIPE_SECRET_KEY: str = ""
    
    # Trial Period Settings
    TRIAL_PERIOD_DAYS: int = 14

    # ✔️ NEW: Pydantic v2 model config
    model_config = ConfigDict(
        env_file=".env",
        extra="allow"       # Allow additional keys
    )


settings = Settings()

# Email config
mail_conf = ConnectionConfig(
    MAIL_USERNAME=settings.EMAIL_USERNAME,
    MAIL_PASSWORD=settings.EMAIL_PASSWORD,
    MAIL_FROM=settings.EMAIL_FROM,
    MAIL_PORT=settings.EMAIL_PORT,
    MAIL_SERVER=settings.EMAIL_HOST,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)
 