import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


SLEEP_BETWEEN_PAGES = 5


def get_driver() -> WebDriver:
    chrome_path = "/usr/local/bin/chromedriver"

    options = Options()
    options.headless = False

    caps = DesiredCapabilities.CHROME
    caps["goog:loggingPrefs"] = {"performance": "ALL"}

    driver = webdriver.Chrome(chrome_path, options=options, desired_capabilities=caps)
    driver.get("https://www.geoguessr.com")
    driver.implicitly_wait(SLEEP_BETWEEN_PAGES)
    return driver


def login(driver: WebDriver):
    with open("./cookies.json", "r") as f:
        cookies = json.load(f)
    cookies_to_set = ["G_ENABLED_IDPS", "_ncfa", "devicetoken"]
    for cookie_name in cookies_to_set:
        driver.add_cookie({"name": cookie_name, "value": cookies[cookie_name]})

    driver.get("https://www.geoguessr.com/streaks")
    accept_cookies = driver.find_element(By.XPATH, "//div[@id='accept-choices']")
    accept_cookies.click()


def launch_game(driver: WebDriver):
    country_streaks = driver.find_element(
        By.XPATH, "//a[@data-qa='play-country-streak']"
    )
    country_streaks.click()

    play_button = driver.find_element(
        By.XPATH, "//button[@data-qa='start-streak-game-button']"
    )

    play_button.click()
    time.sleep(SLEEP_BETWEEN_PAGES)
