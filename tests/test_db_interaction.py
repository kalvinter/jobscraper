import unittest

from Classes.UtilClasses.PlatformRegistryClass import PlatformRegistry
from Classes.UtilClasses.BrowserHandlerClass import BrowserHandler
from Classes.UtilClasses.ConfigHandlerClass import ConfigHandler
from Classes.UtilClasses.DBHandlerClass import DBHandler, Vacancies, Platform, session_scope
from tests.unittest_config import TEST_DB_PATH, TEST_DB_NAME

from Classes.PlatformClasses.KarriereATHandlerClass import KarriereATHandler

import os
from datetime import datetime, timedelta


class TestDBCreation(unittest.TestCase):

    def test_database_creation(self):
        if os.path.isfile(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)
            self.assertEqual(os.path.isfile(TEST_DB_PATH), False)

        dbms = DBHandler(DBHandler.SQLITE, db_name=TEST_DB_NAME)
        dbms.create_database_and_tables()
        # Test if DB was created
        self.assertEqual(os.path.isfile(TEST_DB_PATH), True)

        # Test that all tables were created
        result = dbms.get_tables_in_database()
        self.assertEqual(result, [
            {"name": "platform"},
            {"name": "vacancies"}
        ])

        dbms.load_initial_data()
        with session_scope(dbms) as session:
            platform_data = session.query(Platform).all()
            self.assertEqual(len(platform_data), 1)
            platform_data_row = platform_data[0]
            self.assertEqual([platform_data_row.name, platform_data_row.base_address], ['karriere.at', 'www.karriere.at/'])

        os.remove(TEST_DB_PATH)
        self.assertEqual(os.path.isfile(TEST_DB_PATH), False)


class TestVacancyInteractions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dbms = DBHandler(DBHandler.SQLITE, db_name=TEST_DB_NAME)
        cls.dbms.create_database_and_tables()

        session = cls.dbms.get_session()
        cls.platform = Platform(name="test.at", base_address="www.test.at/")
        session.add(cls.platform)
        session.commit()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        dbms = DBHandler(DBHandler.SQLITE, db_name=TEST_DB_NAME)

        with session_scope(dbms) as session:
            session.query(Platform).delete()

    def tearDown(self):
        with session_scope(self.dbms) as session:
            session.query(Vacancies).delete()

    def test_insert_row_in_articles(self):
        with session_scope(self.dbms) as session:
            new_vacancy = Vacancies(platform=self.platform.name, date=datetime(2019, 1, 1), url="http://",
                                    title="title", company="aha", search_topic='Java', location="Wien")

            session.add(new_vacancy)
            session.flush()

        with session_scope(self.dbms) as session:
            vacancies_instances_list = session.query(Vacancies).all()

            self.assertEqual(len(vacancies_instances_list), 1)

            vacancies_instance = vacancies_instances_list[0]
            self.assertEqual([vacancies_instance.id, vacancies_instance.platform],
                             [1, 'test.at'])

    def test_auto_increment(self):
        with session_scope(self.dbms) as session:
            vacancy_list = [
                Vacancies(platform=self.platform.name, date=datetime(2019, 1, 2), url="http://",
                          title="title", company="aha", search_topic='Java', location="Wien"),
                Vacancies(platform=self.platform.name, date=datetime(2019, 1, 3), url="http://",
                          title="title", company="aha", search_topic='Java', location="Wien")
            ]

            for v in vacancy_list:
                session.add(v)
                session.flush()

        with session_scope(self.dbms) as session:
            vacancies_instances_list = session.query(Vacancies).all()

            id_list = [entry.id for entry in vacancies_instances_list]
            self.assertEqual(id_list, [1, 2])

            title_list = [entry.title for entry in vacancies_instances_list]
            self.assertEqual(title_list, ['title', 'title'])

    def test_auto_delete_postings_after_x_days(self):
        # Reset Value to 14 (might be None due to other tests)
        ConfigHandler.POSTING_RETENTION_IN_DAYS = 30

        today = datetime.now()
        very_old_post_date = today - timedelta(days=ConfigHandler.POSTING_RETENTION_IN_DAYS)

        with session_scope(self.dbms) as session:
            vacancy_list = [
                Vacancies(platform=self.platform.name, date=today, url="http://",
                          title="title", company="aha", search_topic='Java', location="Wien"),
                Vacancies(platform=self.platform.name, date=very_old_post_date, url="http://",
                          title="title", company="aha", search_topic='Java', location="Wien")
            ]

            for v in vacancy_list:
                session.add(v)

        self.dbms.cleanup_job_postings_in_database()

        with session_scope(self.dbms) as session:
            vacancies_instances_list = session.query(Vacancies).all()

            # Only one should be left
            self.assertEqual(len(vacancies_instances_list), 1)

            # Only the new posting should be left
            self.assertEqual(vacancies_instances_list[0].date, today.date())

    def test_disabled_retention_in_days(self):
        """Test if value of "disabled" disables auto-deletion"""
        # Reset Value to 14 (might be None due to other tests)
        ConfigHandler.POSTING_RETENTION_IN_DAYS = 30

        today = datetime.now()
        very_old_post_date = today - timedelta(days=ConfigHandler.POSTING_RETENTION_IN_DAYS)

        ConfigHandler.CONFIG_PATH = os.path.join(ConfigHandler.ROOT_DIR, 'tests', 'test_data',
                                                 'config_jsons', 'config_disabled_retention_days.json')
        ConfigHandler.validate_config_file_base_variables()

        browser_handler = BrowserHandler()
        browser = browser_handler.get_browser()

        platform_registry = PlatformRegistry(browser=browser, dbms=self.dbms)
        platform_registry.register_new_platform(KarriereATHandler)
        platform_registry.create_platform_entries_in_database()

        ConfigHandler.validate_search_topics(platform_registry=platform_registry)

        browser_handler.close_browser()

        # Check if Posting-retention-in-days was correctly set to None
        self.assertEqual(ConfigHandler.POSTING_RETENTION_IN_DAYS, None)

        with session_scope(self.dbms) as session:
            vacancy_list = [
                Vacancies(platform=self.platform.name, date=today, url="http://",
                          title="title", company="aha", search_topic='Java', location="Wien"),
                Vacancies(platform=self.platform.name, date=very_old_post_date, url="http://",
                          title="title", company="aha", search_topic='Java', location="Wien")
            ]

            for v in vacancy_list:
                session.add(v)

        self.dbms.cleanup_job_postings_in_database()

        with session_scope(self.dbms) as session:
            vacancies_instances_list = session.query(Vacancies).all()

            # Auto-Deletion should be disabled - both entries should be present
            self.assertEqual(len(vacancies_instances_list), 2)

            # Auto-Deletion should be disabled - both entries should be present
            date_list = [row.date for row in vacancies_instances_list]
            self.assertEqual(date_list, [today.date(), very_old_post_date.date()])

