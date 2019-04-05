from Classes.PlatformClasses.PlatformHandlerBaseClass import PlatformHandlerBase

from selenium.common.exceptions import NoSuchElementException

from datetime import datetime
import time


class StepStoneHandler(PlatformHandlerBase):
    platform_name = 'STEPSTONE.AT'
    base_address = 'https://www.stepstone.at/'
    header = '---- # (StepStoneHandler)'

    def _get_job_postings(self, search_topic: str, search_url: str) -> list:
        """
        Open the search-url provided through the config-url for the provided search-topic. Read all job posting entries,
        prease next until there are no more results and return the resulting-list.
        :return: Return a list of dictionaries. One dictionary for each job posting.
        """
        vacancy_list = []

        self.browser.get(search_url)

        page = 0

        while True:
            page += 1

            # TODO: Time sleep takes to much time. I wait for an ajax-request to finish which is quicker.
            #  HOW could I explicitly wait? Waiting for an element does not work ...
            time.sleep(2)

            elements = self.browser.find_elements_by_css_selector('.job-element-row')

            print(f'\n# {page} ------------')
            print(elements)

            if not elements:
                break

            for element in elements:

                # Check if the job-posting is part of the recommendations
                try:
                    article_node = element.find_element_by_css_selector('.job-element_recommended')
                    # If this element is found, the job posting is part of the recommendations -> skip
                    continue

                except NoSuchElementException:
                    pass

                try:
                    title = element.find_element_by_css_selector('h2').text

                except Exception as e:
                    print(f"{self.header}: FATAL: An unexpected error occured!")
                    raise Exception(str(e))

                check = self.apply_title_filter(title)

                if not check:
                    continue
                try:
                    company = element.find_element_by_css_selector('.job-element__body__company').text
                    url = element.find_element_by_css_selector('.job-element__url').get_attribute('href')

                    date_string = element.find_element_by_css_selector('.date-time-ago').get_attribute('data-date')
                    date = self._parse_date(date_string=date_string)

                    location = element.find_element_by_css_selector('.job-element__body__location').text

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

            # If next button is found and href is not javascript void - click it
            try:
                next_button = self.browser.find_element_by_css_selector('.at-next')
                if next_button.get_attribute('href') == "javascript:void(0)":
                    break
                else:
                    next_button.click()

            except NoSuchElementException:
                print(f"{self.header}: INFO: No button found to press next.")
                break

        return vacancy_list

