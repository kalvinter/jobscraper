from selenium import webdriver
from Classes.ConfigHandlerClass import ConfigHandler


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
