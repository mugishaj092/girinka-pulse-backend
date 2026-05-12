"""Shared utility functions."""
import random
import string
from datetime import date


def generate_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


def years_between(start_date: date, end_date: date = None) -> float:
    if end_date is None:
        end_date = date.today()
    return round((end_date - start_date).days / 365.25, 2)


def format_phone_rw(phone: str) -> str:
    """Normalize Rwandan phone to +250XXXXXXXXX format."""
    phone = phone.strip().replace(" ", "").replace("-", "")
    if phone.startswith("0"):
        phone = "+250" + phone[1:]
    elif phone.startswith("250"):
        phone = "+" + phone
    elif not phone.startswith("+"):
        phone = "+250" + phone
    return phone


def paginate_queryset(queryset, request, paginator):
    page = paginator.paginate_queryset(queryset, request)
    if page is not None:
        return page, True
    return queryset, False
