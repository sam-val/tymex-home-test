# src/backend
# Handy commands for local development

# pytest
test:
        # Examples:
        # >>> make test k=TestABC
        # >>> make test k=backend/subapp1/tests/
        # >>> make test k="'TestABC or TestCalculation'"

        # With optional path param for faster test lookup
        # >>> make test k=TestLoanCalculation path=backend/subapp1/tests/

	poetry run pytest --no-migrations -q -rx -k ${k} ${path}

test_all:
	poetry run pytest -q -rx .

test_verbose:
	poetry run pytest --no-migrations -v -rx -k ${k} ${path}

test_subapp_with_coverage:
        # Examples:
        # >>> make test_subapp_with_coverage k=backend/app1/
        # >>> make test_subapp_with_coverage k=backend/app2/

	pytest --no-migrations -v -rx -k ${k} ${path} --cov=${k}
