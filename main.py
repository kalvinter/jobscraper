from Classes.ConfigHandlerClass import ConfigHandler
from Classes.DBHandlerClass import DBHandler
from Classes.BrowserHandlerClass import BrowserHandler
from Classes.PlatformRegistryClass import PlatformRegistry
from Classes.ResultPrinterClass import ResultPrinter

from Classes.PlatformClasses.KarriereATHandlerClass import KarriereATHandler
from Classes.PlatformClasses.StepStoneHandlerClass import StepStoneHandler
from Classes.PlatformClasses.MonsterATHandlerClass import MonsterATHandler
from Classes.PlatformClasses.JobsATHandlerClass import JobsATHandler

import argparse
import sys


def main():
    # Initialize CL-Parser
    parser = argparse.ArgumentParser(description='A')
    parser.add_argument('--no-refetch',  action='store_true',
                        help='Vacancies are not refetched. Operations are run against existing entries '
                             'in the database')
    parser.add_argument('--platforms', action='store_true',
                        help='Prints all available platforms for scraping. Each platform can be added in the '
                             'config.json-File for scraping.')
    args = parser.parse_args()

    # Parse and set Config-Values
    ConfigHandler.validate_config_file_base_variables()

    # Initialize Base Classes
    dbms = DBHandler(DBHandler.SQLITE, db_name='job_scraper.sqlite')
    dbms.create_database_and_tables()

    browser_handler = BrowserHandler()

    # Register all platforms that are implemented and stable
    PlatformRegistry.register_new_platform(KarriereATHandler)
    PlatformRegistry.register_new_platform(StepStoneHandler)
    PlatformRegistry.register_new_platform(MonsterATHandler)
    PlatformRegistry.register_new_platform(JobsATHandler)

    if args.platforms:
        print("\nRegistered Platforms:\n-----------------")
        for platform in PlatformRegistry.registered_platforms:
            print(platform.platform_name)
        sys.exit(0)

    # Validate Search-Topics and URLs in config-file comparing it to the registered platforms
    ConfigHandler.validate_search_topics()

    # If 'no-refetch' is not set, Fetch all current job postings
    if not args.no_refetch:
        browser = browser_handler.get_browser()

        PlatformRegistry.instantiate_platforms(browser=browser, dbms=dbms)
        PlatformRegistry.create_platform_entries_in_database(dbms=dbms)

        for platform_name in ConfigHandler.search_types_and_urls.keys():
            platform = PlatformRegistry.get_platform_instance(platform_name)

            for search_topic, search_url in ConfigHandler.search_types_and_urls[platform_name].items():
                platform.run(search_topic=search_topic, search_url=search_url)

    # Print fetched vacancies from db to HTML
    result_printer = ResultPrinter(dbms=dbms)
    result_printer.print_result_to_html(seach_topic_list=ConfigHandler.search_topics,
                                        open_html_after_finish=True)


if __name__ == '__main__':
    main()
