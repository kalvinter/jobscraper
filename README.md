# jobscraper
WebScraper for job-posting websites. Automate finding interesting job postings.

## Getting Started

### Prerequisites

First, download the repository.

The project requires a matching webdriver.exe-File. The project is currently tested for Chrome Version 73. If you use Google Chrome 
look up your Chrome-Browser's version and download the matching webdriver.exe-File from the 
[official source from Google](http://chromedriver.chromium.org/downloads). Put the webdriver-file in the project's 
root directory (where main.py-file is located).

### Installing

If you use pipenv installation is quite easy. , go to the root directory (where main.py-file is located) and enter

```
pipenv install
```

Alternatively, there is an requirements.txt-file present. Activate your virtualenvironment and run 
```
pip install -r requirements.txt 
```

### Running the tests

There are several automated tests defined for this project. Simply run in the root-directory the py-file 'run_test.py'.

```
py run_tests.py
```

## Built With

- [Selenium](https://selenium-python.readthedocs.io/)
- [SQLAlchemy](https://www.sqlalchemy.org/)


## How to use the programme

All main config.json

### Define your own search-queries
In config.json-File add your own search-topic.

Add your own search-url.

### Define stop words
If any of these strings are contained in a jop posting's title, the posting is skipped.


## Extend / change the programme

As stated above, the scraper can only scrape job postings from the pre-defined job-postings platforms. If you want to add new website 
to the scraper, you have to create a new scraper-class in the folder PlatformClasses and it has to inherit from the PlatformHandlerBaseClass.
Inside your new platform-class override the method _get_vacancy_links. 

Finally, register the new platform-handler in the platform-registry-object in the main.py-file.

