from Classes.UtilClasses.DBHandlerClass import session_scope, Platform
from Classes.UtilClasses.DBHandlerClass import DBHandler


class Singleton(type):
    _instance = None

    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance

    def Instance(cls, *args, **kwargs):
        return cls.__call__(*args, **kwargs)


class PlatformRegistry(metaclass=Singleton):
    __instance = None
    header = '---- #'
    dbms = None
    registered_platforms = {}

    def __init__(self, browser, dbms: DBHandler):
        self.browser = browser
        self.dbms = dbms

    def register_new_platform(self, platform_scraper_class):
        self.registered_platforms[platform_scraper_class.platform_name] = \
            platform_scraper_class(browser=self.browser, dbms=self.dbms)

    def get_platform_instance(self, platform_name):
        try:
            return self.registered_platforms[platform_name]

        except KeyError:
            raise ValueError(f"{self.header}: ERROR: Could not find the platform-name '{platform_name}'. "
                             f"Please make sure that it is registered using the function "
                             f"'get_registered_platforms()'")

    def de_register_all_platforms(self):
        self.registered_platforms = {}

    def create_platform_entries_in_database(self):
        if not self.registered_platforms:
            raise ValueError(f"{self.header}: ERROR: before calling load-initial-data, platforms should"
                             f"be instantiated first. Call 'instantiate_platforms' before this method.")

        if not self.registered_platforms:
            raise ValueError(f"{self.header}: ERROR: No platforms have been registered. Please register at least"
                             f"one platform first.")

        with session_scope(self.dbms) as session:

            platform_query_set = session.query(Platform).all()

            platforms_in_db = [entry.name for entry in platform_query_set]

            for platform_name in self.registered_platforms:
                if platform_name not in platforms_in_db:
                    platform = self.get_platform_instance(platform_name)
                    platform_instance = Platform(name=platform.platform_name, base_address=platform.base_address)
                    session.add(platform_instance)

            session.commit()

        print(f"{self.header}: Platform-Table successfully populated.")
