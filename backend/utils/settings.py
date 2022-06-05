""" Application Settings """

import os
from pydantic import BaseSettings  # BaseModel,
from pathlib import Path


class Settings(BaseSettings):
    """Main settings class"""

    app_name: str = "dmart"
    log_path: Path = Path("./logs/")
    log_filename: str = "x-ljson.log"
    jwt_secret: str = ""
    jwt_algorithm: str = ""
    listening_host: str = "0.0.0.0"
    listening_port: int = 8282
    redis_host: str = "127.0.0.1"
    space_names: list[str] = []
    spaces_folder: Path = Path("../spaces/")

    class Config:
        """Load config"""

        env_file = os.getenv("BACKEND_ENV", ".env")
        env_file_encoding = "utf-8"


settings = Settings()
