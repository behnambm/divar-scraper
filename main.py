import os
import csv
import re
import time
from urllib.parse import unquote

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import requests
from bs4 import BeautifulSoup
from telegram.ext import Updater
from fake_useragent import UserAgent
from telegram.ext import Updater


url = 'https://divar.ir/s/urmia/it-computer-jobs'
python_django_exp = r'(react|reactjs|python|django|flask|پایتون|جنگو|فلسک)'
TOKEN = os.environ['BOT_TOKEN']
ua = UserAgent()
# ===========================================

options = Options()
options.headless = True
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(options=options)

# ===========================================

driver.get(url)

WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, '.browse-post-list .post-card-item'))
)

# to hold ad card elements
job_links = []


# scroll down and save links until the end 
initial_height = 300
while True:
    cards = driver.find_elements_by_css_selector('.browse-post-list .post-card-item')

    for card in cards:  # extract url of each card
        job_links.append(card.find_element_by_tag_name('a').get_attribute('href'))

    driver.execute_script(f"window.scrollTo(0, {initial_height})")
    time.sleep(1)
    next_height = driver.execute_script("return document.body.scrollHeight")

    if next_height <= initial_height:
        break
    
    initial_height += 500


# remove duplicates in links list
job_links = list(dict.fromkeys(job_links))


# read the links that have been checked
readed_file = open('path_to_saved_links.csv', newline='')
csv_reader = csv.reader(readed_file)
checked_links = [i[0] for i in csv_reader]  # get index which is a str (link)


for link in job_links: # check all links one by one 
    if link in checked_links:
        continue
    
    resp = requests.get(link, headers={'User-Agent': ua.firefox})
    
    if resp.status_code != 200:
        continue

    soup = BeautifulSoup(resp.content, 'html.parser')

    description = soup.select_one('.kt-description-row__text--primary') 
    if not description:
        continue

    description = description.text

    if re.findall(python_django_exp, description, flags=re.IGNORECASE):
        # send alert to the channel
        updater = Updater(token=TOKEN)

        msg = f"🔥 New Job 🔥\n\n " + unquote(link)
        updater.bot.send_message(chat_id='@YOUR_CHANNEL_ID', text=msg)

    with open('path_to_saved_links.csv', 'at') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow([link])

