"""Config parser for secure settings (database)."""

import os
import yaml

APP_DIR = os.path.dirname(os.path.abspath(__file__))


class AppConfig:
    """Class for parsing app settings from config file (secure settings)."""
    def __init__(self):
        db_config_filename = os.path.join(APP_DIR, 'app.yaml')
        if os.path.isfile(db_config_filename):
            try:
                with open(db_config_filename, 'r') as file:
                    self.data = yaml.safe_load(file)
            except Exception as e:
                raise Exception("There is some problem with "
                                "your database config file. "
                                "Run setup.py again. "
                                "Error: {}".format(e))
        else:
            raise Exception("You haven't setup this app."
                            "Please, run setup.py")

    @property
    def db_host(self) -> str:
        return self.data['host']

    @property
    def db_port(self) -> int:
        return self.data['port']

    @property
    def db_user(self) -> str:
        return self.data['user']

    @property
    def db_password(self) -> str:
        return self.data['password']
