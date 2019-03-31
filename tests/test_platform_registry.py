from Classes.UtilClasses.DBHandlerClass import DBHandler, session_scope, Platform
from Classes.UtilClasses.BrowserHandlerClass import BrowserHandler

from Classes.UtilClasses.PlatformRegistryClass import PlatformRegistry
from Classes.PlatformClasses.KarriereATHandlerClass import KarriereATHandler
from Classes.PlatformClasses.StepStoneHandlerClass import StepStoneHandler

from tests.unittest_config import TEST_DB_NAME

import unittest


class TestPlatformRegistryClass(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dbms = DBHandler(DBHandler.SQLITE, db_name=TEST_DB_NAME)
        cls.dbms.create_database_and_tables()

        cls.browser_handler = BrowserHandler()
        cls.browser = cls.browser_handler.get_browser()

        cls.platform_registry = PlatformRegistry(browser=cls.browser, dbms=cls.dbms)

        # Reset registered list (may be populated from other tests
        cls.platform_registry.de_register_all_platforms()

        cls.platform_registry.register_new_platform(KarriereATHandler)
        cls.platform_registry.register_new_platform(StepStoneHandler)

        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        try:
            # Try to close the browser after all tests have run
            cls.browser_handler.close_browser()

        except:
            pass

        # Reset Database, delete all platforms
        dbms = DBHandler(DBHandler.SQLITE, db_name=TEST_DB_NAME)

        with session_scope(dbms) as session:
            session.query(Platform).delete()

        super().tearDownClass()

    def test_singleton_restriction(self):
        """Test if PlatformRegistry can only be instantiated once"""
        second_platform_registry = PlatformRegistry(browser=self.browser, dbms=self.dbms)

        self.assertEqual(self.platform_registry, second_platform_registry)

    def test_registering_platforms_process(self):
        """ Test if a platform can be registered and fetched without error """
        # First deregister all platforms (clean state)
        self.platform_registry.de_register_all_platforms()

        # Register and instantiate a platform
        self.platform_registry.register_new_platform(KarriereATHandler)

        # Get the instantiated object without a key-error
        platform_instance = self.platform_registry.get_platform_instance(KarriereATHandler.platform_name)

        # Check if it is an instantiated object of KarriereATHandler.
        # If it would be just a class-reference the type would be ABC-MetaClass
        self.assertEqual(type(platform_instance), KarriereATHandler)

    def test_create_platform_entries_in_database(self):
        """ Test if the function creates a database entry for each registered platform """
        self.platform_registry.create_platform_entries_in_database()

        with session_scope(self.dbms) as session:
            platform_query_set = session.query(Platform).all()

            query_set_len = len(platform_query_set)
            self.assertEqual(query_set_len, 2)

            name_list = [entry.name for entry in platform_query_set]

            self.assertEqual(name_list, list(self.platform_registry.registered_platforms.keys()))
