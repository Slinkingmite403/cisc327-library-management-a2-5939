
import pytest
from unittest.mock import Mock
from services.library_service import pay_late_fees, refund_late_fee_payment
from services.payment_service import PaymentGateway


def test_pay_late_fees_success(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value=('To Kill a Mockingbird', 'Harper Lee', '9780061120084', 2))
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={'fee_amount': 3.50,'days_overdue': 7, 'status': 'Book is overdue'})
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (True, "txn_001", "OK")

    ok, msg, txn = pay_late_fees("123456", 1, mock_gateway)  # To Kill a Mockingbird has book_id -> 1

    assert ok
    assert txn == "txn_001"
    assert msg == "Payment successful! OK"
    mock_gateway.process_payment.assert_called_once_with(
        patron_id="123456",
        amount=3.50,
    )

def test_pay_late_fees_fail(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value=('To Kill a Mockingbird', 'Harper Lee', '9780061120084', 2))
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={'fee_amount': 3.50,'days_overdue': 7, 'status': 'Book is overdue'})
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (False, None, "Something wrong")

    ok, msg, txn = pay_late_fees("123456", 1, mock_gateway)  # To Kill a Mockingbird has book_id -> 1

    assert not ok
    assert not txn
    assert msg == "Payment failed: Something wrong"
    mock_gateway.process_payment.assert_called_once_with(
        patron_id="123456",
        amount=3.50,
    )

def test_pay_late_fees_invalid_patron_id(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value=('To Kill a Mockingbird', 'Harper Lee', '9780061120084', 2))
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={'fee_amount': 3.50,'days_overdue': 7, 'status': 'Book is overdue'})
    mock_gateway = Mock(spec=PaymentGateway)

    ok, msg, txn = pay_late_fees("", 1, mock_gateway)

    assert not ok
    assert "Invalid patron ID" in msg
    assert not txn
    mock_gateway.process_payment.assert_not_called()

def test_pay_late_fees_invalid_book_id(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value=None)
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={'fee_amount': 3.50,'days_overdue': 7, 'status': 'Book is overdue'})
    mock_gateway = Mock(spec=PaymentGateway)

    ok, msg, txn = pay_late_fees("123456", 100, mock_gateway)

    assert not ok
    assert "Invalid book ID" in msg
    assert not txn
    mock_gateway.process_payment.assert_not_called()

def test_pay_late_fees_invalid_fee_amount(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value=('To Kill a Mockingbird', 'Harper Lee', '9780061120084', 2))
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={'fee_amount': 0.00, 'days_overdue': 0, 'status': 'Book was returned on time'})
    mock_gateway = Mock(spec=PaymentGateway)

    ok, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    assert not ok
    assert "No late fees" in msg
    assert not txn
    mock_gateway.process_payment.assert_not_called()

def test_pay_late_fees_network_error(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value=('To Kill a Mockingbird', 'Harper Lee', '9780061120084', 2))
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={'fee_amount': 3.50,'days_overdue': 7, 'status': 'Book is overdue'})
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.side_effect = RuntimeError("Network timeout")

    ok, msg, txn = pay_late_fees("123456", 1, mock_gateway)  # To Kill a Mockingbird has book_id -> 1

    assert not ok
    assert "Payment processing error: Network timeout" in msg
    assert not txn
    mock_gateway.process_payment.assert_called_once_with(
        patron_id="123456",
        amount=3.50,
    )


##############################################################################################################################  
##############################################################################################################################   
##############################################################################################################################   
##############################################################################################################################   
##############################################################################################################################   
##############################################################################################################################  
##############################################################################################################################
  

def test_refund_late_fee_payment_success(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value=('To Kill a Mockingbird', 'Harper Lee', '9780061120084', 2))
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={'fee_amount': 3.50,'days_overdue': 7, 'status': 'Book is overdue'})
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (True, "00001234", "Funds returned to sender")

    ok, msg, rid = refund_late_fee_payment("12345678", 3.50, mock_gateway)

    assert ok
    assert rid == "00001234"
    assert "Refund successful! Funds returned to sender" in msg
    mock_gateway.refund_payment.assert_called_once_with(
        amount=3.50,
    )

def test_refund_late_fee_payment_fail(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value=('To Kill a Mockingbird', 'Harper Lee', '9780061120084', 2))
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={'fee_amount': 3.50,'days_overdue': 7, 'status': 'Book is overdue'})
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (False, None, "Something wrong")

    ok, msg, rid = refund_late_fee_payment("12345678", 3.50, mock_gateway)

    assert not ok
    assert not rid
    assert "Refund failed: Something wrong" in msg
    mock_gateway.refund_payment.assert_called_once_with(
        amount=3.50,
    )

def test_refund_late_fee_payment_invalid_transaction_id(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value=('To Kill a Mockingbird', 'Harper Lee', '9780061120084', 2))
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={'fee_amount': 3.50,'days_overdue': 7, 'status': 'Book is overdue'})
    mock_gateway = Mock(spec=PaymentGateway)

    ok, msg, rid = refund_late_fee_payment("", 3.50, mock_gateway)

    assert not ok
    assert not rid
    assert "Invalid transaction ID" in msg
    mock_gateway.refund_payment.assert_not_called()

def test_refund_late_fee_payment_invalid_refund_amount(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value=('To Kill a Mockingbird', 'Harper Lee', '9780061120084', 2))
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={'fee_amount': 3.50,'days_overdue': 7, 'status': 'Book is overdue'})
    mock_gateway = Mock(spec=PaymentGateway)

    ok, msg, rid = refund_late_fee_payment("12345678", 0.00, mock_gateway)

    assert not ok
    assert not rid
    assert "Invalid fee amount" in msg
    mock_gateway.refund_payment.assert_not_called()

def test_refund_late_fee_payment_network_error(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value=('To Kill a Mockingbird', 'Harper Lee', '9780061120084', 2))
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={'fee_amount': 3.50,'days_overdue': 7, 'status': 'Book is overdue'})
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.side_effect = RuntimeError("Network timeout")

    ok, msg, rid = refund_late_fee_payment("12345678", 3.50, mock_gateway)  # To Kill a Mockingbird has book_id -> 1

    assert not ok
    assert "Refund processing error: Network timeout" in msg
    assert not rid
    mock_gateway.refund_payment.assert_called_once_with(
        amount=3.50,
    )