# CareGraph AI
## AI-Powered Family Health & Preventive Care Management Platform

**Product Requirements Document (PRD)**  
**Version:** 1.0  
**Date:** August 24, 2026  
**Status:** Product Definition

---

# 1. Executive Summary

CareGraph AI is an integrated personal and family health management platform designed to create a continuous, intelligent health record for individuals and families.

The platform allows users to:

- Store and manage family health history.
- Maintain personal health profiles.
- Upload and analyze medical reports.
- Track health metrics over time.
- Identify meaningful health trends and risk factors.
- Receive personalized preventive-care guidance.
- Identify appropriate healthcare specialties to discuss with a doctor.
- Receive reminders for health monitoring and follow-ups.
- Generate personalized exercise, lifestyle and nutrition plans.
- Maintain emergency contacts and healthcare-provider information.
- Discover nearby hospitals and healthcare facilities.
- Maintain a centralized family doctor/care-team profile.
- Continuously update recommendations as new health information is added.

The platform is **not intended to replace doctors or provide autonomous medical diagnosis**. AI-generated insights are intended to support health awareness, organization, preventive care and conversations with qualified healthcare professionals.

---

# 2. Product Vision

## Vision

> **Create a lifelong intelligent health companion that connects family history, personal health data, medical reports, lifestyle and healthcare resources into one continuously evolving health profile.**

Instead of treating every medical report, doctor visit and lifestyle decision as an isolated event, CareGraph AI creates a connected health timeline.

### Core concept

**Family History → Personal Health → Medical Reports → Trends → Risk Signals → Preventive Guidance → Lifestyle → Follow-up → New Health Data**

---

# 3. Problem Statement

Healthcare information is often fragmented across:

- Paper medical reports.
- PDF reports.
- Different hospitals.
- Different doctors.
- Personal notes.
- Family members.
- Fitness applications.
- Messaging applications.
- Phone contacts.

Users frequently do not have a complete understanding of their family's medical history or their own long-term health trends.

A person may possess:

- A blood report from 2024.
- Another report from 2025.
- A prescription from a different doctor.
- Family history of a chronic condition.
- Lifestyle changes.
- Multiple healthcare contacts.

But these pieces of information are rarely connected.

## Problem

There is no single intelligent system that combines:

**family history + personal health + medical reports + lifestyle + longitudinal trends + healthcare resources**

into one understandable health-management experience.

---

# 4. Product Goals

## Primary Goals

1. Create a centralized family and personal health profile.
2. Digitize medical reports using AI.
3. Analyze uploaded reports and extract relevant health information.
4. Track health metrics over time.
5. Identify meaningful changes and trends.
6. Use family history as contextual information for preventive-care guidance.
7. Provide explainable recommendations for discussing appropriate healthcare with professionals.
8. Provide personalized lifestyle, exercise and nutrition guidance.
9. Maintain emergency contacts and healthcare-provider information.
10. Help users locate nearby hospitals and healthcare facilities.
11. Build a continuously updating health timeline.
12. Provide reminders for follow-up and preventive-health activities.

---

# 5. Non-Goals

The initial product will NOT:

- Diagnose diseases autonomously.
- Replace doctors.
- Prescribe medicines.
- Change medication dosages.
- Recommend prescription medication without qualified clinical oversight.
- Guarantee disease prediction.
- Make emergency decisions without appropriate safeguards.
- Automatically share medical data without user consent.
- Automatically contact people without user authorization.

---

# 6. Target Users

## Primary User

Individuals aged 18+ who want to organize and monitor their personal and family health information.

## Secondary Users

### Families

Parents, children and siblings who want to maintain a shared family health history.

### Health-conscious users

Users interested in:

- Fitness.
- Nutrition.
- Preventive health.
- Lifestyle improvement.

### Chronic-condition monitoring users

Users who need to track health measurements over time under professional guidance.

### Caregivers

Individuals helping manage health information for parents or other family members.

---

# 7. Core User Journey

```text
Create Account
      ↓
Create Personal Profile
      ↓
Add Family Members
      ↓
Add Family Health History
      ↓
Add Existing Medical Information
      ↓
Upload Medical Reports
      ↓
AI Extracts Information
      ↓
Health Data Structured
      ↓
Historical Data Compared
      ↓
Health Trends Generated
      ↓
Risk Factors Identified
      ↓
Preventive-Care Guidance
      ↓
Lifestyle Recommendations
      ↓
Doctor / Healthcare Guidance
      ↓
Reminders
      ↓
User Adds New Health Data
      ↓
System Re-analyzes Health Profile
```

This loop forms the core of the product.

---

# 8. Functional Requirements

# 8.1 Authentication & Account Management

Users shall be able to:

- Register an account.
- Login securely.
- Logout.
- Reset password.
- Manage profile.
- Configure privacy settings.
- Manage consent.
- Delete account.
- Export personal health information.

### Optional future authentication

- Google/Apple login.
- Passkeys.
- Multi-factor authentication.

---

# 8.2 Personal Health Profile

The system shall allow users to maintain:

### Personal information

- Name.
- Date of birth.
- Sex.
- Height.
- Weight.
- Blood group.
- Allergies.
- Existing medical conditions.
- Medications.
- Lifestyle information.

### Health metrics

- Weight.
- Blood pressure.
- Heart rate.
- Blood glucose.
- HbA1c.
- Cholesterol.
- Sleep duration.
- Physical activity.

The system should allow additional metrics to be added over time.

---

# 8.3 Family Health History

Users shall be able to create a family health tree.

### Supported relationships

- Father.
- Mother.
- Brother.
- Sister.
- Son.
- Daughter.
- Grandfather.
- Grandmother.
- Uncle.
- Aunt.
- Other.

### Family medical information

For each family member:

- Relationship.
- Age.
- Relevant health conditions.
- Approximate age of diagnosis where known.
- Major surgeries.
- Cancer history.
- Genetic conditions.
- Relevant health events.

### Family Health Tree

Example:

```text
                Grandfather
                    │
           ┌────────┴────────┐
           │                 │
         Father            Uncle
           │
     ┌─────┴─────┐
    User       Sibling
```

The family history should be connected to the user's health profile and used as contextual information by the recommendation engine.

---

# 8.4 Medical Report Upload

Users shall be able to upload:

- PDF.
- JPG.
- PNG.
- Supported medical documents.

Examples:

- CBC.
- Blood glucose.
- HbA1c.
- Lipid profile.
- Thyroid report.
- Liver function test.
- Kidney function test.
- ECG report.
- Imaging reports.
- Prescriptions.
- Doctor notes.

---

# 8.5 Medical Document Processing

Pipeline:

```text
Upload
   ↓
File Validation
   ↓
OCR / Document Parsing
   ↓
Text Extraction
   ↓
Medical Entity Extraction
   ↓
Value Normalization
   ↓
Reference Range Extraction
   ↓
Structured Health Data
   ↓
AI Explanation
```

The system should extract:

- Test name.
- Result.
- Unit.
- Reference range.
- Report date.
- Laboratory name.
- Relevant observations.

---

# 8.6 Medical Report Analysis

The system shall provide an understandable summary.

Example:

```text
REPORT SUMMARY

Report date: 20 August 2026

HbA1c
Result: 6.0%
Trend: Increasing

Interpretation:
The reported value should be interpreted
using the laboratory reference range and
clinical context.

Suggested action:
Discuss the result and trend with a
qualified healthcare professional.
```

The system should avoid presenting AI output as a confirmed diagnosis.

---

# 8.7 Longitudinal Health Analysis

The system shall compare current information against historical information.

Example:

```text
HbA1c Trend

2024 ── 5.4
2025 ── 5.7
2026 ── 6.0
```

The system should detect:

- Increasing trends.
- Decreasing trends.
- Stable measurements.
- Sudden changes.
- Repeated abnormal values.
- Missing data.
- Potential follow-up requirements.

---

# 8.8 Health Timeline

Every major health event shall be added to a timeline.

Example:

```text
2026
│
├── Jan
│   └── Weight recorded
│
├── Mar
│   └── Blood pressure recorded
│
├── Jun
│   └── Medical consultation
│
├── Aug
│   └── Blood report uploaded
│
└── Sep
    └── Follow-up reminder
```

Users should be able to filter the timeline by:

- Reports.
- Tests.
- Doctors.
- Conditions.
- Medications.
- Lifestyle.
- Family events.

---

# 8.9 Health Risk & Preventive-Care Engine

The system shall combine:

```text
Family History
+
Age
+
Personal Health
+
Medical Reports
+
Health Trends
+
Lifestyle
+
Existing Conditions
```

to identify relevant health-risk signals.

The engine should use:

1. Evidence-based clinical rules.
2. Validated health guidelines.
3. Machine-learning models where appropriate.
4. User-specific contextual data.

The output should be framed as **risk signals and preventive-care guidance**, not diagnosis.

Example:

```text
Risk Area: Cardiovascular Health

Factors:
• Family history
• Previous blood-pressure readings
• Activity level
• Recent measurements

Suggested action:
Discuss your cardiovascular risk profile
with a healthcare professional.
```

---

# 8.10 Doctor Recommendation Engine

The system shall recommend a **type of healthcare professional to consider**, based on available information.

Examples:

```text
General health concern
→ Primary-care physician / General Physician

Heart-related concern
→ Cardiologist discussion

Skin-related concern
→ Dermatologist discussion

Endocrine-related concern
→ Endocrinologist discussion
```

The recommendation should explain **why the specialty may be relevant**.

The system should not claim that a particular specialist is medically required unless supported by appropriate clinical logic.

---

# 8.11 Test / Screening Guidance

The system shall provide preventive-care guidance based on:

- Age.
- Sex.
- Family history.
- Existing conditions.
- Previous results.
- Relevant clinical guidelines.

Example:

```text
Potential preventive-care topic

Reason:
Family history + age + previous measurements

Action:
Discuss appropriate screening with
your healthcare professional.

Recommended review:
According to applicable clinical guidance
and your doctor's advice.
```

The system must not generate arbitrary test intervals using an LLM alone.

---

# 8.12 Health Reminder System

Users can receive reminders for:

- Follow-up consultations.
- Health measurements.
- Report uploads.
- Preventive screening discussions.
- Medication reminders, where explicitly configured.
- Exercise.
- Sleep.
- Lifestyle goals.

Users shall be able to:

- Snooze.
- Complete.
- Reschedule.
- Disable reminders.

---

# 8.13 Exercise Recommendation Engine

The system shall generate personalized activity goals based on:

- User goals.
- Current activity.
- Age.
- Lifestyle.
- Available equipment.
- User preferences.
- Relevant health information.

Example:

```text
WEEK 1

Walking
20 minutes × 5 days

Mobility
10 minutes × 3 days

Goal:
Build consistent activity.
```

The system should include appropriate safety warnings and recommend professional guidance when medical conditions may affect exercise.

---

# 8.14 Diet & Nutrition Engine

Inputs:

- Age.
- Weight.
- Height.
- Activity level.
- Food preferences.
- Dietary restrictions.
- Allergies.
- Goals.
- Relevant health information.

Outputs:

- Meal suggestions.
- Meal timing.
- Food alternatives.
- Portion guidance.
- Weekly plans.
- Nutrition education.

The system should avoid treating AI-generated nutrition plans as medical treatment.

---

# 8.15 Lifestyle Improvement Engine

The platform shall track:

- Exercise.
- Sleep.
- Diet.
- Hydration.
- Weight.
- Screen time, where available.
- Stress/self-reported wellbeing.

The system should generate weekly insights.

Example:

```text
WEEKLY HEALTH INSIGHT

Exercise:
↑ 18% compared with last week

Sleep:
Stable

Weight:
Stable

Recommendation:
Maintain current activity consistency.
```

---

# 8.16 Emergency Contact Management

Users can manually add:

### Family

- Parents.
- Siblings.
- Spouse.
- Children.

### Friends

- Trusted friends.

### Neighbours

- Trusted nearby contacts.

### Healthcare

- Family doctor.
- Specialists.
- Preferred hospital.

Each contact can include:

- Name.
- Relationship.
- Phone number.
- Notes.
- Emergency priority.

---

# 8.17 Contact Extraction

The system may offer contact import from the device's contact system **only after explicit user permission**.

Example:

```text
Import Emergency Contacts

☑ Father
☑ Mother
☐ Friend
☐ Neighbour

[Confirm Import]
```

The system must never silently access or share contacts.

---

# 8.18 Healthcare Provider Management

Users can maintain:

```text
MY CARE TEAM

Family Doctor
├── Name
├── Phone
├── Clinic
└── Notes

Specialist
├── Name
├── Specialty
├── Phone
└── Notes

Preferred Hospital
├── Name
├── Address
├── Phone
└── Emergency information
```

---

# 8.19 Nearby Healthcare Discovery

Using location permission, the system can show:

- Nearby hospitals.
- Clinics.
- Diagnostic laboratories.
- Pharmacies.
- Emergency healthcare facilities.

Information may include:

- Distance.
- Address.
- Phone.
- Opening hours.
- Available services.

Location access must require user permission.

---

# 8.20 Emergency Mode

A dedicated emergency interface shall provide rapid access to:

```text
🚨 EMERGENCY

[Call Emergency Services]

[Call Family Doctor]

[Call Emergency Contact]

[Find Nearby Hospital]

MY EMERGENCY INFORMATION

Blood Group
Allergies
Current Medications
Important Conditions
Emergency Contacts
```

The emergency feature should prioritize speed and simplicity.

---

# 9. AI Architecture

## AI Layer

### Model 1 — Document Intelligence

Responsible for:

- OCR.
- Medical text extraction.
- Report structuring.

### Model 2 — Health Trend Engine

Responsible for:

- Time-series analysis.
- Trend detection.
- Anomaly identification.

### Model 3 — Recommendation Engine

Responsible for:

- Personalization.
- Doctor specialty suggestions.
- Preventive-care guidance.

### Model 4 — Lifestyle AI

Responsible for:

- Exercise suggestions.
- Nutrition suggestions.
- Lifestyle coaching.

### Model 5 — Health Explanation Assistant

Responsible for converting complex medical information into understandable language.

---

# 10. Hybrid AI Architecture

The product should NOT rely entirely on an LLM.

```text
                 HEALTH DATA
                      │
          ┌───────────┼───────────┐
          ↓           ↓           ↓
       Rules         ML          LLM
          │           │           │
          └───────────┼───────────┘
                      ↓
              Recommendation
                  Engine
                      ↓
              Safety Layer
                      ↓
              User Response
```

### Rules

Used for:

- Clinical thresholds.
- Guideline logic.
- Safety constraints.
- Reminder schedules.

### Machine Learning

Used for:

- Trend analysis.
- Risk scoring.
- Personalization.
- Recommendation ranking.

### LLM

Used for:

- Explanation.
- Natural-language interaction.
- Report summarization.
- Lifestyle-plan generation.

---

# 11. System Architecture

```text
                    WEB / MOBILE APP
                           │
                           ▼
                    API GATEWAY
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
       User Service   Health Service   Document Service
            │              │              │
            └──────────────┼──────────────┘
                           ▼
                    HEALTH DATA LAYER
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
          PostgreSQL   Object Storage  Vector DB
              │            │            │
              └────────────┼────────────┘
                           ▼
                     AI ENGINE
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
    OCR/NLP           ML/Analytics       LLM Layer
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
                  CLINICAL RULE ENGINE
                           │
                           ▼
                  SAFETY / VALIDATION
                           │
                           ▼
                  RECOMMENDATION API
                           │
                           ▼
                     USER INTERFACE
```

---

# 12. Suggested Technology Stack

## Frontend

- React.js / Next.js.
- Tailwind CSS.
- Recharts or equivalent charting library.

## Mobile

Future:

- React Native.

## Backend

- Python.
- FastAPI.
- REST API.

## Database

- PostgreSQL.

## File Storage

- S3-compatible object storage.

## AI/ML

- Python.
- scikit-learn.
- PyTorch.
- Transformers.
- LLM API.
- OCR/document AI.

## Authentication

- JWT/session-based authentication.
- OAuth as optional future feature.

## Infrastructure

- Docker.
- CI/CD.
- Cloud deployment.

---

# 13. Database Architecture

Core entities:

```text
User
 │
 ├── PersonalProfile
 │
 ├── FamilyMembers
 │     └── FamilyConditions
 │
 ├── MedicalReports
 │     └── LabResults
 │
 ├── MedicalConditions
 │
 ├── Medications
 │
 ├── HealthMetrics
 │
 ├── LifestyleLogs
 │     ├── Exercise
 │     ├── Diet
 │     └── Sleep
 │
 ├── Doctors
 │
 ├── Hospitals
 │
 ├── EmergencyContacts
 │
 ├── Recommendations
 │
 ├── Reminders
 │
 └── ConsentRecords
```

---

# 14. Security & Privacy Requirements

Health information is highly sensitive.

The platform shall implement:

- Encryption in transit.
- Encryption at rest.
- Strong authentication.
- Role-based access control.
- Secure document storage.
- Audit logging.
- Consent management.
- Data deletion.
- Data export.
- Minimal data collection.
- Access logging.

Users must explicitly control:

- Who can access their data.
- Whether contacts can be imported.
- Whether location can be used.
- Whether reports can be shared.
- Whether family members can view shared information.

The production implementation must comply with applicable healthcare-data and privacy requirements in its target jurisdiction.

---

# 15. AI Safety Requirements

The AI system must:

- Clearly distinguish information from diagnosis.
- Show uncertainty where appropriate.
- Avoid unsupported medical claims.
- Avoid prescribing medication.
- Avoid changing medication dosage.
- Encourage professional evaluation for concerning findings.
- Use validated clinical sources for medical decision logic.
- Log important AI-generated recommendations.
- Allow users to inspect source information where feasible.
- Prevent prompt injection from uploaded documents from overriding system safety rules.

---

# 16. Recommendation Explainability

Every major recommendation should have a reason.

Instead of:

> "See a cardiologist."

The system should say:

> "Your profile contains several cardiovascular-related factors. Consider discussing your overall cardiovascular risk with a qualified healthcare professional. A primary-care physician can help determine whether specialist evaluation is appropriate."

The system should display:

```text
WHY AM I SEEING THIS?

✓ Family history
✓ Recent health measurements
✓ Historical trend
✓ Lifestyle information

Data considered:
2025–2026 health records
```

---

# 17. Notifications

Notification categories:

### Health

- Measurement reminder.
- Report follow-up.
- Health trend update.

### Lifestyle

- Exercise.
- Hydration.
- Sleep.
- Diet.

### Healthcare

- Appointment reminder.
- Preventive-care review.

### Emergency

- Emergency information access.

Users must control notification preferences.

---

# 18. Dashboard Requirements

The home dashboard should display:

```text
MY HEALTH

Health Overview
│
├── Recent Health Metrics
├── Recent Reports
├── Important Trends
├── Upcoming Reminders
├── Lifestyle Progress
├── Family Health Signals
└── Care Team
```

Primary actions:

```text
[Upload Report]

[Add Health Data]

[View Family History]

[View Health Timeline]

[My Doctors]

[Emergency]
```

---

# 19. Example End-to-End Scenario

## Scenario

A user uploads a new blood report.

### Step 1

User uploads PDF.

### Step 2

OCR extracts:

```text
HbA1c = 6.0%
```

### Step 3

System stores the result.

### Step 4

System retrieves historical values:

```text
2024 → 5.4
2025 → 5.7
2026 → 6.0
```

### Step 5

Trend engine identifies an increasing pattern.

### Step 6

Family-history engine finds relevant family history.

### Step 7

Lifestyle engine evaluates activity and diet information.

### Step 8

Recommendation engine combines the information.

### Step 9

The system generates:

```text
HEALTH INSIGHT

Your recent measurement has increased
compared with previous records.

Because your profile also contains relevant
family-history information, consider
discussing the trend with your healthcare
professional.

The system does not diagnose a condition.
```

### Step 10

User receives a follow-up reminder.

### Step 11

The event becomes part of the health timeline.

This demonstrates the core integrated nature of the platform.

---

# 20. MVP Scope

The first working version should contain:

### Must Have

- User authentication.
- Personal profile.
- Family health history.
- Medical report upload.
- OCR/document extraction.
- AI report explanation.
- Health timeline.
- Basic health trend analysis.
- Basic preventive-care guidance.
- Doctor specialty recommendation.
- Basic lifestyle recommendations.
- Emergency contacts.
- Nearby hospital discovery.

### Should Have

- Health reminders.
- Exercise tracking.
- Diet tracking.
- Sleep tracking.
- Family health dashboard.

### Future

- Wearable integration.
- Voice assistant.
- Advanced predictive models.
- Telemedicine.
- Doctor portal.
- Family collaboration.
- Health insurance integration.
- Hospital/diagnostic integrations.

---

# 21. MVP Success Metrics

### User metrics

- Profile completion rate.
- Family-history completion rate.
- Number of reports uploaded.
- Weekly active users.
- Health tracking frequency.

### AI metrics

- Document extraction accuracy.
- Medical entity extraction accuracy.
- Trend detection accuracy.
- Recommendation relevance.
- User feedback on explanations.

### Product metrics

- Report analysis completion rate.
- Reminder completion rate.
- Lifestyle-plan adherence.
- Repeat usage.

### Safety metrics

- Unsupported medical recommendation rate.
- False-positive rate.
- Escalation accuracy.
- AI safety incident rate.

---

# 22. Development Roadmap

## Phase 1 — Foundation

**Duration: 1–2 weeks**

- Project setup.
- Authentication.
- Database.
- User profile.
- Basic frontend.

## Phase 2 — Family Health

**Duration: 1–2 weeks**

- Family tree.
- Family medical history.
- Family health visualization.

## Phase 3 — Medical AI

**Duration: 2–3 weeks**

- Report upload.
- OCR.
- Medical information extraction.
- Structured storage.
- AI report explanation.

## Phase 4 — Health Intelligence

**Duration: 2–3 weeks**

- Health timeline.
- Historical comparison.
- Trend engine.
- Risk signals.
- Recommendation engine.

## Phase 5 — Lifestyle

**Duration: 1–2 weeks**

- Exercise.
- Diet.
- Sleep.
- Lifestyle dashboard.

## Phase 6 — Healthcare & Emergency

**Duration: 1–2 weeks**

- Doctors.
- Family doctor.
- Emergency contacts.
- Nearby hospitals.
- Emergency mode.

## Phase 7 — Security & Deployment

**Duration: 1–2 weeks**

- Security.
- Audit logs.
- Consent management.
- Testing.
- Deployment.

---

# 23. Future Product Vision

The long-term product can evolve into:

```text
             CAREGRAPH AI
                  │
       ┌──────────┼──────────┐
       ▼          ▼          ▼
     FAMILY     PERSONAL   LIFESTYLE
      HEALTH      HEALTH     HEALTH
       │          │          │
       └──────────┼──────────┘
                  ▼
            HEALTH GRAPH
                  │
       ┌──────────┼──────────┐
       ▼          ▼          ▼
     REPORTS     RISKS     TRENDS
       │          │          │
       └──────────┼──────────┘
                  ▼
           AI HEALTH ENGINE
                  │
       ┌──────────┼──────────┐
       ▼          ▼          ▼
    PREVENTION  LIFESTYLE  CARE TEAM
       │          │          │
       └──────────┼──────────┘
                  ▼
             USER ACTION
                  │
                  ▼
             NEW HEALTH DATA
                  │
                  └──────────────→ HEALTH GRAPH
```

The ultimate product becomes a **longitudinal health intelligence platform**, rather than simply a medical-report analyzer.

---

# 24. Product Positioning

## One-line description

> **CareGraph AI is an intelligent family health platform that connects family history, medical reports, health trends and lifestyle data to provide personalized preventive-care guidance and continuous health management.**

## Pitch

> **“Your family's health history is scattered across generations, hospitals and documents. CareGraph AI brings it together, understands your health journey over time, analyzes your medical reports, identifies meaningful trends, and helps you take informed preventive-health actions.”**

---

# 25. Key Differentiator

The fundamental product advantage is the **connection between modules**.

A conventional application might provide:

```text
Report Analyzer
OR
Fitness Tracker
OR
Diet App
OR
Doctor Finder
OR
Emergency Contacts
```

CareGraph AI combines them:

```text
Family History
       ↓
Personal Health
       ↓
Medical Reports
       ↓
Longitudinal Trends
       ↓
Risk Signals
       ↓
Preventive Guidance
       ↓
Doctor / Healthcare Guidance
       ↓
Lifestyle Plan
       ↓
Health Tracking
       ↓
New Reports
       ↓
Continuous Re-analysis
```

Therefore:

> **The product's core feature is not any individual module. The core feature is the Health Intelligence Graph connecting all modules together.**

---

# 26. Final Product Principle

**CareGraph AI should help users understand and organize their health — not replace healthcare professionals.**

Every recommendation should be:

**Evidence-informed + Explainable + Personalized + Consent-based + Safety-focused**

The system should always make it clear when professional medical evaluation is appropriate.