# Question 6
### Background
You are reviewing a Python implementation of a funds transfer API endpoint. In this system, a Profile
represents a user, and each Profile can own multiple Accounts. Users should only be able to transfer money
from accounts they own.

### Task
Review the following code and identify any security vulnerabilities. Explain what the vulnerability is,
potential consequences, and how you would fix it.

<img width="746" alt="Screenshot 2025-06-25 at 10 29 32" src="https://github.com/user-attachments/assets/ec4d30da-053b-49a6-a908-06a6afaed174" />

# ✅ Answer  
## 🔐 Vulnerabilities

---

### 1. **Lack of Input Validation**

- `amount` might be negative or zero  
- `source_account_id` and `destination_account_id` should not be the same  
- `description` could be too long, null, or potentially malicious  
- `IDs` could be malformed or improperly structured

Proper validation should be in place to ensure data integrity and prevent logic or injection-related issues.


### 2. **No Validation of Source/Destination Accounts**

- The system does not verify whether the source and destination accounts belong to the authenticated user  
- Without this check, an attacker could initiate transfers from someone else’s account  
- Additionally, allowing transfers from an account to itself may lead to unintended behaviors or accounting issues


### 3. **Use of Raw SQL (Best Practice Concern)**

- The code uses raw SQL queries with user-supplied input  
- Even if parameterized, raw SQL is harder to audit and easier to misuse  
- It's best practice to use an ORM (e.g., SQLAlchemy) to reduce the risk of SQL injection and improve maintainability


### 4. **(Optional) Lack of Rate Limiting**

- No rate limiting in place to prevent abuse or spam  
- Implementing API rate limiting (e.g., with Flask-Limiter) helps protect against excessive usage, brute-force attacks, or DoS attempts  
- Might be important for sensitive operations like fund transfers


# Suggested fix

The following code is an attempt to fix the above vulnarabilities

```
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from decimal import Decimal, InvalidOperation
from models import Account   # assume account is from models.py
from database import db  # assume db from database.py

app = Flask(__name__)
jwt = JWTManager(app)

class TransferService:
    def execute_transfer(self, source_account, destination_account, amount, description):
        # Assume rollback/atomicity handled here
        print(f"[Simulated Transfer] {amount} from {source_account.id} to {destination_account.id}")
        return {
            "transaction_id": "TXN12345",
            "status": "COMPLETED"
        }

def validate_transfer_input(profile_id, data):
    print(f"[Simulate] Validating input for user {profile_id}: {data}")

    source_account_id = data.get("source_account_id")
    destination_account_id = data.get("destination_account_id")
    amount_raw = data.get("amount")
    description = data.get("description", "")

    # ...
    # Do validation and raise ValueError if bad input
  
    return {
        "source_account_id": source_account_id,
        "destination_account_id": destination_account_id,
        "amount": amount,
        "description": description,
    }

def check_account_eligibility(source_id: str, dest_id: str, profile_id: str):
    print(f"[Simulate] Checking account access for user {profile_id}: {source_id} → {dest_id}")

    source = db.session.query(Account).filter_by(id=source_id, profile_id=profile_id).first()
    if not source:
        raise PermissionError("Unauthorized access to source account")

    destination = db.session.query(Account).filter_by(id=dest_id).first()
    if not destination:
        raise LookupError("Destination account not found")

    return source, destination

transfer_service = TransferService()

@app.route("/api/transfers/execute", methods=["POST"])
@jwt_required()
def execute_transfer():
    current_profile_id = get_jwt_identity()
    data = request.get_json()

    try:
        validated_data = validate_transfer_input(current_profile_id, data)

        source_account, destination_account = check_account_eligibility(
            validated_data["source_account_id"],
            validated_data["destination_account_id"],
            current_profile_id
        )

        # NOTE: Assume rollback/atomicity handled inside transfer service
        result = transfer_service.execute_transfer(
            source_account,
            destination_account,
            validated_data["amount"],
            validated_data["description"]
        )
        return jsonify(result)

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except PermissionError as pe:
        return jsonify({"error": str(pe)}), 403
    except LookupError as le:
        return jsonify({"error": str(le)}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True)

```

