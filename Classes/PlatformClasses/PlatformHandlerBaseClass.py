from abc import ABC, abstractmethod
from Classes.ConfigHandlerClass import ConfigHandler
from Classes.DBHandlerClass import session_scope, Vacancies


class PlatformHandlerBase(ABC):
    platform_name = "BaseAbstractPlatformHandler"
    header = '---- # (BaseAbstractPlatformHandler)'

    def __init__(self, browser, dbms):
        self.browser = browser
        self.dbms = dbms

    def run(self, search_topic: str, search_url: str):
        vacancy_entries = self._get_vacancy_links(search_topic=search_topic, search_url=search_url)
        self._save_vacancy_entries_to_database(vacancy_entries=vacancy_entries, search_topic=search_topic)

    @abstractmethod
    def _get_vacancy_links(self, search_topic: str, search_url: str) -> list:
        pass

    @staticmethod
    def apply_title_filter(title):
        title_lower = title.lower()

        for keyword in ConfigHandler.STOPWORDS:
            if keyword in title_lower:
                return False

        return True

    def _save_vacancy_entries_to_database(self, vacancy_entries: list, search_topic: str) -> bool:
        with session_scope(self.dbms) as session:
            try:
                # Delete existing entries
                session.query(Vacancies)\
                    .filter(Vacancies.platform == self.platform_name, Vacancies.search_topic == search_topic).delete()

            except Exception as e:
                print(f"{self.header}: ERROR: Could not delete old entries! Msg.: {str(e)}")
                raise

            try:
                for entry in vacancy_entries:
                    print(entry)
                    new_vacancy = Vacancies(platform=entry['platform'], company=entry['company'], url=entry['url'],
                                            title=entry['title'], search_topic=search_topic, date=entry['date'],
                                            location=entry['location'])
                    session.add(new_vacancy)
            except Exception as e:
                print(f"{self.header}: ERROR: Could not insert new entries! Msg.: {str(e)}")
                raise

        return True
