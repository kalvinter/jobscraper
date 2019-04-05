from Classes.PlatformClasses.PlatformHandlerBaseClass import PlatformHandlerBase
from Classes.PlatformClasses.KarriereATHandlerClass import KarriereATHandler
from Classes.UtilClasses.BrowserHandlerClass import BrowserHandler
from Classes.UtilClasses.PlatformRegistryClass import PlatformRegistry
from Classes.UtilClasses.DBHandlerClass import DBHandler, session_scope, Platform, Vacancies
from Classes.UtilClasses.ConfigHandlerClass import ConfigHandler

from tests.unittest_config import TEST_DB_NAME
import unittest

from datetime import datetime


class TestPlatformHandlerBaseClassMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dbms = DBHandler(DBHandler.SQLITE, db_name=TEST_DB_NAME)
        cls.dbms.create_database_and_tables()
        cls.browser_handler = BrowserHandler()
        cls.browser = cls.browser_handler.get_browser()

        cls.platform_registry = PlatformRegistry(browser=cls.browser, dbms=cls.dbms)
        cls.platform_registry.register_new_platform(KarriereATHandler)

        # Create db entries for the registered platform
        cls.platform_registry.create_platform_entries_in_database()

        cls.karriere_at_handler = KarriereATHandler(browser=cls.browser, dbms=cls.dbms)

        cls.search_topic = "Python"
        cls.vacancy_entries = [
            {"platform": KarriereATHandler.platform_name, "company": "reynholm industries",
             "url": "https://www.reynholm.co.uk/", "title": "Head of Everything",
             "search_topic": cls.search_topic, "date": datetime(2019, 3, 30).date(), "location": "London"}
        ]

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
            session.query(Vacancies).delete()

        super().tearDownClass()

    def tearDown(self):
        with session_scope(self.dbms) as session:
            session.query(Vacancies).delete()

    def test_parse_dates_successful(self):
        date_testing_dict = {
            "2019-04-01": "2019-04-01",
            "01.04.2019": "2019-04-01",
            "2017-05-26T12:00": "2017-05-26",
            " 05.04.2019  | Vollzeit   ": "2019-04-05",
            "am 01.04.2019": '2019-04-01',
        }

        try:
            for raw_date, final_date in date_testing_dict.items():
                date = self.karriere_at_handler._parse_date(date_string=raw_date)
                self.assertEqual(str(date), final_date)

        except ValueError as e:
            raise

    def test_parse_dates_failure(self):
        error = False

        try:
            date = self.karriere_at_handler._parse_date(date_string="2019-Hello")

        except ValueError:
            error = True

        self.assertEqual(error, True)

    def test_title_filter_by_stopword_positive(self):
        """Test if, a title without one of the specified stopwords is correctly flagged as ok"""
        ConfigHandler.STOPWORDS = ["expert", "senior"]

        title_check = PlatformHandlerBase.apply_title_filter("lead programmer")
        self.assertEqual(title_check, True)

    def test_title_filter_by_stopword_negative(self):
        """Test if, a title with one of the specified stopwords is correctly flagged as not ok"""
        ConfigHandler.STOPWORDS = ["expert", "senior", "lead"]

        title_check = PlatformHandlerBase.apply_title_filter("lead programmer")
        self.assertEqual(title_check, False)

    def test_saving_a_vacancy_list_to_db(self):
        """ Test that the function _save_vacancy_entries_to_database correctly saves the list to db. """
        self.karriere_at_handler._save_vacancy_entries_to_database(vacancy_entries=self.vacancy_entries,
                                                                   search_topic=self.search_topic)

        with session_scope(dbms=self.dbms) as session:
            vacancy_entries_query_set = session.query(Vacancies).all()

            query_set_len = len(vacancy_entries_query_set)
            self.assertEqual(query_set_len, 1)

            columns = [m.key for m in Vacancies.__table__.columns]
            result_dict = {}

            # Create a dictionary from the result-query-set (except for the id-column)
            for column in columns:
                if column == 'id':
                    continue

                result_dict[column] = getattr(vacancy_entries_query_set[0], column)

            # Compare the result-dictionary with the originally send dictionary
            self.assertEqual(result_dict, self.vacancy_entries[0])

    def test_inserting_an_already_existing_vacancy(self):
        """ Test that a newly scraped entry is skipped when it already exists in the database """
        with session_scope(dbms=self.dbms) as session:
            session.add(Vacancies(**self.vacancy_entries[0]))

        with session_scope(dbms=self.dbms) as session:
            vacancy_entries_query_set = session.query(Vacancies).all()

            # Check that only 1 row exists
            query_set_len = len(vacancy_entries_query_set)
            self.assertEqual(query_set_len, 1)

        self.karriere_at_handler._save_vacancy_entries_to_database(vacancy_entries=self.vacancy_entries,
                                                                   search_topic=self.search_topic)

        with session_scope(dbms=self.dbms) as session:
            vacancy_entries_query_set = session.query(Vacancies).all()

            query_set_len = len(vacancy_entries_query_set)

            # Count() should stay 1
            self.assertEqual(query_set_len, 1)
