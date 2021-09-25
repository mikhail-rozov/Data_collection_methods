from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from pymongo import MongoClient


driver = webdriver.Chrome(executable_path='./chromedriver.exe')
driver.get('https://mail.ru/')
with open('./password.txt', 'r') as f:
    lgn = f.readline()
    pswd = f.readline()

# Убираем галочку "Запомнить":
remember_checkbox = driver.find_element_by_xpath("//input[@id='saveauth']")
remember_checkbox.click()

login = driver.find_element_by_xpath("//input[@name='login']")
login.send_keys(lgn)
login.send_keys(Keys.ENTER)

wait = WebDriverWait(driver, 10)
password = wait.until(expected_conditions.element_to_be_clickable((By.XPATH, "//input[@name='password']")))
password.send_keys(pswd)
password.send_keys(Keys.ENTER)

urls = set()
span = None

while True:
    wait = WebDriverWait(driver, 10)
    links = wait.until(expected_conditions.presence_of_all_elements_located(
        (By.XPATH, "//a[contains(@class, 'js-letter-list-item')]")))

    # Выходим из цикла, если последняя ссылка не поменялась после прокрутки:
    if span == links[-1]:
        break

    for link in links:
        urls.add(link.get_attribute('href'))
    span = links[-1]
    actions = ActionChains(driver)
    actions.move_to_element(links[-1]).perform()

client = MongoClient('localhost', 27017)
db = client.emails
collection = db.mail_ru

urls = list(urls)

for url in urls:
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    sender = wait.until(expected_conditions.presence_of_element_located(
        (By.XPATH, "//div[@class='letter__author']/span"))).text
    sent = wait.until(expected_conditions.presence_of_element_located(
        (By.XPATH, "//div[@class='letter__date']"))).text
    subject = wait.until(expected_conditions.presence_of_element_located(
        (By.XPATH, "//h2[@class='thread__subject']"))).text
    letter_text = wait.until(expected_conditions.presence_of_element_located(
        (By.XPATH, "//div[@class='letter__body']"))).text

    collection.update_one({'_id': url}, {'$set': {'_id': url,
                                                  'sender': sender,
                                                  'sent': sent,
                                                  'subject': subject,
                                                  'text': letter_text}}, upsert=True)
