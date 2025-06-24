import time
class StripePaymentProcessor:
    def process_stripe_payment(self, amount, card_number):
        print(f"Connecting to Stripe API...")
        print(f"Processing ${amount} payment with Stripe")
        return f"stripe-tx-{int(time.time())}"
class EmailSender:
    def send_confirmation(self, email, tx_id, amount):
        print(f"Sending payment confirmation to {email}")
class TransactionService:
    def __init__(self):
        self.stripe_processor = StripePaymentProcessor()
        self.email_sender = EmailSender()
    def process_transaction(self, amount, card_number, email):
        tx_id = self.stripe_processor.process_stripe_payment(amount, card_number)
        self.email_sender.send_confirmation(email, tx_id, amount)
        return tx_id
# Main Application
def main():
    service = TransactionService()
    tx_id = service.process_transaction(99.99, "dummy-number" , "customer@example.com")
if __name__ == "__main__":
    main()
