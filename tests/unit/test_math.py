import pytest
from decimal import Decimal
from app.shared.utils.math import calculate_percentage_change

def test_calculate_percentage_change_zero_old_value():
    assert calculate_percentage_change(Decimal("0"), Decimal("100")) == Decimal("0.00")

def test_calculate_percentage_change_none_old_value():
    assert calculate_percentage_change(None, Decimal("100")) == Decimal("0.00")

def test_calculate_percentage_change_increase():
    res = calculate_percentage_change(Decimal("100"), Decimal("150"))
    assert res == Decimal("50.00")

def test_calculate_percentage_change_decrease():
    res = calculate_percentage_change(Decimal("200"), Decimal("150"))
    assert res == Decimal("-25.00")

def test_calculate_percentage_change_rounding():
    res = calculate_percentage_change(Decimal("3"), Decimal("10"))
    assert res == Decimal("233.33")
    
def test_calculate_percentage_change_no_change():
    res = calculate_percentage_change(Decimal("100.00"), Decimal("100.00"))
    assert res == Decimal("0.00")
