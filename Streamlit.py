import os
import zipfile
import pandas as pd
import streamlit as st
from textblob import TextBlob
import plotly.express as px
ZIP_PATH = "./films.zip"
@st.cache_data
def load_all_data(zip_path):
    all_data = []
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file_name in zip_ref.namelist():
            if file_name.endswith('.csv'):
                with zip_ref.open(file_name) as f:
                    df = pd.read_csv(f)
                    df['Film'] = os.path.splitext(os.path.basename(file_name))[0]
                    all_data.append(df)
    combined = pd.concat(all_data, ignore_index=True)
    return combined
@st.cache_data
def add_sentiment_column(data):
    def analyze(comment):
        polarity = TextBlob(str(comment)).sentiment.polarity
        return 'Positive' if polarity > 0 else 'Negative' if polarity < 0 else 'Neutral'
    data['Sentiment'] = data['Commentaires'].apply(analyze)
    data['Polarity'] = data['Commentaires'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
    return data

# App principale
def main():
    st.set_page_config(page_title="Analyse Sentiments IMDb", layout="wide")
    st.sidebar.title("📊 Navigation")
    page = st.sidebar.selectbox("Choisissez une vue :", ["Vue Globale", "Analyse par Film"])
    data = add_sentiment_column(load_all_data(ZIP_PATH))
    films = sorted(data['Film'].unique())
    if page == "Vue Globale":
        st.title("🎬 Vue Globale - Analyse des Sentiments")
        st.markdown("Analyse comparative entre tous les films disponibles dans l’échantillon.")
        selected_films = st.multiselect("🎞️ Films à comparer :", films, default=films)
        filtered_data = data[data['Film'].isin(selected_films)]
        st.metric("🗂️ Total de commentaires analysés", len(filtered_data))
    # === Nouvelle table de statistiques par film ===
        st.subheader("📈 Statistiques par Film")
        stats_df = filtered_data.groupby('Film').agg(
            Total=('Sentiment', 'count'),
            Positifs=('Sentiment', lambda x: (x == 'Positive').sum()),
            Negatifs=('Sentiment', lambda x: (x == 'Negative').sum()),
            Neutres=('Sentiment', lambda x: (x == 'Neutral').sum()),
           
        ).reset_index()
        stats_df['% Positifs'] = (stats_df['Positifs'] / stats_df['Total'] * 100).round(2)
        stats_df['% Négatifs'] = (stats_df['Negatifs'] / stats_df['Total'] * 100).round(2)
        stats_df['% Neutres'] = (stats_df['Neutres'] / stats_df['Total'] * 100).round(2)
        st.dataframe(stats_df.sort_values(by='% Positifs', ascending=False), use_container_width=True)
    # === Classement TOP 3 ===
        st.subheader("🏆 Top 3 des Films par Sentiment Positif")
        top_films = stats_df.sort_values(by='% Positifs', ascending=False).head(3)
        for i, row in top_films.iterrows():
            st.success(f"{row['Film']} - {row['% Positifs']}% Positifs")
    # === Graphique en barres empilées ===
        st.subheader("📊 Répartition des sentiments par Film")
        fig = px.histogram(
            filtered_data,
            x="Film",
            color="Sentiment",
            barmode="group",
            text_auto=True,
            color_discrete_map={"Positive": "green", "Negative": "red", "Neutral": "gray"},
            title="Répartition des sentiments entre films"
        )
        st.plotly_chart(fig, use_container_width=True)

    elif page == "Analyse par Film":
        st.title("🔎 Analyse Détail par Film")
        selected_film = st.selectbox("🎞️ Choisissez un film :", films)
        film_data = data[data['Film'] == selected_film]
        st.subheader(f"🎥 Film sélectionné : {selected_film}")
        st.metric("Nombre de commentaires", len(film_data))
        # Statistiques
        counts = film_data['Sentiment'].value_counts()
        col1, col2, col3 = st.columns(3)
        col1.metric("Positifs", counts.get('Positive', 0))
        col2.metric("Négatifs", counts.get('Negative', 0))
        col3.metric("Neutres", counts.get('Neutral', 0))
        # Graphique
        st.write("### 📊 Répartition des sentiments")
        pie = px.pie(film_data, names='Sentiment', title="Sentiments des commentaires",
                     color='Sentiment',
                     color_discrete_map={"Positive": "green", "Negative": "red", "Neutral": "gray"})
        st.plotly_chart(pie, use_container_width=True)
        # Top commentaires
        st.write("### 🥇 Commentaires les plus positifs")
        top_pos = film_data.sort_values(by='Polarity', ascending=False).head(3)
        for i, row in top_pos.iterrows():
            st.success(row['Commentaires'])
        st.write("### 😠 Commentaires les plus négatifs")
        top_neg = film_data.sort_values(by='Polarity').head(3)
        for i, row in top_neg.iterrows():
            st.error(row['Commentaires'])
        # Table
        with st.expander("📄 Voir tous les commentaires du film"):
            st.dataframe(film_data[['Commentaires', 'Sentiment', 'Polarity']], use_container_width=True)
       
if __name__ == "__main__":
    main()
