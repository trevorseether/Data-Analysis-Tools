# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 10:02:10 2024

@author: sanmiguel38
"""

import pandas as pd
import os

os.chdir('R:\\REPORTES DE GESTIÓN\\DESARROLLO\\Implementacion NetBank\\Datos para Migracion\\Migracion 06Nov24\\2 - Creditos\\02_Prestamos-completo (interés negativo corregido)')
nombre_csv = "prppg (2).csv"   #              "prppg (2).csv"            "prppg.csv"

#%% MONTO DESEMBOLSADO
columnas_desembolsado = ['NumerodePrestamo-1','CodigodeAgencia-2','FechadeRegistro-3','(No column name)-4','(No column name)-5','(No column name)-6','TipoDeCredito-7','(No column name)-8',
                         'Persona_Autoriza-9','Funcionaria_negocio-10','(No column name)-11','(No column name)-12','CodCiuu-13','CodigoDestinoOperacion-14','(No column name)-15','Moneda_Axon-16','MontoAprobado-17',
                         'PlazoDiasAX-18','UnidadPlazoAX-19','(No column name)-20','(No column name)-21','(No column name)-22','(No column name)-23','(No column name)-24','(No column name)-25','DiaPagoFijo-26',
                         'FechaPrimerPago-27','(No column name)-28','SaldoPrestamoAX-29','(No column name)-30','MontoDesembolsadoAX-31','(No column name)-32','CodigoEstadoOperacion-33','FechaIngresoEstadoActual-34',
                         'FechaIngresoEstadoVencido-35','FechaVencimientoOriguinal-36','FechaVencimientoAct-37','(No column name)-38','(No column name)-39','FechaDesembolsoAxon-40','FechaUltipoPagoAX-41','(No column name)-42',
                         '(No column name)-43','(No column name)-44','(No column name)-45','(No column name)-46','(No column name)-47','(No column name)-48','CantReprogramacionesAxon-49','FechaUltReprogramacionAxon-50',
                         '(No column name)-51','(No column name)-52','(No column name)-53','(No column name)-54','(No column name)-55','(No column name)-56','(No column name)-57','(No column name)-58','(No column name)-59',
                         '(No column name)-60','(No column name)-61','(No column name)-62','(No column name)-63','(No column name)-64','(No column name)-65','(No column name)-66','FechaIncumplimientoAxon-67','(No column name)-68',
                         '(No column name)-69','(No column name)-70','(No column name)-71','(No column name)-72','(No column name)-73','(No column name)-74','(No column name)-75','(No column name)-76','(No column name)-77',
                         '(No column name)-78','(No column name)-79','(No column name)-80','(No column name)-81','(No column name)-82','(No column name)-83','(No column name)-84',]

m_desem = pd.read_csv("prmpr.csv", #no cambiar
                      header = None, 
                      names  = columnas_desembolsado,
                      sep    = ';',
                      dtype  = str)

m_desem = m_desem[['NumerodePrestamo-1', 'MontoDesembolsadoAX-31', 'FechaDesembolsoAxon-40', 'Moneda_Axon-16', 'CodigoEstadoOperacion-33']]
m_desem['MontoDesembolsadoAX-31'] = m_desem['MontoDesembolsadoAX-31'].astype(float).round(2)

creds_vigentes = m_desem[['NumerodePrestamo-1', 'CodigoEstadoOperacion-33']]
creds_vigentes = creds_vigentes[creds_vigentes['CodigoEstadoOperacion-33'] != '9']


del columnas_desembolsado

#%% IMPORTAR CSV DE CUOTAS:
col_cuotas = ['NroPrestamo','FechaVencimiento','numerocuota','capital','interes','CargosGenerales','CargosSeguro','Aporte','TotalCargo','TotalPago','Ahorros','Pagado',]

cuotas = pd.read_csv(nombre_csv, #                    "prppg.csv"             "prppg (2).csv"
                     header = None, 
                     names  = col_cuotas,
                     sep = ';',
                     dtype = str)

del col_cuotas
# número de orden del archivo original
cuotas['orden original'] = range(1, len(cuotas) + 1)

cuotas['fecha format'] = pd.to_datetime(cuotas['FechaVencimiento'], format = '%Y-%m-%d') # '%d/%m/%Y') #'%Y-%m-%d')

cuotas['index unico'] = cuotas['NroPrestamo'] + '-' + cuotas['numerocuota'] + '-' + cuotas['orden original'].astype(str)
###############################################################################
for i in ['capital', 'interes', 'Aporte', 'TotalPago']:
    cuotas[i] = cuotas[i].astype(float)
del i    
###############################################################################

def eliminar_ceros(cuotas):
    # si tienen cero en capital, interés, aportes y valor cuota, pues es una reprogramación, pero hay que eliminarlo porque en Axon genera problemas
    if (cuotas['capital'] == 0) and (cuotas['interes'] == 0) and (cuotas['Aporte'] == 0) and (cuotas['TotalPago'] == 0):
        return 'eliminar, puro cero'
    else:
        return ''
cuotas['puro cero'] = cuotas.apply(eliminar_ceros, axis = 1)

#%% observaciones
ubi = 'C:\\Users\\sanmiguel38\\Desktop\\AXON ENVÍO limpieza de datos\\observaciones de las cuotas\\'

observaciones = pd.read_excel(ubi + 'obs_prppg_rev2.xlsx', 
                              dtype = str)

observaciones['NPRE'] = observaciones['NPRE'].astype(str).str.zfill(8)

sin_cuota_cero  = observaciones[observaciones['Detalle'] == 'NO TIENE CUOTA 0 INICIAL (NO SE MIGRA)']
fecha_cuota_dup = observaciones[observaciones['Detalle'] == 'PLAN DE PAGOS CON FECHA DUPLICADA (NO SE MIGRA)']

#%%
cuotas = cuotas.merge(sin_cuota_cero[['NPRE']],
                      left_on  = 'NroPrestamo',
                      right_on = 'NPRE',
                      how = 'left')

def obs(cuotas):
    if pd.isna(cuotas['NPRE']):
        return ''
    else:
        return 'observación'
cuotas['flag observacion'] = cuotas.apply(obs, axis = 1)
del cuotas['NPRE']

#%% AÑADIR CUOTAS CERO
suma_amortizacion = cuotas.pivot_table(values = 'capital',
                                       index  = 'NroPrestamo',
                                       aggfunc = 'sum').reset_index()
suma_amortizacion['capital'] = suma_amortizacion['capital'].round(2)

# añadir el monto desembolsado
suma_amortizacion = suma_amortizacion.merge(m_desem,
                                            left_on = 'NroPrestamo',
                                            right_on = 'NumerodePrestamo-1',
                                            how = 'left')

suma_amortizacion = suma_amortizacion[['NroPrestamo', 'capital','MontoDesembolsadoAX-31']]
suma_amortizacion['diferencia para cuota cero'] = suma_amortizacion['capital'] - suma_amortizacion['MontoDesembolsadoAX-31']


sin_cuota_cero = sin_cuota_cero.merge(suma_amortizacion[['NroPrestamo', 'diferencia para cuota cero']],
                                      left_on  = 'NPRE',
                                      right_on = 'NroPrestamo',
                                      how      = 'left')

#%% primera cuota
min_cuota = cuotas.pivot_table(values  = 'fecha format',
                               index   = 'NroPrestamo',
                               aggfunc = 'min').reset_index()

min_cuota.rename(columns = {'fecha format':'fecha mínima'}, inplace = True)

###################################################################################
from datetime import timedelta                                                   ##
from dateutil.relativedelta import relativedelta                                 ##
                                                                                 ##
def restar_30_dias(fecha):                                                       ##
    # Restar 30 días directamente a objetos datetime/Timestamp                   ##
    nueva_fecha = fecha - timedelta(days=30)                                     ##
    return nueva_fecha                                                           ##
                                                                                 ##
def restar_un_mes(fecha):                                                        ##
    # Restar un mes completo usando relativedelta                                ##
    nueva_fecha = fecha - relativedelta(months=1)                                ##
    return nueva_fecha                                                           ##
                                                                                 ##
min_cuota['Fecha un mes antes'] = min_cuota['fecha mínima'].apply(restar_un_mes) ##
###################################################################################

m_desem['f desembolso formateado'] = pd.to_datetime(m_desem['FechaDesembolsoAxon-40'], format='%d/%m/%Y')

min_cuota = min_cuota.merge(m_desem[['NumerodePrestamo-1','f desembolso formateado']],
                            left_on  = 'NroPrestamo',
                            right_on = 'NumerodePrestamo-1',
                            how      = 'left')

def fecha_cuota_cero(min_cuota):
    if min_cuota['Fecha un mes antes'] > min_cuota['f desembolso formateado']:
        return min_cuota['Fecha un mes antes']
    else:
        return min_cuota['f desembolso formateado']

min_cuota['fecha cuota cero'] = min_cuota.apply(fecha_cuota_cero, axis = 1)

min_cuota_con_observacion = min_cuota[min_cuota['NroPrestamo'].isin(list(sin_cuota_cero['NPRE']))]
print('validar esta parte, sale 207, al probar con el segundo archivo debe salir dataframe de 602')

###############################################################################
min_cuota_con_observacion = min_cuota_con_observacion.merge(suma_amortizacion[['NroPrestamo', 'diferencia para cuota cero']],
                                                            on  = 'NroPrestamo',
                                                            how = 'left')

cuotas_cero_para_incertar = pd.DataFrame()
cuotas_cero_para_incertar['NroPrestamo']      = min_cuota_con_observacion['NroPrestamo']
cuotas_cero_para_incertar['FechaVencimiento'] = min_cuota_con_observacion['fecha cuota cero']
cuotas_cero_para_incertar['numerocuota']      = '0'
cuotas_cero_para_incertar['capital']          =  0
cuotas_cero_para_incertar['interes']          = min_cuota_con_observacion['diferencia para cuota cero'].round(2)
cuotas_cero_para_incertar['CargosGenerales']  = '0'
cuotas_cero_para_incertar['CargosSeguro']     = '0'
cuotas_cero_para_incertar['Aporte']           =  0
cuotas_cero_para_incertar['TotalCargo']       =  0
cuotas_cero_para_incertar['TotalPago']        =  0
cuotas_cero_para_incertar['Ahorros']          = '0'
cuotas_cero_para_incertar['Pagado']           = '9'
cuotas_cero_para_incertar['index unico']      = cuotas_cero_para_incertar['NroPrestamo'] + '-0'
cuotas_cero_para_incertar['EsFaltante']       = True

# fechas de vencimiento en formato string
cuotas_cero_para_incertar['FechaVencimiento'] = cuotas_cero_para_incertar['FechaVencimiento'].dt.strftime('%Y-%m-%d')

cuotas_cero_para_incertar.to_excel('asdasd.xlsx',
                                   index = False)

#%% corrigiendo el interés mayor a cero, de las cuotas cero, (se reemplaza por cero)

# def correccion_cero_int_cuota_cero(df):
#     if df['interes'] > 0:
#         return 0
#     else:
#         return df['interes']
# cuotas_cero_para_incertar['interes'] = cuotas_cero_para_incertar.apply(correccion_cero_int_cuota_cero, axis = 1)

#%%
cuotas_concatenado =  pd.concat([cuotas,cuotas_cero_para_incertar], ignore_index = True)

# falta ordenar la columna
#%%
df_combinado =  pd.concat([cuotas,cuotas_cero_para_incertar], ignore_index = True)

df_combinado['OrdenOriginal'] = df_combinado.index

# Crear un orden personalizado: 
# Primero por 'Crédito', luego asegurando que las filas faltantes queden antes de las originales
df_combinado = df_combinado.sort_values(by=['NroPrestamo', 'EsFaltante', 'OrdenOriginal'], ascending=[True, False, True])

val = df_combinado[(df_combinado['interes'] < 0) & (df_combinado['numerocuota'] == '0')]

#%%
creds_arreglar_prrprg2 = ['00100855','00100907','00100957','00100986', #'00101006',
                          '00101087','00102064','00102067','00102129','00102185',
                          '00103274','00103362','00107002','00108556','00135699',
                          '00135950',] # podría faltar añadir los casos de la primera hoja

corregir_interes = df_combinado[df_combinado['NroPrestamo'].isin(creds_arreglar_prrprg2) & (df_combinado['numerocuota'] == '0')]

para_corregir_interes = pd.DataFrame()
para_corregir_interes['NroPrestamo'] = corregir_interes['NroPrestamo']
para_corregir_interes['int']         = corregir_interes['interes']

df_combinado = df_combinado.merge(para_corregir_interes,
                                  on  = ['NroPrestamo'],
                                  how = 'left')

def ajuste_final_cap_int_para_que_no_haya_int_negativo(df):
    if (df['NroPrestamo'] in creds_arreglar_prrprg2) and (df['numerocuota'] == '1'):
        return  df['capital'] - df['int']
    else:
        return df['capital']

df_combinado['capital'] = df_combinado.apply(ajuste_final_cap_int_para_que_no_haya_int_negativo, axis = 1)


def ajuste_final_cap_int_para_que_no_haya_int_negativo(df):
    if (df['NroPrestamo'] in creds_arreglar_prrprg2) and (df['numerocuota'] == '1'):
        return  df['interes'] + df['int']
    else:
        return df['interes']

df_combinado['interes'] = df_combinado.apply(ajuste_final_cap_int_para_que_no_haya_int_negativo, axis = 1)

del df_combinado['int']

def asignar_cero_en_int_negativo(df):
    if (df['NroPrestamo'] in creds_arreglar_prrprg2) and (df['numerocuota'] == '0'):
        return 0
    else:
        return df['interes']
df_combinado['interes'] = df_combinado.apply(asignar_cero_en_int_negativo, axis = 1)

#%%
m_desem.rename(columns = {'NumerodePrestamo-1':'NroPrestamo'}, inplace = True)

df_combinado = df_combinado.merge(m_desem[['NroPrestamo', 'MontoDesembolsadoAX-31']],
                                  on  = 'NroPrestamo',
                                  how = 'left')

#%% FILTRADo
df_combinado = df_combinado[df_combinado['puro cero'] != 'eliminar, puro cero']
df_combinado = df_combinado[['NroPrestamo', 'FechaVencimiento', 'numerocuota', 'capital', 'interes',
       'CargosGenerales', 'CargosSeguro', 'Aporte', 'TotalCargo', 'TotalPago',
       'Ahorros', 'Pagado']]

#%% arreglo de las fechas

# Convertir la columna de str a datetime y luego a str con el nuevo formato
df_combinado['FechaVencimiento'] = pd.to_datetime(df_combinado['FechaVencimiento']).dt.strftime('%d/%m/%Y')

df_combinado['nro cuota generado'] = df_combinado.groupby('NroPrestamo').cumcount()

#%% VERIFICACIÓN DE QUE SI FALTA CUADRAR ALGO
pivot_todo = df_combinado.pivot_table(values = 'capital',
                                      index  = 'NroPrestamo',
                                      aggfunc = 'sum').reset_index()
pivot_todo['capital'] = pivot_todo['capital'].round(2)

columna_cero = df_combinado[df_combinado['nro cuota generado'] == 0 & (df_combinado['capital'] == 0)][['NroPrestamo', 'interes']]

pivot_todo = pivot_todo.merge(columna_cero,
                              on = 'NroPrestamo',
                              how = 'left')
pivot_todo = pivot_todo.fillna(0)

pivot_todo = pivot_todo.merge(m_desem[['NroPrestamo','MontoDesembolsadoAX-31']],
                              on = 'NroPrestamo',
                              how = 'left')

pivot_todo['dif'] = (pivot_todo['capital'] - pivot_todo['interes']) - pivot_todo['MontoDesembolsadoAX-31']
pivot_todo['dif'] = pivot_todo['dif'].round(2)

verificar = pivot_todo[pivot_todo['dif'] != 0]
verificar = verificar[verificar['NroPrestamo'].isin(list(creds_vigentes['NumerodePrestamo-1']))]

nro_finco = '00089531'
verificar2 = df_combinado[df_combinado['NroPrestamo'] == nro_finco]

#%%
# nombre = nombre_csv.split('.')[0]
# df_combinado.to_excel(f'combinado ordenado ({nombre}).xlsx',
#                       index = False)
# print('guardado ordenado')

#%%
if 1==1:
    print('creando csv')
    # df1[columnas].to_csv(sheet_nombre + '.csv',  #código para el procesamiento de las cuotas
    df_combinado.to_csv('corregido - ' + nombre_csv, 
                        index    =  False,
                        encoding =  'utf-8-sig', #'utf-8',
                        header   =  False,
                        sep      =  ';')
    print('csv creado')

negativos_investigaaaarr = df_combinado[df_combinado['interes'] < 0]
if negativos_investigaaaarr.shape[0] > 0:
    print('investigar interéses negativos')

#%%

# cuotas_concatenado.to_excel(f'combinado no ordenado ({nombre}).xlsx',
#                             index = False)
# print('guardado el no ordenado')

