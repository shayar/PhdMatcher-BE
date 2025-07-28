# PhD Advisor Matching Platform - Backend

AI-powered PhD Advisor Matching Platform backend built with FastAPI, providing intelligent matching between master's students and potential PhD advisors using semantic analysis and machine learning.

## 🚀 Features

- **JWT Authentication**: Secure user registration and login
- **Profile Management**: User profiles with research interests and resume upload
- **AI-Powered Matching**: Semantic similarity matching using Sentence-BERT
- **Professor Database**: Integration with OpenAlex API for ethical data sourcing
- **Advanced Search**: Natural language search with filtering capabilities
- **Vector Database**: FAISS for efficient similarity search
- **File Processing**: PDF and DOCX resume parsing
- **Scalable Architecture**: Microservices-ready design with Redis caching

## 🛠️ Technology Stack

- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Caching**: Redis
- **AI/ML**: Sentence-Transformers, FAISS
- **File Storage**: AWS S3
- **Authentication**: JWT with python-jose
- **Testing**: Pytest
- **API Documentation**: OpenAPI/Swagger

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- AWS Account (for S3 storage)

## 🔧 Installation

### Using Docker (Recommended)

1. **Clone the repository**

   ```bash
   git clone https://github.com/shayar/PhdMatcher-BE.git
   cd PhdMatcher-BE
   ```

2. **Copy environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run with Docker Compose**

   ```bash
   docker-compose -f docker/docker-compose.yml up -d
   ```

4. **Initialize the database**
   ```bash
   docker-compose -f docker/docker-compose.yml exec backend python scripts/init_db.py
   ```

### Manual Installation

1. **Clone and setup virtual environment**

   ```bash
   git clone https://github.com/shayar/PhdMatcher-BE.git
   cd PhdMatcher-BE
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Setup database**

   ```bash
   # Start PostgreSQL and Redis
   # Then run:
   python scripts/init_db.py
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

## 🔑 Environment Configuration

Key environment variables to configure:

```env
# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=phd_advisor_matching

# Security
SECRET_KEY=your-secret-key-here

# AWS S3
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
S3_BUCKET_NAME=your-bucket-name

# OpenAlex API
OPENALEX_API_EMAIL=your-email@example.com
```

## 🚀 Usage

### API Documentation

Once running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Core Endpoints

- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/users/me` - Get current user profile
- `POST /api/v1/users/upload-resume` - Upload resume
- `POST /api/v1/search/` - Search professors
- `GET /api/v1/matching/me` - Find matches for current user

### Loading Professor Data

```bash
# Load professors from a specific institution (using ROR ID)
python scripts/load_professors.py 00f54p054  # Stanford University

# Build FAISS index after loading data
python scripts/build_faiss_index.py
```

## 🧪 Testing

### Run Tests with Docker

```bash
# Run all tests
docker-compose -f docker/docker-compose.yml run test

# Run specific test file
docker-compose -f docker/docker-compose.yml run test pytest tests/test_auth.py -v
```

### Run Tests Manually

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific tests
pytest tests/test_auth.py::test_login_success -v
```

### Test Structure

```
tests/
├── conftest.py              # Test configuration and fixtures
├── test_auth.py            # Authentication tests
├── test_users.py           # User management tests
├── test_matching.py        # Matching algorithm tests
├── test_services/          # Service layer tests
└── test_utils/             # Utility function tests
```

## 📊 Database Schema

### Core Tables

- **users**: User profiles and authentication
- **professors**: Professor data from OpenAlex
- **institutions**: University/institution information

### Key Relationships

```sql
users (1) -> (*) user_matches
professors (*) -> (1) institutions
professors (1) -> (*) professor_concepts
```

## 🔍 AI/ML Pipeline

### Embedding Generation

1. **Text Processing**: Extract text from resumes and research profiles
2. **Embedding**: Use Sentence-BERT to generate 384-dimensional vectors
3. **Storage**: Store embeddings in database and FAISS index

### Matching Algorithm

1. **User Embedding**: Combine resume text and research interests
2. **Similarity Search**: Use FAISS for efficient vector similarity search
3. **Filtering**: Apply location, university, and other filters
4. **Ranking**: Sort by similarity score and additional metrics

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**

   ```bash
   export ENVIRONMENT=production
   export DEBUG=false
   ```

2. **Database Migration**

   ```bash
   alembic upgrade head
   ```

3. **Run with Gunicorn**
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### AWS Deployment Options

- **EC2**: Use the provided Docker configuration
- **ECS**: Deploy using AWS Elastic Container Service
- **Lambda**: Serverless deployment with Mangum adapter

## 📈 Performance Optimization

### Caching Strategy

- **Redis**: API response caching, session storage
- **FAISS**: In-memory vector search for fast similarity matching
- **Database**: Connection pooling and query optimization

### Monitoring

- **Health Checks**: `/health` endpoint for load balancer monitoring
- **Logging**: Structured logging with correlation IDs
- **Metrics**: Built-in FastAPI metrics and custom business metrics

## 🔒 Security

- **Authentication**: JWT tokens with secure secret key
- **Input Validation**: Pydantic models for request validation
- **CORS**: Configurable cross-origin resource sharing
- **Rate Limiting**: Built-in request rate limiting
- **File Upload**: Secure file validation and S3 storage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run code formatting
black app/ tests/
isort app/ tests/

# Run linting
flake8 app/ tests/
mypy app/
```

## 📝 API Examples

### User Registration

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "student@example.com",
       "password": "securepassword",
       "full_name": "John Doe"
     }'
```

### Upload Resume

```bash
curl -X POST "http://localhost:8000/api/v1/users/upload-resume" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@resume.pdf"
```

### Search Professors

```bash
curl -X POST "http://localhost:8000/api/v1/search/" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "machine learning at Stanford",
       "filters": {
         "university": "Stanford",
         "min_works_count": 10
       },
       "limit": 20
     }'
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAlex API Documentation](https://docs.openalex.org/)
- [Sentence-Transformers Documentation](https://www.sbert.net/)
- [FAISS Documentation](https://faiss.ai/)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Issues and Support

- **Bug Reports**: [GitHub Issues](https://github.com/shayar/PhdMatcher-BE/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/shayar/PhdMatcher-BE/discussions)
- **Email**: shayarshrestha7@gmail.com

---

Made with ❤️ for the academic community
