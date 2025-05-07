# LLM Admin Service

This is the Django-based admin service for the LLM Assistant project. It provides a web interface for managing conversations, messages, and system configuration.

## Setup

1. Create a `.env` file in the root directory with the following variables:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database settings
DB_NAME=llm_admin
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# CORS settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:80
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver 0.0.0.0:8001
```

## API Endpoints

- `GET /api/healthz/` - Health check endpoint
- `POST /api/create-superuser/` - Create a superuser if none exists
- `GET /api/conversations/` - List all conversations
- `POST /api/conversations/create/` - Create a new conversation
- `GET /api/conversations/<id>/` - Get a specific conversation
- `POST /api/conversations/<id>/messages/` - Add a message to a conversation

## Docker

To run the service using Docker:

```bash
docker build -t llm-admin .
docker run -p 8001:8001 llm-admin
```

## Development

The service uses Django's admin interface for managing data. Access it at `/admin/` after creating a superuser.
