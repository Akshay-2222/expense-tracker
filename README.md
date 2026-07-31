# Smart Expense Tracker API

A small REST API for managing personal expenses, built with Python and Flask.

## Features

- Add an expense with `title`, `amount`, `category`, and `date`
- View all expenses
- Filter expenses by category
- Calculate total expenses overall and by category
- Delete an expense by ID
- Bonus: search expenses by title keyword

Expenses are stored in memory, so data resets when the server restarts.

## Project Structure

```text
expense-tracker/
  README.md
  AI_NOTES.md
  requirements.txt
  src/
    app.py
  tests/
    test_app.py
```

## Install Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows, activate the virtual environment with:

```bash
.venv\Scripts\activate
```

## Run the Server

```bash
python3 src/app.py
```

The API runs at `http://localhost:5000`.

## Run Tests

```bash
python3 -m pytest tests -v
```

## API Endpoints

### Add an Expense

```http
POST /expenses
Content-Type: application/json
```

```json
{
  "title": "Lunch",
  "amount": 12.5,
  "category": "Food",
  "date": "2026-07-31"
}
```

### View All Expenses

```http
GET /expenses
```

### Filter Expenses by Category

```http
GET /expenses?category=Food
```

### Get Total Expenses

```http
GET /expenses/total
```

### Get Total Expenses by Category

```http
GET /expenses/total?category=Food
```

### Delete an Expense

```http
DELETE /expenses/<expense_id>
```

### Bonus: Search Expenses

```http
GET /expenses/search?q=lunch
```

## Validation Rules

| Field | Rule |
| --- | --- |
| title | Required non-empty string |
| amount | Required positive number |
| category | Required non-empty string |
| date | Required date in `YYYY-MM-DD` format |

