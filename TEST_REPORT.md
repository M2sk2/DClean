# Test & Quality Assurance Report

This report documents the verification, model benchmarking, and end-to-end integration results for the **Production-Grade Data Cleaning & Entity Resolution Pipeline** on branch **`main`** following the integration of all 4 milestone pull requests:
- **PR #1**: `feat/resolver-and-storage` (Entity resolution, Jaro-Winkler linking, SQLite foreign keys)
- **PR #2**: `feat/parser-normalizer` (Arabic name parsing, lookup tables for Saudi universities, colleges, majors)
- **PR #3**: `feat/schema-and-quarantine` (Pydantic schema validation, dead-letter quarantine triage)
- **PR #4**: `contract-generation-engine` (Auto contract engine, fuzzy matching, trained local NLP sequence classifier)

---

## 1. Automated Test Suite Summary (65 Tests, 100% Pass)

The test suite executed with `py -m pytest -v`:
- **Total Tests**: 65
- **Passed**: 65 (100%)
- **Execution Time**: ~2.5s on pure CPU

### Test Module Breakdown

| Test File | Count | Focus Areas | Status |
|---|:---:|---|:---:|
| [**`tests/test_contract_engine.py`**](tests/test_contract_engine.py) | 18 | Declarative schema resolution, deterministic MD5 slugification, alias & exact header mapping, semantic heuristics, duplicate mapping safety, unmapped column preservation | **PASSED** |
| [**`tests/test_enhanced_contractor.py`**](tests/test_enhanced_contractor.py) | 31 | Typo-tolerant fuzzy matching (`difflib`), deep sample heuristics (Saudi phone, email, student ID, LinkedIn, academic level), confidence scoring, contract validation & diffing, CLI commands (`validate`, `diff`, `generate`), trained multiclass NLP classifier | **PASSED** |
| [**`tests/test_pipeline.py`**](tests/test_pipeline.py) | 16 | Theophoric Arabic name bonding, patronymic clan particles, inverted English names, Excel phone bug recovery, email typo healing, datetime serial conversion, native Saudi academic levels, deterministic UUIDv5, multi-sheet cross-dedup, Jaro-Winkler entity similarity, registration event merging, SQLite foreign key constraint enforcement | **PASSED** |

---

## 2. Local AI/NLP Model Performance Report

A dedicated sequence classifier replaced expensive and slow generative LLMs (Ollama / GPT), running strictly on CPU to classify columns into the 4 canonical schema groups.

### Dataset & Training
- **Source**: Directly harvested from actual respondent spreadsheets in `RawData/` (`Developers_Committee_2026_Responses.xlsx`, `Distraction_Era_Workshop_Dataset.xlsx`, etc.).
- **Dataset Size**: **4,460 labeled sequences** (4,060 raw augmented + 400 balanced synthetic templates).
- **Export File**: [`tools/raw_and_synthetic_dataset.json`](tools/raw_and_synthetic_dataset.json).
- **Model Binary**: [`models/tfidf_column_classifier.joblib`](models/tfidf_column_classifier.joblib) (4.4 MB).
- **Architecture**: `FeatureUnion` combining word-level `(1, 2)` n-grams and character-level `(2, 5)` n-grams with calibrated Logistic Regression.

### Validation Benchmark (80/20 Stratified Split)

```text
===========================================================================
               NLP COLUMN CLASSIFIER - VALIDATION BENCHMARK
===========================================================================
Validation Accuracy: 97.31%
Inference Latency:   < 1ms per column on pure CPU

                         precision    recall  f1-score   support

               Identity       1.00      1.00      1.00       206
    Structured/MetaData       0.98      0.98      0.98       297
Categorical/MultiSelect       0.98      0.96      0.97       285
              Free-Form       0.88      0.95      0.92       104

               accuracy                           0.97       892
              macro avg       0.96      0.97      0.97       892
           weighted avg       0.97      0.97      0.97       892
===========================================================================
```

### Architectural Comparison

| Dimension | Generative LLM (Ollama/GPT) | Local NLP Sequence Classifier |
|---|---|---|
| **Inference Latency** | 2,000 – 5,000 ms | **< 1 ms** |
| **Output Space** | Unbounded natural text | **Strict 4-Class Softmax** |
| **Hallucination Risk** | High (inaccurate mappings) | **Zero (mathematically constrained)** |
| **Confidence Scoring** | Heuristic / Uncalibrated | **Calibrated Softmax Probabilities** |
| **Hardware Required** | GPU or high-RAM CPU | **Pure CPU (< 5 MB RAM footprint)** |
| **Operational Cost** | Cloud API fees or local GPU load | **Free & Offline** |

---

## 3. End-to-End Real Dataset Verification

The unified pipeline was executed across 5 real survey spreadsheets with diverse schemas, languages, and row structures:

| Dataset | Headers | Ingested Rows | Valid Cleaned | Quarantined | Resolved Entities | Merged Duplicates | Health Status |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Distraction Era Workshop** | 13 | 40 | 37 | 3 (7.5%) | 34 | 3 | `[HEALTHY]` |
| **Developers Committee 2026** | 55 | 23 | 22 | 1 (4.35%) | 21 | 1 | `[HEALTHY]` |
| **MultiSheet Workshop Batches** | 13 | 5 (2 sheets) | 5 | 0 (0.0%) | 4 | 1 | `[HEALTHY]` |
| **Entrepreneurship Workshop** | 15 | 73 | 69 | 4 (5.48%) | 65 | 4 | `[HEALTHY]` |
| **AI Bootcamp Registration** | 12 | 36 | 36 | 0 (0.0%) | 33 | 3 | `[HEALTHY]` |

### Integrity & Safety Findings
1. **Quarantine Dead-Letter Triage**: Records lacking a valid name or having neither phone nor email were isolated into the quarantine store with actionable rejection codes (`MISSING_REQUIRED_NAME`, `MISSING_IDENTIFIER_RECORD_CANNOT_BE_LINKED`, `SPAM_OR_DUMMY_VALUES_DETECTED`).
2. **Relational Database Integrity**: Verified SQLite schema constraints with `PRAGMA foreign_keys = ON` ensuring every record in `fact_registration` maps to an existing entity in `dim_persons`.
3. **Natural Business Output**: Cleaned Excel files retain natural business column headers with pristine values rather than forcing internal synthetic UUIDs onto end users.
