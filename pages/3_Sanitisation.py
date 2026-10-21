import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Sanitisation", layout="wide")
st.title("✨ Sanitisation et Formatage")

file_upload = st.file_uploader("Importer le fichier à nettoyer", type=['csv', 'xlsx'])

def formater_telephone(val):
    if pd.isna(val): return val
    chiffres = re.sub(r'\D', '', str(val))
    if len(chiffres) == 10:
        return f"({chiffres[:3]}) {chiffres[3:6]}-{chiffres[6:]}"
    return val # Retourne intact si ce n'est pas 10 chiffres

if file_upload:
    df = pd.read_csv(file_upload) if file_upload.name.endswith('csv') else pd.read_excel(file_upload)
    
    colonne = st.selectbox("Sélectionner la colonne à nettoyer :", df.columns)
    action = st.radio("Action à appliquer :", ["Tout en minuscules", "Tout en MAJUSCULES", "Format Téléphone (123) 456-7890"])
    
    if st.button("Appliquer le formatage"):
        df_clean = df.copy()
        if action == "Tout en minuscules":
            df_clean[colonne] = df_clean[colonne].astype(str).str.lower()
        elif action == "Tout en MAJUSCULES":
            df_clean[colonne] = df_clean[colonne].astype(str).str.upper()
        elif action == "Format Téléphone (123) 456-7890":
            df_clean[colonne] = df_clean[colonne].apply(formater_telephone)
            
        st.dataframe(df_clean.head(50), use_container_width=True)
        st.download_button("Télécharger le fichier nettoyé", data=df_clean.to_csv(index=False), file_name="fichier_sanitise.csv")