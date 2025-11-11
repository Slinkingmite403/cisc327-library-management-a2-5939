
from random import randint
from typing import Tuple, Dict

class PaymentGateway:

    def __init__(self, api_key: str = "test_key_12345"):  # use test api key
        self.api_key = api_key

    def process_payment(self, patron_id: str, amount: float) -> Tuple[bool, str, str]:
        if not patron_id.isdigit() or len(patron_id) != 6:
            return False, None, "Invalid patron ID"
        
        if amount <= 0.00 or amount > 15.00:
            return False, None, "Invalid fee amount"
        
        transaction_id = randint(10000000, 99999999)
        return True, transaction_id, "Late fee payment successful"
        
    def refund_payment(self, amount: float) -> Tuple[bool, str, str]:
        if amount <= 0.00 or amount > 15.00:
            return False, None, "Invalid fee amount"
        
        refund_id = randint(10000000, 99999999)
        return True, refund_id, "Funds returned to sender"