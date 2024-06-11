from django.core.validators import RegexValidator

is_numeric = RegexValidator(r"^[0-9]*$", "Only numbers, leading zeros are ok.")
