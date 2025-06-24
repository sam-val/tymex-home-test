import logging
from datetime import datetime
from decimal import Decimal
class TransferService:
    def __init__(self, account_repository):
        self.account_repository = account_repository
        self.logger = logging.getLogger(__name__)
    def transfer_money(self, from_account_id: str, to_account_id: str, amount: Decimal) -> bool:
        try:
            # Find source account and check balance
            source_account = self.account_repository.find_by_id(from_account_id)
            if not source_account:
                raise RuntimeError("Source account not found")
            if source_account.balance < amount:
                self.logger.error(f"Insufficient funds in account {from_account_id}")
                return False
            # Find destination account
            destination_account = self.account_repository.find_by_id(to_account_id)
            if not destination_account:
                raise RuntimeError("Destination account not found")
            # Update source account balance
            source_account.balance = source_account.balance - amount
            source_account.last_updated = datetime.now()
            self.account_repository.save(source_account)
            # Update destination account balance
            destination_account.balance = destination_account.balance + amount
            destination_account.last_updated = datetime.now()
            self.account_repository.save(destination_account)
            self.logger.info(f"Transfer of {amount} from account {from_account_id} to {to_account_id} completed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error during transfer: {str(e)}", exc_info=True)
            return False
