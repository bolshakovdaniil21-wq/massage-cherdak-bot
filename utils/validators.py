import re


def validate_phone(phone: str) -> bool:
    cleaned = re.sub(r"[\s\-\(\)]", "", phone)
    return bool(re.match(r"^(\+7|7|8)?9\d{9}$", cleaned))


def format_phone(phone: str) -> str:
    cleaned = re.sub(r"[\s\-\(\)]", "", phone)
    if cleaned.startswith("+7"):
        digits = cleaned[2:]
    elif cleaned.startswith("7") or cleaned.startswith("8"):
        digits = cleaned[1:]
    else:
        digits = cleaned
    if len(digits) == 10:
        return f"+7 ({digits[0:3]}) {digits[3:6]}-{digits[6:8]}-{digits[8:10]}"
    return phone


def validate_name(name: str) -> bool:
    name = name.strip()
    return len(name) >= 2 and any(c.isalpha() for c in name)
