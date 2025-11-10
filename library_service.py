"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books, get_patron_borrowed_books
)

def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    
    Args:
        title: Book title (max 200 chars)
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Input validation
    if not title or not title.strip():
        return False, "Title is required."
    
    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."
    
    if not author or not author.strip():
        return False, "Author is required."
    
    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."
    
    if len(isbn) != 13:
        return False, "ISBN must be exactly 13 digits."
    
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."
    
    # Check for duplicate ISBN
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."
    
    # Insert new book
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    
    if current_borrowed > 5:
        return False, "You have reached the maximum borrowing limit of 5 books."
    
    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'

def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Process book return by a patron.
    Implements R4 as per requirements

    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
    Returns:
        tuple: (success: bool, message: str)
    """
    # Verify book was borrowed by patron
    if not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID"

    borrowed_books = get_patron_borrowed_books(patron_id)
    book = get_book_by_id(book_id)

    if not book:
        return False, "Invalid book ID"

    borrowed_ids = [b["book_id"] for b in borrowed_books]
    if book_id not in borrowed_ids:
        return False, "Patron has no record of borrowing this book"
    
    # Update available book copies
    availability_success = update_book_availability(book_id, 1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."

    # Reocrd return date
    return_date = datetime.now()
    return_date_update_success = update_borrow_record_return_date(patron_id, book_id, return_date)
    if not return_date_update_success:
        return False, "Database error occured while updating return date"

    # Calculates and displays any late fees owed
    borrowed_record = next((b for b in borrowed_books if b["book_id"] == book_id), None)
    if borrowed_record and borrowed_record["is_overdue"]:
        fee = calculate_late_fee_for_book(patron_id,book_id)
        return True, f"Successfully returned '{book['title]}'. Return date: {return_date.strftime('%Y-%m-%d')}\n\nStatus: {fee['status']}\nDays Overdue: {fee['days_overdue']}\nLate Fee Amount: {fee['fee_amount']}"

    return True, f"Successfully returned '{book["title"]}'. Return date: {return_date.strftime("%Y-%m-%d")}"

def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    """
    Calculate late fees for a specific book.
    Implements R5 as per requirements 

    $0.50/day for first 7 days overdue
    $1.00/day for each additional day after 7 days
    Maximum $15.00 per book
    Returns JSON response with fee amount and days overdue

    Args: 
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
    Returns:
        JSON response with the fee amount and days overdue
    """

    if not patron_id.isdigit() or len(patron_id) != 6 or book_id < 1 or book_id > 6:
        return {'fee_amount': 0.00, 'days_overdue': 0, 'status': 'Invalid ID'}

    borrowed_books = get_patron_borrowed_books(patron_id)
    book_record = next((b for b in borrowed_books if b["book_id"] == book_id), None)

    if not book_record:
        return {'fee_amount': 0.00, 'days_overdue': 0, 'status': 'No such borroed book'}

    due_date = book_record["due_date"]
    days_overdue = (datetime.now() - due_date).days

    if days_overdue <= 0:
        return {'fee_amount': 0.00, 'days_overdue': 0, 'status': 'Book was returned on time'}

    if days_overdue <= 7:
        fee_amount = 0.50 * days_overdue
    else:
        fee_amount = 3.50 + (1.00 * (days_overdue-7))

    if fee_amount > 15.00:
        fee_amount = 15.00
        return {'fee_amount': fee_amount, 'days_overdue': days_overdue, 'status': 'Maximum overdue fee'}

    
    return {    # return the calculated values
        'fee_amount': fee_amount,
        'days_overdue': days_overdue,
        'status': 'Book is overdue'
    }

def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Search for books in the catalog.
    Implements R6 as per requirements

    Args:
        search_term: text to search for
        search_type: 'title', 'author', or 'isbn'
    Returns:

    """

    search_term = search_term.strip()
    search_term = search_term.lower()
    valid_types = {'title','author','isbn'}

    if search_type not in valid_types:
        return []
    
    matches = []
    
    books = get_all_books()
    for book in books:
        if search_type in ("title", "author"):
            # Partial, case insensitive match
            if search_term in book[search_type].lower():
                matches.append(book)
        elif search_type == "isbn":
            # Exact match
            if book["isbn"] == search_term:
                matches.append(book)

    return matches

def get_patron_status_report(patron_id: str) -> Dict:
    """
    Get status report for a patron.
    Implements R7: Patron Status Report

    Args:
        patron_id: 6-digit library card ID
    Returns:
        Dictionary
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {}

    # Get currently borrowed books (active loans)
    borrowed_books = get_patron_borrowed_books(patron_id)
    books_borrowed_count = get_patron_borrow_count(patron_id)

    # Calculate total late fees
    total_late_fees = 0.0
    for b in borrowed_books:
        fee_info = calculate_late_fee_for_book(patron_id, b["book_id"])
        total_late_fees += fee_info.get("fee_amount", 0.0)

    # Prepare list of current borrowed books
    currently_borrowed = []
    for b in borrowed_books:
        currently_borrowed.append({
            "title": b["title"],
            "author": b["author"],
            "due_date": b["due_date"].strftime("%Y-%m-%d"),
            "is_overdue": b["is_overdue"]
        })

    # same?
    borrowing_history = currently_borrowed.copy()

    # Build the final status report
    return {
        "currently_borrowed": currently_borrowed,
        "total_late_fees": round(total_late_fees, 2),
        "books_borrowed_count": books_borrowed_count,
        "borrowing_history": borrowing_history
    }