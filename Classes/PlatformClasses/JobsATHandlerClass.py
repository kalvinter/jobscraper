from Classes.PlatformClasses.PlatformHandlerBaseClass import PlatformHandlerBase

from selenium.common.exceptions import NoSuchElementException

from datetime import datetime
import time


class JobsATHandler(PlatformHandlerBase):
    platform_name = 'JOBS.AT'
    base_address = 'https://jobs.at/'
    header = '---- # (JobsATHandler)'

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

            elements = self.browser.find_elements_by_css_selector('.m-list-item')

            if self.verbose:
                print(f'\n# {page} ------------')
                print(elements)

            if not elements:
                break

            for element in elements:
                try:
                    title = element.find_element_by_css_selector('.m-list-item-title').text

                    check = self._apply_title_filter(title)

                    if not check:
                        # If a stopword is found in the title -> skip the entry
                        continue

                    try:
                        company = element.find_element_by_css_selector('.m-job-company > a').text

                    except NoSuchElementException:
                        company = element.find_element_by_css_selector('.m-job-company').text

                    try:
                        url = element.find_element_by_css_selector('.m-list-item-title > a').get_attribute('href')

                    except NoSuchElementException:
                        # If no link is found, the vacancy is already filled
                        continue

                    date_string = element.find_element_by_css_selector('.m-list-sneakPeek').text

                    # Current format found on Jobs.at -> "05.04.2019 | Vollzeit"
                    date = self._parse_date(date_string=date_string.split(' ')[0])

                    location = element.find_element_by_css_selector('.js-locationLink').text

                except Exception as e:
                    print(f"{self.header}: FATAL: An unexpected error occured. Could not scrape platform "
                          f"{self.platform_name}! Error Msg: {str(e)}")
                    self.scrape_status[search_topic] = False
                    return []

                vacancy_list.append({
                    "platform": self.platform_name,
                    "company": company,
                    "url": url,
                    "title": title,
                    "date": date,
                    "location": location,
                })

            # If next button is found and href is not javascript void - click it
            try:
                next_button = self.browser.find_element_by_css_selector('.m-pagination-item--last')
                if 'b--disabled' in next_button.get_attribute('class'):
                    break

                next_button.click()

            except NoSuchElementException:
                print(f"{self.header}: INFO: No button found to press next.")
                break

        if self.verbose:
            for i in vacancy_list:
                print(i)

        return vacancy_list

