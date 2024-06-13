# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 10:52:28 2024

@author: sanmiguel38
"""

# =============================================================================
# DATOS FINANCIEROS MENSUALES PARA FACTORING
# =============================================================================

import pandas as pd
import os

#%%
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\FACTORING\\datos financieros\\mayo')

nombre      = 'Rpt_FacturasxPrestamoFactotingXClienteXAceptantemayo.xlsx'
tc          = 3.734 #3.747
fecha_corte = pd.Timestamp('2024-06-10')

#%%
datos = pd.read_excel(io       = nombre, 
                      skiprows = 12,
                      dtype = { 'RUC\nCliente'   : str,
                                'Nro Factura'    : str,
                                'Ruc\nAceptante' : str })

# Eliminación de columnas Unnamed
datos = datos.loc[:, ~datos.columns.str.contains('^Unnamed')]

datos.dropna(subset = ['RUC\nCliente', 
                       'Cliente'],
             inplace = True,
             how     = 'all')

#%%
datos['FechaCorte'] = pd.Timestamp(fecha_corte)

def tipo_prod(df):
    if pd.isna(df['Aceptante']):
        return 'Confirming'
    else:
        return 'Factoring'
datos['Tipo producto'] = datos.apply(tipo_prod, axis = 1)

def proveedor(df):
    if pd.isna(df['Aceptante']):
        return df['Cliente']
    else:
        return df['Aceptante']
datos['Deudor'] = datos.apply(proveedor, axis = 1)

def ruc_deudor(df):
    if pd.isna(df['Ruc\nAceptante']):
        return df['RUC\nCliente']
    else:
        return df['Ruc\nAceptante']
datos['Ruc Deudor'] = datos.apply(ruc_deudor, axis = 1)

#%% SOLARIZACIÓN
datos['Tipo de Cambio'] = tc
datos['MN'] = datos['MN'].str.strip()

columna = 'Valor Facial Neto'  #'Monto Financiado' #'Valor Facial Neto'
def solarizacion_datos(datos):
    if datos['MN'] == 'US$':
        return datos[columna] * tc
    else:
        return datos[columna]
datos[f'{columna} SOLES'] = datos.apply(solarizacion_datos, axis = 1)
datos[f'{columna} SOLES'] = datos[f'{columna} SOLES'].round(2)

#%% SEGMENTACIÓN POR DÍAS VENCIDOS
def segment_dias(datos):
    if datos['Dias Vencidos'] <= 0:
        return 'A. SIN MORA'

    if datos['Dias Vencidos'] <= 30:
        return 'B. 1 - 30 días'
    if datos['Dias Vencidos'] <= 60:
        return 'C. 31 - 60 días'
    if datos['Dias Vencidos'] <= 90:
        return 'D. 61 - 90 días'
    if datos['Dias Vencidos'] <= 120:
        return 'E. 91 - 120 días'
    if datos['Dias Vencidos'] > 120:
        return 'F. >120 días'

datos['SEGMENTACIÓN'] = datos.apply(segment_dias, axis = 1)

#%%
morosidad_tabla_pivot = datos.pivot_table(values  = f'{columna} SOLES',
                                          index   = 'SEGMENTACIÓN',
                                          aggfunc = 'sum').reset_index()
print(f'{columna} SOLES' + ':')
print(morosidad_tabla_pivot[f'{columna} SOLES'].sum())

#%%
porcentaje_moneda = datos.pivot_table(values  = f'{columna} SOLES',
                                      index   = 'MN',
                                      aggfunc = 'sum').reset_index()

#%%



