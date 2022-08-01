from typing import Sequence

from django import template

# Half range of navigation pages
HALF_RANGE: int = 5

register = template.Library()


@register.filter
def page(page_range: Sequence[int], number: int):
    if number <= HALF_RANGE:
        page_range = page_range[:number + HALF_RANGE]
    else:
        page_range = page_range[number - HALF_RANGE - 1: number + HALF_RANGE]
    return page_range
