from Classes.DBHandlerClass import session_scope, Platform
from Classes.DBHandlerClass import DBHandler


class PlatformRegistry:
    header = '---- #'
    dbms = None
    registered_platforms = {}

    @classmethod
    def register_new_platform(cls, platform_scraper_class):
        cls.registered_platforms[platform_scraper_class.platform_name] = platform_scraper_class

    @classmethod
    def get_registered_platforms(cls):
        return cls.registered_platforms

    @classmethod
    def instantiate_platforms(cls, browser, dbms: DBHandler):
        for name, platform in cls.registered_platforms.items():
            cls.registered_platforms[name] = platform(browser=browser, dbms=dbms)

    @classmethod
    def get_platform_instance(cls, platform_name):
        try:
            return cls.registered_platforms[platform_name]

        except KeyError:
            raise ValueError(f"{cls.header}: ERROR: Could not find the platform-name '{platform_name}'. "
                             f"Please make sure that it is registered using the function "
                             f"'get_registered_platforms()'")

    @classmethod
    def de_register_all_platforms(cls):
        cls.registered_platforms = {}

    @classmethod
    def create_platform_entries_in_database(cls, dbms: DBHandler) -> int:
        if not cls.registered_platforms:
            raise ValueError(f"{cls.header}: ERROR: before calling load-initial-data, platforms should"
                             f"be instantiated first. Call 'instantiate_platforms' before this method.")

        if not cls.registered_platforms:
            raise ValueError(f"{cls.header}: ERROR: No platforms have been registered. Please register at least"
                             f"one platform first.")

        with session_scope(dbms) as session:

            platform_query_set = session.query(Platform).all()

            platforms_in_db = [entry.name for entry in platform_query_set]

            for platform_name in cls.registered_platforms:
                if platform_name not in platforms_in_db:
                    platform = PlatformRegistry.get_platform_instance(platform_name)
                    platform_instance = Platform(name=platform.platform_name, base_address=platform.base_address)
                    session.add(platform_instance)

            session.commit()

        print(f"{cls.header}: Platform-Table successfully populated.")
        return True
