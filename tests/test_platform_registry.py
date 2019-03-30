from Classes.DBHandlerClass import DBHandler, session_scope, Platform
from Classes.BrowserHandlerClass import BrowserHandler
from Classes.PlatformClasses.PlatformHandlerBaseClass import PlatformHandlerBase

from Classes.PlatformRegistryClass import PlatformRegistry
from Classes.PlatformClasses.KarriereATHandlerClass import KarriereATHandler
from Classes.PlatformClasses.StepStoneHandlerClass import StepStoneHandler

from tests.unittest_config import TEST_DB_PATH, TEST_DB_NAME

import unittest


class TestPlatformRegistryClass(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dbms = DBHandler(DBHandler.SQLITE, db_name=TEST_DB_NAME)
        cls.dbms.create_database_and_tables()

        browser_handler = BrowserHandler()
        cls.browser = browser_handler.get_browser()

        # Reset registered list (may be populated from other tests
        PlatformRegistry.de_register_all_platforms()

        PlatformRegistry.register_new_platform(KarriereATHandler)
        PlatformRegistry.register_new_platform(StepStoneHandler)

        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        # Reset registered list (may be populated from other tests
        PlatformRegistry.de_register_all_platforms()

        dbms = DBHandler(DBHandler.SQLITE, db_name=TEST_DB_NAME)

        with session_scope(dbms) as session:
            session.query(Platform).delete()

        super().tearDownClass()

    def test_create_platform_entries_in_database(self):
        print(PlatformRegistry.registered_platforms)
        PlatformRegistry.create_platform_entries_in_database(dbms=self.dbms)

        with session_scope(self.dbms) as session:
            platform_query_set = session.query(Platform).all()

            query_set_len = len(platform_query_set)
            self.assertEqual(query_set_len, 2)

            name_list = [entry.name for entry in platform_query_set]
            self.assertEqual(name_list, ["KARRIERE.AT", "STEPSTONE.AT"])
