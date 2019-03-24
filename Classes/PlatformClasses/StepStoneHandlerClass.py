from Classes.PlatformClasses.PlatformHandlerBaseClass import PlatformHandlerBase
from Classes.ConfigHandlerClass import ConfigHandler

from datetime import datetime
import time


class StepStoneHandler(PlatformHandlerBase):

    def __init__(self, browser, dbms):
        super().__init__(browser=browser, dbms=dbms)
        self.header = '---- # (StepStoneHandler)'

        self.platform_name = 'stepstone.at'
        self.base_address = 'https://www.stepstone.at/'

        self.search_type = 'Java'
        self.search_adress = 'https://www.stepstone.at/5/ergebnisliste.html?ke=Java&ws=Wien&ex=90001&suid=9ca21fcc-' \
                             '3eaf-4edb-9853-51d91ff34c97&fsk=658860&an=facets&li=100&fid=90002&fn=experiences&fa=' \
                             'deselect'

    def _get_vacancy_links(self, search_topic: str = None) -> list:
        """
        Open the search-url provided through the config-url for the provided search-topic. Read all job posting entries,
        prease next until there are no more results and return the resulting-list.
        :return: Return a list of dictionaries. One dictionary for each job posting.
        """
        if search_topic is None or search_topic not in ConfigHandler.search_types_and_urls.keys():
            raise ValueError("Search topic must be included in the config-json and not None.")

        elif self.platform_name not in ConfigHandler.search_types_and_urls[search_topic].keys():
            raise ValueError(f"Platform Name: '{self.platform_name}' could not be found in the config-json-file.")

        vacancy_list = []

        self.browser.get(ConfigHandler.search_types_and_urls[search_topic][self.platform_name])

        page = 0

        while True:
            page += 1

            # TODO: Time sleep takes to much time. I wait for an ajax-request to finish which is quicker.
            #  HOW could I explicitly wait? Waiting for an element does not work ...
            time.sleep(2)

            elements = self.browser.find_elements_by_css_selector('.job-element-row')

            print(f'\n# {page} ------------')
            print(elements)

            for element in elements:
                title = element.find_element_by_css_selector('h2').text

                check = self.apply_title_filter(title)

                if not check:
                    continue

                company = element.find_element_by_css_selector('.job-element__body__company').text
                url = element.find_element_by_css_selector('.job-element__url').get_attribute('href')
                date_raw = element.find_element_by_css_selector('.date-time-ago').get_attribute('data-date')
                date = datetime.strptime(date_raw.split(' ')[0], '%Y-%m-%d')

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
                next_button = self.browser.find_element_by_css_selector('.at-next')
                if next_button.get_attribute('href') == "javascript:void(0)":
                    break
                else:
                    next_button.click()

            except Exception as e:
                print(str(e))
                break
        return vacancy_list

