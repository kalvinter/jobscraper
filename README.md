# jobscraper
[![codecov](https://codecov.io/gh/kalvinter/jobscraper/branch/master/graph/badge.svg?token=dIrpvpdPVr)](https://codecov.io/gh/kalvinter/jobscraper)

WebScraper for job-posting websites. Automate finding interesting job postings. Spend less time looking for job postings and focus on writing your applications.

Currently four major Austrian job-posting-websites are implemented:
- karriere.at
- stepstone.at
- monster.at
- jobs.at

The repository is easily extendable and intended as a hobby project to play with selenium and make looking for 
a job more fun ;)  

## Features

1) Search-results-pages of implemented websites are scraped
2) All scraped results are saved in an SQLite database
3) The results are written to an HTML-File which can be used to explore the individual job postings.

## Getting Started

### Prerequisites

- **Python 3.6+**

- **Download the required webdriver-exe-File for your browser.** The project requires a matching webdriver.exe-file. The project is currently tested for Chrome Version 73. 
If you use Google Chrome, look up your Chrome-Browser's version by clicking on 'help' in a Chrome-Window. Then click 
on 'about Google Chrome'. There you should see your browser's version. After that download the matching 
webdriver.exe-File from the [official source from Google](http://chromedriver.chromium.org/downloads). 
Copy the webdriver-file in the project's root directory (where main.py-file is located). Lastly, compare the file
name to the name provided in the config.json-File under the key "DRIVER_EXE_NAME". If your driver-file is named 
differently update the file-name in config.json so that it matches the name of your exe-file.

```
	"DRIVER_EXE_NAME": "mydriver.exe",
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

## Using the script

You can start the script by simply running the main.py-File
```
py main.py
```

All options to customize the scraping can be changed in the **config.json**-File. 
The file is located in the repository's root directory. There are four main config-options. 

1) **DRIVER_EXE_NAME**: Please specify the file-name of your webdriver.exe-File. The script will look for this file-name in the repository's root directory.
2) **STOPWORDS**: If a job posting's title contains one of the stopwords defined here, the job posting will be skipped.
3) **PLATFORMS**: For each of the implemented job-posting-website, add a search-url with a recognizable search-topic-name.
4) **POSTING_RETENTION_IN_DAYS**: Specify the retention time of job postings in days. Any posting older than this value will be deleted.
 

### How can I define my own search-queries (Config-Option: PLATFORMS)?
For each of the implemented job-posting-websites you can define a search-topic and search-url.
The search-topic is just a name that will be associated with the scraped results.

In config.json-File you can simply add your own search-query by adding a new key-value-pair to the 
job-posting-platform of your choice.

Example: If you want to scrape all job-postings on karriere.at, open the website in your browser, select all the 
filter options to your liking (Full-time, beginner, advanced etc.) and copy the URL. Next create
a new key-value-entry inside of the "KARRIERE.AT"-Key. The new key is your search topic (here it is "New Topic") 
and the value is the URL you have just copied. 

```
"PLATFORMS": {
		"KARRIERE.AT": {
			"Django Python": "https://www.karriere.at/jobs/django-python/wien",
			"New Topic": "https://www.karriere.at/jobs/some-keyword/wien"
		},		
	}
```

### How can I define my own stopwords?
Simply add your own stopwords as string in config.json.
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

After that simply register the new PlatformHandler-Class in the main-function
by writing 
```
platform_registry.register_new_platform(NewPlatformHandler)
```

## Built With

- [Selenium](https://selenium-python.readthedocs.io/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
