"""
DClean Unified Launcher.

Acts as the single entrypoint for the desktop shortcut, Windows context menu,
and command-line usage. Automatically discovers dashboard modules if present,
or provides a lightweight, responsive desktop GUI and headless one-click cleaner.
"""

import os
import sys
import argparse
import subprocess
from typing import Optional

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def run_headless_clean(file_path: str, contract_path: Optional[str] = None) -> bool:
    """
    Executes cleaning on a single file headless (used for Windows right-click context menu).
    Opens the output directory upon completion and displays a status dialog.
    """
    from pipeline.runner import PipelineRunner

    if not os.path.exists(file_path):
        print(f"[Error] Target file does not exist: {file_path}")
        return False

    base_dir = os.path.dirname(os.path.abspath(file_path))
    file_stem = os.path.splitext(os.path.basename(file_path))[0]
    out_excel = os.path.join(base_dir, f"{file_stem}_Cleaned.xlsx")
    out_db = os.path.join(base_dir, f"{file_stem}_Cleaned.db")

    print(f"[DClean] Cleaning file: {file_path}")
    print(f"[DClean] Contract: {contract_path or 'Auto-Detect (Local NLP Classifier)'}")
    
    runner = PipelineRunner(contract_path=contract_path, db_path=out_db)
    summary = runner.run(input_file_path=file_path, output_excel_path=out_excel)

    msg = (
        f"DClean Processing Complete!\n\n"
        f"File: {os.path.basename(file_path)}\n"
        f"Total Ingested: {summary.total_rows} rows\n"
        f"Cleaned Valid: {summary.valid_rows} rows\n"
        f"Quarantined: {summary.quarantined_rows} ({summary.quarantine_rate_pct}%)\n"
        f"Unique Entities: {summary.unique_persons_resolved}\n"
        f"Merged Duplicates: {summary.duplicate_events_merged}\n"
        f"Health Status: {summary.status}\n\n"
        f"Cleaned Excel: {out_excel}"
    )

    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("DClean - Success", msg)
        # Open explorer to the folder
        os.startfile(base_dir)
    except Exception:
        print(msg)

    return True

def launch_dashboard() -> bool:
    """
    Checks if a team dashboard module exists (e.g. dashboard.py or dashboard/app.py).
    If found, launches it via Streamlit.
    """
    candidates = [
        os.path.join(PROJECT_ROOT, "dashboard.py"),
        os.path.join(PROJECT_ROOT, "dashboard", "app.py"),
        os.path.join(PROJECT_ROOT, "app.py")
    ]
    for c in candidates:
        if os.path.exists(c):
            print(f"[DClean] Found dashboard at {c}. Launching Streamlit...")
            try:
                subprocess.run([sys.executable, "-m", "streamlit", "run", c])
                return True
            except Exception as e:
                print(f"[DClean] Could not start streamlit: {e}")
                return False
    return False

def launch_desktop_gui(initial_file: Optional[str] = None):
    """
    Native lightweight GUI for drag-and-drop cleaning, contract selection, and audit review.
    Works with zero additional dependencies via built-in tkinter/ttk.
    """
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox

    root = tk.Tk()
    root.title("DClean - Data Cleaning & Entity Resolution")
    root.geometry("720x560")
    root.minsize(640, 480)

    # Set icon if available
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "dclean_icon.ico")
    if os.path.exists(icon_path):
        try:
            root.iconbitmap(icon_path)
        except Exception:
            pass

    # Styling
    style = ttk.Style(root)
    style.theme_use("clam")

    # Header frame
    header_frame = ttk.Frame(root, padding=15)
    header_frame.pack(fill="x")

    title_lbl = ttk.Label(
        header_frame,
        text="DClean Data Processing Studio",
        font=("Segoe UI", 16, "bold"),
        foreground="#0284c7"
    )
    title_lbl.pack(anchor="w")

    subtitle_lbl = ttk.Label(
        header_frame,
        text="Generalized ETL, Local NLP Column Classification & MDM Entity Deduplication",
        font=("Segoe UI", 9)
    )
    subtitle_lbl.pack(anchor="w", pady=(2, 0))

    ttk.Separator(root, orient="horizontal").pack(fill="x", padx=15, pady=5)

    # Main content frame
    content_frame = ttk.Frame(root, padding=15)
    content_frame.pack(fill="both", expand=True)

    # 1. File Selection
    file_var = tk.StringVar(value=initial_file or "")

    file_lbl_frame = ttk.LabelFrame(content_frame, text=" 1. Raw Input File (.xlsx, .csv) ", padding=10)
    file_lbl_frame.pack(fill="x", pady=5)

    file_entry = ttk.Entry(file_lbl_frame, textvariable=file_var, font=("Segoe UI", 10))
    file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

    def browse_file():
        fn = filedialog.askopenfilename(
            title="Select Raw Dataset",
            filetypes=[("Tabular Files", "*.xlsx *.xls *.csv *.xlsm"), ("All Files", "*.*")]
        )
        if fn:
            file_var.set(fn)

    browse_btn = ttk.Button(file_lbl_frame, text="Browse...", command=browse_file)
    browse_btn.pack(side="right")

    # 2. Contract Selection Mode
    contract_mode_var = tk.StringVar(value="auto")
    contract_path_var = tk.StringVar(value="")

    contract_frame = ttk.LabelFrame(content_frame, text=" 2. Schema Contract Strategy ", padding=10)
    contract_frame.pack(fill="x", pady=5)

    auto_radio = ttk.Radiobutton(
        contract_frame,
        text="Auto-Detect Schema with Local AI/NLP Classifier (Zero Hallucination, Fast)",
        variable=contract_mode_var,
        value="auto"
    )
    auto_radio.pack(anchor="w", pady=2)

    custom_radio = ttk.Radiobutton(
        contract_frame,
        text="Use Custom Declarative YAML Contract",
        variable=contract_mode_var,
        value="custom"
    )
    custom_radio.pack(anchor="w", pady=2)

    custom_file_subframe = ttk.Frame(contract_frame)
    custom_file_subframe.pack(fill="x", pady=4)

    contract_entry = ttk.Entry(custom_file_subframe, textvariable=contract_path_var, font=("Segoe UI", 9))
    contract_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

    def browse_contract():
        fn = filedialog.askopenfilename(
            title="Select YAML Contract",
            filetypes=[("YAML Files", "*.yaml *.yml"), ("All Files", "*.*")]
        )
        if fn:
            contract_path_var.set(fn)
            contract_mode_var.set("custom")

    contract_browse_btn = ttk.Button(custom_file_subframe, text="Browse Contract...", command=browse_contract)
    contract_browse_btn.pack(side="right")

    # 3. Log & Results area
    log_frame = ttk.LabelFrame(content_frame, text=" Execution & Audit Log ", padding=10)
    log_frame.pack(fill="both", expand=True, pady=5)

    log_text = tk.Text(log_frame, wrap="word", font=("Consolas", 9), height=8)
    log_text.pack(fill="both", expand=True)

    def log(msg: str):
        log_text.insert("end", msg + "\n")
        log_text.see("end")
        root.update_idletasks()

    # Action buttons frame
    btn_frame = ttk.Frame(root, padding=15)
    btn_frame.pack(fill="x", side="bottom")

    last_out_dir = {"path": ""}
    last_out_excel = {"path": ""}
    last_out_db = {"path": ""}

    def open_output_folder():
        if last_out_dir["path"] and os.path.exists(last_out_dir["path"]):
            os.startfile(last_out_dir["path"])
        else:
            messagebox.showinfo("DClean", "No output generated yet.")

    def open_excel():
        if last_out_excel["path"] and os.path.exists(last_out_excel["path"]):
            os.startfile(last_out_excel["path"])
        else:
            messagebox.showinfo("DClean", "Cleaned Excel file not found.")

    def run_clean_action():
        target_file = file_var.get().strip()
        if not target_file or not os.path.exists(target_file):
            messagebox.showerror("Error", "Please specify a valid input file.")
            return

        contract = None
        if contract_mode_var.get() == "custom":
            c_file = contract_path_var.get().strip()
            if not c_file or not os.path.exists(c_file):
                messagebox.showerror("Error", "Please specify a valid YAML contract file.")
                return
            contract = c_file

        log_text.delete("1.0", "end")
        log("=" * 65)
        log("Starting DClean Processing Pipeline...")
        log(f"Input:    {target_file}")
        log(f"Strategy: {'Auto-Detect (Local NLP Model)' if not contract else contract}")
        log("-" * 65)

        clean_btn.config(state="disabled")
        root.config(cursor="wait")

        try:
            from pipeline.runner import PipelineRunner

            base_dir = os.path.dirname(os.path.abspath(target_file))
            stem = os.path.splitext(os.path.basename(target_file))[0]
            out_excel = os.path.join(base_dir, f"{stem}_Cleaned.xlsx")
            out_db = os.path.join(base_dir, f"{stem}_Cleaned.db")

            runner = PipelineRunner(contract_path=contract, db_path=out_db)
            summary = runner.run(input_file_path=target_file, output_excel_path=out_excel)

            log("\n[SUCCESS] Pipeline Finished Successfully!")
            log(f"  Total Ingested:       {summary.total_rows} rows")
            log(f"  Valid Processed:      {summary.valid_rows} rows")
            log(f"  Quarantined:          {summary.quarantined_rows} ({summary.quarantine_rate_pct}%)")
            log(f"  Unique Entities:      {summary.unique_persons_resolved}")
            log(f"  Duplicates Merged:    {summary.duplicate_events_merged}")
            log(f"  Pipeline Health:      {summary.status}")
            log("-" * 65)
            log(f"Clean Excel: {out_excel}")
            log(f"Clean Database: {out_db}")

            last_out_dir["path"] = base_dir
            last_out_excel["path"] = out_excel
            last_out_db["path"] = out_db

            excel_btn.config(state="normal")
            folder_btn.config(state="normal")
            messagebox.showinfo("Complete", f"Successfully cleaned {summary.valid_rows} records!\nHealth: {summary.status}")

        except Exception as e:
            log(f"\n[ERROR] Pipeline failed: {e}")
            messagebox.showerror("Pipeline Failure", str(e))
        finally:
            clean_btn.config(state="normal")
            root.config(cursor="")

    clean_btn = ttk.Button(btn_frame, text="⚡ Clean Data Now", command=run_clean_action, style="Accent.TButton")
    clean_btn.pack(side="left", padx=5)

    excel_btn = ttk.Button(btn_frame, text="📊 Open Cleaned Excel", command=open_excel, state="disabled")
    excel_btn.pack(side="left", padx=5)

    folder_btn = ttk.Button(btn_frame, text="📁 Open Output Folder", command=open_output_folder, state="disabled")
    folder_btn.pack(side="left", padx=5)

    close_btn = ttk.Button(btn_frame, text="Close", command=root.destroy)
    close_btn.pack(side="right", padx=5)

    root.mainloop()

def main():
    parser = argparse.ArgumentParser(description="DClean Desktop Launcher & Headless Processor")
    parser.add_argument("file", nargs="?", default=None, help="Optional raw tabular file to clean immediately")
    parser.add_argument("--contract", "-c", default=None, help="Optional YAML contract path")
    parser.add_argument("--gui", action="store_true", help="Force open desktop GUI window")
    parser.add_argument("--dashboard", action="store_true", help="Launch Streamlit dashboard if available")

    args = parser.parse_args()

    # 1. If dashboard explicitly requested, try launching it
    if args.dashboard:
        if launch_dashboard():
            return

    # 2. If a file was passed as argument (e.g. from Windows Explorer context menu)
    if args.file and not args.gui:
        success = run_headless_clean(args.file, contract_path=args.contract)
        sys.exit(0 if success else 1)

    # 3. If dashboard exists and GUI not explicitly forced, launch dashboard
    if not args.gui:
        if launch_dashboard():
            return

    # 4. Fallback to native lightweight desktop GUI
    launch_desktop_gui(initial_file=args.file)

if __name__ == "__main__":
    main()
