from abc import ABC, abstractmethod

from config import TITLE_FILTER
from Classes.DBHandlerClass import session_scope, Vacancies
from datetime import datetime
import time


class PlatformHandlerBase(ABC):

    def __init__(self, browser, dbms):
        self.browser = browser
        self.dbms = dbms
        self.platform_name = ''
        self.header = '---- # (PlatformHandler)'
        self.search_type = None

    def run(self, search_type):
        self.search_type = search_type
        vacancy_entries = self._get_vacancy_links()
        self._save_entries_to_database(vacancy_entries)
        return None

    @abstractmethod
    def _get_vacancy_links(self) -> list:
        pass

    @staticmethod
    def apply_title_filter(title):
        title_lower = title.lower()

        for keyword_type, keywords in TITLE_FILTER.items():

            if keyword_type == 'negative':
                for word in keywords:
                    if word in title_lower:
                        return False

            elif keyword_type == 'positive':
                for word in keywords:
                    if word in title_lower:
                        return True

        return True

    def _save_entries_to_database(self, vacancy_entries):
        with session_scope(self.dbms) as session:
            try:
                # Delete existing entries
                session.query(Vacancies).filter(Vacancies.platform == self.platform_name).delete()

            except Exception as e:
                print(f"{self.header}: ERROR: Could not delete old entries! Msg.: {str(e)}")
                raise

            try:
                for entry in vacancy_entries:
                    new_vacancy = Vacancies(platform=entry['platform'], company=entry['company'], url=entry['url'],
                                            title=entry['title'], search_type=self.search_type, date=entry['date'])
                    session.add(new_vacancy)
            except Exception as e:
                print(f"{self.header}: ERROR: Could not insert new entries! Msg.: {str(e)}")
                raise

        return True
