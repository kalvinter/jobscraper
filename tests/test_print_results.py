from Classes.UtilClasses.BrowserHandlerClass import BrowserHandler
from Classes.DisplayClasses.ResultPrinterClass import ResultPrinter
from Classes.UtilClasses.DBHandlerClass import DBHandler
from Classes.UtilClasses.PlatformRegistryClass import PlatformRegistry

from tests.unittest_config import TEST_DB_NAME
from tests.test_data.load_data_fixture_script import load_data_scripture

import unittest


class TestPrintDisplayHTMLResult(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dbms = DBHandler(DBHandler.SQLITE, db_name=TEST_DB_NAME)
        cls.dbms.create_database_and_tables()

        cls.browser_handler = BrowserHandler()
        cls.browser = cls.browser_handler.get_browser()
        cls.platform_registry = PlatformRegistry(browser=cls.browser, dbms=cls.dbms)
        cls.result_handler = ResultPrinter(dbms=cls.dbms, platform_registry=cls.platform_registry)

        # Load data fixture
        load_data_scripture(dbms=cls.dbms, platform_registry=cls.platform_registry)
        super().setUpClass()

        # Manually set scrape-status for all platforms loaded from data fixture
        for platform in cls.platform_registry.registered_platforms:
            platform_instance = cls.platform_registry.get_platform_instance(platform)
            platform_instance.scrape_status['Java'] = True

    @classmethod
    def tearDownClass(cls):
        try:
            # Try to close the browser after all tests have run
            cls.browser_handler.close_browser()

        except:
            pass

    def test_print_result_html(self):
        self.result_handler.print_result_to_html(seach_topic_list=['Java'], open_html_after_finish=True)


