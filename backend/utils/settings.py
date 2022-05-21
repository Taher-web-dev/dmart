""" Application Settings """

import os
from pydantic import BaseSettings  # BaseModel,
from pathlib import Path


class Settings(BaseSettings):
    """ Main settings class """

    app_name: str = "datamart"
    log_path: Path = Path("./logs/")
    jwt_secret: str = ""
    jwt_algorithm: str = ""
    listening_host: str = "0.0.0.0"
    listening_port: int = 8282
    space_root : Path = Path("../space") 


    class Config:
        """ Load config """

        env_file = os.getenv('BACKEND_ENV', '.env')
        env_file_encoding = 'utf-8'


settings = Settings()

