# linkedin-targets.py (working title ;0)
---
linkedin-targets.py is a python script that aids in finding social engineering targets faster. Instead of manually searching Linkedin, this script will scrape that data for you and highlight the person's name, job title, location, time they've worked there\*, and if their profile *possibly* has a resume.

When hunting for social engineering targets, having personal knowledge of the target can be the difference between landing the hook or not. 

Hence two important pieces of output from the script:
Time at Company = New employees may be unaware of certain protocols within the company

Resume = Having knowledge of a target's education, cell phone number, work experience and volunteer expierence allows you to build a better persona when engaging with the target

The script runs for a default time of 30 seconds, this can be adjusted by passing the `--time` option.

## Usage
Using the script is very simple, however configuration can be tricky so please read below.

```
python3 linkedin-targets.py --help
```

There are really two different sets of options to choose from:

This option will fetch LinkedIn urls and export them to spreadsheet along with the person's name, job title, location, time they've worked there\*, and if their profile *possibly* has a resume.

```
python3 linkedin-targets.py --company <LinkedIn Company Name> --time 30
```
This option will do the above but also export a possible list of emails. This requires you to have some knowledge of the email address schema such as first.last etc. In the future I will look to integrate this with the Hunter API but for now, doing it based on names gathered and proposed email schema.

```
python3 linkedin-targets.py --company <LinkedIn Company Name> --time 30 --emails first.last --domain email.com
```

### Undetected-Chromedriver
---
linkedin-targets.py utilizes the undetected-chromedriver by ultrafunkamsterdam (https://github.com/ultrafunkamsterdam/undetected-chromedriver) which is an optimized version of the Selenium Chromedriver patch.

This helps in avoiding triggers from anti-bot services.

This version uses undetected-chromedriver 3.1.0, using another version may result in detection or incompatibilty.

This script was tested pretty extensively with Chromedriver version 104.0.5112.29 and a fully updated Kali Linux machine however if you encounter:
`from session not created: This version of ChromeDriver only supports Chrome version 106`

Edit the python script on line 102 to reflect your version of chromedriver/chromium 
```
browser = uc.Chrome(version_main=104) #or whatever version you're running
```

In this repo is zip file containing Chromedriver version 104.0.5112.29. Chromedriver should also be added to your $PATH.


### LinkedSocks Config
---
In this repo is a config file called LinkedSocks.py. This file must contain the credentials for your sock puppet. If you use your regualr LinkedIn, the person will be notified that "John Doe view your profile". 

Also, you must login and update the place of work to that of the target organization, this will allow you to enumerate how long they've worked at company compared to your sock puppet. (i.e John started 3 months after you did)

Credentials are pulled from this config so there is no need to edit credentials in the main script.

### Other Config
---
Other libraries used in this script can all be installed with via the requirements file
`pip install -r requirements.txt`


### Detections
---
None reported yet

If a sock puppet get's hit with the `authwall` page from LinkedIn, the account has triggered bot detections and needs to be removed from automating searches, there's a soft timeout on this but lasts about a week.

