from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

def currency(dollars):
    dollars = int(dollars)
    return "$ %s" % (intcomma(dollars))

register.filter('currency', currency)


def celular(number):
    if number != 0:
        pais = str(number)[:2]
        cel = str(number)[2]
        numero = str(number)[3:]
        return "+ %s %s %s" % (pais, cel, numero)
    else:
        return "No hay información"
    

register.filter('celular', celular)


def telefono_fijo(number):
    if number != 0:
        pais = '56'
        if len(str(number).split("0"))>=2:
            cel = str(number).split("0")[1]
            numero = str(number)[-7:]
        else:
            cel = str(number)
            numero = ""
        return "+ %s %s %s" % (pais, cel, numero)
    else:
        return "No hay información"

register.filter('telefono_fijo', telefono_fijo)


def porcentaje(number):
    number = round(number*100, 2)
    return "{} %".format(number)

register.filter('porcentaje', porcentaje)