# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 10:02:10 2024

@author: sanmiguel38
"""

import pandas as pd
import os

os.chdir('R:\\REPORTES DE GESTIÓN\\DESARROLLO\\Implementacion NetBank\\Datos para Migracion\\Migracion 06Nov24\\2 - Creditos\\02_Prestamos-completo')

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

m_desem = pd.read_csv("prmpr.csv", 
                      header = None, 
                      names  = columnas_desembolsado,
                      sep = ';',
                      dtype = str)

m_desem = m_desem[['NumerodePrestamo-1', 'MontoDesembolsadoAX-31', 'FechaDesembolsoAxon-40', 'Moneda_Axon-16', 'CodigoEstadoOperacion-33']]
m_desem['MontoDesembolsadoAX-31'] = m_desem['MontoDesembolsadoAX-31'].astype(float).round(2)

del columnas_desembolsado

#%% cuotas:
col_cuotas = ['NroPrestamo','FechaVencimiento','numerocuota','capital','interes','CargosGenerales','CargosSeguro','Aporte','TotalCargo','TotalPago','Ahorros','Pagado',]

cuotas = pd.read_csv("prppg.csv", #                    "prppg.csv"             "prppg (2).csv"
                     header = None, 
                     names  = col_cuotas,
                     sep = ';',
                     dtype = str)

del col_cuotas
# número de orden del archivo original
cuotas['orden original'] = range(1, len(cuotas) + 1)

cuotas['fecha format'] = pd.to_datetime(cuotas['FechaVencimiento'], format='%Y-%m-%d')

cuotas['index unico'] = cuotas['NroPrestamo'] + '-' + cuotas['numerocuota'] + '-' + cuotas['orden original'].astype(str)
###############################################################################
for i in ['capital', 'interes', 'Aporte', 'TotalPago']:
    cuotas[i] = cuotas[i].astype(float)
del i    
###############################################################################

def eliminar_ceros(cuotas):
    # si tienen cero en capital, interés, aportes y valor cuota, pues es una reprogramación, pero hay que eliminarlo porque en Axon genera problemas
    if (cuotas['capital'] == 0) and (cuotas['interes'] == 0) and(cuotas['Aporte'] == 0) and (cuotas['TotalPago'] == 0):
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
cuotas_cero_para_incertar['capital']          = 0
cuotas_cero_para_incertar['interes']          = min_cuota_con_observacion['diferencia para cuota cero']
cuotas_cero_para_incertar['CargosGenerales']  = '0'
cuotas_cero_para_incertar['Aporte']           = 0
cuotas_cero_para_incertar['TotalCargo']       = 0
cuotas_cero_para_incertar['TotalPago']        = 0
cuotas_cero_para_incertar['Ahorros']          = '0'
cuotas_cero_para_incertar['Pagado']           = '9'
cuotas_cero_para_incertar['index unico']      = cuotas_cero_para_incertar['NroPrestamo'] + '-0'

#%%
cuotas_concatenado =  pd.concat([cuotas,cuotas_cero_para_incertar], ignore_index = True)

# falta ordenar la columna


