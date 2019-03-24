from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import ROOT_DIR
import os


class BrowserHandler:

    def __init__(self):
        self.driver = None

    def get_browser(self):

        self.driver = webdriver.Chrome(ROOT_DIR + '/chromedriver.exe')

        return self.driver
