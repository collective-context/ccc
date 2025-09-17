.PHONY: security test clean

security:
	@echo "🔒 Running Security Checks..."
	mkdir -p reports
	pip-audit --desc --fix --dry-run || true
	bandit -r lib/ -f json -o reports/bandit.json || true
	safety check --json > reports/safety.json || true
	@echo "✅ Security scan complete"

test:
	@echo "🧪 Running Tests..."
	pytest --cov=lib --cov-report=term-missing
	@echo "✅ Tests complete"

test-security:
	@echo "🔐 Running Security Tests..."
	pytest tests/security/ -v
	@echo "✅ Security tests complete"

clean:
	rm -rf htmlcov/
	rm -rf reports/
	rm -rf .pytest_cache/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

all: clean security test