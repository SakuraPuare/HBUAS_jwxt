import pathlib

import yaml


class Config:
    def __init__(self, file_name: str = 'config.yaml') -> None:
        self.config = self.__read_config(pathlib.Path(file_name))
        self.account: dict = self.config.get("account")
        self.page: dict = self.config.get("page")

    @staticmethod
    def __read_config(file: pathlib.Path) -> dict:
        with open(file) as f:
            data = yaml.safe_load(f)
        return data
