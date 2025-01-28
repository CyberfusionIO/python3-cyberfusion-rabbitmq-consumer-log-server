from pydantic import (
    BaseSettings,
)


class Settings(BaseSettings):
    """Settings."""

    api_token: str = "change_me"
    gui_password: str = "change_me"
    database_path: str = "./rabbitmq-consumer-log-server.db"
    templates_directory: str = "templates"
    static_files_directory: str = "static"

    class Config:
        """Config."""

        secrets_dir = "/etc/rabbitmq-consumer-log-server"


settings = Settings()
