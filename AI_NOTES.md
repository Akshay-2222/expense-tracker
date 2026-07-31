# AI Usage Notes

This project was built with significant help from AI tools. I used AI to move faster, but I also reviewed the code, checked that it matched the assignment requirements, and made changes before submission.

## Tools Used

- Claude: generated the first full draft of the Flask API, tests, README, and AI notes.
- ChatGPT/Codex: reviewed the draft, checked it against the assignment instructions, and helped revise the project before submission.

## What Was AI-Generated vs. Done by Me

### AI-Generated

- The first version of the Flask application in `src/app.py`
- The route structure for adding, listing, filtering, totaling, searching, and deleting expenses
- The first version of the pytest test suite
- The first drafts of `README.md` and `AI_NOTES.md`

### Done by Me With AI Assistance

- Read the assignment instructions and compared them against the generated files
- Checked that the required project structure was present: `README.md`, `AI_NOTES.md`, `src/`, and `tests/`
- Kept the implementation simple with in-memory storage because the assignment allowed it
- Chose search by title as the single optional bonus feature
- Reviewed the validation rules for required fields, positive amounts, non-empty strings, and date format
- Ran or prepared the documented install, run, and test commands so the reviewer can execute the project consistently

## What I Validated, Tested, or Changed

- I removed the extra monthly summary bonus endpoint from the generated version because the assignment said to pick at most one optional bonus.
- I kept the search endpoint as the single bonus feature because it is small, easy to test, and useful for an expense tracker.
- I checked that invalid inputs return `400 Bad Request`, including missing fields, empty strings, invalid dates, and non-positive amounts.
- I checked that deleting a missing expense returns `404 Not Found`.
- I checked that category filtering is case-insensitive by storing categories in lowercase.
- I checked that totals include both the overall amount and a category breakdown.
- I rewrote these notes to be specific about AI usage instead of using a generic template.

## AI Suggestions I Did Not Use

- I did not use SQLite or SQLAlchemy because the assignment said a database was not required, and in-memory storage keeps setup simple.
- I did not split the app into Flask Blueprints because the project is small enough for a single source file.
- I did not use Pydantic because manual validation was enough for this API and avoided another dependency.
- I did not include more than one bonus feature because the assignment explicitly said to pick at most one.

