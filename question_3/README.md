# Question 3
If you are the reviewer of this code block, what’s your thinking?

<img width="727" alt="Screenshot 2025-06-24 at 23 45 12" src="https://github.com/user-attachments/assets/d89903d0-c588-4729-9f60-e44c689b9622" />

## My review (ignoring mock logic)
1. no spacing between lines
2. the code lacks type-hinting
3. line 3, `card_number` is not used
4. line 8, `tx_id`, `amount` not used
5. line 6, `int(time.time())` might not be unique, can use `uuid` instead
6. line 21, `tx_id` is not used
7. functions with name `process` is too general (future devs can put all kind of stuff in it because it's so-called a "general" function). Can change names to `store_transaction` or `charge_and_notify`, unless it's an API view where logic is limited already, but I prefer specific names.
8. `TransactionService.__init__()` can accept `processer` & `sender` type objects to make it more dynamic and dependencies-injection friendly

If applied, result might look like:
```
import uuid
from typing import Protocol


class PaymentProcessor(Protocol):
    def charge(self, amount: float, card_number: str) -> str: ...


class EmailSenderInterface(Protocol):
    def send_receipt(self, email: str, tx_id: str, amount: float) -> None: ...


class StripePaymentProcessor:
    def charge(self, amount: float, card_number: str) -> str:
        print("Connecting to Stripe API...")
        print(f"Charging ${amount} to card ending in {card_number[-4:]}")
        return f"stripe-tx-{uuid.uuid4()}"


class EmailSender:
    def send_receipt(self, email: str, tx_id: str, amount: float) -> None:
        print(f"Sending payment confirmation to {email} for transaction {tx_id} of ${amount}")


class TransactionService:
    def __init__(self, processor: PaymentProcessor, sender: EmailSenderInterface):
        self.processor = processor
        self.sender = sender

    def charge_and_notify(self, amount: float, card_number: str, email: str) -> str:
        tx_id = self.processor.charge(amount, card_number)
        self.sender.send_receipt(email, tx_id, amount)
        return tx_id


def main() -> None:
    service = TransactionService(StripePaymentProcessor(), EmailSender())
    tx_id = service.charge_and_notify(99.99, "4242424242424242", "customer@example.com")
    print(f"Transaction completed: {tx_id}")


if __name__ == "__main__":
    main()

```
