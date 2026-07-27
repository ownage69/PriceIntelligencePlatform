from decimal import Decimal


def calculate_percentage_change(old_value: Decimal, new_value: Decimal) -> Decimal:
    if not old_value or old_value == Decimal("0"):
        return Decimal("0.00")
    
    change = ((new_value - old_value) / old_value) * Decimal("100")
    return change.quantize(Decimal("0.01"))
