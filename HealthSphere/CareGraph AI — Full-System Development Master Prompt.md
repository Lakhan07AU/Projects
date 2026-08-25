# MASTER DEVELOPMENT PROMPT
## Build CareGraph AI — Full-Stack AI Family Health Intelligence Platform

You are a senior full-stack architect, AI/ML engineer, backend engineer, frontend engineer, database engineer, DevOps engineer, security engineer, UX designer, and healthcare-product engineer.

Your task is to **design, develop, test, integrate, and prepare for deployment a fully functional application called `CareGraph AI`**.

Do not create a prototype with fake buttons or placeholder functionality.

Build a working, modular, production-oriented system where all major modules are connected through a central health-data and health-intelligence architecture.

---

# 1. PRODUCT

## Product Name

**CareGraph AI**

## Tagline

**Understand your history. Track your health. Act earlier.**

## Product Description

CareGraph AI is an AI-powered personal and family health-management platform.

It allows users to:

1. Create a personal health profile.
2. Build and maintain family health history.
3. Upload medical reports.
4. Extract structured medical information from uploaded documents.
5. Analyze medical reports.
6. Compare current reports with historical reports.
7. Detect health trends.
8. Identify relevant health-risk signals.
9. Provide preventive-care guidance.
10. Suggest appropriate healthcare specialties to discuss with a professional.
11. Provide evidence-informed exercise recommendations.
12. Provide personalized lifestyle guidance.
13. Generate nutrition/diet suggestions.
14. Track health metrics.
15. Maintain a health timeline.
16. Maintain family doctor and healthcare-provider information.
17. Maintain emergency contacts.
18. Find nearby hospitals and healthcare facilities.
19. Provide an emergency-access screen.
20. Generate reminders and follow-up tasks.
21. Continuously update the user's health profile as new information is added.

The application must function as **one integrated system**, not as disconnected modules.

---

# 2. CRITICAL HEALTHCARE SAFETY RULE

This application is a health-management and decision-support system.

It is NOT an autonomous doctor.

The system must NEVER:

- Claim to diagnose a disease.
- Prescribe medication.
- Change medication dosage.
- Tell a user to stop medication.
- Guarantee that a user will develop or not develop a disease.
- Present an AI risk score as a medical diagnosis.
- Generate arbitrary medical test schedules.
- Pretend that an AI recommendation is a doctor's decision.

Use language such as:

- "This may be worth discussing with your healthcare professional."
- "This result appears outside the reference range shown on the report."
- "Your records show an increasing trend."
- "Consider discussing appropriate screening with a qualified healthcare professional."

Do NOT use:

- "You have diabetes."
- "You definitely have heart disease."
- "Take this medicine."
- "Stop taking your medicine."

All medical recommendations must be based on explicit rules, validated sources/guidelines, or clearly labeled general wellness guidance.

---

# 3. DEVELOPMENT PRINCIPLE

Build the system in this order:

```text
Architecture
↓
Database
↓
Backend APIs
↓
Authentication
↓
Core health data
↓
Medical document pipeline
↓
AI/ML layer
↓
Recommendation engine
↓
Frontend
↓
Integration
↓
Testing
↓
Security
↓
Deployment
```

Do not build isolated UI screens first.

Every frontend feature must connect to a real backend API and persistent database.

Do not use fake/mock data in production functionality.

Seed data may be provided for development/testing only.

---

# 4. RECOMMENDED TECHNOLOGY STACK

Use the following stack unless there is a strong technical reason to change it.

## Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS
- shadcn/ui or equivalent accessible component system
- Recharts for charts
- React Hook Form
- Zod

## Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic

## Database

- PostgreSQL

## Cache / background processing

- Redis
- Celery or equivalent task queue

## File storage

Use S3-compatible object storage.

Development can use local storage or MinIO.

## AI / ML

- Python
- scikit-learn
- PyTorch where required
- Hugging Face Transformers where useful
- LLM API abstraction
- OCR/document-processing layer

Do not hard-code the application to one AI provider.

Create an AI provider abstraction.

Example:

```text
AIProvider
├── OpenAIProvider
├── LocalModelProvider
└── MockAIProvider
```

## Deployment

Use Docker.

Create:

- Dockerfile
- docker-compose.yml
- environment configuration
- production deployment documentation
- health checks

---

# 5. REPOSITORY STRUCTURE

Use a monorepo.

Recommended:

```text
caregraph-ai/
│
├── apps/
│   ├── web/
│   │   ├── app/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── lib/
│   │   └── tests/
│   │
│   └── api/
│       ├── app/
│       │   ├── api/
│       │   ├── core/
│       │   ├── models/
│       │   ├── schemas/
│       │   ├── services/
│       │   ├── repositories/
│       │   ├── ai/
│       │   ├── clinical/
│       │   ├── workers/
│       │   └── tests/
│       │
│       └── alembic/
│
├── packages/
│   ├── shared-types/
│   ├── ui/
│   └── config/
│
├── ml/
│   ├── preprocessing/
│   ├── models/
│   ├── evaluation/
│   └── notebooks/
│
├── infrastructure/
│   ├── docker/
│   └── deployment/
│
├── docs/
│   ├── architecture.md
│   ├── api.md
│   ├── database.md
│   ├── ai-safety.md
│   └── deployment.md
│
├── tests/
│   ├── integration/
│   ├── e2e/
│   └── security/
│
├── .env.example
├── docker-compose.yml
├── README.md
└── LICENSE
```

Keep responsibilities separated.

---

# 6. CENTRAL ARCHITECTURE

The most important architectural principle is:

## One central Health Profile

All modules must communicate through the user's health profile.

```text
                    USER
                     │
                     ▼
             PERSONAL PROFILE
                     │
       ┌─────────────┼─────────────┐
       │             │             │
       ▼             ▼             ▼
 FAMILY HISTORY   MEDICAL       LIFESTYLE
                  REPORTS
       │             │             │
       └─────────────┼─────────────┘
                     ▼
              HEALTH DATA LAYER
                     │
                     ▼
             HEALTH INTELLIGENCE
                  ENGINE
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
    TRENDS         RISK        RECOMMENDATIONS
       │             │             │
       └─────────────┼─────────────┘
                     ▼
             PERSONAL HEALTH
                 ASSISTANT
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
     DOCTOR       LIFESTYLE     EMERGENCY
     GUIDANCE     GUIDANCE       SYSTEM
```

---

# 7. USER ROLES

Implement:

## User

Normal account owner.

## Caregiver

Optional future role for managing another person's profile with permission.

## Healthcare Professional

Optional future role.

Do not implement unrestricted access between users.

Use explicit authorization and consent.

---

# 8. AUTHENTICATION

Implement:

- Registration
- Login
- Logout
- Password hashing
- Password reset
- Email verification architecture
- Refresh tokens/session handling
- Protected routes
- Account deletion

Use secure password hashing.

Never store plaintext passwords.

Implement rate limiting for authentication endpoints.

---

# 9. PERSONAL HEALTH PROFILE

Create a complete profile.

Fields should include:

```text
name
date_of_birth
sex
height
weight
blood_group
allergies
existing_conditions
current_medications
lifestyle_information
diet_preferences
exercise_preferences
emergency_information
```

Do not make every field mandatory.

Users must be able to update their profile.

Create audit records for important changes.

---

# 10. FAMILY HEALTH HISTORY

Create a family-tree module.

Users can add:

- Father
- Mother
- Brother
- Sister
- Son
- Daughter
- Grandfather
- Grandmother
- Uncle
- Aunt
- Other

Each family member can contain:

```text
relationship
name
date_of_birth
age
living_status
conditions
diagnosis_age
major_surgeries
genetic_conditions
relevant_notes
```

Create family-health relationships.

Display:

```text
Family Tree
↓
Family Conditions
↓
Potentially Relevant Family History
```

The system should never assume a family member has a condition unless entered by the user.

---

# 11. MEDICAL CONDITION MODEL

Create normalized condition entities.

Each condition should support:

```text
id
name
category
description
source
created_at
updated_at
```

User conditions should reference normalized conditions.

Do not store everything as arbitrary text.

Allow free-text notes in addition to structured fields.

---

# 12. MEDICAL REPORT MODULE

Users must be able to:

- Upload PDF.
- Upload JPG.
- Upload PNG.
- View uploaded documents.
- Delete documents.
- Download documents.
- View analysis.
- Compare reports.

Supported document categories:

```text
CBC
Lipid Profile
HbA1c
Blood Glucose
Thyroid
Liver Function
Kidney Function
ECG
Imaging Report
Prescription
Doctor Note
Other
```

---

# 13. DOCUMENT PROCESSING PIPELINE

Implement asynchronous processing.

Pipeline:

```text
UPLOAD
↓
VALIDATE
↓
STORE ORIGINAL
↓
CREATE PROCESSING JOB
↓
OCR / TEXT EXTRACTION
↓
DOCUMENT CLASSIFICATION
↓
MEDICAL ENTITY EXTRACTION
↓
LAB VALUE EXTRACTION
↓
REFERENCE RANGE EXTRACTION
↓
NORMALIZATION
↓
SAVE STRUCTURED DATA
↓
TREND ANALYSIS
↓
AI EXPLANATION
↓
SAFETY VALIDATION
↓
MARK COMPLETE
```

Never block the upload request while processing a large report.

Use background jobs.

---

# 14. MEDICAL DATA EXTRACTION

Extract structured information such as:

```text
test_name
value
unit
reference_low
reference_high
abnormal_flag
report_date
laboratory
category
confidence
```

Example:

```json
{
  "test_name": "HbA1c",
  "value": 6.0,
  "unit": "%",
  "reference_low": null,
  "reference_high": null,
  "report_date": "2026-08-20",
  "confidence": 0.96
}
```

Do not invent missing reference ranges.

If the report does not contain a reference range, mark it as unavailable.

---

# 15. MEDICAL REPORT ANALYSIS

Generate:

## Summary

What information was extracted.

## Abnormal/flagged results

Only based on the report's provided reference range or validated rules.

## Trend

Compare with historical results.

## Explanation

Explain medical terminology in plain language.

## Recommended discussion

Tell the user what may be worth discussing with a healthcare professional.

Do not diagnose.

---

# 16. HEALTH TIMELINE

Create a unified timeline containing:

- Report uploads
- Lab results
- Health measurements
- Doctor visits
- Conditions
- Medications
- Lifestyle milestones
- Recommendations
- Reminders

Each event should have:

```text
event_type
date
title
description
source
related_entity
```

Allow filtering.

---

# 17. HEALTH METRICS

Support:

- Weight
- Height
- BMI
- Blood pressure
- Heart rate
- Blood glucose
- HbA1c
- Cholesterol
- Sleep
- Exercise duration
- Steps
- Other configurable metrics

Create APIs:

```text
POST /health-metrics
GET /health-metrics
GET /health-metrics/{metric}
GET /health-metrics/{metric}/trend
```

Create interactive charts.

---

# 18. TREND ENGINE

Build a reusable trend-analysis service.

Input:

```text
metric
date
value
```

Output:

```text
direction
rate_of_change
stability
possible_outlier
confidence
```

Support:

- Stable
- Increasing
- Decreasing
- Sudden change
- Insufficient data

Do not label a trend as a disease.

---

# 19. FAMILY RISK CONTEXT ENGINE

Combine:

```text
family history
+
personal history
+
age
+
health measurements
+
medical reports
+
lifestyle
```

Use this to identify relevant contextual risk factors.

The engine should return:

```json
{
  "risk_area": "cardiovascular_health",
  "signals": [],
  "confidence": 0.72,
  "explanation": "",
  "recommended_discussion": ""
}
```

Do not expose raw ML scores as medical truth.

---

# 20. CLINICAL RULE ENGINE

Do not put clinical decision logic inside LLM prompts.

Create a separate rule engine.

Example:

```text
ClinicalRule
├── id
├── condition
├── population
├── trigger
├── recommendation
├── source
├── version
└── last_reviewed
```

Every medical rule must have:

- Source.
- Version.
- Review date.
- Applicable population.
- Explanation.

The LLM can explain the result but must not invent the rule.

---

# 21. PREVENTIVE-CARE ENGINE

Create a preventive-care engine that evaluates applicable guidance.

Inputs:

```text
age
sex
family history
medical history
existing conditions
previous measurements
previous screening information
```

Output:

```text
topic
reason
guidance
source
priority
```

Use wording such as:

> "Consider discussing this screening topic with your healthcare professional."

Do not automatically claim that a specific test is medically necessary unless the applicable validated guideline supports that statement.

---

# 22. DOCTOR SPECIALTY RECOMMENDATION

Create a specialty recommendation engine.

Input:

```text
health signals
report categories
existing conditions
user-selected concerns
```

Output:

```text
specialty
reason
confidence
```

Example:

```json
{
  "specialty": "Cardiology",
  "reason": "Several cardiovascular-related factors may warrant professional discussion.",
  "confidence": 0.74
}
```

Never claim:

> "You need a cardiologist."

Use:

> "A cardiology consultation may be worth discussing with your primary-care physician."

---

# 23. LIFESTYLE ENGINE

Create personalized wellness recommendations.

Inputs:

```text
activity
sleep
diet
weight
goals
preferences
```

Output:

```text
exercise_plan
sleep_goal
nutrition_guidance
habit_goals
weekly_summary
```

Separate general wellness guidance from medical treatment.

---

# 24. EXERCISE ENGINE

Generate weekly plans.

Example:

```text
Monday
Walking — 20 min

Tuesday
Mobility — 10 min

Wednesday
Walking — 20 min

Thursday
Rest / light movement

Friday
Walking — 25 min
```

Include safety logic.

If the user's profile indicates potentially relevant medical concerns, use cautious language and recommend professional advice before major changes.

---

# 25. DIET ENGINE

Inputs:

```text
age
height
weight
activity
goal
food_preference
diet_type
allergies
health_context
budget
location
```

Output:

```text
daily_meals
weekly_plan
food_substitutions
nutrition_notes
shopping_list
```

Do not provide dangerous crash diets.

Do not provide therapeutic diets as a substitute for professional medical advice.

---

# 26. AI HEALTH ASSISTANT

Create a conversational health assistant.

It should have access ONLY to the user's authorized structured health context.

Architecture:

```text
User Question
↓
Intent Detection
↓
Retrieve Relevant User Data
↓
Retrieve Approved Clinical Knowledge
↓
Generate Response
↓
Safety Filter
↓
Response
```

The assistant should be able to answer:

- "What changed in my latest report?"
- "Show my HbA1c trend."
- "What health information have I uploaded?"
- "What lifestyle habits should I improve?"
- "What should I discuss with my doctor?"
- "Show my upcoming reminders."

It should NOT answer with unsupported diagnosis or prescriptions.

---

# 27. RAG / KNOWLEDGE SYSTEM

Create a retrieval architecture.

Use approved sources for medical information.

Store metadata:

```text
source
title
version
publication_date
last_reviewed
jurisdiction
topic
```

The model must prefer approved knowledge sources over unsupported generated claims.

Every clinical recommendation should be traceable to its rule/source where possible.

---

# 28. EMERGENCY CONTACTS

Allow users to create:

```text
name
relationship
phone
priority
notes
```

Categories:

- Family
- Friend
- Neighbour
- Doctor
- Other

Allow one-tap calling through the appropriate device/browser capability where supported.

Do not automatically call anyone without user action, except for future explicitly authorized emergency workflows.

---

# 29. CONTACT IMPORT

Implement an explicit permission-based import flow.

Do not scrape contacts.

Do not silently read contacts.

User flow:

```text
Import Contacts
↓
Request permission
↓
Show contacts
↓
User selects contacts
↓
Confirm
↓
Save selected contacts
```

---

# 30. DOCTOR MANAGEMENT

Allow users to manually add:

```text
doctor_name
specialty
clinic
phone
email
address
notes
```

Allow marking one provider as:

```text
Family Doctor
```

Allow multiple specialists.

---

# 31. HOSPITAL / HEALTHCARE DISCOVERY

Create a healthcare discovery service abstraction.

Support:

- Nearby hospitals.
- Clinics.
- Diagnostic labs.
- Pharmacies.

Do not hard-code location data.

Create provider abstraction:

```text
HealthcareLocationProvider
├── GoogleMapsProvider
├── MapboxProvider
└── MockProvider
```

Require user location permission.

Display:

```text
name
distance
address
phone
opening_hours
services
```

---

# 32. EMERGENCY DASHBOARD

Create a dedicated high-visibility emergency page.

Display:

```text
EMERGENCY

Call Emergency Services

Call Emergency Contact

Call Family Doctor

Find Nearby Hospital

Emergency Health Information

Blood Group
Allergies
Important Conditions
Current Medications
```

The emergency page must load extremely quickly.

Avoid unnecessary AI processing on the emergency screen.

---

# 33. REMINDER ENGINE

Create:

```text
Reminder
├── id
├── user_id
├── type
├── title
├── description
├── due_at
├── recurrence
├── status
└── source
```

Support:

- One-time.
- Daily.
- Weekly.
- Monthly.
- Custom recurrence.

Allow:

- Complete.
- Snooze.
- Reschedule.
- Delete.

---

# 34. NOTIFICATION SYSTEM

Build notification abstraction:

```text
NotificationService
├── InApp
├── Email
├── Push
└── SMS
```

Only implement providers that are configured.

Never hard-code credentials.

---

# 35. DASHBOARD

Build a polished dashboard.

Sections:

```text
Health Overview
Recent Reports
Health Trends
Family Health
Lifestyle
Upcoming Reminders
Care Team
Emergency
AI Insights
```

Primary actions:

```text
Upload Report
Add Health Data
Add Family Member
View Timeline
View Reports
View Recommendations
```

---

# 36. FAMILY DASHBOARD

Show:

```text
Family Health Overview

Family members
Known health conditions
Relevant family-history patterns
Important records
```

Do not expose private information of another family member unless permission exists.

---

# 37. REPORT COMPARISON UI

Allow users to select:

```text
Report A
vs
Report B
```

Display:

```text
Metric        Previous      Current       Trend
HbA1c         5.7           6.0           ↑
Cholesterol   ...           ...           →
...
```

Include report dates.

Never compare incompatible tests without validation.

---

# 38. HEALTH GRAPH

Create a visual health relationship system.

Example:

```text
Family History
      │
      ▼
Risk Context
      │
      ▼
Personal Metrics
      │
      ▼
Medical Reports
      │
      ▼
Health Trends
      │
      ▼
Recommendations
      │
      ▼
Lifestyle
      │
      ▼
Future Health Data
```

This should be the core differentiating feature of the product.

---

# 39. DATABASE TABLES

Create migrations for at least:

```text
users
user_profiles
family_members
family_relationships
family_conditions
conditions
user_conditions
medical_reports
medical_report_pages
medical_entities
lab_results
health_metrics
health_metric_values
medications
doctors
doctor_relationships
hospitals
emergency_contacts
lifestyle_profiles
exercise_logs
diet_logs
sleep_logs
recommendations
clinical_rules
clinical_sources
health_timeline_events
reminders
notifications
ai_conversations
ai_messages
document_processing_jobs
consents
audit_logs
```

Use foreign keys.

Use indexes on:

- user_id
- report_date
- metric_type
- family relationships
- timeline dates

---

# 40. API DESIGN

Implement REST APIs.

Example:

## Authentication

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/logout
POST /api/v1/auth/refresh
POST /api/v1/auth/forgot-password
```

## Profile

```text
GET /api/v1/profile
PUT /api/v1/profile
```

## Family

```text
GET /api/v1/family
POST /api/v1/family/members
PUT /api/v1/family/members/{id}
DELETE /api/v1/family/members/{id}
GET /api/v1/family/tree
```

## Reports

```text
POST /api/v1/reports
GET /api/v1/reports
GET /api/v1/reports/{id}
DELETE /api/v1/reports/{id}
POST /api/v1/reports/{id}/analyze
GET /api/v1/reports/{id}/analysis
```

## Health metrics

```text
POST /api/v1/health-metrics
GET /api/v1/health-metrics
GET /api/v1/health-metrics/{type}/trend
```

## Recommendations

```text
GET /api/v1/recommendations
GET /api/v1/recommendations/{id}
```

## Lifestyle

```text
GET /api/v1/lifestyle
PUT /api/v1/lifestyle
POST /api/v1/exercise
POST /api/v1/diet
POST /api/v1/sleep
```

## Doctors

```text
GET /api/v1/doctors
POST /api/v1/doctors
PUT /api/v1/doctors/{id}
DELETE /api/v1/doctors/{id}
```

## Emergency contacts

```text
GET /api/v1/emergency-contacts
POST /api/v1/emergency-contacts
PUT /api/v1/emergency-contacts/{id}
DELETE /api/v1/emergency-contacts/{id}
```

## Healthcare discovery

```text
GET /api/v1/healthcare/nearby
```

## AI Assistant

```text
POST /api/v1/assistant/chat
GET /api/v1/assistant/history
```

---

# 41. FRONTEND ROUTES

Create:

```text
/
 /login
 /register
 /dashboard
 /profile
 /family
 /family/tree
 /reports
 /reports/upload
 /reports/[id]
 /health
 /health/timeline
 /health/trends
 /recommendations
 /lifestyle
 /lifestyle/exercise
 /lifestyle/diet
 /lifestyle/sleep
 /doctors
 /hospitals
 /emergency
 /contacts
 /settings
 /privacy
 /assistant
```

Protect authenticated routes.

---

# 42. UI/UX DESIGN

Use a modern healthcare interface.

Design principles:

- Clean.
- Calm.
- Accessible.
- Mobile responsive.
- High contrast.
- Minimal cognitive load.
- Clear medical disclaimers.
- No unnecessary animations.
- Fast navigation.

Use cards for:

- Health metrics.
- Reports.
- Recommendations.
- Reminders.
- Care team.

Use charts for:

- Trends.
- Health measurements.
- Lifestyle progress.

---

# 43. MOBILE RESPONSIVENESS

The application must work on:

- Desktop.
- Tablet.
- Mobile.

The emergency page must be especially optimized for mobile.

---

# 44. ACCESSIBILITY

Implement:

- Keyboard navigation.
- Semantic HTML.
- ARIA labels where necessary.
- Accessible form validation.
- Color-independent status indicators.
- Readable font sizes.
- Screen-reader compatibility.

---

# 45. SECURITY

Implement:

- HTTPS-ready architecture.
- Secure cookies/tokens.
- Password hashing.
- Input validation.
- SQL injection protection.
- XSS protection.
- CSRF protection where applicable.
- Rate limiting.
- File upload validation.
- Malware-aware upload strategy.
- File type verification.
- Maximum file sizes.
- Access control.
- Audit logging.

Never expose:

```text
API keys
database passwords
JWT secrets
storage credentials
```

in frontend code.

---

# 46. MEDICAL DATA SECURITY

Treat health information as highly sensitive.

Implement:

```text
Encryption in transit
Encryption at rest
Access controls
Consent management
Audit logs
Data deletion
Data export
Least privilege
```

Do not log sensitive medical information unnecessarily.

Do not put medical report contents into ordinary application logs.

---

# 47. AI SECURITY

Protect against:

- Prompt injection.
- Malicious uploaded documents.
- Data exfiltration.
- Jailbreak attempts.
- Tool abuse.

Uploaded documents are untrusted input.

Never allow text inside a medical document to override system instructions.

---

# 48. AI OUTPUT VALIDATION

All AI-generated medical outputs must pass through:

```text
LLM
↓
Structured Output Validator
↓
Safety Validator
↓
Clinical Rule Validator
↓
Final Response
```

Reject malformed or unsafe output.

Use structured JSON from AI models whenever possible.

---

# 49. CONFIDENCE HANDLING

Every AI extraction should have confidence.

Example:

```text
Extraction confidence: 96%
```

If confidence is low:

```text
We could not confidently read this value.
Please verify it against the original report.
```

Never silently invent missing information.

---

# 50. DATA PROVENANCE

Every extracted medical value must track its origin.

Example:

```text
HbA1c
Value: 6.0%
Source:
Blood_Report_Aug_2026.pdf
Page: 2
Extraction confidence: 96%
```

This is critical.

Users must be able to verify information against the original document.

---

# 51. AUDIT LOGGING

Record important actions:

```text
LOGIN
REPORT_UPLOADED
REPORT_ANALYZED
PROFILE_UPDATED
FAMILY_MEMBER_ADDED
RECOMMENDATION_GENERATED
CONTACT_IMPORTED
DATA_EXPORTED
DATA_DELETED
```

Do not store unnecessary sensitive payloads in logs.

---

# 52. CONSENT MANAGEMENT

Create a consent system.

Users should be able to manage:

```text
Location Access
Contact Access
Medical Data Processing
AI Analysis
Data Sharing
Notifications
```

Store:

```text
consent_type
granted
timestamp
version
```

---

# 53. ERROR HANDLING

Every API must return consistent errors.

Example:

```json
{
  "success": false,
  "error": {
    "code": "REPORT_PROCESSING_FAILED",
    "message": "The medical report could not be processed."
  }
}
```

Never expose stack traces to users.

---

# 54. BACKGROUND JOBS

Use background processing for:

- OCR.
- Medical report extraction.
- AI analysis.
- Trend recalculation.
- Recommendation generation.
- Notifications.
- Scheduled reminders.

Show job status:

```text
Uploading
Processing
Analyzing
Complete
Failed
```

---

# 55. OBSERVABILITY

Implement:

- Structured application logs.
- Error tracking abstraction.
- Health endpoints.
- Database health check.
- AI service health check.
- Background worker health.
- Request IDs.

Endpoints:

```text
/health
/ready
```

---

# 56. TESTING

Write tests at all levels.

## Unit tests

Test:

- Authentication.
- Health calculations.
- Trend engine.
- Recommendation rules.
- Data validation.
- Permissions.

## Integration tests

Test:

```text
Upload
→ OCR
→ Extraction
→ Database
→ Analysis
→ Recommendation
```

## E2E tests

Test:

```text
Register
→ Login
→ Add family member
→ Upload report
→ Analyze report
→ View trend
→ View recommendation
→ Add emergency contact
```

## Security tests

Test:

- Unauthorized access.
- Broken object-level authorization.
- File upload attacks.
- SQL injection.
- XSS.
- Authentication abuse.

---

# 57. SAMPLE DATA

Create development seed data.

Include:

- Example user.
- Family members.
- Sample health metrics.
- Sample reports.
- Sample doctors.
- Sample emergency contacts.

Clearly label all seed data as fictional.

Never present seed data as real medical information.

---

# 58. ENVIRONMENT VARIABLES

Create `.env.example`.

Include placeholders for:

```text
DATABASE_URL
REDIS_URL
SECRET_KEY
JWT_SECRET
STORAGE_ENDPOINT
STORAGE_ACCESS_KEY
STORAGE_SECRET_KEY
STORAGE_BUCKET
AI_PROVIDER
AI_API_KEY
MAP_PROVIDER
MAP_API_KEY
EMAIL_PROVIDER
EMAIL_API_KEY
```

Never commit `.env`.

---

# 59. DOCKER

Create:

```text
docker-compose.yml
```

Services:

```text
frontend
backend
postgres
redis
worker
minio
```

Application should start with one documented command.

Example:

```bash
docker compose up --build
```

---

# 60. LOCAL DEVELOPMENT

README must explain:

```text
Prerequisites
Installation
Environment variables
Database migration
Seed data
Starting backend
Starting frontend
Starting workers
Running tests
```

---

# 61. DATABASE MIGRATIONS

Use Alembic.

Provide:

```bash
alembic upgrade head
```

Never manually require users to create tables.

---

# 62. API DOCUMENTATION

FastAPI should automatically expose:

```text
/api/docs
/api/redoc
```

Document:

- Request schema.
- Response schema.
- Authentication.
- Errors.
- Example responses.

---

# 63. FRONTEND STATE MANAGEMENT

Use an appropriate data-fetching architecture.

Recommended:

- TanStack Query.
- React Hook Form.
- Zod.

Avoid unnecessary global state.

---

# 64. FILE UPLOAD UX

Show:

```text
Drag & Drop

or

Choose File

Supported:
PDF, JPG, PNG

Maximum size:
Configured by backend
```

After upload:

```text
Upload complete

Processing report...
```

Then:

```text
Analysis complete

View results
```

---

# 65. MEDICAL REPORT UI

Display:

```text
Report Information

Date
Type
Source
Uploaded At

Extracted Results

Test
Value
Unit
Reference Range
Status

AI Explanation

Historical Trend

Recommended Discussion
```

Always allow the user to open the original report.

---

# 66. HEALTH TIMELINE UI

Create a vertical timeline.

Example:

```text
AUG 2026
│
● Blood report uploaded
│
● HbA1c analyzed
│
● Health trend updated
│
● Recommendation generated
```

---

# 67. HEALTH INSIGHTS

The dashboard should show a limited number of important insights.

Example:

```text
Health Insight

Your latest measurement has changed
compared with your previous record.

Why:
Previous value: X
Current value: Y

Suggested action:
Discuss the trend with your healthcare
professional if appropriate.
```

Do not overwhelm users.

---

# 68. SEARCH

Implement search across:

- Reports.
- Health timeline.
- Doctors.
- Family members.
- Health metrics.

Do not search raw medical documents using unsafe direct SQL string interpolation.

---

# 69. DATA EXPORT

Allow users to export their information.

Possible format:

```text
PDF summary
JSON
CSV
```

Export should include:

- Profile.
- Family history.
- Reports metadata.
- Health metrics.
- Timeline.
- Recommendations.
- Contacts.

Do not expose another person's data without authorization.

---

# 70. ACCOUNT DELETION

Implement permanent deletion workflow.

Before deletion:

```text
Confirm account deletion
↓
Explain consequences
↓
Optional data export
↓
User confirmation
↓
Deletion
```

Use soft deletion where required for audit/security purposes, while following applicable retention requirements.

---

# 71. PERFORMANCE REQUIREMENTS

Target:

- Dashboard initial load < 3 seconds under normal conditions.
- API response < 500ms for simple CRUD operations under normal conditions.
- Medical report processing must be asynchronous.
- Large documents must never block API workers.

Optimize database queries.

Add indexes.

Use pagination.

---

# 72. SCALABILITY

The architecture should support:

```text
100 users
→ 1,000 users
→ 10,000 users
→ 100,000+ users
```

without rewriting the core architecture.

Use stateless backend APIs where possible.

Use background workers for expensive AI operations.

---

# 73. DESIGN SYSTEM

Create reusable components:

```text
Button
Card
Modal
Dialog
Input
Select
DatePicker
MetricCard
TrendChart
ReportCard
FamilyMemberCard
RecommendationCard
ReminderCard
DoctorCard
EmergencyContactCard
HealthTimeline
UploadZone
AIInsightCard
```

Do not duplicate UI code.

---

# 74. FINAL DASHBOARD STRUCTURE

Build:

```text
┌──────────────────────────────────────────────┐
│ CAREGRAPH AI                                 │
├──────────────┬───────────────────────────────┤
│ Dashboard    │                               │
│ Health       │       HEALTH OVERVIEW         │
│ Family       │                               │
│ Reports      │   Metrics                     │
│ Timeline     │   Trends                      │
│ Insights     │   Recent Reports              │
│ Lifestyle    │   AI Insights                 │
│ Doctors      │   Upcoming Reminders          │
│ Hospitals    │                               │
│ Emergency    │                               │
│ Settings     │                               │
└──────────────┴───────────────────────────────┘
```

---

# 75. CORE INTEGRATION TEST

The application is not considered complete until this workflow works end-to-end:

```text
USER REGISTERS
      ↓
CREATES PROFILE
      ↓
ADDS FAMILY MEMBERS
      ↓
ADDS FAMILY HEALTH HISTORY
      ↓
UPLOADS MEDICAL REPORT
      ↓
REPORT STORED
      ↓
OCR RUNS
      ↓
MEDICAL DATA EXTRACTED
      ↓
RESULTS STORED
      ↓
HISTORICAL DATA RETRIEVED
      ↓
TREND CALCULATED
      ↓
FAMILY HISTORY CONTEXT APPLIED
      ↓
PREVENTIVE-CARE ENGINE RUNS
      ↓
RECOMMENDATION GENERATED
      ↓
SAFETY VALIDATION
      ↓
USER SEES INSIGHT
      ↓
HEALTH TIMELINE UPDATED
      ↓
REMINDER CREATED IF APPROPRIATE
      ↓
LIFESTYLE ENGINE UPDATES GUIDANCE
      ↓
USER TRACKS NEW DATA
      ↓
SYSTEM RE-ANALYZES
```

This workflow must be tested automatically.

---

# 76. DEVELOPMENT EXECUTION RULES

Do not attempt to generate the entire application in one unverified code dump.

Work incrementally.

For every phase:

1. Inspect the existing repository.
2. Create/update architecture.
3. Implement the feature.
4. Connect frontend to backend.
5. Create database migrations.
6. Write tests.
7. Run tests.
8. Fix errors.
9. Verify integration.
10. Update documentation.

Never claim a feature is complete if it is only mocked.

Never leave:

```text
TODO
FIXME
IMPLEMENT_ME
coming soon
placeholder
```

for core functionality.

---

# 77. WHEN AN EXTERNAL API IS REQUIRED

Create an abstraction layer.

Do not hard-code a vendor.

For example:

```text
MapsService
DocumentAIService
AIService
NotificationService
StorageService
```

Each service should have:

```text
interface
implementation
configuration
mock implementation
tests
```

This allows providers to be replaced later.

---

# 78. AI PROVIDER FAILURE

If the AI service is unavailable:

The application should still allow:

- Login.
- Profile management.
- Family history.
- Health metrics.
- Report storage.
- Timeline.
- Contacts.
- Doctors.

Display:

> "AI analysis is temporarily unavailable. Your report has been safely stored and can be analyzed later."

Do not crash the entire application.

---

# 79. MEDICAL REPORT FAILURE

If OCR cannot read the report:

```text
We couldn't reliably extract information
from this document.

Please verify the document quality or
enter the relevant values manually.
```

Never fabricate values.

---

# 80. USER CONTROL

Users must always be able to:

- Edit incorrect extracted data.
- Delete incorrect data.
- Correct family history.
- Delete reports.
- Disable AI analysis.
- Disable notifications.
- Remove emergency contacts.
- Revoke permissions.

---

# 81. AI CHAT CONTEXT

The assistant should retrieve only relevant information.

For example:

User:

> "What changed in my latest blood report?"

Retrieve:

```text
Latest report
Previous comparable report
Relevant health metrics
Relevant timeline events
```

Do not send the user's entire medical history to the model unnecessarily.

Use least-data retrieval.

---

# 82. PRIVACY-FIRST AI

Do not send:

- Unnecessary contacts.
- Unrelated family information.
- Unrelated medical reports.

to the LLM.

Use minimum necessary context.

---

# 83. SECURITY TEST CASE

Attempt:

```text
User A → access User B report
```

Expected:

```text
403 Forbidden
```

Attempt:

```text
User A → access User B emergency contact
```

Expected:

```text
403 Forbidden
```

Attempt:

```text
Unauthenticated → /api/v1/reports
```

Expected:

```text
401 Unauthorized
```

---

# 84. ACCEPTANCE CRITERIA

The system is considered MVP-complete only when:

### Authentication

- [ ] Registration works.
- [ ] Login works.
- [ ] Protected routes work.
- [ ] Logout works.

### Health profile

- [ ] User can create profile.
- [ ] User can edit profile.
- [ ] User can track health metrics.

### Family

- [ ] User can add family members.
- [ ] User can add family conditions.
- [ ] Family tree renders.
- [ ] Family data is private.

### Reports

- [ ] User can upload report.
- [ ] File is securely stored.
- [ ] OCR works.
- [ ] Medical data extraction works.
- [ ] Extracted data can be corrected.
- [ ] AI explanation works.
- [ ] Original report remains accessible.

### Health intelligence

- [ ] Historical values are compared.
- [ ] Trends are calculated.
- [ ] Recommendations are generated.
- [ ] Recommendations show explanations.
- [ ] Clinical rules have source metadata.

### Lifestyle

- [ ] Exercise plan works.
- [ ] Diet guidance works.
- [ ] Lifestyle tracking works.

### Healthcare

- [ ] Doctors can be added.
- [ ] Family doctor can be selected.
- [ ] Nearby healthcare discovery works with permission.

### Emergency

- [ ] Emergency contacts can be added.
- [ ] Emergency screen works.
- [ ] Emergency information displays correctly.

### Infrastructure

- [ ] Database migrations work.
- [ ] Docker works.
- [ ] Background worker works.
- [ ] Tests pass.
- [ ] API documentation exists.
- [ ] Environment configuration exists.

---

# 85. FINAL QUALITY REQUIREMENT

Before declaring the system complete, perform:

```text
Unit Tests
↓
Integration Tests
↓
E2E Tests
↓
Security Tests
↓
Permission Tests
↓
AI Safety Tests
↓
Performance Checks
↓
Mobile UI Testing
↓
Desktop UI Testing
↓
Docker Build
↓
Production Build
```

Fix all blocking issues.

---

# 86. REQUIRED DOCUMENTATION

Create:

```text
README.md
docs/architecture.md
docs/database.md
docs/api.md
docs/ai-architecture.md
docs/ai-safety.md
docs/security.md
docs/deployment.md
docs/development.md
```

README must include:

- Product overview.
- Architecture.
- Features.
- Tech stack.
- Installation.
- Environment variables.
- Database setup.
- Running the application.
- Running tests.
- Docker instructions.
- Deployment instructions.
- AI safety limitations.

---

# 87. DEFINITION OF DONE

Do not say:

> "The project is complete"

until:

1. Frontend works.
2. Backend works.
3. Database works.
4. Authentication works.
5. Family history works.
6. Medical reports work.
7. OCR works.
8. AI extraction works.
9. Health trends work.
10. Recommendation engine works.
11. Lifestyle features work.
12. Doctor management works.
13. Emergency contacts work.
14. Healthcare discovery works.
15. Notifications/reminders work.
16. Permissions work.
17. Security controls work.
18. Tests pass.
19. Docker deployment works.
20. Documentation is complete.

---

# 88. STARTING INSTRUCTION

Begin by:

### STEP 1

Inspect the existing repository and determine:

- Existing files.
- Existing framework.
- Existing dependencies.
- Existing database.
- Existing frontend.
- Existing backend.
- Existing environment configuration.

Do not overwrite working code unnecessarily.

### STEP 2

Create an architecture plan.

### STEP 3

Create the complete database schema and migrations.

### STEP 4

Implement authentication and user profile.

### STEP 5

Implement family health history.

### STEP 6

Implement medical report upload and secure storage.

### STEP 7

Implement asynchronous OCR and document processing.

### STEP 8

Implement structured medical-data extraction.

### STEP 9

Implement health metrics and timeline.

### STEP 10

Implement trend analysis.

### STEP 11

Implement clinical-rule and preventive-care architecture.

### STEP 12

Implement doctor-specialty recommendation.

### STEP 13

Implement lifestyle, exercise and nutrition modules.

### STEP 14

Implement doctors, emergency contacts and healthcare discovery.

### STEP 15

Implement AI health assistant.

### STEP 16

Integrate every module.

### STEP 17

Implement security, consent and audit logging.

### STEP 18

Write and run complete tests.

### STEP 19

Dockerize the complete system.

### STEP 20

Create final documentation and deployment instructions.

---

# 89. MOST IMPORTANT INSTRUCTION

Do not build CareGraph AI as a collection of independent features.

Build it as a **single connected health intelligence platform**.

The central relationship must be:

```text
                 FAMILY HISTORY
                       │
                       ▼
               PERSONAL PROFILE
                       │
                       ▼
                 MEDICAL REPORTS
                       │
                       ▼
                STRUCTURED DATA
                       │
                       ▼
                 HEALTH TIMELINE
                       │
                       ▼
                 TREND ENGINE
                       │
                       ▼
              RISK / CONTEXT ENGINE
                       │
                       ▼
            PREVENTIVE-CARE ENGINE
                       │
             ┌─────────┼─────────┐
             ▼         ▼         ▼
          DOCTOR     TEST      LIFESTYLE
         GUIDANCE   GUIDANCE    GUIDANCE
             │         │         │
             └─────────┼─────────┘
                       ▼
                USER HEALTH PLAN
                       │
                       ▼
                 NEW HEALTH DATA
                       │
                       └───────────────┐
                                       ▼
                                RE-ANALYSIS LOOP
```

Every new piece of health information should have the ability to update the relevant parts of the user's health profile.

The final result should feel like:

> **A continuously evolving digital health memory and preventive-care assistant for an individual and their family.**

Now begin implementation with repository inspection and architecture setup. Do not skip testing or security. Do not use fake implementations for core features.