from Classes.PlatformClasses.PlatformHandlerBaseClass import PlatformHandlerBase

from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException

from datetime import datetime
import time


class MonsterATHandler(PlatformHandlerBase):
    platform_name = 'MONSTER.AT'
    base_address = 'https://www.monster.at/'
    header = '---- # (MonsterATHandler)'

    def _get_job_postings(self, search_topic: str, search_url: str) -> list:
        """
        Open the search-url provided through the config-url for the provided search-topic. Read all job posting entries,
        prease next until there are no more results and return the resulting-list.
        :return: Return a list of dictionaries. One dictionary for each job posting.
        """
        vacancy_list = []

        self.browser.get(search_url)

        # Check if the search result is empty. If yes - return empty list
        try:
            page_header = self.browser.find_element_by_css_selector('.title > .pivot').text

            if 'keine' in page_header.lower():
                return vacancy_list

        except Exception as e:
            print(f"{self.header}: FATAL: An unexpected error occured. Could not scrape platform "
                  f"{self.platform_name}! Error Msg: {str(e)}")
            self.scrape_status[search_topic] = False
            return []

        # In desktop view, find the button and press it
        while True:

            # If next button is found and href is not javascript void - click it
            try:
                next_button = self.browser.find_element_by_css_selector('#loadMoreJobs')
                next_button.click()

            except (NoSuchElementException, ElementNotVisibleException):
                print(f"{self.header}: INFO: No button found to press next.")
                break

        # In mobile View there is no button -> you have to scroll down
        last_height = self.browser.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down to bottom
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(0.5)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # TODO: Time sleep takes to much time. I wait for an ajax-request to finish which is quicker.
        #  HOW could I explicitly wait? Waiting for an element does not work ...
        time.sleep(2)

        # Start scraping the results
        results_container = self.browser.find_element_by_css_selector('#ResultsScrollable')

        elements = results_container.find_elements_by_css_selector('.flex-row')

        for element in elements:
            try:
                title = element.find_element_by_css_selector('a').text

                check = self._apply_title_filter(title)

                if not check:
                    # If a stopword is found in the title -> skip the entry
                    continue

                company = element.find_element_by_css_selector('.company').text
                url = element.find_element_by_css_selector('a').get_attribute('href')

                date_string = element.find_element_by_css_selector('time').get_attribute('datetime')
                date = self._parse_date(date_string=date_string)

                location = element.find_element_by_css_selector('.location').text

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

        if self.verbose:
            for i in vacancy_list:
                print(i)

        return vacancy_list

