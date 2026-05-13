# Churn Intelligence OS

A lightweight churn audit and intelligence engine for B2B SaaS businesses.

## Project structure

- `backend/`
  - `validator/` - CSV validation logic
  - `engine/` - rule-based scoring engine
  - `reports/` - PDF report generation
  - `tests/` - component and integration test scripts
- `frontend/`
  - `app.py` - Streamlit audit tool UI
- `data/`
  - `generate_sample_data.py` - sample customer dataset generator
- `.github/workflows/` - CI workflow configuration
- `requirements.txt` - Python dependencies

## Setup

```bash
cd "F:/Customer Churn Prediction"
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run locally

```bash
cd "F:/Customer Churn Prediction"
.venv\Scripts\streamlit run app.py
```

Then open `http://127.0.0.1:8501`.

## Tests

```bash
cd "F:/Customer Churn Prediction"
.venv\Scripts\python backend\tests\test_components.py
.venv\Scripts\python backend\tests\test_pdf.py
```

## GitHub Actions

A CI workflow is configured in `.github/workflows/python-app.yml` to:
- install dependencies
- run Python syntax checks
- run backend test scripts

## Git setup

This project is prepared for the remote:

`https://github.com/farhaanqazi/Churn-Prediction-Intelligence.git`

> Note: changes have been committed locally but not pushed.
