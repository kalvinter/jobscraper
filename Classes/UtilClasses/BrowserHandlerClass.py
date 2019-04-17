from selenium import webdriver
from Classes.UtilClasses.ConfigHandlerClass import ConfigHandler


class BrowserHandler:

    def __init__(self):
        self.driver = None

    def get_browser(self) -> webdriver:
        """
        Instantiate a new web-driver instance.
        :return: web-driver-instance
        """
        # Place any driver-options, plugin-imports or other changes to the browser instance here
        if ConfigHandler.DRIVER_TYPE.lower() == 'chrome':
            self.driver = webdriver.Chrome(ConfigHandler.DRIVER_PATH)

        elif ConfigHandler.DRIVER_TYPE.lower() == 'firefox':
            self.driver = webdriver.Firefox(executable_path=ConfigHandler.DRIVER_PATH)

        else:
            raise ValueError("DRIVER_TYPE incorrectly set.")

        self.driver.maximize_window()

        return self.driver

    def close_browser(self):
        self.driver.close()
        self.driver = None
