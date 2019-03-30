from Classes.PlatformRegistryClass import PlatformRegistry
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
    TEMPLATE_HTML_PATH = os.path.join(ROOT_DIR, "resources", "result_template.html")
    RESULT_HTML_PATH = os.path.join(ROOT_DIR, "result.html")
    RESULT_HTML_FILE_NAME = "result.html"

    STOPWORDS = []
    search_types_and_urls = {}
    search_topics = set([])

    header = f"---- # (ConfigHandler)"

    @classmethod
    def validate_config_file_base_variables(cls):
        """
        Load the config-json-file, parse and set the base variables for the programme.
        :return: None
        """
        with open(cls.CONFIG_PATH, 'r') as config_file:
            try:
                config_json = json.loads(config_file.read())

            except json.JSONDecodeError:
                msg = f"{cls.header}: ERROR: Was unable to parse Config-JSON-File. Please check the File's syntax!" \
                    f"You can copy your config-files content into the following web-tools to check it for " \
                    f"syntax-errors: https://jsonlint.com/"
                raise ValueError(msg)

        try:
            cls.DRIVER_PATH = os.path.join(cls.ROOT_DIR, config_json['DRIVER_EXE_NAME'])
        except KeyError:
            raise ValueError(f'{cls.header}: ERROR: Could not find "DRIVER_EXE_NAME" in config.json! Please add'
                             f'the name of the webdriver-exe-File to config.json. '
                             f'Example: "DRIVER_EXE_NAME": "webdriver.exe"')

        if not os.path.isfile(cls.DRIVER_PATH):
            raise ValueError(f"{cls.header}: ERROR: Could not locate webdriver-file. Please check if the necessary "
                             f"webdriver.exe-File exists, that the name is correctly defined in config.json and that "
                             f"it is located in the programmes root-directory {cls.ROOT_DIR}.")

        try:
            cls.STOPWORDS = config_json['STOPWORDS']

            if not cls.STOPWORDS:
                print(f"{cls.header}: INFO: No Stopwords defined in config.json!")

        except KeyError:
            raise ValueError(f'{cls.header}: ERROR: Could not find "STOPWORDS" in config.json! Please add'
                             f'the key with a list of Stopwords to apply. If you do not want to apply any '
                             f'Stopwords just add an empty list to config.json. Example: "STOPWORDS"": []')

        print(f"{cls.header}: Base-Variables successfully parsed.")

    @classmethod
    def validate_search_topics(cls):
        """
        Loag the config.json-file, parse the values inside of the main 'PLATFORMS'-Key. Check that each platform is
        implemented in this software through the platform-registry. Add every search-topic-ulr-pair to the main
        search-dict.
        :param platform_registry: PlatformRegistry-Singleton
        :return: None
        """
        if not PlatformRegistry.registered_platforms:
            raise ValueError(f"{cls.header}: ERROR: No platforms have been registered. Please register at least"
                             f"one platform first.")

        with open(cls.CONFIG_PATH, 'r') as config_file:
            config_json = json.loads(config_file.read())

            # For every platform-key, check if it registered aka implemented
            config_platform_section = config_json['PLATFORMS']
            for platform in config_platform_section.keys():
                registered_platform_names = list(PlatformRegistry.registered_platforms.keys())
                if platform not in registered_platform_names:
                    msg = f"{cls.header}: ERROR: A platform defined in the config.json is not implemented "\
                        f"in this version of this programme. Only add platforms that are supported"\
                        f"to config.json and make sure that you correctly spell the platform's name.\n"\
                        f"Invalid Platform: '{platform}'\n"\
                        f"The following platforms are available:"\

                    for pf in PlatformRegistry.registered_platforms.keys():
                        msg += f'\n{pf}'
                    raise ValueError(msg)

                else:
                    # If it is registered check if a search-topic and URL is defined
                    if len(config_platform_section[platform].keys()) > 0:

                        for search_topic in config_platform_section[platform].keys():
                            # If everything passes, add it to the main search dict
                            cls.search_types_and_urls[platform] = {
                                search_topic: config_platform_section[platform][search_topic]
                            }
                            cls.search_topics.add(search_topic)

        print(f"{cls.header}: Search-Topic and Platform-Variables successfully parsed.")