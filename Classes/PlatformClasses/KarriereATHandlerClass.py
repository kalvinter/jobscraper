from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from Classes.PlatformClasses.PlatformHandlerBaseClass import PlatformHandlerBase

from datetime import datetime
import time


class KarriereATHandler(PlatformHandlerBase):

    def __init__(self, browser, dbms):
        super().__init__(browser=browser, dbms=dbms)
        self.header = '---- # (KarriereATHandler)'

        self.platform_name = 'karriere.at'
        self.base_address = 'https://www.karriere.at/'

        self.search_type = 'Java'
        self.search_adress = 'https://www.karriere.at/jobs/java/wien?jobLevels%5B%5D=3954&states%5B%5D=2430'

    def _get_vacancy_links(self):
        vacancy_list = []

        self.browser.get(self.search_adress)

        page = 0

        while True:
            page += 1

            # TODO: Time sleep takes to much time. I wait for an ajax-request to finish which is quicker.
            #  HOW could I explicitly wait? Waiting for an element does not work ...
            time.sleep(1)

            elements = self.browser.find_elements_by_css_selector('.m-jobItem__dataContainer')

            print(f'\n# {page} ------------')
            print(elements)

            for element in elements:
                title = element.find_element_by_css_selector('h2').text

                check = self.apply_title_filter(title)

                if not check:
                    continue

                company = element.find_element_by_css_selector('.m-jobItem__company').text
                url = element.find_element_by_css_selector('.m-jobItem__titleLink').get_attribute('href')
                date_raw = element.find_element_by_css_selector('.m-jobItem__date').text
                date = datetime.strptime(date_raw.replace('am ', ''), '%d.%m.%Y')

                vacancy_list.append({
                    "platform": self.platform_name,
                    "company": company,
                    "url": url,
                    "title": title,
                    "date": date
                })

            for i in vacancy_list:
                print(i)

            # Check if next button is active
            try:
                next_button = self.browser.find_element_by_css_selector('.m-pagination__button--next')
                next_button.click()

            except Exception as e:
                print(str(e))
                break
        return vacancy_list

