# Auto Lead Generation CRM - Backend API

A comprehensive FastAPI backend for the Auto Lead Generation SMART BDM CRM system.

## Features

- **User Management & RBAC**: Role-based access control with Admin, Sales Coordinator, Reviewer, and BDM roles
- **Product & Campaign Management**: CRUD operations for products, keywords, and campaigns
- **Automated Lead Generation**: Integration with DuckDuckGo, OpenCorporates, and Google Places APIs
- **Lead Management**: Auto leads and final leads with approval workflow
- **AI-Powered Relevance Scoring**: Using sentence-transformers and spaCy for semantic matching
- **Activity Logging**: Comprehensive audit trail for all user actions
- **Reports & Analytics**: Dashboard statistics and performance metrics
- **CSV Export**: Export leads and reports to CSV format
- **Email Notifications**: SMTP integration for lead notifications

## Tech Stack

- **Framework**: FastAPI
- **Database**: MySQL 8.0
- **ORM**: SQLAlchemy
- **Authentication**: JWT with Bearer tokens
- **AI/NLP**: sentence-transformers, spaCy
- **Task Queue**: Celery + Redis
- **Web Scraping**: BeautifulSoup, Requests
- **Data Export**: pandas

## Quick Start

### Using Docker (Recommended)

1. Clone the repository and navigate to backend directory:
```bash
cd backend
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Update `.env` with your configuration:
```bash
# Database will be auto-configured with Docker
# Add your external API keys:
OPENCORPORATES_API_KEY=your_key_here
GOOGLE_MAPS_API_KEY=your_key_here
HUNTER_API_KEY=your_key_here

# Email configuration (optional)
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

4. Start all services:
```bash
docker-compose up -d
```

5. The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **MySQL**: localhost:3306
- **Redis**: localhost:6379

### Manual Installation

1. Install Python 3.11+ and MySQL 8.0

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

4. Set up MySQL database:
```bash
mysql -u root -p < database/init.sql
```

5. Configure environment:
```bash
cp .env.example .env
# Edit .env with your database and API credentials
```

6. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user info

### Users
- `GET /api/users/` - List all users (Admin only)
- `POST /api/users/` - Create user (Admin only)
- `GET /api/users/{user_id}` - Get user details
- `PUT /api/users/{user_id}` - Update user
- `DELETE /api/users/{user_id}` - Delete user (Admin only)

### Products
- `GET /api/products/` - List products
- `POST /api/products/` - Create product (Admin only)
- `GET /api/products/{product_id}` - Get product details
- `PUT /api/products/{product_id}` - Update product (Admin only)
- `DELETE /api/products/{product_id}` - Delete product (Admin only)

### Campaigns
- `GET /api/campaigns/` - List campaigns
- `POST /api/campaigns/` - Create campaign
- `GET /api/campaigns/{campaign_id}` - Get campaign details
- `PUT /api/campaigns/{campaign_id}` - Update campaign
- `POST /api/campaigns/{campaign_id}/run` - Run campaign to generate leads

### Leads
- `GET /api/leads/auto` - List auto-generated leads
- `POST /api/leads/auto` - Create auto lead
- `PUT /api/leads/auto/{lead_id}/finalize` - Move auto leads to final
- `GET /api/leads/final` - List final leads
- `POST /api/leads/final` - Create final lead
- `PUT /api/leads/final/{lead_id}` - Update final lead
- `DELETE /api/leads/final/{lead_id}` - Delete final lead
- `GET /api/leads/export` - Export leads to CSV

### Lead Management
- `GET /api/lead-tags/` - List lead tags
- `POST /api/lead-tags/` - Create lead tag
- `POST /api/lead-tags/assign` - Assign tag to lead
- `GET /api/lead-notes/` - List lead notes
- `POST /api/lead-notes/` - Create lead note

### Reports & Analytics
- `GET /api/reports/dashboard-stats` - Dashboard statistics
- `GET /api/reports/leads-by-region` - Leads by region
- `GET /api/reports/top-products` - Top performing products
- `GET /api/reports/conversion-funnel` - Conversion funnel data
- `GET /api/reports/campaign-performance` - Campaign performance metrics

### Activity Logs
- `GET /api/activity-logs/` - List activity logs
- `GET /api/activity-logs/recent` - Recent system activity (Admin only)

## Default Credentials

- **Email**: admin@smartcrm.com
- **Password**: admin123
- **Role**: Admin

## External API Integration

### DuckDuckGo Search
- No API key required
- Rate limited to reasonable usage
- Used for basic company searches

### OpenCorporates API
1. Sign up at https://opencorporates.com/api_accounts/new
2. Get your API token
3. Add to `.env`: `OPENCORPORATES_API_KEY=your_token`
4. Free tier: 500 calls/month

### Google Maps Places API
1. Create project in Google Cloud Console
2. Enable Places API
3. Create API key with restrictions
4. Add to `.env`: `GOOGLE_MAPS_API_KEY=your_key`
5. Free tier: $200 credit/month

### Hunter.io Email Finder
1. Sign up at https://hunter.io/
2. Get API key from dashboard
3. Add to `.env`: `HUNTER_API_KEY=your_key`
4. Free tier: 25 requests/month

## Lead Generation Process

1. **Campaign Creation**: Define product, region, and keywords
2. **Automated Search**: System searches multiple sources (DuckDuckGo, OpenCorporates, Google Places)
3. **AI Scoring**: Relevance scoring using keyword matching and semantic similarity
4. **Data Enrichment**: Extract company information and contact details
5. **Review Process**: Sales team reviews and approves high-quality leads
6. **Final Processing**: Approved leads moved to final leads for outreach

## Database Schema

The system uses MySQL with the following main tables:
- `users` - User accounts and roles
- `products` - Product/service definitions
- `regions` - Geographic targeting regions
- `campaigns` - Lead generation campaigns
- `auto_leads` - Generated leads from campaigns
- `final_leads` - Approved leads ready for outreach
- `lead_tags` - Tagging system for categorization
- `lead_notes` - Communication history
- `activity_logs` - Audit trail

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black app/
isort app/
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## Deployment

### Production Setup
1. Use environment variables for all configuration
2. Set up SSL/TLS certificates
3. Configure reverse proxy (nginx)
4. Set up monitoring and logging
5. Configure backup strategy for MySQL

### Environment Variables
```bash
DATABASE_URL=mysql+pymysql://user:pass@host:port/db
SECRET_KEY=your-secret-key
OPENCORPORATES_API_KEY=your-key
GOOGLE_MAPS_API_KEY=your-key
SMTP_USERNAME=your-email
SMTP_PASSWORD=your-password
```

## Monitoring & Logging

- Application logs are written to stdout
- Database queries can be logged by setting `DEBUG=True`
- Activity logs are stored in the database
- Health check endpoint: `/health`

## Security Features

- JWT-based authentication
- Role-based access control (RBAC)
- Password hashing with bcrypt
- SQL injection prevention with SQLAlchemy ORM
- CORS configuration
- Input validation with Pydantic

## Performance Optimization

- Database indexing on frequently queried columns
- Connection pooling with SQLAlchemy
- Background task processing with Celery
- Caching with Redis
- Pagination for large datasets

## Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the logs for error details
3. Ensure all environment variables are configured
4. Verify database connectivity and migrations

## License

This project is licensed under the MIT License.