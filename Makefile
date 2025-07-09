.PHONY: help install dev test format lint type-check build publish publish-test clean docs deploy-credentials test-credentials migrate

help:
	@echo "BICAM Development Commands"
	@echo "========================="
	@echo "install      - Install package with uv"
	@echo "dev          - Set up development environment"
	@echo "test         - Run tests with coverage"
	@echo "test-quick   - Run tests without coverage"
	@echo "format       - Format code with black and ruff"
	@echo "lint         - Run linting checks"
	@echo "type-check   - Run type checking with mypy"
	@echo "build        - Build package for distribution"
	@echo "build-test   - Build and test package locally"
	@echo "publish      - Build and publish to PyPI"
	@echo "publish-test - Build and publish to TestPyPI"
	@echo "deploy-credentials - Deploy credential server to AWS"
	@echo "test-credentials   - Test credential server authentication"
	@echo "migrate      - Migrate from old to new auth system"
	@echo "clean        - Clean build artifacts and cache"
	@echo "docs         - Build documentation"

install:
	uv pip install .

dev:
	./scripts/setup_dev.sh

test:
	uv run pytest tests/ -v --cov=bicam --cov-report=html --cov-report=term-missing

test-quick:
	uv run pytest tests/ -v

format:
	uv run black bicam/ tests/ scripts/*.py
	uv run ruff check --fix bicam/ tests/ scripts/*.py

lint:
	uv run ruff check bicam/ tests/ scripts/*.py
	uv run black --check bicam/ tests/ scripts/*.py

type-check:
	uv run mypy bicam/

build: clean .env
	python scripts/credentials/3_build_credentials.py
	uv build
	@echo "Cleaning up credentials..."
	@rm -f bicam/_auth.py

# Load environment from .env file for other targets
.env:
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Run ./scripts/credentials/setup_credential_server.sh first."; \
		exit 1; \
	fi

build-test: clean
	@echo "Building package for testing (with mock credentials)..."
	@echo "Creating mock auth file for build..."
	@echo '"""Mock authentication module for testing."""' > bicam/_auth.py
	@echo '' >> bicam/_auth.py
	@echo 'import boto3' >> bicam/_auth.py
	@echo 'from functools import lru_cache' >> bicam/_auth.py
	@echo '' >> bicam/_auth.py
	@echo '@lru_cache(maxsize=1)' >> bicam/_auth.py
	@echo 'def get_s3_client():' >> bicam/_auth.py
	@echo '    """Get authenticated S3 client."""' >> bicam/_auth.py
	@echo '    return boto3.client(' >> bicam/_auth.py
	@echo "        's3'," >> bicam/_auth.py
	@echo "        region_name='us-east-1'" >> bicam/_auth.py
	@echo '    )' >> bicam/_auth.py
	uv build
	@echo "Testing package installation..."
	uv pip install --find-links dist/ bicam
	@echo "Testing package import..."
	uv run python -c "import bicam; print(f'✓ Successfully imported bicam {bicam.__version__}')"
	@echo "Testing CLI..."
	uv run bicam --version
	@echo "Cleaning up mock auth file..."
	@rm -f bicam/_auth.py
	@echo "✓ Build test completed successfully!"

publish:
	./scripts/build_and_publish.sh --publish

publish-test:
	./scripts/build_and_publish.sh --test-publish

deploy-credentials: .env
	./scripts/credentials/deploy_credentials_server.sh

test-credentials: .env
	./scripts/credentials/4_test_credentials.py

migrate:
	./scripts/credentials/migrate_to_credential_server.sh

clean:
	rm -rf build/ dist/ *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -f bicam/_auth.py
	rm -rf .coverage htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/

docs:
	@echo "Building documentation..."
	uv run sphinx-build -b html docs/ docs/_build/html
	@echo "Documentation built in docs/_build/html/"

docs-clean:
	rm -rf docs/_build/
