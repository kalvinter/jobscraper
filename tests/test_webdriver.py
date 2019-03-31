import unittest

from Classes.UtilClasses import BrowserHandlerClass
from tests.unittest_config import TEST_URL

import time


class TestBrowserCreation(unittest.TestCase):

    def tearDown(self):
        try:
            # Try to close the browser after all tests have run
            self.browser_handler.close_browser()

        except:
            pass

    def test_start_browser(self):
        self.browser_handler = BrowserHandlerClass.BrowserHandler()
        browser = self.browser_handler.get_browser()

        browser.get(TEST_URL)
        h1 = browser.find_element_by_css_selector('h1')
        time.sleep(1)
        self.assertEqual(h1.text, 'Impressum und Offenlegung')

