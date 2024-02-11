import time
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import pandas as pd
from decouple import config


class BaseScrapper:
    def __init__(self) -> None:
        self.drivers: dict[str, WebDriver] = {}

    def open_browser(self):
        opts = webdriver.ChromeOptions()
        driver = webdriver.Remote(options=opts)
        if not driver.session_id:
            raise Exception("Not able to regisrer a driver")
        driver.maximize_window()
        self.drivers[driver.session_id] = driver

        return driver.session_id


class AmazonScrapper(BaseScrapper):
    def __init__(self) -> None:
        super().__init__()
        self.url = "https://wwww.amazon.com.br"

    def execute(self, products: list[str]):
        driver_key = self.open_browser()
        self.drivers[driver_key].get(self.url)
        self.set_delivery_by_zipcode(driver_key, config("ZIPCODE"))
        content_wait = WebDriverWait(self.drivers[driver_key], timeout=20)
        card_content = []
        result = []
        for product in products:
            # search for products
            try:
                search_input = content_wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "input#twotabsearchtextbox")
                    )
                )
                search_input.send_keys(product)
                time.sleep(3)

            except TimeoutException:
                print("not found text input")

            try:
                button_submit = content_wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "input#nav-search-submit-button")
                    )
                )
                button_submit.click()
            except TimeoutException:
                print("not found submit button")

            # get 3 first
            try:
                card_content = content_wait.until(
                    EC.presence_of_all_elements_located(
                        (
                            By.XPATH,
                            "//*[@id='search']/div[1]/div[1]/div/span[1]/div[1]/div[@data-component-type='s-search-result']",
                        )
                    )
                )

            except TimeoutException:
                print("not found any result")

            # create in memory list
            if not len(card_content):
                print("not found any result")
            elif len(card_content) > 3:
                card_content = card_content[0:2]

            card_content = [
                self.get_data_from_card(result.get_attribute("outerHTML"))
                for result in card_content
            ]
            # go to page and get content for each one
            for card in card_content:
                print(f"Go to {card.get('name')}")
                self.drivers[driver_key].get(f"{self.url}{card.get('link')}")
                complete_data = self.get_data_from_static_page(
                    self.drivers[driver_key].page_source
                )
                result.append({**card, **complete_data})

    @staticmethod
    def get_data_from_card(html: str) -> dict:
        soup = BeautifulSoup(html, "html.parser")

        # Extrair o nome do produto
        product_name = soup.find("h2").get_text()
        # Extrair o link de acesso
        product_link = soup.find("a", {"class": "a-link-normal s-no-outline"}).get(
            "href"
        )

        result = {"name": product_name, "link": product_link}

        return result

    @staticmethod
    def get_data_from_static_page(html: str) -> dict:
        soup = BeautifulSoup(html, "html.parser")
        price = soup.select_one("div#apex_desktop span.a-price").text
        name = soup.select_one("h1#title").text
        spec_table = soup.select_one("table#productDetails_techSpec_section_1").text
        spec_df = pd.read_html(spec_table)

    def set_delivery_by_zipcode(self, driver_key: str, zipcode: str) -> str:
        change_zipcode = WebDriverWait(self.drivers[driver_key], timeout=20).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[@id='nav-global-location-popover-link']")
            )
        )

        time.sleep(5)

        change_zipcode.click()

        time.sleep(5)

        inputs_xpath = [
            "//input[@id='GLUXZipUpdateInput_0']" "//input[@id='GLUXZipUpdateInput_1']"
        ]

        splited_zipcode = zipcode.split("-")
        for idx, value in enumerate(splited_zipcode):
            zipcode_input = WebDriverWait(self.drivers[driver_key], timeout=20).until(
                EC.presence_of_element_located((By.XPATH, inputs_xpath[idx]))
            )
            time.sleep(2)
            zipcode_input.send_keys(value)
            time.sleep(4)
