from Classes.UtilClasses.ConfigHandlerClass import ConfigHandler
from Classes.UtilClasses.DBHandlerClass import DBHandler
from Classes.UtilClasses.BrowserHandlerClass import BrowserHandler
from Classes.UtilClasses.PlatformRegistryClass import PlatformRegistry
from Classes.DisplayClasses.ResultPrinterClass import ResultPrinter

from Classes.PlatformClasses.KarriereATHandlerClass import KarriereATHandler
from Classes.PlatformClasses.StepStoneHandlerClass import StepStoneHandler
from Classes.PlatformClasses.MonsterATHandlerClass import MonsterATHandler
from Classes.PlatformClasses.JobsATHandlerClass import JobsATHandler

import argparse
import sys


'''
The project's core-code can be found in the Classes-directory. It consists of three main packages:
    
    1)  UtilClasses:        Contains all overhead-utitlity-classes that are associated with DB-connection and parsing
                            config-variables (search-url, search-topics), creating the browser etc.
    
    2)  PlatformClasses:    Contains all classes that perform the actual web-scraping. All 
                            platform-handler-classes inherit from the PlatformHandlerBaseClass.
    
    3)  DisplayClasses:     Contains all classes that are associated with displaying the result.
                            Currently, there is only a class printing the result to HTML. Future extension to display
                            the config, dialogs and result in a window should be added here.

'''


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

    # Parse and set Config-Values from config.json
    ConfigHandler.validate_config_file_base_variables()

    # Initialize Base Classes
    dbms = DBHandler(DBHandler.SQLITE, db_name='job_scraper.sqlite')
    dbms.create_database_and_tables()

    browser_handler = BrowserHandler()
    browser = browser_handler.get_browser()

    platform_registry = PlatformRegistry(browser=browser, dbms=dbms)

    # Register and instantiate all platforms that are implemented and stable
    platform_registry.register_new_platform(KarriereATHandler)
    platform_registry.register_new_platform(StepStoneHandler)
    platform_registry.register_new_platform(MonsterATHandler)
    platform_registry.register_new_platform(JobsATHandler)

    if args.platforms:
        print("\nRegistered Platforms:\n-----------------")
        for platform in PlatformRegistry.registered_platforms:
            print(platform.platform_name)
        sys.exit(0)

    # Validate Search-Topics and URLs in config-file comparing it to the registered platforms
    ConfigHandler.validate_search_topics(platform_registry=platform_registry)

    # If 'no-refetch' is not set, Fetch all current job postings
    if not args.no_refetch:

        platform_registry.create_platform_entries_in_database()

        for platform_name in ConfigHandler.search_types_and_urls.keys():
            platform = platform_registry.get_platform_instance(platform_name)

            for search_topic, search_url in ConfigHandler.search_types_and_urls[platform_name].items():
                platform.run(search_topic=search_topic, search_url=search_url)

    browser_handler.close_browser()

    # Print fetched vacancies from db to HTML
    result_printer = ResultPrinter(dbms=dbms)
    result_printer.print_result_to_html(seach_topic_list=ConfigHandler.search_topics,
                                        open_html_after_finish=True)


if __name__ == '__main__':
    main()
