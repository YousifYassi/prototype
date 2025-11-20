# Jurisdiction & Industry-Specific Safety Monitoring Implementation

## Overview

This implementation adds comprehensive support for jurisdiction-based regulations and industry-specific safety standards with a hybrid model approach and severity weighting system.

## Features Implemented

### 1. Database Schema
- **Jurisdiction**: Store regulatory jurisdictions (e.g., Ontario, Canada)
- **Industry**: Define industry types (food safety, construction, light industry)
- **Project**: Organize cameras/videos by jurisdiction and industry
- **JurisdictionRegulation**: Map regulations to specific violations
- **ActionSeverity**: Define severity levels (1-5) for each unsafe action
- **ProjectActionSeverity**: Allow custom severity overrides per project
- **Stream**: Persist live stream configurations to database

### 2. Backend Implementation

#### Model Registry System (`backend/model_registry.py`)
- Intelligent model loading with fallback logic
- Priority order:
  1. Custom model path (project-specific)
  2. Jurisdiction + Industry model (`ontario_food_safety_model.pth`)
  3. Industry-only model (`industry_food_safety_model.pth`)
  4. Jurisdiction-only model (`jurisdiction_ontario_model.pth`)
  5. Generic fallback model (`best_model.pth`)

#### API Endpoints
**Jurisdiction & Industry:**
- `GET /jurisdictions` - List available jurisdictions
- `GET /industries` - List available industries
- `GET /jurisdictions/{id}/regulations` - Get applicable regulations

**Project Management:**
- `POST /projects` - Create project
- `GET /projects` - List user's projects
- `GET /projects/{id}` - Get project details with severity levels
- `PUT /projects/{id}` - Update project settings
- `DELETE /projects/{id}` - Delete project
- `PUT /projects/{id}/action-severity` - Update custom severity levels

**Enhanced Endpoints:**
- `POST /videos/upload` - Now accepts optional `project_id`
- `POST /streams` - Now requires `project_id`

#### Enhanced Detection (`inference.py`)
- Severity-based alert filtering
- Regulation violation details in alerts
- Project-specific model loading
- Configurable minimum severity threshold

### 3. Frontend Implementation

#### New Pages
**ProjectListPage** (`/projects`)
- Grid view of all projects
- Shows jurisdiction, industry, camera/video counts
- Severity badge display

**ProjectCreatePage** (`/projects/new`)
- Form to create new projects
- Jurisdiction and industry selectors
- Minimum severity threshold configuration

**ProjectDetailsPage** (`/projects/{id}`)
- Tabs: Overview, Regulations, Settings
- Action severity levels with color coding
- Regulation references with links
- Project statistics

#### Updated Pages
- **VideoUploadPage**: Added optional project selector
- **LiveStreamPage**: Added required project selector
- **Layout**: Added "Projects" navigation link

### 4. Configuration

#### Updated `config.yaml`
```yaml
jurisdiction_industry_actions:
  ontario_food_safety:
    - "no_hair_net"
    - "no_gloves"
    - "cross_contamination"
    - "improper_temperature_handling"
  
  ontario_construction:
    - "no_hard_hat"
    - "no_safety_harness"
    - "unsafe_scaffolding"
    - "no_high_visibility_vest"
  
  ontario_light_industry:
    - "no_safety_glasses"
    - "loose_clothing_near_machinery"
    - "improper_lifting"
```

### 5. Severity System

**Severity Levels:**
1. **Low** (1) - Minor violations, informational
2. **Medium** (2) - Moderate risk violations
3. **High** (3) - Significant safety concerns
4. **Critical** (4) - Serious violations requiring immediate attention
5. **Emergency** (5) - Life-threatening situations

**Severity Configuration:**
- Default severities defined per jurisdiction/industry
- Projects can set minimum severity threshold for alerts
- Custom severity overrides available per project
- Notification priority based on severity level

**Alert Enhancements:**
- Alerts include severity level and label
- Regulation violation codes included
- Filtering based on minimum severity threshold
- Severity-based color coding in UI

### 6. Regulation Data

#### Ontario Regulations Seeded
Based on Ontario Occupational Health and Safety Act (OHSA):

**Food Safety:**
- OHSA_25(2)(h): Personal protective equipment requirements
- OHSA_26(1): Cross-contamination prevention

**Construction:**
- OHSA_26.1(1): Head protection requirements
- OHSA_26.1(2): Fall protection equipment
- OHSA_26.1(3): High visibility clothing

**Light Industry:**
- OHSA_25(1)(a): Eye protection requirements
- OHSA_25(1)(c): Clothing around machinery
- OHSA_25(2)(d): Manual handling and lifting

## Setup Instructions

### 1. Run Database Migration
```bash
python backend/migrations/add_jurisdiction_industry.py
```

This creates new tables and migrates existing data to a default project.

### 2. Seed Regulation Data
```bash
python backend/seed_regulations.py
```

This populates:
- Jurisdictions (Ontario, Generic)
- Industries (Food Safety, Construction, Light Industry, General)
- Regulations for each jurisdiction/industry combination
- Default severity levels for unsafe actions

### 3. Restart Backend
```bash
python backend/start_backend.py
```

### 4. Frontend (if needed)
```bash
cd frontend
npm install  # If new dependencies were added
npm run dev
```

## Usage Workflow

### For Users

1. **Create a Project**
   - Navigate to Projects → New Project
   - Enter project name (e.g., "Main Restaurant Kitchen")
   - Select jurisdiction (e.g., Ontario)
   - Select industry (e.g., Food Safety)
   - Set minimum severity level for alerts
   - Click "Create Project"

2. **Upload Videos**
   - Go to Upload Video
   - Select project from dropdown (optional but recommended)
   - Upload video file
   - System applies project-specific rules and severity filtering

3. **Add Live Streams**
   - Go to Live Streams → Add New Stream
   - Enter stream details
   - **Select project** (required)
   - System monitors with jurisdiction-specific detection

4. **View Project Details**
   - Navigate to Projects → Select project
   - View action severity levels
   - Check applicable regulations
   - Adjust settings as needed

### For Administrators

1. **Add New Jurisdictions**
   - Update `backend/seed_regulations.py`
   - Add new jurisdiction entry
   - Define regulations for that jurisdiction
   - Run seeding script

2. **Add New Industries**
   - Update `backend/seed_regulations.py`
   - Add new industry with hazard categories
   - Define severity levels for actions
   - Run seeding script

3. **Train Specialized Models**
   - Collect jurisdiction/industry-specific training data
   - Train model using existing training pipeline
   - Save as: `checkpoints/{jurisdiction}_{industry}_model.pth`
   - System automatically uses specialized model

## Benefits

1. **Compliance**: Ensures monitoring aligns with local regulations
2. **Accuracy**: Industry-specific models reduce false positives
3. **Prioritization**: Severity system helps focus on critical issues
4. **Scalability**: Easy to add new jurisdictions and industries
5. **Flexibility**: Custom severity overrides per project
6. **Traceability**: Regulation violation codes for documentation

## Future Enhancements

1. **Real-time Regulation Updates**: API integration with regulatory databases
2. **Multi-language Support**: Regulation descriptions in multiple languages
3. **Custom Action Definitions**: Allow users to define custom unsafe actions
4. **Reporting**: Generate compliance reports with regulation references
5. **Model Training Pipeline**: Automated training for new jurisdiction/industry combinations
6. **Notification Channels**: Severity-based routing to different alert channels

## Technical Notes

- Backward compatible: Existing videos without projects use generic model
- Database migration preserves all existing data
- Frontend gracefully handles missing projects (optional selection)
- Model registry caches loaded models for performance
- Severity filtering happens before alert cooldown check
- Regulation mappings stored as JSON for flexibility

## API Examples

### Create a Project
```bash
curl -X POST http://localhost:8000/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Downtown Restaurant",
    "jurisdiction_id": 1,
    "industry_id": 1,
    "min_severity_alert": 3
  }'
```

### Get Project with Severities
```bash
curl http://localhost:8000/projects/1 \
  -H "Authorization: Bearer $TOKEN"
```

### Update Action Severity
```bash
curl -X PUT http://localhost:8000/projects/1/action-severity \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action_name": "no_hair_net",
    "custom_severity_level": 4
  }'
```

## Support

For questions or issues:
1. Check regulation URLs in project details
2. Review logs in `logs/training.log`
3. Verify model files in `checkpoints/` directory
4. Check database with: `sqlite3 backend/workplace_safety.db`

## License

This implementation follows the same license as the main application.

