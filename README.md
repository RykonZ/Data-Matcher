# ⚡ Data Matcher V4.3

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

**Data Matcher** is a high-performance desktop utility designed to audit and match massive CSV datasets. Built for speed and accuracy, it handles complex data cleaning and cross-referencing in seconds—even with millions of rows.

## 🚀 Performance Benchmarks
Unlike Excel or standard VLOOKUPs, Data Matcher utilizes a **vectorized matching engine**.
* **Small Sets (1k - 50k rows):** Near-instant execution.
* **Large Sets (1M+ rows):** Processed in seconds using O(1) set-lookup logic.
* **Memory Efficient:** Optimized to handle large files without crashing your system.

## ✨ Key Features
* **Multi-Tier Matching:** * **Exact Match:** 1:1 identical strings.
    * **Trim/Case Neutral:** Ignores accidental spaces and capitalization.
    * **Symbol Stripping:** Matches IDs even if one has dashes, dots, or slashes (e.g., `123-ABC` matches `123ABC`).
* **Batch Processing:** Load multiple source files (File A) to check against one master reference (File B).
* **Audit Trail:** Every export includes a `Match_Fidelity` column and a timestamp for data integrity.
* **Clean UI:** Modern Dark Mode interface built with CustomTkinter.

## 💪 Reliability & Stability
* **Zero Crashes:** During extensive stress testing with datasets exceeding 1,000,000 rows, the engine remained stable with 0% crash rates.
* **Pro Tip:** For the highest match accuracy, it is recommended to enable both **"Auto-Trim"** and **"Strip Symbols"**. This ensures that hidden characters, spaces, and formatting differences (like dashes in serial numbers) don't prevent a successful match.

## ⚠️ Disclaimer
This software is provided "as is", without warranty of any kind, express or implied. In no event shall the author (RykonZ) be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software. 

*Always back up your data before performing large-scale audits.*

## 🛠️ Installation & Usage

### Option 1: Standalone (.exe)
1. Go to the [Releases](https://github.com/RykonZ/Data-Matcher/releases) page.
2. Download `DataMatcher.zip`.
3. Extract and run `DataMatcher.exe`.
   * *Note: As the software is self-signed by me (RykonZ), Windows may show a "SmartScreen" warning. Click 'More Info' -> 'Run Anyway'.*

### Option 2: Run from Source
If you have Python installed:
```bash
pip install pandas customtkinter
python DataMatcher.py
