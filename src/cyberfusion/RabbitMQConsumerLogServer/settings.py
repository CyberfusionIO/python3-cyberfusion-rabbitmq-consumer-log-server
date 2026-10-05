from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings."""

    model_config = SettingsConfigDict(
        secrets_dir="/etc/rabbitmq-consumer-log-server",
        env_file=".env",
        extra="ignore",
    )

    api_token: str = "change_me"
    gui_password: str = "change_me"
    database_uri: str = "mysql+pymysql://rabbitmq-consumer-log-server:rabbitmq-consumer-log-server@127.0.0.1/rabbitmq-consumer-log-server"
    views_directory: str = "views"
    static_files_directory: str = "static"
    keep_days: int = 45


settings = Settings()
