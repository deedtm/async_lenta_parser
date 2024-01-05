import json
from logging import info
import time
from selenium import webdriver
from multiprocessing import Pool
from bs_parse import get_stock_value
from fake_useragent import UserAgent

options = webdriver.FirefoxOptions()
options.set_preference("general.useragent.override", UserAgent().random)
options.add_argument("--headless")


def get_driver(store_id: str, city_key: str):
    driver = webdriver.Firefox(options=options, service=webdriver.FirefoxService(r'geckodriver\geckodriver.exe'))
    driver.get('https://lenta.com')

    with open("request_data.json", "r") as f:
        cookies: dict = json.load(f)["cookies"]
    cookies["StoreSubDomainCookie"] = store_id
    cookies["Store"] = store_id
    cookies["CityCookie"] = city_key
    cookies["CitySubDomainCookie"] = city_key

    for cookie_name, cookie_value in cookies.items():
        driver.add_cookie({'name': cookie_name, 'value': cookie_value})
    driver.refresh()

    return driver


def close_driver(driver: webdriver.Firefox):
    driver.close()
    driver.quit()



def get_stock(url: str, driver: webdriver.Firefox):
    driver.get(url)
    info(msg=url)
    time.sleep(1.1)
    return get_stock_value(driver.page_source)

