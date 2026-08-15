# ROADGUARD AI
## AI-Powered Pothole Detection, Automatic Complaint Registration, Repair Estimation & Government Management Platform

You are a senior AI/ML engineer, Computer Vision engineer, Python backend developer, full-stack developer, GIS engineer, database architect, GenAI engineer, UI/UX designer, DevOps engineer, security engineer, and technical project mentor.

Build a complete, professional, production-style full-stack project called:

# ROADGUARD AI

### Tagline:
**Detect. Report. Prioritize. Repair.**

The project is an AI-powered road infrastructure management platform that uses Computer Vision to detect potholes and road damage from images/videos, automatically registers complaints with GPS location, detects duplicate complaints, estimates damage/repair area, calculates preliminary repair cost, prioritizes road repairs, and provides separate Public, Government, and Repair Team dashboards.

The system must also use Generative AI meaningfully for repair reports, explanations, summaries, and natural-language government analytics.

---

# 1. IMPORTANT DEVELOPMENT RULE

Do NOT try to generate the entire application in one giant code dump.

Develop the application incrementally.

First analyze the requirements and create:

1. System architecture
2. Component architecture
3. Database ER diagram
4. Folder structure
5. API specification
6. Frontend page structure
7. AI pipeline
8. GenAI architecture
9. Development roadmap

Then implement the application phase by phase.

After each major phase:

- Run tests
- Check for errors
- Fix errors
- Verify APIs
- Verify database
- Verify frontend
- Update documentation

Never leave major buttons or pages as fake placeholders.

---

# 2. PROJECT OBJECTIVE

The system should implement this complete workflow:

Citizen
↓
Upload/capture road image
↓
Image validation
↓
Computer Vision
↓
Pothole detection
↓
Segmentation
↓
Severity estimation
↓
Area estimation
↓
GPS/geolocation
↓
Duplicate detection
↓
Automatic complaint registration
↓
Repair area estimation
↓
Cost estimation
↓
Priority calculation
↓
Government verification
↓
Repair team assignment
↓
Repair
↓
Before/after verification
↓
Citizen confirmation
↓
Complaint closure

---

# 3. TECHNOLOGY STACK

## FRONTEND

Use only technologies that are already familiar to a developer who knows HTML, CSS and JavaScript.

Use:

- HTML5
- CSS3
- Vanilla JavaScript ES6+
- Bootstrap 5
- Chart.js
- Leaflet.js
- Fetch API

DO NOT use:

- React
- Next.js
- Vue
- Angular
- TypeScript
- Redux
- Tailwind CSS

The frontend must be understandable and editable by someone who knows HTML, CSS and JavaScript.

---

# 4. FRONTEND STRUCTURE

Use a traditional multi-page architecture.

Suggested structure:

frontend/

    index.html

    login.html
    register.html

    report.html
    complaints.html
    complaint-details.html

    map.html
    profile.html
    notifications.html

    government/
        dashboard.html
        potholes.html
        pothole-details.html
        repairs.html
        analytics.html
        users.html
        cost-rates.html

    repair-team/
        dashboard.html
        assignments.html
        repair-details.html

    css/
        style.css
        dashboard.css
        responsive.css
        map.css
        forms.css

    js/
        api.js
        auth.js
        login.js
        register.js
        report.js
        potholes.js
        map.js
        dashboard.js
        analytics.js
        repairs.js
        repair-team.js
        charts.js
        notifications.js
        utils.js

    assets/
        images/
        icons/

Use Bootstrap components where appropriate.

Use reusable JavaScript functions.

Use Fetch API for all backend communication.

---

# 5. FRONTEND DESIGN

The UI should look like a modern Smart City/Government platform rather than a basic college CRUD application.

Design requirements:

- Clean
- Professional
- Responsive
- Mobile-friendly
- Modern cards
- Tables
- Maps
- Charts
- Status badges
- Filters
- Search
- Modals
- Toast notifications
- Loading indicators
- Empty states
- Error states

Use a consistent design system.

Use icons through Bootstrap Icons or another lightweight icon library.

---

# 6. PUBLIC/CITIZEN PORTAL

Create a professional homepage.

Hero section:

# Making Every Road Safer with AI

Subtitle:

**Detect. Report. Prioritize. Repair.**

Buttons:

- Report a Pothole
- Explore Road Conditions

Show:

- Total reported potholes
- Total repaired
- Critical potholes
- Repair completion rate

Sections:

1. How RoadGuard AI works
2. AI detection
3. Public map
4. Recent reports
5. Repair progress
6. Statistics
7. About the project

---

# 7. CITIZEN REGISTRATION

Create:

register.html

Fields:

- Name
- Email
- Phone
- Password
- Confirm Password

Validate all fields.

Never store passwords in plaintext.

Use backend password hashing.

---

# 8. LOGIN

Create:

login.html

Support:

- Citizen
- Government Official
- Admin
- Repair Team

After login, redirect based on role.

Citizen:

/report.html

Government:

/government/dashboard.html

Repair Team:

/repair-team/dashboard.html

---

# 9. CITIZEN REPORTING SYSTEM

Create report.html.

The user should be able to:

1. Upload image
2. Upload video
3. Capture image if browser supports camera
4. Analyze image
5. Obtain GPS
6. View AI results
7. Confirm location
8. Submit complaint

---

# 10. IMAGE UPLOAD

Accept:

- JPG
- JPEG
- PNG
- WebP

Validate:

- File type
- File size
- Image dimensions

Show preview before upload.

Display loading state:

"Analyzing road image..."

---

# 11. COMPUTER VISION PIPELINE

Create a dedicated AI module.

Backend structure:

backend/
    app/
        ai/
            cv/
                detector.py
                segmenter.py
                severity.py
                area_estimator.py
                image_validator.py

Use:

- Python
- OpenCV
- NumPy
- Pillow
- Ultralytics YOLO

The architecture must support a custom-trained pothole detection model.

---

# 12. YOLO DETECTION

Create a configurable YOLO inference service.

Example:

Input:

Road image

Output:

{
    "detected": true,
    "confidence": 0.94,
    "detections": [
        {
            "class": "pothole",
            "confidence": 0.94,
            "bbox": [x1, y1, x2, y2]
        }
    ]
}

Display on frontend:

- Bounding box
- Confidence
- Number of potholes

---

# 13. IMPORTANT MODEL RULE

Do NOT pretend a generic pretrained YOLO model can automatically detect potholes accurately.

Create:

DEMO_MODE=true

When DEMO_MODE is true:

Use mock/sample inference for demonstration.

Clearly display:

"Demo AI Analysis"

When DEMO_MODE=false:

Load the actual pothole model using:

MODEL_PATH

This allows the project to work before the custom pothole dataset/model is available.

---

# 14. POTHOLE SEGMENTATION

Implement segmentation architecture.

Possible approach:

- YOLO segmentation
- SAM/SAM2-assisted workflow
- Another segmentation model

Keep segmentation modular.

Output:

- Segmentation mask
- Pixel area
- Bounding box

Example:

{
    "mask_available": true,
    "pixel_area": 14532
}

---

# 15. SEVERITY ENGINE

Create a severity scoring engine.

Inputs:

- Pothole area
- Detection confidence
- Estimated dimensions
- Depth if available
- Traffic level
- Number of reports
- Road importance

Output:

severity_score: 0–100

Classification:

LOW
MEDIUM
HIGH
CRITICAL

Example configurable thresholds:

0–25 = LOW
26–50 = MEDIUM
51–75 = HIGH
76–100 = CRITICAL

Clearly state these are project-configurable thresholds, not official engineering standards.

---

# 16. AREA ESTIMATION

Create:

area_estimator.py

Estimate physical area from image information.

Important:

A normal RGB image cannot reliably determine exact real-world dimensions without calibration/depth information.

Therefore:

Display:

"Estimated Area"

not:

"Exact Area"

Support future improvements:

- Camera calibration
- Depth estimation
- Smartphone AR/depth
- Stereo vision

Example:

Pixel area:

14532

Estimated area:

3.4 m²

Confidence:

0.72

---

# 17. GPS LOCATION

When reporting a pothole:

Request browser geolocation permission.

Capture:

- Latitude
- Longitude
- Timestamp

Allow the user to manually select the location on a Leaflet map if GPS is unavailable.

Never expose exact private user information publicly.

---

# 18. GEOGRAPHIC INFORMATION

Use:

PostgreSQL + PostGIS

Store:

- latitude
- longitude
- geometry
- road
- ward
- city
- district
- state

Support:

- Nearby potholes
- Distance calculation
- Ward filtering
- City filtering
- Road filtering

Use spatial indexes.

---

# 19. AUTOMATIC COMPLAINT CREATION

After AI analysis, display:

## Complaint Preview

Complaint ID:

Generated after submission.

Issue:

Pothole

Severity:

HIGH

AI Confidence:

94.3%

Estimated affected area:

3.4 m²

Location:

Automatically determined

Estimated repair cost:

₹21,000

Then:

[Confirm & Submit]

After submission:

Generate:

RGA-2026-000001

---

# 20. DUPLICATE COMPLAINT DETECTION

Implement duplicate detection.

Use:

1. GPS distance
2. Time
3. Image similarity
4. Existing pothole status

Example:

Existing:

PTH-000421

New citizen report:

REPORT-000982

If detected as duplicate:

Attach new report to PTH-000421.

Increase:

Supporting reports = 48

Do not create unnecessary duplicate potholes.

---

# 21. PUBLIC MAP

Use:

Leaflet.js

Create:

map.html

Display:

- Low potholes
- Medium potholes
- High potholes
- Critical potholes
- Repaired potholes

Use different marker styles/icons.

Clicking marker displays:

Pothole ID
Severity
Location
Report date
Number of reports
Estimated cost
Status

Never display:

- Citizen phone
- Citizen email
- Private account details

---

# 22. PUBLIC POTHOLE DETAILS

Create:

complaint-details.html

Show:

- Pothole ID
- Location
- Severity
- Date reported
- Number of reports
- Estimated area
- Estimated repair area
- Estimated cost
- Current status
- Assigned department/team if public
- Repair progress
- Before/after images when available

---

# 23. GOVERNMENT DASHBOARD

Create:

government/dashboard.html

Professional dashboard.

Top cards:

Total Potholes
Critical Potholes
Pending Verification
Repairs In Progress
Completed Repairs
Estimated Repair Budget
Actual Repair Cost
Average Repair Time

---

# 24. GOVERNMENT MAP

Create a map showing:

All potholes

Filters:

- Severity
- Ward
- Road
- Status
- Date
- Priority
- Repair team

Clicking a pothole opens details.

---

# 25. GOVERNMENT POTHOLE TABLE

Create:

government/potholes.html

Columns:

Pothole ID
Location
Severity
AI Confidence
Reports
Area
Priority
Estimated Cost
Status
Assigned Team
Date
Actions

Actions:

- View
- Verify
- Reject
- Assign
- Prioritize
- Update status

---

# 26. GOVERNMENT ANALYTICS

Create:

government/analytics.html

Use Chart.js.

Charts:

1. Potholes by severity
2. Potholes by ward
3. Reports over time
4. Repairs over time
5. Estimated vs actual cost
6. Average repair time
7. Road health
8. Pending vs completed
9. Top damaged roads

Add filters:

- Date
- Ward
- Severity
- Status

---

# 27. PRIORITY ENGINE

Create:

priority.py

Calculate:

Priority Score

Using:

- Severity
- Traffic level
- Road importance
- Supporting reports
- Pending duration

Example:

Priority Score = 92

Priority:

CRITICAL

Allow government officials to manually override priority.

Store:

- Original AI priority
- Modified priority
- Modification reason
- Modified by
- Modified timestamp

---

# 28. ROAD HEALTH SCORE

Create a score from:

0–100

Consider:

- Pothole density
- Severity
- Unresolved potholes
- Repair history
- Report frequency

Example:

90 = Excellent
75 = Good
55 = Moderate
35 = Poor
20 = Critical

Display road health in:

- Government dashboard
- Public map
- Road details

---

# 29. REPAIR AREA CALCULATION

Create a deterministic calculator.

Input:

Detected pothole area

Configurable:

Repair margin

Example:

Detected area:

3.5 m²

Repair margin:

20%

Recommended repair area:

4.2 m²

Do not claim this margin is an official engineering rule.

Make it configurable from admin settings.

---

# 30. COST ESTIMATION ENGINE

Create:

cost_estimator.py

Do NOT use GenAI to directly calculate cost.

Use deterministic formulas.

Components:

Material
Labor
Equipment
Transportation
Contingency

Formula:

Material Cost
+
Labor Cost
+
Equipment Cost
+
Transportation
+
Contingency

=

Estimated Total

Example:

Material = ₹8,000
Labor = ₹6,000
Equipment = ₹4,000
Transport = ₹2,000
Contingency = ₹1,000

Total:

₹21,000

Display:

"AI-assisted preliminary estimate."

Actual rates must come from the database.

---

# 31. COST RATE ADMIN PANEL

Create:

government/cost-rates.html

Admin can configure:

- Asphalt rate
- Concrete rate
- Labor rate
- Equipment rate
- Transport rate
- Contingency percentage
- Repair margin

Store rates in database.

Track:

- Effective date
- Updated by
- Previous value
- New value

---

# 32. REPAIR WORKFLOW

Statuses:

SUBMITTED
↓
AI_ANALYZED
↓
PENDING_VERIFICATION
↓
VERIFIED
↓
PRIORITIZED
↓
ASSIGNED
↓
IN_PROGRESS
↓
COMPLETED
↓
CITIZEN_VERIFICATION
↓
CLOSED

Validate status transitions.

Do not allow arbitrary invalid transitions.

---

# 33. REPAIR TEAM DASHBOARD

Create:

repair-team/dashboard.html

Show:

- Assigned repairs
- Pending repairs
- In-progress repairs
- Completed repairs

Each assignment should show:

Pothole ID
Location
Severity
Priority
Repair area
Estimated cost
Deadline
Before image

Repair team can:

- Accept job
- Start job
- Upload progress image
- Enter actual cost
- Mark completed

---

# 34. BEFORE/AFTER VERIFICATION

Allow repair teams to upload after-repair images.

Computer Vision compares:

Before image

vs

After image

Estimate:

- Remaining visible pothole area
- Damage reduction
- Repair verification score

Example:

Before:

4.2 m²

After:

0.4 m²

Reduction:

90.5%

Display:

"AI-assisted repair verification."

Do not claim official engineering certification.

---

# 35. CITIZEN VERIFICATION

After repair:

Citizen sees:

"Was this pothole repaired?"

Buttons:

YES
NO
PARTIALLY

Allow image upload.

Use citizen feedback as another data point.

---

# 36. NOTIFICATIONS

Create in-app notifications.

Citizen:

- Complaint submitted
- Complaint verified
- Repair assigned
- Repair started
- Repair completed
- Complaint closed

Government:

- New critical pothole
- New high-priority report
- Overdue repair

Repair team:

- New assignment
- Assignment changed
- Deadline approaching

---

# 37. GENAI SYSTEM

Create:

backend/app/ai/genai/

Files:

llm_service.py
prompt_manager.py
report_generator.py
assistant.py

Make the LLM provider configurable through environment variables.

Support an OpenAI-compatible API.

Never hard-code API keys.

---

# 38. GENAI REPAIR REPORT

Input structured data:

- Pothole ID
- Location
- Severity
- Confidence
- Area
- Repair area
- Cost breakdown
- Priority
- Status

Generate:

# Road Damage Assessment

Sections:

1. Problem Summary
2. Location
3. AI Detection
4. Severity
5. Estimated Area
6. Recommended Repair Area
7. Cost Estimate
8. Recommended Action
9. Priority
10. Limitations

The LLM must not invent numerical values.

All numbers must come from the backend.

---

# 39. GENAI GOVERNMENT ASSISTANT

Add an AI assistant inside the government dashboard.

Officials can ask:

"How many critical potholes are pending?"

"Which ward has the most potholes?"

"What is the estimated repair budget for Ward 17?"

"Show the top 10 priority potholes."

"What was the average repair time last month?"

"Which roads have deteriorated the most?"

The assistant must use controlled backend functions.

Create functions:

get_pothole_statistics()
get_ward_statistics()
get_repair_budget()
get_priority_potholes()
get_repair_time_statistics()
get_road_health()

Never allow the LLM to execute arbitrary SQL.

---

# 40. GENAI PUBLIC ASSISTANT

Optional public assistant.

Allow users to ask:

"Are there dangerous potholes near my selected location?"

"How many potholes are on this road?"

"Which nearby roads have critical damage?"

Only expose public information.

Do not reveal private citizen information.

---

# 41. RAG SYSTEM

Create optional RAG architecture.

Sources:

- Road repair guidelines
- Government documents
- Cost-rate documents
- Internal SOPs

Pipeline:

Documents
↓
Chunking
↓
Embeddings
↓
Vector database
↓
Retriever
↓
LLM

The system should cite the retrieved document when answering document-based questions.

Keep RAG modular so it can be enabled later.

---

# 42. DATABASE

Use PostgreSQL.

Use PostGIS for geospatial information.

Tables:

users
roles
potholes
reports
detections
segments
road_segments
wards
repairs
repair_teams
repair_updates
cost_rates
notifications
ai_analysis
model_versions
audit_logs

Use:

- Foreign keys
- Indexes
- Constraints
- Created/updated timestamps

Use UUIDs where appropriate.

---

# 43. DATABASE EXAMPLE

POTHOLES:

id
latitude
longitude
geometry
severity
severity_score
confidence
estimated_area
repair_area
estimated_cost
priority_score
status
road_id
ward_id
created_at
updated_at

REPORTS:

id
pothole_id
user_id
image_path
latitude
longitude
timestamp
ai_confidence

REPAIRS:

id
pothole_id
team_id
estimated_cost
actual_cost
repair_area
status
start_date
completion_date

---

# 44. AUTHENTICATION

Use:

JWT

Roles:

CITIZEN
GOVERNMENT_OFFICIAL
ADMIN
REPAIR_TEAM

Implement:

- Password hashing
- Login
- Logout/token handling
- Protected APIs
- Role-based authorization

Frontend must hide unauthorized navigation options.

Backend must independently enforce permissions.

Never rely only on frontend authorization.

---

# 45. SECURITY

Implement:

- Password hashing
- JWT
- CORS configuration
- Input validation
- File validation
- File size limits
- Rate limiting where appropriate
- SQL injection protection
- XSS-safe output
- Secure API keys
- Audit logging

Never store secrets in source code.

Never commit .env.

Create:

.env.example

---

# 46. FILE STORAGE

Use local storage during development.

Structure:

uploads/

    potholes/

    repairs/

    profiles/

Store file metadata in database.

Create storage abstraction so it can later support:

- S3
- Cloud storage
- MinIO

---

# 47. API DESIGN

FastAPI endpoints:

AUTH:

POST /api/auth/register
POST /api/auth/login
GET /api/auth/me

REPORTS:

POST /api/reports/analyze
POST /api/reports
GET /api/reports
GET /api/reports/{id}

POTHOLES:

GET /api/potholes
GET /api/potholes/{id}
GET /api/potholes/nearby
POST /api/potholes/{id}/verify
POST /api/potholes/{id}/reject

REPAIRS:

POST /api/repairs
GET /api/repairs
GET /api/repairs/{id}
PATCH /api/repairs/{id}
POST /api/repairs/{id}/complete

DASHBOARD:

GET /api/dashboard/statistics
GET /api/dashboard/wards
GET /api/dashboard/severity
GET /api/dashboard/costs

AI:

POST /api/ai/analyze
POST /api/ai/report
POST /api/ai/assistant

MAP:

GET /api/map/potholes
GET /api/map/nearby

Create automatic OpenAPI documentation.

---

# 48. BACKEND STRUCTURE

Use:

backend/

    app/

        main.py

        core/
            config.py
            security.py

        db/
            database.py
            models.py
            migrations/

        api/
            auth.py
            reports.py
            potholes.py
            repairs.py
            dashboard.py
            map.py
            ai.py

        schemas/
            user.py
            report.py
            pothole.py
            repair.py
            dashboard.py

        services/
            complaint_service.py
            cost_estimator.py
            priority.py
            duplicate_detector.py
            road_health.py

        ai/
            cv/
                detector.py
                segmenter.py
                severity.py
                area_estimator.py

            genai/
                llm_service.py
                prompt_manager.py
                report_generator.py
                assistant.py

            rag/
                embeddings.py
                retriever.py

        utils/
            logging.py
            file_validation.py

---

# 49. ML TRAINING PIPELINE

Create:

ml/

    data/

    training/

    evaluation/

    inference/

    notebooks/

Include:

- Dataset preparation
- Annotation guidance
- Train/validation split
- YOLO training
- Evaluation
- Model export
- Inference testing

Metrics:

Detection:

- Precision
- Recall
- mAP50
- mAP50-95

Segmentation:

- IoU
- Mask precision
- Mask recall

Do not claim good model performance unless the model has actually been trained and evaluated.

---

# 50. DEMO DATA

Create a database seed script.

Generate at least:

100 synthetic potholes

Multiple:

- Wards
- Roads
- Severity levels
- Statuses
- Repair teams
- Complaints
- Cost estimates

Use fake/demo data only.

Never include real people's personal information.

---

# 51. DEMO MODE

Environment variable:

DEMO_MODE=true

Demo mode should allow the complete application workflow without:

- trained YOLO model
- external LLM
- external notification service

When demo mode is active, clearly display:

"Demo Mode"

Do not falsely represent mock output as actual AI inference.

---

# 52. ERROR HANDLING

Handle:

- Invalid image
- No pothole detected
- Low AI confidence
- GPS unavailable
- Model unavailable
- Database unavailable
- LLM unavailable
- Invalid file
- File too large
- Unauthorized access
- Duplicate complaint
- Invalid repair status

Frontend should display clear messages.

Backend should return structured error responses.

---

# 53. LOGGING

Implement structured logging.

Log:

- API requests
- Errors
- AI inference
- Authentication events
- Repair changes
- Admin actions

Never log:

- Passwords
- JWT secrets
- API keys

---

# 54. AUDIT LOG

For government/admin actions record:

User
Action
Object
Old value
New value
Timestamp
IP if appropriate

Examples:

Official changed severity.

Admin changed cost rate.

Repair team marked repair completed.

---

# 55. TESTING

Create backend tests for:

- Registration
- Login
- Role authorization
- Image validation
- Cost calculation
- Severity calculation
- Priority calculation
- Duplicate detection
- Repair workflow
- Dashboard statistics

Test:

Citizen cannot access government APIs.

Government can manage potholes.

Repair team can only manage assigned repairs.

---

# 56. DOCKER

Create:

Dockerfile
docker-compose.yml

Services:

frontend
backend
postgres

Optional:

vector database

Use Docker Compose for local development.

---

# 57. ENVIRONMENT VARIABLES

Create:

.env.example

Include:

DATABASE_URL=
JWT_SECRET=
MODEL_PATH=
DEMO_MODE=true
LLM_API_KEY=
LLM_MODEL=
STORAGE_PATH=
CORS_ORIGINS=

Never put real credentials in source code.

---

# 58. README

Create a professional README.

Include:

1. Project overview
2. Problem statement
3. Solution
4. Features
5. Architecture
6. Technology stack
7. Folder structure
8. Database schema
9. Installation
10. Environment variables
11. Running frontend
12. Running backend
13. Docker setup
14. AI model setup
15. Training model
16. GenAI setup
17. API documentation
18. Demo mode
19. Testing
20. Limitations
21. Future scope

---

# 59. PROJECT DOCUMENTATION

Also create:

docs/

    architecture.md
    api.md
    database.md
    ai-pipeline.md
    genai.md
    deployment.md
    testing.md

---

# 60. LIMITATIONS

Clearly document:

1. RGB images do not provide reliable physical depth without additional information.
2. Cost estimates are preliminary.
3. AI detection can produce false positives/negatives.
4. Government engineering verification is still required.
5. GPS may be inaccurate.
6. Road repair recommendations are not a substitute for professional engineering inspection.
7. GenAI outputs must be treated as assistance rather than official decisions.

---

# 61. FUTURE FEATURES

Document future possibilities:

- Mobile application
- Dashcam-based continuous detection
- Drone road inspection
- IoT road sensors
- Traffic data integration
- Weather correlation
- Accident-risk prediction
- Predictive road maintenance
- Satellite imagery
- Advanced depth estimation
- Automatic government notification
- Multi-city deployment

---

# 62. FINAL USER EXPERIENCE

The complete demo should work like this:

## CITIZEN

Open website.

↓

Click:

"Report Pothole"

↓

Upload image.

↓

AI analyzes image.

↓

Display:

Pothole detected.

Confidence: 94%

Severity: HIGH

Estimated area: 3.4 m²

↓

GPS automatically obtained.

↓

Citizen confirms.

↓

Complaint generated:

RGA-2026-000001

↓

Pothole appears on public map.

---

## GOVERNMENT

Official logs in.

↓

Dashboard shows:

12,482 potholes

721 critical

2,841 pending

8,920 repaired

₹4.8 crore estimated repair budget

↓

Official opens pothole.

↓

Views:

Image
AI detection
Severity
Location
Reports
Estimated repair area
Cost
Priority

↓

Assigns repair team.

---

## REPAIR TEAM

Logs in.

↓

Sees assigned pothole.

↓

Travels to location.

↓

Uploads after-repair image.

↓

Enters actual cost.

↓

Marks:

COMPLETED

---

## AI

Compares:

Before vs After

↓

Generates:

Repair verification score.

---

## CITIZEN

Receives notification:

"Your reported pothole has been repaired."

↓

Views before/after images.

↓

Confirms:

YES

↓

Complaint:

CLOSED

---

# 63. GOVERNMENT GENAI DEMO

Government official asks:

"Which ward currently requires the highest repair budget?"

System should:

1. Query actual database.
2. Calculate values.
3. Send structured results to LLM.
4. Generate a natural-language explanation.

Example:

"Based on the current database, Ward 17 has the highest preliminary repair budget at ₹18.4 lakh, primarily due to 12 critical and 34 high-priority potholes."

The numerical values must come from the backend.

---

# 64. FRONTEND PAGES REQUIRED

Create at minimum:

Public:

index.html
login.html
register.html
report.html
map.html
complaints.html
complaint-details.html
profile.html
notifications.html

Government:

government/dashboard.html
government/potholes.html
government/pothole-details.html
government/repairs.html
government/analytics.html
government/users.html
government/cost-rates.html

Repair Team:

repair-team/dashboard.html
repair-team/assignments.html
repair-team/repair-details.html

---

# 65. UI COMPONENTS

Build reusable Bootstrap-based components:

Navbar
Sidebar
Footer
Stat cards
Data tables
Filters
Search
Map container
Modal
Toast
Loading spinner
AI result card
Severity badge
Status badge
Cost card
Repair timeline
Notification dropdown

Use JavaScript modules rather than duplicating large amounts of code.

---

# 66. PERFORMANCE

Optimize:

- Image upload size
- API calls
- Database queries
- Map markers
- Dashboard queries

Use pagination for large tables.

Use map clustering for many potholes.

Do not load thousands of records into the browser unnecessarily.

---

# 67. ACCESSIBILITY

Implement:

- Semantic HTML
- Proper labels
- Keyboard navigation
- Accessible buttons
- Alt text
- Good contrast
- Responsive layout

---

# 68. RESPONSIVENESS

The citizen portal must work on:

- Desktop
- Laptop
- Tablet
- Mobile

Government dashboard should prioritize desktop but remain responsive.

---

# 69. FINAL ACCEPTANCE CRITERIA

The application is complete only when all of these work:

[ ] Citizen registration

[ ] Citizen login

[ ] Government login

[ ] Repair team login

[ ] Role-based access

[ ] Image upload

[ ] Image validation

[ ] AI pothole detection

[ ] Detection confidence

[ ] Bounding box

[ ] Segmentation support

[ ] Severity score

[ ] Estimated area

[ ] GPS capture

[ ] Manual map location

[ ] Duplicate detection

[ ] Automatic complaint ID

[ ] Complaint tracking

[ ] Public pothole map

[ ] Government map

[ ] Government dashboard

[ ] Government analytics

[ ] Priority scoring

[ ] Road health score

[ ] Repair area calculation

[ ] Cost estimation

[ ] Cost-rate management

[ ] Repair assignment

[ ] Repair team dashboard

[ ] Repair progress

[ ] Before/after images

[ ] AI repair verification

[ ] Citizen repair verification

[ ] Notifications

[ ] GenAI repair report

[ ] GenAI government assistant

[ ] Optional RAG

[ ] Audit logs

[ ] Error handling

[ ] Tests

[ ] Docker

[ ] README

[ ] API documentation

[ ] Demo mode

---

# 70. MOST IMPORTANT RULE

Do not sacrifice correctness for appearance.

The system should clearly distinguish:

REAL AI MODEL
DEMO/MOCK AI
ESTIMATION
ACTUAL COST
AI RECOMMENDATION
OFFICIAL GOVERNMENT DECISION

Never fabricate AI accuracy, engineering measurements, government data, repair costs, or official approval.

---

# 71. START NOW

First provide:

1. High-level architecture
2. Detailed component architecture
3. Database ER diagram in Mermaid
4. Complete folder structure
5. API endpoint specification
6. Frontend page/navigation structure
7. AI/CV pipeline
8. GenAI pipeline
9. Cost estimation pipeline
10. Development phases
11. Dependencies
12. Environment variables

Then start implementing:

## PHASE 1

Build:

- Project structure
- FastAPI backend
- PostgreSQL database configuration
- Database models
- Authentication
- JWT
- Role-based access
- Basic HTML/CSS/JavaScript frontend
- Bootstrap integration
- Login
- Registration
- Dashboard routing

After PHASE 1 is implemented and tested, continue to PHASE 2.

Do not skip testing.

Do not generate unrelated features before the current phase works.

The final project name must be:

# ROADGUARD AI

### Detect. Report. Prioritize. Repair.