# src/backend
# Handy commands for local development

shell:
	poetry run shell

run_dev:
	poetry run fastapi dev 

# db
migrations:
	# Examples:
	# >>> make migrations msg="'test'"
	poetry run alembic revision --autogenerate -m ${msg}

upgrade:
	poetry run alembic upgrade +1 

upgrade_up_to:
		# Examples:
		# >>> make upgrade_up_to id=123abc
	poetry run alembic upgrade ${id} 

upgrade_all:
	poetry run alembic upgrade head 

downgrade:
	poetry run alembic downgrade -1

downgrade_up_to:
		# up to but not including this revision
		# Examples:
		# >>> make downgrade_up_to id=123abc
	poetry run alembic downgrade ${id} 

# DANGEROUS
downgrade_all:
	poetry run alembic downgrade base

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
