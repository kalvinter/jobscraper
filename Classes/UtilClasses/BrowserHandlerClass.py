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
        self.driver = webdriver.Chrome(ConfigHandler.DRIVER_PATH)

        return self.driver

    def close_browser(self):
        self.driver.close()
        self.driver = None
