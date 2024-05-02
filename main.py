import json
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def fetch_zip_codes():
    """
    Fetches zip codes from a government API for a specific department.
    Returns a list of zip codes if successful, an empty list otherwise.
    """
    response = requests.get('https://geo.api.gouv.fr/departements/38/communes/')
    if response.status_code == 200:
        return [zip_code for item in response.json() if 'codesPostaux' in item for zip_code in item['codesPostaux']]
    return []


def setup_webdriver():
    """
    Sets up and returns a Selenium WebDriver.
    Uses ChromeDriverManager to handle the installation of the ChromeDriver if necessary.
    """
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service)


def main():
    """
    Main function to orchestrate the fetching of zip codes, setting up WebDriver, and scraping the club logos.
    Logs club logos to a JSON file and outputs any zip codes that failed to yield results.
    """
    zip_codes = fetch_zip_codes()
    if not zip_codes:
        print("No zip codes found, exiting.")
        return

    driver = setup_webdriver()
    url = 'https://isere.fff.fr/les-clubs/'
    driver.get(url)

    club_logos = {}
    failed_zip_codes = []

    try:
        # Click to agree on the consent popup
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
        ).click()

        # Wait for the search input field and store it for reuse
        input_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[placeholder="Recherchez un club par nom, ville ou CP"]'))
        )

        for zip_code in zip_codes:
            print(f"Processing zip code: {zip_code}")
            input_field.clear()
            input_field.send_keys(zip_code)
            input_field.send_keys(Keys.RETURN)

            # Handle search results or the absence thereof
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'search-results'))
                )
                search_club_lists = driver.find_elements(By.CSS_SELECTOR, '.search-club-list')
                for club in search_club_lists:
                    logo_url = club.find_element(By.CSS_SELECTOR, 'img').get_attribute('src')
                    club_name = club.find_element(By.CLASS_NAME, 'name-club').text
                    if club_name and logo_url:
                        club_logos[club_name] = logo_url
            except Exception as e:
                print(f"No result or error for zip code: {zip_code}")
                failed_zip_codes.append(zip_code)

    finally:
        # Clean up by closing the browser once done
        driver.quit()

        # Save the collected club logos to a JSON file
        with open('club_logos.json', 'w') as outfile:
            json.dump(club_logos, outfile, indent=4)

        if failed_zip_codes:
            print("Failed to find results for the following zip codes:")
            print(failed_zip_codes)


if __name__ == "__main__":
    main()
