import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from googletrans import Translator
import time
import re
# Initialiser le traducteur
translator = Translator()
# Configuration de Selenium
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
url = 'https://www.imdb.com/fr/title/tt2543472/reviews/?ref_=tt_ov_ql_2'
try:
    driver.get(url)  
    try:
        cookie_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="accept-button"]'))
        )
        cookie_btn.click()
    except:
        pass
    # --- 🔹 EXTRACTION DU NOM DU FILM ---
    try:
        title_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'h2[data-testid="subtitle"]'))
        )
        movie_title = title_element.text.strip()
        print(f"Nom du film : {movie_title}")
    except:
        movie_title = "Titre non trouvé"
        print("Impossible d'extraire le titre du film.")
    # --- 🔹 EXTRACTION DES COMMENTAIRES ---
    load_more_selector = 'button.ipc-see-more__button'
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, load_more_selector))
    )  
    for _ in range(3):
        try:
            btn = driver.find_element(By.CSS_SELECTOR, load_more_selector)
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(2)
        except:
            break  
    comments_selector = 'div.ipc-html-content-inner-div'
    WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, comments_selector))) 
    comments = []
    for element in driver.find_elements(By.CSS_SELECTOR, comments_selector):
        text = element.text.strip()
        if text:
            try:
                translated = translator.translate(text, src='en', dest='fr').text
                comments.append(translated)
            except:
                comments.append(text)
    # Sauvegarde avec le titre du film
    df = pd.DataFrame({'Commentaires': comments})
    filename_safe_title = re.sub(r'[\\/*?:"<>|]', "_", movie_title)
    df.to_csv(f'commentaires_{filename_safe_title.replace(" ", "_")}.csv', index=False)
    print(f"{len(comments)} commentaires sauvegardés pour '{movie_title}'.")

finally:
    driver.quit()
