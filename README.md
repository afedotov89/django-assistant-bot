# Django Assistant Bot

A powerful Django-based framework for building AI-powered chat assistants with support for multiple AI models and platforms.

## Features

- Support for multiple AI providers (OpenAI, Groq, Ollama, Transformers)
- Built-in Telegram platform integration
- Extensible architecture for adding new platforms
- Document processing and RAG (Retrieval-Augmented Generation) capabilities
- Multi-language support
- Dialog management and persistence
- Resource management system
- Asynchronous message processing
- Debug mode for development
- Whitelist access control

## Installation

```bash
pip install .
```

## Project Structure

The project is organized into several Django apps:

### admin
Administrative interface and management commands:
- Management commands for queue processing
- Admin interface customization
- Bot configuration management

### ai
Core AI functionality:

#### dialog.py
Handles AI dialog management:
- Message context management
- AI provider integration
- Response handling
- Token calculation
- Context size management

#### domain.py
Core domain models for AI interaction:
- Message structure
- AI Response format
- Common data types

#### embedders/
Various embedding providers:
- `gpu_service.py`: GPU-accelerated embeddings
- `ollama.py`: Ollama embeddings integration
- `openai.py`: OpenAI embeddings
- `transformers.py`: Hugging Face Transformers embeddings

#### providers/
AI model providers implementation:
- `base.py`: Base provider interface
- `gpu_service.py`: GPU service integration
- `groq.py`: Groq API integration
- `ollama.py`: Ollama models support
- `openai.py`: OpenAI API integration
- `transformers.py`: Local transformer models

#### services/
AI-related services:
- `ai_service.py`: Core AI service functionality
  - Provider management
  - Response formatting
  - Error handling

### bot
Main bot functionality:

#### assistant_bot.py
Core bot implementation:
- Message handling
- Command processing
- State management
- Dialog control
- Platform integration

#### chat_completion.py
Chat completion handling:
- Message generation
- Context management
- Model selection
- Response formatting

#### platforms/
Platform-specific implementations:
- Telegram integration with markdown support
- Extensible base for other platforms

#### services/
Bot-related services:
- `dialog_service.py`: Dialog management
- `instance_service.py`: Bot instance handling
- `schema_service.py`: JSON schema validation
- `context_service/`: Context management

#### schemas/
JSON schemas for various operations:
- Context checking
- Document selection
- Question handling
- Topic classification
- Search operations

### Domain Models

#### Update
Represents an incoming update from the platform:
```python
@dataclasses.dataclass
class Update:
    chat_id: str              # Chat identifier
    message_id: Optional[int] # Message identifier
    text: Optional[str]       # Message text
    photo: Optional[Photo]    # Photo data if present
    user: Optional[User]      # User information
    callback_query: Optional[CallbackQuery] # Callback data
```

#### Answer Types
Two types of responses are supported:

1. SingleAnswer:
```python
answer = SingleAnswer(
    text="Response text",
    thinking="Internal thought process",
    image_url="Optional image URL",
    is_markdown=True,
    buttons=[[Button("Click me", "/command")]],
    state={"key": "value"},
    usage=[{"model": "gpt-4", "tokens": 150}]
)
```

2. MultiPartAnswer for complex responses:
```python
multi_answer = MultiPartAnswer([
    SingleAnswer(text="Part 1"),
    SingleAnswer(text="Part 2")
])
```

### Command System Examples

1. Basic command:
```python
@AssistantBot.command(r'/start')
async def command_start(self, match, message_id):
    return SingleAnswer("Bot started!")
```

2. Command with parameters:
```python
@AssistantBot.command(r'/search\s+(.*)')
async def command_search(self, match, message_id):
    query = match.group(1)
    return SingleAnswer(f"Searching for: {query}")
```

### State Management Examples

1. Updating state:
```python
await self.update_state({
    'current_mode': 'search',
    'last_query': 'example',
    'results_count': 5
})
```

2. Reading state:
```python
current_mode = self.instance.state.get('current_mode')
if current_mode == 'search':
    # Handle search mode
```

### Resource Management Examples

1. Loading localized messages:
```python
# messages/en/welcome.txt
resource_manager = ResourceManager(codename='mybot', language='en')
welcome_text = resource_manager.get_message('welcome.txt')
```

2. Error handling:
```python
try:
    text = resource_manager.get_phrase('key')
except NoMessageFound:
    text = "Default message"
```

### loading
Data loading functionality:
- CSV data import
- Data validation
- Format conversion
- Import management commands

### processing
Document processing:

#### documents/
Document processing pipeline:
- `processor.py`: Main document processor
- Custom processing steps

#### schemas/
Processing operation schemas:
- Document questions generation
- Document formatting
- Question merging
- Document splitting
- Section extraction

#### wiki.py
Wiki document processing:
- Content extraction
- Structure analysis
- Metadata handling

### rag
Retrieval-Augmented Generation:

#### services/
- `search_service.py`: Vector-based document search
  - Similarity scoring
  - Result ranking
  - Context retrieval

### RAG Examples

#### Document Search and Retrieval
```python
from assistant.rag.services.search_service import SearchService
from assistant.storage.models import Document

# Initialize search service
search_service = SearchService()

# Search for relevant documents
results = await search_service.search(
    query="How to configure logging?",
    limit=3,
    similarity_threshold=0.8
)

# Process search results
for doc in results:
    print(f"Document: {doc.name}")
    print(f"Similarity: {doc.similarity_score}")
    print(f"Content: {doc.content[:200]}...")
```

#### Integrating RAG with Bot Responses
```python
async def handle_user_query(query: str) -> str:
    # Search for relevant documents
    docs = await search_service.search(query)
    
    # Build context from documents
    context = "\n".join([
        f"Document '{doc.name}':\n{doc.content}"
        for doc in docs
    ])
    
    # Create messages with context
    messages = [
        {
            "role": "system",
            "content": f"Use this context to answer questions:\n{context}"
        },
        {
            "role": "user",
            "content": query
        }
    ]
    
    # Get AI response with context
    response = await ai_service.get_response(messages)
    return response.text
```

#### Vector Search Configuration
```python
# settings.py
VECTOR_SEARCH_SETTINGS = {
    'model': 'text-embedding-3-small',  # Embedding model
    'dimensions': 1536,                 # Vector dimensions
    'metric': 'cosine',                # Similarity metric
    'index_type': 'hnsw',              # Index type for pgvector
    'ef_search': 100,                  # HNSW search parameter
    'm': 16                            # HNSW graph parameter
}
```

### storage
Data storage:

#### models.py
Database models:
- Document storage
- Wiki document management
- Embedding storage
- Metadata management

#### api/
REST API implementation:
- `filters.py`: Query filtering
- `pagination.py`: Result pagination
- `serializers.py`: Data serialization
- `views.py`: API endpoints

### utils
Utility functions:

#### db.py
Database utilities:
- Connection management
- Query optimization
- Transaction handling

#### debug.py
Debugging tools:
- Performance monitoring
- Error tracking
- Debug logging

#### json_schema.py
JSON schema utilities:
- Schema validation
- Format checking
- Error reporting

#### language.py
Language processing:
- Language detection
- Text processing
- Character encoding

#### repeat_until.py
Retry mechanism:
- Operation retrying
- Error handling
- Timeout management

#### throttle.py
Rate limiting:
- API call throttling
- Request queuing
- Limit enforcement

## Configuration

### Environment Variables
```bash
# AI Provider Settings
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key
OLLAMA_HOST=http://localhost:11434

# Database Settings
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Redis Settings (for Celery)
REDIS_URL=redis://localhost:6379/0

# Telegram Bot Settings
TELEGRAM_BOT_TOKEN=your_bot_token
```

### Django Settings
```python
# AI Models Configuration
DEFAULT_AI_MODEL = 'gpt-3.5-turbo'
DIALOG_FAST_AI_MODEL = 'gpt-3.5-turbo'
DIALOG_STRONG_AI_MODEL = 'gpt-4'

# Vector Search Settings
VECTOR_SIMILARITY_THRESHOLD = 0.8
MAX_SEARCH_RESULTS = 5

# Bot Settings
BOT_MESSAGE_TIMEOUT = 60
BOT_MAX_RETRIES = 3
```

## Development

### Adding New AI Providers

1. Create a new provider class in `assistant.ai.providers`:
```python
from assistant.ai.providers.base import AIProvider

class NewProvider(AIProvider):
    async def get_response(self, messages, max_tokens=1024, json_format=False):
        # Implementation
        pass
```

2. Register in `ai_service.py`:
```python
PROVIDERS = {
    'new-provider': NewProvider,
}
```

### Adding New Platforms

1. Create platform implementation:
```python
from assistant.bot.domain import BotPlatform

class NewPlatform(BotPlatform):
    async def send_message(self, chat_id, text, **kwargs):
        # Implementation
        pass
```

2. Register in your bot configuration.

## Testing

Run tests with pytest:
```bash
pytest
```

Test coverage:
```bash
pytest --cov=assistant
```

## Deployment

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Configure environment variables

3. Run migrations:
```bash
python manage.py migrate
```

4. Start Celery worker:
```bash
celery -A your_project worker -l info
```

5. Run the bot:
```bash
python manage.py runbot
```

## License

This project is licensed under the MIT License.

## Author

Aleksandr Fedotov (a_fedotov89@mail.ru)