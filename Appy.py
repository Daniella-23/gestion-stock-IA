import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from modele import prévoir_stock  # ← importe ta fonction depuis le fichier modele.py

st.set_page_config(page_title="Assistant IA - Gestion de Stock", layout="centered")
st.title("📦 IA pour la Gestion Intelligente des Stocks")

st.markdown("**Entrez les ventes mensuelles d’un produit ou importez un fichier pour obtenir :**")
st.markdown("- 🔮 Des prévisions de ventes")
st.markdown("- 📦 Un stock optimal recommandé")
st.markdown("- 🧠 Un profil produit (via K-Means)")

option = st.radio("Méthode de saisie :", ["📝 Manuelle", "📁 Fichier CSV"])

df_input = None

if option == "📝 Manuelle":
    ventes_text = st.text_area("Entrez les ventes mensuelles (séparées par virgules) :", "12, 15, 9, 18, 0, 11")
    try:
        ventes = [int(x.strip()) for x in ventes_text.split(",")]
        dates = pd.date_range(end=pd.Timestamp.today(), periods=len(ventes), freq='MS')
        df_input = pd.DataFrame({'date': dates, 'sales': ventes})
    except:
        st.error("Format invalide.")
else:
    file = st.file_uploader("Chargez un fichier CSV avec colonnes : date, sales", type=['csv'])
    if file:
        df_input = pd.read_csv(file)
        try:
            df_input['date'] = pd.to_datetime(df_input['date'])
        except:
            st.error("Erreur dans la colonne 'date'.")
            df_input = None

if df_input is not None and st.button("🔍 Analyser"):
    result = prévoir_stock(df_input)
    st.success("✅ Analyse terminée")

    st.subheader("📊 Résultats")
    st.write(f"**Prévision (3 mois) :** {result['forecast']}")
    st.write(f"**Stock de sécurité :** {result['stock_securite']} unités")
    st.write(f"**Stock optimal :** {result['stock_optimal']} unités")
    st.write(f"**Profil du produit (cluster) :** {result['profil_cluster']}")
    
    # Graphique
    st.subheader("📈 Graphique de prévision")
    fig, ax = plt.subplots()
    df_input.set_index('date')['sales'].plot(ax=ax, label="Historique", marker='o')
    future_dates = pd.date_range(start=df_input['date'].max() + pd.DateOffset(months=1), periods=3, freq='MS')
    pd.Series(result['forecast'], index=future_dates).plot(ax=ax, label="Prévision", linestyle='--', color='red', marker='o')
    ax.set_ylabel("Ventes")
    ax.set_xlabel("Date")
    ax.legend()
    st.pyplot(fig)
