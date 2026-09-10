import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

# Fixed namespace UUID for deterministic UUIDv5 generation across batches
PIPELINE_NAMESPACE = uuid.UUID("e7b3992b-8b54-4a27-a06f-47dc08e1bf9a")

def generate_deterministic_person_uuid(primary_key: str) -> str:
    """
    Generates a consistent, reproducible UUIDv5 from a canonical natural key
    (such as an E.164 phone number or lowercase email).
    Ensures that re-running the pipeline on different days assigns the exact same ID.
    """
    clean_key = str(primary_key).strip().lower()
    return str(uuid.uuid5(PIPELINE_NAMESPACE, clean_key))

class CleanPerson(BaseModel):
    """
    Dimension model representing a unique real-world individual in dim_persons.
    Used strictly for internal Master Data Management (MDM) deduplication and clustering.
    """
    person_id: str
    canonical_email: Optional[str] = None
    canonical_phone_e164: Optional[str] = None
    full_name_ar: Optional[str] = None
    full_name_en: Optional[str] = None
    first_name: Optional[str] = None
    father_name: Optional[str] = None
    family_name: Optional[str] = None
    clean_display_name: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class FactRegistration(BaseModel):
    """
    Transactional event record representing a registration/submission linked to dim_persons.
    """
    registration_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    person_id: str
    sheet_name: str = "default_sheet"
    dataset_id: str = "default_dataset"
    attended_flag: bool = False
    consent_photo: bool = False
    major: Optional[str] = None
    university: Optional[str] = None
    academic_lvl: Optional[str] = None
    registered_at: str
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)

class QuarantineRecord(BaseModel):
    """
    Dead-letter store record for rows failing contract assertions.
    Captures exact raw row data and specific programmatic failure codes.
    """
    quarantine_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_file: str
    sheet_name: str
    row_index: int
    raw_payload: Dict[str, Any]
    rejection_codes: List[str]
    quarantined_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class AuditSummary(BaseModel):
    """
    Observability & governance summary for a batch ingestion run.
    """
    source_file: str
    sheet_name: str
    total_rows: int
    valid_rows: int
    quarantined_rows: int
    unique_persons_resolved: int
    duplicate_events_merged: int
    quarantine_rate_pct: float
    status: str
