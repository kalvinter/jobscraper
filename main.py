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


def _register_platforms(platform_registry: PlatformRegistry):
    """ Register and instantiate all platforms that are implemented and stable so that they can be used """
    platform_registry.register_new_platform(KarriereATHandler)
    platform_registry.register_new_platform(StepStoneHandler)
    platform_registry.register_new_platform(MonsterATHandler)
    platform_registry.register_new_platform(JobsATHandler)


def main():
    # Initialize CL-Parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--platforms', action='store_true',
                        help='Prints all available platforms for scraping. Each platform can be added in the '
                             'config.json-File for scraping.')
    parser.add_argument('-v', action='store_true',
                        help='Verbose-mode. Prints all generated messages. Used for debugging.')

    args = parser.parse_args()
    print(args)
    # Parse and set Config-Values from config.json
    ConfigHandler.validate_config_file_base_variables()
    ConfigHandler.set_verbosity_level(args.v)

    # Initialize Base Classes
    dbms = DBHandler(DBHandler.SQLITE, db_name='job_scraper.sqlite')
    dbms.create_database_and_tables()

    browser_handler = BrowserHandler()
    browser = browser_handler.get_browser()

    platform_registry = PlatformRegistry(browser=browser, dbms=dbms)

    _register_platforms(platform_registry=platform_registry)

    # If -platforms-flag is set, display all registered platforms and exit
    if args.platforms:
        print("\nRegistered Platforms:\n-----------------")
        for platform in PlatformRegistry.registered_platforms:
            print(platform.platform_name)
        sys.exit(0)

    # Validate Search-Topics and URLs in config-file comparing it to the registered platforms
    ConfigHandler.validate_search_topics(platform_registry=platform_registry)

    # Clean up database and remove job-postings that are older than the retention-range
    dbms.cleanup_job_postings_in_database()

    # Check if all registered platforms exist as entries in the database
    platform_registry.create_platform_entries_in_database()

    # Perform web-scraping
    for platform_name in ConfigHandler.search_types_and_urls.keys():
        platform = platform_registry.get_platform_instance(platform_name)

        for search_topic, search_url in ConfigHandler.search_types_and_urls[platform_name].items():
            platform.run(search_topic=search_topic, search_url=search_url)

    browser_handler.close_browser()

    # Print fetched vacancies from db to HTML
    result_printer = ResultPrinter(dbms=dbms, platform_registry=platform_registry)
    result_printer.print_result_to_html(seach_topic_list=ConfigHandler.search_topics,
                                        open_html_after_finish=True)


if __name__ == '__main__':
    main()
