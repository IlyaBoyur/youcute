from django import template


register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={"class": css})


@register.filter
def uglify(text):
    result = ""
    for i in range(len(text)):
        if (i % 2 == 0):
            result += text[i].lower()
        else:
            result += text[i].upper()
    return result
