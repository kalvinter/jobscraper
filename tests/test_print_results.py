from Classes.BrowserHandlerClass import BrowserHandler
from Classes.ResultPrinterClass import ResultPrinter
from Classes.DBHandlerClass import DBHandler, session_scope

from tests.unittest_config import TEST_DB_NAME
from tests.test_data.load_data_fixture_script import load_data_scripture

import unittest


class TestPrintDisplayHTMLResult(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dbms = DBHandler(DBHandler.SQLITE, db_name=TEST_DB_NAME)
        cls.dbms.create_database_and_tables()

        browser_handler = BrowserHandler()
        cls.browser = browser_handler.get_browser()

        cls.result_handler = ResultPrinter(dbms=cls.dbms, browser=cls.browser)

        # Load data fixture
        load_data_scripture(dbms=cls.dbms)

    def test_print_result_html(self):
        self.result_handler.print_result_to_html(seach_topic='Java', open_html_after_finish=True)


