# Question 5
Given this code block

![Screenshot 2025-06-25 at 00 41 09](https://github.com/user-attachments/assets/a89fcdfa-fad4-43c0-86f2-09bca1441aff)

Additional context:
- The application runs on multiple servers behind a load balancer
- During peak times, the system processes hundreds of transfers per second
- Some accounts (like corporate accounts) are involved in many concurrent transfers"
  
What specific issues would you identify in this code, and how would you fix them?

# The issues
## 1. Not commited as a transaction
Two accounts are updated at same time, should be commited to database as a transaction

## 2. Accounts are not locked during update
For high concurrency, should lock the row to ensure data consistency.
Can lock accounts in sorted order to avoid deadlock

## 3. Forget to rollback in the try/except block
When error occurs during transaction, should perform rollback

# Fixed code
This is my fix of the above issues. Assume that we use SQLAlchemy

```python
import logging
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError


class TransferService:
    def __init__(self, account_repository):
        self.account_repository = account_repository
        self.logger = logging.getLogger(__name__)

    def transfer_money(self, db: Session, from_account_id: str, to_account_id: str, amount: Decimal) -> bool:
        try:
            account_ids = sorted([from_account_id, to_account_id])

            with db.begin():  # Transaction block
                # Lock both accounts using FOR UPDATE
                source_account = self.account_repository.find_by_id(
                    db, from_account_id, for_update_no_key=True  # for no key update, less restrictive
                )
                destination_account = self.account_repository.find_by_id(
                    db, to_account_id, for_update_no_key=True   # for no key update, less restrictive
                )

                if not source_account:
                    raise RuntimeError("Source account not found")
                if not destination_account:
                    raise RuntimeError("Destination account not found")

                if source_account.balance < amount:
                    self.logger.error(f"Insufficient funds in account {from_account_id}")
                    return False

                source_account.balance -= amount
                source_account.last_updated = datetime.utcnow()

                destination_account.balance += amount
                destination_account.last_updated = datetime.utcnow()

                self.account_repository.save(db, source_account)
                self.account_repository.save(db, destination_account)

            self.logger.info(f"Transferred {amount} from {from_account_id} to {to_account_id}")
            return True

        except Exception as e:
            db.rollback()
            self.logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return False

```
