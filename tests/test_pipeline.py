import os
import pytest
from pipeline.name_parser import ArabicNameParser
from pipeline.normalizers import PhoneNormalizer, EmailNormalizer, DateTimeNormalizer, CategoricalNormalizer
from pipeline.schema import generate_deterministic_person_uuid
from pipeline.runner import PipelineRunner
from pipeline.contract_generator import AutoContractGenerator

def test_arabic_name_compound_bonding():
    # Test that 'عبد الله' is bonded and not split
    parsed = ArabicNameParser.parse_arabic_name("عبد الله محمد السالم")
    assert parsed.first_name == "عبدالله"
    assert parsed.father_name == "محمد"
    assert parsed.family_name == "السالم"
    assert parsed.full_clean == "عبدالله محمد السالم"

def test_arabic_name_patronymic_clan():
    # Test 'آل سعود' and 'بن باز'
    parsed = ArabicNameParser.parse_arabic_name("أحمد بن إبراهيم آل سعود")
    assert parsed.first_name == "أحمد"
    assert "إبراهيم" in parsed.father_name
    assert parsed.family_name == "آل سعود"

def test_english_inverted_name():
    # Test 'Al-Harbi, Salman'
    parsed = ArabicNameParser.parse_english_name("Al-Harbi, Salman")
    assert parsed.first_name == "Salman"
    assert parsed.family_name == "Al-Harbi"
    assert parsed.full_clean == "Salman Al-Harbi"

def test_phone_normalization_and_excel_bug():
    # Test standard local 05
    assert PhoneNormalizer.normalize("0507788990") == "+966507788990"
    
    # Test Excel stripped leading zero (508889900 -> +966508889900)
    assert PhoneNormalizer.normalize("508889900") == "+966508889900"
    assert PhoneNormalizer.normalize(508889900) == "+966508889900"
    
    # Test double zero prefix (00966...)
    assert PhoneNormalizer.normalize("00966531122334") == "+966531122334"
    
    # Test redundant +96605...
    assert PhoneNormalizer.normalize("+9660554975066") == "+966554975066"
    
    # Test hyphens & spaces
    assert PhoneNormalizer.normalize("+966-54-321-7890") == "+966543217890"
    
    # Test invalid short phone
    assert PhoneNormalizer.normalize("0501234") is None

def test_email_normalization_and_typo_fix():
    # Test uppercase and extra whitespace
    assert EmailNormalizer.normalize("  FAHAD@HOTMAIL.COM  ") == "fahad@hotmail.com"
    
    # Test domain typo fix (@gmaill.com -> @gmail.com)
    assert EmailNormalizer.normalize("nouf@gmaill.com") == "nouf@gmail.com"
    assert EmailNormalizer.normalize("saif.basheer@hotmial.com") == "saif.basheer@hotmail.com"
    
    # Test malformed email without @
    assert EmailNormalizer.normalize("amal.sudairy.gmail.com") is None

def test_datetime_excel_serial():
    # Test Excel serial number float (46266.6125)
    iso_date = DateTimeNormalizer.normalize("46266.6125")
    assert "2026-09-01" in iso_date

def test_academic_level_native_normalization():
    # Test native Saudi terms (NO pseudo-normalization hallucination!)
    assert CategoricalNormalizer.normalize_academic_level("سنة أولى") == "بكالوريوس - سنة 1"
    assert CategoricalNormalizer.normalize_academic_level("1") == "بكالوريوس - سنة 1"
    assert CategoricalNormalizer.normalize_academic_level("سنة ثانية") == "بكالوريوس - سنة 2"
    assert CategoricalNormalizer.normalize_academic_level("سنة رابعة") == "بكالوريوس - سنة 4"
    assert CategoricalNormalizer.normalize_academic_level("خريج") == "خريج"
    assert CategoricalNormalizer.normalize_academic_level("سنة امتياز") == "سنة امتياز"
    
    # Non-standard term should be preserved trimmed WITHOUT hallucinating pseudo categories
    assert CategoricalNormalizer.normalize_academic_level("طالب زائر") == "طالب زائر"

def test_categorical_boolean_and_multiselect():
    # Booleans
    assert CategoricalNormalizer.parse_boolean("نعم") is True
    assert CategoricalNormalizer.parse_boolean("حاضر") is True
    assert CategoricalNormalizer.parse_boolean("موافق") is True
    assert CategoricalNormalizer.parse_boolean("لا") is False
    assert CategoricalNormalizer.parse_boolean("غائب") is False
    assert CategoricalNormalizer.parse_boolean(None) is None

    # Multi-select list splitting & deduplication
    skills = "Python, SQL, Python, Pandas، Docker; SQL"
    clean_skills = CategoricalNormalizer.normalize_multiselect(skills)
    assert clean_skills == "Python, SQL, Pandas, Docker"

def test_uuidv5_deterministic_consistency():
    # UUIDv5 produces identical outputs across calls
    uuid1 = generate_deterministic_person_uuid("+966501234567")
    uuid2 = generate_deterministic_person_uuid("+966501234567")
    uuid_diff = generate_deterministic_person_uuid("+966559876543")

    assert uuid1 == uuid2
    assert uuid1 != uuid_diff
    assert len(uuid1) == 36

def test_auto_contract_generator():
    headers = ["الاسم الكامل", "رقم الجوال", "البريد الإلكتروني", "المستوى الدراسي", "هل توافق على الشروط؟", "لماذا ترغب بالانضمام؟"]
    contract = AutoContractGenerator.generate_contract(headers=headers, dataset_id="test_contract")
    mappings = {m["aliases"][0]: m["group"] for m in contract["canonical_mappings"]}
    
    assert mappings["الاسم الكامل"] == "Identity"
    assert mappings["رقم الجوال"] == "Identity"
    assert mappings["البريد الإلكتروني"] == "Identity"
    assert mappings["المستوى الدراسي"] == "Structured/MetaData"
    assert mappings["هل توافق على الشروط؟"] == "Categorical/MultiSelect"
    assert mappings["لماذا ترغب بالانضمام؟"] == "Free-Form"

def test_end_to_end_workshop_dataset():
    dataset_file = r"c:\Users\Admin\Documents\DataCleaning\RawData\Distraction_Era_Workshop_Dataset.xlsx"
    contract_file = r"c:\Users\Admin\Documents\DataCleaning\config\workshop_contract.yaml"
    test_db = r"c:\Users\Admin\Documents\DataCleaning\CleanData\test_workshop.db"
    test_output_excel = r"c:\Users\Admin\Documents\DataCleaning\CleanData\test_workshop_cleaned.xlsx"

    if os.path.exists(test_db):
        os.remove(test_db)
    if os.path.exists(test_output_excel):
        os.remove(test_output_excel)

    runner = PipelineRunner(contract_path=contract_file, db_path=test_db)
    summary = runner.run(input_file_path=dataset_file, output_excel_path=test_output_excel)

    assert summary.total_rows == 40
    assert summary.quarantined_rows == 3 # Rows 38, 39, 40
    assert summary.valid_rows == 37
    assert summary.duplicate_events_merged >= 2 # Tariq Al-Ali, Layan Al-Sharif
    assert summary.status == "HEALTHY"
    assert os.path.exists(test_db)
    assert os.path.exists(test_output_excel)

def test_end_to_end_developers_committee_55_columns():
    dataset_file = r"c:\Users\Admin\Documents\DataCleaning\RawData\Developers_Committee_2026_Responses.xlsx"
    contract_file = r"c:\Users\Admin\Documents\DataCleaning\config\developers_committee_contract.yaml"
    test_db = r"c:\Users\Admin\Documents\DataCleaning\CleanData\test_committee.db"
    test_output_excel = r"c:\Users\Admin\Documents\DataCleaning\CleanData\test_committee_cleaned.xlsx"

    if os.path.exists(test_db):
        os.remove(test_db)
    if os.path.exists(test_output_excel):
        os.remove(test_output_excel)

    runner = PipelineRunner(contract_path=contract_file, db_path=test_db)
    summary = runner.run(input_file_path=dataset_file, output_excel_path=test_output_excel)

    assert summary.total_rows == 23
    assert summary.quarantined_rows == 1 # The row with missing name
    assert summary.valid_rows == 22
    assert summary.status == "HEALTHY"
    assert os.path.exists(test_db)
    assert os.path.exists(test_output_excel)

def test_multisheet_excel_processing_and_cross_sheet_dedup():
    dataset_file = r"c:\Users\Admin\Documents\DataCleaning\RawData\MultiSheet_Workshop_Batches.xlsx"
    test_db = r"c:\Users\Admin\Documents\DataCleaning\CleanData\test_multisheet.db"
    test_output_excel = r"c:\Users\Admin\Documents\DataCleaning\CleanData\test_multisheet_cleaned.xlsx"

    if os.path.exists(test_db):
        os.remove(test_db)
    if os.path.exists(test_output_excel):
        os.remove(test_output_excel)

    # Uses auto-generated schema contract since no contract path provided!
    runner = PipelineRunner(contract_path=None, db_path=test_db)
    summary = runner.run(input_file_path=dataset_file, output_excel_path=test_output_excel)

    # Sheet 1 has 3 rows, Sheet 2 has 2 rows = Total 5 rows
    assert summary.total_rows == 5
    assert summary.valid_rows == 5
    assert "Morning_Session" in summary.sheet_name
    assert "Evening_Session" in summary.sheet_name
    # Abdullah Al-Salem is in BOTH sheets! The MDM resolver merges him into 1 unique entity:
    # 3 in Sheet 1 + 1 new in Sheet 2 = 4 unique entities
    assert summary.unique_persons_resolved == 4
    assert summary.duplicate_events_merged >= 1
    assert os.path.exists(test_db)
    assert os.path.exists(test_output_excel)
