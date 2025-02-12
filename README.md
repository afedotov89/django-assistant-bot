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
Administrative interface and management commands.

### ai
Core AI functionality:
- `dialog.py`: AI dialog management
- `domain.py`: Core domain models
- `embedders/`: Various embedding providers (GPU, Ollama, OpenAI, Transformers)
- `providers/`: AI model providers implementation
- `services/`: AI-related services

### bot
Main bot functionality:
- `assistant_bot.py`: Core bot implementation
- `chat_completion.py`: Chat completion handling
- `platforms/`: Platform-specific implementations (e.g., Telegram)
- `services/`: Bot-related services
- `schemas/`: JSON schemas for various bot operations

### loading
Data loading functionality:
- CSV data loading
- Management commands for data import

### processing
Document processing:
- Wiki document processing
- Document splitting and formatting
- Question generation and merging
- Custom processing steps

### rag
Retrieval-Augmented Generation:
- Search services
- Document retrieval

### storage
Data storage:
- Document storage
- API endpoints
- Database models

### utils
Utility functions:
- Database utilities
- Debugging tools
- JSON schema handling
- Language processing
- Throttling

## Configuration

The bot can be configured through Django settings and environment variables. Key settings include:

- `DEFAULT_AI_MODEL`: Default AI model to use
- `DIALOG_FAST_AI_MODEL`: Model for quick responses
- `DIALOG_STRONG_AI_MODEL`: Model for complex processing

## Usage

1. Install the package:
```bash
pip install .
```

2. Add required apps to INSTALLED_APPS in your Django settings:
```python
INSTALLED_APPS = [
    ...
    'assistant.admin',
    'assistant.ai',
    'assistant.bot',
    'assistant.loading',
    'assistant.processing',
    'assistant.rag',
    'assistant.storage',
]
```

3. Configure your AI providers in settings.py:
```python
DEFAULT_AI_MODEL = 'your-default-model'
DIALOG_FAST_AI_MODEL = 'fast-model'
DIALOG_STRONG_AI_MODEL = 'strong-model'
```

4. Set up your platform credentials (e.g., Telegram bot token) in environment variables.

5. Run migrations:
```bash
python manage.py migrate
```

## Example Implementation

See the `example` directory for a complete working example of a bot implementation.

## Commands

The bot supports various commands:

- `/start`: Start a new conversation
- `/help`: Show help message
- `/continue`: Continue the previous response
- `/new`: Start a new dialog
- `/model <model_id>`: Switch AI model
- `/models`: List available AI models
- `/debug`: Show debug information
- `/doc <doc_id>`: Show document content
- `/wiki <wiki_id>`: Show wiki document

## Development

### Adding New AI Providers

1. Create a new provider in `assistant.ai.providers`
2. Implement the required interface
3. Register the provider in settings

### Adding New Platforms

1. Create a new platform implementation in `assistant.bot.platforms`
2. Implement the platform interface
3. Register the platform in your bot configuration

## Dependencies

Key dependencies include:
- Django 4.2.13
- djangorestframework 3.15.1
- python-telegram-bot 21.1.1
- openai 1.28.1
- groq 0.6.0
- ollama 0.4.4
- celery 5.4.0
- pgvector 0.2.5 (for vector embeddings)

## License

This project is licensed under the MIT License.

## Author

Aleksandr Fedotov (a_fedotov89@mail.ru)