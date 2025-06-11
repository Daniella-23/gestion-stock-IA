import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

def prévoir_stock(df):
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    serie = df.set_index('date')['sales']
    serie.index.freq = 'MS'

    # Moyenne / écart-type / nb mois
    moyenne = serie.mean()
    ecart_type = serie.std()
    nb_mois = serie.count()

    # ARIMA
    model = ARIMA(serie, order=(2, 1, 2))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=3)

    # Stock de sécurité
    Z = 1.65
    L = 1
    stock_securite = Z * ecart_type * np.sqrt(L)
    stock_total = moyenne + stock_securite

    # Clustering fictif (modèle simulé ici)
    kmeans = KMeans(n_clusters=4, random_state=42)
    fake_data = pd.DataFrame({
        'mean_sales': np.random.uniform(1, 30, 100),
        'std_sales': np.random.uniform(0, 20, 100),
        'nb_months_sold': np.random.randint(1, 12, 100)
    })
    scaler = StandardScaler()
    X_train = scaler.fit_transform(fake_data)
    kmeans.fit(X_train)

    # Profil du produit
    X_user = pd.DataFrame([[moyenne, ecart_type, nb_mois]], columns=['mean_sales', 'std_sales', 'nb_months_sold'])
    X_user_scaled = scaler.transform(X_user)
    profil = int(kmeans.predict(X_user_scaled)[0])

    return {
        'moyenne': round(moyenne, 2),
        'ecart_type': round(ecart_type, 2),
        'stock_securite': round(stock_securite),
        'stock_optimal': round(stock_total),
        'forecast': forecast.round(2).tolist(),
        'profil_cluster': profil,
        'nb_mois': nb_mois
    }
