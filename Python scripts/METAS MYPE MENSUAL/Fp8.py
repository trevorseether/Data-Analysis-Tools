# -*- coding: utf-8 -*-
"""
Created on Fri Oct 18 11:05:49 2024

@author: sanmiguel38
"""

# =============================================================================
# PROCESAMIENTO PARA FP8
# =============================================================================

import os
import pandas as pd

import pyodbc

import warnings
warnings.filterwarnings('ignore')

#%%
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\fp8\\2024\\noviembre')

archivo_base       = 'Rec_30.11.2024_t.xlsx'
archivo_pendientes = 'Mora_29.11.2024_r.xlsx'

fecha_corte        = '2024-11-30' # YYYY-MM-DD

fecha_vencimiento  = '2024-11-20' #fecha 05 o fecha 20 YYYY-MM-DD
numero_proceso     = 'p2' #p1 o p2

unir_datos_desde_sql = False # True o False

#%% DATOS DE LOS EXCELS
base = pd.read_excel(archivo_base,
                     dtype = str)

base['Fincore'] = base['N°\nPréstamo'].str.split('-').str[1]

pendientes = pd.read_excel(archivo_pendientes,
                           dtype = str)
pendientes['Fincore'] = pendientes['N°\nPréstamo'].str.split('-').str[1]

columnas = ['Código\nSocio', 
            'Socio', 
            'DNI', 
            'N°\nPréstamo', 
            'Fincore', 
            'Producto', 
            'Vencido \nDesde', 
            'Empleador', 
            'Planilla', 
            'Funcionario',
            
            'Codigo \nFinalidad']

base       = base[columnas]
pendientes = pendientes[columnas[0:-1]]

#%%
if unir_datos_desde_sql == True:
        
    fecha_corte_sql = fecha_corte.replace('-', '')
    
    conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')
    
    query = f'''
    SELECT 
     	
     	FechaCorte1,
     	Nro_Fincore,
     	TipodeProducto43,
     	administrador,
     	originador,
     	Saldodecolocacionescreditosdirectos24
        
    FROM anexos_riesgos3..ANX06
    WHERE FechaCorte1 = '{fecha_corte_sql}'
    
    '''
    anexo_06 = pd.read_sql_query(query, conn)
    
    del conn
    del fecha_corte_sql
    
    '-------------------------------------------------------------------------'    
    base = base.merge(anexo_06,
                      left_on  = 'Fincore',
                      right_on = 'Nro_Fincore',
                      how      = 'left')
    
    pendientes = pendientes.merge(anexo_06,
                                  left_on  = 'Fincore',
                                  right_on = 'Nro_Fincore',
                                  how      = 'left')

#%% Formato de las fechas y filtrado del mes
base['Fecha Vencimiento']       = pd.to_datetime(base['Vencido \nDesde'],       dayfirst=True, errors='coerce')
pendientes['Fecha Vencimiento'] = pd.to_datetime(pendientes['Vencido \nDesde'], dayfirst=True, errors='coerce')

# filtrando por producto
# base       = base[base['Producto'].isin(            ['PEQUEÑA EMPRESA', 'MICROEMPRESA', 'LIBRE DISPONIBILIDAD'])]
# pendientes = pendientes[pendientes['Producto'].isin(['PEQUEÑA EMPRESA', 'MICROEMPRESA', 'LIBRE DISPONIBILIDAD'])]

fecha_ultimo_dia = pd.Timestamp(fecha_corte)
fecha_primer_dia = pd.Timestamp(fecha_corte[0:8] + '01')

# filtrando del mes
base_filtrado_mes = base[(base['Fecha Vencimiento'] >= fecha_primer_dia)  & (base['Fecha Vencimiento'] <= fecha_ultimo_dia)]
pend_filtrado_mes = pendientes[(pendientes['Fecha Vencimiento'] >= fecha_primer_dia)  & (pendientes['Fecha Vencimiento'] <= fecha_ultimo_dia)]

# verificación de las fechas de vencimiento
fechas_vencimiento = base_filtrado_mes[(base_filtrado_mes['Producto'].isin(['PEQUEÑA EMPRESA', 'MICROEMPRESA', 'LIBRE DISPONIBILIDAD',
                                                                           'PEQUEÑA EMPRESAS', 'MICROEMPRESAS', ''])) &
                                       (base_filtrado_mes['Codigo \nFinalidad'] != '41')   |
                                       (base_filtrado_mes['Codigo \nFinalidad'] == '32')]
print(fechas_vencimiento['Fecha Vencimiento'].unique())
print('''Debe salir como:
['2024-09-05T00:00:00.000000000' '2024-09-20T00:00:00.000000000']''')

#%%
base_filtrado_mes = base[base['Fecha Vencimiento'] == pd.Timestamp(fecha_vencimiento)]
pend_filtrado_mes = pendientes[pendientes['Fecha Vencimiento'] == pd.Timestamp(fecha_vencimiento)]

if (base_filtrado_mes.shape[0] > 0) & (pend_filtrado_mes.shape[0] > 0):
    print('ok')
else:
    print('algo está mal filtrado')

#%%
def identificación_pendientes(df):
    pendientes = list(pend_filtrado_mes['N°\nPréstamo'])
    
    if df['N°\nPréstamo'] in pendientes:
        return 'pendiente'
    else:
        return 'cancelado hasta 8 días'

base_filtrado_mes['Fp8'] = base_filtrado_mes.apply(identificación_pendientes, axis = 1)

#%% TABLA PIVOT
conteo_creditos_fp8 = base_filtrado_mes.pivot_table(index   = 'Funcionario',
                                                    columns = 'Fp8',
                                                    values  = 'N°\nPréstamo',
                                                    aggfunc = 'count').reset_index()
    
conteo_creditos_fp8 = conteo_creditos_fp8.fillna(0)

conteo_creditos_fp8['denominador'] = conteo_creditos_fp8['cancelado hasta 8 días'] + conteo_creditos_fp8['pendiente']
conteo_creditos_fp8['fp8']         = conteo_creditos_fp8['cancelado hasta 8 días'] / conteo_creditos_fp8['denominador']

#%%
columnas = conteo_creditos_fp8.columns + f' {numero_proceso}'
conteo_creditos_fp8.columns = columnas

#%%
conteo_creditos_fp8.to_excel(f'fp8_{fecha_vencimiento}.xlsx',
                             index = False)




