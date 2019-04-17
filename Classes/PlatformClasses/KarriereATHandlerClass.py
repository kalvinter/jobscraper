from Classes.PlatformClasses.PlatformHandlerBaseClass import PlatformHandlerBase
from selenium.common.exceptions import NoSuchElementException
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

            elements = self.browser.find_elements_by_css_selector(
                '.m-jobahontasSearchList__activeJobs > .m-jobahontasList > .m-jobahontasList__item')

            if self.verbose:
                print(f'\n# {page} ------------')
                print(elements)

            if not elements:
                # Karriere.at is currently testing a new web-site design. If no elements are found, the legacy
                # algorithm should be used
                vacancy_list = self._get_job_postings_legacy(search_topic=search_topic, search_url=search_url)
                break

            for element in elements:
                self.browser.execute_script(
                    "let container = document.getElementsByClassName('c-jobahontasSearch__listingInner')[0];"
                    f"container.scrollTop = {int(element.get_attribute('offsetTop'))-10};")

                try:
                    title = element.find_element_by_css_selector('.m-jobahontasListItem__titleLink').text

                    check = self._apply_title_filter(title)

                    if not check:
                        # If a stopword is found in the title -> skip the entry
                        continue

                    company = element.find_element_by_css_selector(".m-jobahontasListItem__companyName").text
                    url = element.find_element_by_css_selector('.m-jobahontasListItem__titleLink')\
                        .get_attribute('href')

                    date_string = element.find_element_by_css_selector('.m-jobahontasListItem__date').text
                    date = self._parse_date(date_string=date_string)

                    location = element.find_element_by_css_selector('.m-jobahontasListItem__locationLink').text

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

            try:
                # Scroll button in the left-hand search container into view
                self.browser.execute_script("let buttonPos = document.getElementsByClassName('m-pagination__button--next')[0].offsetTop;"
                                            "let container = document.getElementsByClassName('c-jobahontasSearch__listingInner')[0];"
                                            "container.scrollTop = buttonPos-10;")

                # Find next button and try clicking it -> load more entries
                next_button = self.browser.find_element_by_css_selector('.m-pagination__button--next')

                if "m-pagination__button--disabled" in next_button.get_attribute('class'):
                    # If this class is present, there are no more pages available
                    break
                else:
                    next_button.click()
            except NoSuchElementException as e:
                # If it is not clickable, no more entries can be loaded -> break
                print(f"{self.header}: INFO: (Page: {page}) No button found to press next.")
                if self.verbose:
                    print(str(e))
                break

        return vacancy_list

    def _get_job_postings_legacy(self, search_topic: str, search_url: str):
        page = 0
        vacancy_list = []

        while True:
            page += 1

            # TODO: Time sleep takes to much time. I wait for an ajax-request to finish which is quicker.
            #  HOW could I explicitly wait? Waiting for an element does not work ...
            time.sleep(2)

            elements = self.browser.find_elements_by_css_selector(
                '.m-jobItem__dataContainer')

            if self.verbose:
                print(f'\n# {page} ------------')
                print(elements)

            if not elements:
                break

            for element in elements:
                try:
                    title = element.find_element_by_css_selector('.m-jobItem__titleLink').text

                    check = self._apply_title_filter(title)

                    if not check:
                        # If a stopword is found in the title -> skip the entry
                        continue

                    company = element.find_element_by_css_selector(".m-jobItem__company").text
                    url = element.find_element_by_css_selector('.m-jobItem__titleLink')\
                        .get_attribute('href')

                    date_string = element.find_element_by_css_selector('.m-jobItem__date').text
                    date = self._parse_date(date_string=date_string)

                    location = element.find_element_by_css_selector('.m-jobItem__locationLink').text

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

            try:
                # Find next button and try clicking it -> load more entries
                next_button = self.browser.find_element_by_css_selector('.m-pagination__button--next')

                if "m-pagination__button--disabled" in next_button.get_attribute('class'):
                    # If this class is present, there are no more pages available
                    break
                else:
                    next_button.click()

            except NoSuchElementException as e:
                # If it is not clickable, no more entries can be loaded -> break
                print(f"{self.header}: INFO: (Page: {page}) No button found to press next.")
                if self.verbose:
                    print(str(e))
                break

        return vacancy_list