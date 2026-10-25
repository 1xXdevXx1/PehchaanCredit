import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional


# PM SVANidhi standard loan limits
SVANIDHI_TRANCHES = {
    1: 10000.0,
    2: 20000.0,
    3: 50000.0
}

VALID_CATEGORIES = [
    'Fruit & Vegetable',
    'Chai & Snacks',
    'Flower Vendor',
    'Street Food',
    'Cobbler / Artisan',
    'Textiles & Garments',
    'General Store',
    'Barber / Salon'
]

# Multilingual Voice Intent Sample Prompts & Templates
VOICE_INTENT_SAMPLES = {
    'hi': {
        'language': 'Hindi',
        'transcription': 'नमस्ते, मुझे अपनी फल की दुकान के लिए बीस हजार रुपये का पीएम स्वनिधि लोन चाहिए, बारह महीने की किश्त पर।',
        'intent': 'APPLY_LOAN',
        'loan_amount': 20000.0,
        'tenure_months': 12,
        'readback_template': 'नमस्ते {vendor_name} जी, आपने {business_type} के लिए ₹{amount:,.0f} के पीएम स्वनिधि ऋण हेतु {tenure} महीने की किश्त पर आवेदन दर्ज किया है। आपकी मासिक अनुमानित ईएमआई लगभग ₹{emi:,.0f} होगी। क्या आप इसे पुष्ट करते हैं?'
    },
    'ta': {
        'language': 'Tamil',
        'transcription': 'வணக்கம், எனது தேனீர் கடைக்காக இருபதாயிரம் ரூபாய் PM SVANidhi கடன் 12 மாத தவணையில் தேவைப்படுகிறது.',
        'intent': 'APPLY_LOAN',
        'loan_amount': 20000.0,
        'tenure_months': 12,
        'readback_template': 'வணக்கம் {vendor_name} அவர்களே, உங்கள் {business_type} வணிகத்திற்காக ₹{amount:,.0f} PM SVANidhi கடனுக்கு {tenure} மாத தவணைக்கு விண்ணப்பித்துள்ளீர்கள். உங்கள் உத்தேச மாதாந்திர தவணை ₹{emi:,.0f}. இதை உறுதிப்படுத்துகிறீர்களா?'
    },
    'te': {
        'language': 'Telugu',
        'transcription': 'నమస్కారం, నా కూరగాయల దుకాణానికి ఇరవై వేల రూపాయల PM SVANidhi రుణం 12 నెలల కాలపరిమితికి కావాలి.',
        'intent': 'APPLY_LOAN',
        'loan_amount': 20000.0,
        'tenure_months': 12,
        'readback_template': 'నమస్కారం {vendor_name} గారు, మీ {business_type} వ్యాపారానికి ₹{amount:,.0f} PM SVANidhi రుణాన్ని {tenure} నెలల కాలానికి దరఖాస్తు చేసుకున్నారు. మీ నెలవారీ చెల్లింపు సుమారు ₹{emi:,.0f}. మీరు దీన్ని ధృవీకరిస్తున్నారా?'
    },
    'mr': {
        'language': 'Marathi',
        'transcription': 'नमस्कार, माझ्या चहाच्या दुकानासाठी मला वीस हजार रुपयांचे पीएम स्वनिधी कर्ज १२ महिन्यांच्या हप्त्यावर हवे आहे.',
        'intent': 'APPLY_LOAN',
        'loan_amount': 20000.0,
        'tenure_months': 12,
        'readback_template': 'नमस्कार {vendor_name} जी, तुम्ही {business_type} साठी ₹{amount:,.0f} पीएम स्वनिधी कर्जासाठी {tenure} महिन्यांच्या हप्त्यासाठी अर्ज केला आहे. तुमचा अंदाजे मासिक हप्ता ₹{emi:,.0f} असेल. तुम्ही याची पुष्टी करता का?'
    },
    'en': {
        'language': 'English',
        'transcription': 'Hello, I want to apply for twenty thousand rupees PM SVANidhi loan for my shop with twelve months tenure.',
        'intent': 'APPLY_LOAN',
        'loan_amount': 20000.0,
        'tenure_months': 12,
        'readback_template': 'Hello {vendor_name}, you have requested a PM SVANidhi loan of ₹{amount:,.0f} for your {business_type} business with a repayment tenure of {tenure} months. Estimated monthly EMI is ₹{emi:,.0f}. Please confirm to proceed.'
    }
}

class AuditChain:
    """
    Immutable Hash-Chained Audit Log for Zero-Hallucination Agent actions.
    Each block hashes (prev_hash + timestamp + action + payload).
    """
    @staticmethod
    def compute_block_hash(prev_hash: str, timestamp: str, action: str, payload: dict) -> str:
        content = f"{prev_hash}|{timestamp}|{action}|{json.dumps(payload, sort_keys=True)}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

def process_voice_intent(
    vendor_id: str,
    language_code: str,
    voice_audio_base64: Optional[str] = None,
    raw_text: Optional[str] = None,
    vendor_profile: Optional[dict] = None
) -> Dict[str, Any]:
    """
    Simulates speech-to-intent pipeline (Whisper / Multilingual NLU) grounded with RAG
    against the vendor profile and transaction ledger.
    """
    lang = language_code.lower()
    if lang not in VOICE_INTENT_SAMPLES:
        lang = 'en'
        
    sample = VOICE_INTENT_SAMPLES[lang]
    transcription = raw_text if raw_text else sample['transcription']
    
    # Grounding to vendor profile
    v_name = (vendor_profile.get('vendor_name') if vendor_profile else None) or 'Murugan S.'
    b_type = (vendor_profile.get('business_type') if vendor_profile else None) or 'Fruit & Vegetable'
    city = (vendor_profile.get('city') if vendor_profile else None) or 'Chennai'
    
    # Determine tranche and loan amount based on intent or credit history
    requested_amt = sample['loan_amount']
    tenure = sample['tenure_months']
    monthly_rate = 0.07 / 12.0 # 7% subsidized interest under PM SVANidhi
    emi = (requested_amt * monthly_rate * ((1 + monthly_rate)**tenure)) / (((1 + monthly_rate)**tenure) - 1)
    
    readback_text = sample['readback_template'].format(
        vendor_name=v_name,
        business_type=b_type,
        amount=requested_amt,
        tenure=tenure,
        emi=emi
    )
    
    # Provenance trail with field-level confidence scores
    fields = [
        {
            'field': 'vendor_name',
            'value': v_name,
            'source': 'KYC_DATABASE',
            'confidence': 1.0,
            'status': 'VERIFIED'
        },
        {
            'field': 'business_category',
            'value': b_type,
            'source': 'MERCHANT_CLASSIFIER_RAG',
            'confidence': 0.98,
            'status': 'VERIFIED'
        },
        {
            'field': 'loan_amount_requested',
            'value': f"₹{requested_amt:,.0f}",
            'source': 'VOICE_INTENT_ASR',
            'confidence': 0.96,
            'status': 'EXTRACTED'
        },
        {
            'field': 'repayment_tenure_months',
            'value': f"{tenure} Months",
            'source': 'VOICE_INTENT_ASR',
            'confidence': 0.95,
            'status': 'EXTRACTED'
        },
        {
            'field': 'vpa_upi',
            'value': f"{vendor_id.lower()}@okaxis",
            'source': 'TRANSACTION_LEDGER',
            'confidence': 1.0,
            'status': 'VERIFIED'
        },
        {
            'field': 'urban_local_body_id',
            'value': f"ULB-TN-{city[:3].upper()}-0842",
            'source': 'MUNICIPAL_CORP_REGISTRY',
            'confidence': 0.92,
            'status': 'GROUNDED'
        },
        {
            'field': 'operating_pincode',
            'value': '600001' if city == 'Chennai' else '625001',
            'source': 'GEO_CLUSTERING',
            'confidence': 0.94,
            'status': 'GROUNDED'
        }
    ]
    
    # Genesis or next audit hash block
    genesis_prev = "0000000000000000000000000000000000000000000000000000000000000000"
    ts_now = datetime.now(timezone.utc).isoformat()
    block_payload = {
        'vendor_id': vendor_id,
        'language': lang,
        'loan_amount': requested_amt,
        'tenure': tenure,
        'transcription': transcription
    }
    block_hash = AuditChain.compute_block_hash(genesis_prev, ts_now, 'VOICE_INTENT_EXTRACTED', block_payload)
    
    return {
        'vendor_id': vendor_id,
        'language_code': lang,
        'language_name': sample['language'],
        'transcription': transcription,
        'extracted_intent': sample['intent'],
        'loan_amount_requested': requested_amt,
        'repayment_tenure_months': tenure,
        'estimated_emi': round(emi, 2),
        'readback_verification_text': readback_text,
        'readback_status': 'PENDING_CONFIRMATION',
        'fields_provenance': fields,
        'overall_confidence': 0.965,
        'audit_hash': block_hash,
        'prev_audit_hash': genesis_prev,
        'timestamp': ts_now
    }

def verify_and_confirm_application(
    vendor_id: str,
    application_data: dict,
    prev_hash: str
) -> Dict[str, Any]:
    """
    Confirms readback verification and seals the application into the audit chain.
    """
    ts_now = datetime.now(timezone.utc).isoformat()
    block_hash = AuditChain.compute_block_hash(
        prev_hash, ts_now, 'READBACK_CONFIRMED', {'vendor_id': vendor_id, 'status': 'CONFIRMED'}
    )
    
    return {
        'vendor_id': vendor_id,
        'application_id': f"SVA-2026-{abs(hash(vendor_id)) % 899999 + 100000}",
        'status': 'SUBMITTED_TO_PORTAL',
        'readback_status': 'CONFIRMED',
        'audit_hash': block_hash,
        'prev_audit_hash': prev_hash,
        'timestamp': ts_now,
        'submission_receipt': {
            'portal': 'PM SVANidhi / Udyam Assist Platform',
            'scheme_code': 'PMA-SVANIDHI-T1',
            'lender_routing': 'State Bank of India (Mylapore Branch)',
            'interest_subsidy': '7% per annum credited quarterly',
            'digital_incentive': '₹1,200 annual cashback on UPI merchant receipts'
        }
    }
