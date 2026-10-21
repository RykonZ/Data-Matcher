# 📖 Technical Documentation: Data Matcher V4.3

## 1. Architecture Overview
Data Matcher is built on a **Modular Event-Driven Architecture** using `customtkinter` for the GUI and `pandas` for the data processing engine. The application is designed to handle high-volume CSV auditing while maintaining a responsive user interface.

## 2. The Matching Engine (Core Logic)
The "Crazy Fast" performance (1M+ rows in seconds) is achieved through **Vectorization** and **Hash-Set Lookups** rather than iterative loops.

### The Three-Tier Strategy:
1. **Tier 1: Exact Match**
   - Utilizes a direct `isin()` check against a raw Python `set()`. 
   - Complexity: **O(1)** average time complexity per lookup.
2. **Tier 2: Normalized Match (Trim/Case)**
   - Applies `.str.strip().str.lower()` vectorized operations across the entire column at once.
3. **Tier 3: Structural Match (Symbol Stripped)**
   - Uses Optimized Regex `[^a-zA-Z0-9]` to remove formatting. This ensures IDs like `ABC-123` and `ABC.123` are recognized as the same entity.

## 3. Memory Optimization Techniques
To prevent system crashes during 1M+ row audits, the following techniques are implemented:
* **Header-Only Peeking:** Using `pd.read_csv(nrows=0)` to populate UI dropdowns without loading the full file.
* **Column Pruning:** Only the necessary search and ID columns are loaded into RAM from the Reference File (File B).
* **Garbage Collection:** Explicitly deleting large temporary DataFrames (`del df_b`) after the lookup sets are generated.

## 4. Key Functions
### `resource_path(relative_path)`
Ensures that assets like `icon.ico` are correctly located whether the script is run as a `.py` file or bundled into a PyInstaller `.exe`.

### `clean(series, trim_only)`
The central normalization hub. It uses NumPy-backed Pandas operations to process string columns at scale.

### `process_logic()`
The main execution thread. It orchestrates the loading of the batch queue, performs the tiered matching, and generates the final `Match_Fidelity` audit trail.

## 5. Security & Integrity
* **Digital Signing:** The `.exe` is signed with a SHA-256 certificate to ensure file integrity.
* **Audit Logs:** Every result includes a `Source_File` and `Audit_Timestamp` column to provide a permanent record of when and where the match was found.

## 6. Developer Disclaimer
This documentation is for informational purposes. The logic is provided "as is" under the **GPL v3 License**. Modifications to the core engine should be tested against the 1M row benchmark to ensure no performance regressions are introduced.
