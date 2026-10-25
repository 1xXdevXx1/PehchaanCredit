# PehchaanCredit: Technical Architecture & Patent Blueprint
### An Alternate Credit Scoring Ecosystem for India's Informal Street Vendors

---

## Executive Summary & Innovation Matrix

| Feature / Domain | Conventional Bureau (CIBIL/Equifax) | Baseline PehchaanCredit | **Upgraded Patent Blueprint** |
| :--- | :--- | :--- | :--- |
| **Data Ingestion** | Bureau trade lines, credit cards, formal debt history | Raw UPI transaction logs | **UPI + Mandi Timestamps + RBI Account Aggregator (AA) + Weather Covariates** |
| **Supplier Discipline** | Not captured | Outbound supplier ratio | **Circular Statistics ($R, CV$) on morning Mandi cycles ($4\text{ AM}-9\text{ AM}$)** |
| **Operating Rhythm** | Not captured | Simple daytime ratio (7 AM - 10 PM) | **Shannon Entropy on 24 hourly bins ($1 - H/H_{max}$) + Haversine geo-dispersion** |
| **Customer Loyalty** | Not captured | Count of repeat customers | **Customer Density Rate (CDR) + Reciprocity Filter ($RR_{ij}$) + Gaussian Recurrence** |
| **Anti-Collusion Engine** | Heuristic blacklists | NetworkX directed cycles & Isolation Forest | **Multi-Attributed Edges ($\text{RAR} > 0.5$) + Time2Vec + T-GAT Temporal Attention** |
| **Seasonality & Risk** | Static score | STL decomposition | **Weather/Monsoon Covariates + Quantile Risk Bands (P10, P50, P90)** |
| **Explainability** | Generic adverse reason codes | Global TreeSHAP feature importances | **Plain-Language Itemized Waterfall Statement ($620 + 38 + 21 + 18 + 14 - 11 = 700$)** |
| **Inclusion / Loan Filing** | English/paper forms with bureau rejection | Underwriter dashboard only | **Multilingual GenAI Voice Agent (Whisper/Gemini) + Read-Back + SHA-256 Audit Chain** |

---

## Section 1: Novel Alternate Metrics & Behavioral Proxies

### 1.1 Mandi Cycle & Circular Statistics for SPV (Supplier Payment Velocity)
A vendor's UPI log reflects their unwritten diary. Genuine street vendors wake up before dawn to purchase fresh inventory at wholesale markets (Mandi).
- **Circular Angle Transformation**:
  $$\theta_i = \left(\frac{\text{hour}_i}{24}\right) \times 2\pi$$
- **Mean Resultant Vector & Circular Variance**:
  $$C = \frac{1}{n} \sum_{i=1}^n \cos(\theta_i), \quad S = \frac{1}{n} \sum_{i=1}^n \sin(\theta_i)$$
  $$R = \sqrt{C^2 + S^2} \in [0, 1], \quad \text{CircularVariance} = 1 - R$$
- **Composite SPV Formula**:
  $$\text{SPV} = \text{SPV}_{base} \times (0.75 + 0.25 \times R_{supp})$$

> 🎓 **Explain to your professor like this:**
> *"Prof, conventional banks reject vendors because they lack supplier invoices. We proved that vendor supplier payments cluster tightly between 4 AM and 9 AM at wholesale mandis. Because time on a 24-hour clock wraps around at midnight, linear standard deviation fails. Using directional circular statistics, we compute the mean resultant vector length $R$. A high $R$ proves disciplined daily wholesale purchases, proving genuine business operations."*

---

### 1.2 TSCI with Circular Variance & Peak-Hour Shannon Entropy
Measures customer-side business rhythm without requiring invasive tracking.
- **Shannon Entropy on 24 Hourly Bins**:
  $$p_h = \frac{\text{count}(h)}{N}, \quad H = -\sum_{p_h > 0} p_h \log_2(p_h)$$
  $$H_{max} = \log_2(24) \approx 4.58496, \quad \text{EntropyConcentration} = 1 - \frac{H}{H_{max}}$$
- **Haversine Geo-Dispersion**:
  Measures geographic stability of the vendor's vending cart or pitch using coordinate standard deviation in kilometers.
- **Composite TSCI**:
  $$\text{TSCI} = 0.35 \times \text{Temporal} + 0.25 \times (1 - CV_{cust}) + 0.25 \times \text{EntropyConcentration} + 0.15 \times \text{GeoConsistency}$$

---

### 1.3 Micro-Customer Recurrence & Reciprocity Filter (MCS)
Distinguishes organic retail sales from collusive peer transfers.
- **Customer Density Rate (CDR)**:
  $$\text{CDR} = \frac{N_{\text{unique counterparties}}}{N_{\text{total customer tx}}}$$
- **Reciprocal Amount Ratio Filter ($\text{RAR}$)**:
  Counterparties appearing in both inbound and outbound transactions with:
  $$RR_{ij} = \frac{\min(\text{in}_{ij}, \text{out}_{ij})}{\max(\text{in}_{ij}, \text{out}_{ij})} > 0.30$$
  are flagged and excluded from genuine customer counts.
- **Gaussian Bell-Shaped Recurrence**:
  An optimal neighborhood business has 25%–35% repeat buyers:
  $$f(\text{Recurrence}) = \exp\left(-\frac{(\text{Rate} - 0.30)^2}{2 \times (0.20)^2}\right)$$

---

## Section 2: Anti-Collusion & Circular Fraud Engine

### 2.1 Multi-Attributed Directed Graph
Edges $E(u, v)$ contain:
- `frequency`: count of transactions
- `mean_amount` and `amount_variance`
- `time_velocity`: mean inter-arrival delta in hours
- `reciprocal_amount_ratio`: $\text{RAR}_{uv} = \min(A_{uv}, A_{vu}) / \max(A_{uv}, A_{vu})$

### 2.2 Collusion Cycle Detection ($\text{RAR} > 0.50$)
Detects artificial wash trading rings ($A \to B \to C \to A$) by isolating edges with $\text{RAR} > 0.50$ and searching for directed simple cycles of length 2 to 5.

### 2.3 Time2Vec + Temporal Graph Attention Network (T-GAT)
Computes harmonic time embeddings:
$$\text{t2v}(t)[0] = \omega_0 t + \phi_0 \quad (\text{linear trend})$$
$$\text{t2v}(t)[i] = \sin(\omega_i t + \phi_i) \quad (\text{periodic harmonics for } i=1..d-1)$$
Multi-head attention over temporal interactions generates robust node embeddings that detect subtle velocity manipulation.

---

## Section 3: Seasonality & Dynamic Scoring Engine

### 3.1 Regional Weather & Festival Covariates
Street vendors suffer revenue drops during monsoon downpours and surge during regional festivals (Diwali, Pongal, Eid). Rather than penalizing a vendor for bad weather:
- Compare vendor revenue against the regional cluster cohort during monsoon months (Oct–Dec in Tamil Nadu).
- Expected resilience: $\text{Resilience}_{adjusted} = 0.70 \times \text{Resilience}_{STL} + 0.30 \times \min(1.1, \text{MonsoonResilience})$.

### 3.2 Quantile Risk Bands (P10, P50, P90)
Instead of a single brittle number, underwriters receive probabilistic credit quality:
- **P10 (Worst-Case / Adverse Conditions)**: Floor score during severe monsoon or economic stress.
- **P50 (Median Baseline)**: Standard operating cashflow score.
- **P90 (Optimistic / Peak Festival)**: Upper bound capacity during high festive trade.

### 3.3 Plain-Language SHAP Waterfall Attribution
Every credit score is accompanied by an itemized credit statement:
$$\text{Base Score } 620 + \Delta\text{SPV } (+38) + \Delta\text{TSCI } (+21) + \Delta\text{Resilience } (+18) + \Delta\text{MCS } (+14) - \Delta\text{SVPS } (-11) = 700$$

---

## Section 4: Multilingual Agentic Form-Filling Engine (GenAI)

### 4.1 Speech-to-Intent Pipeline
Supports voice interaction in Hindi, Tamil, Telugu, Marathi, and Indian English. Converts spoken prompts into validated PM SVANidhi schema fields (`loan_amount_requested`, `repayment_tenure_months`, `operating_pincode`, `vpa_upi`).

### 4.2 Zero-Hallucination Guardrails
1. **RAG Grounding**: Every field is bound to a verified provenance source (`KYC_DATABASE`, `TRANSACTION_LEDGER`, `MUNICIPAL_CORP_REGISTRY`) with confidence scores $\ge 92\%$.
2. **Read-Back Verification**: The agent speaks the application summary aloud in the vendor's native dialect before submission.
3. **Immutable Audit Chain**: Each action is permanently anchored using SHA-256 block hashing:
   $$\text{Block Hash} = \text{SHA-256}(\text{prev\_hash} \parallel \text{timestamp} \parallel \text{action} \parallel \text{payload})$$

---

## Section 5: RBI Account Aggregator (AA) System Flow

1. **Consent Artifact Generation**: Implements the RBI Account Aggregator technical specification with `ACTIVE` status, 365-day validity, and daily recurrent fetch.
2. **Financial Information (FI) Decryption**: Ingests primary savings account data from SBI/HDFC FIPs, verifying average daily balance (₹18,450) and zero 180-day cheque bounces to cross-validate UPI ledger cashflows.

---

## Section 6: Patent Claims Drafting (Indian Patents Act §3(k))

### Technical Effect & Physical Transformation
Under Section 3(k) of the Indian Patents Act, software algorithms are patentable if they produce a technical effect and solve a specific technical problem via technical data transformations.

- **Claim 1 (Independent Method Claim)**:
  *A computer-implemented method for technical alternate credit assessment of informal merchant nodes comprising:*
  1. Transforming asynchronous electronic transaction timestamps into circular angle coordinates $\theta_i = (\text{hour}_i / 24) \times 2\pi$;
  2. Computing the mean resultant vector length $R = \sqrt{C^2 + S^2}$ to derive supplier payment velocity;
  3. Generating a multi-attributed directed transaction graph with reciprocal amount ratio $\text{RAR}_{uv} = \min(A_{uv}, A_{vu}) / \max(A_{uv}, A_{vu})$;
  4. Executing cycle search restricted to graph edges with $\text{RAR} > 0.50$ to compute synthetic volume penalty score (SVPS);
  5. Generating quantile risk intervals (P10, P50, P90) modulated by regional meteorological covariates.

- **Claim 2 (Dependent Claim - T-GAT Time2Vec)**:
  *The method of Claim 1, wherein temporal interaction anomaly detection comprises computing periodic harmonic projections $\text{t2v}(t)[i] = \sin(\omega_i t + \phi_i)$ and feeding multi-head temporal attention layers.*

- **Claim 3 (Dependent Claim - Zero-Hallucination Audit Chain)**:
  *The method of Claim 1, further comprising capturing multilingual speech-to-intent tokens, grounding extracted fields against municipal registry records, speaking a read-back verification script, and committing the confirmed transaction to an immutable SHA-256 hash-chained audit block.*
