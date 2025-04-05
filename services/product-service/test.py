import re

@staticmethod
def normalize_unit_price(unit_str):
    if not unit_str:
        return None, None

    try:
        clean_str = ' '.join(str(unit_str).strip().lower().split())

        # Each tuple contains (regex pattern, is_pence)
        patterns = [
            (r'£([\d.]+)\s*per\s*([\w/]+)', False),  # £1.45 per 1L
            (r'([\d.]+)p\s*per\s*([\w/]+)', True),   # 20p per 100ml
            (r'£([\d.]+)\s*/\s*([\w/]+)', False),    # £0.20/100ml
            (r'([\d.]+)\s*p\s*/\s*([\w/]+)', True),  # 20 p / 100ml
            (r'([\d.]+)\s*per\s*([\w/]+)', False),   # 1.45 per litre (assume pounds unless marked p)
        ]

        for pattern, is_pence in patterns:
            match = re.search(pattern, clean_str)
            if match:
                price = float(match.group(1))
                unit = match.group(2).lower()

                if is_pence:
                    price = price / 100
                return price, unit

    except (ValueError, AttributeError, TypeError) as e:
        # Use logging if this isn't inside Flask
        print(f"Failed to parse unit price '{unit_str}': {str(e)}")

    return None, None

    

test_cases = [
    "£1.45 per 1L",
    "20p per 100ml",
    "£0.20/100ml",
    "20 p / 100ml",
    "1.45 per litre"  # Might need additional pattern
]

for case in test_cases:
    price, unit = normalize_unit_price(case)
    print(f"'{case}' -> {price}, {unit}")   