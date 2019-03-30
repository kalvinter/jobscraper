from Classes.ConfigHandlerClass import ConfigHandler
from Classes.PlatformRegistryClass import PlatformRegistry
from Classes.PlatformClasses.StepStoneHandlerClass import StepStoneHandler
from Classes.PlatformClasses.KarriereATHandlerClass import KarriereATHandler

import unittest
import os


class TestConfigJSONParsing(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        PlatformRegistry.register_new_platform(KarriereATHandler)
        PlatformRegistry.register_new_platform(StepStoneHandler)

    def test_successfull_parsing(self):
        ConfigHandler.CONFIG_PATH = os.path.join(ConfigHandler.ROOT_DIR, 'tests', 'test_data',
                                                 'config_jsons', 'config_success.json')
        ConfigHandler.validate_config_file_base_variables()
        ConfigHandler.validate_search_topics()

    def test_invalid_json(self):
        """Test if an invalid JSON throws a ValueError"""
        ConfigHandler.CONFIG_PATH = os.path.join(ConfigHandler.ROOT_DIR, 'tests', 'test_data',
                                                 'config_jsons', 'config_invalid_json.json')
        error = False

        try:
            ConfigHandler.validate_config_file_base_variables()
            ConfigHandler.validate_search_topics()

        except ValueError:
            error = True

        self.assertTrue(error)

    def test_invalid_webdriver_defined(self):
        """Test if an invalid Webdriver causes a ValueError"""
        ConfigHandler.CONFIG_PATH = os.path.join(ConfigHandler.ROOT_DIR, 'tests', 'test_data',
                                                 'config_jsons', 'config_invalid_webdriver.json')
        error = False

        try:
            ConfigHandler.validate_config_file_base_variables()
            ConfigHandler.validate_search_topics()

        except ValueError:
            error = True

        self.assertTrue(error)

    def test_no_stopwords_defined(self):
        ConfigHandler.CONFIG_PATH = os.path.join(ConfigHandler.ROOT_DIR, 'tests', 'test_data',
                                                 'config_jsons', 'config_invalid_stopwords.json')
        error = False

        try:
            ConfigHandler.validate_config_file_base_variables()
            ConfigHandler.validate_search_topics()

        except ValueError:
            error = True

        self.assertTrue(error)

    def test_invalid_platform_definied(self):
        ConfigHandler.CONFIG_PATH = os.path.join(ConfigHandler.ROOT_DIR, 'tests', 'test_data',
                                                 'config_jsons', 'config_invalid_platform.json')
        error = False

        try:
            ConfigHandler.validate_config_file_base_variables()
            ConfigHandler.validate_search_topics()

        except ValueError:
            error = True

        self.assertTrue(error)





