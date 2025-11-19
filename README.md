# CodeGuard AI

AI-powered Codebase Vulnerability Scanner, Reviewer, and Auto-Commenter using RAG (Retrieval-Augmented Generation).

## Features

- **Vulnerability Scanning**: Detect OWASP Top 10, CWE patterns, insecure functions, hardcoded secrets, weak crypto, SQL injection, XSS, RCE, and more
- **Code Review**: AI-powered suggestions for performance, readability, idioms, refactoring, and design patterns
- **Auto-Commenting**: Automatically add inline comments explaining complex logic and edge cases
- **RAG-Powered**: Uses Retrieval-Augmented Generation for context-aware analysis
- **Multi-Language Support**: Python, JavaScript, TypeScript, Java, Go, Rust, C/C++, PHP, Ruby, and more
- **Interactive Dashboard**: React-based web interface with Monaco Editor for code viewing
- **CLI Tool**: Command-line interface for quick scans

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React + TypeScript + Tailwind CSS + Monaco Editor
- **RAG**: LangChain + Qdrant + Sentence Transformers
- **LLM**: Ollama (local) + OpenAI (fallback)
- **Database**: PostgreSQL (SQLModel)
- **Vector DB**: Qdrant
- **Infrastructure**: Terraform → AWS (ECS, RDS, ALB, S3, ECR)
- **CI/CD**: GitHub Actions

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- PostgreSQL 15+
- Qdrant (via Docker)

### Local Setup with Docker Compose

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/codeguard-ai.git
   cd codeguard-ai
   ```

2. **Create environment file**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start services**:
   ```bash
   docker-compose up -d
   ```

4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Manual Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install frontend dependencies**:
   ```bash
   cd frontend
   npm install
   ```

3. **Start PostgreSQL and Qdrant**:
   ```bash
   docker-compose up -d postgres qdrant
   ```

4. **Run database migrations**:
   ```bash
   # Initialize database (creates tables)
   python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"
   ```

5. **Start backend**:
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Start frontend** (in another terminal):
   ```bash
   cd frontend
   npm run dev
   ```

## Usage

### CLI

Scan a repository:
```bash
codeguard scan https://github.com/user/repo --output report.json
```

Scan a local directory:
```bash
codeguard scan ./my-project --format markdown --output report.md
```

With options:
```bash
codeguard scan https://github.com/user/repo \
  --branch main \
  --include "*.py" \
  --exclude "tests/*" \
  --output report.html
```

### API

Start a scan:
```bash
curl -X POST http://localhost:8000/api/v1/scan \
  -H "Content-Type: application/json" \
  -d '{
    "repository_url": "https://github.com/user/repo",
    "branch": "main"
  }'
```

Get scan results:
```bash
curl http://localhost:8000/api/v1/scan/{scan_id}
```

### Web Dashboard

1. Navigate to http://localhost:3000
2. Click "New Scan"
3. Enter repository URL or local path
4. View results in the dashboard

## AWS Deployment

### Prerequisites

- AWS CLI configured
- Terraform 1.5.0+
- AWS account with appropriate permissions

### Deploy Infrastructure

1. **Configure Terraform variables**:
   ```bash
   cd infra
   terraform init
   ```

2. **Create terraform.tfvars**:
   ```hcl
   aws_region = "us-east-1"
   db_password = "your-secure-password"
   secret_key = "your-secret-key"
   openai_api_key = "your-openai-key"  # Optional
   github_pat = "your-github-pat"       # Optional
   ```

3. **Deploy**:
   ```bash
   terraform plan
   terraform apply
   ```

4. **Get outputs**:
   ```bash
   terraform output alb_dns_name
   terraform output ecr_repo_url
   ```

### Build and Push Docker Images

```bash
# Build backend
docker build -f docker/backend.Dockerfile -t codeguard-backend .

# Build frontend
docker build -f docker/frontend.Dockerfile -t codeguard-frontend .

# Tag and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ecr-repo-url>
docker tag codeguard-backend:latest <ecr-repo-url>/codeguard-backend:latest
docker push <ecr-repo-url>/codeguard-backend:latest
```

## Configuration

### Environment Variables

Key environment variables (see `.env.example` for full list):

- `DATABASE_URL`: PostgreSQL connection URL
- `QDRANT_HOST`: Qdrant host (default: localhost)
- `QDRANT_PORT`: Qdrant port (default: 6333)
- `OLLAMA_BASE_URL`: Ollama API URL (default: http://localhost:11434)
- `OLLAMA_MODEL`: Ollama model name (default: codellama:34b-instruct)
- `OPENAI_API_KEY`: OpenAI API key (for fallback)
- `SECRET_KEY`: Application secret key (required)

### LLM Configuration

CodeGuard AI supports multiple LLM backends:

1. **Ollama** (recommended for local development):
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull model
   ollama pull codellama:34b-instruct
   ```

2. **OpenAI** (fallback):
   Set `OPENAI_API_KEY` and `USE_OPENAI_FALLBACK=true` in `.env`

## Testing

Run unit tests:
```bash
pytest tests/unit/
```

Run integration tests:
```bash
pytest tests/integration/
```

Run all tests with coverage:
```bash
pytest tests/ --cov=app --cov-report=html
```

## Project Structure

```
codeguard-ai/
├── app/                    # Backend application
│   ├── api/               # FastAPI routes
│   ├── core/              # Configuration, LLM, ingestion
│   ├── models/            # Pydantic and SQLModel schemas
│   ├── rag/               # RAG components (chunking, embeddings)
│   ├── scanner/            # Scanner orchestrator
│   ├── cli.py             # CLI tool
│   └── main.py            # FastAPI app
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API client
│   │   └── types/         # TypeScript types
│   └── package.json
├── infra/                 # Terraform infrastructure
│   ├── modules/           # Reusable modules
│   └── main.tf            # Main configuration
├── docker/                # Dockerfiles
├── tests/                 # Test suite
├── .github/workflows/     # GitHub Actions
└── README.md
```

## CI/CD

GitHub Actions workflows:

- **test.yml**: Run tests, linting, type checking
- **build-push.yml**: Build and push Docker images to ECR
- **deploy.yml**: Deploy infrastructure with Terraform
- **scan-pr.yml**: Automatically scan PRs and post comments

## Security

CodeGuard AI includes:

- Security scanning with Bandit, Semgrep, Safety
- Secure Docker images (non-root user, minimal base images)
- Secrets management via AWS Secrets Manager
- HTTPS with ACM certificates
- VPC isolation for resources

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

- Issues: https://github.com/yourusername/codeguard-ai/issues
- Documentation: https://codeguard-ai.readthedocs.io

## Roadmap

- [ ] GitHub Bot for automatic PR comments
- [ ] Fine-tuned CodeLlama model
- [ ] Export to GitHub Security Alerts (CodeQL compatible)
- [ ] Support for more languages
- [ ] Real-time scanning with WebSockets
- [ ] Custom rule definitions
- [ ] Team collaboration features

