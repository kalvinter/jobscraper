import unittest

from Classes.DBHandlerClass import DBHandler, Vacancies, Platform, session_scope
from tests.unittest_config import TEST_DB_PATH, TEST_DB_NAME

import os
from datetime import datetime


class TestDBCreation(unittest.TestCase):

    def test_create_database(self):
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

    def tearDown(self):
        with session_scope(self.dbms) as session:
            session.query(Vacancies).delete()

    def test_insert_row_in_articles(self):
        with session_scope(self.dbms) as session:
            new_vacancy = Vacancies(platform=self.platform.name, date=datetime(2019, 1, 1), url="http://",
                                    title="title", company="aha", search_type='Java')

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
                          title="title", company="aha", search_type='Java'),
                Vacancies(platform=self.platform.name, date=datetime(2019, 1, 3), url="http://",
                          title="title", company="aha", search_type='Java')
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

