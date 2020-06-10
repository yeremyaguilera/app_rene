import os
import sys
import django
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reneapp.settings')

django.setup()

from info_complementaria.models import UF

if len(sys.argv) == 2:
    if sys.argv[1] == "update":
        #Limpiamos la base de datos
        for cada_valor_uf in UF.objects.all():
            cada_valor_uf.delete()
        print("Se limpio la BD de UFs")

        df_uf = pd.read_excel("excel_files/UF.xlsx").drop("Unnamed: 0", axis = 1)

        for index, cada_valor_uf in df_uf.iterrows():
            operacion = UF.objects.create(**cada_valor_uf)
        print("Se actualizaron los valores de las UFs con éxito")
        print("El proceso finalizó con éxito")
    else:
        print("Quisiste decir 'update'?")
else:
    print("Debes ingresas un parámetro a ejecutar en insertar_UF")