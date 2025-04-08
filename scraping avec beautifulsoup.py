import pandas as pd
import requests
from bs4 import BeautifulSoup

url = 'https://www.imdb.com/title/tt0468569/reviews/?ref_=tt_urv'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    commentaires = []    
    # Trouver toutes les balises contenant les commentaires
    cm_data = soup.findAll('div', attrs={'class': 'ipc-html-content-inner-div'})    
    # Extraire le texte de chaque commentaire
    for store in cm_data:
        commentaires.append(store.text.strip())
    # Créer un DataFrame pandas
    commentaires_df = pd.DataFrame({'Commentaire': commentaires})
    # Sauvegarder les commentaires dans un fichier CSV
    commentaires_df.to_csv('commentaires2.csv', index=False, encoding='utf-8')  
    print("Extraction réussie. Les commentaires ont été enregistrés dans 'commentaires.csv'.")
else:
    print(f"Erreur : impossible d'accéder à la page. Code de statut {response.status_code}")
