from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from contextlib import contextmanager

import os
from typing import Tuple


#db_path = f"sqlite:///{os.getcwd()}\\job_scraper.db"
#engine = create_engine(db_path, echo=True)
Base = declarative_base()


@contextmanager
def session_scope(dbms):
    """Provide a transactional scope around a series of operations."""
    session = dbms.Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class DBHandler:
    SQLITE = 'sqlite'

    # Table Names
    VACANCIES = 'vacancies'
    PLATFORM = 'platform'

    # http://docs.sqlalchemy.org/en/latest/core/engines.html
    DB_ENGINE = {
        SQLITE: f"sqlite:///{os.getcwd()}\\"
    }

    # Main DB Connection Ref Obj
    db_engine = None

    def __init__(self, dbtype, db_name):
        if dbtype in self.DB_ENGINE.keys():
            engine_url = self.DB_ENGINE[dbtype] + db_name
            self.db_engine = create_engine(engine_url)
            print(self.db_engine)
        else:
            raise ValueError("DBType does not exist!")

        self.Session = sessionmaker(bind=self.db_engine)

        self.initial_platform_data = [
            Platform(name="karriere.at", base_address="www.karriere.at/"),
        ]

    def get_session(self):
        return self.Session()

    def create_database_and_tables(self):
        try:
            Base.metadata.create_all(self.db_engine)
            print("Tables created")

        except Exception as e:
            print("Error occurred during Table creation!")
            print(e)

    def get_tables_in_database(self):
        table_query = "SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%';"
        result = self.execute_query(table_query, select_query=True)
        return result

    def load_initial_data(self):
        with session_scope(self) as session:
            for platform_instance in self.initial_platform_data:
                session.add(platform_instance)

    def execute_query(self, query, select_query: bool = True, insert_query: bool = False, update_query: bool = False):
        with self.db_engine.connect() as connection:
            try:
                result = connection.execute(query)

                if update_query or insert_query:
                    print(f"Database Return Code: {result}")

                elif select_query:
                    result_list = []
                    for row in result:
                        result_list.append(dict(row))
                    return result_list

            except Exception as e:
                print(e)


class Vacancies(Base):

    __tablename__ = "vacancies"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    search_type = Column(String)
    platform = Column(ForeignKey('platform.name'))
    company = Column(String)
    date = Column(Date)
    url = Column(String)
    title = Column(String)

    def __init__(self, platform, search_type, date, url, company, title):
        self.platform = platform
        self.search_type = search_type
        self.date = date
        self.url = url
        self.company = company
        self.title = title

    def __str__(self):
        return f"{str(self.id)}: {self.platform}; {self.date}; {self.url}; {self.title}"

    def save(self, dbms):
        insert_query = f"INSERT INTO {self.__tablename__} (platform, date, url, title, text) " \
            f"VALUES({self.platform}, {self.date}, {self.url}, {self.title});"
        dbms.execute_query(insert_query, insert_query=True)


class Platform(Base):

    __tablename__ = "platform"

    name = Column(String, primary_key=True)
    base_address = Column(String)

    def __init__(self, name, base_address):
        self.name = name
        self.base_address = base_address

    def __str__(self):
        return f"{self.name}: {self.base_address}"

    def save(self, dbms):
        insert_query = f"INSERT INTO {self.__tablename__} (platform, date, url, title, text) " \
            f"VALUES({self.name}, {self.base_address};"
        dbms.execute_query(insert_query, insert_query=True)
