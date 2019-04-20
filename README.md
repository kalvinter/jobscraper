# JobScraper
[![codecov](https://codecov.io/gh/kalvinter/jobscraper/branch/master/graph/badge.svg?token=dIrpvpdPVr)](https://codecov.io/gh/kalvinter/jobscraper)

WebScraper for job-posting websites. Get a quick overview over all potentiall interesting job-postings across multiple platforms.

The repository can easily be extended by new job-posting-websites. It is intended as a hobby project to play with selenium and make looking for a job more fun ;)

Currently four major Austrian job-posting-websites are implemented:
- karriere.at (current and newest website version)
- stepstone.at
- monster.at
- jobs.at

## Features

1) Search-results-pages of implemented websites are scraped
2) All scraped results are saved in an SQLite database
3) The results are written to an HTML-File which can be used to explore the individual job postings.

## Getting Started

### Prerequisites

- **Python 3.6+**

- **Download the required webdriver-file for your browser.**
  - **Google Chrome**: Tested for Chrome version 73. Download the chromedriver-file matching to your Chrome version from the [official Google source](http://chromedriver.chromium.org/downloads).  
  - **Firefox**: Tested for version 66 and geckodriver version 0.24.0. Download the latest geckodriver release from [the geckodriver github-page](https://github.com/mozilla/geckodriver/releases).
- **Copy the webdriver-file in the folder "webdriver"**. Don't change the webdriver-file's name!
- **Update the webdriver name in config.json**: Update the value for the key "DRIVER_EXE_NAME" in config.json to match 
your downloaded webdriver's name.

```
"DRIVER_EXE_NAME": "chromedriver.exe",
```

### Installation

There is a PipFile as well as a requirements.txt-File located in the root-directory. 

You can either install all dependencies via pipenv:
```
pipenv install
```
or you can just install the dependencies directly from the requirements.txt-file via pip. 
```
pip install -r requirements.txt 
```

### Running the tests

You can run all tests by running the run_test.py-file.

```
py run_tests.py
```

If any of the tests fails, please let me know by opening a new issue. 

## Using the JobScraper

You can start the scraper by simply running the main.py-file
```
py main.py
```

Using the flag -h shows help messages and further flags and available options.
```
py main.py -h
```

All options to customize the scraping can be changed in the **config.json**-File in the repository's root directory. There are four main config-options:

1) **DRIVER_EXE_NAME**: The file-name of your webdriver.exe-file saved in the folder "webdriver".
2) **STOPWORDS**: A job posting is skipped if it's title contains one of the stopwords defined here.
3) **PLATFORMS**: Here you can specify for each implemented job-posting-websites which search-urls should be scraped.
4) **POSTING_RETENTION_IN_DAYS**: Any job posting older than this value will be deleted from the database.
 

### How can I define my own search-queries?
For each implemented job-posting-websites you can define a search-topic and search-url in config.json.
The search-topic is just a name associated with the scraped results.

In the config.json-file you can simply add your own search-query by adding a new key-value-pair to the 
job-posting-platform of your choice.

- *Example: If you want to scrape all job-postings on karriere.at, open the website in your browser, select 
filter options and copy the URL. Next, create a new key-value-entry inside of the "KARRIERE.AT"-Key. The new key is 
your search topic (here it is "New Topic") and the value is the URL from your browser.* 

```
"PLATFORMS": {
		"KARRIERE.AT": {
			"Django Python": "https://www.karriere.at/jobs/django-python/wien",
			"New Topic": "https://www.karriere.at/jobs/new-keyword/wien"
		},		
	}
```

### How can I define my own stopwords?
Simply add your own stopwords as string to the list with the key "STOPWORDS" in config.json.
```
 "STOPWORDS": [
    "new_stopword_1",
    "new_stopword_2"
],

```

If any of these strings are found in a jop posting's title, the posting is skipped.

### How can I disable / change the retention time of job postings?
You can specify the retention time of job postings in days in the config.json-file. 
Enter a valid integer for the number of days. Any posting older than this value will be deleted.

```
"POSTING_RETENTION_IN_DAYS": 14
```
 
Enter the value "disabled" to disable auto-deletion.

```
"POSTING_RETENTION_IN_DAYS": "disabled"
```


## How can I add new job-posting-websites for scraping?

New job-posting-websites can be added by sub-classing PlatformHandlerBase. 
You have to set a platform_name and overwrite the _get_job_postings-function.  
```
class NewPlatformHandler(PlatformHandlerBase):
    platform_name = 'NEWPLATFORM.AT'
```

When overwriting the _get_job_postings-function you only have to make sure that you
- **Return a list** where each job-posting is dictionary with keys corresponding to the Vacancies-table:
```
{
	"platform": self.platform_name,
	"company": company,
	"url": url,
	"title": title,
	"date": date,
	"location": location,
}
```
- **In case of an exception**, set self.scrape_status[search_topic] to False and return an empty list. The scrape_status variable stores the success-status of each scrapings.
```
except (NoSuchElementException, ElementNotVisibleException) as e:
	... do something ...
	self.scrape_status[search_topic] = False
	return []
```

After that, register the new PlatformHandler-Class in _register_platforms-function 
in main.py: 
```
def _register_platforms(platform_registry: PlatformRegistry):
    ...
    platform_registry.register_new_platform(NewPlatformHandler)
```

Finally, add the new platform together with a search-topic and a search ULR in the config.json-File:

```
"PLATFORMS": {
		"NEWPLATTFORM.at": {
			"New Topic": "https://www.newplatfomr.at/"
		}
	}
```

## Built With

- [Selenium](https://selenium-python.readthedocs.io/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
