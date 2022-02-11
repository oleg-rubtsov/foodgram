from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_even(value):
    if value < 1:
        raise ValidationError(
            _('%(value)s некорректное время приготовления. Минимум 1.'),
            params={'value': value},
        )
