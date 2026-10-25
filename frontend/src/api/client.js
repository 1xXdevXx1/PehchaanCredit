const API_BASE = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_BASE_URL) || 'http://localhost:8000/api';

export async function fetchVendors() {
  const res = await fetch(API_BASE + '/vendors');
  if (!res.ok) throw new Error('Failed to load vendors');
  return res.json();
}

export async function fetchVendorDetails(vendorId) {
  const res = await fetch(API_BASE + '/vendors/' + encodeURIComponent(vendorId));
  if (!res.ok) throw new Error('Failed to load vendor details');
  return res.json();
}

export async function fetchVendorTransactions(vendorId) {
  const res = await fetch(API_BASE + '/vendors/' + encodeURIComponent(vendorId) + '/transactions');
  if (!res.ok) throw new Error('Failed to load transactions');
  return res.json();
}

export async function fetchBehavioralMetrics(vendorId) {
  const res = await fetch(API_BASE + '/vendors/' + encodeURIComponent(vendorId) + '/behavior');
  if (!res.ok) throw new Error('Failed to load behavioral metrics');
  return res.json();
}

export async function fetchFraudAnalysis(vendorId) {
  const res = await fetch(API_BASE + '/vendors/' + encodeURIComponent(vendorId) + '/fraud');
  if (!res.ok) throw new Error('Failed to load fraud analysis');
  return res.json();
}

export async function fetchAssessmentReport(vendorId) {
  const res = await fetch(API_BASE + '/vendors/' + encodeURIComponent(vendorId) + '/assessment');
  if (!res.ok) throw new Error('Failed to load assessment report');
  return res.json();
}

export async function runAssessment(vendorId) {
  const res = await fetch(API_BASE + '/vendors/' + encodeURIComponent(vendorId) + '/assess', {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Failed to trigger assessment');
  return res.json();
}

export async function fetchLoanVoiceIntent(vendorId, languageCode = 'hi', rawText = null) {
  const res = await fetch(API_BASE + '/vendors/' + encodeURIComponent(vendorId) + '/loan-application/voice-intent', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ language_code: languageCode, raw_text: rawText })
  });
  if (!res.ok) throw new Error('Failed to process voice intent');
  return res.json();
}

export async function fetchLoanApplicationPreview(vendorId, lang = 'hi') {
  const res = await fetch(API_BASE + '/vendors/' + encodeURIComponent(vendorId) + '/loan-application/preview?lang=' + encodeURIComponent(lang));
  if (!res.ok) throw new Error('Failed to load application preview');
  return res.json();
}

export async function submitLoanApplication(vendorId, payload) {
  const res = await fetch(API_BASE + '/vendors/' + encodeURIComponent(vendorId) + '/loan-application/submit', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('Failed to submit loan application');
  return res.json();
}

export async function fetchAAConsentStatus(vendorId) {
  const res = await fetch(API_BASE + '/aa/consent/' + encodeURIComponent(vendorId) + '/status');
  if (!res.ok) throw new Error('Failed to fetch AA consent status');
  return res.json();
}

export async function initiateAAConsent(vendorId, fipId = 'SBI-FIP-01') {
  const res = await fetch(API_BASE + '/aa/consent/initiate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ vendor_id: vendorId, fip_id: fipId })
  });
  if (!res.ok) throw new Error('Failed to initiate AA consent');
  return res.json();
}