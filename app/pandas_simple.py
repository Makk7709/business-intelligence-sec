import streamlit as st
import pandas as pd

# Configuration de la page
st.set_page_config(
    page_title="Test Pandas Simple",
    page_icon="📊"
)

# Titre de l'application
st.title("Test Pandas Simple")
st.write("Cette application teste uniquement Pandas pour identifier la source du problème.")

# Créer un DataFrame simple
data = {
    'Année': [2022, 2023, 2024],
    'Valeur': [100, 150, 200]
}

# Créer et afficher le DataFrame
df = pd.DataFrame(data)
st.dataframe(df)

# Afficher un message de succès
st.success("Le DataFrame a été créé et affiché avec succès !") 