# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 18:07:32 2024

@author: sanmiguel38
"""

# =============================================================================
# LÍNEA ASIGNADA VS LÍNEA CONSUMIDA
# =============================================================================

import pandas as pd
import os
import pyodbc

import warnings
warnings.filterwarnings('ignore')

#%%
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\FACTORING\\lineas consumidas\\junio\\17 06 2024')
nombre           = 'Rpt_LineaAsignadaXLineaConsumidaXFecha17062024 (1).xlsx'
filas_skip       = 8
tipo_cambio      = 3.77
fecha_corte      = '2024-05-17'
CARGA_SQL_SERVER = True

#%%
lineas = pd.read_excel(io = nombre, 
                       skiprows = filas_skip)

# Eliminación de columnas Unnamed
lineas = lineas.loc[:, ~lineas.columns.str.contains('^Unnamed')]

lineas.dropna(subset = ['Fecha Reporte', 
                        'Producto'],
             inplace = True,
             how     = 'all')

#%%
lineas = lineas.fillna(0)

lineas['Porcentaje de utilización'] = lineas['Linea Ocupada Total (S/.)'] / lineas['Linea Asignada (S/.)']

#%%
formatos = [ '%d/%m/%Y %H:%M:%S',
             '%d/%m/%Y',
             '%Y%m%d',
             '%Y-%m-%d',
             '%Y-%m-%d %H:%M:%S',
             '%Y/%m/%d %H:%M:%S',
             '%Y-%m-%d %H:%M:%S PM',
             '%Y-%m-%d %H:%M:%S AM',
             '%Y/%m/%d %H:%M:%S PM',
             '%Y/%m/%d %H:%M:%S AM' ] # Lista de formatos a analizar

def parse_date(date_str):
    for formato in formatos:
        try:
            return pd.to_datetime(   arg = date_str, 
                                  format = formato,)
        except ValueError:
            pass
    return pd.NaT

lineas['Fecha Reporte'] = lineas['Fecha Reporte'].apply(parse_date)

lineas['FechaCorte'] = pd.Timestamp(fecha_corte)

#%%
lineas = lineas[['FechaCorte',
                 'Producto',
                 'Deudor',
                 'Linea Asignada (S/.)',
                 'Linea Ocupada Total (S/.)',
                 'Porcentaje de utilización']]

