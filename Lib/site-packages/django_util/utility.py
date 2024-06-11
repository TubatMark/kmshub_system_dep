from django.utils.functional import lazy
from django.utils.safestring import mark_safe


def is_object_creator(object, profile):
    return object.profile == profile


# deprecated
# https://docs.djangoproject.com/en/3.2/topics/i18n/translation/#other-uses-of-lazy-in-delayed-translations
# https://stackoverflow.com/questions/10706296/how-do-i-input-html-into-the-help-text-of-a-django-form-field
# obsolete as of django v4.1; https://docs.djangoproject.com/en/4.1/releases/4.1/#utilities
mark_safe_lazy = lazy(mark_safe, str)
