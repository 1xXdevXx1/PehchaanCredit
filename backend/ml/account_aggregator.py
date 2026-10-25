import hashlib
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

class AccountAggregatorEngine:
    """
    Simulation of RBI-compliant Account Aggregator (AA) framework.
    Manages consent lifecycle (REQUESTED -> ACTIVE -> REVOKED) and encrypted
    Financial Information (FI) payload ingestion.
    """
    def __init__(self):
        self.consents = {}
        
    def initiate_consent_request(
        self,
        vendor_id: str,
        fip_id: str = 'SBI-FIP-01',
        purpose_code: str = 'CREDIT_ASSESSMENT'
    ) -> Dict[str, Any]:
        consent_id = f"AA-CONSENT-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now(timezone.utc)
        expiry = now + timedelta(days=90)
        
        artifact = {
            'consent_id': consent_id,
            'vendor_id': vendor_id,
            'status': 'ACTIVE', # Set active for seamless demo
            'fiu_id': 'PEHCHAAN_CREDIT_FIU',
            'fip_id': fip_id,
            'purpose': {
                'code': purpose_code,
                'ref_uri': 'https://api.rbi.org.in/aa/purpose/101',
                'description': 'Credit underwriting and cash-flow verification for informal vendor micro-lending'
            },
            'fi_types': ['DEPOSIT', 'TRANSACTION', 'TERM_DEPOSIT'],
            'data_range': {
                'from': (now - timedelta(days=365)).strftime('%Y-%m-%d'),
                'to': now.strftime('%Y-%m-%d')
            },
            'data_life': {'unit': 'MONTH', 'value': 12},
            'frequency': {'unit': 'DAILY', 'value': 1},
            'consent_handle': f"HANDLE-{uuid.uuid4().hex[:12]}",
            'created_at': now.isoformat() + 'Z',
            'expires_at': expiry.isoformat() + 'Z'
        }
        
        self.consents[vendor_id] = artifact
        return artifact

    def get_consent_status(self, vendor_id: str) -> Dict[str, Any]:
        if vendor_id in self.consents:
            return self.consents[vendor_id]
            
        # Default mock active consent for verified platform vendors
        return {
            'consent_id': f"AA-CONSENT-VND-{abs(hash(vendor_id)) % 89999 + 10000}",
            'vendor_id': vendor_id,
            'status': 'ACTIVE',
            'fiu_id': 'PEHCHAAN_CREDIT_FIU',
            'fip_id': 'SBI-FIP-01 (State Bank of India)',
            'fi_types': ['DEPOSIT', 'TRANSACTION'],
            'data_range': {'from': '2025-09-01', 'to': '2026-09-01'},
            'frequency': {'unit': 'DAILY', 'value': 1},
            'consent_handle': f"HANDLE-{vendor_id.lower()}-992",
            'created_at': '2026-08-15T09:00:00Z',
            'expires_at': '2026-11-15T09:00:00Z',
            'verified_bank_name': 'State Bank of India',
            'account_mask': 'XXXXXXXX9021',
            'avg_daily_balance': 18450.0,
            'outward_cheque_bounces': 0,
            'aa_data_verified': True
        }

    def process_fi_webhook(self, consent_handle: str, encrypted_payload: str) -> Dict[str, Any]:
        """
        Simulates end-to-end decryption of DHE-encrypted AA Financial Information payload.
        """
        return {
            'status': 'SUCCESS',
            'consent_handle': consent_handle,
            'decrypted_records': 142,
            'verified_inflow_annual': 1450000.0,
            'bounces_last_180d': 0,
            'verified_timestamp': datetime.now(timezone.utc).isoformat()
        }

# Global singleton instance
aa_engine = AccountAggregatorEngine()

