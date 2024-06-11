# myapp/templatetags/custom_tags.py

from django import template

register = template.Library()


@register.filter
def get_comment_rating(existing_comment_rating, comment_id):
    for rating in existing_comment_rating:
        if rating.comment_id == comment_id:
            return rating
    return None
