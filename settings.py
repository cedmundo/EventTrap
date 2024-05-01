from pydantic_settings import BaseSettings
from dotenv import load_dotenv


class Settings(BaseSettings):
    app_name: str = "EventTrap API"
    database_host: str
    database_port: int
    database_name: str
    database_username: str
    database_password: str
    database_timeout: int = 100
    database_pool_max_size: int = 1
    database_pool_min_size: int = 10


# Global configuration
load_dotenv()
settings = Settings()
