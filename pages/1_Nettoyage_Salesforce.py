import streamlit as st
import pandas as pd

# Configuration de la page avec Material Icon
st.set_page_config(page_title="Nettoyage Salesforce", page_icon=":material/cleaning_services:", layout="wide")

# Injection CSS pour forcer la police "Outfit" de Google Fonts
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="st-"], .stMarkdown, .stText, h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
    }
    
    /* Ajustement de la taille des métriques pour plus d'élégance */
    div[data-testid="metric-container"] {
        font-family: 'Outfit', sans-serif !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title(":material/cleaning_services: Tableau de Bord : Audit Nettoyage Salesforce")

def calculer_taille_gb(df, col_taille, col_id=None):
    if df.empty or col_taille not in df.columns: return 0.0
    temp_df = df.drop_duplicates(subset=[col_id]) if col_id and col_id in df.columns else df
    return pd.to_numeric(temp_df[col_taille], errors='coerce').fillna(0).sum() / (1024 ** 3)

# --- ZONE DE TÉLÉVERSEMENT (UPLOAD) ---
st.sidebar.header(":material/upload_file: Fichiers requis")
file_doc = st.sidebar.file_uploader("ContentDocument (csv format)", type=['csv'])
file_relier = st.sidebar.file_uploader("ContentDocumentLink (csv format)", type=['csv'])
file_imported = st.sidebar.file_uploader("sharinpix__MediaImport__c (csv format)", type=['csv'])

if file_doc and file_relier and file_imported:
    try:
        # Chargement des données
        df_doc = pd.read_csv(file_doc)
        df_relier = pd.read_csv(file_relier)
        df_imported = pd.read_csv(file_imported)
        
        # --- CONTRÔLES LATÉRAUX ---
        st.sidebar.markdown("---")
        st.sidebar.header(":material/tune: Contrôles de l'Audit")
        st.sidebar.info(":material/info: Les SNOTES sont exclus d'office de la suppression.")
        
        if 'FileType' in df_doc.columns:
            types_disponibles = df_doc[df_doc['FileType'] != 'SNOTE']['FileType'].dropna().unique().tolist()
            types_selectionnes = st.sidebar.multiselect(
                "Types à analyser :",
                options=types_disponibles,
                default=[t for t in types_disponibles if t in ['PNG', 'JPEG', 'JPG', 'PDF']]
            )
        else:
            st.sidebar.error("Colonne 'FileType' manquante.")
            types_selectionnes = []
        
        st.sidebar.markdown("---")
        exclure_pdf_import = st.sidebar.checkbox("Bloquer l'import des PDF dans SharinPix", value=True)

        # --- LOGIQUE DE NETTOYAGE ---
        df_doc_clean = df_doc[(df_doc['FileType'] != 'SNOTE') & (df_doc['FileType'].isin(types_selectionnes))]
        
        # 1. Orphelins 
        if 'LinkedEntityId' in df_relier.columns:
            liens_non_orphelins = df_relier[~df_relier['LinkedEntityId'].astype(str).str.startswith(('005', '058'))]['ContentDocumentId'].unique()
            df_orphelins = df_doc_clean[~df_doc_clean['Id'].isin(liens_non_orphelins)]
        else:
            st.error(":material/warning: La colonne 'LinkedEntityId' manque dans le fichier ContentDocumentLink.")
            df_orphelins = pd.DataFrame()

        # 2. SharinPix & Préparation de l'import
        # On suppose que la colonne de liaison dans imported s'appelle sharinpix__ContentDocumentId__c
        col_import = 'sharinpix__ContentDocumentId__c' if 'sharinpix__ContentDocumentId__c' in df_imported.columns else df_imported.columns[1]
        
        df_deja_importes = df_doc_clean[df_doc_clean['Id'].isin(df_imported[col_import])]
        df_a_importer = df_doc_clean[~df_doc_clean['Id'].isin(df_imported[col_import])]
        
        if exclure_pdf_import and not df_a_importer.empty:
            df_a_importer = df_a_importer[df_a_importer['FileType'] != 'PDF']
            
        # Fusion pour récupérer le LinkedEntityId
        if 'LinkedEntityId' in df_relier.columns and not df_a_importer.empty:
            df_a_importer = pd.merge(
                df_a_importer, 
                df_relier[['ContentDocumentId', 'LinkedEntityId']], 
                left_on='Id', 
                right_on='ContentDocumentId', 
                how='left'
            )
            df_a_importer.drop(columns=['ContentDocumentId'], inplace=True)
            
            # Exclusion des liens rattachés uniquement à des Utilisateurs (005)
            df_a_importer = df_a_importer[~df_a_importer['LinkedEntityId'].astype(str).str.startswith('005')]
            df_a_importer.rename(columns={'LinkedEntityId': 'AlbumId (LinkedEntityId)'}, inplace=True)
        
        # 3. Total à supprimer 
        df_a_supprimer = pd.concat([df_deja_importes, df_doc_clean[~df_doc_clean['Id'].isin(df_imported[col_import])]]).drop_duplicates(subset=['Id'])
        if exclure_pdf_import:
            df_a_supprimer = df_a_supprimer[df_a_supprimer['FileType'] != 'PDF']

        # 4. Liste des Intouchables
        df_snotes = df_doc[df_doc['FileType'] == 'SNOTE']
        df_pdfs_exclus = df_doc[df_doc['FileType'] == 'PDF'] if exclure_pdf_import else pd.DataFrame()
        df_intouchables = pd.concat([df_snotes, df_pdfs_exclus]).drop_duplicates(subset=['Id'])

        # --- AFFICHAGE UI : MÉTRIQUES ---
        st.header(":material/analytics: Statistiques Globales")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Cibles (Filtrées)", f"{len(df_doc_clean)}", f"{calculer_taille_gb(df_doc_clean, 'ContentSize'):.2f} GB")
        col2.metric("Déjà Importés", f"{len(df_deja_importes)}", f"{calculer_taille_gb(df_deja_importes, 'ContentSize'):.2f} GB")
        col3.metric("À Importer (Lignes)", f"{len(df_a_importer)}", f"{calculer_taille_gb(df_a_importer, 'ContentSize', 'Id'):.2f} GB réels")
        col4.metric(":material/delete_forever: Total à Supprimer", f"{len(df_a_supprimer)}", f"{calculer_taille_gb(df_a_supprimer, 'ContentSize'):.2f} GB", delta_color="inverse")

        st.write("---")
        
        # --- AFFICHAGE UI : ONGLETS ET TABLES ---
        tab1, tab2, tab3, tab4 = st.tabs([
            ":material/upload_file: À Importer", 
            ":material/delete: Liste de Suppression", 
            ":material/link_off: Orphelins",
            ":material/shield: Intouchables (SNOTE/PDF)"
        ])

        with tab1:
            st.subheader("Lignes prêtes pour l'import SharinPix")
            st.dataframe(df_a_importer, use_container_width=True)
            if not df_a_importer.empty:
                st.download_button(":material/download: Télécharger (À importer)", df_a_importer.to_csv(index=False), "a_importer.csv", "text/csv")

        with tab2:
            st.subheader("Fichiers physiques à supprimer de Salesforce")
            st.dataframe(df_a_supprimer, use_container_width=True)
            if not df_a_supprimer.empty:
                st.download_button(":material/download: Télécharger (Suppression)", df_a_supprimer.to_csv(index=False), "a_supprimer.csv", "text/csv")

        with tab3:
            st.subheader("Fichiers sans lien d'affaire")
            if not df_orphelins.empty:
                st.dataframe(df_orphelins, use_container_width=True)
                st.download_button(":material/download: Télécharger (Orphelins)", df_orphelins.to_csv(index=False), "orphelins.csv", "text/csv")
            else:
                st.success(":material/check_circle: Aucun orphelin détecté.")

        with tab4:
            st.subheader("Fichiers protégés (Ignorés par le nettoyage)")
            st.dataframe(df_intouchables, use_container_width=True)
            if not df_intouchables.empty:
                st.download_button(":material/download: Télécharger (Intouchables)", df_intouchables.to_csv(index=False), "intouchables.csv", "text/csv")

    except Exception as e:
        st.error(f":material/error: Erreur d'exécution : {e}")
else:
    st.info(":material/upload: Veuillez glisser les 3 fichiers requis dans le menu latéral pour afficher le tableau de bord.")