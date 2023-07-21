# -*- coding: utf-8 -*-

import pandas as pd

datos = pd.DataFrame({
    'nombre': ['Juan', 'María', 'Pedro', 'Ana', 'Luis'],
    'edad': [25, 30, 40, 35, 28],
    'fechas': ['20230530', '2023-12-05', '--', '2023-06-08 12:30:45', '2023-06-08 03:45:00 PM'],
    'ciudad': ['Lima', 'Madrid', 'México DF', 'Buenos Aires', 'Santiago']
})

# Aplica la función de análisis personalizada a la columna 'c'
datos['fechas'] = datos['fechas'].astype(str)  # Convierte los valores en la columna 'c' a cadenas

###############################################################################

formatos = ['%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y',
            '%Y%m%d', '%Y-%m-%d', 
            '%Y-%m-%d %H:%M:%S', 
            '%Y/%m/%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S PM',
            '%Y-%m-%d %H:%M:%S AM',
            '%Y/%m/%d %H:%M:%S PM',
            '%Y/%m/%d %H:%M:%S AM']  # Lista de formatos a analizar

def parse_dates(date_str):
    for formato in formatos:
        try:
            return pd.to_datetime(date_str, format=formato)
        except ValueError:
            pass
    return pd.NaT

datos['fechas'] = datos['fechas'].apply(parse_dates)

