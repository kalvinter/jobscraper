from Classes.DBHandlerClass import session_scope, Vacancies, Platform
from config import ROOT_DIR

from datetime import datetime
import json


def load_data_scripture(dbms):
    platform_json_file = ROOT_DIR + "/tests/test_data/platform.json"
    vacancies_json_file = ROOT_DIR + "/tests/test_data/vacancies.json"

    with session_scope(dbms=dbms) as session:

        with open(platform_json_file, 'r') as json_file:
            platform_file = json.loads(json_file.read())

            for row in platform_file:
                session.add(
                    Platform(name=row['name'], base_address=row['base_address'])
                )

        session.commit()
        session.flush()

        with open(vacancies_json_file, 'r') as json_file:
            platform_file = json.loads(json_file.read())

            for row in platform_file:
                date = datetime.strptime(row['date'], '%Y-%m-%d')
                session.add(
                    Vacancies(platform=row['platform'], search_topic=row['search_type'], date=date,
                              url=row['url'], company=row['company'], title=row['title'])
                )
