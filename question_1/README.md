# Question 1
```
Using Java or Python, implement an idempotency key mechanism for a RESTful API that processes
payment transactions.

Your implementation should:
1. Accept an idempotency key in API requests
2. Store the request and response associated with each idempotency key
3. Return the payment transaction response when the same idempotency key is reused
4. Handle concurrent requests with the same idempotency key correctly
5. Set appropriate expiration for stored idempotency keys
```

# Async FastAPI Server

A async fastapi server that fulfills 5 of the above requirements:

1. [API accepts itempotency_id](#️-endpoints)
2. [Store the request and response in table](#model)
3. [Return the payment transaction response when the same idempotency key is reused](#️-endpoints)
4. [Handle concurrent requests with the same idempotency key correctly](#handling-of-concurrency-requirement-4)
5. [Set appropriate expiration for stored idempotency keys](#expired-idempotency)

*repo uses a template from [another repo of mine](https://github.com/sam-val/fastapi-django-like-template)

## 📚 Table of Contents

- [✨ Features](#-features)
- [🛠️ Quick Start](#️-quick-start)
- [🛠️ API](#️-endpoints)
- [⚙️ Makefile Commands](#️-makefile-commands)

## ✨ Features

- Django-style folder layout (`apps/`, `api/`, `config/`)
- Versioned APIs (`v1`, `v2`, etc.)
- [`poetry`](https://python-poetry.org/) for dependency management
- [`alembic`](https://alembic.sqlalchemy.org/) for database migrations
- [`pytest`](https://docs.pytest.org/) for testing
- Built-in support for [`pre-commit`](https://pre-commit.com/)
- IPython shell (`make shell`) similar to Django's shell
- Developer-friendly `Makefile` commands for common tasks

## 🛠️ Quick Start
### Depedencies: `Python3.13`, `poetry`, `make` (for Makefile)

### 🔧 Install Poetry

If you don't have Poetry, install it using the [official instructions](https://python-poetry.org/docs/#installation). For most systems, this works:

**MacOS/Linux:**

```bash
curl -sSL https://install.python-poetry.org | python3.13 -
```

You may need to restart your shell or manually add Poetry to your PATH. Add the following to your .bashrc, .zshrc, or equivalent:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Then restart your terminal and verify it works:

```bash
poetry --version
```

### 🔧 Init dependencies 
```bash
# at root dir
poetry env use python3.13
poetry install --no-root
```

### Run Server

Start the local server with:

```bash
make run_dev # (with make)
# or
poetry run fastapi dev
```

This will start the server at `localhost:8000`

## 🛠️ Endpoints 
The server comes with Swagger UI. You can check & play with the APIs docs on: `localhost:8000/docs`

### Detail

<details>
 <summary><code>POST</code> <code><b>/api/payment/v1/payments/</b></code>

 <code>(process payments)</code></summary>


##### Payload

> | name     | type     | data type | description          | example            |
> | -------- | -------- | --------- | -------------------- | ------------------ |
> | idempotency_id | required | str     |  idempotency from client, for this test, string will do | 123           |
> | request_data | required | str       | for this test, string will do             | !whGRZ4q%B\*x7x7uS |

##### Responses

> | http code | content-type       | response                       |
> | --------- | ------------------ | ------------------------------ |
> | `201`     | `application/json` | `{ "data": { "response_data": "!whGRZ4q%B\*x7x7uS" }, "message": "Success" }` |
> | `409`     | `application/json` | `{"detail": "Resource already exists"}` |


##### Example cURL

> ```bash
> curl -X 'https://localhost:8000/api/payment/v1/payments/' \
> --header 'Content-Type: application/json' \
> --data '{
>    "idempotency_id": "123",
>    "request_data": "request data"
> }'
> ```

</details>

``This api tries to fulfill the requirement. It stores the request & response data (here simplified as string) based on idempotency id.``

### Expired Idempotency

``
If the idempotency expires, it returns 409 since record with same idempotency exists and response is no longer valid
``

### Expiry Time Config
Can be configured in `apps/payments/constants.py`
For this test I make it a small amout of time
```bash
# apps/payments/constants.py
IDEMPOTENCY_EXPIRY_SECONDS = 20
```

### Handling of concurrency (requirement #4)

If there is two (or more) requests happening at the same time, the second request will fail thanks to the DB constraint on the IdempotencyKey table (`idempotency_id is set as primary key`)

## Model
To keep this simple, I make one model, enough to fulfill the requirement

### Idempotency Key
```
class IdempotencyKey(SQLModel, table=True):
    key: str = Field(primary_key=True)
    request_data: str  # for this test, simplify data as string
    response_data: str
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now() + timedelta(seconds=IDEMPOTENCY_EXPIRY_SECONDS)
    )
```


## ⚙️ Makefile Commands (extra)

Use `make <command>` to run common development tasks:

```make
make run_dev         # Start the FastAPI app
make migrations     # Run Alembic migration files
make upgrade        # Upgrade Alembic migration
make downgrade      # Downgrade Alembic migration
make shell          # Start an interactive shell (IPython)
make test_all       # Run tests with pytest
```
