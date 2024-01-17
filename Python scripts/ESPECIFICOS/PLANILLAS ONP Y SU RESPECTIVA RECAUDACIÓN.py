# -*- coding: utf-8 -*-
"""
Created on Wed Jan 17 09:49:01 2024

@author: sanmiguel38
"""

import os
import pandas as pd

os.chdir('C:\\Users\\sanmiguel38\\Desktop\\anexos de los últimos 6 meses')

objetos_en_directorio = os.listdir()

archivos_filtrados = [archivo for archivo in objetos_en_directorio \
                      if 'Rpt_DeudoresSBS Anexo06' in archivo]
    
#%%

dicc_dtype = {'Código Socio 7/'        : str,
              'Número de Documento 10/': str,
              'Tipo de Producto 43/'   : str,
              'Nro Prestamo \nFincore' : str}

col_necesarias = ['Apellidos y Nombres / Razón Social 2/',
                  'Código Socio 7/',
                  'Tipo de Documento 9/',
                  'Número de Documento 10/',
                  'Domicilio 12/',
                  'Fecha de Desembolso 21/',
                  'Monto de Desembolso 22/',
                  'Saldo de colocaciones (créditos directos) 24/',
                  'Capital Vigente 26/',
                  'Capital Refinanciado 28/',
                  'Capital Vencido 29/',
                  'Capital en Cobranza Judicial 30/',
                  'Dias de Mora 33/',
                  'Saldos de Créditos Castigados 38/',
                  'Tipo de Producto 43/',
                  'TIPO DE PRODUCTO TXT',
                  'Número de Cuotas Programadas 44/',
                  'Número de Cuotas Pagadas 45/',
                  'FEC_ULT_REPROG',
                  'PLAZO_REPR',
                  'TIPO_REPRO',
                  'PLAZO REPRO ACUMULADO',
                  'NRO CUOTAS REPROG CANCELADAS',
                  'NRO REPROG',
                  'Fecha Castigo TXT',
                  'Dscto Enviado TXT',
                  'Desc Pagado TXT',
                  'Fecha Ultimo \nPago TXT',
                  'Nro Prestamo \nFincore',
                  'PLANILLA CONSOLIDADA',
                  'Departamento',
                  'Provincia',
                  'Distrito',
                  'Funcionario Origuinador',
                  'Funcionario Actual']

#%%
dic = pd.read_excel(io       = 'Rpt_DeudoresSBS Anexo06 - Diciembre 2023 - campos ampliados version final v4.xlsx',
                    skiprows = 2,
                    dtype    = dicc_dtype )

dic.dropna(subset = {'Apellidos y Nombres / Razón Social 2/'}, inplace = True)

dic = dic[col_necesarias]

#%%
dic_onp = dic[(dic['PLANILLA CONSOLIDADA'].str.contains('ONP - DEC', 
                                                        na = False,
                                                        case = False))]

dic_onp_60 = dic_onp[dic_onp['Dias de Mora 33/'] > 60]
dic_onp_60['FECHA_CORTE'] = pd.Timestamp('2023-12-31')

#%%
nov = pd.read_excel(io       = 'Rpt_DeudoresSBS Anexo06 - Noviembre 2023 - campos ampliados v03.xlsx',
                    skiprows = 2,
                    dtype    = dicc_dtype )

nov.dropna(subset = {'Apellidos y Nombres / Razón Social 2/'}, inplace = True)
nov = nov[col_necesarias]
nov_onp = nov[(nov['PLANILLA CONSOLIDADA'].str.contains('ONP - DEC', 
                                                        na = False,
                                                        case = False))]

nov_onp_60 = nov_onp[nov_onp['Dias de Mora 33/'] > 60]
nov_onp_60['FECHA_CORTE'] = pd.Timestamp('2023-11-30')

#%%
octu = pd.read_excel(io       = 'Rpt_DeudoresSBS Anexo06 - Octubre 2023 - campos ampliados FINAL 02.xlsx',
                    skiprows = 2,
                    dtype    = dicc_dtype )

octu.dropna(subset = {'Apellidos y Nombres / Razón Social 2/'}, inplace = True)

octu['PLANILLA CONSOLIDADA'] = octu['Nombre PlanillaTXT']
def planilla_consolidada(df):
    if df['PLANILLA CONSOLIDADA'] == 'PLANILLA LIQUIDADOS':
        return df['Planilla Anterior TXT']
    else:
        return df['PLANILLA CONSOLIDADA']
    
octu['PLANILLA CONSOLIDADA'] = octu.apply(planilla_consolidada, 
                                          axis=1)    

octu = octu[col_necesarias]
octu_onp = octu[(octu['PLANILLA CONSOLIDADA'].str.contains('ONP - DEC', 
                                                        na = False,
                                                        case = False))]

octu_onp_60 = octu_onp[octu_onp['Dias de Mora 33/'] > 60]
octu_onp_60['FECHA_CORTE'] = pd.Timestamp('2023-10-31')
#%%
seti = pd.read_excel(io       = 'Rpt_DeudoresSBS Anexo06 - setiembre 2023 - campos ampliados v04.xlsx',
                    skiprows = 2,
                    dtype    = dicc_dtype )

seti.dropna(subset = {'Apellidos y Nombres / Razón Social 2/'}, inplace = True)

seti['PLANILLA CONSOLIDADA'] = seti['Nombre PlanillaTXT']    
seti['PLANILLA CONSOLIDADA'] = seti.apply(planilla_consolidada, 
                                          axis=1)    

seti = seti[col_necesarias]
seti_onp = seti[(seti['PLANILLA CONSOLIDADA'].str.contains('ONP - DEC', 
                                                        na = False,
                                                        case = False))]

seti_onp_60 = seti_onp[seti_onp['Dias de Mora 33/'] > 60]
seti_onp_60['FECHA_CORTE'] = pd.Timestamp('2023-09-30')

#%%
agos = pd.read_excel(io       = 'Rpt_DeudoresSBS Anexo06 - AGOSTO 2023 PROCESADO 06 FINAL.xlsx',
                    skiprows = 2,
                    dtype    = dicc_dtype )

agos.dropna(subset = {'Apellidos y Nombres / Razón Social 2/'}, inplace = True)

agos['PLANILLA CONSOLIDADA'] = agos['Nombre PlanillaTXT']    
agos['PLANILLA CONSOLIDADA'] = agos.apply(planilla_consolidada, 
                                          axis=1)    

agos = agos[col_necesarias]
agos_onp = agos[(agos['PLANILLA CONSOLIDADA'].str.contains('ONP - DEC', 
                                                        na = False,
                                                        case = False))]

agos_onp_60 = agos_onp[agos_onp['Dias de Mora 33/'] > 60]
agos_onp_60['FECHA_CORTE'] = pd.Timestamp('2023-08-31')

#%%
juli = pd.read_excel(io       = 'Rpt_DeudoresSBS Anexo06 - JULIO 2023 Versión Final.xlsx',
                    skiprows = 2,
                    dtype    = dicc_dtype )

juli.dropna(subset = {'Apellidos y Nombres / Razón Social 2/'}, inplace = True)

juli['PLANILLA CONSOLIDADA'] = juli['Nombre PlanillaTXT']    
juli['PLANILLA CONSOLIDADA'] = juli.apply(planilla_consolidada, 
                                          axis=1)    

juli = juli[col_necesarias]
juli_onp = juli[(juli['PLANILLA CONSOLIDADA'].str.contains('ONP - DEC', 
                                                        na = False,
                                                        case = False))]

juli_onp_60 = juli_onp[juli_onp['Dias de Mora 33/'] > 60]
juli_onp_60['FECHA_CORTE'] = pd.Timestamp('2023-07-31')

#%%
# recaudación diciembre
os.chdir('cobranzas')
rec_dic = pd.read_excel(io = 'Ingresos por Cobranza Diciembre-23 - General.xlsx', 
                        dtype = {'PagareFincore': str})

rec_dic['PagareFincore'] = rec_dic['PagareFincore'].str.strip()
total_dic = rec_dic.pivot_table(values = 'TOTAL',
                                index = 'PagareFincore')

total_dic = total_dic.reset_index()

#%% rec noviembre
rec_novi = pd.read_excel(io = 'Ingresos por Cobranza Noviembre-23 - General.xlsx', 
                        dtype = {'PagareFincore': str})

rec_novi['PagareFincore'] = rec_novi['PagareFincore'].str.strip()
total_novi = rec_novi.pivot_table(values = 'TOTAL',
                                index = 'PagareFincore')

total_novi = total_novi.reset_index()

#%% rec octubre
rec_octu = pd.read_excel(io = 'Ingresos por Cobranza Octubre-23 - General.xlsx', 
                        dtype = {'PagareFincore': str})

rec_octu['PagareFincore'] = rec_octu['PagareFincore'].str.strip()
total_octu = rec_octu.pivot_table(values = 'TOTAL',
                                index = 'PagareFincore')

total_octu = total_octu.reset_index()

#%% rec setiembre
rec_seti = pd.read_excel(io = 'Ingresos por Cobranza Setiembre-23 - General.xlsx', 
                        dtype = {'PagareFincore': str})

rec_seti['PagareFincore'] = rec_seti['PagareFincore'].str.strip()
total_seti = rec_seti.pivot_table(values = 'TOTAL',
                                index = 'PagareFincore')

total_seti = total_seti.reset_index()

#%% rec agosto
rec_agos = pd.read_excel(io = 'Ingresos por Cobranza Agosto-23 - General.xlsx', 
                        dtype = {'PagareFincore': str})

rec_agos['PagareFincore'] = rec_agos['PagareFincore'].str.strip()
total_agos = rec_agos.pivot_table(values = 'TOTAL',
                                index = 'PagareFincore')

total_agos = total_agos.reset_index()

#%% rec julito
rec_juli = pd.read_excel(io = 'Ingresos por Cobranza Julio-23 - General.xlsx', 
                        dtype = {'PagareFincore': str})

rec_juli['PagareFincore'] = rec_juli['PagareFincore'].str.strip()
total_juli = rec_juli.pivot_table(values = 'TOTAL',
                                index = 'PagareFincore')

total_juli = total_juli.reset_index()

#%%
# merge
diciembre = dic_onp_60.merge(total_dic,
                             left_on = 'Nro Prestamo \nFincore',
                             right_on = 'PagareFincore',
                             how = 'left')
del diciembre['PagareFincore']
diciembre['TOTAL'].fillna(0, inplace = True)

#################################################
noviembre = nov_onp_60.merge(total_novi,
                             left_on = 'Nro Prestamo \nFincore',
                             right_on = 'PagareFincore',
                             how = 'left')
del noviembre['PagareFincore']
noviembre['TOTAL'].fillna(0, inplace = True)

#################################################
octubre = octu_onp_60.merge(total_octu,
                             left_on = 'Nro Prestamo \nFincore',
                             right_on = 'PagareFincore',
                             how = 'left')
del octubre['PagareFincore']
octubre['TOTAL'].fillna(0, inplace = True)

#################################################
setiembre = seti_onp_60.merge(total_seti,
                             left_on = 'Nro Prestamo \nFincore',
                             right_on = 'PagareFincore',
                             how = 'left')
del setiembre['PagareFincore']
setiembre['TOTAL'].fillna(0, inplace = True)

#################################################
agosto = agos_onp_60.merge(total_agos,
                             left_on = 'Nro Prestamo \nFincore',
                             right_on = 'PagareFincore',
                             how = 'left')
del agosto['PagareFincore']
agosto['TOTAL'].fillna(0, inplace = True)

#################################################
julio = juli_onp_60.merge(total_juli,
                             left_on = 'Nro Prestamo \nFincore',
                             right_on = 'PagareFincore',
                             how = 'left')
del julio['PagareFincore']
julio['TOTAL'].fillna(0, inplace = True)

#%%
# concatenado
concatenado = pd.concat([julio, agosto, setiembre,
                         octubre, noviembre, diciembre], ignore_index=True)

concatenado.to_excel('ONP mayor a 60 días.xlsx',
                     index = False)
