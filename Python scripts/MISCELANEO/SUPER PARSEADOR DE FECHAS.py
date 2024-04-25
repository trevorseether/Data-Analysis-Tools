# -*- coding: utf-8 -*-
"""


@author: Joseph Montoya
"""

###############################################################################
#                        SUPER PARSEADOR DE FECHAS                            #
###############################################################################

import pandas as pd

#%% DataFrame de jemplo
datos = pd.DataFrame(
    {
    'nombre': ['Juan', 'María', 'Pedro', 'Ana', 'Luis'],
    'edad'  : [25, 30, 40, 35, 28],
    'fechas': ['20230530', '2023-12-05', '--', '2023-06-08 12:30:45', '2023-06-08 03:45:00 PM'],
    'ciudad': ['Lima', 'Madrid', 'México DF', 'Buenos Aires', 'Santiago']
    })

# Aplica la función de análisis personalizada a la columna 'fechas'
datos['fechas'] = datos['fechas'].astype(str)  # Convierte los valores en la columna 'fechas' a cadenas

#%%

# Función de análisis de fechas
def parse_dates(date_str):
    '''
    Parameters
    ----------
    date_str : Es el formato que va a analizar dentro de la columna del DataFrame.

    Returns
    -------
    Si el date_str tiene una estructura compatible con los formatos preestablecidos
    para su iteración, la convertirá en un DateTime

    '''
    #formatos en los cuales se tratará de convertir a DateTime
    formatos = ['%d/%m/%Y %H:%M:%S',
                '%d/%m/%Y',
                '%Y%m%d', '%Y-%m-%d', 
                '%Y-%m-%d %H:%M:%S', 
                '%Y/%m/%d %H:%M:%S',
                '%Y-%m-%d %H:%M:%S PM',
                '%Y-%m-%d %H:%M:%S AM',
                '%Y/%m/%d %H:%M:%S PM',
                '%Y/%m/%d %H:%M:%S AM']

    for formato in formatos:
        try:
            return pd.to_datetime(date_str, format=formato)
        except ValueError:
            pass
    return pd.NaT

datos['fechas'] = datos['fechas'].apply(parse_dates)

#%%
nulos = datos[pd.isna(datos['fechas'])]


