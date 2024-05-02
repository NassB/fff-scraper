import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


with open("club_logos.json", "w") as file:
    # Use the `truncate()` method to clear the file's content
    file.truncate()

# Set up Selenium WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Define the URL of the website to scrape and open it
url = 'https://isere.fff.fr/les-clubs/'
driver.get(url)

# Define the list of clubs
clubs = [
    "BALMES",
    "La BATIE MONTGASCON",
    "Le BOUCHAGE/PASSINS",
    "BOURBRE",
    "BOURGOIN ASP",
    "BOURGOIN FC",
    "BOUVESSE",
    "CASSOLARD PASSAGEOIS",
    "CESSIEU",
    "CHARVIEU CHAV",
    "CORBELIN",
    "CREMIEU",
    "CREYS MORESTEL",
    "DOLOMIEU",
    "DOMARIN",
    "l’ISLE D’ABEAU",
    "LA TOUR ST CLAIR",
    "LAUZES",
    "LES AVENIERES",
    "MEYRIE",
    "NIVOLAS",
    "ROCHETOIRIN",
    "RUY MONTCEAU",
    "SEREZIN DE LA TOUR",
    "St ANDRE LE GAZ",
    "St QUENTIN FALLAVIER",
    "TIGNIEU JAM.",
    "TURCS DE LA VERPILLERE",
    "VALLEE HIEN 38",
    "VALLEE DU GUIERS",
    "VEZERONCE/HUERT",
    "O.VILLEFONTAINE",
    "ABBAYE",
    "ASIEG",
    "BAJATIERE",
    "2 ROCHERS",
    "FC 2A",
    "GF 38",
    "GRENOBLE DAUPHINE",
    "VILLENEUVE",
    "VOREPPE",
    "ECHIROLLES FC",
    "EYBENS",
    "FONTAINE AS",
    "MISTRAL FC",
    "NOYAREY",
    "POISAT",
    "QUATRE MONTAGNES",
    "St MARTIN D’HERES",
    "SASSENAGE",
    "SEYSSINET",
    "SEYSSINS",
    "TUNISIENS SMH",
    "TURCS DE GRENOBLE",
    "U.O. PORTUGAL",
    "USVO",
    # SECTEUR PONTCHARRA
    "1.2.3 BOUGE",
    "CROLLES",
    "DOMENE",
    "FROGES",
    "GIERES",
    "GONCELIN",
    "GRESIVAUDAN",
    "MANIVAL",
    "PAYS ALLEVARD",
    "PONTCHARRA",
    "RACHAIS",
    "ST HILAIRE TOUVET",
    "ST MARTIN URIAGE",
    "TOUVET TERRASSE",
    # Add the remaining clubs here
]

# Initialize JSON object to store club logos
club_logos = {}

# List to store clubs where no result was found
failed_clubs = []

try:
    # Handle the consent popup
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
    ).click()

    # Find the input field by its placeholder attribute once
    input_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'input[placeholder="Recherchez un club par nom, ville ou CP"]'))
    )

    # Iterate through each club
    for club in clubs:
        input_field.clear()
        input_field.send_keys(club)

        # Simulate pressing Enter to load the result
        input_field.send_keys(Keys.RETURN)

        # Wait for results to be processed
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.search-results'))
        )

        # Handle no results scenario
        no_result_message_elements = driver.find_elements(By.CSS_SELECTOR, '.no_result_club')
        if no_result_message_elements and "Aucun résultat pour votre recherche" in no_result_message_elements[0].text:
            print(f"No result found for club: {club}")
            failed_clubs.append(club)
            club_logos[club] = ''
            continue
        else:
            # Retrieve the logos directly from search results without clicking
            logo_elements = driver.find_elements(By.CSS_SELECTOR, '.logo-club img')

            if logo_elements:
                logo_url = logo_elements[0].get_attribute('src')
                logo_name = driver.find_element(By.CLASS_NAME, 'name-club').text
                if logo_name:
                    print(logo_name)
                    club_logos[logo_name] = logo_url
                else:
                    club_logos[club] = logo_url
            else:
                club_logos[club] = ''

        driver.implicitly_wait(5)

finally:
    # Close the browser
    driver.quit()

    # Save the collected logos to a file
    with open('club_logos.json', 'w') as outfile:
        json.dump(club_logos, outfile, indent=4)

    # Print any clubs that failed to find results
    if failed_clubs:
        print("Failed to find results for the following clubs:")
        print(failed_clubs)
