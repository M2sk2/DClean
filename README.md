# DClean

> **Automated bilingual data cleaning, standardization, and deduplication for survey and registration spreadsheets.**

DClean is an intelligent, offline data cleaning application built for Arabic and English tabular datasets (`.xlsx`, `.csv`). It automatically heals messy input, standardizes Saudi phone numbers and educational profiles, isolates bad records into a quarantine sheet, and resolves duplicate person submissions.

---

## ✨ What DClean Does For You

- **🇸🇦 Saudi & Bilingual Normalization**:
  - **Phone Numbers**: Converts numbers to Saudi E.164 (`+9665XXXXXXXX`), automatically recovering dropped leading zeros caused by Excel auto-formatting.
  - **Names**: Normalizes Arabic compound names (`عبد الله` $\rightarrow$ `عبدالله`), patronymics, and inverted English names.
  - **Email Healing**: Auto-corrects common email typos (e.g., `@gmaill.com` $\rightarrow$ `@gmail.com`).
  - **Educational Directory**: Maps university, college, and major variants to canonical Saudi standards.
- **🛡️ Zero-Data-Loss Quarantine**: Records missing critical identification are never silently deleted. They are routed to a **Quarantine sheet** with clear rejection reason codes (`MISSING_REQUIRED_NAME`, `UNLINKABLE_IDENTIFIER`).
- **👥 Smart Deduplication (Entity Resolution)**: Links multiple submissions from the same respondent across sheets and forms, merging duplicate entries into a single clean profile.
- **🔒 100% Local & Private**: Runs completely on your machine—no external API calls, cloud uploads, or privacy risks.

---

## 🚀 Ways to Use DClean

### 1. Interactive Web Studio (Streamlit Dashboard)
The easiest way to clean, inspect, and export your data in a visual dashboard:

```powershell
py -m streamlit run dashboard.py
# or via installed CLI:
dclean dashboard
```

- **Drag & Drop**: Upload any `.xlsx` or `.csv` spreadsheet with an instant raw data preview.
- **Strategy Toggle**: Choose between **Auto-Detect** (instant local AI schema matching) or **Custom YAML Contracts**.
- **Live Audit Cards**: View row counts, quarantine percentage, and unique persons resolved in real time.
- **Tabbed Review**: Inspect your clean dataset side-by-side with quarantined rows.
- **Dual Export**: Download clean data as a formatted **Excel workbook (`.xlsx`)** or an auditable **SQLite database (`.db`)**.

---

### 2. Windows Explorer Right-Click Context Menu
Clean files directly from your desktop or folder:
1. Right-click any `.xlsx`, `.csv`, or `.xlsm` file.
2. Click **"Clean with DClean"**.
3. A progress dialog will process the file and save the output as `[Filename]_Cleaned.xlsx`.

---

### 3. Command-Line Interface (CLI)
For fast batch processing from the terminal:

```powershell
# Clean a dataset using automatic column detection
dclean clean -i "RawData/Workshop_Responses.xlsx"

# Clean using an explicit YAML contract
dclean clean -i "RawData/Workshop_Responses.xlsx" -c "config/workshop_contract.yaml"

# Launch the visual web dashboard
dclean dashboard
```

*(If running directly from source without installing: use `py -m pipeline.cli -i "..."`)*

---

## 📦 Installation

### Option A: Windows One-Click Installer (Zero Admin Rights Needed)
Double-click [`installer/install.bat`](installer/install.bat) or run in PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File installer/install.ps1
```

- Installs to `%LocalAppData%\Programs\DClean`.
- Adds **Desktop** and **Start Menu** shortcuts.
- Adds the global `dclean` command to your terminal `PATH`.
- Adds the **"Clean with DClean"** right-click context menu.
- To uninstall cleanly anytime: run [`installer/uninstall.bat`](installer/uninstall.bat).

> [!NOTE]
> During installation, step `[4/6]` downloads and sets up the local Python dependencies. This takes 1–2 minutes on first run.

### Option B: Run from Source (Cross-Platform)
Works on Windows, macOS, and Linux with Python 3.10+:

```powershell
git clone https://github.com/M2sk2/DClean.git
cd DClean
pip install -r requirements.txt
```

---

## 📊 What You Get (Output Formats)

Every cleaning job generates two ready-to-use deliverables:

### 1. Formatted Excel Workbook (`..._Cleaned.xlsx`)
- **`cleaned_dataset`**: Clean, validated, human-readable records with standardized formatting ready for reporting.
- **`quarantine_records`**: Quarantined records with the original row numbers and exact rejection reasons for audit.
- **`audit_summary`**: High-level execution metrics (total ingested, clean rows, quarantine rate, unique persons).

### 2. Relational SQLite Database (`.db`)
- **`dim_persons`**: Unique individuals with canonical names, verified phones, and emails.
- **`fact_registration`**: Timestamped registration records linked to persons via foreign keys.
- **`quarantine_records`**: Complete dead-letter table for downstream governance.

---

## 📁 Project Overview

```text
DClean/
├── dashboard.py           # Interactive Web Studio
├── installer/             # One-click Windows installer & shortcuts
├── config/                # Declarative schema contracts (.yaml)
├── RawData/               # Place input spreadsheets here (.xlsx, .csv)
├── CleanData/             # Processed Excel workbooks and SQLite databases
└── requirements.txt       # Project dependencies
```
