# Data Matcher & Salesforce Toolkit

[Français](#version-française) | [English](#english-version)

---

## Version Française

Application web interactive de traitement et de manipulation de données développée avec **Streamlit** et **Pandas**. Cet outil permet d'effectuer des audits d'espace de stockage Salesforce, de croiser et fusionner des jeux de données (exact & *fuzzy matching*) et d'appliquer des règles de nettoyage et de sanitisation sur des fichiers CSV ou Excel.

### Fonctionnalités

* **🧹 Nettoyage Salesforce** : 
  * Audit volumétrique des fichiers joints (`ContentDocument`, `ContentDocumentLink`, `sharinpix__MediaImport__c`).
  * Calcul de l'espace de stockage récupérable (en Go) et détection des fichiers orphelins.
  * Génération de rapports pré-formatés pour la préparation d'import SharinPix ou la suppression sécurisée dans Salesforce.
* **🔗 Data Matcher & Fusion** :
  * Croisement dynamique entre deux jeux de données (Fichier Source A vs Fichier Référence B).
  * Algorithme de correspondance exacte, de nettoyage automatique (*auto-trim*, retrait des symboles) ou approximatif (*fuzzy matching* par ratio de similarité textuelle).
  * Rapatriement ciblé de colonnes et exportation du rapport fusionné en CSV/Excel.
* **✨ Sanitisation** :
  * Nettoyage de colonnes par lot : passage en majuscules ou minuscules.
  * Normalisation automatique des numéros de téléphone au format `(123) 456-7890`.

### Architecture & Fonctionnement

L'application repose sur la structure de navigation multi-pages native de Streamlit :

1. **`app_principale.py`** : Point d'entrée de l'application. Gère la configuration globale, la feuille de style CSS (`Outfit` font) et le menu d'accueil.
2. **`pages/1_Nettoyage_Salesforce.py`** : Module d'analyse volumétrique, d'exclusion d'utilisateurs/fichiers protégés (SNOTES, PDF) et de préparation à la suppression.
3. **`pages/2_Data_Matcher.py`** : Moteur de croisement utilisant des dictionnaires de recherche optimisés et la bibliothèque `difflib` pour le calcul du score de similarité textuelle.
4. **`pages/3_Sanitisation.py`** : Outil de traitement en masse et de reformatage par expressions régulières (`re`).

### Prérequis

* **Python** : Version 3.9 ou supérieure.
* **Dépendances** : Streamlit, Pandas, OpenPyXL.

### Configuration & Installation (Setup)

1. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/votre-compte/Data-Matcher.git
   cd Data-Matcher
   ```

2. **Créer et activer un environnement virtuel** :
   ```bash
   python -m venv venv
   # Sous Windows (PowerShell) :
   .\venv\Scripts\Activate.ps1
   # Sous Windows (CMD) :
   venv\Scripts\activate.bat
   # Sous Linux / macOS :
   source venv/bin/activate
   ```

3. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

4. **Lancer l'application** :
   ```bash
   streamlit run app_principale.py
   ```

### Procédure de déploiement / Build

S'agissant d'une application Streamlit, le déploiement ne nécessite pas de compilation en binaire exécutable :

* **Déploiement local ou serveur** : Lancement via la commande `streamlit run app_principale.py`.
* **Déploiement Cloud (Streamlit Community Cloud / Heroku / Docker)** :
  * Assurez-vous que `requirements.txt` est à la racine.
  * Pointez le point d'entrée du déploiement sur `app_principale.py`.

### Transparence IA

Des outils d'intelligence artificielle générative ont été utilisés comme support pour l'accélération du développement, l'optimisation des structures de recherche Pandas et la rédaction de la documentation.

---

## English Version

An interactive data manipulation web application built with **Streamlit** and **Pandas**. This toolkit enables Salesforce storage cleanup audits, dataset matching/merging (exact and fuzzy matching), and data sanitization/formatting for CSV and Excel files.

### Features

* **🧹 Salesforce Cleanup**:
  * Storage consumption audit for file attachments (`ContentDocument`, `ContentDocumentLink`, `sharinpix__MediaImport__c`).
  * Reclaimable storage capacity calculation (in GB) and orphan file identification.
  * Pre-formatted export file generation for SharinPix preparation or safe deletion jobs.
* **🔗 Data Matcher & Merge**:
  * Cross-referencing between two files (Source File A vs Reference File B).
  * Exact matching, text cleaning (*auto-trim*, symbol removal), or approximate string matching (*fuzzy matching* based on similarity ratio).
  * Dynamic column joining and merged report export to CSV or Excel.
* **✨ Sanitization**:
  * Batch column formatting: text casing (UPPERCASE / lowercase).
  * Phone number normalization to standard `(123) 456-7890` format.

### Architecture & Mechanics

The application uses Streamlit's native multi-page routing system:

1. **`app_principale.py`**: Main application entry point. Handles global page settings, custom CSS styling (`Outfit` font), and landing menu navigation.
2. **`pages/1_Nettoyage_Salesforce.py`**: Storage audit module, user/protected file exclusion logic (SNOTES, PDFs), and deletion list builder.
3. **`pages/2_Data_Matcher.py`**: Record-matching engine using optimized lookup tables and `difflib` sequence matching for string similarity scoring.
4. **`pages/3_Sanitisation.py`**: Batch processing and regular expression (`re`) text formatting tool.

### Prerequisites

* **Python**: Version 3.9 or higher.
* **Dependencies**: Streamlit, Pandas, OpenPyXL.

### Setup & Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/Data-Matcher.git
   cd Data-Matcher
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   # Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # Windows (CMD):
   venv\Scripts\activate.bat
   # Linux / macOS:
   source venv/bin/activate
   ```

3. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   streamlit run app_principale.py
   ```

### Deployment & Build Process

As a web application built on Streamlit, binary compilation is not required:

* **Local / On-Premise Execution**: Launched directly via `streamlit run app_principale.py`.
* **Cloud Deployment (Streamlit Community Cloud / Docker)**:
  * Ensure `requirements.txt` is located in the repository root.
  * Set `app_principale.py` as the application entry point.

### AI Disclosure

Generative AI tools were used during development to assist with code optimization, Pandas data transformation pipelines, and documentation.
