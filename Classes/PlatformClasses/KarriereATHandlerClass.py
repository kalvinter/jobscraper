from Classes.PlatformClasses.PlatformHandlerBaseClass import PlatformHandlerBase

from datetime import datetime
import time


class KarriereATHandler(PlatformHandlerBase):
    platform_name = 'KARRIERE.AT'
    base_address = 'https://www.karriere.at/'
    header = '---- # (KarriereATHandler)'

    def _get_job_postings(self, search_topic: str, search_url: str):
        vacancy_list = []

        self.browser.get(search_url)

        page = 0

        while True:
            page += 1

            # TODO: Time sleep takes to much time. I wait for an ajax-request to finish which is quicker.
            #  HOW could I explicitly wait? Waiting for an element does not work ...
            time.sleep(2)

            elements = self.browser.find_elements_by_css_selector('.m-jobItem__dataContainer')

            print(f'\n# {page} ------------')
            print(elements)

            if not elements:
                break

            for element in elements:
                try:
                    title = element.find_element_by_css_selector('h2').text

                except Exception as e:
                    print(f"{self.header}: FATAL: An unexpected error occured!")
                    raise Exception(str(e))

                check = self.apply_title_filter(title)

                if not check:
                    continue

                try:
                    company = element.find_element_by_css_selector('.m-jobItem__company').text
                    url = element.find_element_by_css_selector('.m-jobItem__titleLink').get_attribute('href')

                    date_string = element.find_element_by_css_selector('.m-jobItem__date').text
                    date = self._parse_date(date_string=date_string)

                    location = element.find_element_by_css_selector('.m-jobItem__locationLink').text

                except Exception as e:
                    print(f"{self.header}: FATAL: An unexpected error occured!")
                    raise Exception(str(e))

                vacancy_list.append({
                    "platform": self.platform_name,
                    "company": company,
                    "url": url,
                    "title": title,
                    "date": date,
                    "location": location,
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

