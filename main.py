from Classes.ConfigHandlerClass import ConfigHandler
from Classes.DBHandlerClass import DBHandler
from Classes.BrowserHandlerClass import BrowserHandler
from Classes.PlatformRegistryClass import PlatformRegistry
from Classes.ResultPrinterClass import ResultPrinter

from Classes.PlatformClasses.KarriereATHandlerClass import KarriereATHandler
from Classes.PlatformClasses.StepStoneHandlerClass import StepStoneHandler

import argparse
import time


def main():
    # Initialize CL-Parser
    parser = argparse.ArgumentParser(description='A')
    parser.add_argument('--no-refetch',  action='store_true',
                        help='Vacancies are not refetched. Operations are run against existing entries '
                             'in the database')
    args = parser.parse_args()

    # Parse and set Config-Values
    ConfigHandler.validate_config_file()

    # Initialize Base Classes
    dbms = DBHandler(DBHandler.SQLITE, db_name='job_scraper.sqlite')
    dbms.create_database_and_tables()

    browser_handler = BrowserHandler()
    browser = browser_handler.get_browser()

    # If no-refetch is not set, Fetch all vacancies
    if not args.no_refetch:
        platform_registry = PlatformRegistry(dbms=dbms)

        platform_registry.register_platform(KarriereATHandler(browser=browser, dbms=dbms))
        platform_registry.register_platform(StepStoneHandler(browser=browser, dbms=dbms))

        platform_registry.load_initial_data()

        for platform in platform_registry.platforms:
            for search_topic in ConfigHandler.search_types_and_urls.keys():
                platform.run(search_topic=search_topic)

    # Print fetched vacancies from db to HTML
    result_printer = ResultPrinter(dbms=dbms, browser=browser)
    result_printer.print_result_to_html(seach_topic_list=list(ConfigHandler.search_types_and_urls.keys()),
                                        open_html_after_finish=True)
    time.sleep(1)


if __name__ == '__main__':
    main()
