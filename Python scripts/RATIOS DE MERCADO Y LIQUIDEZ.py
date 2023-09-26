# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 10:18:16 2023

@author: Joseph Montoya
"""

###############################################################################
#                  REPORTE DE RATIOS DE MERCADO Y LIQUIDEZ                    #
###############################################################################

#%%
from datetime import datetime
import pandas as pd
import calendar
import os
#import pyodbc
#%%
######## UBICACIÓN ############################################################
fecha_txt = 'Agosto - 2023' #escribir el mes que estamos haciendo

ubicacion = 'C:\\Users\\sanmiguel38\\Desktop\\ratios\\2023 AGOSTO'

INSUMO = 'Ratios - Cronogramas de creditos vigentes al 31-Agosto-23 - No incl castigados.xlsx'

# ubicación anexo06 ###########################################################
ubi_anx06 = 'C:\\Users\\sanmiguel38\\Desktop\\TRANSICION  ANEXO 6\\2023 AGOSTO\\fase 3'

anx06 = 'Rpt_DeudoresSBS Anexo06 - AGOSTO 2023 PROCESADO 04 FINAL.xlsx'

filas_skip = 2
#%%
########### INSUMO ############################################################
os.chdir(ubicacion)
df = pd.read_excel(INSUMO,
                   skiprows = 0,
                   dtype    = {'NroPrestamoFincore' : str,
                               'FechaVencimiento'   : str,
                               'CodPrestamoFox'     : str})

df = df.rename(columns={'NroPrestamoFincore': 'NroPrestamo'})

df['NroPrestamo'] = df['NroPrestamo'].astype(str).str.strip()
df = df.rename(columns={"Fecha Vencimiento": "FechaVencimiento"})
df = df.rename(columns={"Moneda Prestamo": "MonedaPrestamo"})

#%%
#parseando la columna de fechas
df["FechaVencimiento"] = df["FechaVencimiento"].astype(str)  # Convierte los valores en la columna 'c' a cadenas
formatos = ['%Y%m%d', '%Y-%m-%d', 
            '%Y-%m-%d %H:%M:%S', 
            '%Y/%m/%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S PM',
            '%Y-%m-%d %H:%M:%S AM',
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y']  # Lista de formatos a analizar
def parse_dates(date_str):
    for formato in formatos:
        try:
            return pd.to_datetime(date_str, format=formato)
        except ValueError:
            pass
    return pd.NaT

df["FechaVencimiento"] = df["FechaVencimiento"].apply(parse_dates)

#%%
'nos quedamos solamente con los de este año:'
df_filtrado = df.query('FechaVencimiento >= "2023-01-01"')

''' ejemplo d un equivalente a Like, para el query
df_filtrado = df.query('FechaVencimiento >= "2023-01-01" and MonedaPrestamo.str.contains("US")')
'''
                                         
#%%
###############################################################################
##  SACAMOS LA LISTA DE CRÉDITOS VIGENTES DEL ANEXO 06
###############################################################################
#usamos este código

anx06_ubi = ubi_anx06 + '\\' + anx06
numeros_fincores = pd.read_excel(anx06_ubi,
                                 skiprows = filas_skip,
                                 dtype = {'Nro Prestamo \nFincore' : object})

fincores = numeros_fincores['Nro Prestamo \nFincore'].tolist()
df_filtrado_2 = df_filtrado[df_filtrado['NroPrestamo'].isin(fincores)]


#%% creando columnas adicionales

df_filtrado['Mes'] = df_filtrado['FechaVencimiento'].dt.month
df_filtrado['Año'] = df_filtrado['FechaVencimiento'].dt.year
df_filtrado['Mes_Texto'] = df_filtrado['FechaVencimiento'].dt.strftime('%B')
df_filtrado['Mes_año'] = df_filtrado['FechaVencimiento'].dt.to_period('M')
df_filtrado['Fecha_Agrupada'] = df_filtrado['Año'].astype(str) + '/' + df_filtrado['Mes_Texto']

#%%
'tabla pivote'
df_filtrado
df_filtrado['Fecha_Agrupada'] = pd.to_datetime(df_filtrado['Fecha_Agrupada'], format='%Y/%B')
df_filtrado = df_filtrado[df_filtrado['Interes'] >= 0]
pivot_table = df_filtrado.pivot_table(columns='MonedaPrestamo',
                                      values=['Capital','Interes'], 
                                      index=['Fecha_Agrupada'],                                      
                                      aggfunc='sum'
                                      )

#%%
pivot_table = pivot_table.reset_index()

pivot_table.columns

#%%

#agregando la columna de años
pivot_table['Años'] = pivot_table['Fecha_Agrupada'].dt.year

#agregando la columna de meses
meses = {1: 'Enero',    2: 'Febrero',   3: 'Marzo',         
         4: 'Abril',    5: 'Mayo',      6: 'Junio', 
         7: 'Julio',    8: 'Agosto',    9: 'Septiembre',    
         10:'Octubre', 11: 'Noviembre',12: 'Diciembre'}

pivot_table['Meses'] = pivot_table['Fecha_Agrupada'].dt.month.map(meses)

#%% dataframe
#ordenamiento por si acaso
pivot_table = pivot_table.sort_values(by='Fecha_Agrupada', ascending=True)

dataframe_final = pivot_table[['Años', 'Meses']]

dataframe_final.loc[:, ('SOLES', 'Capital')] = pivot_table.loc[:, ('Capital', 'S/')]
dataframe_final.loc[:, ('SOLES', 'Interés')] = pivot_table.loc[:, ('Interes', 'S/')]

dataframe_final.loc[:, ('DOLARES', 'Capital')] = pivot_table.loc[:, ('Capital', 'US$')]
dataframe_final.loc[:, ('DOLARES', 'Interés')] = pivot_table.loc[:, ('Interes', 'US$')]

#%%

'CREACIÓN DEL EXCEL'
#primero creamos un excel auxiliar para poner bien las columnas :'v
nombre = "temporal.xlsx"
try:
    ruta = nombre
    os.remove(ruta)
except FileNotFoundError:
    pass

dataframe_final.to_excel(nombre,
                      index=True)

df = pd.read_excel('temporal.xlsx')
df = df.drop(df.columns[0], axis=1)
df = df.drop(1, axis=0)

try:
    ruta = nombre
    os.remove(ruta)
except FileNotFoundError:
    pass

reporte = 'Ratios - Cronogramas ' + fecha_txt + '.xlsx'

try:
    ruta = reporte
    os.remove(ruta)
except FileNotFoundError:
    pass

df.to_excel(reporte,
                      index=False)

