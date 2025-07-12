# template-fastapi

A comprehensive FastAPI template with Azure cloud services integration, Agent-based workflows, and multi-service API architecture.

## Features

- **Multiple API Services**: Items management, file operations, restaurant discovery, speech transcription, and agent-based chat
- **Azure Cloud Integration**: CosmosDB, Blob Storage, OpenAI, AI Speech, and Application Insights
- **Agent Workflows**: LangGraph and Azure AI Foundry integration for conversational AI
- **Real-time Communication**: WebSocket-based chat functionality
- **Comprehensive Logging**: Configurable log levels with structured error handling
- **Testing & Quality**: 37+ automated tests with logging and monitoring
- **Container Ready**: Docker support with multi-stage builds

## Quick Start

### Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended) or pip
- [GNU Make](https://www.gnu.org/software/make/)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd template-fastapi

# Install dependencies
make install-deps-dev

# Copy environment template
cp .env.template .env
# Edit .env with your Azure service credentials
```

### Running the Application

```bash
# Development server with hot reload
make dev

# Production server
make run

# Run tests
make test

# View documentation
make docs-serve
```

The API will be available at http://localhost:8000 with interactive documentation at http://localhost:8000/docs.

## API Services

### Core Services
- **Items API** (`/items/`): CRUD operations for item management
- **Files API** (`/files/`): File upload, download, and management with Azure Blob Storage
- **Restaurants API** (`/foodies/`): Restaurant discovery with geospatial search
- **Speech API** (`/speeches/`): Batch transcription jobs using Azure AI Speech

### Agent Services
- **LangGraph Agents** (`/agents/langgraph/`): AI agents with custom tools
- **Azure AI Foundry** (`/agents/azure-ai-foundry/`): Thread-based conversations
- **Chat Interface** (`/chats/`): Real-time WebSocket chat with agent integration

### Demo & Utilities
- **Demo Endpoints** (`/demos/`): Dice rolling, flaky endpoints for testing
- **Health & Monitoring**: Application Insights integration with OpenTelemetry

## Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://<name>.openai.azure.com/
AZURE_OPENAI_API_KEY=<key>
AZURE_OPENAI_MODEL_CHAT=gpt-4o

# Azure Storage & Database
AZURE_COSMOSDB_CONNECTION_STRING=<connection-string>
AZURE_BLOB_STORAGE_CONNECTION_STRING=<connection-string>

# Monitoring
APPLICATIONINSIGHTS_CONNECTION_STRING=<connection-string>
```

See `.env.template` for complete configuration options.

## Docker Deployment

```bash
# Build image
make docker-build

# Run container
docker run -p 8000:8000 --env-file .env ks6088ts/template-fastapi:latest

# Docker Compose (if available)
docker-compose up
```

## Development

### Project Structure

```
template_fastapi/
├── routers/          # API route handlers
│   ├── agents/       # Agent-based endpoints
│   ├── chats.py      # WebSocket chat
│   ├── demos.py      # Demo endpoints
│   ├── files.py      # File operations
│   ├── foodies.py    # Restaurant API
│   ├── items.py      # Items CRUD
│   └── speeches.py   # Speech transcription
├── models/           # Pydantic data models
├── repositories/     # Data access layer
├── settings/         # Configuration management
└── templates/        # Jinja2 templates
```

### Testing

```bash
# Run all tests
make test

# Run with coverage
pytest --cov=template_fastapi

# Run specific test file
pytest tests/test_api.py -v
```

### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Apply auto-fixes
make fix
```

## Azure Functions Deployment

The application supports Azure Functions deployment:

```bash
# Export requirements
uv export --format requirements-txt --no-dev --no-hashes --output-file requirements.txt

# Deploy to Azure Functions
func azure functionapp publish <function-app-name>
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run quality checks (`make ci-test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
