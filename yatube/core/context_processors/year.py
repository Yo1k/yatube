from datetime import datetime


def year(request):
    """Adds a variable with the current year."""
    return {
        'year': datetime.now().year
    }
