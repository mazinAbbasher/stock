# Stock Alert System

## Features

- User registration and JWT login
- Create, view, and delete stock price alerts (threshold & duration)
- Alerts linked to user accounts
- Email notification when alerts trigger

## Requirements

- Python 3.x
- Redis (for Celery message broker)

## Installation

First, install and start Redis (required for Celery):

**On Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo service redis-server start
```

**On macOS (with Homebrew):**
```bash
brew install redis
brew services start redis
```

Make sure Redis is running before starting Celery.

Then install project dependencies:
```bash
git clone https://github.com/mazinAbbasher/stock
cd stock
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```

## Environment Variables

Create a `.env` file in the project root directory with your email credentials for sending notifications. Example:

```
EMAIL=your_gmail_address@gmail.com
EMAIL_APP_PASSWORD=your_gmail_app_password
```

> **Note:** You must use an [App Password](https://support.google.com/accounts/answer/185833) if you have 2FA enabled on your Google account.

## Running Locally
In three different terminals run 
```bash
python manage.py runserver 
celery -A stock worker --loglevel=info
celery -A stock beat --loglevel=info
```

## API Endpoints

- `POST /api/auth/register/` — Register new user (`email`, `password`)
- `POST /api/auth/login/` — Obtain JWT token (`email`, `password`)
- `POST /api/auth/token/refresh/` — Refresh JWT token
- `GET /api/alerts/` — List your alerts (add `?triggered=true` to filter triggered)
- `POST /api/alerts/` — Create new alert (see below for details)
- `DELETE /api/alerts/<id>/` — Delete alert

All alert endpoints require JWT authentication.

## Creating Alerts

To create an alert, send a `POST` request to `/api/alerts/` with your JWT token in the `Authorization` header:

```
Authorization: Bearer <your_access_token>
Content-Type: application/json
```

### 1. Threshold Alert

A threshold alert notifies you when a stock price goes above or below a certain value.

**Example Request:**
```json
POST /api/alerts/
{
  "symbol": "AAPL",
  "alert_type": "threshold",
  "condition": "above",         // or "below"
  "target_price": 200.00,
}
```

- `symbol`: Stock symbol (e.g., "AAPL", "TSLA")
- `alert_type`: `"threshold"`
- `condition`: `"above"` or `"below"`
- `target_price`: The price to compare against

### 2. Duration Alert

A duration alert notifies you if a stock price stays above or below a value for a specified number of minutes.

**Example Request:**
```json
POST /api/alerts/
{
  "symbol": "TSLA",
  "alert_type": "duration",
  "condition": "below",         // or "above"
  "target_price": 600.00,
  "duration_minutes": 120       // e.g., 120 minutes = 2 hours
}
```

- `symbol`: Stock symbol (e.g., "AAPL", "TSLA")
- `alert_type`: `"duration"`
- `condition`: `"above"` or `"below"`
- `target_price`: The price to compare against
- `duration_minutes`: Number of minutes the condition must hold

### Example cURL Command

```bash
curl -X POST http://localhost:8000/api/alerts/alerts/ \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "alert_type": "threshold",
    "condition": "above",
    "target_price": 200,
    "duration_minutes": null
  }'
```

## Viewing Alerts

- List all your alerts: `GET /api/alerts/`
- List only triggered alerts: `GET /api/alerts/?triggered=true`
- List only untriggered alerts: `GET /api/alerts/?triggered=false`

## Deleting Alerts

- Delete an alert: `DELETE /api/alerts/<id>/`
Make sure the URL includes a trailing slash after the ID.
## Testing Alerts

1. Register and log in to get a JWT token.
2. Use the token to create alerts via the API (see above).
3. Wait for background tasks to run (every 5 minutes).
4. Check your email for notifications.

