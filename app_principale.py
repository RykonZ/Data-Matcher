import streamlit as st

st.set_page_config(page_title="Boîte à Outils Data", page_icon=":material/build:", layout="centered")

st.title(":material/build: Boîte à Outils Data & Salesforce")
st.markdown("""
Bienvenue dans l'outil interne de gestion des données. 
Sélectionnez une application dans le menu latéral à gauche pour commencer.

**Outils disponibles :**
*   🧹 **Nettoyage Salesforce :** Audit, protection des données et préparation à la suppression.
*   🔗 **Data Matcher :** Croisement de listes et recherche de valeurs uniques entre deux fichiers.
*   ✨ **Sanitisation :** Nettoyage de chaînes de caractères et formatage (ex: Numéros de téléphone).
""")