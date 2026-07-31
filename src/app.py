from datetime import datetime
import uuid

from flask import Flask, jsonify, request


app = Flask(__name__)
expenses = []


def find_expense(expense_id):
    return next((expense for expense in expenses if expense["id"] == expense_id), None)


def validate_expense_data(data):
    required_fields = ["title", "amount", "category", "date"]
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: '{field}'"

    if not isinstance(data["title"], str) or not data["title"].strip():
        return False, "Field 'title' must be a non-empty string"

    try:
        amount = float(data["amount"])
    except (TypeError, ValueError):
        return False, "Field 'amount' must be a valid number"

    if amount <= 0:
        return False, "Field 'amount' must be a positive number"

    if not isinstance(data["category"], str) or not data["category"].strip():
        return False, "Field 'category' must be a non-empty string"

    if not isinstance(data["date"], str):
        return False, "Field 'date' must be in YYYY-MM-DD format"

    try:
        datetime.strptime(data["date"], "%Y-%m-%d")
    except ValueError:
        return False, "Field 'date' must be in YYYY-MM-DD format"

    return True, None


@app.route("/expenses", methods=["POST"])
def add_expense():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be JSON"}), 400

    is_valid, error = validate_expense_data(data)
    if not is_valid:
        return jsonify({"error": error}), 400

    expense = {
        "id": str(uuid.uuid4()),
        "title": data["title"].strip(),
        "amount": round(float(data["amount"]), 2),
        "category": data["category"].strip().lower(),
        "date": data["date"],
    }
    expenses.append(expense)
    return jsonify(expense), 201


@app.route("/expenses", methods=["GET"])
def get_expenses():
    category = request.args.get("category", "").strip().lower()
    if category:
        return jsonify([expense for expense in expenses if expense["category"] == category]), 200

    return jsonify(expenses), 200


@app.route("/expenses/total", methods=["GET"])
def get_total():
    category = request.args.get("category", "").strip().lower()

    if category:
        filtered_expenses = [
            expense for expense in expenses if expense["category"] == category
        ]
        total = round(sum(expense["amount"] for expense in filtered_expenses), 2)
        return jsonify({"category": category, "total": total, "count": len(filtered_expenses)}), 200

    by_category = {}
    for expense in expenses:
        category_name = expense["category"]
        by_category[category_name] = round(
            by_category.get(category_name, 0) + expense["amount"], 2
        )

    total = round(sum(expense["amount"] for expense in expenses), 2)
    return jsonify({"total": total, "count": len(expenses), "by_category": by_category}), 200


@app.route("/expenses/search", methods=["GET"])
def search_expenses():
    query = request.args.get("q", "").strip().lower()
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    matches = [expense for expense in expenses if query in expense["title"].lower()]
    return jsonify(matches), 200


@app.route("/expenses/<expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    expense = find_expense(expense_id)
    if expense is None:
        return jsonify({"error": f"Expense with id '{expense_id}' not found"}), 404

    expenses.remove(expense)
    return jsonify({"message": "Expense deleted successfully", "deleted": expense}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)

