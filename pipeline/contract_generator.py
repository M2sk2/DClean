import re
import os
import yaml
from typing import List, Dict, Any, Optional

class AutoContractGenerator:
    """
    Automated Schema Contractor & 4-Group Column Classifier.
    Analyzes raw spreadsheet headers and sample data rows to:
    1. Group every column into one of the 4 guideline groups:
       - Identity
       - Structured/MetaData
       - Categorical/MultiSelect
       - Free-Form
    2. Map canonical fields to internal standard targets (full_name_ar, email, phone, etc.).
    3. Generate and cache a declarative YAML contract (config/<dataset_id>_contract.yaml).
    """

    IDENTITY_PATTERNS = {
        "full_name_ar": [r"اسم.*عرب", r"fullname.*ar", r"الاسم الثلاثي", r"الاسم الكامل", r"اسم المشارك", r"اسم الطالب"],
        "full_name_en": [r"اسم.*انجل", r"اسم.*إنجل", r"fullname.*en", r"english name", r"participant name"],
        "phone": [r"جوال", r"هاتف", r"phone", r"mobile", r"whatsapp", r"واتساب", r"رقم.*تواصل", r"وسيلة.*تواصل"],
        "email": [r"بريد", r"ايميل", r"إيميل", r"email", r"gmail"],
        "academic_email": [r"بريد.*جامع", r"إيميل.*جامع", r"student.*email", r"academic.*email"]
    }

    STRUCTURED_PATTERNS = {
        "registered_at": [r"timestamp", r"وقت", r"تاريخ", r"date", r"submission time"],
        "student_id": [r"الرقم.*الجامعي", r"رقم.*الطالب", r"رقم.*القيد", r"student.*id", r"academic.*id"],
        "university": [r"اسم.*الجامعة", r"^الجامعة$", r"جهة.*الدراسة", r"university", r"^uni$"],
        "major": [r"تخصص", r"major", r"قسم", r"college", r"كلية", r"specialization"],
        "academic_lvl": [r"مستوى.*دراس", r"سنة.*دراس", r"academic.*lvl", r"academic.*level", r"مرحلة.*دراس"],
        "gender": [r"جنس", r"gender", r"ذكر/أنثى"],
        "branch": [r"فرع", r"branch", r"مدينة", r"city", r"منطقة", r"مقر"],
        "linkedin_url": [r"linkedin", r"لينكد"]
    }

    CATEGORICAL_PATTERNS = {
        "attendance": [r"حضور", r"attendance", r"حاضر", r"status"],
        "consent_photo": [r"تصوير", r"photo", r"صورة", r"موافقة.*تصوير", r"تغطية.*إعلامية"],
        "is_member": [r"عضو", r"member"],
        "boolean_question": [r"^هل\s+", r"agree", r"موافق"]
    }

    @classmethod
    def _normalize_str(cls, text: str) -> str:
        s = str(text).strip().lower()
        s = re.sub(r"[^\w\s]", " ", s)
        return re.sub(r"\s+", " ", s).strip()

    @classmethod
    def classify_column(cls, header: str, sample_values: Optional[List[Any]] = None) -> Dict[str, Any]:
        """
        Classifies a single header + sample values into the 4 guideline groups.
        """
        norm_h = cls._normalize_str(header)
        samples_str = " ".join(str(s).lower() for s in (sample_values or []) if s is not None)

        # 1. Identity Check
        for field, patterns in cls.IDENTITY_PATTERNS.items():
            for p in patterns:
                if re.search(p, norm_h, re.IGNORECASE):
                    return {
                        "target_field": field,
                        "group": "Identity",
                        "type": "phone" if field == "phone" else ("email" if "email" in field else "string"),
                        "transformers": ["strip", f"normalize_{field}"]
                    }

        # Catch generic 'name'
        if any(w in norm_h for w in ["name", "الاسم"]):
            if any(w in norm_h for w in ["en", "english", "انجليزي", "إنجليزي"]):
                return {"target_field": "full_name_en", "group": "Identity", "type": "string", "transformers": ["strip", "title_case_en"]}
            else:
                return {"target_field": "full_name_ar", "group": "Identity", "type": "string", "transformers": ["strip", "normalize_arabic_name"]}

        # 2. Structured / MetaData Check
        for field, patterns in cls.STRUCTURED_PATTERNS.items():
            for p in patterns:
                if re.search(p, norm_h, re.IGNORECASE):
                    return {
                        "target_field": field,
                        "group": "Structured/MetaData",
                        "type": "datetime" if field == "registered_at" else "string",
                        "transformers": ["strip", f"canonical_{field}"]
                    }

        # Check if samples look like datetimes or numeric serials
        if any(re.match(r"^\d{4}-\d{2}-\d{2}", str(s).strip()) for s in (sample_values or []) if s):
            return {
                "target_field": "registered_at",
                "group": "Structured/MetaData",
                "type": "datetime",
                "transformers": ["parse_utc_iso"]
            }

        # 3. Categorical / MultiSelect Check
        for field, patterns in cls.CATEGORICAL_PATTERNS.items():
            for p in patterns:
                if re.search(p, norm_h, re.IGNORECASE):
                    return {
                        "target_field": cls._slugify(header),
                        "group": "Categorical/MultiSelect",
                        "type": "boolean",
                        "transformers": ["parse_boolean"]
                    }

        # Check if sample values are clearly boolean (نعم / لا, yes / no)
        clean_samples = [str(s).strip().lower() for s in (sample_values or []) if s]
        if clean_samples and all(s in ["نعم", "لا", "yes", "no", "true", "false", "موافق", "غير موافق", "1", "0"] for s in clean_samples):
            return {
                "target_field": cls._slugify(header),
                "group": "Categorical/MultiSelect",
                "type": "boolean",
                "transformers": ["parse_boolean"]
            }

        # Check if samples are comma/semicolon-separated multi-select lists
        if any(any(d in str(s) for d in [",", "،", ";"]) for s in clean_samples):
            return {
                "target_field": cls._slugify(header),
                "group": "Categorical/MultiSelect",
                "type": "string",
                "transformers": ["strip", "normalize_multiselect"]
            }

        # Check choice/selection keywords in header
        if any(k in norm_h for k in ["اختر", "اختيار", "select", "choose", "radio"]):
            return {
                "target_field": cls._slugify(header),
                "group": "Categorical/MultiSelect",
                "type": "string",
                "transformers": ["strip"]
            }

        # 4. Free-Form Check (Questions, descriptions, motivations, challenges)
        if any(k in norm_h for k in [
            "ماذا", "لماذا", "كيف", "صف", "توقع", "تشتت", "خبرة", "مهارات", "تحدي",
            "what", "why", "how", "describe", "explain", "expect", "distract", "skill", "challenge"
        ]) or (sample_values and any(len(str(s).split()) > 5 for s in sample_values if s)):
            return {
                "target_field": cls._slugify(header),
                "group": "Free-Form",
                "type": "text",
                "transformers": ["strip"]
            }

        # Default fallback
        return {
            "target_field": cls._slugify(header),
            "group": "Structured/MetaData",
            "type": "string",
            "transformers": ["strip"]
        }

    @staticmethod
    def _slugify(text: str) -> str:
        s = re.sub(r"[^\w\s]", "", str(text)).strip().lower()
        slug = re.sub(r"\s+", "_", s)
        # If Arabic or empty, truncate
        if not slug or not re.match(r"^[a-zA-Z0-9_]+$", slug):
            # Create deterministic alphanumeric hash
            h = abs(hash(text)) % 1000000
            return f"col_{h}"
        return slug[:40]

    @classmethod
    def generate_contract(
        cls,
        headers: List[str],
        sample_rows: Optional[List[Dict[str, Any]]] = None,
        dataset_id: str = "dataset",
        output_yaml_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates a complete declarative YAML contract for a tabular dataset.
        """
        mappings = []
        assigned_targets = set()

        for h in headers:
            samples = []
            if sample_rows:
                for row in sample_rows[:5]:
                    if h in row and row[h] is not None:
                        samples.append(row[h])

            classification = cls.classify_column(h, samples)
            target = classification["target_field"]
            # If target already assigned, disambiguate with slug
            if target in assigned_targets:
                target = f"{target}_{cls._slugify(h)}"
            assigned_targets.add(target)

            mapping_entry = {
                "target_field": target,
                "group": classification["group"],
                "type": classification["type"],
                "aliases": [h],
                "required": classification["group"] == "Identity" and target in ["phone", "email", "full_name_ar"],
                "transformers": classification["transformers"]
            }
            mappings.append(mapping_entry)

        contract_dict = {
            "version": 1.0,
            "dataset_id": dataset_id,
            "quarantine_threshold_pct": 15.0,
            "canonical_mappings": mappings,
            "unmapped_columns_strategy": "store_jsonb"
        }

        if output_yaml_path:
            os.makedirs(os.path.dirname(output_yaml_path), exist_ok=True)
            with open(output_yaml_path, "w", encoding="utf-8") as f:
                yaml.dump(contract_dict, f, allow_unicode=True, sort_keys=False)
            print(f"[ContractGenerator] Generated contract -> {output_yaml_path}")

        return contract_dict
