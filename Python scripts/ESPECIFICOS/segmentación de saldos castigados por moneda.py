# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 17:05:20 2024

@author: sanmiguel38
"""
# =============================================================================
# LECTOR DE DATOS DEL ANEXO06 ANTIGUO
# =============================================================================

import pandas as pd

#%%
ubi        = 'R:\\REPORTES SUCAVE SBS\\FEBRERO 2020'
nombre     = 'ANEXO Nº 6 Febrero 2020.xlsx'
filas_skip = 3

#%%

col_castig = 'Saldos de Créditos Castigados 38/'

datos_anx06 = pd.read_excel(ubi + '\\' + nombre,
                            skiprows   = filas_skip,
                            # sheet_name = 'Rpt_DeudoresSBS',
                            dtype      = {'Numero de Crédito 18/'  : str,
                                          'Moneda del crédito 17/' : str})

datos_anx06['Numero de Crédito 18/']  = datos_anx06['Numero de Crédito 18/'].str.strip()
datos_anx06['Moneda del crédito 17/'] = datos_anx06['Moneda del crédito 17/'].str.strip()

datos_anx06_filtrado = datos_anx06[['Numero de Crédito 18/', 
                                    'Moneda del crédito 17/',
                                    col_castig]]

datos_anx06_filtrado = datos_anx06_filtrado[datos_anx06_filtrado[col_castig] > 0]

#%%
pivot_castigados = datos_anx06_filtrado.pivot_table(values  = col_castig,
                                                    columns = 'Moneda del crédito 17/',
                                                    aggfunc = 'sum')

