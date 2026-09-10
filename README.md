# Production-Grade Generalized Data Cleaning & Entity Resolution Pipeline

A generalized, multi-dataset ETL data cleaning and entity resolution system built specifically for tabular responses (`.xlsx` and `.csv`). Built in strict accordance with the project guidelines in [`Guidelines/`](Guidelines/).

---

## 1. Architectural Principles & Guidelines Alignment

The system strictly enforces the boundary between **Deterministic Normalization** (where zero data corruption is tolerated) and **Stochastic / Probabilistic Reasoning** (where human variation occurs):

```
                                 RAW TABULAR DATASET
                                (.xlsx / .csv formats)
                                          │
                  [Stochastic / AI]       ▼
    ┌───────────────────────────────────────────────────────────────────────────┐
    │ 1. Schema Contractor & Column Grouping Classifier                         │
    │    - Auto-classifies headers into 4 schema groups:                        │
    │      * Identity                                                           │
    │      * Structured / MetaData                                              │
    │      * Categorical / MultiSelect                                          │
    │      * Free-Form                                                          │
    │    - Dynamically generates declarative YAML contracts                     │
    └─────────────────────────────────────┬─────────────────────────────────────┘
                                          │
                  [Deterministic]         ▼
    ┌───────────────────────────────────────────────────────────────────────────┐
    │ 2. Deterministic Cleaning & Normalization Engine                          │
    │    - Identity: Compound-aware Arabic/English NLP, E.164 Saudi phones      │
    │      (auto-fixing Excel dropped zeros), email domain typo auto-healing    │
    │    - Metadata: Native Saudi higher education academic level mapping       │
    │      (zero pseudo-normalization), university canonical lookup             │
    │    - Categorical / MultiSelect: Multilingual booleans, clean token lists  │
    │    - Quarantine: Dead-letter triage store with rejection reason codes     │
    └─────────────────────────────────────┬─────────────────────────────────────┘
                                          │
                  [Probabilistic]         ▼
    ┌───────────────────────────────────────────────────────────────────────────┐
    │ 3. Entity Resolution & Deduplication (MDM Layer)                          │
    │    - Probabilistic record linkage (Jaro-Winkler) + deterministic indexing │
    │    - Deterministic UUIDv5 clustering across batches                       │
    │    - Survivorship rules (recency timestamps & completeness union)         │
    │    - Kept strictly internal: Clean output retains natural columns         │
    └─────────────────────────────────────┬─────────────────────────────────────┘
                                          │
                                          ▼
                                 PERSISTED OUTPUT
    ┌───────────────────────────────────────────────────────────────────────────┐
    │ - Cleaned Dataset (.xlsx): Natural business columns, pristine & deduplicated│
    │ - Quarantine Store (.xlsx): Rejected records with specific failure codes  │
    │ - Audit Summary (.xlsx): Ingestion, deduplication & quality metrics       │
    │ - SQLite Database (.db): dim_persons, fact tables, quarantine, and audit  │
    └───────────────────────────────────────────────────────────────────────────┘
```

---

## 2. The 4 Column Taxonomy Groups

Every column ingested by the pipeline belongs to one of four strict groups:

| Group | Nature & Handling Rules | Examples |
| :--- | :--- | :--- |
| **1. Identity** | **Strictly Deterministic.** Zero AI hallucination or pseudo-normalization permitted. Compound-aware NLP for Arabic and English names, E.164 Saudi phone formatting, and email syntax/typo healing. | `الاسم الكامل`, `FullName(En)`, `رقم الجوال`, `البريد الإلكتروني` |
| **2. Structured / MetaData** | Standardized context attributes. Evaluated against controlled vocabularies (e.g. Saudi universities and academic levels). Datetimes converted to UTC ISO-8601. | `الجامعة`, `التخصص`, `المستوى الدراسي`, `Timestamp` |
| **3. Categorical / MultiSelect** | Controlled options and agreements. Boolean parsing (`نعم/لا`, `حضر/غائب`), checkbox list splitting, trimming, and deduplication. | `الموافقة على الشروط`, `حالة الحضور`, `المهارات التقنية` |
| **4. Free-Form** | User raw answers. Text sanitization while preserving original nuance and meaning without destructive rewriting. | `توقعاتك من الورشة`, `أكبر مصدر تشتت`, `لماذا ترغب بالانضمام؟` |

---

## 3. Core Engine Capabilities

### A. Deterministic Identity Normalization ([`pipeline/normalizers.py`](pipeline/normalizers.py))
- **Saudi Arabia Phone Normalization**:
  - Automatically heals the classic Excel bug where leading zeros are stripped (`508889900` $\rightarrow$ `+966508889900`).
  - Resolves double zero international prefixes (`009665...` $\rightarrow$ `+9665...`).
  - Eliminates redundant local prefixes appended to international (`+96605...` $\rightarrow$ `+9665...`).
  - Strips formatting noise (spaces, dashes, parentheses).
- **Email Normalization**:
  - Trims whitespace, removes `mailto:` prefixes, and lowercases text.
  - Automatically heals common domain typos: `@gmaill.com` $\rightarrow$ `@gmail.com`, `@hotmial.com` $\rightarrow$ `@hotmail.com`, `@outloo.com` $\rightarrow$ `@outlook.com`.
- **Compound-Aware Name Parser ([`pipeline/name_parser.py`](pipeline/name_parser.py))**:
  - Bonds theophoric and compound Arabic prefixes into a single token (`عبد الله` $\rightarrow$ `عبدالله`, `سيف الدين`, `نور الهدى`).
  - Preserves patronymic and clan particles (`آل سعود`, `بن باز`, `أبو بكر`).
  - Handles diacritics/harakat (`مُحَمَّد`).
  - Handles inverted English names (`Al-Harbi, Salman` $\rightarrow$ First: `Salman`, Family: `Al-Harbi`).
  - Strips honorific titles (`د.`, `م.`, `أستاذ`, `Dr.`, `Eng.`).
- **Saudi Higher Education Academic Level Normalization**:
  - Standardizes to native Saudi terminology (`سنة تحضيرية`, `بكالوريوس - سنة 1`, `بكالوريوس - سنة 2`, `بكالوريوس - سنة 3`, `بكالوريوس - سنة 4`, `بكالوريوس - سنة 5`, `سنة امتياز`, `خريج`, `ماجستير`, `دكتوراه`).
  - **Zero Pseudo-Normalization**: If a student enters an unlisted role (`طالب زائر`, `طالب ثانوي`), the string is preserved trimmed as-is rather than hallucinating an arbitrary English category.

### B. Automated Schema Contractor ([`pipeline/contract_generator.py`](pipeline/contract_generator.py))
- No need to handcraft YAML files manually for every new dataset.
- Analyzes incoming headers and sample values, classifies them into the 4 groups, and produces a cached contract in `config/<dataset>_contract.yaml`.
- Compatible with local lightweight LLMs (Qwen 2.5 3B/7B via Ollama), Cloud APIs (Gemini Flash), or the built-in zero-dependency offline semantic heuristic engine.

### C. Multi-Sheet Excel Processing ([`pipeline/runner.py`](pipeline/runner.py))
- Automatically discovers all tabular sheets within workbooks (`wb.sheetnames`).
- Auto-detects table header rows and skips blank/notes sheets.
- Cleans and deduplicates participants across sheets and batches.

### D. Probabilistic Entity Resolution & Deduplication ([`pipeline/entity_resolver.py`](pipeline/entity_resolver.py))
- Master Data Management (MDM) layer combining deterministic phone/email indexing with Jaro-Winkler string similarity on normalized name keys.
- Assigns reproducible, deterministic UUIDv5 identifiers.
- Applies survivorship rules: merges most complete contact info, retains latest submission timestamp, and preserves positive attendance.
- **Clean Natural Output**: Synthetic internal IDs are kept strictly in the database and not forced onto the business spreadsheet.

### E. Quarantine Dead-Letter Store ([`pipeline/quarantine.py`](pipeline/quarantine.py))
- Rows violating core contract assertions (missing name, missing all contact info, or test spam) are isolated with machine-readable rejection codes:
  - `MISSING_REQUIRED_NAME`
  - `MISSING_IDENTIFIER_RECORD_CANNOT_BE_LINKED`
  - `SPAM_OR_DUMMY_VALUES_DETECTED`

---

## 4. Repository Structure

```
DataCleaning/
│
├── pipeline/                           # Core generalized pipeline package
│   ├── __init__.py                     # Package exports
│   ├── schema.py                       # Pydantic data models
│   ├── name_parser.py                  # Compound-aware Arabic/English name parser
│   ├── normalizers.py                  # Phone (+966), Email, DateTime, Academic normalizers
│   ├── contract_generator.py           # Automated 4-group schema contractor
│   ├── contract_engine.py              # Dynamic header resolution & JSONB extractor
│   ├── entity_resolver.py              # MDM probabilistic deduplication layer
│   ├── quarantine.py                   # Dead-letter triage manager
│   ├── storage.py                      # SQLite & styled multi-sheet Excel persistence
│   ├── runner.py                       # Multi-sheet orchestrator
│   └── cli.py                          # Command-line interface
│
├── config/                             # Declarative YAML schema contracts
│   ├── workshop_contract.yaml          # Contract for Distraction_Era (13 columns)
│   └── developers_committee_contract.yaml # Contract for Developers Committee (55 columns)
│
├── Guidelines/                         # Project specifications
│   ├── DataCleaning_Schema.md          # 4-group schema definitions
│   ├── Generalization.md               # ETL generalization & architectural rules
│   ├── DataGenerating.md               # Synthetic dirty data injection rules
│   ├── Pipeline_Documentation.md       # Comprehensive technical deep-dive
│   └── Probabilistic Record Linkage... # Entity linkage references
│
├── RawData/                            # Synthetic raw input datasets
│   ├── Distraction_Era_Workshop_Dataset.xlsx # 13 columns, 40 rows
│   ├── Developers_Committee_2026_Responses.xlsx # 55 columns, 23 rows
│   └── MultiSheet_Workshop_Batches.xlsx # 2 sheets with shared attendees
│
├── CleanData/                          # Processed outputs
│   ├── Distraction_Era_Cleaned.xlsx
│   ├── Developers_Committee_Cleaned.xlsx
│   ├── MultiSheet_Cleaned.xlsx
│   └── cleaned_database.db             # Relational SQLite database
│
├── tools/
│   └── generate_datasets.py            # Synthetic dirty dataset generator
│
├── tests/
│   └── test_pipeline.py                # 13 automated unit & integration tests
│
└── README.md                           # Master project documentation
```

---

## 5. Quickstart & Usage

### 1. Installation
The pipeline requires Python 3.10+ and standard libraries:
```bash
py -m pip install openpyxl phonenumbers pydantic pyyaml pytest pandas
```

### 2. Generate Synthetic Datasets
To generate the dirty test datasets with controlled anomalies:
```bash
py tools/generate_datasets.py
```

### 3. Run via Command-Line Interface (CLI)

**Option A: Clean Dataset with an Existing Contract**:
```bash
py -m pipeline.cli --input RawData/Distraction_Era_Workshop_Dataset.xlsx --contract config/workshop_contract.yaml --output-excel CleanData/Distraction_Era_Cleaned.xlsx
```

**Option B: Clean Wide 55-Column Dataset**:
```bash
py -m pipeline.cli --input RawData/Developers_Committee_2026_Responses.xlsx --contract config/developers_committee_contract.yaml --output-excel CleanData/Developers_Committee_Cleaned.xlsx
```

**Option C: Clean with Auto-Generated Contract (Zero Manual Configuration)**:
```bash
py -m pipeline.cli --input RawData/MultiSheet_Workshop_Batches.xlsx --output-excel CleanData/MultiSheet_Cleaned.xlsx
```

### 4. Run Automated Test Suite (TDD)
```bash
py -m pytest tests/test_pipeline.py -v
```

---

## 6. Programmatic Python Usage

```python
from pipeline.runner import PipelineRunner

# Initialize runner (contract_path is optional; auto-generates if None)
runner = PipelineRunner(
    contract_path="config/workshop_contract.yaml",
    db_path="CleanData/cleaned_database.db"
)

# Run end-to-end cleaning & entity deduplication
summary = runner.run(
    input_file_path="RawData/Distraction_Era_Workshop_Dataset.xlsx",
    output_excel_path="CleanData/Workshop_Cleaned.xlsx"
)

print(f"Ingested: {summary.total_rows}")
print(f"Cleaned Valid: {summary.valid_rows}")
print(f"Quarantined: {summary.quarantined_rows} ({summary.quarantine_rate_pct}%)")
print(f"Unique Entities Resolved: {summary.unique_persons_resolved}")
print(f"Duplicates Merged: {summary.duplicate_events_merged}")
print(f"Status: {summary.status}")
```
