# Executive Summary



<!-- AUTO:TOP_RISKS_START -->
# Top risks (by residual) — 2025-12-18

| Rank | Risk | Title | Category | Inherent | Residual | Treatment | Status | Target | Owner |
|---:|---|---|---|---:|---:|---|---|---|---|
| 1 | R01 | Account takeover via phishing | IAM / Phishing | 16 (Critical) | 12 (High) | Reduce | Open | 2026-03-31 | IT |
| 2 | R10 | Insufficient logging & detection | Detection / Logging | 16 (Critical) | 12 (High) | Reduce | Open | 2026-06-30 | IT |
| 3 | R03 | Ransomware via remote access | Ransomware / Remote Access | 15 (Critical) | 10 (High) | Reduce | Open | 2026-04-30 | IT |
| 4 | R05 | Privileged account misuse | IAM / Privileged Access | 15 (Critical) | 10 (High) | Reduce | Open | 2026-05-31 | IT |
| 5 | R25 | Flat network enables lateral movement | Network Security | 15 (Critical) | 10 (High) | Reduce | Open | 2026-10-31 | IT |
<!-- AUTO:TOP_RISKS_END -->



<!-- AUTO:KPIS_START -->
## KPI snapshot
- Total risks: **30**
- Residual levels: `{'High': 5, 'Medium': 24, 'Low': 1}`
- Inherent levels: `{'Critical': 7, 'High': 18, 'Medium': 5}`
- Treatments: `{'reduce': 30}`
- Statuses: `{'Open': 30}`
<!-- AUTO:KPIS_END -->






## Top 10 Actions (next 90 days)

1) Enforce MFA for all + conditional access (R01/R03)

2) Disable legacy authentication + harden email (R01/R02)

3) Immutable/offline backups + monthly restore tests (R04)

4) Patch baseline for endpoints + remove local admin where possible (R07)

5) Centralize logs (at least identity/email/VPN) + basic alerting (R10)

6) Privileged access hygiene (unique admin accounts, audit logs) (R05)

7) Remote access hardening (VPN patching, MFA, restrictions) (R03)

8) Laptop security baseline (BitLocker + MDM + remote wipe) (R08)

9) Vendor security questionnaire + contract clauses (R09)

10) Incident response plan + tabletop exercise (R11)



## Roadmap (delivery)

- Critical (0â€“90 days): A01, A02, A03, A04, A05, A09, A10

- Next (3â€“6 months): A06, A07, A08, A12

- Longer term (6â€“12 months): A11



## KPIs (to track)

- MFA coverage (%), legacy auth sign-ins (count)

- Patch compliance (% within SLA)

- Backup restore test success rate (%)

- Log coverage (% critical sources ingested) + MTTD trend

- Tabletop exercises completed (count)

- Vendors assessed (%), vendor access reviews completed (count)



