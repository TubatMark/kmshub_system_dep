from typing import Any
from urllib.parse import urlparse

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import ManyToManyField, ManyToManyRel, ManyToOneRel

# general
related_fields = (
    GenericRelation,
    ManyToManyField,
    ManyToManyRel,
    ManyToOneRel,
)

complex_fields = (ArrayField,)


# class
class UpperTextField(models.TextField):
    """
    A TextField that is stripped and uppercase
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value: Any) -> Any:
        if value:
            return str(value).strip().upper()
        else:
            return value


class NoParamURLField(models.URLField):
    """
    A URLField that parse and keep only netloc and path
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value: Any) -> Any:
        if value is not None:
            tmp = urlparse(value)
            output = tmp.netloc + tmp.path
            return output
        else:
            return None


# for admin.py
list_display_exclude = tuple(list(related_fields) + list(complex_fields))
list_filter_base = ["is_admin_verified"]
list_filter_base_public_contribute = list_filter_base + ["is_verified"]
