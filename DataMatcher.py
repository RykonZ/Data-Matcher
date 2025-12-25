import pandas as pd
import customtkinter as ctk
from tkinter import filedialog, messagebox
import time
import re
from datetime import datetime
import os
import sys

def resource_path(relative_path):
    """ 
    Resolves the absolute path for resources. 
    Ensures compatibility with both standard Python execution and PyInstaller bundles.
    """
    try:
        # PyInstaller creates a temporary folder stored in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# UI Configuration
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class DataMatcherV4_3_Final(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Setup ---
        self.title("Data Matcher")
        self.geometry("1400x950")

        # --- Icon Handling ---
        icon_name = "icon.ico"
        try:
            icon_path = resource_path(icon_name)
            self.iconbitmap(icon_path)
        except Exception as e:
            # Fallback if icon is missing: log error and continue
            print(f"Icon load skipped: {e}")

        # --- Application State ---
        self.queue_a = []
        self.ref_path = ""
        self.final_df = pd.DataFrame()
        self.curr_a_path = ""
        self.curr_a_cols = []
        
        self.opt_trim = ctk.BooleanVar(value=True)
        self.opt_strip = ctk.BooleanVar(value=False)

        # --- UI Grid Layout Configuration ---
        self.grid_columnconfigure(0, weight=0) 
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar: Configuration Panel ---
        self.sidebar = ctk.CTkScrollableFrame(self, width=350, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Section 1: Source File Configuration (File A)
        self.frame_a_group = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.frame_a_group.pack(pady=(20, 10), padx=10, fill="x")

        ctk.CTkLabel(self.frame_a_group, text="1. SOURCE CONFIG", font=ctk.CTkFont(size=15, weight="bold")).pack(pady=5)
        self.btn_load_a = ctk.CTkButton(self.frame_a_group, text="📂 Load File A", height=32, command=self.peek_file_a)
        self.btn_load_a.pack(pady=5, padx=10, fill="x")
        self.lbl_a = ctk.CTkLabel(self.frame_a_group, text="No file selected", text_color="gray", font=ctk.CTkFont(size=11))
        self.lbl_a.pack()

        self.container_a = ctk.CTkFrame(self.frame_a_group, fg_color="transparent")
        self.drop_id_a = ctk.CTkOptionMenu(self.container_a, values=[], height=28, command=self.update_checks_a)
        self.scroll_a = ctk.CTkFrame(self.container_a)
        self.vars_a = {}
        self.btn_add_queue = ctk.CTkButton(self.container_a, text="➕ Add to Queue", fg_color="#2ecc71", hover_color="#27ae60", command=self.add_to_queue)

        # Visual Separator
        ctk.CTkFrame(self.sidebar, height=2, fg_color="#333").pack(fill="x", padx=30, pady=20)

        # Section 2: Reference File Configuration (File B)
        self.frame_b_group = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.frame_b_group.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(self.frame_b_group, text="2. REFERENCE CONFIG", font=ctk.CTkFont(size=15, weight="bold")).pack(pady=5)
        self.btn_load_b = ctk.CTkButton(self.frame_b_group, text="🎯 Load File B", fg_color="#9b59b6", height=32, command=self.peek_file_b)
        self.btn_load_b.pack(pady=5, padx=10, fill="x")
        self.lbl_b = ctk.CTkLabel(self.frame_b_group, text="No reference selected", text_color="gray", font=ctk.CTkFont(size=11))
        self.lbl_b.pack()

        self.container_b = ctk.CTkFrame(self.frame_b_group, fg_color="transparent")
        self.scroll_b = ctk.CTkFrame(self.container_b)
        self.vars_b = {}

        # --- Main Workspace ---
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=20, pady=10)

        # Cleaning Settings Header
        self.options_frame = ctk.CTkFrame(self.content)
        self.options_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(self.options_frame, text="CLEANING & AUDIT SETTINGS:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=15)
        ctk.CTkSwitch(self.options_frame, text="Auto-Trim", variable=self.opt_trim).pack(side="left", padx=10)
        ctk.CTkSwitch(self.options_frame, text="Strip Symbols", variable=self.opt_strip).pack(side="left", padx=10)

        # Batch Processing Queue Display
        self.queue_box = ctk.CTkScrollableFrame(self.content, height=180, label_text="BATCH QUEUE", label_font=ctk.CTkFont(weight="bold"))
        self.queue_box.pack(fill="x", pady=(0, 10))

        # Execution Toolbar
        self.tool_bar = ctk.CTkFrame(self.content)
        self.tool_bar.pack(fill="x", pady=5)
        
        ctk.CTkLabel(self.tool_bar, text="Result Mode:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(20, 5))
        self.mode_var = ctk.StringVar(value="Unique")
        ctk.CTkRadioButton(self.tool_bar, text="Unique", variable=self.mode_var, value="Unique", font=ctk.CTkFont(size=11)).pack(side="left", padx=10)
        ctk.CTkRadioButton(self.tool_bar, text="All", variable=self.mode_var, value="All", font=ctk.CTkFont(size=11)).pack(side="left", padx=10)

        self.btn_run = ctk.CTkButton(self.tool_bar, text="⚡ RUN & AUDIT", width=160, height=35, command=self.process_logic)
        self.btn_run.pack(side="left", padx=30, pady=10)

        self.btn_export = ctk.CTkButton(self.tool_bar, text="📥 DOWNLOAD AUDITED CSV", width=220, height=35, fg_color="#e67e22", command=self.download_csv)

        # Feedback & Progress Monitoring
        self.progress_bar = ctk.CTkProgressBar(self.content, height=15)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=(10, 2))
        self.stat_label = ctk.CTkLabel(self.content, text="Ready", font=ctk.CTkFont(size=12, slant="italic"), text_color="gray")
        self.stat_label.pack(anchor="w", padx=10)

        # Data Preview Area
        self.preview = ctk.CTkTextbox(self.content, font=ctk.CTkFont(family="Courier New", size=12), wrap="none")
        self.preview.pack(fill="both", expand=True, pady=(5, 10))

        # Attribution Footer
        self.footer = ctk.CTkLabel(self, text="Built by RykonZ | version 4.3", font=ctk.CTkFont(size=9))
        self.footer.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-2)

    # --- Data Processing Core ---
    def clean(self, series, trim_only=False):
        """ 
        Performs high-speed string normalization using vectorized operations.
        Vectorized operations are significantly faster than standard loops in Python.
        """
        series = series.astype(str).fillna("")
        
        if self.opt_trim.get() or trim_only:
            series = series.str.strip().str.lower()
            
        if self.opt_strip.get() and not trim_only:
            # Regex substitution: Removes all non-alphanumeric characters
            series = series.str.replace(r'[^a-zA-Z0-9]', '', regex=True)
            
        return series

    def peek_file_a(self):
        """ Opens Source File A and retrieves headers without loading the full dataset into memory. """
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if path:
            self.curr_a_path = path
            # Optimization: Loading 'nrows=0' retrieves column names instantly for large files
            self.curr_a_cols = list(pd.read_csv(path, nrows=0).columns)
            self.lbl_a.configure(text=path.split('/')[-1], text_color="#3498db")
            self.container_a.pack(fill="x")
            self.drop_id_a.pack(pady=2)
            self.drop_id_a.configure(values=self.curr_a_cols)
            self.drop_id_a.set(self.curr_a_cols[0])
            self.scroll_a.pack(pady=5, fill="x")
            self.btn_add_queue.pack(pady=15, padx=30, fill="x")
            self.update_checks_a(self.drop_id_a.get())

    def update_checks_a(self, sel_id):
        """ Updates the column selection list, excluding the primary ID column. """
        for w in self.scroll_a.winfo_children(): w.destroy()
        self.vars_a = {}
        for c in self.curr_a_cols:
            if c != sel_id:
                v = ctk.BooleanVar(); cb = ctk.CTkCheckBox(self.scroll_a, text=c, font=ctk.CTkFont(size=11), variable=v)
                cb.pack(anchor="w", pady=1, padx=10); self.vars_a[c] = v

    def add_to_queue(self):
        """ Adds the current file configuration to the batch processing queue. """
        fname = self.curr_a_path.split('/')[-1]
        if any(item['path'] == self.curr_a_path for item in self.queue_a):
            messagebox.showerror("Duplicate", f"'{fname}' is already in queue.")
            return
        sel = [k for k, v in self.vars_a.items() if v.get()]
        if not sel: 
            messagebox.showwarning("Warning", "Please select at least one search column.")
            return
        self.queue_a.append({"path": self.curr_a_path, "name": fname, "id": self.drop_id_a.get(), "cols": sel})
        self.render_queue()
        self.reset_a_section()

    def reset_a_section(self):
        """ Clears the Source Config UI to prepare for the next file selection. """
        self.curr_a_path = ""
        self.lbl_a.configure(text="No file selected", text_color="gray")
        for w in self.container_a.winfo_children():
            if not isinstance(w, (ctk.CTkOptionMenu, ctk.CTkFrame, ctk.CTkButton)): w.destroy()
        self.container_a.pack_forget()

    def peek_file_b(self):
        """ Opens Reference File B and displays column selection for matching. """
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if path:
            self.ref_path = path
            # Memory Optimization: Load only headers to determine column structure
            cols_b = list(pd.read_csv(path, nrows=0).columns)
            self.lbl_b.configure(text=path.split('/')[-1], text_color="#9b59b6")
            self.container_b.pack(fill="x")
            self.scroll_b.pack(pady=5, fill="x")
            for w in self.scroll_b.winfo_children(): w.destroy()
            self.vars_b = {}
            for c in cols_b:
                v = ctk.BooleanVar(); cb = ctk.CTkCheckBox(self.scroll_b, text=c, font=ctk.CTkFont(size=11), variable=v)
                cb.pack(anchor="w", pady=1, padx=10); self.vars_b[c] = v

    def render_queue(self):
        """ Refreshes the Batch Queue UI display. """
        for w in self.queue_box.winfo_children(): w.destroy()
        for i, item in enumerate(self.queue_a):
            card = ctk.CTkFrame(self.queue_box)
            card.pack(fill="x", pady=2, padx=5)
            detail_text = f"📄 {item['name']}\nID: {item['id']} | SEARCH: {', '.join(item['cols'])}"
            ctk.CTkLabel(card, text=detail_text, font=ctk.CTkFont(size=11), justify="left").pack(side="left", padx=15, pady=5)
            ctk.CTkButton(card, text="✕", width=25, height=25, fg_color="#c0392b", command=lambda idx=i: self.remove_item(idx)).pack(side="right", padx=10)
        self.btn_export.pack_forget()

    def remove_item(self, idx):
        """ Removes an item from the batch queue. """
        self.queue_a.pop(idx)
        self.render_queue()

    # --- Match Engine (Main Logic) ---
    def process_logic(self):
        """
        Executes the matching algorithm across three tiers:
        1. Exact Match
        2. Case/Trim Neutral Match
        3. Symbol-Stripped Neutral Match
        """
        try:
            sel_b = [k for k, v in self.vars_b.items() if v.get()]
            if not self.queue_a or not self.ref_path or not sel_b:
                messagebox.showerror("Error", "Missing Queue or Reference File configuration.")
                self.btn_export.pack_forget()
                return

            start_t = time.time()
            self.progress_bar.set(0)
            self.stat_label.configure(text="Initializing Memory...", text_color="#3498db")
            self.update_idletasks() # Refresh UI to show status before processing
            
            # Optimization: Only load the necessary columns from Reference File B
            df_b = pd.read_csv(self.ref_path, usecols=sel_b)
            
            # Optimization: Flatten the DataFrame into a NumPy array for ultra-fast conversion to a Set
            # Set-based lookups are O(1) compared to O(n) list lookups.
            vals_b = df_b[sel_b].astype(str).to_numpy().flatten()
            
            # Generate Lookup Sets
            ref_raw = set(vals_b)
            s_vals_b = pd.Series(vals_b)
            ref_trim = set(self.clean(s_vals_b, trim_only=True).unique())
            ref_strip = set(self.clean(s_vals_b).unique())
            
            # Free memory from temporary reference objects
            del df_b, vals_b, s_vals_b

            results = []
            total = len(self.queue_a)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for i, item in enumerate(self.queue_a):
                self.stat_label.configure(text=f"Auditing {item['name']}...", text_color="#3498db")
                self.update_idletasks()

                df = pd.read_csv(item["path"])
                df['Match_Fidelity'] = "No Match"
                df['Source_File'] = item['name']
                df['Audit_Timestamp'] = timestamp

                for col in item["cols"]:
                    # Tier 1: Exact Case-Sensitive Match
                    exact_mask = df[col].astype(str).isin(ref_raw)
                    df.loc[exact_mask & (df['Match_Fidelity'] == "No Match"), 'Match_Fidelity'] = "Exact Match"
                    
                    # Tier 2: Match after removing white-space and matching case
                    if self.opt_trim.get():
                        trim_mask = self.clean(df[col], trim_only=True).isin(ref_trim)
                        df.loc[trim_mask & (df['Match_Fidelity'] == "No Match"), 'Match_Fidelity'] = "Fidelity: Trimmed/Case"

                    # Tier 3: Match after removing special characters (symbols/dots/dashes)
                    if self.opt_strip.get():
                        strip_mask = self.clean(df[col]).isin(ref_strip)
                        df.loc[strip_mask & (df['Match_Fidelity'] == "No Match"), 'Match_Fidelity'] = "Fidelity: Symbol Stripped"
                
                # Filter results based on User Choice (Unique IDs vs All Records)
                matched = df[df['Match_Fidelity'] != "No Match"]
                if self.mode_var.get() == "Unique":
                    matched = matched.drop_duplicates(subset=[item["id"]])
                
                results.append(matched)
                self.progress_bar.set((i+1)/total)

            # Consolidate all queue results into one DataFrame
            self.final_df = pd.concat(results, ignore_index=True)
            
            if not self.final_df.empty:
                self.preview.delete("0.0", "end")
                self.preview.insert("end", self.final_df.head(100).to_string(index=False))
                self.btn_export.pack(side="right", padx=20, pady=10)
                elapsed = time.time() - start_t
                self.stat_label.configure(text=f"Success! {len(self.final_df)} matches verified in {elapsed:.1f}s.", text_color="#2ecc71")
            else:
                self.stat_label.configure(text="No matches found.", text_color="#e74c3c")
                self.btn_export.pack_forget()
            
        except Exception as e: 
            messagebox.showerror("Error", str(e))
            self.btn_export.pack_forget()

    def download_csv(self):
        """ Exports the resulting audit trail to a CSV file. """
        p = filedialog.asksaveasfilename(defaultextension=".csv")
        if p: 
            self.final_df.to_csv(p, index=False)
            messagebox.showinfo("Saved", "Export Complete.")

if __name__ == "__main__":
    app = DataMatcherV4_3_Final()
    app.mainloop()