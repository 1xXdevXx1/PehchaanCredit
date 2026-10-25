from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Boolean, Text
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Vendor(Base):
    __tablename__ = 'vendors'
    vendor_id = Column(String, primary_key=True)
    vendor_name = Column(String, nullable=False)
    business_type = Column(String, nullable=False)
    city = Column(String, nullable=False)
    vendor_age = Column(Integer)
    business_age_months = Column(Integer)
    archetype = Column(String)

class Transaction(Base):
    __tablename__ = 'transactions'
    transaction_id = Column(String, primary_key=True)
    timestamp = Column(String, nullable=False)
    vendor_id = Column(String, nullable=False, index=True)
    counterparty_id = Column(String, nullable=False)
    transaction_type = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    payment_channel = Column(String, nullable=False)
    business_type = Column(String)
    city = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)

class Assessment(Base):
    __tablename__ = 'assessments'
    vendor_id = Column(String, primary_key=True)
    credit_score = Column(Integer)
    rating = Column(String)
    behavioral_trust = Column(Integer)
    q_base = Column(Float)
    q_final = Column(Float)
    svps = Column(Float)
    fraud_risk = Column(Float)
    decision = Column(String)
    action = Column(String)
    spv = Column(Float)
    tsci = Column(Float)
    mcs = Column(Float)
    resilience = Column(Float)
    fsi = Column(Float)
    tci = Column(Float)
    bgi = Column(Float)
    fri = Column(Float)
    explanation_json = Column(Text)
    created_at = Column(String)

class LoanApplicationRecord(Base):
    __tablename__ = 'loan_applications'
    application_id = Column(String, primary_key=True)
    vendor_id = Column(String, nullable=False, index=True)
    language = Column(String, default='hi')
    transcription = Column(Text)
    loan_amount = Column(Float, nullable=False)
    tenure_months = Column(Integer, nullable=False)
    status = Column(String, default='SUBMITTED')
    readback_confirmed = Column(Boolean, default=True)
    audit_hash = Column(String)
    provenance_json = Column(Text)
    created_at = Column(String)

class AAConsentRecord(Base):
    __tablename__ = 'aa_consents'
    consent_id = Column(String, primary_key=True)
    vendor_id = Column(String, nullable=False, index=True)
    status = Column(String, default='ACTIVE')
    fiu_id = Column(String, default='PEHCHAAN_CREDIT_FIU')
    fip_id = Column(String)
    consent_handle = Column(String)
    created_at = Column(String)
    expires_at = Column(String)

