from pydantic import BaseModel
from typing import List, Optional, Any


class VendorBase(BaseModel):
    vendor_id: str
    vendor_name: str
    business_type: str
    city: str
    vendor_age: Optional[int] = None
    business_age_months: Optional[int] = None
    archetype: Optional[str] = None

class VendorCardResponse(VendorBase):
    credit_score: int
    rating: str
    behavioral_trust: int
    risk: str
    volume: float
    growth: float
    days: int
    transactions: int
    customers: int
    spv: float
    tsci: float
    mcs: float
    resilience: float
    svps: float

class TransactionResponse(BaseModel):
    transaction_id: str
    timestamp: str
    vendor_id: str
    counterparty_id: str
    transaction_type: str
    amount: float
    payment_channel: str
    status: str = 'Normal'

class BehavioralMetricsResponse(BaseModel):
    vendor_id: str
    fsi: float
    tci: float
    bgi: float
    fri: float
    spv: float
    tsci: float
    mcs: float
    resilience: float
    svps: float
    active_days: int
    total_volume: float
    growth_rate: float
    unique_customers: int
    avg_tx_per_day: int

class FraudAnalysisResponse(BaseModel):
    vendor_id: str
    fraud_risk: float
    svps: float
    risk_band: str
    rule_flags: List[str]
    rule_score: float
    anomaly_score: float
    has_cycles: bool
    cycle_count: int
    cycles: List[List[str]]
    evidence: List[str]
    decision: str
    action: str

class WaterfallItem(BaseModel):
    factor: str
    delta: int
    is_base: bool
    rationale: str

class WaterfallResponse(BaseModel):
    base_score: int
    final_score: int
    formula_summary: str
    waterfall_items: List[WaterfallItem]

class AssessmentResponse(BaseModel):
    vendor_id: str
    vendor_name: str
    business_type: str
    city: str
    credit_score: int
    rating: str
    q_base: float
    q_final: float
    svps: float
    behavioral_trust: int
    fraud_risk: float
    decision: str
    action: str
    confidence: str
    top_positive_factors: List[str]
    top_negative_factors: List[str]
    spv: float
    tsci: float
    mcs: float
    resilience: float
    fsi: float
    tci: float
    bgi: float
    fri: float
    p10_score: Optional[int] = None
    p50_score: Optional[int] = None
    p90_score: Optional[int] = None
    waterfall: Optional[WaterfallResponse] = None

class VoiceIntentRequest(BaseModel):
    language_code: str = 'hi'
    raw_text: Optional[str] = None
    voice_audio_base64: Optional[str] = None

class FieldProvenance(BaseModel):
    field: str
    value: str
    source: str
    confidence: float
    status: str

class VoiceIntentResponse(BaseModel):
    vendor_id: str
    language_code: str
    language_name: str
    transcription: str
    extracted_intent: str
    loan_amount_requested: float
    repayment_tenure_months: int
    estimated_emi: float
    readback_verification_text: str
    readback_status: str
    fields_provenance: List[FieldProvenance]
    overall_confidence: float
    audit_hash: str
    prev_audit_hash: str
    timestamp: str

class ReadbackConfirmRequest(BaseModel):
    vendor_id: str
    application_data: Optional[dict] = None
    prev_hash: Optional[str] = None

class LoanSubmissionResponse(BaseModel):
    vendor_id: str
    application_id: str
    status: str
    readback_status: str
    audit_hash: str
    prev_audit_hash: str
    timestamp: str
    submission_receipt: dict

class AAConsentResponse(BaseModel):
    consent_id: str
    vendor_id: str
    status: str
    fiu_id: str
    fip_id: str
    consent_handle: str
    created_at: str
    expires_at: str
    verified_bank_name: Optional[str] = None
    account_mask: Optional[str] = None
    avg_daily_balance: Optional[float] = None
    outward_cheque_bounces: Optional[int] = None
    aa_data_verified: Optional[bool] = None
    frequency: Optional[Any] = 'DAILY RECURRENT'
    data_range: Optional[Any] = None


class AAInitiateRequest(BaseModel):
    vendor_id: str
    fip_id: Optional[str] = 'SBI-FIP-01'
    purpose_code: Optional[str] = 'CREDIT_ASSESSMENT'

