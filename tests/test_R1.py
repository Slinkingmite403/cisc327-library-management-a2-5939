import pytest

from services.library_service import (
    add_book_to_catalog
)

def test_missing_title():
    success, msg = add_book_to_catalog("", "Jane Doe", "1234567890123", 5)
    assert not success
    assert "title is required" in msg.lower()


def test_title_too_long():
    long_title = "T" * 201
    success, msg = add_book_to_catalog(long_title, "Jane Doe", "1234567890123", 5)
    assert not success
    assert "title must be less than 200" in msg.lower()


def test_missing_author():
    success, msg = add_book_to_catalog("A Good Title", "", "1234567890123", 5)
    assert not success
    assert "author is required" in msg.lower()


def test_author_too_long():
    long_author = "A" * 101
    success, msg = add_book_to_catalog("A Good Title", long_author, "1234567890123", 5)
    assert not success
    assert "author must be less than 100" in msg.lower()


def test_isbn_not_13_digits():
    success, msg = add_book_to_catalog("Title", "Author", "12345", 5)
    assert not success
    assert "isbn must be exactly 13" in msg.lower()


def test_total_copies_not_positive():
    success, msg = add_book_to_catalog("Title", "Author", "1234567890123", 0)
    assert not success
    assert "total copies must be a positive integer" in msg.lower()
