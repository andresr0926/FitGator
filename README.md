
# FitGator

Minimal MVP skeleton for Sprint 1.

## Run
```bash
python -m fitgator.app.main
```

## Test
```bash
pip install -r fitgator/requirements.txt
pytest -q fitgator/tests
```

## Structure
- `fitgator/fitgator/` – core package
- `fitgator/app/` – entry points (CLI/GUI)
- `fitgator/tests/` – pytest tests
- `.circleci/config.yml` – CI pipeline
