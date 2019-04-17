from pathlib import Path
import os
import json


class ConfigHandler:
    """
    ConfigHandler is intended to be used as class and not instantiated. Config-Variables are imported directly
    from the ConfigHandler-Class.
    """
    ROOT_DIR = Path(__file__).parent.parent.parent
    CONFIG_PATH = os.path.join(ROOT_DIR, 'config.json')
    DRIVER_PATH = os.path.join(ROOT_DIR, 'webdriver', "chromedriver.exe")
    DRIVER_TYPE = "chrome"

    POSTING_RETENTION_IN_DAYS = 30

    TEMPLATE_HTML_PATH = os.path.join(ROOT_DIR, "resources", "result_template.html")
    RESULT_HTML_PATH = os.path.join(ROOT_DIR, "result.html")
    RESULT_HTML_FILE_NAME = "result.html"

    STOPWORDS = []
    search_types_and_urls = {}
    search_topics = set([])

    header = f"---- # (ConfigHandler)"

    VERBOSE_SETTING = False

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
            cls.DRIVER_PATH = os.path.join(cls.ROOT_DIR, 'webdriver', config_json['DRIVER_EXE_NAME'])

        except KeyError:
            raise ValueError(f'{cls.header}: ERROR: Could not find "DRIVER_EXE_NAME" in config.json! Please add'
                             f'the name of the webdriver-exe-File to config.json. '
                             f'Example: "DRIVER_EXE_NAME": "webdriver.exe"')

        driver_name = config_json['DRIVER_EXE_NAME'].lower()

        if 'chrome' in driver_name:
            ConfigHandler.DRIVER_TYPE = 'chrome'
        elif 'gecko' in driver_name:
            ConfigHandler.DRIVER_TYPE = 'firefox'
        else:
            raise ValueError(f'{cls.header}: Could not recognize the webdriver-type. If you use Chrome, please make '
                             f'sure that the word chrome is contained in the webdriver name. If you use Firefox'
                             f'please make sure, that the word "gecko" is contained in the webdriver name.')

        if not os.path.isfile(cls.DRIVER_PATH):
            raise ValueError(f"{cls.header}: ERROR: Could not locate webdriver-file. Please check if the necessary "
                             f"webdriver.exe-File exists, that the name is correctly defined in config.json and that "
                             f"it is located in the webdriver-folder {cls.ROOT_DIR}.")

        try:
            cls.STOPWORDS = config_json['STOPWORDS']

            if not cls.STOPWORDS:
                print(f"{cls.header}: INFO: No Stopwords defined in config.json!")

        except KeyError:
            raise ValueError(f'{cls.header}: ERROR: Could not find "STOPWORDS" in config.json! Please add'
                             f'the key with a list of Stopwords to apply. If you do not want to apply any '
                             f'Stopwords just add an empty list to config.json. Example: "STOPWORDS"": []')

        if type(cls.STOPWORDS) != list:
            raise ValueError(f'{cls.header}: ERROR: Invalid "STOPWORDS" in config.json! Please specify the stopwords '
                             f'as a list of Strings. Example: "STOPWORDS": ["expert", "internship"]')
        else:
            if len(cls.STOPWORDS) > 0:
                if type(cls.STOPWORDS[0]) != str:
                    raise ValueError(f'{cls.header}: ERROR: Invalid "STOPWORDS" in config.json! Please specify the '
                                     f'stopwords as a list of Strings. Example: "STOPWORDS": ["expert", "internship"]')

        try:
            retention_days = config_json['POSTING_RETENTION_IN_DAYS']

            if retention_days == 'disabled':
                ConfigHandler.POSTING_RETENTION_IN_DAYS = None
                print(f'{cls.header}: INFO: Auto-deletion is disabled.')

            elif type(retention_days) != int:
                raise ValueError(f'{cls.header}: Value provided in config.json for the key "POSTING_RETENTION_IN_DAYS"'
                                 f'is not an integer! Please provide an integer value. Example. '
                                 f'"POSTING_RETENTION_IN_DAYS": 14')

        except KeyError:
            print(f'{cls.header}: INFO: Key "POSTING_RETENTION_IN_DAYS" not found in config.json-file. Using the '
                  f"default value of {cls.POSTING_RETENTION_IN_DAYS}-days retention. "
                  f"All job-postings older than this default value will be deleted.")

        print(f"{cls.header}: Base-Variables successfully parsed.")

    @classmethod
    def validate_search_topics(cls, platform_registry):
        """
        Load the config.json-file, parse the values inside of the main 'PLATFORMS'-Key. Check that each platform is
        implemented in this software through the platform-registry. Add every search-topic-ulr-pair to the main
        search-dict.
        :param platform_registry: PlatformRegistry-Singleton
        :return: None
        """
        if not platform_registry.registered_platforms:
            raise ValueError(f"{cls.header}: ERROR: No platforms have been registered. Please register at least"
                             f"one platform first.")

        with open(cls.CONFIG_PATH, 'r') as config_file:
            config_json = json.loads(config_file.read())

            # For every platform-key, check if it registered aka implemented
            config_platform_section = config_json['PLATFORMS']
            for platform in config_platform_section.keys():
                registered_platform_names = list(platform_registry.registered_platforms.keys())
                if platform not in registered_platform_names:
                    msg = f"{cls.header}: ERROR: A platform defined in the config.json is not implemented "\
                        f"in this version of this programme. Only add platforms that are supported"\
                        f"to config.json and make sure that you correctly spell the platform's name.\n"\
                        f"Invalid Platform: '{platform}'\n"\
                        f"The following platforms are available:"\

                    for pf in platform_registry.registered_platforms.keys():
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

    @classmethod
    def set_verbosity_level(cls, verbose: bool = False):
        cls.VERBOSE_SETTING = verbose
