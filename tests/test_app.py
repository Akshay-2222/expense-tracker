import os
import sys

import pytest


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app import app, expenses


@pytest.fixture(autouse=True)
def clear_expenses():
    expenses.clear()
    yield
    expenses.clear()


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def add_sample_expense(client, title="Lunch", amount=12.5, category="Food", date="2026-07-01"):
    return client.post(
        "/expenses",
        json={
            "title": title,
            "amount": amount,
            "category": category,
            "date": date,
        },
    )


def test_add_expense_success(client):
    response = add_sample_expense(client)

    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "Lunch"
    assert data["amount"] == 12.5
    assert data["category"] == "food"
    assert data["date"] == "2026-07-01"
    assert "id" in data


@pytest.mark.parametrize(
    "payload, expected_error",
    [
        ({"amount": 10, "category": "Food", "date": "2026-07-01"}, "title"),
        ({"title": "Bus", "category": "Transport", "date": "2026-07-01"}, "amount"),
        ({"title": "Bus", "amount": 10, "date": "2026-07-01"}, "category"),
        ({"title": "Bus", "amount": 10, "category": "Transport"}, "date"),
    ],
)
def test_add_expense_missing_required_fields(client, payload, expected_error):
    response = client.post("/expenses", json=payload)

    assert response.status_code == 400
    assert expected_error in response.get_json()["error"]


@pytest.mark.parametrize("amount", ["abc", -5, 0])
def test_add_expense_rejects_invalid_amount(client, amount):
    response = client.post(
        "/expenses",
        json={
            "title": "Bus",
            "amount": amount,
            "category": "Transport",
            "date": "2026-07-01",
        },
    )

    assert response.status_code == 400


@pytest.mark.parametrize("field", ["title", "category"])
def test_add_expense_rejects_empty_strings(client, field):
    payload = {
        "title": "Bus",
        "amount": 10,
        "category": "Transport",
        "date": "2026-07-01",
    }
    payload[field] = "   "

    response = client.post("/expenses", json=payload)

    assert response.status_code == 400


def test_add_expense_rejects_invalid_date(client):
    response = client.post(
        "/expenses",
        json={
            "title": "Bus",
            "amount": 10,
            "category": "Transport",
            "date": "01-07-2026",
        },
    )

    assert response.status_code == 400
    assert "date" in response.get_json()["error"]


def test_add_expense_rejects_missing_json_body(client):
    response = client.post("/expenses")

    assert response.status_code == 400


def test_add_expense_generates_unique_ids(client):
    first = add_sample_expense(client, title="Lunch").get_json()
    second = add_sample_expense(client, title="Dinner").get_json()

    assert first["id"] != second["id"]


def test_get_all_expenses_empty(client):
    response = client.get("/expenses")

    assert response.status_code == 200
    assert response.get_json() == []


def test_get_all_expenses(client):
    add_sample_expense(client, title="Lunch")
    add_sample_expense(client, title="Dinner")

    response = client.get("/expenses")

    assert response.status_code == 200
    assert len(response.get_json()) == 2


def test_filter_by_category(client):
    add_sample_expense(client, title="Lunch", category="Food")
    add_sample_expense(client, title="Bus", category="Transport")
    add_sample_expense(client, title="Dinner", category="Food")

    response = client.get("/expenses?category=Food")

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert all(expense["category"] == "food" for expense in data)


def test_filter_by_category_case_insensitive(client):
    add_sample_expense(client, title="Lunch", category="Food")

    response = client.get("/expenses?category=FOOD")

    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_filter_by_nonexistent_category(client):
    add_sample_expense(client, title="Lunch", category="Food")

    response = client.get("/expenses?category=Entertainment")

    assert response.status_code == 200
    assert response.get_json() == []


def test_total_empty(client):
    response = client.get("/expenses/total")

    assert response.status_code == 200
    data = response.get_json()
    assert data["total"] == 0
    assert data["count"] == 0
    assert data["by_category"] == {}


def test_total_overall_and_by_category(client):
    add_sample_expense(client, amount=10, category="Food")
    add_sample_expense(client, amount=15, category="Food")
    add_sample_expense(client, amount=20, category="Transport")

    response = client.get("/expenses/total")

    assert response.status_code == 200
    data = response.get_json()
    assert data["total"] == 45
    assert data["count"] == 3
    assert data["by_category"]["food"] == 25
    assert data["by_category"]["transport"] == 20


def test_total_filtered_by_category(client):
    add_sample_expense(client, amount=10, category="Food")
    add_sample_expense(client, amount=15, category="Food")
    add_sample_expense(client, amount=20, category="Transport")

    response = client.get("/expenses/total?category=Food")

    assert response.status_code == 200
    data = response.get_json()
    assert data["category"] == "food"
    assert data["total"] == 25
    assert data["count"] == 2


def test_total_filtered_nonexistent_category(client):
    add_sample_expense(client)

    response = client.get("/expenses/total?category=Entertainment")

    assert response.status_code == 200
    assert response.get_json()["total"] == 0


def test_delete_expense_success(client):
    expense_id = add_sample_expense(client).get_json()["id"]

    response = client.delete(f"/expenses/{expense_id}")

    assert response.status_code == 200
    assert response.get_json()["deleted"]["id"] == expense_id
    assert client.get("/expenses").get_json() == []


def test_delete_nonexistent_expense(client):
    response = client.delete("/expenses/missing-id")

    assert response.status_code == 404
    assert "not found" in response.get_json()["error"]


def test_delete_only_removes_target(client):
    add_sample_expense(client, title="Lunch")
    dinner = add_sample_expense(client, title="Dinner").get_json()

    client.delete(f"/expenses/{dinner['id']}")
    remaining = client.get("/expenses").get_json()

    assert len(remaining) == 1
    assert remaining[0]["title"] == "Lunch"


def test_search_expenses(client):
    add_sample_expense(client, title="Lunch at restaurant")
    add_sample_expense(client, title="Bus ticket")

    response = client.get("/expenses/search?q=lunch")

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["title"] == "Lunch at restaurant"


def test_search_requires_query(client):
    response = client.get("/expenses/search")

    assert response.status_code == 400


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"

