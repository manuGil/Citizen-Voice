# AI Context - CitizenVoice Project

This file provides comprehensive context about the CitizenVoice codebase for AI assistants working on this project.

## Project Overview

**CitizenVoice** is an inclusive, web-based software platform for collaborative data collection that facilitates citizen participation in urban planning and design. The platform enables communities to create surveys, collect geo-spatial and non-geo-spatial data, and visualize community insights.

### Main Features
- **Citizen Mapping (maptool)**: Tool to create questionnaires and collect geo-spatial and non-geo-spatial data about citizens' perceptions of their urban environment
- **Community Dashboard (cv-portal)**: Dashboard to visualize geo-spatial data collected through the Citizen Mapping tool, allowing insights into community concerns and priorities
- **RESTful APIs**: Voice API (v3) and Civilian API (v1) for integration with other applications

## Architecture

CitizenVoice is a **multi-service platform** with three main components:

### 1. Django Backend API (`citizenvoice/`)

**Technology Stack:**
- Django 4.0.6+
- Django REST Framework
- PostgreSQL with PostGIS extension
- GDAL 3.3.2+ (for spatial data processing)
- Python 3.10+

**Main Django Apps:**
- `voice/` - Core survey and response management (Voice API v3)
  - Handles surveys, questions, responses, and spatial data
  - Primary API for survey creation and management
- `civilian/` - Dashboard data API (Civilian API v1)
  - Provides GeoJSON data for visualization
  - Used by Community Dashboard
- `authentication/` - User authentication with social login (Google, GitHub OAuth)
- `survey_design/` - Survey creation interface (legacy)
- `respondent/` - Survey response handling
- `users/` - User management

**Key API Endpoints:**
- Voice API: `/voice/v3/` (surveys, questions, responses, spatial data)
- Civilian API: `/civilian/v1/` (dashboard data with GeoJSON)
- Admin: `/api/admin/`
- Health check: `/health/`
- Authentication: `/api/auth/`

**API Documentation:**
- Voice API schema: `/voice/v3/schema/`
- Voice API docs: `/voice/v3/schema/redoc/`
- Civilian API schema: `/civilian/v1/schema/`
- Civilian API docs: `/civilian/v1/schema/redoc/`

### 2. Maptool Frontend (`maptool/`)

**Purpose:** Citizen mapping tool for survey creation and response collection

**Technology Stack:**
- Nuxt 3
- Vue 3
- Leaflet maps
- Vuetify UI
- TailwindCSS
- Node.js with Yarn

**Key Features:**
- Interactive mapping with drawing tools
- Survey forms and question types
- Geo-spatial data collection (points, lines, polygons)
- Survey creation and management interface

**API Integration:**
- Connects to Voice API (`/voice/v3/`) for survey management
- Authentication via `/api/auth/`
- Environment variable: `NUXT_API_PARTY_ENDPOINTS_CMS_API_URL`
- Runs on port 3000 (development)

**Key Directories:**
- `components/` - Vue components including question blocks and map views
- `pages/` - Application pages (design, survey, login, etc.)
- `stores/` - State management
- `middleware/` - Authorization and validation middleware

### 3. CV-Portal Frontend (`cv-portal/`)

**Purpose:** Community dashboard for visualizing collected data

**Technology Stack:**
- Nuxt 3
- Vue 3
- Leaflet maps
- TailwindCSS
- Node.js with Yarn

**Key Features:**
- Data visualization
- GeoJSON mapping
- Community insights
- Topic-based filtering

**API Integration:**
- Connects to Civilian API (`/civilian/v1/`) for spatial data
- Environment variable: `NUXT_API_PARTY_ENDPOINTS_CMS_API_V1_URL`
- Runs on port 4000 (development)

## Development Commands

### Django Backend

**Virtual Environment:**
```bash
conda activate pygdal
```

**Common Commands:**
```bash
cd citizenvoice
python manage.py runserver          # Start development server
python manage.py migrate            # Run database migrations
python manage.py test               # Run tests
python manage.py createsuperuser    # Create admin user
python manage.py loaddata civilian-db.json  # Load sample data
```

**Local Development Setup:**
- Create `local.env` file for Django settings
- Uncomment dotenv loading in `settings.py` (lines 34-36)
- Requires PostgreSQL with PostGIS extension
- Requires GDAL 3.3.2+ installed

### Frontend Applications

**Maptool (Citizen Mapping):**
```bash
cd maptool
yarn install    # Install dependencies
yarn dev        # Start dev server (port 3000)
yarn build      # Build for production
yarn lint       # Lint code
```

**CV-Portal (Community Dashboard):**
```bash
cd cv-portal
yarn install    # Install dependencies
yarn dev        # Start dev server (port 4000)
yarn build      # Build for production
```

### Docker Environment

**Full Stack:**
```bash
docker compose --env-file .env up --build
```

**Development with File Watching:**
```bash
docker compose --env-file .env up --build --watch
```

**Docker Services:**
- `postgis_db` - PostgreSQL with PostGIS (port 5432)
- `api` - Django application (port 8000)
- `maptool` - Citizen Mapping app (internal port 3000)
- `cvportal` - Community Dashboard (internal port 4000)
- `nginx` - Reverse proxy (port 80)

**Access:**
- Full stack via Nginx: http://localhost
- Direct API access: http://localhost:8000
- Maptool direct: http://localhost:3000 (if exposed)
- CV-Portal direct: http://localhost:4000 (if exposed)

## Environment Setup

### Docker (Recommended)

**Required Files:**
1. `.env` file with:
   - Database settings (POSTGRES_USER, POSTGRES_DBASE, POSTGRES_PORT)
   - Django settings (DJANGO_DEBUG, DJANGO_ALLOWED_HOSTS, DJANGO_DB_ENGINE)
2. `secrets/` directory with:
   - `postgres_password.txt` - Database password
   - `django_token.txt` - Django SECRET_KEY

**Start Services:**
```bash
docker compose --env-file .env up --build
```

### Local Development

**Backend Requirements:**
- Python 3.10+
- PostgreSQL with PostGIS extension
- GDAL 3.3.2+
- Conda environment `pygdal` (or equivalent virtual environment)

**Frontend Requirements:**
- Node.js
- Yarn package manager

**Setup Steps:**
1. Install PostgreSQL with PostGIS
2. Install GDAL (version 3.3.2+)
3. Create `local.env` for Django settings
4. Uncomment dotenv loading in `citizenvoice/citizenvoice/settings.py`
5. Run migrations: `python manage.py migrate`
6. Install frontend dependencies: `yarn install` in `maptool/` and `cv-portal/`

## Database & Spatial Data

**Database:**
- PostgreSQL with PostGIS extension
- Spatial reference system: WGS84
- Sample data: `citizenvoice/civilian-db.json`

**Spatial Data:**
- Survey responses include GeoJSON geometries
- Supported geometry types: Points, Lines, Polygons
- Stored in PostGIS-enabled PostgreSQL database
- Coordinates in WGS84 (EPSG:4326)

**Database Models:**
- Located in app-specific `models/` directories
- Voice app models: surveys, questions, responses, spatial data
- Civilian app models: dashboard data structures

## File Structure

```
Citizen-Voice/
├── citizenvoice/          # Django backend
│   ├── voice/            # Voice API v3
│   ├── civilian/         # Civilian API v1
│   ├── authentication/    # Auth with OAuth
│   ├── survey_design/    # Legacy survey creation
│   ├── respondent/       # Response handling
│   ├── users/            # User management
│   ├── tests/            # Test suite
│   └── manage.py
├── maptool/              # Citizen Mapping frontend
│   ├── components/       # Vue components
│   ├── pages/            # Application pages
│   ├── stores/           # State management
│   └── middleware/       # Auth & validation
├── cv-portal/            # Community Dashboard frontend
│   ├── components/       # Vue components
│   ├── pages/            # Dashboard pages
│   └── layouts/         # Layout components
├── docs/                 # Documentation (Sphinx)
├── docker-compose.yaml   # Docker configuration
├── nginx.conf            # Nginx reverse proxy config
└── secrets/              # Secret files (gitignored)
```

## Testing

**Django Tests:**
```bash
cd citizenvoice
python manage.py test
```

**Test Locations:**
- Each app's `tests.py` file
- Main `citizenvoice/tests/` directory
- Test files: `test_api_methods.py`, `test_api_models.py`

**Frontend Testing:**
- Not currently configured

## Development Notes

**Version Control:**
- Main development branch: `devel`
- Production deployments use nginx reverse proxy

**Authentication:**
- OAuth integration with Google and GitHub
- Requires setup of OAuth credentials
- Secrets stored in `secrets/` directory

**File Uploads:**
- Handled through Django media system
- Media files stored in `citizenvoice/media/`
- Survey answers may include file uploads

**CORS:**
- CORS headers configured for cross-origin API access
- Configured in Django settings

**API Standards:**
- RESTful APIs following OpenAPI specification
- API documentation auto-generated from schemas
- Versioned APIs (v3 for Voice, v1 for Civilian)

**Spatial Data Processing:**
- GDAL required for spatial operations
- PostGIS extension for spatial database queries
- GeoJSON format for API responses

## Common Workflows

**Adding a New Feature:**
1. Backend: Add models in appropriate app, create migrations, update serializers/views
2. Frontend: Add components/pages, update stores if needed, connect to API
3. Test: Write tests for backend, manually test frontend
4. Document: Update API docs if endpoints changed

**Debugging:**
- Backend: Check Django logs, use Django debug toolbar if enabled
- Frontend: Use browser dev tools, check Nuxt dev server logs
- Docker: Use `docker compose logs [service]` to view logs

**Database Changes:**
1. Modify models in Django app
2. Create migration: `python manage.py makemigrations`
3. Apply migration: `python manage.py migrate`
4. Update serializers if API models changed

## Important Files Reference

- `CLAUDE.md` - Original Claude Code context (similar to this file)
- `README.md` - Project overview and citation
- `docker-compose.yaml` - Docker service configuration
- `nginx.conf` - Reverse proxy configuration
- `citizenvoice/citizenvoice/settings.py` - Django settings
- `citizenvoice/civilian-db.json` - Sample database fixture
- `maptool/nuxt.config.js` - Maptool Nuxt configuration
- `cv-portal/nuxt.config.ts` - CV-Portal Nuxt configuration

## License

GPL v3 - See LICENSE file for details.

## Citation

If using this software, cite:
*Goncalves, J. E., Forgaci, C., Verma, T., van der Laarse, G., Ijpma, J., Aslan, Y., Ioannou, I., & Garcia Alvarez, M. Citizen Voice [Computer software]*

