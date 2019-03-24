from Classes.DBHandlerClass import session_scope, Platform


class PlatformRegistry:

    def __init__(self, dbms):
        self.header = '---- #'
        self.dbms = dbms
        self.platforms = []

    def register_platform(self, platform_scraper_class):
        self.platforms.append(platform_scraper_class)

    def load_initial_data(self):
        with session_scope(self.dbms) as session:

            table_count = session.query(Platform).count()
            if table_count > 0:
                print(f"{self.header}: Platform-Table already populated.")
                return False

            for platform in self.platforms:
                platform_instance = Platform(name=platform.platform_name, base_address=platform.base_address)
                session.add(platform_instance)

            session.commit()

        print(f"{self.header}: Platform-Table successfully populated.")
        return True
