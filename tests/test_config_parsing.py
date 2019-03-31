from Classes.UtilClasses.ConfigHandlerClass import ConfigHandler
from Classes.UtilClasses.DBHandlerClass import DBHandler, session_scope
from Classes.UtilClasses.BrowserHandlerClass import BrowserHandler
from Classes.UtilClasses.PlatformRegistryClass import PlatformRegistry
from Classes.PlatformClasses.StepStoneHandlerClass import StepStoneHandler
from Classes.PlatformClasses.KarriereATHandlerClass import KarriereATHandler

from tests.unittest_config import TEST_DB_NAME

import unittest
import os


class TestConfigJSONParsing(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dbms = DBHandler(DBHandler.SQLITE, db_name=TEST_DB_NAME)

        cls.browser_handler = BrowserHandler()
        cls.browser = cls.browser_handler.get_browser()

        cls.platform_registry = PlatformRegistry(browser=cls.browser, dbms=cls.dbms)
        cls.platform_registry.register_new_platform(KarriereATHandler)
        cls.platform_registry.register_new_platform(StepStoneHandler)

    @classmethod
    def tearDownClass(cls):
        try:
            # Try to close the browser after all tests have run
            cls.browser_handler.close_browser()

        except:
            pass

    def test_successfull_parsing(self):
        """Test if a valid JSON is successfully parsed and config-variables set"""
        ConfigHandler.CONFIG_PATH = os.path.join(ConfigHandler.ROOT_DIR, 'tests', 'test_data',
                                                 'config_jsons', 'config_success.json')
        ConfigHandler.validate_config_file_base_variables()
        ConfigHandler.validate_search_topics(platform_registry=self.platform_registry)

    def test_no_retention_in_days_value(self):
        """Test if a missing "retention_in_days"-value causes the default value to be used"""
        initial_posting_retention_in_days_value = ConfigHandler.POSTING_RETENTION_IN_DAYS
        ConfigHandler.CONFIG_PATH = os.path.join(ConfigHandler.ROOT_DIR, 'tests', 'test_data',
                                                 'config_jsons', 'config_success.json')
        ConfigHandler.validate_config_file_base_variables()
        ConfigHandler.validate_search_topics(platform_registry=self.platform_registry)

        self.assertEqual(ConfigHandler.POSTING_RETENTION_IN_DAYS, initial_posting_retention_in_days_value)

    def test_parsing_disabled_retention_in_days(self):
        """Test if value of "disabled" disables auto-deletion"""
        ConfigHandler.CONFIG_PATH = os.path.join(ConfigHandler.ROOT_DIR, 'tests', 'test_data',
                                                 'config_jsons', 'config_disabled_retention_days.json')
        ConfigHandler.validate_config_file_base_variables()
        ConfigHandler.validate_search_topics(platform_registry=self.platform_registry)

        self.assertEqual(ConfigHandler.POSTING_RETENTION_IN_DAYS, None)

    def test_invalid_retention_in_days_value(self):
        """Test if an invalid "retention_in_days"-value throws a ValueError"""
        ConfigHandler.CONFIG_PATH = os.path.join(ConfigHandler.ROOT_DIR, 'tests', 'test_data',
                                                 'config_jsons', 'config_invalid_retention_days.json')
        error = False

        try:
            ConfigHandler.validate_config_file_base_variables()
            ConfigHandler.validate_search_topics(platform_registry=self.platform_registry)

        except ValueError:
            error = True

        self.assertTrue(error)

    def test_invalid_json(self):
        """Test if an invalid JSON throws a ValueError"""
        ConfigHandler.CONFIG_PATH = os.path.join(ConfigHandler.ROOT_DIR, 'tests', 'test_data',
                                                 'config_jsons', 'config_invalid_json.json')
        error = False

        try:
            ConfigHandler.validate_config_file_base_variables()
            ConfigHandler.validate_search_topics(platform_registry=self.platform_registry)

        except ValueError:
            error = True

        self.assertTrue(error)

    def test_invalid_webdriver_defined(self):
        """Test if an invalid Webdriver-Name (with which no exe can be found) causes a ValueError"""
        ConfigHandler.CONFIG_PATH = os.path.join(ConfigHandler.ROOT_DIR, 'tests', 'test_data',
                                                 'config_jsons', 'config_invalid_webdriver.json')
        error = False

        try:
            ConfigHandler.validate_config_file_base_variables()
            ConfigHandler.validate_search_topics(platform_registry=self.platform_registry)

        except ValueError:
            error = True

        self.assertTrue(error)

    def test_invalid_stopwords_defined(self):
        """ Test if an error is thrown when stopwords are not defined as a list of strings."""
        ConfigHandler.CONFIG_PATH = os.path.join(ConfigHandler.ROOT_DIR, 'tests', 'test_data',
                                                 'config_jsons', 'config_invalid_stopwords.json')
        error = False

        try:
            ConfigHandler.validate_config_file_base_variables()
            ConfigHandler.validate_search_topics(platform_registry=self.platform_registry)

        except ValueError:
            error = True

        self.assertTrue(error)

    def test_no_stopwords_defined(self):
        """ Test if an error is thrown when no stopword-key is present in config.json"""
        ConfigHandler.CONFIG_PATH = os.path.join(ConfigHandler.ROOT_DIR, 'tests', 'test_data',
                                                 'config_jsons', 'config_no_stopwords.json')
        error = False

        try:
            ConfigHandler.validate_config_file_base_variables()
            ConfigHandler.validate_search_topics(platform_registry=self.platform_registry)

        except ValueError:
            error = True

        self.assertTrue(error)

    def test_invalid_platform_defined(self):
        """ Test if an error is thrown, when a platform is entered in config.json which has not been registered in
        main.py"""
        ConfigHandler.CONFIG_PATH = os.path.join(ConfigHandler.ROOT_DIR, 'tests', 'test_data',
                                                 'config_jsons', 'config_invalid_platform.json')
        error = False

        try:
            ConfigHandler.validate_config_file_base_variables()
            ConfigHandler.validate_search_topics(platform_registry=self.platform_registry)

        except ValueError:
            error = True

        self.assertTrue(error)

    def test_no_platform_defined(self):
        """ Test if an error is thrown, when no PLATFORMS-key is present in config.json"""
        ConfigHandler.CONFIG_PATH = os.path.join(ConfigHandler.ROOT_DIR, 'tests', 'test_data',
                                                 'config_jsons', 'config_no_platforms.json')
        error = False

        try:
            ConfigHandler.validate_config_file_base_variables()
            ConfigHandler.validate_search_topics(platform_registry=self.platform_registry)

        except ValueError:
            error = True

        self.assertTrue(error)





