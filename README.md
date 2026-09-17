# DClean: Generalized Data Cleaning & Entity Resolution Pipeline

A high-performance, generalized ETL system designed for bilingual (Arabic & English) tabular survey datasets (`.xlsx` and `.csv`). Built in strict accordance with the project guidelines in [`Guidelines/`](Guidelines/).

---

## Key Highlights

- **Interactive Streamlit Dashboard**: Full web studio ([`dashboard.py`](dashboard.py)) with raw data preview, contract strategy toggles, real-time audit metrics, quarantine inspection, and dual Excel/SQLite export.
- **Local NLP Column Classifier**: Replaced slow generative LLMs with a lightweight, local sequence classifier (<1ms CPU inference, **97.31% validation accuracy**, zero hallucination risk).
- **Deterministic Identity Normalization**: Heals Excel dropped-zero bugs on Saudi phones (`508889900` $\rightarrow$ `+966508889900`), fixes email domain typos (`@gmaill.com` $\rightarrow$ `@gmail.com`), and parses compound Arabic names (`عبد الله` $\rightarrow$ `عبدالله`).
- **Comprehensive Controlled Vocabularies**: 680+ canonical mappings for Saudi universities, colleges, majors, and native academic levels ([`pipeline/lookup_data.py`](pipeline/lookup_data.py)).
- **Quarantine Dead-Letter Store**: Isolates un-linkable or corrupt records with machine-readable rejection reason codes (`MISSING_REQUIRED_NAME`, `MISSING_IDENTIFIER_RECORD_CANNOT_BE_LINKED`, etc.).
- **MDM Entity Resolution**: Combines deterministic indexing and probabilistic Jaro-Winkler matching with reproducible UUIDv5 clustering and survivorship rules.
- **Windows Desktop & Shell Integration**: One-click installer with desktop shortcut, Windows Explorer right-click context menu (*"Clean with DClean"*), and global terminal CLI (`dclean`).

---

## Architecture

```text
                           RAW TABULAR DATASET (.xlsx / .csv)
                                         │
                 [Local NLP Classifier]  ▼
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │ 1. Schema Contractor & Classifier (models/tfidf_column_classifier.joblib)   │
  │    - 4-Group Taxonomy: Identity, Structured, Categorical, Free-Form         │
  │    - Automatic declarative YAML schema generation & fuzzy header matching   │
  └──────────────────────────────────────┬──────────────────────────────────────┘
                                         │
                 [Deterministic Engine]  ▼
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │ 2. Cleaning & Normalization Engine (pipeline/normalizers.py)                │
  │    - Arabic compound name parser & inverted English name normalizer         │
  │    - Saudi E.164 phone formatting & email typo auto-healing                 │
  │    - Saudi university, college, major, and academic level lookups           │
  │    - Multi-select token splitting & multilingual boolean parsing            │
  └──────────────────┬──────────────────────────────────────────────────────────┘
                     │ (Failed assertions)
                     ├──────────────────────────────► [Quarantine Dead-Letter Store]
                     │ (Passed records)
                 [MDM Layer]  ▼
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │ 3. Entity Resolution & Deduplication (pipeline/entity_resolver.py)          │
  │    - Deterministic phone/email indexing + probabilistic Jaro-Winkler linkage│
  │    - Deterministic UUIDv5 clustering & survivorship merging                 │
  └──────────────────────────────────────┬──────────────────────────────────────┘
                                         │
                                         ▼
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │ 4. Persistence Layer (pipeline/storage.py)                                  │
  │    - Formatted Excel (.xlsx): Cleaned dataset, Quarantine, Audit sheets     │
  │    - SQLite Database (.db): dim_persons, fact_registration (FK enforced)   │
  └─────────────────────────────────────────────────────────────────────────────┘
```

---

## Taxonomy Groups

| Group | Approach | Core Rules | Examples |
|---|---|---|---|
| **1. Identity** | Deterministic | Zero hallucination. Compound-aware Arabic/English NLP, E.164 phone formatting, and email syntax/typo healing. | `الاسم الكامل`, `Phone`, `Email` |
| **2. Structured / MetaData** | Controlled Lookups | Standardized against Saudi educational lookups. ISO-8601 UTC datetimes. Preserves unknown strings cleanly. | `الجامعة`, `التخصص`, `المستوى الدراسي` |
| **3. Categorical / MultiSelect** | Rule-Based | Multilingual boolean resolution (`نعم/لا`, `حضر/غائب`), clean token lists. | `الموافقة على الشروط`, `حالة الحضور` |
| **4. Free-Form** | Sanitization Only | Preserves respondent wording and nuance without destructive alteration. | `توقعاتك من الورشة`, `أكبر مصدر تشتت` |

---

## Prerequisites & Setup

### Option A: Standard Developer Setup (All Platforms)
For running directly from source on Windows, macOS, or Linux (Python 3.10+):
```powershell
# 1. Clone the repository
git clone https://github.com/M2sk2/DClean.git
cd DClean

# 2. Install dependencies
pip install -r requirements.txt
```

---

### Option B: Windows One-Click Installer (Zero Admin Rights Needed)
Double-click [`installer/install.bat`](installer/install.bat) or execute in PowerShell:
```powershell
powershell -ExecutionPolicy Bypass -File installer/install.ps1
```
- **Target Location**: `%LocalAppData%\Programs\DClean` (no administrator privileges required).
- **Desktop & Start Menu**: Creates desktop shortcut and start menu item with custom high-res icon.
- **System PATH**: Adds `dclean` to user `PATH` for seamless terminal access in new command prompts.
- **Windows Explorer Context Menu**: Right-click any `.xlsx`, `.csv`, or `.xlsm` file and select **"Clean with DClean"** to clean instantly.
- **Uninstall**: Run [`installer/uninstall.bat`](installer/uninstall.bat) anytime for clean removal.

> [!NOTE]
> During installation, stage `[4/6]` installs the local virtual environment and pre-compiled wheels (`pandas`, `scikit-learn`, `streamlit`). This step takes 1–2 minutes on first run.

---

## Quickstart & Usage

### 1. Launch the Interactive Web Studio (Streamlit Dashboard)
Run the browser-based studio for interactive file upload, live previews, and dual exports:
```powershell
py -m streamlit run dashboard.py
# or if installed via installer:
dclean dashboard
```
- **Live Preview**: Inspect uploaded raw tabular datasets before processing.
- **Contract Strategy**: Switch between **Auto-Detect** (Local NLP Classifier) and **Declarative YAML Contracts** from `config/`.
- **Audit & Governance**: View live KPIs (valid rows, quarantine rate, unique persons resolved, duplicate events merged).
- **Tabbed Results Review**: Inspect the Cleaned dataset side-by-side with Quarantined records and machine-readable rejection codes.
- **Dual Export**: One-click download for formatted Excel (`.xlsx`) and SQLite relational database (`.db`).

---

### 2. Command-Line Interface (CLI)

Clean datasets directly from your terminal:
```powershell
# Clean with auto-detected schema (Local NLP sequence classifier)
dclean clean -i "RawData/Distraction_Era_Workshop_Dataset.xlsx"
# or directly with Python:
py -m pipeline.cli -i "RawData/Distraction_Era_Workshop_Dataset.xlsx"

# Clean with an explicit declarative YAML contract
dclean clean -i "RawData/Developers_Committee_2026_Responses.xlsx" -c "config/developers_committee_contract.yaml"

# Launch desktop GUI or web studio
dclean gui
dclean dashboard
```

---

### 3. Contract Schema Tools

```powershell
# Validate an existing YAML contract against project rules
dclean validate -c "config/workshop_contract.yaml"

# Diff a spreadsheet's headers against a contract schema
dclean diff -i "RawData/Distraction_Era_Workshop_Dataset.xlsx" -c "config/workshop_contract.yaml"

# Auto-generate a new contract YAML from raw data
dclean generate -i "RawData/Distraction_Era_Workshop_Dataset.xlsx" -o "config/new_contract.yaml"
```

---

### 4. Train / Retrain the Column Classifier
Harvests real column headers and sample cell values directly from spreadsheets in `RawData/`:
```powershell
py tools/train_column_classifier.py --fast-only
```

---

## Testing & Quality Assurance

Run the complete test suite (**72 automated tests**):
```powershell
py -m pytest -v
```

For full test reports, confusion matrices, and validation benchmarks across 5 real datasets, see [**`TEST_REPORT.md`**](TEST_REPORT.md).

---

## Programmatic Usage

```python
from pipeline.runner import PipelineRunner

runner = PipelineRunner(
    contract_path="config/workshop_contract.yaml",
    db_path="CleanData/cleaned_database.db"
)

summary = runner.run(
    input_file_path="RawData/Distraction_Era_Workshop_Dataset.xlsx",
    output_excel_path="CleanData/Workshop_Cleaned.xlsx"
)

print(f"Ingested: {summary.total_rows} | Cleaned: {summary.valid_rows} | Quarantined: {summary.quarantined_rows}")
print(f"Unique Persons Resolved: {summary.unique_persons_resolved} | Status: {summary.status}")
```

---

## Repository Structure

```text
DataCleaning/
├── dashboard.py              # Interactive Streamlit Web Studio
├── pipeline/                 # Core generalized ETL engine
│   ├── cli.py                # Command-line interface
│   ├── contract_engine.py    # Schema resolver & fuzzy header matching
│   ├── contract_generator.py # Auto contract generator & CLI tools
│   ├── entity_resolver.py    # MDM probabilistic deduplication & survivorship
│   ├── lookup_data.py        # Canonical lookups for Saudi colleges, majors, universities
│   ├── name_parser.py        # Compound-aware Arabic & English name parser
│   ├── normalizers.py        # E.164 phone, email typo healing, datetimes, lookups
│   ├── quarantine.py         # Dead-letter triage manager
│   ├── runner.py             # Multi-sheet workbook orchestrator
│   ├── schema.py             # Pydantic data contracts
│   └── storage.py            # SQLite & multi-sheet styled Excel persistence
├── installer/                # Windows installation & packaging suite
│   ├── install.bat / .ps1    # Automated installer (Non-admin HKCU & AppData)
│   ├── uninstall.bat / .ps1  # Clean uninstaller
│   ├── dclean_launcher.py    # Desktop GUI & right-click cleaner
│   ├── dclean_cli.py         # Global CLI wrapper
│   ├── dclean_setup.iss      # Inno Setup compiler script
│   ├── dclean.spec           # PyInstaller standalone specification
│   └── assets/               # Application icons (.ico)
├── config/                   # Declarative YAML schema contracts
├── models/                   # Trained NLP column classification weights (.joblib)
├── tools/                    # Data harvesting & model training scripts
├── RawData/                  # Input spreadsheets
├── CleanData/                # Processed output workbooks & SQLite database
├── tests/                    # 72 unit, integration, and stress tests
├── TEST_REPORT.md            # Quality assurance and verification report
└── README.md                 # Project documentation
```
