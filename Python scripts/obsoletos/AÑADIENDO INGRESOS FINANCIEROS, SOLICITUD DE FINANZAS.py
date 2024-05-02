# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 15:55:58 2023

@author: sanmiguel38
"""

# =============================================================================
# AÑADIENDO LA COBRANZA AL REPORTE ENVIADO POR CLAUDIA DE FINANZAS
# =============================================================================

principal = 'DpVEM4UvxrHqsJdjU52JGD.xlsx'
cob1 = 'Ingresos por Cobranza Julio-23 - General.xlsx'
cob2 = 'Ingresos por Cobranza Agosto-23 - General.xlsx'
cob3 = 'Ingresos por Cobranza Setiembre-23 - General.xlsx'

directorio = 'C:\\Users\\sanmiguel38\\Desktop\\AÑADIENDO INGRESOS FINANCIEROS'

#%%

import pandas as pd
import os

#%%
os.chdir(directorio)

#%%
princ = pd.read_excel(principal,
                      skiprows = 0,
                      dtype = {'FINCORE'             : str,
                               'REFERENCIA DE ORDEN' : str})

princ['FINCORE'] = princ['FINCORE'].str.strip()

#%%
#PRIMERO
df1 = pd.read_excel(cob1,
                    dtype = {'codigosocio'  : object, 
                             'doc_ident'    : object,
                             'PagareFincore': object} )
#aquí NO hay que eliminar duplicados
#eliminamos columnas vacías
df1.dropna(subset = ['codigosocio', 
                     'doc_ident',
                     'PagareFincore'], 
                                inplace = True, 
                                how     = 'all')
# FUNCIÓN DE AGREGACIÓN
# df1_sum_capital = df1.groupby('PagareFincore')['Capital'].sum().reset_index()
# df1_sum_TOTAL = df1.groupby('PagareFincore')['TOTAL'].sum().reset_index()
df1_sum_INT_OTROS = df1.groupby('PagareFincore')['Ingresos Financ'].sum().reset_index()

df1_sum_INT_OTROS.rename(columns = {'PagareFincore'   : 'fincore_julio',
                                    'Ingresos Financ' : 'Ingresos Financ julio'}, 
                         inplace = True)
###############################################################################
#SEGUNDO
df2 = pd.read_excel(cob2,
                    dtype = {'codigosocio'  : object, 
                             'doc_ident'    : object,
                             'PagareFincore': object} )
#aquí NO hay que eliminar duplicados
#eliminamos columnas vacías
df2.dropna(subset = ['codigosocio', 
                     'doc_ident',
                     'PagareFincore'], 
                                inplace = True, 
                                how     = 'all')
# FUNCIÓN DE AGREGACIÓN
# df2_sum_capital = df1.groupby('PagareFincore')['Capital'].sum().reset_index()
# df2_sum_TOTAL = df1.groupby('PagareFincore')['TOTAL'].sum().reset_index()
df2_sum_INT_OTROS = df2.groupby('PagareFincore')['Ingresos Financ'].sum().reset_index()

df2_sum_INT_OTROS.rename(columns = {'PagareFincore'   : 'fincore_ago',
                                    'Ingresos Financ' : 'Ingresos Financ ago'}, 
                         inplace = True)
###############################################################################
#TERCER
df3 = pd.read_excel(cob3,
                    dtype = {'codigosocio'  : object, 
                             'doc_ident'    : object,
                             'PagareFincore': object} )
#aquí NO hay que eliminar duplicados
#eliminamos columnas vacías
df3.dropna(subset = ['codigosocio', 
                     'doc_ident',
                     'PagareFincore'], 
                                inplace = True, 
                                how     = 'all')
# FUNCIÓN DE AGREGACIÓN
# df3_sum_capital = df1.groupby('PagareFincore')['Capital'].sum().reset_index()
# df3_sum_TOTAL = df1.groupby('PagareFincore')['TOTAL'].sum().reset_index()
df3_sum_INT_OTROS = df3.groupby('PagareFincore')['Ingresos Financ'].sum().reset_index()

df3_sum_INT_OTROS.rename(columns = {'PagareFincore'   : 'fincore_set',
                                    'Ingresos Financ' : 'Ingresos Financ set'}, 
                         inplace = True)

#%%
# MERGE

princ = princ.merge(df1_sum_INT_OTROS,
                         left_on  = ['FINCORE'], 
                         right_on = ['fincore_julio'],
                         how      = 'left')

princ = princ.merge(df2_sum_INT_OTROS,
                         left_on  = ['FINCORE'], 
                         right_on = ['fincore_ago'],
                         how      = 'left')

princ = princ.merge(df3_sum_INT_OTROS,
                         left_on  = ['FINCORE'], 
                         right_on = ['fincore_set'],
                         how      = 'left')

#%% eliminación de columnas

princ.drop(columns = ['fincore_julio', 
                      'fincore_ago', 
                      'fincore_set'], inplace = True)

#%% FILL NA

princ['Ingresos Financ julio'].fillna(0, inplace = True)
princ['Ingresos Financ ago'].fillna(0, inplace = True)
princ['Ingresos Financ set'].fillna(0, inplace = True)

princ['INGRESO FINANCIERO'] = princ['Ingresos Financ julio'] + princ['Ingresos Financ ago'] + princ['Ingresos Financ set']

#%% excel

princ.to_excel('ingresos financieros.xlsx',
               index = False)
