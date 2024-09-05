# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 12:55:00 2024

@author: sanmiguel38
"""

import pandas as pd
import os

# =============================================================================
# FUNCIONARIO X SEDE
# =============================================================================
ubi          = 'C:\\Users\\sanmiguel38\\Desktop\\ingresos por cobranza'
nombre_excel = 'Ingresos por Cobranza Agosto-24 - General.xlsx'

#%%
os.chdir(ubi)
df = pd.read_excel(io       = ubi + '\\' + nombre_excel, 
                   skiprows = 0,
                   sheet_name = 'IngCob Agosto24',
                   dtype = str)
df.dropna(subset=['Socio', 
                  'doc_ident',
                  'PagareFincore'], inplace = True, how = 'all') #eliminando las filas vacías

df['CodFuncionario'] = df['CodFuncionario'].str.strip()

#%%
def asignacion_sede(df):
    if df['CodFuncionario'] in ['13','14','15', '16','17','18','19','20','21','22','23','53','78','87']:
        return 'PROSEVA'
    elif df['CodFuncionario'] in ['117','135','138','155','156']:
        return 'AREQUIPA'
    elif df['CodFuncionario'] in ['123','127','141','146','174']:
        return 'LOS OLIVOS'
    elif df['CodFuncionario'] in ['115','133','137','144','151','152','154','170']:
        return 'SANTA ANITA'
    elif df['CodFuncionario'] in ['80']:
        return 'TARAPOTO'
    elif df['CodFuncionario'] in ['61','104','119','145','150','157','166','173']:
        return 'TRUJILLO'
    elif df['CodFuncionario'] in ['1','3','4','7','24','25','26','27','28','32','35',
                                  '36','37','38','39','40','41','47','49','58','76',
                                  '82','84','93','97','98','106','108','111','116',
                                  '122','125','128','136','147','148','153','161',
                                  '167','168','171',]:
        return 'MAGDALENA'
    else:
        return 'NO ASIGNADO'

#aplicamos la función
df['ZONA'] = df.apply(asignacion_sede, axis=1)

#%%
df[['PagareFincore','CodFuncionario', 'Funcionario', 'ZONA']].to_excel('zona.xlsx', index = False)

