import pytest
from services.library_service import borrow_book_by_patron
from database import insert_book, insert_borrow_record


def test_borrow_valid():    # TEST SUCCESS
    success, msg = borrow_book_by_patron("123456", 1)
    assert success
    assert "Successfully borrowed" in msg

def test_invalid_book_id():       # TEST SUCCESS
    success, msg = borrow_book_by_patron("123456", 999)  # ID that doesn't exist
    assert not success
    assert "Book not found" in msg

def test_invalid_patron_id():       # TEST SUCCESS
    success, msg = borrow_book_by_patron("12a45", 1)
    assert not success
    assert "Invalid patron ID" in msg

def test_borrow_invalid_unavailable_book():     # TEST SUCCESS
    success, msg = borrow_book_by_patron("123456", 3)  # ID of the book with 0 copies
    assert not success
    assert "not available" in msg
