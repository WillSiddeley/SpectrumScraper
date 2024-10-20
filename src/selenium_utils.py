import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

class SeleniumUtils:

    def __init__(self, driver: webdriver.Chrome, timeout = 20) -> None:
        # Instance variables
        self.debug = os.getenv("SELENIUM_DEBUG") is not None
        self.driver = driver
        self.timeout = timeout
        # Get the full page height and width for full page screenshots
        total_width = driver.execute_script("return document.body.scrollWidth")
        total_height = driver.execute_script("return document.body.scrollHeight")
        # Set the viewport height to the full page height
        driver.set_window_size(total_width, total_height)

    def click_element(self, element: WebElement, legacy_click = True) -> None:
        # Click the button
        if legacy_click:
            # If legacy click is enabled, use the legacy click method
            self.driver.execute_script("arguments[0].click();", element)
        else:
            # Otherwise, use the standard click method
            element.click()

    def scroll_to_element(self, element: WebElement) -> None:
        # Scroll the button into view
        self.driver.execute_script("arguments[0].scrollIntoView();", element)

    def scroll_to_and_click(self, element: WebElement, legacy_click = True) -> None:
        # Scroll to the button
        self.scroll_to_element(element)
        # Click the button
        self.click_element(element, legacy_click)

    def screenshot(self, screenshot_name: str) -> None:
        if not self.debug: return
        # Create a screenshots directory if it does not exist
        if not os.path.exists("./screenshots"):
            os.makedirs("./screenshots")
        # Take a screenshot of the current page
        self.driver.save_screenshot(f"./screenshots/{screenshot_name}.png")
        # Print the screenshot path
        print(f"Screenshot saved as ./screenshots/{screenshot_name}.png")

    def page_source(self, page_source_name: str) -> None:
        if not self.debug: return
        # Create an html directory if it does not exist
        if not os.path.exists("./html"):
            os.makedirs("./html")
        # Save the page source
        with open(f"./html/{page_source_name}.html", "w") as file:
            file.write(self.driver.page_source)
        # Print the page source path
        print(f"Page source saved as ./html/{page_source_name}.html")

    def screenshot_and_source(self, file_name) -> None:
        # Take a screenshot of the current page
        self.screenshot(file_name)
        # Save the page source
        self.page_source(file_name)