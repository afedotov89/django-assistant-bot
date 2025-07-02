# Example of using Django Assistant Bot

This is a Django project.

## Prerequisites

* create `.env` and fill it
* run Django server

## Celery workers

```bash
# Queries
celery -A project worker -Q query

# Broadcasting
celery -A project worker -Q broadcasting

# Periodic tasks
celery -A project beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```


## Useful commands

```bash
# Run bot in interactive mode in console
./manage.py chat task_manager

# Run Telegram bot in long polling mode (using Celery)
./manage.py telegram_poll task_manager

# Run Telegram bot in synchronous mode (without Celery) with auto-reloading for development
./manage.py telegram_poll task_manager --sync --dev
```

> **Note**: The `telegram_poll` command now uses a direct mechanism for receiving updates from Telegram API instead of the python-telegram-bot library.


## Teelgram Webhook

Use `https://<your-domain>/telegram/task_manager/`
