# DClean: Generalized Data Cleaning & Entity Resolution Pipeline

A high-performance, generalized ETL pipeline designed for bilingual (Arabic & English) tabular survey datasets (`.xlsx` and `.csv`). Built in strict accordance with the project guidelines in [`Guidelines/`](Guidelines/).

---

## Key Highlights

- **Local NLP Column Classifier**: Replaced slow generative LLMs with a lightweight, local sequence classifier (<1ms CPU inference, **97.31% validation accuracy**, zero hallucination risk).
- **Deterministic Identity Normalization**: Heals Excel dropped-zero bugs on Saudi phones (`508889900` $\rightarrow$ `+966508889900`), fixes domain typos (`@gmaill.com` $\rightarrow$ `@gmail.com`), and parses compound Arabic names (`عبد الله` $\rightarrow$ `عبدالله`).
- **Comprehensive Controlled Vocabularies**: 680+ canonical mappings for Saudi universities, colleges, majors, and native academic levels ([`pipeline/lookup_data.py`](pipeline/lookup_data.py)).
- **Quarantine Dead-Letter Store**: Isolates invalid records with specific rejection codes to prevent pipeline corruption without silent data loss.
- **MDM Entity Resolution**: Combines deterministic indexing and probabilistic Jaro-Winkler matching with reproducible UUIDv5 clustering and survivorship rules.
- **Relational & Business Outputs**: Dual persistence into SQLite (relational schema with `PRAGMA foreign_keys = ON`) and pristine formatted Excel (natural business columns without synthetic internal IDs).

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

## Quickstart & Windows Installation

### Option 1: One-Click Windows Setup (Zero Admin Rights Needed)
Double-click [`installer/install.bat`](installer/install.bat) or run in PowerShell:
```powershell
powershell -ExecutionPolicy Bypass -File installer/install.ps1
```
- Installs to `%LocalAppData%\Programs\DClean`.
- Generates Desktop and Start Menu shortcuts with app icon.
- Adds `dclean` to your system `PATH` for terminal access.
- Adds **"Clean with DClean"** right-click context menu to `.xlsx`, `.csv`, and `.xlsm` files.
- To uninstall anytime: run [`installer/uninstall.bat`](installer/uninstall.bat).

### Option 2: Desktop GUI Studio
Launch DClean anytime via your Desktop shortcut or run:
```powershell
dclean gui
# or
py installer/dclean_launcher.py
```

### Option 3: Standard Terminal CLI
```powershell
py -m pip install -r requirements.txt

# Run with auto-detected schema (Local NLP sequence classifier)
dclean clean -i "RawData/Distraction_Era_Workshop_Dataset.xlsx"

# Run with an explicit declarative contract
dclean clean -i "RawData/Developers_Committee_2026_Responses.xlsx" -c "config/developers_committee_contract.yaml"
```

### 3. Contract Tools (Validation, Diffing, Generation)

```powershell
# Validate an existing YAML contract
py -m pipeline.contract_generator validate -c "config/workshop_contract.yaml"

# Diff a spreadsheet's headers against a contract
py -m pipeline.contract_generator diff -i "RawData/Distraction_Era_Workshop_Dataset.xlsx" -c "config/workshop_contract.yaml"

# Auto-generate a new contract YAML from raw data
py -m pipeline.contract_generator generate -i "RawData/Distraction_Era_Workshop_Dataset.xlsx" -o "config/new_contract.yaml"
```

### 4. Train / Retrain the Column Classifier
Harvests actual column headers and cells directly from `RawData/`:
```powershell
py tools/train_column_classifier.py --fast-only
```

---

## Testing & Quality Assurance

Run the comprehensive test suite (65 tests):
```powershell
py -m pytest -v
```

For complete test logs, confusion matrices, and benchmarks across 5 real datasets, see [**`TEST_REPORT.md`**](TEST_REPORT.md).

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
├── config/                   # Declarative YAML schema contracts
├── models/                   # Trained NLP column classification weights (.joblib)
├── tools/                    # Data harvesting & model training scripts
├── RawData/                  # Input spreadsheets
├── CleanData/                # Processed output workbooks & SQLite database
├── tests/                    # 65 unit, integration, and stress tests
├── TEST_REPORT.md            # Quality assurance and verification report
└── README.md                 # Project documentation
```
