# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 12:19:20 2024

@author: sanmiguel38
"""

# =============================================================================
# DATOS EXPERIAN PARA COMPLETAR DATOS DE EMPRESAS PARA LOS INVERSIONISTAS
# =============================================================================

import pandas as pd
import os
import pyodbc

import warnings
warnings.filterwarnings('ignore')

#%% PARÁMETROS INICIALES
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\FACTORING\\MENSUAL-EXPERIAN\\octubre')

nombre = 'C__inetpub_cliente__ExcelPano_Pano_2158968_45303354_639.txt'
corte  = '2024-10-04' # yyyy-mm-dd

#%% EXCEL DETALLE DEUDORES
ubi_excel    = 'C:\\Users\\sanmiguel38\\Desktop\\FACTORING\\MENSUAL-EXPERIAN\\DATOS PARA INVERSIONISTAS\\SET 2024'
nombre_excel = 'DETALLE DEUDORES FINAL (1).xlsx'
filas_skip   = 1
sheet_nombre = 'Hoja 1'

#%% 
"LECTOR DE .TXT"
experian_data = pd.read_csv(nombre,
                            skiprows = 0,
                            dtype    = {'N. DOCUMENTO' : str})

# "LECTOR DE EXCEL"
# experian_data = pd.read_excel(io       = nombre, 
#                               skiprows = 0,
#                               dtype    = {'N. DOCUMENTO' : str })

#%%
experian_data.drop_duplicates(subset  = 'N. DOCUMENTO', 
                              inplace = True)

#%% calificación (nuevo)
def calficacion(df):
    if df['PER'] > 0:
        return 'PÉRDIDA'
    if df['DUD'] > 0:
        return 'DUDOSO'
    if df['DEF'] > 0:
        return 'DEFICIENTE'
    if df['CPP'] > 0:
        return 'CPP'
    else:
        return 'NORMAL'

experian_data['CALIFICACIÓN'] = experian_data.apply(calficacion, axis = 1)

#%%%
experian_data['N. DOCUMENTO'] = experian_data['N. DOCUMENTO'].str.strip()
experian_data['FechaCorte'] = pd.Timestamp(corte)

experian_data = experian_data[['T. DOCUMENTO',
                               'N. DOCUMENTO',
                               'NOMBRE CPT'  ,
                               'DEUDA SBS'   ,
                               '# ENTIDADES' ,
                               'PROTESTO'    ,  # (nuevo)
                               'CALIFICACIÓN',  # (nuevo)
                               #'SEM. ACT.'   ,
                               'FechaCorte']]

experian_data['N. DOCUMENTO'] = experian_data['N. DOCUMENTO'].str.strip()

#%%
os.chdir(ubi_excel)

excel_para_rellenar = pd.read_excel(io         = nombre_excel, 
                                    sheet_name = sheet_nombre,
                                    skiprows   = filas_skip,
                                    dtype      = str)


excel_para_rellenar['Ruc'] = excel_para_rellenar['Ruc'].str.strip()

excel = excel_para_rellenar[['Ruc', 'Razón social']]

excel = excel.merge(experian_data[['N. DOCUMENTO', 'DEUDA SBS', 'CALIFICACIÓN', 'PROTESTO']],
                    left_on    = 'Ruc',
                    right_on   = 'N. DOCUMENTO',
                    how        = 'left')

#%% no hacen match (para que los incluyan a Experian)

no_match = excel[pd.isna(excel['N. DOCUMENTO'])]

if no_match.shape[0] > 0:
    print('casos que no hacen match:')
    print(no_match.shape[0])
    no_match[['Ruc', 'Razón social']].to_excel('agregar a Experian.xlsx')

#%%
excel.to_excel(f'datos_{corte}.xlsx',
               index = False)


