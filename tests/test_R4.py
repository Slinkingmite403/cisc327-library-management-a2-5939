import pytest
from services.library_service import return_book_by_patron

def test_return_book_successful():      # TEST SUCCESS
    success, msg = return_book_by_patron("123456", 1)
    assert success is True
    assert "Successfully returned" in msg

def test_return_book_invalid_patron_id():       # TEST SUCCESS
    success, msg = return_book_by_patron("12", 1)
    assert success is False
    assert "Invalid patron" in msg
    
def test_return_book_invalid_book_id():     # TEST SUCCESS
    success, msg = return_book_by_patron("123456", -1)
    assert success is False
    assert "Invalid book" in msg

def test_return_book_not_borrowed():        # TEST SUCCESS
    success, msg = return_book_by_patron("123456", 2)
    assert success is False
    assert "Patron has no record of borrowing this book" in msg
