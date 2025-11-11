import pytest
from services.library_service import get_patron_status_report

def test_status_report_with_valid_patron():     # TEST FAIL
    report = get_patron_status_report("123456")
    assert "currently_borrowed" in report
    assert "total_late_fees" in report
    assert "books_borrowed_count" in report
    assert "borrowing_history" in report

def test_status_report_no_books():      # TEST FAIL
    report = get_patron_status_report("111111")
    assert report["books_borrowed_count"] == 0

def test_status_report_with_late_fees():        # TEST FAIL
    report = get_patron_status_report("222222")
    assert report["total_late_fees"] >= 0

def test_status_report_invalid_patron():
    report = get_patron_status_report("xxxxxx")
    assert report == {} or "error" in report.get("status", "").lower()
