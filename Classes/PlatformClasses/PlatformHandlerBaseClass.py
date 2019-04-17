from abc import ABC, abstractmethod
from Classes.UtilClasses.ConfigHandlerClass import ConfigHandler
from Classes.UtilClasses.DBHandlerClass import session_scope, Vacancies

from datetime import datetime
import re
import time

class PlatformHandlerBase(ABC):
    platform_name = "BaseAbstractPlatformHandler"
    header = '---- # (BaseAbstractPlatformHandler)'
    verbose = False
    scrape_status = {}

    def __init__(self, browser, dbms, verbose: bool = False):
        self.browser = browser
        self.dbms = dbms
        self.verbose = verbose
        self.scrape_status = {}

    def run(self, search_topic: str, search_url: str):
        print(f"{self.header}: INFO: Start scraping {self.platform_name}. Search-Topic: {search_topic}")

        # Initialize default scrape-status before each run. Is set to False only if an error occurred
        self.scrape_status[search_topic] = True

        # Scrape entries
        vacancy_entries = self._get_job_postings(search_topic=search_topic, search_url=search_url)

        if self.scrape_status[search_topic]:
            # If scrape-status for this search_topic / search_url is True -> no error occurred
            self._save_vacancy_entries_to_database(vacancy_entries=vacancy_entries, search_topic=search_topic)
            print(f"{self.header}: INFO: Finished scraping {self.platform_name}. Search-Topic: {search_topic}. "
                  f"Found {len(vacancy_entries)} Job-Postings.")
        else:
            # If scrape-status is False -> an error occurred
            print(f"{self.header}: INFO: Failed scraping {self.platform_name}. Search-Topic: {search_topic}. "
                  f"An error occurred.")

    @abstractmethod
    def _get_job_postings(self, search_topic: str, search_url: str) -> list:
        pass

    @staticmethod
    def _apply_title_filter(title):
        title_lower = title.lower()

        for keyword in ConfigHandler.STOPWORDS:
            if keyword in title_lower:
                return False

        return True

    def _save_vacancy_entries_to_database(self, vacancy_entries: list, search_topic: str) -> bool:
        with session_scope(self.dbms) as session:
            try:
                for entry in vacancy_entries:
                    # Check if the entry already exists in the database
                    exists_check = session.query(Vacancies.id).filter(
                        Vacancies.platform == entry['platform'], Vacancies.company == entry['company'],
                        Vacancies.url == entry['url'], Vacancies.title == entry['title'],
                        Vacancies.search_topic == search_topic, Vacancies.date == entry['date'],
                        Vacancies.location == entry['location']
                    ).scalar() is not None

                    # If it does not exist, add it
                    if not exists_check:
                        new_vacancy = Vacancies(platform=entry['platform'], company=entry['company'], url=entry['url'],
                                                title=entry['title'], search_topic=search_topic, date=entry['date'],
                                                location=entry['location'])
                        session.add(new_vacancy)

            except Exception as e:
                print(f"{self.header}: ERROR: Could not insert new entries! Msg.: {str(e)}")
                raise

        return True

    def _parse_date(self, date_string):
        if 'T' in date_string:
            date_string = date_string.split('T')[0]

        # Remove all characters from datestring which are not numerical, dot (.) or dash (-).
        elif re.match(r'([^\d.-]+)', date_string):
            date_string = re.sub(r'([^\d.-]+)', '', date_string)

        date_patterns = [
            '%Y-%m-%d',
            '%Y-%m-%d ',
            '%Y-%m-%dT',
            '%d.%m.%Y',
        ]

        date = None

        for pattern in date_patterns:
            try:
                date = datetime.strptime(date_string, pattern).date()
                break

            except ValueError:
                continue

        if date is None:
            raise ValueError(f"{self.header}: ERROR: Could not parse datetime '{date_string}' found on the platform "
                             f"{self.platform_name}. Please contact the developer to fix it "
                             f"or if you are a python developer "
                             f"yourself, adapt the function '_parse_date()'.")

        return date