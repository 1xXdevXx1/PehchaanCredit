# PehchaanCredit Formulas and Behavioral Metrics Reference

## 1. Core Behavioral Indices

### A. SPV — Supplier Payment Velocity (Weight: 15%)
\\text{SPV} = \\frac{\\text{Supplier Outbound Payments}}{\\text{Total Outbound Volume}}
- **Interpretation**: Measures authentic inventory restocking vs personal transfers or fund drainage.

### B. TSCI — Transaction Stability & Consistency Index (Weight: 15%)
\\text{TSCI} = 0.5 \\times \\text{Temporal} + 0.3 \\times \\text{Peak-Hour} + 0.2 \\times \\text{Geo}
- **Components**:
  - **Temporal**: Consistency of operating business days over time.
  - **Peak-Hour**: Concentration of transactions during plausible business operating hours (7:00 AM – 10:00 PM).
  - **Geo**: Variance and consistency of mobile vendor geolocation.

### C. MCS — Merchant Customer Score (Weight: 15%)
\\text{MCS} = \\text{Customer Diversity} + \\text{Healthy Recurrence} - \\text{Reciprocity}
- **Interpretation**: High unique customer base with organic return visits, penalized by circular back-and-forth transfers.

### D. Seasonal Resilience (Weight: 10%)
\\text{Resilience} = \\frac{\\text{Actual Income}}{\\text{Expected Seasonal Income}}
- Evaluated using STL decomposition (Trend + Seasonality + Residual) when history >= 60 days, with robust median-ratio fallback.

---

## 2. Fraud & Synthetic Volume Penalty

### SVPS — Synthetic Volume Penalty Score $\\in [0, 1]$
- Aggregates:
  1. **Rule Engine**: Repeated identical amounts, night transactions (11 PM - 4 AM), sudden volume spikes.
  2. **Isolation Forest**: Aggregate behavioural outlier score.
  3. **NetworkX Graph Cycles**: Directed circular flow loops ( \\to B \\to C \\to A$) and reciprocal flow.

### Adjusted Volume
\\text{Adjusted Volume} = \\text{Raw Volume} \\times (1 - \\text{SVPS})

---

## 3. Final Credit Score & Rating Bands

### Final Quality ({final}$)
Q_{final} = Q_{base} \\times (1 - 0.25 \\times \\text{SVPS})

### Credit Score ( \\le \\text{Score} \\le 900$)
\\text{Credit Score} = 300 + 600 \\times Q_{final}

### Project-Defined Rating Bands (College Prototype)
- **800 – 900**: Excellent
- **750 – 799**: Very Good
- **700 – 749**: Good
- **650 – 699**: Fair
- **600 – 649**: Weak
- **< 600**: Poor

> **Disclaimer**: These are project-defined prototype bands and do not represent official RBI, CIBIL, or bank credit bureau ratings.