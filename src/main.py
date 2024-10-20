import os
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import docker
import docker.errors

def scrape_license_data(geocode, filename):
    """
    Scrapes license data using a Docker container.

    This function pulls the latest Docker image for the Spectrum Scraper,
    runs the container with the specified environment variables, and prints
    the logs from the container.

    Args:
        geocode (str): The geographic code to be used by the scraper.
        filename (str): The name of the file where the scraped data will be saved. The file name DOES NOT need a file extention.

    Raises:
        docker.errors.APIError: If there is an error pulling the Docker image.

    Example:
        scrape_license_data("TEL-002", "output")
    """
    client = docker.from_env()
    image_name = "deathyvoid/spectrum-scraper:0.0.1"
    try:
        # Try to pull the latest image
        client.images.pull(image_name)
    except docker.errors.APIError as e:
        # Log the error and continue
        print(f"Failed to pull the latest image: {e}")

    # Run the Docker container with the specified environment variables
    container = client.containers.run(
        image_name,
        environment={"GEO_CODE": geocode, "FILE_NAME": filename},
        volumes={os.getcwd(): {'bind': '/app', 'mode': 'rw'}},
        detach=True,
    )

    # Wait for the container to finish
    logs = container.logs(stream=True)
    for line in logs:
        print(line.decode('utf-8').strip())

    # Print the container logs
    print(container.logs().decode('utf-8'))

def main(geo_code: str, filename: str = "output") -> None:
    # Get the filename without the extension
    filename = os.path.splitext(filename)[0]

    # Create file paths
    log_file_name = f"./logs/{filename}.log"
    csv_file_path = f"./output/{filename}.csv"

    # Create directories that do not exist
    if not os.path.exists("./logs"):
        os.makedirs("./logs")
    if not os.path.exists("./output"):
        os.makedirs("./output")

    # Create a logger object
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s - %(levelname)s]: %(message)s',
        filename=log_file_name,
        filemode='w' if os.path.exists(log_file_name) else 'a'
    )
    logger = logging.getLogger(__name__)

    # Set up Chrome WebDriver options
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Path to the ChromeDriver executable
    webdriver_service = Service('/usr/bin/chromedriver')

    # Function to log an assertion error
    def log_assert(condition, message):
        try:
            # Assert the condition
            assert condition, message
        # Catch all assertion errors
        except AssertionError as e:
            logger.error(e)
            # Re-raise the error
            raise e

    # Function to both log and print a message
    def log_print(message):
        # Log the message
        logger.info(message)
        # Print the message
        print(message, flush=True)

    # Initialize an empty DataFrame
    df = pd.DataFrame()

    # Create the CSV file with the headers
    if not os.path.exists(csv_file_path):
        df.to_csv(csv_file_path, mode='w', header=True, index=False)

    try:
        found_rows = 0

        # Sleep for 5 seconds to avoid getting blocked
        time.sleep(5)

        # Log the current geocode
        log_print(f"Processing geocode: {geo_code}")

        # Initialize the WebDriver
        driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

        # Instantiate SeleniumUtils
        selenium_utils = SeleniumUtils(driver)

        # Navigate to the target webpage
        driver.get('https://sms-sgs.ic.gc.ca/licenseSearch/searchSpectrumLicense')

        # Take page source after page load
        selenium_utils.page_source("page_load")

        # Wait for the page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "lookupLicenceArea")))

        # Locate the "Lookup" button by its ID
        lookup_button = driver.find_element(By.ID, "lookupLicenceArea")

        # Scroll and click the button
        selenium_utils.scroll_to_and_click(lookup_button)

        # Take page source after button click
        selenium_utils.page_source("lookup")

        # Wait for the page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "GeoCode")))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "searchTierButton")))

        # Locate the area code name by its ID
        area_code = driver.find_element(By.ID, "GeoCode")

        # Scroll the area code name into view
        selenium_utils.scroll_to_and_click(area_code)

        # Type area code into the form field
        driver.execute_script(f"arguments[0].value = '{geo_code}';", area_code)

        # Locate the submit button by its ID
        submit_button = driver.find_element(By.ID, "searchTierButton")

        # Scroll and click the button
        selenium_utils.scroll_to_and_click(submit_button)

        # Take page source after button click
        selenium_utils.page_source("area_code_fill")

        # Wait for the results <table> element to show up
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "tierTable")))

        desired_element = None
        # Loop over the table rows until a <td> element with the text `geo_code` is found
        for row in driver.find_elements(By.XPATH, "//table[@id='tierTable']/tbody/tr/td"):
            # Get the <td> elements in the row
            a = row.find_elements(By.TAG_NAME, "a")
            # Check if the first <a> element contains the `geo_code`
            if a and a[0].get_attribute('innerHTML') == geo_code:
                # Print the row and break the loop
                log_print(f"Located the row with the area code: {geo_code}")
                # Save the desired element
                desired_element = a[0]
                # Break the loop
                break

        # Skip to the next geocode if the desired element is not found
        if desired_element is None:
            raise Exception(f"Could not locate the row with the area code: {geo_code}")

        # Scroll and click the desired element which is the <a> element
        selenium_utils.scroll_to_and_click(desired_element)

        # Wait for the page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "lookupLicenceArea")))
        selenium_utils.page_source("area_code_click")

        # Locate the submit button by its ID
        search_button = driver.find_element(By.ID, "searchLicenceButton")

        # Scroll and click the search button
        selenium_utils.scroll_to_and_click(search_button)

        selenium_utils.page_source("search_button_click")
        
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "spectrumLicenceSearchResultTable")))

        # Get the text of the number of total results above the table
        total_results = driver.find_element(By.XPATH, "//section[@id='search-result']/div/div/div[@class='form-group']")

        # Get the inner text of the element
        total_results_text = total_results.get_attribute('innerText')
        log_assert(total_results_text is not None, "Total results text is empty")
        
        # Get the number of results of rows across all pages
        num_results = int(total_results_text.split("Total number of results: ")[-1]) # type: ignore
        log_print(f"Geocode {geo_code} has total number of results: {num_results}")

        # If there are no results, raise an exception
        if num_results == 0:
            raise Exception(f"No results found for geocode: {geo_code}")

        # The table is paginated, so we need to loop over each page to retrieve all the data
        pages = driver.find_elements(By.XPATH, "//section/div/ul[@class='pagination']/li[not(contains(@class, 'disabled'))]/a[not(contains(text(), 'Next'))]")
        log_print(f"Number of pages found for geocode {geo_code}: {len(pages)}")

        # Get the number of pages
        num_pages = len(pages) if len(pages) > 0 else 1
        
        selenium_utils.page_source("each_page")

        # Click on each page
        for index in range(num_pages):
            log_print(f"Processing page: {index + 1} for geocode: {geo_code}")
            # If on the first page, the page is already loaded
            if index != 0:
                # Re-locate the page element to avoid stale element reference
                page = driver.find_element(By.XPATH, f"//section/div/ul[@class='pagination']/li[not(contains(@class, 'disabled'))]/a[contains(text(), '{index + 1}')]")
                # Scroll and click on the next page
                selenium_utils.scroll_to_and_click(page)
                # Wait for the page to load
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "spectrumLicenceSearchResultTable")))
            # Dump the page source
            selenium_utils.page_source(f"page_{index + 1}_click")
            # Get each row in the table
            rows = driver.find_elements(By.XPATH, "//table[@id='spectrumLicenceSearchResultTable']/tbody/tr")
            for row in rows:
                data_row: list[str] = []
                # Get all the <td> elements in the row
                cells = row.find_elements(By.TAG_NAME, "td")
                # Loop over all the cells to get info from each cell
                for cell in cells:
                    elem_text = None
                    # Check if the cell has a nested <a> tag
                    # Nested <a> tag means its the cell with the authorization number
                    if cell.find_elements(By.TAG_NAME, "a"):
                        # Get the element reference 
                        a = cell.find_element(By.TAG_NAME, "a")
                        # Get the authorization number raw text
                        elem_text = a.get_attribute('innerText')
                    else:
                        # Get the inner text of the cell
                        elem_text = cell.get_attribute('innerText')
                    # Sanitization of the cell contents
                    if elem_text: 
                        # Remove leading / trailing whitespace and control characters
                        sanitized = elem_text.strip(' \t\n\r')
                        # Replace commas with a space or another character to prevent column splitting
                        sanitized = sanitized.replace(",", "")
                        # Remove any additional characters that might interfere with the CSV structure
                        sanitized = sanitized.replace('"', "'").replace(";", " ")
                        # Split the text by newline
                        data_row += sanitized.split("\n")
                found_rows += 1
                # Append the row to the DataFrame and write to CSV
                pd.DataFrame([data_row]).to_csv(csv_file_path, mode='a', header=False, index=False)
        # Assert the number of results is the same as the number of data rows
        log_assert(num_results == found_rows, f"Number of results: {num_results} does not match the number of data rows: {found_rows}")
    except Exception as e:
        logger.error(e)
    finally:
        driver.quit()
    # Print final message
    log_print(f"Finished processing geocode: {geo_code}")

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

if __name__ == "__main__":
    # Get the geocode from the environment variable
    geo_code = os.getenv("GEO_CODE")
    file_name = os.getenv("FILE_NAME")
    # Raise an exception if the geocode is not set
    if geo_code is None:
        raise Exception("GEO_CODE environment variable is not set")
    # Call the main function with the geocode
    main(geo_code, file_name or "output")