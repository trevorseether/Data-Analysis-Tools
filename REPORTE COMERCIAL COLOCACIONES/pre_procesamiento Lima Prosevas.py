# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 09:28:40 2024

@author: sanmiguel38
"""
# =============================================================================
# Preparador del excel para comercial
# =============================================================================
import os
import pandas as pd

#%%
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\DIANA LORENA\\2024 enero\\datos')

lima       = 'CIERRE DRIVE LIMA_ENERO.xlsx'
lima_sheet = 'ENERO24'

proseva       = 'CIERRE DRIVE PROSEVA_ENERO.xlsx'
proseva_sheet = 'ENERO24'

# fincore       = 'CIERRE_FINCORE.xlsx'
# fincore_sheet = 'Rpt_ResumenPrestamosXFuncionari'

fecha_corte = '2024-01-31'

#%%
lima_df = pd.read_excel(io = lima,
                        sheet_name = lima_sheet)

lima_df = lima_df[['FECHA DESEMBOLSO',
                   'FUNCIONARIO/SEDE',
                   'EMPRESA',
                   'CONDICION',
                   'SOCIO',
                   'DOC (DNI/CE/RUC)',
                   'MONTO  PRESTAMO',
                   'CANAL OFICINA',
                   'FECHA DE REVISION',
                   'ANALISTA',
                   'ESTADO FINAL',
                   'PRODUCTO'
                   ]]

mask = lima_df['ESTADO FINAL'] == 'APROBADO'
lima_df['FECHA DESEMBOLSO'] = lima_df.loc[mask, 'FECHA DESEMBOLSO'].fillna(pd.to_datetime(fecha_corte))
lima_df['FECHA DE REVISION'] = lima_df['FECHA DE REVISION'].fillna(pd.to_datetime(fecha_corte))

lima_df['MONTO  PRESTAMO'] = pd.to_numeric(lima_df['MONTO  PRESTAMO'], errors = 'coerce')

lima_df.dropna(subset = ['PRODUCTO', 
                         'FUNCIONARIO/SEDE',
                         'CONDICION',
                         'MONTO  PRESTAMO',
                         'ESTADO FINAL'], inplace = True, how = 'all')

cantidad_nulos = lima_df['ESTADO FINAL'].isnull().sum()

print("Cantidad de valores nulos en 'ESTADO FINAL':", cantidad_nulos)

#%%
proseva_df = pd.read_excel(io = proseva,
                           sheet_name = proseva_sheet)

proseva_df = proseva_df[['FECHA DESEMBOLSO',
                         'FUNCIONARIO/SEDE',
                         'EMPRESA',
                         'CONDICION',
                         'SOCIO',
                         'DOC (DNI/CE/RUC)',
                         'MONTO PRESTAMO',
                         'FECHA DE REVISION',
                         'ANALISTA',
                         'ESTADO FINAL',
                         'CANAL OFICINA',
                         'PRODUCTO'
                         ]]

mask = proseva_df['ESTADO FINAL'] == 'APROBADO'
proseva_df['FECHA DESEMBOLSO'] = proseva_df.loc[mask, 'FECHA DESEMBOLSO'].fillna(pd.to_datetime(fecha_corte))
proseva_df['FECHA DE REVISION'] = proseva_df['FECHA DE REVISION'].fillna(pd.to_datetime(fecha_corte))

proseva_df['MONTO PRESTAMO'] = pd.to_numeric(proseva_df['MONTO PRESTAMO'], errors = 'coerce')

proseva_df.dropna(subset = ['PRODUCTO', 
                            'FUNCIONARIO/SEDE',
                            'CONDICION',
                            'MONTO PRESTAMO',
                            'ESTADO FINAL'], inplace = True, how = 'all')

cantidad_nulos = proseva_df['ESTADO FINAL'].isnull().sum()

print("Cantidad de valores nulos en 'ESTADO FINAL':", cantidad_nulos)

#%%
# creación de carpeta
nombre_carpeta = 'carpeta para sql'

if not os.path.exists(nombre_carpeta):
    os.makedirs(nombre_carpeta)
else:
    print('la carpeta ya existe')
    

# creación de los excels
lima_df.to_excel(f'carpeta para sql\\DXP_LD_{lima_sheet}.xlsx', index = False)

proseva_df.to_excel(f'carpeta para sql\\prosevas_{lima_sheet}.xlsx', index = False)
