from pathlib import Path
import os
import json


class ConfigHandler:
    """
    ConfigHandler is intended to be used as class and not instantiated. Config-Variables are imported directly
    from the ConfigHandler-Class.
    """
    ROOT_DIR = Path(__file__).parent.parent
    CONFIG_PATH = os.path.join(ROOT_DIR, 'config.json')
    DRIVER_PATH = os.path.join(ROOT_DIR, "chromedriver.exe")
    RESULT_HTML_PATH = os.path.join(ROOT_DIR, "result.html")
    RESULT_HTML_FILE_NAME = "result.html"

    STOPWORDS = []
    search_types_and_urls = {}

    header = f"---- # (ConfigHandler)"

    @classmethod
    def validate_config_file(cls):
        """
        Load the config-json-file, parse it and set base-config-variables for the programme.
        :return:
        """
        with open(cls.CONFIG_PATH, 'r') as config_file:
            try:
                config_json = json.loads(config_file.read())

            except json.JSONDecodeError:
                msg = f"{cls.header}: ERROR: Was unable to parse Config-JSON-File. Please check the File's syntax!"
                raise ValueError(msg)

        cls.DRIVER_PATH = os.path.join(cls.ROOT_DIR, config_json['DRIVER_EXE_NAME'])
        cls.STOPWORDS = config_json['STOPWORDS']
        cls.search_types_and_urls = config_json['SEARCH_TOPICS']

        print(f"{cls.header}: Config successfully parsed.")

