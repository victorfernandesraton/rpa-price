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
        content_wait = WebDriverWait(self.drivers[driver_key], timeout=20)
        result_list = []
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
                result_list = content_wait.until(
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
            if not len(result_list):
                print("not found any result")
            elif len(result_list) > 3:
                result_list = result_list[0:2]
            # go to page and get content for each one
