# -*- coding: utf-8 -*- 
import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from slack import WebClient
from slack.errors import SlackApiError

logging.basicConfig(level=logging.DEBUG)


slack_token = ''
client = WebClient(token=slack_token)

url = 'https://fsmobile.ourhome.co.kr/TASystem/MealTicketSub/mobile/transit/index#/App/INTRO'
#xpath
storename = '//*[@id="wrapper"]/div[2]/div/div[6]/div/div[1]/div[1]/div/select/option' #지점명
lunchbtn = '//*[@id="wrapper"]/div[2]/div/div[6]/div/ul/div/div/li[2]/a/span' #중식 버튼
mainmenu = '//*[@id="wrapper"]/div[2]/div/div[6]/div/div[2]/div/div/ul[2]/li/span/span[1]'
menus = '//*[@id="wrapper"]/div[2]/div/div[6]/div/div[2]/div/div/ul[2]/li/ul'
webhookurl = 'https://hooks.slack.com/services/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'
mytoken = ""

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument('--headless')
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

driver.get(url)
# stale element reference: element is not attached to the page document
# 오류 때문에 sleep 추가
time.sleep(3)

WebDriverWait(driver, 3).until(
    EC.presence_of_element_located(
        (By.XPATH, storename)
    )
)
store = driver.find_element_by_xpath(storename).get_attribute("innerHTML").strip()
msg = '오늘의 점심 메뉴는 '
# 지점명이 일치하면 데이터를 가져온다
if store == "토탈소프트뱅크부산점":
    print("지점명이 일치합니다")

    WebDriverWait(driver, 3).until(
        EC.presence_of_element_located(
            (By.XPATH, mainmenu)
        )
    )

    main = driver.find_element_by_xpath(mainmenu)
    print(main.get_attribute("innerHTML"))
    msg = msg + main.get_attribute("innerHTML") + ', '
    WebDriverWait(driver, 3).until(
        EC.presence_of_element_located(
            (By.XPATH, menus)
        )
    )

    # 세부 메뉴 목록(ul > li 목록)을 불러와 합친다
    for i, e in enumerate(driver.find_element_by_xpath(menus).find_elements(By.CSS_SELECTOR, "li")):
        print(e.get_attribute("innerHTML"))
        msg = msg + e.get_attribute("innerHTML") + ', '
    msg = msg[0:-2] + ' 입니다'
else:
    msg = '지점명이 일치하지 않습니다'

driver.close()

try:
  response = client.chat_postMessage(
    channel="C01G2ML7TGF",
    text=msg
  )
except SlackApiError as e:
  # You will get a SlackApiError if "ok" is False
  assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'