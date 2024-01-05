#/usr/bin/python3 
#linkedin-targets.py

from bs4 import BeautifulSoup
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from datetime import datetime
import random
import argparse
import re
import csv
import pandas as pd
import time
import warnings 
import sys
from LinkedSocks import sockSecrets

#Print the ASCII art
with open('banner.txt', 'r') as f:
	for line in f:
		print(line.rstrip())

#Initialize argparse
parser = argparse.ArgumentParser(fromfile_prefix_chars='@')

#Load arguments
parser.add_argument('--company', type=str, required=True, help='target organization')
parser.add_argument('--time', required =True, type=int, help='seconds to scroll the people page of the company on Linkedin. Default = 30, Max = 200')
parser.add_argument('--emails', required=False, type=str, help='generate list of emails \n\t --emails "first.last" \n\t --emails "f.last" \n\t --emails "flast"')
parser.add_argument('--domain', required=False, type=str, help='email domain suffix (e.g. "gmail.com", "yahoo.com")')

#Parse the arguments
args = parser.parse_args()

#Written in older version of Selenium, ignoring deprecation warnings for clean console
#Will update in future release
warnings.filterwarnings("ignore", category=DeprecationWarning)

#Getting and formatting target organization
company = args.company
company = company.replace(" ", "-")


#If --emails wasn't supplied
emailFormat = " "
emailDomain = " "

if args.emails:
	emailFormat = args.emails
	emailDomain = '@' + args.domain
else:
	pass

#Default scroll time if no value given
if args.time:
	if args.time > 200:
		print('[+] You exceeded the maximum scroll time')
		print('[+] python3 linkedin-targets.py -h')
		sys.exit(1)
	elif args.time < 30:
		print('[+] You entered a value below the default, setting scrollTime to 30')
		scrollTime = 30
	elif args.time in range(30,200):
		scrollTime = args.time
else:
	scrollTime = 30

#Setting up User Agents
ua = UserAgent()
userAgent = ua.random

#Setting up some global variables
profileCount = 0
uaCounter = 0
names = []
totalURLs = []
finalURLs = []
firstNames = []
lastNames = []
emails = []
temp = []
n = 0
isPDF = "pdf"
isResume = "Resume"
startedWhen = "before you did"

#Setting up our output files
currentTime = datetime.now()
filePrefix = currentTime.strftime('%d-%m-%Y-%H-%M-%S')
csvHeaders = ['Name', 'Job Title', 'Location', 'Time at Company', 'Possible Resume']
saveFile = open(f'{filePrefix}-results.csv', 'w', newline='')
writer = csv.writer(saveFile)
writer.writerow(csvHeaders)

#Printing company here to verify we're searching the correct org
print(f"[+] Fetching {company} profiles from Linkedin!")

#Instatiate the browser and log into LinkedIn
options = Options()
browser = uc.Chrome(version_main=104)
options.add_argument(f'user-agent={userAgent}')
print(f'[+] User Agent set as {userAgent}')
browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
browser.maximize_window()
browser.get("https://linkedin.com/uas/login")

#Uncomment below if browser/connection is slow and adjust sleep time accordingly
time.sleep(3)

#Logging into LinkedIn 
username = browser.find_element_by_id("username")
username.send_keys(sockSecrets.get('username'))
time.sleep(2.4)  
password = browser.find_element_by_id("password")
password.send_keys(sockSecrets.get('password'))
time.sleep(1.1)        
browser.find_element_by_xpath("//button[@type='submit']").click()

#Searching LinkedIn
browser.get(f"https://www.linkedin.com/company/{company}/people/")
start = time.time()

#Initializing some values here to scroll the page
#Because the LinkedIn people page loads more when scrolling to the bottom
#This while loop will continue for a predetermined amount of time
#Increase to scrape more and decrease to scrape less
#Default = 30 (time is in seconds)
startPoint = 0
endPoint = 1100

while True:
    browser.execute_script(f"window.scrollTo({startPoint}, {endPoint})")

    initialScroll = endPoint
    endPoint += 1000
	
	#Pausing briefly so the data can load
	#Adjust sleep time accordingly
    time.sleep(3)
    end = time.time()

	#Scroll for 30 seconds (default)
    if round(end - start) > int(scrollTime):
        break

#Gathering all elements on page with tagname <a>
lnks=browser.find_elements_by_tag_name("a")
#Looking through each <a> and grabbing the href link 
for lnk in lnks:
	href = lnk.get_attribute('href')
	totalURLs.append(href)

#Cleaning up all the urls to remove duplicates and non linkedin profiles
for i in totalURLs:
	if i[25:27] == "in":
		finalURLs.append(i)

#Declaring variable for use here
outputURLs = [*set(finalURLs)]

#If you want to print URLs to terminal - uncomment here
#print(f"Printing {company} LinkedIn profile URLs")
#for k in outputURLs:
#	print(k)

#Dump into csv
df = pd.DataFrame(data={"LinkedIn URLs": outputURLs})
df.to_csv(f"./{filePrefix}-LinkedInURLS.csv", sep=',',index=False)

#Sleep before jumping into scrape
countOf = len(outputURLs)
print(f"[+] {countOf} URLs gathered for {company}")
print("[+] Sleeping for 30 seconds...")
time.sleep(10)
print("[+] 20 seconds...")
time.sleep(10)
print("[+] 10 seconds...")
time.sleep(10)
print("[+] Scraping started!")

#Defining some other global variables
profileCount = 0
isHere = 0
totalCount = len(outputURLs)

while profileCount < len(outputURLs):

	#Some terminal checks to show you we're still working
	if profileCount == (len(outputURLs)/4):
		print('[+] 25% Completed')
	elif profileCount == (len(outputURLs)/2):
		print('[+] 50% Completed')
	elif profileCount == (len(outputURLs)/1.25):
		print('[+] 80% Completed')
	elif profileCount == (len(outputURLs) - 1):
		print('[+] Wrapping up')
	else:
		pass

	#Debug
	#print(f"Visiting URL #{profileCount}")
	
	isHere = isHere + 1

	if isHere == 10:
		print(f'[+] Still working! Current status is {profileCount} out of {totalCount} URLs scraped')
		isHere = 0

	#Grab profile to scrape
	profile = outputURLs[profileCount]

	####Testing profiles####
	#profile = "https://www.linkedin.com/in/matthew-abbott-866181247/"
	#profile = "https://www.linkedin.com/in/damonyargeau/"
	####Testing profiles####
	
	#Increment counter variables
	uaCounter = uaCounter + 1
	profileCount = profileCount + 1

	#Request profile and get source code
	browser.get(profile)

	#Randomzie sleep
	sleepValue = random.uniform(0.2,3.7)
	time.sleep(sleepValue)

	#Grab page source for BS4
	pSource = browser.page_source

	#Initilize BS4
	soup = BeautifulSoup(pSource, 'lxml')
	
	#Pull section of source where name and location is // also grabbing job title
	name = soup.find('div', {'class': 'pv-text-details__left-panel'})
	

	#Find the name and clean up the text
	nameLocation = name.find("h1")
	name = nameLocation.get_text().strip()

	jobTitleLocation = soup.find('div', {'class': 'text-body-medium break-words'})
	jobTitle = jobTitleLocation.get_text().strip()

	#Array used for email generation
	temp = name.split()
	firstNames.append(temp[0])
	lastNames.append(temp[1])
	names.append(name)

	#Rinse and repeat for location
	location = soup.find('div', {'class': 'pv-text-details__left-panel pb2'})
	location_loc = soup.find_all("span", {'class': 'text-body-small inline t-black--light break-words'})
	location = location_loc[0].get_text().strip()

	#A bit different for the overlay section
	overlay = soup.find('div', {'class': 'pvs-media-content__preview flex-1'})

	#Grabbing all visually hidden elements
	overlay_loc = soup.find_all("span", {'class': 'visually-hidden'})

	#Decalring some local variables
	timeAtCompany = " "
	exists = " "

	for i in range(len(overlay_loc)):
		overlay_stripped = overlay_loc[i].get_text().strip()

		#Want more information, uncomment below and comment out rest of for loop
		#print(overlay_stripped)

		if startedWhen in overlay_stripped:
			#Pulling out the "...started X months before you did..." line
			timeAtCompany = overlay_stripped
		else:
			pass

		if overlay_stripped[-3:] == isPDF or isResume in overlay_stripped:
			#Checking the featured overlay for the word Resume and .pdf extension
			exists = "X"
		else:
			pass
	
	#Write row to csv
	writer.writerow([name, jobTitle, location, timeAtCompany, exists])
	#Write it now
	saveFile.flush()

if args.emails:
	if emailFormat == 'first.last':
		while n < len(names):
			temp = names[n]
			tempEmail = re.sub("[ ]", ".", temp)
			email = tempEmail + emailDomain
			emails.append(email)
			n = n + 1
	
	elif emailFormat == 'f.last':
		while n < len(names):
			temp = names[n]
			tempArray = temp.split()
			emailPrefix = temp[0]
			email = emailPrefix + '.' + tempArray[1] + emailDomain
			emails.append(email)
			n = n + 1
	
	elif emailFormat == 'flast':
		while n < len(names):
			temp = names[n]
			tempArray = temp.split()
			emailPrefix = temp[0]
			email = emailPrefix + tempArray[1] + emailDomain
			emails.append(email)
			n = n + 1

df = pd.DataFrame(data={"Emails": emails})
df.to_csv(f"./{filePrefix}-Emails.csv", sep=',',index=False)

print('[+] Files created:')
print(f'\t{filePrefix}-Emails.csv')
print(f'\t{filePrefix}-LinkedInURLs.csv')
print(f'\t{filePrefix}-results.csv')
print('[+] All done! ( ͡° ͜ʖ ͡°)')