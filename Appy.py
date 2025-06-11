import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import io
from fpdf import FPDF
from modele import prévoir_stock

# CONFIGURATION DE LA PAGE
st.set_page_config(
    page_title="Assistant IA pour la Gestion Intelligente des Stocks",
    layout="centered",
    page_icon="📦💡"
)

# LOGO
logo = Image.open("logo.png")
st.image(logo, width=150)

# TITRE
st.title("💡SmartStocker")

# INTRODUCTION
st.markdown("""
🧠 Bienvenue sur SmartStocker – Votre Solution Intelligente de Gestion de Stock

Optimisez vos stocks. Gagnez du temps. Anticipez la demande.

Notre interface combine la puissance de l’intelligence artificielle avec une analyse fine de vos données produits pour vous offrir une gestion de stock simple, rapide et intelligente.
Grâce à des algorithmes de prévision avancés, vous pouvez :

✅ Prévoir les ventes avec précision
✅ Réduire les ruptures et le surstock
✅ Segmentez intelligemment vos produits
✅ Calculer le stock optimal selon la demande réelle
✅ Télécharger vos rapports en un clic (Excel ou PDF)

🤖 Une IA à votre service

Notre système apprend de vos données pour vous proposer des décisions automatisées ou assistées, adaptées à votre activité.
Il ne s’agit pas seulement de suivre vos stocks, mais de les anticiper intelligemment.


🌍 Une solution pensée pour vous

Que vous soyez un commerçant local, un e-commerçant, ou une entreprise en pleine croissance, SmartStocker s’adapte à vos besoins.
Développée avec une vision locale, notre plateforme est légère, intuitive et compatible avec vos outils existants.


🚀 Lancez-vous dès aujourd’hui

Gérez vos stocks comme les grandes entreprises, grâce à une IA simple, accessible et efficace.
Faites confiance à la technologie pour vous aider à mieux gérer, mieux vendre, mieux décider.

_Crée par **Daniella** — Étudiante IA passionnée_
""")

st.divider()

# SAISIE DES DONNÉES
option = st.radio("Méthode de saisie :", ["📝 Entrer les ventes manuellement", "📁 Importer un fichier CSV"])

df_input = None

if option == "📝 Entrer les ventes manuellement":
    ventes_text = st.text_area("Entre les ventes mensuelles séparées par des virgules :", "12, 15, 9, 18, 0, 11")
    try:
        ventes = [int(x.strip()) for x in ventes_text.split(",")]
        dates = pd.date_range(end=pd.Timestamp.today(), periods=len(ventes), freq='MS')
        df_input = pd.DataFrame({'date': dates, 'sales': ventes})
    except:
        st.error("❌ Format invalide. Vérifie les chiffres et les virgules.")
        df_input = None

else:
    file = st.file_uploader("📁 Importe un fichier CSV avec colonnes : date, sales", type=['csv'])
    if file:
        try:
            df_input = pd.read_csv(file)
            df_input['date'] = pd.to_datetime(df_input['date'])
        except:
            st.error("❌ Erreur dans le fichier. Vérifie le format.")
            df_input = None

# ANALYSE
if df_input is not None and st.button("🔍 Lancer l’analyse"):
    result = prévoir_stock(df_input)
    st.success("✅ Analyse terminée avec succès")

    # Résultats
    st.subheader("📊 Résultats")
    st.write(f"**Prévisions (3 prochains mois)** : `{result['forecast']}`")
    st.write(f"**Stock de sécurité recommandé** : `{result['stock_securite']} unités`")
    st.write(f"**Stock total optimal** : `{result['stock_optimal']} unités`")
    st.write(f"**Profil du produit (cluster K-Means)** : `Cluster {result['profil_cluster']}`")

    # Graphique
    st.subheader("📈 Évolution des ventes + prévisions")
    fig, ax = plt.subplots()
    df_input.set_index('date')['sales'].plot(ax=ax, label="Historique", marker='o')
    future_dates = pd.date_range(start=df_input['date'].max() + pd.DateOffset(months=1), periods=3, freq='MS')
    pd.Series(result['forecast'], index=future_dates).plot(ax=ax, label="Prévision", linestyle='--', marker='o', color='red')
    ax.set_ylabel("Ventes")
    ax.set_xlabel("Date")
    ax.legend()
    st.pyplot(fig)

    # EXCEL
    st.subheader("📥 Télécharger les résultats (Excel)")
    df_result = pd.DataFrame({
        "Prévision mois 1": [result['forecast'][0]],
        "Prévision mois 2": [result['forecast'][1]],
        "Prévision mois 3": [result['forecast'][2]],
        "Stock sécurité": [result['stock_securite']],
        "Stock optimal": [result['stock_optimal']],
        "Profil produit (cluster)": [result['profil_cluster']]
    })

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_result.to_excel(writer, index=False, sheet_name="Résultats")
        writer.save()

    st.download_button(
        label="📥 Télécharger (Excel)",
        data=buffer,
        file_name="resultats_stock.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # PDF
    st.subheader("📝 Télécharger les résultats (PDF)")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Résultats - Prévision de Stock", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Prévision mois 1 : {result['forecast'][0]}", ln=True)
    pdf.cell(200, 10, txt=f"Prévision mois 2 : {result['forecast'][1]}", ln=True)
    pdf.cell(200, 10, txt=f"Prévision mois 3 : {result['forecast'][2]}", ln=True)
    pdf.cell(200, 10, txt=f"Stock de sécurité : {result['stock_securite']} unités", ln=True)
    pdf.cell(200, 10, txt=f"Stock optimal : {result['stock_optimal']} unités", ln=True)
    pdf.cell(200, 10, txt=f"Profil produit (Cluster) : {result['profil_cluster']}", ln=True)

    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)

    st.download_button(
        label="📝 Télécharger (PDF)",
        data=pdf_output,
        file_name="resultats_stock.pdf",
        mime="application/pdf"
    )

# FOOTER
st.divider()
st.markdown("💡 *Propulsé par Streamlit · Modèle ARIMA + K-Means · Projet IA de Daniella*")
