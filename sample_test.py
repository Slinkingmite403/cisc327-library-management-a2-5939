import pytest
from services.library_service import (
    add_book_to_catalog
)

#def test_add_book_valid_input():        # TEST SUCCESS - Test book is already added into Database. This test will now fail unless library.db is deleted and rebuilt
    #"""Test adding a book with valid input."""
    #success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
    
    #assert success is True
    #assert "successfully added" in message.lower()

#def test_add_book_invalid_isbn_too_short():     # TEST SUCCESS
    #"""Test adding a book with ISBN too short."""
    #success, message = add_book_to_catalog("Test Book", "Test Author", "123456789", 5)
    
    #assert success is False
    #assert "13 digits" in message


# Add more test methods for each function and edge case. You can keep all your test in a separate folder named `tests`.