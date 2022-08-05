from typing import Sequence

from django import template

# The number of pages
ON_EACH_SIDE: int = 3

register = template.Library()


@register.filter
def page(page_range: Sequence[int], number: int) -> Sequence[int]:
    """Returns fixed `page_range` range iterator of page numbers.

    The `page range` is used for displaying page links for navigation. The
    number of links to include on each side of the `number` link,
    the current page, is determined by the `ON_EACH_SIDE`.
    """
    if number <= ON_EACH_SIDE:
        return page_range[:number + ON_EACH_SIDE]
    else:
        return page_range[number - ON_EACH_SIDE - 1: number + ON_EACH_SIDE]
