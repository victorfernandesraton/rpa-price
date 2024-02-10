from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait, time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


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
        for product in products:
            try:
                search_input = WebDriverWait(
                    self.drivers[driver_key], timeout=20
                ).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "input#twotabsearchtextbox")
                    )
                )
                search_input.send_keys(product)
                time.sleep(3)

            except TimeoutException:
                print("not found text input")

            try:
                button_submit = WebDriverWait(
                    self.drivers[driver_key], timeout=20
                ).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "input#nav-search-submit-button")
                    )
                )
                button_submit.click()
            except TimeoutException:
                print("not found submit button")

            # search for products
            # get 3 first
            # create in memory list
            # go to page and get content for each one
