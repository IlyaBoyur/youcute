import datetime as dt


def year(request):
    """
    Добавляет переменную с текущим годом.
    """
    return {
        'year': dt.datetime.now().year
    }


def logo_text(request):
    """
    Добавляет логотип в виде текса.
    """
    return {
        'logo_text': "Youcute"
    }
