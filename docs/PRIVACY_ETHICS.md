# DRISHTI Privacy & Ethics Framework

## Foundational Principle

**DRISHTI is a humanitarian alert system, NOT a surveillance system.**

Its sole purpose is the recovery of missing persons and trafficking victims.
Every architectural decision reflects this mandate.

---

## Legal Compliance

### Digital Personal Data Protection Act 2023 (DPDP Act)

DRISHTI is designed for compliance with India's DPDP Act 2023:

| Requirement | DRISHTI Implementation |
|-------------|----------------------|
| Purpose Limitation | Data processed only for missing person recovery |
| Data Minimization | Only essential biometrics collected |
| Consent | Families provide explicit consent at case registration |
| Data Principal Rights | Deletion within 30 days of case closure |
| Cross-Border Transfer | Data stays within India; no foreign processing |
| Breach Notification | Audit system triggers alerts for unauthorized access |
| Data Fiduciary | Designated Data Protection Officer required |

### Other Applicable Laws

- **POCSO Act 2012** — Additional protections for child victim data
- **IT Act 2000, Section 43A** — Reasonable security practices
- **Evidence Act** — Chain of custody for biometric evidence

---

## Six Core Privacy Safeguards

### 1. Consent-First Database
- Only processes faces of **registered** missing persons
- Family must provide explicit written consent at FIR filing
- No facial recognition run on general public
- Faces removed from active search **30 days after** person is found

### 2. No Live Tracking
- System does NOT continuously monitor or track anyone
- Face matching activates **only** when a registered case query is submitted
- No "always-on" population scanning
- No behavioral profiling beyond missing person cases

### 3. Human-in-the-Loop (HITL)
- AI flags potential matches; **officer decides** on every action
- No automated detention, interception, or arrest
- Every alert requires officer verification before action
- Minimum 2-officer verification for high-impact interventions

### 4. Complete Audit Trail
- Every search logged: `officer_id`, `timestamp`, `query_type`, `result_count`
- Every alert logged: `created_by`, `acknowledged_by`, `action_taken`
- Audit logs retained for **1 year** minimum, read-only
- Independent quarterly audit by designated oversight body
- Tamper-evident audit chain (append-only with cryptographic integrity)

### 5. Decentralized Architecture
- State police units see **only their state's data**
- No single national surveillance database
- Federated matching planned: face embeddings never leave source state
- Inter-state queries require formal protocol and dual authorization

### 6. Data Security
- All data encrypted at rest (AES-256)
- All data encrypted in transit (TLS 1.3)
- Biometric embeddings stored as irreversible hashes
- Evidence photos stored in isolated S3 buckets with access logging
- Regular penetration testing required before production deployment

---

## Prohibited Uses

The following uses of DRISHTI are **explicitly prohibited**:

- ❌ Tracking political activists, journalists, or protestors
- ❌ Monitoring individuals not registered as missing persons
- ❌ Building general-population biometric databases
- ❌ Real-time mass surveillance of public spaces
- ❌ Sharing data with foreign intelligence agencies
- ❌ Using data for purposes other than missing person recovery
- ❌ Automated arrest, detention, or flagging at checkpoints without human verification

Violations of these prohibitions should be reported to:
- National Human Rights Commission (NHRC)
- State Women's Commission
- Designated Data Protection Officer

---

## Ethical Review Process

Before production deployment, DRISHTI must undergo:

1. **Technical security audit** — Independent pen-testing firm
2. **Privacy impact assessment** — Per DPDP Act requirements
3. **Ethics review** — Civil society, legal experts, affected communities
4. **Pilot program** — Limited deployment with full audit before scale
5. **Annual review** — Outcomes, bias testing, community feedback

---

## Bias and Accuracy Standards

### Required Testing Before Deployment

| Demographic Group | Minimum Accuracy |
|------------------|-----------------|
| Adult faces (clear) | ≥ 99% (ArcFace standard) |
| Child faces | ≥ 95% |
| Occluded/masked faces | ≥ 70% |
| Low-quality CCTV | ≥ 60% |
| Across skin tones | < 5% accuracy variance |
| Across genders | < 3% accuracy variance |

Deployment is blocked if any group falls below minimum accuracy standards.

### Ongoing Monitoring

- Monthly bias reports by skin tone, age, gender
- False positive rate tracked and reported publicly
- Community feedback channel for misidentification reports

---

## Transparency Report

DRISHTI operators must publish **annual transparency reports** including:

- Total cases registered
- Total searches conducted
- Successful recoveries attributed to the system
- False positive incidents and outcomes
- Data breaches (if any)
- Audit findings

Reports should be available at: `drishti.gov.in/transparency`

---

## Contact & Reporting

**Data Protection Officer:** [dpo@drishti.gov.in]
**Ethics Concerns:** [ethics@drishti.gov.in]
**Security Vulnerabilities:** [security@drishti.gov.in]
**Misidentification Reports:** [appeals@drishti.gov.in]
