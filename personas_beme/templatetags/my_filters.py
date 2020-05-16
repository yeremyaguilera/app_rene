from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from info_complementaria.models import PeriodoGracia

register = template.Library()


def bolean_to_value(T_o_F):
    if T_o_F == True:
        return "SI"
    elif T_o_F == False:
        return "NO"
    else:
        return "No hay Informacion"

register.filter('bolean_to_value', bolean_to_value)


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

def num_cuo_to_plazo(num_cuo):
    periodo_de_gracia = PeriodoGracia.objects.all().reverse()[0].periodo_de_gracia
    return num_cuo + periodo_de_gracia

register.filter('num_cuo_to_plazo', num_cuo_to_plazo)

def string_to_num(string):
    num = int(string)
    return num

register.filter('string_to_num', string_to_num)