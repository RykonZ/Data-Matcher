import streamlit as st
import pandas as pd
import re
import difflib

# Configuration de la page avec Material Icon
st.set_page_config(page_title="Data Matcher", page_icon=":material/join_inner:", layout="wide")

# Injection CSS pour forcer la police "Outfit"
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="st-"], .stMarkdown, .stText, h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
    }
    div[data-testid="metric-container"] {
        font-family: 'Outfit', sans-serif !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title(":material/join_inner: Data Matcher & Fusion")
st.markdown("Croisez deux listes, analysez la fidélité des correspondances et rapatriez les colonnes désirées dans un rapport unique.")

# --- ZONE D'UPLOAD ---
col1, col2 = st.columns(2)
with col1:
    st.header(":material/upload_file: Fichier A (Source)")
    file_a = st.file_uploader("Importer Fichier A", type=['csv', 'xlsx'], key="file_a")
with col2:
    st.header(":material/upload_file: Fichier B (Référence)")
    file_b = st.file_uploader("Importer Fichier B", type=['csv', 'xlsx'], key="file_b")

if file_a and file_b:
    # Chargement des fichiers
    df_a = pd.read_csv(file_a) if file_a.name.endswith('csv') else pd.read_excel(file_a)
    df_b = pd.read_csv(file_b) if file_b.name.endswith('csv') else pd.read_excel(file_b)
    
    st.markdown("---")
    st.subheader(":material/key: Clés de liaison et Colonnes d'affichage")
    
    # Sélection des clés de match
    col_a_sel, col_b_sel = st.columns(2)
    col_a = col_a_sel.selectbox("🔑 Colonne Clé (Fichier A) - Ce qu'on cherche", df_a.columns)
    col_b = col_b_sel.selectbox("🔑 Colonne Clé (Fichier B) - Où on le cherche", df_b.columns)
    
    # Sélection des colonnes à afficher dans le rapport final
    out_a_sel, out_b_sel = st.columns(2)
    cols_out_a = out_a_sel.multiselect("👁️ Colonnes à extraire du Fichier A", df_a.columns, default=[col_a])
    cols_out_b = out_b_sel.multiselect("👁️ Colonnes à extraire du Fichier B", df_b.columns, default=[col_b])
    
    st.markdown("---")
    
    # --- OPTIONS DE MATCHING ---
    st.subheader(":material/settings: Options de traitement")
    
    opt_col1, opt_col2, opt_col3 = st.columns(3)
    
    with opt_col1:
        unique_only = st.checkbox("Résultats uniques (Fichier A)", value=True, help="Dédoublonne le fichier source avant l'analyse pour un rapport plus léger.")
        auto_trim = st.checkbox("Auto-Trim", value=True, help="Ignore les espaces invisibles avant et après le texte.")
        
    with opt_col2:
        strip_symbols = st.checkbox("Strip Symbols", value=False, help="Ignore la ponctuation et les caractères spéciaux pour la comparaison.")
        use_fuzzy = st.checkbox("Activer Fuzzy Match", value=False, help="Tolère les fautes de frappe (Plus lent).")
        
    with opt_col3:
        if use_fuzzy:
            fuzzy_threshold = st.slider("Tolérance Fuzzy (%)", min_value=50, max_value=99, value=80)
        else:
            fuzzy_threshold = 80

    # --- LOGIQUE D'ANALYSE ET DE FUSION ---
    if st.button(":material/play_arrow: Lancer l'analyse et la fusion", type="primary"):
        
        # 1. Préparation du Fichier B (Création de dictionnaires de recherche pour la vitesse)
        df_b_valid = df_b.dropna(subset=[col_b]).copy()
        df_b_valid['__str_b'] = df_b_valid[col_b].astype(str)
        
        lookup_exact = {}
        lookup_trim = {}
        lookup_strip = {}
        
        # On mappe la valeur cherchée vers les Index des lignes dans df_b
        for idx, val in df_b_valid['__str_b'].items():
            lookup_exact.setdefault(val, []).append(idx)
            if auto_trim:
                lookup_trim.setdefault(val.strip(), []).append(idx)
            if strip_symbols:
                lookup_strip.setdefault(re.sub(r'[^\w\s]', '', val), []).append(idx)
                
        unique_b_strs = list(lookup_exact.keys())
        
        # 2. Préparation du Fichier A
        df_a_to_process = df_a.dropna(subset=[col_a]).copy()
        if unique_only:
            df_a_to_process = df_a_to_process.drop_duplicates(subset=[col_a])
            
        resultats = []
        progress_bar = st.progress(0)
        total_a = len(df_a_to_process)
        
        # 3. Moteur de correspondance itératif
        for idx_enum, (idx_a, row_a) in enumerate(df_a_to_process.iterrows()):
            v_a = str(row_a[col_a])
            match_status = "Aucune"
            matched_indices_b = []
            
            # Cascade de vérification
            if v_a in lookup_exact:
                match_status = "Exacte"
                matched_indices_b = lookup_exact[v_a]
            elif auto_trim and v_a.strip() in lookup_trim:
                match_status = "Exacte (Trim)"
                matched_indices_b = lookup_trim[v_a.strip()]
            elif strip_symbols and re.sub(r'[^\w\s]', '', v_a) in lookup_strip:
                match_status = "Exacte (Sans symboles)"
                matched_indices_b = lookup_strip[re.sub(r'[^\w\s]', '', v_a)]
            elif use_fuzzy:
                matches = difflib.get_close_matches(v_a, unique_b_strs, n=1, cutoff=fuzzy_threshold/100.0)
                if matches:
                    best_match = matches[0]
                    score = int(difflib.SequenceMatcher(None, v_a, best_match).ratio() * 100)
                    match_status = f"Fuzzy ({score}%)"
                    matched_indices_b = lookup_exact[best_match]

            # Construction de la ligne de résultat
            base_row = {f"[A] {col}": row_a[col] for col in cols_out_a}
            base_row['Fidélité_Match'] = match_status
            
            # Fusion avec les données du Fichier B
            if matched_indices_b:
                # S'il y a plusieurs correspondances dans B, on crée plusieurs lignes (Left Join behavior)
                for idx_b in matched_indices_b:
                    row_b = df_b_valid.loc[idx_b]
                    combined = base_row.copy()
                    for col in cols_out_b:
                        combined[f"[B] {col}"] = row_b[col]
                    resultats.append(combined)
            else:
                combined = base_row.copy()
                for col in cols_out_b:
                    combined[f"[B] {col}"] = None  # Laisse vide si aucun match
                resultats.append(combined)
            
            # Mise à jour fluide de la barre de progression
            if idx_enum % max(1, (total_a // 20)) == 0:
                progress_bar.progress(idx_enum / total_a)
                
        progress_bar.progress(1.0)
        
        # 4. Affichage et Export
        df_resultat = pd.DataFrame(resultats)
        matches_count = len(df_resultat[df_resultat['Fidélité_Match'] != "Aucune"])
        
        st.success(f":material/check_circle: Fusion terminée : **{matches_count}** correspondances trouvées.")
        
        st.dataframe(df_resultat, use_container_width=True)
        
        st.download_button(
            label=":material/download: Télécharger le rapport fusionné",
            data=df_resultat.to_csv(index=False),
            file_name="fusion_data_matcher.csv",
            mime="text/csv",
            type="primary"
        )