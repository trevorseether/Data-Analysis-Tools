# -*- coding: utf-8 -*-

"""
Created on Wed Feb  8 11:37:33 2023

@author: Joseph Montoya
"""
# =============================================================================
# .............................................................................
# ........####...##..##..######..##..##...####............####.....##..........
# .......##..##..###.##..##.......####...##..##..........##..##...##...........
# .......######..##.###..####......##....##..##..........##..##..#####.........
# .......##..##..##..##..##.......####...##..##..........##..##..##..##........
# .......##..##..##..##..######..##..##...####............####....####.........
# .............................................................................
# =============================================================================

 #%% IMPORTACIÓN DE MÓDULOS

import pandas as pd
import os
import calendar
# import numpy as np
from datetime import datetime #, timedelta
from colorama import Back # , Style, init, Fore
import pyodbc
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# validar que se hayan retirado del anexo06 los créditos vendidos en el mes respectivo **********
# si es que se han vendido créditos claro
# =============================================================================

#%% ADVERTENCIA
#REVISAR EN EL EXCEL ANTES DE EMPEZAR A PROCESAR:

"periodo de gracia por Reprog inicio"
"periodo de gracia por Reprog Término"

#deben estar en formato de fecha

#%% PARÁMETROS INICIALES

# DIRECTORIO DE TRABAJO ########################################################
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\TRANSICION  ANEXO 6\\2024\\2024 mayo')
################################################################################

# ANEXO PRELIMINAR (el que se hace junto a los reprogramados) #######################
anexo_del_mes = "Rpt_DeudoresSBS Anexo06 - Mayo 2024 - campos ampliados procesado 01.xlsx"
#####################################################################################

# CALIFICACIÓN REFINANCIADOS: (este es el archivo de la calificación que añade Enrique manualmente) ####################
archivo_refinanciados = 'REFINANCIADOS RECLASIFICADOS 31 05 2024 nuevmente.xlsx' #nombre del archivo de los refinanciados ########
########################################################################################################################

# Cuando Enrique nos manda la calificación de los refinanciados, debemos eliminar las demás
# columnas en ese excel y solo quedarnos con el mes que necesitamos:
#################################################################################################
mes_calif = 'Mayo' # aqui debemos poner el mes donde esté la calificación más reciente       ###
# es el nombre de la columna más reciente que nos manda Enrique                               ###
#################################################################################################

###############################################
uit = 5150 #valor de la uit en el año 2023  ###
###############################################

# FECHA DE CORTE #######################################
fecha_corte     = '2024-05-31' #ejemplo '2023-06-30' ###
fech_corte_txt  = 'Mayo 2024'
########################################################

#%% Códigos de los productos
prod43_mype = [15,16,17,18,19,             '15','16','17','18','19',
               21,22,23,24,25,26,27,28,29, '21','22','23','24','25','26','27','28','29',
               95,96,97,98,99,             '95','96','97','98','99']

prod_dxp  = [34, 35, 36, 37, 38, 39]
prod_ld   = [30, 31, 32, 33]
prod_mic  = [20, 21, 22, 23, 24, 25, 26, 29]
prod_peq  = [15, 16, 17, 18, 19]
prod_med  = [95, 96, 97, 98, 99]
prod_hip  = [41, 45]

#%% ESTABLECER FECHA CORTE

#esta función nos permite obtener el número de días del mes de corte
def dias_en_mes(fecha):
    # Convertimos la fecha en formato de cadena a objeto datetime
    fecha_objeto = datetime.strptime(fecha, '%Y-%m-%d')
    
    # Obtenemos el número de días del mes utilizando el método monthrange del módulo calendar
    # esta linea desempaqueta una tupla y descarta el primer valor
    _, dias_en_el_mes = calendar.monthrange(fecha_objeto.year, fecha_objeto.month)
    # dias_en_el_mes = calendar.monthrange(fecha_objeto.year, fecha_objeto.month)[1] #alternativa al código anterior
    
    # Retornamos el número de días en el mes
    return dias_en_el_mes

dias_corte = dias_en_mes(fecha_corte)

#%% FUNCIÓN PARA FORMATEAR FECHAS
#3
#función que transforma fechas en formato '18/01/2023 y devuelve 20230118'
'''
def convertir_formato_fecha(fecha):
    fecha = pd.to_datetime(fecha, format='%d/%m/%Y') #aqui podemos cambiar el formato
    fecha = fecha.strftime('%Y%m%d')
    return fecha

#dataframe de ejemplo
df = pd.DataFrame({'Fecha': ['18/01/2023', '19/01/2023', '20/01/2023']})

#aplicación de ejemplo
df['Fecha'] = df['Fecha'].apply(convertir_formato_fecha)
'''

#%% IMPORTACIÓN DE ARCHIVOS
#5
df1 = pd.read_excel(anexo_del_mes,
                   dtype = {'Registro 1/'                   : object, 
                            'Fecha de Nacimiento 3/'        : object,
                            'Código Socio 7/'               : object,
                            'Tipo de Documento 9/'          : object,
                            'Número de Documento 10/'       : object,
                            'Relación Laboral con la Cooperativa 13/'       : object, 
                            'Código de Agencia 16/'         : object,
                            'Moneda del crédito 17/'        : object, 
                            'Numero de Crédito 18/'         : object,
                            'Tipo de Crédito 19/'           : object,
                            'Sub Tipo de Crédito 20/'       : object,
                            'Fecha de Desembolso 21/'       : object,
                            'Cuenta Contable 25/'           : object,
                            'Cuenta Contable Crédito Castigado 39/'         : object,
                            'Tipo de Producto 43/'          : object,
                            'Fecha de Vencimiento Origuinal del Credito 48/': object,
                            'Fecha de Vencimiento Actual del Crédito 49/'   : object,
                            'Nro Prestamo \nFincore'        : object,
                            'Refinanciado TXT'              : object
                            },
                   skiprows = 2)

#eliminando las filas con NaN en las siguiente columnas al mismo tiempo:
df1.dropna(subset = ['Apellidos y Nombres / Razón Social 2/', 
                     'Fecha de Nacimiento 3/',
                     'Número de Documento 10/',
                     'Domicilio 12/',
                     'Numero de Crédito 18/'], 
           inplace = True, 
           how     = 'all')

#leyendo la lista de socios con cred < 100 soles
df_100=pd.read_excel(anexo_del_mes,
                 dtype      = {'Código Socio 7/' : object},
                 skiprows   = 0,
                 sheet_name = 'socios con cred < 100 soles')
                    
anexo06 = df1.columns  ; socios_menor_100 = df_100.columns
del anexo_del_mes

# %% hay dos nuevos productos, el 26 y el 27
# el 26 es emprendimiento mujer (microempresa)
# el 27 es multioficios(hay que pasarlo a 32)
df1['Tipo de Producto 43/'] = df1['Tipo de Producto 43/'].astype(str)
df1['Tipo de Producto 43/'] = df1['Tipo de Producto 43/'].str.strip()
df1.loc[df1['Tipo de Producto 43/'] == '27', 'Tipo de Producto 43/'] = '32'
df1.loc[df1['Tipo de Producto 43/'] == '26', 'Tipo Credito TXT']     = 'EMPRENDE MUJER'

df1.loc[df1['Tipo de Producto 43/'] == '32', 'Tipo Credito TXT']     = 'LD-MULTIOFICIOS'
df1.loc[df1['Tipo de Producto 43/'] == '32', 'Tipo de Crédito 19/']  = '12'

print(df1[df1['Tipo de Producto 43/'] == '27'].shape[0])
print('debe salir cero')

#%% CRÉDITOS EN LA COOPAC
#POR SI ACASO VEMOS CUANTOS CRÉDITOS DE LA COOPAC HAY
df1['Nombre PlanillaTXT'] = df1['Nombre PlanillaTXT'].fillna('')
creditos_coopac = df1[df1['Nombre PlanillaTXT'].str.contains('dito san miguel', case = False) | 
                     (df1['Nombre PlanillaTXT'].str.contains('san miguel', case = False) & 
                     (df1['Nombre PlanillaTXT'].str.contains('coopac', case = False)))]

print(creditos_coopac[['Numero de Crédito 18/', 'Nombre PlanillaTXT']]) #vamos a ver las planillas
print(creditos_coopac[['Numero de Crédito 18/', 'Nombre PlanillaTXT']].shape[0]) #vamos a ver las planillas

#%% corrección originador andrea bilbao
cred_andrea_bilbao = pd.read_excel(io = 'ORIGINADOR ANDREA BILBAO.xlsx', 
                                   dtype = {'nro_fincore' : str})
columna_funcionario = 'Funcionario Origuinador'
def originador_reasignacion(df):
    if df['Nro Prestamo \nFincore'] in list(cred_andrea_bilbao['nro_fincore']):
        return 'ANDREA BILBAO BRICEÑO'
    else:
        return df[columna_funcionario]

df1[columna_funcionario] = df1.apply(originador_reasignacion, axis = 1)

#%% CORRECCIÓN DEL TIPO DE DOCUMENTO

#pequeña corrección al anexo06

# Reemplazar el valor de 'Tipo de Documento 9/' donde 'Nro Prestamo Fincore' sea '00092306'
# es una corrección recurrente
df1.loc[df1['Nro Prestamo \nFincore'] == '00109244', 'Tipo de Documento 9/'] = '1'
df1.loc[df1['Código Socio 7/']        == '00035504', 'Tipo de Documento 9/'] = '1'
df1.loc[df1['Nro Prestamo \nFincore'] == '00092306', 'Tipo de Documento 9/'] = '1'

tipo_cero = df1[(df1['Tipo de Documento 9/'] ==  0) | \
                (df1['Tipo de Documento 9/'] == '0')]

#si sale vacío, está todo bien
if tipo_cero.shape[0] == 0:
    print(0)
    print('todo bien')
else:
    print('investigar, hay algún tipo de documento con cero, y no debe tenerlo')
    print(tipo_cero['Nro Prestamo \nFincore'])
#456 Ejemplo de código para realizar un update en función de múltiples condiciones
#456df1.loc[(df1['Nro Prestamo Fincore'] == '00092306') & \
#456        (df1['sexo'] == 'M') & \
#456        (df1['Refinanciado'] == 'TIPO 1') & \
#456        (df1['producto'].isin([5, 7, 25, 0])), 'Tipo de Documento 9/'] = 1
del tipo_cero

#%% CORRECCIÓN CUENTA CONTABLE CASTIGADOS
# código añadido al reporte preliminar

# def añadiendo_cuenta_contable(df1):
#     if df1['Saldos de Créditos Castigados 38/'] > 0:
#         return '811302'
#     else:
#         return df1['Cuenta Contable Crédito Castigado 39/']
    
# df1['Cuenta Contable Crédito Castigado 39/'] = df1.apply(añadiendo_cuenta_contable, axis=1)    

# #arreglando la Cuenta Contable Crédito Castigado 39/ (811302 ->  8113020000)
# df1['Cuenta Contable Crédito Castigado 39/'] = df1['Cuenta Contable Crédito Castigado 39/'].str.strip()

# def cuenta_contable_castigados(df1):
#     if '811302' in df1['Cuenta Contable Crédito Castigado 39/']:
#         return '8113020000'
#     else:
#         ''
# df1['Cuenta Contable Crédito Castigado 39/'] = df1.apply(cuenta_contable_castigados, axis=1)

# print(df1['Cuenta Contable Crédito Castigado 39/'].unique())
# print('si sale 8113020000 entonces todo bien')

#%% CLASIFICACIÓN DE LOS REFINANCIADOS

###############################################################################
####        LEER EL ARCHIVO DE LA CLASIFICACIÓN DE LOS REFINANCIADOS    #######
###############################################################################

#ahora vamos a leer el archivo donde Enrique manualmente elabora la clasificación de los refinanciados
#para leer bien este reporte primero debemos eliminar los otros meses del excel (ya que se repiten)
nombre_col_fincore = 'Pagaré Actual'

calif_ref = pd.read_excel(archivo_refinanciados,
                          skiprows = 3,
                          dtype = {'Nº de Crédito FINCORE' : object,
                                   nombre_col_fincore         : str})

calif_ref[nombre_col_fincore] = calif_ref[nombre_col_fincore].str.strip() #si aquí salta un error, es porque le han cambiado el nombre a la columna

calif_ref[mes_calif] = calif_ref[mes_calif].astype(float)

calif_ref = calif_ref.rename(columns = {mes_calif        : 'calificacion especial'})
calif_ref = calif_ref.rename(columns = {nombre_col_fincore  : 'fincore ref'}) #aquí antes la columna se llamaba Nº de Crédito FINCORE

calif_ref = calif_ref[['fincore ref','calificacion especial']]

calif_ref.dropna(subset = ['fincore ref', 
                           'calificacion especial'], 
                 inplace = True, 
                 how     = 'all')

# alerta de duplicados en el archivo de refinanciados
duplicados = calif_ref[calif_ref.duplicated(subset = 'fincore ref', 
                                            keep   = False)]
if duplicados.shape[0] == 0:
    print(Back.GREEN + 'SIN DUPLICADOS')
else:
    print(Back.RED + '🚨 NRO FINCORE DUPLICADOS 🚨')
    print(duplicados['fincore ref'])

del archivo_refinanciados
del mes_calif

#de aqui esta tabla se usará después de aplicar la calificación con alineamiento de manera individual (linea )
                                        
#%% parseo de fechas
'parseando datos de fechas'
'hay que tener cuidado con esta vaina, si las fechas no están en el formato indicado se pierden'

df1['Fecha de Nacimiento 3/'] = pd.to_datetime(df1['Fecha de Nacimiento 3/'], 
                                               format='%Y%m%d') #no tiene ,errors='coerce'), si algo no hace match te avisará
print(df1[df1['Fecha de Nacimiento 3/'].isnull()].shape[0])
df1['Fecha de Desembolso 21/'] = pd.to_datetime(df1['Fecha de Desembolso 21/'], 
                                                format='%Y%m%d') #no tiene ,errors='coerce'), si algo no hace match te avisará 
print(df1[df1['Fecha de Desembolso 21/'].isnull()].shape[0])
df1['Fecha de Vencimiento Origuinal del Credito 48/'] = pd.to_datetime(df1['Fecha de Vencimiento Origuinal del Credito 48/'], 
                                                                       format='%Y%m%d') #no tiene ,errors='coerce'), si algo no hace match te avisará
print(df1[df1['Fecha de Vencimiento Origuinal del Credito 48/'].isnull()].shape[0])
df1['Fecha de Vencimiento Actual del Crédito 49/'] = pd.to_datetime(df1['Fecha de Vencimiento Actual del Crédito 49/'], 
                                                                    format='%Y%m%d') #no tiene ,errors='coerce'), si algo no hace match te avisará  
print(df1[df1['Fecha de Vencimiento Actual del Crédito 49/'].isnull()].shape[0])
                    
#%% limpieza de datos
#quitando posibles espacios vacíos en el código del socio
df1['Código Socio 7/'] = df1['Código Socio 7/'].str.strip()

df1['Nro Prestamo \nFincore'] = df1['Nro Prestamo \nFincore'].str.strip()

df1['Número de Documento 10/'] = df1['Número de Documento 10/'].str.strip()
df1['Tipo de Documento 9/'] = df1['Tipo de Documento 9/'].astype(int).astype(str).str.strip()

#%% COMPROBACIÓN DE SOCIOS CON MENOS DE UN CRÉDITO
# resultado_1
# haciendo un merge en realidad innecesario pero es para comprobar la primera columna 
# 'Socios al menos con un cred < 100 soles
# amarillo =  cred <100
# rosado =  cred >= 100
# PROV.REQUERIDA A SER EVALUADA.'

df100_merge = df_100.copy() #que raro, el nro fincore es número int (ಥ_ಥ)
df100_merge = df100_merge.rename(columns={"Código Socio 7/": "codigo de socio"})
df100_merge.drop_duplicates(subset='codigo de socio', inplace=True)
df100_merge = df100_merge["codigo de socio"]

df_resultado = df1.merge(df100_merge, 
                         left_on  = ["Código Socio 7/"], 
                         right_on = ["codigo de socio"],
                         how      = 'left')

print(df_resultado.shape[0])
df_resultado.drop_duplicates(subset='Nro Prestamo \nFincore', inplace=True)
print(df_resultado.shape[0])
print('si sale menos, es porque hubo duplicados')
df_resultado = df_resultado.rename(columns={"codigo de socio": "al menos 1 crédito < 100"})

dataframe = df_resultado.copy()

# del df_resultado
# df_resultado = dataframe

#%%% limpieza refinanciados

#ojo que aquí estamos reemplazando el calif_ref de la lectura del archivo que manda enrique

#lo ponemos todo en mayúsculas
df_resultado['Refinanciado TXT'] = df_resultado['Refinanciado TXT'].str.upper()
df_resultado['Refinanciado TXT'] = df_resultado['Refinanciado TXT'].str.strip()
df_resultado['Refinanciado TXT'] = df_resultado['Refinanciado TXT'].astype(str)
print(df_resultado['Refinanciado TXT'].unique())

#%% CLASIFICACIÓN POR CRÉDITO SIN ALINEAMIENTO (14/)
df_resultado['Refinanciado TXT']        =   df_resultado['Refinanciado TXT'].str.strip()
df_resultado['Nro Prestamo \nFincore']  =   df_resultado['Nro Prestamo \nFincore'].str.strip()

'hora de calcular la clasificación con alineamiento interno:'

#por si acaso convertirmo el tipo de dato a numero
df_resultado['Dias de Mora 33/'] = df_resultado['Dias de Mora 33/'].astype(int)
def alineamiento(df_resultado):
    if ('REFINANCIADO' not in df_resultado['Refinanciado TXT'] or 'Refinanciado' not in df_resultado['Refinanciado TXT']):
        if df_resultado['Tipo de Crédito 19/'] in ['06', '07', '08']:
            if df_resultado['Dias de Mora 33/'] <= 15:
                return '0'
            elif df_resultado['Dias de Mora 33/'] <= 60:
                return '1'
            elif df_resultado['Dias de Mora 33/'] <= 120:
                return '2'
            elif df_resultado['Dias de Mora 33/'] <= 365:
                return '3'
            elif df_resultado['Dias de Mora 33/'] > 365:
                return '4'
        elif df_resultado['Tipo de Crédito 19/'] in ['09', '10', '11','12']:
            if df_resultado['Dias de Mora 33/'] <= 8:
                return '0'
            elif df_resultado['Dias de Mora 33/'] <= 30:
                return '1'
            elif df_resultado['Dias de Mora 33/'] <= 60:
                return '2'
            elif df_resultado['Dias de Mora 33/'] <= 120:
                return '3'
            elif df_resultado['Dias de Mora 33/'] > 120:
                return '4'
        elif df_resultado['Tipo de Crédito 19/'] in ['13']:
            if df_resultado['Dias de Mora 33/'] <= 30:
                return '0'
            elif df_resultado['Dias de Mora 33/'] <= 60:
                return '1'
            elif df_resultado['Dias de Mora 33/'] <= 120:
                return '2'
            elif df_resultado['Dias de Mora 33/'] <= 365:
                return '3'
            elif df_resultado['Dias de Mora 33/'] > 365:
                return '4'
    elif ('REFINANCIADO' in df_resultado['Refinanciado TXT'] or 'Refinanciado' in df_resultado['Refinanciado TXT']):
        return df_resultado['Clasificación del Deudor 14/'].astype(int).astype(str)
    else:
        return 'revisar caso'

#aplicamos la función
df_resultado['alineamiento14 provisional'] = df_resultado.apply(alineamiento, axis=1)

#convertimos esa columna a numerica
df_resultado['alineamiento14 provisional'] = df_resultado['alineamiento14 provisional'].astype(float)

#este resultado se debería asignar a la columna 14/
df_resultado['Clasificación del Deudor 14/'] = df_resultado['alineamiento14 provisional']

#%%% CLASIFICACIÓN SIN ALINEAMIENTO, TOMANDO EN CUENTA LOS REFINANCIADOS (14/)
#HASTA AQUÍ HEMOS CREADO EL ALINEAMIENTO POR LA LÓGICA ESTABLECIDA
#FALTA PONERLE LA CLASIFICACIÓN MANUAL QUE ELABORA ENRIQUE A LOS CRÉDITOS REFINANCIADOS

calif_ref['fincore'] = calif_ref['fincore ref'].str.strip()

#hacemos un merge
df_resultado = df_resultado.merge(calif_ref, 
                          how      = 'left', 
                          left_on  = ['Nro Prestamo \nFincore'], 
                          right_on = ['fincore ref'])

fincores = df_resultado[['fincore ref', 'calificacion especial']].copy()                                   
fincores = fincores.dropna()
fincores = fincores['fincore ref'].tolist()
                                   
def asignacion_calif_refinanciados(df_resultado):
    if df_resultado['Nro Prestamo \nFincore'] in fincores:
        return df_resultado['calificacion especial']
    else:
        return df_resultado['alineamiento14 provisional']

df_resultado['alineamiento 14 final'] = df_resultado.apply(asignacion_calif_refinanciados, axis=1)

df_resultado['alineamiento14 provisional'] = df_resultado['alineamiento 14 final']
df_resultado['Clasificación del Deudor 14/'] = df_resultado['alineamiento 14 final']   

#%% CLASIFICACIÓN CON ALINEAMIENTO 15/
'ALINEAMIENTO 15/'
#primero que nada, debemos sumar todo el saldo de cartera para que sirva para hacer un merge
saldo_total = df_resultado.groupby('Código Socio 7/')['Saldo de colocaciones (créditos directos) 24/'].sum().reset_index()
saldo_total = saldo_total.rename(columns={"Código Socio 7/": "codigo para merge"})
saldo_total = saldo_total.rename(columns={"Saldo de colocaciones (créditos directos) 24/": "saldo para dividir"})

#merge
df_resultado = df_resultado.merge(saldo_total, 
                                  how      = 'left', 
                                  left_on  = ['Código Socio 7/'], 
                                  right_on = ["codigo para merge"])

df_resultado.drop(["codigo para merge"], axis=1, inplace=True)

#verificamos si hay nulos
#todo bien si sale un dataframe vacío
df_nulos_alineamiento = df_resultado[df_resultado["saldo para dividir"].isnull()] 

#división
df_resultado['porcentaje del total'] =  df_resultado['Saldo de colocaciones (créditos directos) 24/']/ \
                                        df_resultado["saldo para dividir"]

#%% PARTE 2 ALINEAMIENTO 15/
#creamos función que crea columna auxiliar para escoger los que sirven para el alineamiento
def monto_menor(df_resultado):
    if ((df_resultado['Saldo de colocaciones (créditos directos) 24/'] < 100) and \
        (df_resultado['porcentaje del total'] < 0.01)) or \
        ((df_resultado['porcentaje del total'] < 0.01) and \
        (df_resultado['Saldo de colocaciones (créditos directos) 24/'] < 3*uit)):
        return 'menor'
    else:
        return 'mayor'
    
df_resultado['credito menor'] = df_resultado.apply(monto_menor, axis=1)

#SENTINEL EXPERIAN inicio 1
#parte del código que servirá para el reporte de SENTINEL - EXPERIAN
nro_creditos_por_socio = df_resultado.groupby('Código Socio 7/').agg({'Nro Prestamo \nFincore': 'nunique'}).reset_index()
nro_creditos_por_socio = nro_creditos_por_socio.rename(columns={"Código Socio 7/" : 'cod socio unico'})
nro_creditos_por_socio = nro_creditos_por_socio.rename(columns={'Nro Prestamo \nFincore' : 'nro de préstamos'})

#MERGE PARA INDICAR AL ANEXO06, EL NRO DE CRÉDITOS QUE TIENE AL MISMO TIEMPO
df_resultado = df_resultado.merge(nro_creditos_por_socio, 
                                  how      = 'left', 
                                  left_on  = ['Código Socio 7/'], 
                                  right_on = ['cod socio unico'])
df_resultado.drop(['cod socio unico'], axis=1, inplace=True)
#SENTINEL EXPERIAN final 1

#procedemos a filtrar los que son mayores
df_filtro_alineamiento = df_resultado[df_resultado['credito menor'] == 'mayor']
df_filtro_alineamiento = df_filtro_alineamiento[['Clasificación del Deudor 14/', "Código Socio 7/"]]

#agrupamos por código y máximo alineamiento
calificacion = df_filtro_alineamiento.groupby("Código Socio 7/")['Clasificación del Deudor 14/'].max().reset_index()
calificacion = calificacion.rename(columns={"Código Socio 7/": 'cod socio para merge'})
calificacion = calificacion.rename(columns={'Clasificación del Deudor 14/': 'calificacion para merge'})

#hora del merge
df_resultado = df_resultado.merge(calificacion, 
                                  how     = 'left', 
                                  left_on = ['Código Socio 7/'], 
                                  right_on= ['cod socio para merge'])
#hasta aquí ya hemos asignado el tipo de producto, de manera general, debería estar todo unificado. falta poner las excepciones,

#para sentinel-experian iniico 2
#vamos a filtrar la calificación para el reporte de experian
filtro_experian = df_resultado[(df_resultado['credito menor'] == 'mayor') |
                               (df_resultado['nro de préstamos'] == 1)]


filtro_experian = filtro_experian[['Código Socio 7/', 'credito menor', 'Clasificación del Deudor 14/',
                 'calificacion para merge', 'nro de préstamos']]
def arreglo_cal_experian(filtro_experian):
    if pd.isnull(filtro_experian['calificacion para merge']): #atento a esta parte del código
        return filtro_experian['Clasificación del Deudor 14/']
    else:
        return filtro_experian['calificacion para merge']
filtro_experian['calificacion para merge'] = filtro_experian.apply(arreglo_cal_experian, axis=1)
filtro_experian.drop(['Clasificación del Deudor 14/'], axis=1, inplace=True)
filtro_experian = filtro_experian.rename(columns={"Código Socio 7/": 'cod socio para merge de sentinel'})

# hice algo para el reporte de experian pero ya no sirve, solo sirve el de abajo

#%% ASIGNACIÓN DE CLASIFICACIÓN CON ALINEAMIENTO PARA EXCEPCIONES
#SE ASIGNA LA CALIFICACIÓN, EXCEPTO PARA LOS PUCHITOS Y LOS REFINANCIADOS, LOS REFINANCIADOS, CREO QUE YA ESTÁN BIEN ASIGNADOS xd
def asignacion_15(df_resultado):
    if df_resultado['credito menor'] == 'mayor':
        return df_resultado['calificacion para merge']
    elif df_resultado['credito menor'] == 'menor':
        return df_resultado['Clasificación del Deudor 14/']
    else:
        return 'investigar caso'

df_resultado['alineamiento 15 por joseph'] = df_resultado.apply(asignacion_15, axis=1)

#vamos a colocar nuevamente el alineamiento para los refinanciados, no estoy seguro si hace falta esta función  :v
def asignacion_refinanciados(df_resultado):
    if df_resultado['Refinanciado TXT'] == 'REFINANCIADO':
        return df_resultado['Clasificación del Deudor 14/']
    else:
        return df_resultado['alineamiento 15 por joseph']
    
df_resultado['alineamiento 15 por joseph'] = df_resultado.apply(asignacion_refinanciados, axis=1)

df_resultado['alineamiento 15 anterior'] = df_resultado['Clasificación del Deudor con Alineamiento 15/']
df_resultado['Clasificación del Deudor con Alineamiento 15/'] = df_resultado['alineamiento 15 por joseph']

# HASTA AQUÍ YA LA CALIFICACIÓN ESTÁ CORRECTAMENTE ASIGNADA

#%% ALINEAMIENTO PARA SENTINEL - EXPERIAN

filtrados_sentinel = df_resultado[((df_resultado['credito menor'] == 'mayor') | \
                                  (df_resultado['nro de préstamos'] == 1)) 
                                  |
                                  (~((df_resultado['credito menor'] == 'mayor') | \
                                  (df_resultado['nro de préstamos'] == 1))) & \
                                  (df_resultado['Saldos de Créditos Castigados 38/'] > 0)]
    
filtrados_sentinel = filtrados_sentinel[['Apellidos y Nombres / Razón Social 2/',
                                         'Código Socio 7/', 
                                         'credito menor',
                                         'nro de préstamos',
                                         'Clasificación del Deudor con Alineamiento 15/']]
filtrados_sentinel = filtrados_sentinel.rename(columns={"Código Socio 7/": 'cod socio para merge'})
filtrados_sentinel = filtrados_sentinel.rename(columns={'Clasificación del Deudor con Alineamiento 15/': 'calificacion para merge'})
filtrados_sentinel['cod socio para merge'] = filtrados_sentinel['cod socio para merge'].str.strip()

#filtrados_sentinel[filtrados_sentinel['cod socio para merge'] == '00001056'] #para verificar la existencia de algún crédito

#AGRUPACIÓN PARA EL MATCH
calificacion_para_sentinel = filtrados_sentinel.groupby('cod socio para merge')['calificacion para merge'].max().reset_index()

#DATOS DE LA CALIFICACIÓN DE LOS CRÉDITOS PARA SENTINEL
#AHORA SÍ
try:
    ruta = 'calificacion para reporte experian.xlsx'
    os.remove(ruta)
except FileNotFoundError:
    pass

calificacion_para_sentinel.to_excel(ruta,
                                    index = False)
#este excel será usado por experian  

#%% VERIFIACIÓN QUE NO VERIFICA XD
# CÓDIGO VERIFICADOR DEL ALINEAMIENTO 15 DEL ANEXO-06

# Calcular el conteo de diferentes productos por NumerodeDocumento10
grouped = df_resultado.groupby('Código Socio 7/').agg({'Clasificación del Deudor con Alineamiento 15/': 'nunique'}) #contar el número de valores únicos
grouped.columns = ['DIFERENTES PRODUCTOS']

# Filtrar los grupos con más de un producto diferente
result = grouped[grouped['DIFERENTES PRODUCTOS'] > 1]
#EL RESULTADO NO TIENE PORQUÉ SER UN DATAFRAME VACÍO, por lo tanto esta verificación no sirve xd
print('simplemente muestra los socios que tienen diferentes clasificaciones si tienen más de un crédito')
print(result)

#%% PROVISIONES
'función para elaborar las provisiones'
    
def provision_SA(df_resultado):
    if df_resultado['Clasificación del Deudor 14/'] == 0:
        if df_resultado['Tipo de Crédito 19/'] in ['12','11','10', '09','08', 12,11,10,9,8]:                                                   
            return 0.01
        elif df_resultado['Tipo de Crédito 19/'] in ['13', '07', '06',13,7,6]:
            return 0.007
    elif df_resultado['Saldo de Garantías Autoliquidables 35/'] > 0:
        if df_resultado['Clasificación del Deudor 14/'] in [1,2,3,4,'1','2','3','4']:
            return 0.01
    elif df_resultado['Saldos de Garantías Preferidas 34/'] > 0:
        if df_resultado['Clasificación del Deudor 14/'] == 1:
            return 0.025
        if df_resultado['Clasificación del Deudor 14/'] == 2:
            return 0.125
        if df_resultado['Clasificación del Deudor 14/'] == 3:
            return 0.30
        if df_resultado['Clasificación del Deudor 14/'] == 4:
            return 0.60
    elif (df_resultado['Saldos de Garantías Preferidas 34/'] == 0) and \
        (df_resultado['Saldo de Garantías Autoliquidables 35/'] == 0):
        if df_resultado['Clasificación del Deudor 14/'] == 1:
            return 0.05
        if df_resultado['Clasificación del Deudor 14/'] == 2:
            return 0.25
        if df_resultado['Clasificación del Deudor 14/'] == 3:
            return 0.6
        if df_resultado['Clasificación del Deudor 14/'] == 4:
            return 1.00
    else:
        return ''

df_resultado['Tasa de Provisión SA'] = df_resultado.apply(provision_SA, axis=1)

#%%% PROVISIONES P2
def provision(df_resultado):
    if df_resultado['Clasificación del Deudor con Alineamiento 15/'] == 0:
        if df_resultado['Tipo de Crédito 19/'] in ['12','11','10', '09','08',12,11,10,9,8]:                                                   
            return 0.01
        elif df_resultado['Tipo de Crédito 19/'] in ['13', '07', '06',13,7,6]:
            return 0.007
    elif df_resultado['Saldo de Garantías Autoliquidables 35/'] > 0:
        if df_resultado['Clasificación del Deudor con Alineamiento 15/'] in [1,2,3,4,'1','2','3','4']:
            return 0.01
    elif df_resultado['Saldos de Garantías Preferidas 34/'] > 0:
        if df_resultado['Clasificación del Deudor con Alineamiento 15/'] == 1:
            return 0.025
        if df_resultado['Clasificación del Deudor con Alineamiento 15/'] == 2:
            return 0.125
        if df_resultado['Clasificación del Deudor con Alineamiento 15/'] == 3:
            return 0.30
        if df_resultado['Clasificación del Deudor con Alineamiento 15/'] == 4:
            return 0.60
    elif (df_resultado['Saldos de Garantías Preferidas 34/'] == 0) and \
        (df_resultado['Saldo de Garantías Autoliquidables 35/'] == 0):
        if df_resultado['Clasificación del Deudor con Alineamiento 15/'] == 1:
            return 0.05
        if df_resultado['Clasificación del Deudor con Alineamiento 15/'] == 2:
            return 0.25
        if df_resultado['Clasificación del Deudor con Alineamiento 15/'] == 3:
            return 0.6
        if df_resultado['Clasificación del Deudor con Alineamiento 15/'] == 4:
            return 1.00
    else:
        return ''
###
df_resultado['Tasa de Provisión'] = df_resultado.apply(provision, axis=1)
###

#%% TASA DE INTERÉS CONVERTIDA A DIARIA
'tasa de interés anual'
df_resultado['Tasa de Interés Anual 23/'].dtype

def int_diario(df_resultado):
    return (((1 + float(df_resultado['Tasa de Interés Anual 23/']))**(1/360))-1) * 100

df_resultado['Tasa Diaria'] = df_resultado.apply(int_diario, axis=1)

#%% ASIGNACIÓN DE GARANTÍAS
'garantías preferidas'
#para asignar las garantías preferidas, tenemos una lista de créditos con garantías preferidas,
#solo si estos créditos del anexo 06 están en esta lista se le va a asignar el saldo de crédito24

df_resultado['Monto de Garantías Preferidas'] = df_resultado['Saldos de Garantías Preferidas 34/']

def garant_pref(df_resultado):
    if df_resultado['Nro Prestamo \nFincore'] in ['00025314'	,
                                                  '00021989'	,
                                                  '00024551'	,
                                                  '00023254'	,
                                                  '00025067'	,
                                                  '00024033'	,
                                                  '00025678'	,
                                                  '00023259'	,
                                                  '00022958'	,
                                                  '00024926'	,
                                                  '00023451'	,
                                                  '00023202'	,
                                                  '00023215'	,
                                                  '00024860'	,
                                                  '00025566'	,
                                                  '00021994'	
                                                  ]:  
        return df_resultado['Saldo de colocaciones (créditos directos) 24/']
    else:
        return 0
    
df_resultado['Saldos de Garantías Preferidas 34/'] = df_resultado.apply(garant_pref, axis=1)   

#%% GARANTÍAS AUTOLIQUIDABLES
'garantías autoliquidables'
#para las garantías autoliquidables 

df_resultado['Monto de Garantías Autoliquidables'] = df_resultado['Saldo de Garantías Autoliquidables 35/']

def garant_autoliqui(df_resultado):
    if df_resultado['Saldo de Garantías Autoliquidables 35/'] > 0:  
        return df_resultado['Saldo de colocaciones (créditos directos) 24/']
    else:
        return 0
    
df_resultado['Saldo de Garantías Autoliquidables 35/'] = df_resultado.apply(garant_autoliqui, axis=1)

#%% VERIFICACIÓN DE GARANTÍAS
# VERIFICACIÓN DE GARANTÍAS (NO DEBE HABER GARANTÍAS AUTOLIQUIDABLES Y PREFERIDAS)

verificacion_garantías = df_resultado[(df_resultado['Saldo de Garantías Autoliquidables 35/'] > 0) &
                                      (df_resultado['Saldos de Garantías Preferidas 34/'] > 0)]

print('hay ' + str(verificacion_garantías.shape[0]) + ' filas con garantías autoliquidables y preferidas al mismo tiempo')
if verificacion_garantías.shape[0] == 0:
    print(Back.GREEN + 'todo bien')
else:
    print(Back.RED +'investigar')

del verificacion_garantías

#%% CARTERA ATRASADA
'CARTERA ATRASADA'

def cartera_atrasada(df_resultado):
    return df_resultado['Capital Vencido 29/'] + df_resultado['Capital en Cobranza Judicial 30/']

df_resultado['Cartera Atrasada'] = df_resultado.apply(cartera_atrasada, axis=1)   

#%% RANGO DÍAS MORA
'rango días mora'

def rango_dias_mora(df_resultado):
    if df_resultado['Dias de Mora 33/'] <= 8:
        return 'De 0 a 8'
    elif df_resultado['Dias de Mora 33/'] <= 30:
        return 'De 9 a 30'
    elif df_resultado['Dias de Mora 33/'] <= 60:
        return 'De 31 a 60'
    elif df_resultado['Dias de Mora 33/'] <= 90:
        return 'De 61 a 90'
    elif df_resultado['Dias de Mora 33/'] <= 120:
        return 'De 91 a 120'
    elif df_resultado['Dias de Mora 33/'] <= 180:
        return 'De 121 a 180'
    elif df_resultado['Dias de Mora 33/'] <= 365:
        return 'De 181 a 365'
    elif df_resultado['Dias de Mora 33/'] <= 730:
        return 'De 366 a 730'
    elif df_resultado['Dias de Mora 33/'] > 730:
        return 'De 731 a mas'
    else:
        return 'revisar caso'
    

df_resultado['Rango Días de Mora'] = df_resultado.apply(rango_dias_mora, axis=1) 

#%% SITUACIÓN DEL SOCIO
'columna auxiliar que indica si es vigente, refinanciado, vencido o judicial'
'servirá para asignar la cuenta contbale 25'

def situacion(df_resultado):
    if (df_resultado['Capital Vigente 26/'] > df_resultado['Capital Refinanciado 28/'] and
        df_resultado['Capital Vigente 26/'] > df_resultado['Capital Vencido 29/']  and
        df_resultado['Capital Vigente 26/'] > df_resultado['Capital en Cobranza Judicial 30/']):
       return 'VIGENTE'
    elif (df_resultado['Capital Refinanciado 28/'] > df_resultado['Capital Vigente 26/'] and
          df_resultado['Capital Refinanciado 28/'] > df_resultado['Capital Vencido 29/']  and
          df_resultado['Capital Refinanciado 28/'] > df_resultado['Capital en Cobranza Judicial 30/']):
       return 'REFINANCIADO'
    elif (df_resultado['Capital Vencido 29/'] > df_resultado['Capital Vigente 26/'] and
          df_resultado['Capital Vencido 29/'] > df_resultado['Capital Refinanciado 28/']  and
          df_resultado['Capital Vencido 29/'] > df_resultado['Capital en Cobranza Judicial 30/']):
       return 'VENCIDO'
    elif (df_resultado['Capital en Cobranza Judicial 30/'] > df_resultado['Capital Vigente 26/'] and
          df_resultado['Capital en Cobranza Judicial 30/'] > df_resultado['Capital Refinanciado 28/']  and
          df_resultado['Capital en Cobranza Judicial 30/'] > df_resultado['Capital Vencido 29/']):
       return 'JUDICIAL'
    else:
        return ' '
    
df_resultado['AUXILIAR_SITUACION'] = df_resultado.apply(situacion, axis=1) 

#%% ASIGNACIÓN DE CUENTAS CONTABLES
'CREACIÓN DE LAS TABLAS DE LAS CUENTAS CONTABLES'

cuentas_01 = pd.DataFrame({'TIPO CREDITO':['08','09','10','12','13'],
                           'VIGENTE':['1411120600','1411130600',
                                      '1411020600','1411030604',
                                      '1411040601'],
                           'REFINANCIADO':['1414120600','1414130600',
                                           '1414020600','1414030604',
                                           '1414040601'],
                           'VENCIDO':['1415120600','1415130600',
                                      '1415020600','1415030604',
                                      '1415040601'],
                           'JUDICIAL':['1416120600','1416130600',
                                       '1416020600','1416030604',
                                       '1416040601'],
                           ' ':['','',
                                       '','',
                                       '']})

cuentas_02 = pd.DataFrame({'TIPO CREDITO':['08','09','10','12','13'],
                           'VIGENTE':['1421120600','1421130600',
                                      '1421020600','1421030604',
                                      '1421040601'],
                           'REFINANCIADO':['1424120600','1424130600',
                                           '1424020600','1424030604',
                                           '1424040601'],
                           'VENCIDO':['1425120600','1425130600',
                                      '1425020600','1425030604',
                                      '1425040601'],
                           'JUDICIAL':['1426120600','1426130600',
                                       '1426020600','1426030604',
                                       '1426040601'],
                           ' ':['','',
                                       '','',
                                       '']})

#%% ASIGNACIÓN DE CUENTAS CONTABLES P2
'asignación de la cuenta contable 25'

def asignacion_25(df_resultado):
    
    valor1 = ''
    valor2 = ''
    
    tipo_credito = df_resultado['Tipo de Crédito 19/']
    situacion = df_resultado['AUXILIAR_SITUACION']
    
    if df_resultado['Moneda del crédito 17/'] == '01':
        if tipo_credito in cuentas_01['TIPO CREDITO'].values:
            valor1 = cuentas_01.loc[cuentas_01['TIPO CREDITO'] == tipo_credito, situacion].values[0]
        return valor1

    elif df_resultado['Moneda del crédito 17/'] == '02':
        if tipo_credito in cuentas_02['TIPO CREDITO'].values:
            valor2 = cuentas_02.loc[cuentas_01['TIPO CREDITO'] == tipo_credito, situacion].values[0]
        return valor2
    else:
        return ''
    

df_resultado['Cuenta Contable 25/'] = df_resultado.apply(asignacion_25, axis=1) 

# cuentas_02.loc[cuentas_02['TIPO CREDITO'] == '08', 'REFINANCIADO'].values[0]

#%% RECALCULANDO EL TIPO DE PRODUCTO PARA MYPE
'vamos a calcular el tipo de producto, principalmente para mype'
#primero que nada creamos la columna que nos servirá de comparación cuando terminemos
df_resultado['Tipo de Producto 43/ original'] = df_resultado['Tipo de Producto 43/']

# PROBAR SI FUNCIONA
# si el crédito tiene partida registral y es anterior al 2019
# o si el crédito tiene partida registral y tiene Origen Prestamos = 'POND'
# debe ser 41
df_resultado['Partida Registral 8/'] = df_resultado['Partida Registral 8/'].str.strip()
#primero verificar si existen créditos que deben ser hipotecarios

def producto_43(row): #aparentemente está funcionando
    if ((len(str(row['Partida Registral 8/'])) > 2) and \
    (row['Fecha de Desembolso 21/'] <= pd.to_datetime('2019-12-31'))) or \
     ((len(str(row['Partida Registral 8/'])) > 2) and \
     (row['Origen\n Prestamo'] == 'POND')):
        return 41
    else:
        return row['Tipo de Producto 43/ original']

df_resultado['Tipo de Producto 43/'] = df_resultado.apply(producto_43, axis=1)

#% verificación, lo desactivo porque si funciona

#x = df_resultado[(df_resultado['Tipo de Producto 43/'] != 41) & \
#             (len(str(df_resultado['Partida Registral 8/'])) > 2) & \
#             df_resultado['''Origen
# Prestamo'''] == 'POND']
#print(x) #no recuerdo pero imagino que debe salir vacío xd
#'''

#%% PRODUCTO 43 (41)

df_resultado['Partida Registral 8/'] = df_resultado['Partida Registral 8/'].fillna('')

def producto_43(row): #aparentemente este sí funciona, seguir investigando
    if (row['Partida Registral 8/'] != '') & \
    (row['Fecha de Desembolso 21/'] <= pd.to_datetime('2019-12-31')) | \
     ((row['Partida Registral 8/'] != '') & \
     (row['Origen\n Prestamo'] == 'POND')):
        return '41'
    else:
        return row['Tipo de Producto 43/ original']

df_resultado['Tipo de Producto 43/'] = df_resultado.apply(producto_43, axis=1)

#%% 37 PARA TRABAJADORES DE LA COOPERATIVA
#AHORA VAMOS A ASIGNAR 37 A LOS CRÉDITOS QUE TENGAN PLANILLA = COOPAC SAN MIGUEL
def producto_37(df_resultado):
    if df_resultado['Nombre PlanillaTXT'] == 'COOPERATIVA DE AHORRO Y CREDITO SAN MIGUEL LTDA.':
        return 37
    else:
        return df_resultado['Tipo de Producto 43/']
    # PROBAR SI FUNCIONAAAA
df_resultado['Tipo de Producto 43/'] = df_resultado.apply(producto_37, axis=1)

print(df_resultado[df_resultado['Tipo de Producto 43/'] == 37][['Tipo de Producto 43/', 'Nombre PlanillaTXT']])
print('en total son: ' + str(df_resultado[df_resultado['Tipo de Producto 43/'] == 37].shape[0]))
#si salen 37s y la coopac es porque sí funciona

#%%% limpieza
'por si acaso quitando espacios a la columna del código del socio'

df_resultado['Código Socio 7/'] = df_resultado['Código Socio 7/'].str.strip()

#%% LECTURA DE INFORMACIÓN DE LOS 6 ÚLTIMOS MESES
conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')

f_corte_sql = fecha_corte[0:4] + fecha_corte[5:7] + fecha_corte[8:10]

query = f'''
DECLARE @fechacorte AS VARCHAR(8) = '{f_corte_sql}';

DECLARE @fecha6MESES AS DATETIME;
SET @fecha6MESES = EOMONTH(DATEADD(MONTH, -5, EOMONTH(CONVERT(DATETIME, @fechacorte, 112))));

SELECT 
	Nro_Fincore, 
	CodigoSocio7,
	Saldodecolocacionescreditosdirectos24,
	FechaCorte1,
	TipodeProducto43,
	CASE 
		WHEN TipodeProducto43 IN (34,35,36,37,38,39)       THEN 'DXP'
		WHEN TipodeProducto43 IN (30,31,32,33)             THEN 'LIBRE DISPONIBILIDAD'
		WHEN TipodeProducto43 IN (15,16,17,18,19)          THEN 'PEQUEÑA EMPRESA'
		WHEN TipodeProducto43 IN (21,22,23,24,25,26,27,29) THEN 'MICRO EMPRESA'
		WHEN TipodeProducto43 IN (95,96,97,98,99)          THEN 'MEDIANA EMPRESA'
		WHEN TipodeProducto43 IN (41,45)                   THEN 'HIPOTECARIA'
		    ELSE 'OTROS'
            
		END AS 'TIPO_PRODUCTO'
FROM 
	anexos_riesgos3..ANX06
WHERE 
	FechaCorte1 >= @fecha6MESES
ORDER BY 
	FechaCorte1,
	CodigoSocio7
'''
    
base_6meses = pd.read_sql_query(query, conn)

base_6meses['Saldodecolocacionescreditosdirectos24'] = pd.to_numeric(base_6meses['Saldodecolocacionescreditosdirectos24'])

del conn

#%% PIVOT DE CODIGO SOCIO Y FECHA CORTE (SOLO MYPES)
base_6meses = base_6meses[base_6meses['TipodeProducto43'].isin(prod43_mype)]

pivot_6meses = base_6meses.pivot_table( values  = 'Saldodecolocacionescreditosdirectos24',
                                        index   = 'CodigoSocio7',
                                        columns = 'FechaCorte1',
                                        aggfunc = 'sum').reset_index()
pivot_6meses = pivot_6meses.fillna(0)

#%% RECALCULAR PROD 43
#vamos a volver a calcular el tipo de producto43

df_corto = df_resultado[['Tipo de Producto 43/',
                         'Saldos de Créditos Castigados 38/',
                         'Saldo de colocaciones (créditos directos) 24/',
                         'Código Socio 7/']]

#sumamos saldo de cartera y saldo castigado
df_corto.loc[:, 'monto mype'] = df_corto['Saldo de colocaciones (créditos directos) 24/'] + df_corto['Saldos de Créditos Castigados 38/']

# convierte la columna 'Tipo de Producto 43/' al tipo de dato int
df_corto['Tipo de Producto 43/'] = df_corto['Tipo de Producto 43/'].astype(int)

#filtrado
corto_filtrado = df_corto.loc[df_corto['Tipo de Producto 43/'].isin(prod43_mype)]
#tabla resumen de sumarización						                                          
tabla_resumen = corto_filtrado.groupby('Código Socio 7/')['monto mype'].sum()
tabla_resumen = tabla_resumen.reset_index()

#rename
tabla_resumen = tabla_resumen.rename(columns={"Código Socio 7/": "socio mype"})

tabla_resumen = tabla_resumen.merge(pivot_6meses,
                                    left_on  = "socio mype",
                                    right_on = 'CodigoSocio7',
                                    how      = 'left')
del tabla_resumen['CodigoSocio7']
tabla_resumen.fillna(0, inplace = True)

def verificar_mype(fila):
    if any(valor > 300000 for valor in fila[1:]):
        return 'MEDIANA'
    elif any(valor > 20220 for valor in fila[1:]):
        return 'PEQUE'
    else:
        return 'MICRO'
    
tabla_resumen['tipo mype'] = tabla_resumen.apply(verificar_mype, axis = 1)

#%%% asignación del monto mype sumado
#asignamos
df_resultado_2 = df_resultado.copy()

df_resultado_2 = df_resultado_2.merge(tabla_resumen[['socio mype','tipo mype']], 
                                      how      ='left', 
                                      left_on  =['Código Socio 7/'], 
                                      right_on =['socio mype'])

df_resultado_2['tipo mype'] = df_resultado_2['tipo mype'].fillna('no es mype')

x = df_resultado_2.columns

#%%% asignación mype
df_resultado_2['Tipo de Producto 43/'] = df_resultado_2['Tipo de Producto 43/'].astype(float)

def asignacion_mype(df_resultado_2):
    if df_resultado_2['Tipo de Producto 43/'] in prod43_mype:
        if df_resultado_2['tipo mype'] == 'MICRO':
            return 20
        elif df_resultado_2['tipo mype'] == 'PEQUE':
            return 10
        else:
            return 90
    else:
        return df_resultado_2.loc['Tipo de Producto 43/']

df_resultado_2['producto_mype_2'] = df_resultado_2.apply(asignacion_mype, axis=1)
df_resultado_2['Tipo de Producto 43/'] = df_resultado_2['Tipo de Producto 43/'].truncate(0) #no está haciendo nada este código xd

#%%% resta decenas
#nos muestra si hay alguna diferencia en la parte de las decenas de la asignación del tipo de producto 43
df_resultado_2['resta_decenas'] = ((df_resultado_2['producto_mype_2'] // 10) - (df_resultado_2['Tipo de Producto 43/'] // 10))

#%%% asignación mype
'ahora que ya tenemos la diferencia del tipo de producto, asignamos el tipo de producto que deben de tener'
def asign_mype(df_resultado_2):
    if (df_resultado_2['resta_decenas'] == 1):
        ######################################################################
        if (df_resultado_2['Tipo de Producto 43/'] == 15):                   #
            return 22                                                        #
        elif (df_resultado_2['Tipo de Producto 43/'] == 16):                 #
            return 23                                                        #
        elif (df_resultado_2['Tipo de Producto 43/'] == 17):                 #
            return 24                                                        #
        elif (df_resultado_2['Tipo de Producto 43/'] == 18):                 #
            return 18 #20 #no tiene equivalente                              #
        elif (df_resultado_2['Tipo de Producto 43/'] == 19):                 #
            return 29                                                        #
        ######################################################################
    if (df_resultado_2['resta_decenas'] == -1):
        if (df_resultado_2['Tipo de Producto 43/'] == 21):
            return 16 #no tenía equivalente
        elif (df_resultado_2['Tipo de Producto 43/'] == 22):
            return 15
        elif (df_resultado_2['Tipo de Producto 43/'] == 23):
            return 16
        elif (df_resultado_2['Tipo de Producto 43/'] == 24):
            return 17
        elif (df_resultado_2['Tipo de Producto 43/'] == 25):
            return 10 #no hay equivalente
        elif (df_resultado_2['Tipo de Producto 43/'] == 29):
            return 19
    elif (df_resultado_2['resta_decenas'] == 8):
        if (df_resultado_2['Tipo de Producto 43/'] == 15):
            return 95 #no tiene equivalente
        elif (df_resultado_2['Tipo de Producto 43/'] == 16):
            return 96
        elif (df_resultado_2['Tipo de Producto 43/'] == 17):
            return 97
        elif (df_resultado_2['Tipo de Producto 43/'] == 18):
            return 98
        elif (df_resultado_2['Tipo de Producto 43/'] == 19):
            return 99
        ######################################################################
    elif (df_resultado_2['resta_decenas'] == -8):                            #
        if (df_resultado_2['Tipo de Producto 43/'] == 95):                   #
            return 15 #no tiene equivalente                                  #
        elif (df_resultado_2['Tipo de Producto 43/'] == 96):                 #
            return 16                                                        #
        elif (df_resultado_2['Tipo de Producto 43/'] == 97):                 #
            return 17                                                        #
        elif (df_resultado_2['Tipo de Producto 43/'] == 98):                 #
            return 18                                                        #
        elif (df_resultado_2['Tipo de Producto 43/'] == 99):                 #
            return 19                                                        #
        ######################################################################
    else:
        return df_resultado_2.loc['Tipo de Producto 43/']

df_resultado_2['producto final'] = df_resultado_2.apply(asign_mype, axis=1)
df_resultado_2['Tipo de Producto 43/ corregido'] = df_resultado_2['producto final']

#esta columna tiene el tipo de producto43 ya corregido
#%%% comprobación mype
#comprobación de las diferencias de tipo de producto
df_resultado_2['anterior'] = df_resultado_2['Tipo de Producto 43/']
df_resultado_2['producto final'] = pd.to_numeric(df_resultado_2['producto final'])
df_resultado_2['anterior'] = pd.to_numeric(df_resultado_2['anterior'])

def comprobac(df_resultado_2):
    if df_resultado_2['producto final'] - df_resultado_2['anterior'] != 0:
        return 'diferente'
    else:
        return '='
    
df_resultado_2['dif_prod'] = df_resultado_2.apply(comprobac, axis=1)

df_resultado_2['Tipo de Producto 43/'] = df_resultado_2['Tipo de Producto 43/ corregido']


print('se reasignaron ' + str(df_resultado_2[df_resultado_2['dif_prod'] == 'diferente'].shape[0]) + ' créditos')

#%%% verificación de que cada socio mype tenga un úncio alineamiento
# VERIFICACIÓN DEL ALINEAMIENTO QUE ESTÉ IGUAL PARA TODOS LOS CRÉDITOS MYPE

anx06_filtered = df_resultado_2.copy()

# Seleccionar los TipodeProducto43 deseados
tipos_producto_deseados = prod43_mype
anx06_filtered = anx06_filtered[anx06_filtered['Tipo de Producto 43/'].isin(tipos_producto_deseados)]

# Calcular el conteo de diferentes productos por NumerodeDocumento10
grouped = anx06_filtered.groupby('Código Socio 7/').agg({'Tipo de Producto 43/': 'nunique'})
grouped.columns = ['DIFERENTES PRODUCTOS']

# Filtrar los grupos con más de un producto diferente
result = grouped[grouped['DIFERENTES PRODUCTOS'] > 1]
# SI SALE UN DATAFRAME VACÍO, TODO ESTÁ BIEN

result = result.reset_index()
print(result)
# 'alinear alineamiento de los que tienen diferentes productos'
# anx06_filtered['Tipo de Producto 43/'] = anx06_filtered['Tipo de Producto 43/'].astype(int)

# aver = df_resultado_2[df_resultado_2['Código Socio 7/'].isin(list(result['Código Socio 7/']))][['Código Socio 7/', 'Tipo de Producto 43/']]

# def prod_mype_aux(df):
#     if df['Tipo de Producto 43/'] in prod_mic:
#         return 'micro'
#     if df['Tipo de Producto 43/'] in prod_peq:
#         return 'peque'
#     if df['Tipo de Producto 43/'] in prod_med:
#         return 'media'
# aver['tipo'] = aver.apply(prod_mype_aux, axis=1)

# grouped = aver.groupby('Código Socio 7/').agg({'tipo': 'nunique'}).reset_index()
# modificar = grouped[grouped['tipo'] > 1]

# def ahora_si(df):

#%% CRÉDITOS MAYORES A 50K QUE NO SEAN MYPE PARA ANALIZARLOS
# POR SI ACASO, BUSCAMOS CRÉDITOS CON MONTOS MAYORES A 50K QUE NO SEAN MYPE

not_in = prod43_mype + [41, 45, '41', '45']
mayores_para_investigar = df_resultado_2[~df_resultado_2['Tipo de Producto 43/'].isin(not_in)]
mayores_para_investigar = mayores_para_investigar[mayores_para_investigar['Saldo de colocaciones (créditos directos) 24/'] > 50000]
print(mayores_para_investigar[['Nro Prestamo \nFincore', 
                               'Fecha de Desembolso 21/', 
                               'Tipo de Producto 43/']])

if mayores_para_investigar.shape[0]:
    mayores_para_investigar[['Apellidos y Nombres / Razón Social 2/',
                             'Nro Prestamo \nFincore', 
                             'Fecha de Desembolso 21/', 
                             'Tipo de Producto 43/']].to_excel('créditos medio raros.xlsx')
#%% conclusión
#########################################################################################
#### HASTA AQUÍ YA TERMINAMOS EL TIPO DE PRODUCTO 43/, LO QUE SIGUE SON OTRAS COSAS  #####
#########################################################################################

#%% cambio de nombre
#AÑADIENDO UNA COLUMNA QUE ES LO MISMO QUE OTRA PERO CON OTRO NOMBRE
df_resultado_2['Fecha Ultimo Pago'] = df_resultado_2['Fecha Ultimo \nPago TXT']

#%% REUBICACIÓN DE COLUMNAS
#moviendo estas dos columnas al final

lista_columns = list(df_resultado_2.columns)
columna_a_mover = "periodo de gracia por Reprog inicio"
lista_columns.remove(columna_a_mover)
columna_a_mover = "periodo de gracia por Reprog Término"
lista_columns.remove(columna_a_mover)

# Agrega el nombre de la columna al final de la lista
columnas_nuevas = lista_columns + ["periodo de gracia por Reprog inicio"]
columnas_nuevas = columnas_nuevas + ["periodo de gracia por Reprog Término"]

# Reordena las columnas del DataFrame utilizando la nueva lista de nombres de columnas
df_resultado_2 = df_resultado_2.reindex(columns=columnas_nuevas)

#%% parseo de fechas
#parseando datos

#aqui hay riesgo de perder fechas si es que están mal escritas
#usar el algoritmo verificador para comprobar
conteo1 = df_resultado_2["periodo de gracia por Reprog inicio"].value_counts()['--']
print('guiones: ',str(conteo1))
df_resultado_2["periodo de gracia por Reprog inicio"] = \
pd.to_datetime(df_resultado_2["periodo de gracia por Reprog inicio"], format='%Y-%m-%d %H:%M:%S', errors='coerce')
df_resultado_2["periodo de gracia por Reprog inicio"] = df_resultado_2["periodo de gracia por Reprog inicio"].dt.date
print('guiones después de procesar: ', str(df_resultado_2["periodo de gracia por Reprog inicio"].isna().sum()))

conteo2 = df_resultado_2["periodo de gracia por Reprog Término"] .value_counts()['--']
print('guiones: ',str(conteo2))
df_resultado_2["periodo de gracia por Reprog Término"] = \
pd.to_datetime(df_resultado_2["periodo de gracia por Reprog Término"], format='%Y-%m-%d %H:%M:%S', errors='coerce')
df_resultado_2["periodo de gracia por Reprog Término"] = df_resultado_2["periodo de gracia por Reprog Término"].dt.date
print('guiones después de procesar: ', str(df_resultado_2["periodo de gracia por Reprog Término"].isna().sum()))

#%% fecha término de gracia por desembolso 
#
def fechatermino(fecha, periodo_gracia):
    return fecha + pd.DateOffset(days = periodo_gracia)

df_resultado_2['fecha término de gracia por desembolso'] = df_resultado_2.apply(
    lambda x: fechatermino(x['Fecha de Desembolso 21/'], x['Periodo de Gracia 47/']), axis=1)

x = df_resultado_2[['fecha término de gracia por desembolso','Fecha de Desembolso 21/', 'Periodo de Gracia 47/']]


#%% DD vs DF
#DD vs DF
def DD_vs_DF(df_resultado_2):
    if pd.isna(df_resultado_2['fecha término de gracia por desembolso']):
        return df_resultado_2["periodo de gracia por Reprog Término"]
    elif pd.isna(df_resultado_2["periodo de gracia por Reprog Término"]):
        return df_resultado_2['fecha término de gracia por desembolso']
    else:
        return max(df_resultado_2['fecha término de gracia por desembolso'], df_resultado_2["periodo de gracia por Reprog Término"])

df_resultado_2['DD vs DF'] = df_resultado_2.apply(DD_vs_DF, axis=1)

#%% reubicación de columna
#moviendo esa columna al final
df_resultado_2['''Fecha Venc de Ult Cuota Cancelada
Contabilidad''']= df_resultado_2['''Fecha Venc de Ult Cuota Cancelada
(NVO)''']

#%% DG vs BW
#cálculo de las columnas de fechas
df_resultado_2['Fecha Ultimo Pago'] = \
pd.to_datetime(df_resultado_2['Fecha Ultimo Pago'], 
               format='%Y-%m-%d %H:%M:%S', errors='coerce')
df_resultado_2['Fecha Ultimo Pago'] = df_resultado_2['Fecha Ultimo Pago'].dt.date

def DG_vs_BW(df_resultado_2):
    if pd.isna(df_resultado_2['DD vs DF']):
        return df_resultado_2['Fecha Ultimo Pago']
    elif pd.isna(df_resultado_2['Fecha Ultimo Pago']):
        return df_resultado_2['DD vs DF']
    else:
        return max(df_resultado_2['DD vs DF'], df_resultado_2['Fecha Ultimo Pago'])

df_resultado_2['DG vs BW'] = df_resultado_2.apply(DG_vs_BW, 
                                                  axis=1)

#%% DG vs BW con FVUCC
df_resultado_2['Fecha Venc de Ult Cuota Cancelada\nContabilidad'] = \
pd.to_datetime(df_resultado_2['Fecha Venc de Ult Cuota Cancelada\nContabilidad'], 
               format = '%Y-%m-%d %H:%M:%S', 
               errors = 'coerce')

#truncamos las horas minutos y nos quedamos solo con las fechas
df_resultado_2['Fecha Venc de Ult Cuota Cancelada\nContabilidad'] = \
df_resultado_2['Fecha Venc de Ult Cuota Cancelada\nContabilidad'].dt.date

#rename
df_resultado_2 = df_resultado_2.rename(columns={'''Fecha Venc de Ult Cuota Cancelada
Contabilidad''': '''Fecha Venc de Ult Cuota Cancelada Contabilidad'''})

#cálculo de DG vs BW con FVUCC
def con_fvucc(df_resultado_2):
    if pd.isna(df_resultado_2['Fecha Venc de Ult Cuota Cancelada Contabilidad']):
        return df_resultado_2['DG vs BW']
    else:
        return df_resultado_2['Fecha Venc de Ult Cuota Cancelada Contabilidad']

df_resultado_2['DG vs BW con FVUCC'] = df_resultado_2.apply(con_fvucc, 
                                                            axis=1)

#%% DH vs CS
#noup
fecha_fija = pd.to_datetime(fecha_corte)

# Definir función para aplicar a cada fila
def max_fecha(row):
    if pd.isna(row['DG vs BW con FVUCC']):
        return (fecha_fija - row['Fecha de Desembolso 21/']).days
    else:
        return max((fecha_fija - row['DG vs BW con FVUCC']).days, 0)
                   

# Aplicar la función a cada fila del DataFrame
df_resultado_2['DH vs CS'] = df_resultado_2.apply(max_fecha, axis=1)

#%% DH vs CS
#calculando 'DH vs CS'para los créditos que tienen días mora

def dh_vs_cs_morosos(row, dias_sumar):
    if row['Dias de Mora 33/'] > 0:
        return row['Dias de Mora 33/'] + dias_sumar
    else:
        return row['DH vs CS']

df_resultado_2['DH vs CS 2'] = df_resultado_2.apply(dh_vs_cs_morosos, 
                                                    axis=1,
                                                    args=(dias_corte,))

df_resultado_2['DH vs CS'] = df_resultado_2['DH vs CS 2']
df_resultado_2.drop(['DH vs CS 2'], axis=1, inplace=True)

#%% DH vs CS
#calculando DH vs CS para los que tienen capital vigente y vencido al mismo tiempo
def dh_vs_ambos(df_resultado_2, dias_sumar):
    if (df_resultado_2['Capital Vigente 26/'] > 0 and \
        df_resultado_2['Capital Vencido 29/'] > 0):
        return dias_sumar
    else:
        return df_resultado_2['DH vs CS']

df_resultado_2['DH vs CS 2'] = df_resultado_2.apply(dh_vs_ambos, 
                                                    axis=1,
                                                    args=(dias_corte,))

df_resultado_2['DH vs CS'] = df_resultado_2['DH vs CS 2']
df_resultado_2.drop(['DH vs CS 2'], axis=1, inplace=True)

#%% DH vs CS creditos monocuotas
#modificación de DH VS CS, para créditos monocuotas
####################
# verificar si funciona bien, yo creo que sí uwu
####################

def dfvscs_monocuota(df_resultado_2):
    if df_resultado_2['Número de Cuotas Programadas 44/'] == 1:
        return float(max((fecha_fija - df_resultado_2['Fecha de Desembolso 21/']).days, 0)) #si algo falla, este debe ser
    else:
        return df_resultado_2['DH vs CS']

df_resultado_2['DH vs CS 2'] = df_resultado_2.apply(dfvscs_monocuota, 
                                                            axis=1)
df_resultado_2['DH vs CS'] = df_resultado_2['DH vs CS 2']
df_resultado_2.drop(['DH vs CS 2'], axis=1, inplace=True)
    
#%% DH vs CS ajuste
#modificación de dh vs cs de los devengados, vamos a 
#cambiar algunos porque Jenny se ha hueveado
########################################################
#segunda parte de los devengados, vamos a cambiar algunos porque Jenny se ha hueveado
#import os
#import pandas as pd

#os.chdir('C:\\Users\\sanmiguel38\\Desktop\\TRANSICION  ANEXO 6\\2023 abril')
#df_resultado_2 = pd.read_excel('ANX06 procesado 2023-04-30 enviado por Jenny.xlsx',
#                               skiprows=2)


df_resultado_2['Fecha Venc de Ult Cuota Cancelada Contabilidad temporal'] = \
df_resultado_2['Fecha Venc de Ult Cuota Cancelada Contabilidad'].fillna('--')
'''
def modificacion_dhvscs(df_resultado_2):
    if (((df_resultado_2['Capital Vigente 26/'] > 0) and \
        (df_resultado_2['Capital Vencido 29/'] > 0))) and \
        df_resultado_2['Fecha Venc de Ult Cuota Cancelada Contabilidad temporal'] == '--':
        
        return (fecha_fija - df_resultado_2['Fecha de Desembolso 21/']).days
    
    elif (((df_resultado_2['Capital Vigente 26/'] > 0) and \
        (df_resultado_2['Capital Vencido 29/'] > 0))) and \
        df_resultado_2['Fecha Venc de Ult Cuota Cancelada Contabilidad temporal'] != '--':
        
        return (fecha_fija - df_resultado_2['Fecha Venc de Ult Cuota Cancelada Contabilidad']).days
    else:
        return df_resultado_2['DH vs CS']

df_resultado_2['DH vs CS 2'] = df_resultado_2.apply(modificacion_dhvscs, 
                                                            axis=1)
''' #esta vaina me ha fallado no sé porqué

def modificacion_dhvscs(row):
    fecha_fija = pd.Timestamp(fecha_corte) #'2023-05-31')  # Reemplaza 'yyyy-mm-dd'
    
    if ((row['Capital Vigente 26/'] > 0) and (row['Capital Vencido 29/'] > 0)) and \
            row['Fecha Venc de Ult Cuota Cancelada Contabilidad temporal'] == '--':
        fecha_desembolso = pd.to_datetime(row['Fecha de Desembolso 21/'])
        return (fecha_fija - fecha_desembolso).days

    elif ((row['Capital Vigente 26/'] > 0) and (row['Capital Vencido 29/'] > 0)) and \
            row['Fecha Venc de Ult Cuota Cancelada Contabilidad temporal'] != '--':
        fecha_cancelada = pd.to_datetime(row['Fecha Venc de Ult Cuota Cancelada Contabilidad'])
        return (fecha_fija - fecha_cancelada).days

    else:
        return row['DH vs CS']

df_resultado_2['DH vs CS 2'] = df_resultado_2.apply(modificacion_dhvscs, axis=1)


df_resultado_2['DH vs CS'] = df_resultado_2['DH vs CS 2']
df_resultado_2.drop(['DH vs CS 2'], axis=1, inplace=True)


#%% DEVENGADOS
'intereses devengados, calculados de manera genérica'
def devengados_genericos(df_resultado_2):
    if df_resultado_2['Número de Cuotas Programadas 44/'] != 1:
        return df_resultado_2['Capital Vigente 26/']* (\
       (((1+(df_resultado_2['Tasa Diaria']/100))**df_resultado_2['DH vs CS']))-1)
    elif df_resultado_2['Número de Cuotas Programadas 44/'] == 1:
        return df_resultado_2['Capital Vigente 26/']* (\
       (((1+(df_resultado_2['Tasa Diaria']/100))**float(max((fecha_fija - df_resultado_2['Fecha de Desembolso 21/']).days, 0))))-1)
    
df_resultado_2['rendimiento devengado'] = df_resultado_2.apply(devengados_genericos, axis=1)
df_resultado_2['rendimiento devengado'] = df_resultado_2['rendimiento devengado'].round(2)

# df_resultado_2['Rendimiento\nDevengado 40/'] = df_resultado_2['rendimiento devengado']

#%% días para intereses en suspenso
'intereses en suspenso, calculados de manera genérica'

fecha_fija = pd.to_datetime(fecha_corte)

import pandas as pd
#from datetime import datetime

def dias_suspenso(row):
    # verificamos que las columnas 'Capital Vigente 26/' y 'Capital Vencido 29/' sean mayores que cero
    if (row['Capital Vigente 26/'] > 0) & (row['Capital Vencido 29/'] > 0):
        # si se cumple la condición, retornamos la columna 'Dias de Mora 33/'
        return row['Dias de Mora 33/']
    else:
        # si no se cumple la condición, calculamos la diferencia de días entre la fecha '28-03-2023' y la fecha en 'DG vs BW con FVUCC'
        fecha1 = datetime.strptime(fecha_corte, '%Y-%m-%d').date()
        fecha2 = row['DG vs BW con FVUCC'].strftime('%Y-%m-%d')
        fecha2 = datetime.strptime(fecha2, '%Y-%m-%d').date()
        dias_suspenso = (fecha1 - fecha2).days
        # retornamos el resultado
        return dias_suspenso

df_resultado_2['dias int suspenso'] = df_resultado_2.apply(dias_suspenso, axis=1)

#%% #reemplazando los negativos
def ceros(df_resultado_2):
    if df_resultado_2['dias int suspenso'] < 0:
        return 0
    else:
        return df_resultado_2['dias int suspenso']

df_resultado_2['dias int suspenso'] = df_resultado_2.apply(ceros, axis=1)

#%% dias int suspenso
#última parte de los días en suspenso:
def ultima_dias_suspenso(df_resultado_2):
    fecha1 = datetime.strptime(fecha_corte, '%Y-%m-%d').date()
    fecha2 = df_resultado_2['DG vs BW con FVUCC'].strftime('%Y-%m-%d')
    fecha2 = datetime.strptime(fecha2, '%Y-%m-%d').date()

    if (fecha1 - fecha2).days < df_resultado_2['Dias de Mora 33/']:
        return df_resultado_2['Dias de Mora 33/'] + dias_corte
    else:
        return df_resultado_2['dias int suspenso']
    
df_resultado_2['dias int suspenso 2'] = df_resultado_2.apply(ultima_dias_suspenso, axis=1)

df_resultado_2['dias int suspenso'] = df_resultado_2['dias int suspenso 2']
df_resultado_2.drop(['dias int suspenso 2'], axis=1, inplace=True)

#%% dias int suspenso
#lo anterior ya no era lo último 
#añadiendo unas excepciones
  
def modificacion_dias_suspenso(row):
    fecha_fija = pd.Timestamp(fecha_corte)  # 'yyyy-mm-dd' FECHA DE CORTE
    
    if ((row['Capital Vigente 26/'] > 0) and (row['Capital Vencido 29/'] > 0)) and \
            row['Fecha Venc de Ult Cuota Cancelada Contabilidad temporal'] == '--':
        fecha_desembolso = pd.to_datetime(row['Fecha de Desembolso 21/'])
        return (fecha_fija - fecha_desembolso).days

    elif ((row['Capital Vigente 26/'] > 0) and (row['Capital Vencido 29/'] > 0)) and \
            row['Fecha Venc de Ult Cuota Cancelada Contabilidad temporal'] != '--':
        fecha_cancelada = pd.to_datetime(row['Fecha Venc de Ult Cuota Cancelada Contabilidad'])
        return (fecha_fija - fecha_cancelada).days

    else:
        return row['dias int suspenso']

df_resultado_2['dias int suspenso 2'] = df_resultado_2.apply(modificacion_dias_suspenso, 
                                                             axis = 1)
df_resultado_2['dias int suspenso'] = df_resultado_2['dias int suspenso 2']
df_resultado_2.drop(['dias int suspenso 2'], 
                    axis    = 1,
                    inplace = True)

#%% INTERESES EN SUSPENSO
'intereses en suspenso'
def int_suspenso(df_resultado_2):
    return (df_resultado_2['Capital Vencido 29/'] + df_resultado_2['Capital en Cobranza Judicial 30/'])* (\
    (((1+(df_resultado_2['Tasa Diaria']/100))**df_resultado_2['dias int suspenso']))-1)

df_resultado_2['intereses en suspenso'] = df_resultado_2.apply(int_suspenso, axis=1)

df_resultado_2['Intereses en Suspenso 41/'] = df_resultado_2['Interes Suspenso Nuevo']

df_resultado_2['Intereses en Suspenso 41/'].sum()

#%% REASIGNAMOS DEVENGADOS Y SUSPENSO DEL FINCORE AL ANEXO 06

col_devengado = 'Interes Devengado Nuevo'
col_suspenso  = 'Interes Suspenso Nuevo'

# # 'Interes\nDevengado Total'
# # 'Interes \nSuspenso Total'

# df_resultado_2['Rendimiento\nDevengado 40/'] = df_resultado_2[col_devengado].round(2)

# df_resultado_2['Intereses en Suspenso 41/'] = df_resultado_2[col_suspenso].round(2)

#%% antes de asignar devengados, vamos a revisar unos casitos
fecha_corte_datetime = pd.Timestamp(fecha_corte[0:8] + '01')

df_resultado_2['Fecha de Desembolso 21/'] = pd.to_datetime(df_resultado_2['Fecha de Desembolso 21/'])

inv = df_resultado_2[(df_resultado_2['Rendimiento\nDevengado 40/']        == 0) &
                     (df_resultado_2['Intereses en Suspenso 41/']         == 0) &
                     (df_resultado_2['Saldos de Créditos Castigados 38/'] == 0) &
                     (df_resultado_2['Número de Cuotas Pagadas 45/']      == 0) &
                     (df_resultado_2['Fecha de Desembolso 21/'] >= fecha_corte_datetime) &
                     (df_resultado_2['Fecha de Desembolso 21/'] < pd.Timestamp(fecha_corte)) &
                     
                     ~( # ojo que es una negación de las siguientes características:
                     (df_resultado_2['Flag Termino Periodo Gracia'] == 'SI') &
                     (df_resultado_2['Número de Cuotas Pagadas 45/'] == 0) &
                     (df_resultado_2['Fecha de Desembolso 21/'] >= pd.Timestamp('2023-01-01')) #no cambiar esta fecha
                     ) & 
                     # esto ya no es negación xd
                     (df_resultado_2['Refinanciado TXT'] != 'REFINANCIADO')
                     ]

print(inv[['Fecha de Desembolso 21/', 'Nro Prestamo \nFincore']].shape[0])
print('si sale más de cero, es porque hay unos casos a los cuales aplicarles cálculo de devengados')

cred_para_calc = list(inv['Nro Prestamo \nFincore'])
# asignación de devengados a los casos estos
def dev_0_vigente(df_resultado_2):
    if (df_resultado_2['Nro Prestamo \nFincore'] in cred_para_calc) and \
        (1==1):
        return df_resultado_2['Capital Vigente 26/']* (\
        (((1+(df_resultado_2['Tasa Diaria']/100))**float(max((fecha_fija - df_resultado_2['Fecha de Desembolso 21/']).days, 0))))-1)
    else:
        return df_resultado_2['Rendimiento\nDevengado 40/']
    
df_resultado_2['Rendimiento\nDevengado 40/'] = df_resultado_2.apply(dev_0_vigente, axis = 1)
df_resultado_2['Rendimiento\nDevengado 40/'] = df_resultado_2['Rendimiento\nDevengado 40/'].round(2)

print(df_resultado_2[col_devengado].sum())
print(df_resultado_2['Rendimiento\nDevengado 40/'].sum())

def dev_0_ref(df_resultado_2):
    if (df_resultado_2['Nro Prestamo \nFincore'] in cred_para_calc) and (df_resultado_2['Capital Refinanciado 28/'] > 0):
        return df_resultado_2['Capital Refinanciado 28/']* (\
        (((1+(df_resultado_2['Tasa Diaria']/100))**float(max((fecha_fija - df_resultado_2['Fecha de Desembolso 21/']).days, 0))))-1)
    else:
        return df_resultado_2['Rendimiento\nDevengado 40/']
    
df_resultado_2['Rendimiento\nDevengado 40/'] = df_resultado_2.apply(dev_0_ref, axis= 1)
df_resultado_2['Rendimiento\nDevengado 40/'] = df_resultado_2['Rendimiento\nDevengado 40/'].round(2)

# Filtrado para verificar
condicion1 = df_resultado_2['Nro Prestamo \nFincore'].isin(list(inv['Nro Prestamo \nFincore']))
condicion2 = (df_resultado_2['Rendimiento\nDevengado 40/'] == 0)

print(df_resultado_2[condicion1 & condicion2].shape[0])

#%% procedimiento eliminado
'AHORA CALCULAR LOS INTERESES DIFERIDOS'
#necesario para poder calcular la cartera neta = 
#Saldo de colocaciones (créditos directos) 24/ - Ingresos Diferidos 42/

'de momento no se va a poder programar, no tenemos info, el contador general lo va a realizar, y tendremos que volver a procesar el archivo'
#%% CARTERA NETA
'AHORA QUE YA TENEMOS LOS INGRESOS DIFERIDOS'
#calculamos la cartera neta
def cartera_neta(df_resultado_2):
    return df_resultado_2['Saldo de colocaciones (créditos directos) 24/'] - \
        df_resultado_2['Ingresos Diferidos 42/']
        
df_resultado_2['Cartera Neta'] = df_resultado_2.apply(cartera_neta, axis=1)

#%% Provisiones Requeridas 36/ SA
#cálculo de provisiones requeridas 36 SA

df_resultado_2['Provisiones Requeridas 36/ SA'] = df_resultado_2['Cartera Neta'] * \
                                                  df_resultado_2['Tasa de Provisión SA']

df_resultado_2['Provisiones Requeridas 36/ SA'] = df_resultado_2['Provisiones Requeridas 36/ SA'].round(2)

#%% Provisiones Constituidas 37/
#cálculo de las provisiones constituidas 37/
def prov_cons_37(df_resultado_2):
    if df_resultado_2['''Nro Prestamo 
Fincore'''] in ['00000681',*
                '00025314',*
                '00025678',
                '00001346',
                '00009592',
                '00050796',
                '00021245',
                '00014203',
                '00019911',
                '00052890',
                '00020153',
                '00000633',
                '00021016',
                '00000942',
                '00023215',
                '00020154',
                '00054955',
                '00016572',
                '00001147',
                '00001287',
                '00021994'
] or \
(df_resultado_2['Tipo de Producto 43/'] in ['34','35','36','37','38','39', 34,35,36,37,38,39]) and \
    (df_resultado_2['Dias de Mora 33/'] > 360):
        return df_resultado_2['Provisiones Requeridas 36/']
    else:
        return  df_resultado_2['Provisiones Requeridas 36/'] * 0.52 # 0.50 es lo mínimo

df_resultado_2['Provisiones Constituidas 37/'] = df_resultado_2.apply(prov_cons_37, 
                                                                      axis=1)

df_resultado_2['Provisiones Constituidas 37/'] = df_resultado_2['Provisiones Constituidas 37/'].round(2)
df_resultado_2['Provisiones Requeridas 36/'] = df_resultado_2['Provisiones Requeridas 36/'].round(2)

print(df_resultado_2['Provisiones Constituidas 37/'].sum())
print(df_resultado_2['Provisiones Requeridas 36/'].sum())


#%% CÁLCULOS
'VERIFICACIÓN'
#LAS PROVISIONES CONSTITUIDAS DEL MES, DEBEN SER (EN MONTO) MAYORES A LA DEL MES PASADO
#Y LAS PROVISIONES CONSTITUIDAS DIVIDIDAS ENTRE LAS PROVISIONES REQUERIDAS DEBE SER > 60%

suma_requeridas = df_resultado_2['Provisiones Requeridas 36/'].sum()
suma_constituidas = df_resultado_2['Provisiones Constituidas 37/'].sum()

div = suma_constituidas/suma_requeridas
print('EL PORCENTAJE ES: ',"{:.2f}%".format(div*100))
print('constituidas mes pasado: 8824428.8200')
print(suma_constituidas)

#hay que revisar bien, porque en algún momento se cambiaron estos valores,
#pues se llegó a asignar correctamente las provisiones, pero luego qué chucha habrá pasado

print(df_resultado_2['Provisiones Constituidas 37/'].sum() / df_resultado_2['Cartera Atrasada'].sum())

#%% COLUMNAS CONTABILIDAD
#añadiendo las columnas que Jenny necesita

df_resultado_2['FEC_REPROG'] = df_resultado_2['FEC_ULT_REPROG']

# reemplazar guiones con None
df_resultado_2['FEC_REPROG'] = df_resultado_2['FEC_REPROG'].replace('--', None)

# convertir a datetime
df_resultado_2['FEC_REPROG'] = pd.to_datetime(df_resultado_2['FEC_REPROG'], errors='coerce')

df_resultado_2['FEC_REPROG'] = df_resultado_2['FEC_REPROG'].fillna('--')

#%%% limpieza
# añadiendo -- a algunas columnas de fechas, para que las fórmulas de excel funcionen bien

df_resultado_2['Fecha Ultimo Pago'] = df_resultado_2['Fecha Ultimo Pago'].fillna('--')

#%% REDONDEO DE DEVENGADOS e I.SUSPENSO A DOS DECIMALES
#redondeando columnas 
df_resultado_2['rendimiento devengado'] = df_resultado_2['rendimiento devengado'].round(2) # mi estimación
df_resultado_2['intereses en suspenso'] = df_resultado_2['intereses en suspenso'].round(2) # mi estimación

#%% REDONDEO DE TEA A 4 DECIMALES
df_resultado_2['TEA TXT'] = df_resultado_2['Tasa de Interés Anual 23/'].round(4)

#%% 51/ 52/
#CALCULANDO LAS COLUMNAS 51 Y 52
#chequear, aún no está probado
df_resultado_2['Saldo de Créditos que no cuentan con cobertura 51/'] = df_resultado_2['Cartera Neta'] - \
                                                                        (df_resultado_2['Saldos de Garantías Preferidas 34/'] + \
                                                                         df_resultado_2['Saldo de Garantías Autoliquidables 35/'])
#chequear, aún no está probado     
'''                                                                 
def calculo_52(df_resultado_2):
    if df_resultado_2['FEC_ULT_REPROG'] != '--': 
        return df_resultado_2['Saldo de colocaciones (créditos directos) 24/']
    else:
        return 0

df_resultado_2['Saldo Capital de Créditos Reprogramados 52/'] = df_resultado_2.apply(calculo_52, axis=1) #chequear, aún no está probado
#chequear, aún no está probado
'''
#%% PRODUCTO TXT
#tipo de producto txt para hacer tablas dinámicas
def producto_txt(df_resultado_2):
    tipo_producto = df_resultado_2['Tipo de Producto 43/']
    
    if tipo_producto in prod_dxp:
        return 'DXP'
    elif tipo_producto in prod_ld:
        return 'LD'
    elif tipo_producto in prod_mic:
        return 'MICRO'
    elif tipo_producto in prod_peq:
        return 'PEQUEÑA'
    elif tipo_producto in prod_med:
        return 'MEDIANA'
    elif tipo_producto in prod_hip:
        return 'HIPOTECARIA'

df_resultado_2['TIPO DE PRODUCTO TXT'] = df_resultado_2.apply(producto_txt, axis=1)

#%% COLUMNAS ROJAS
#AÑADIENDO LAS COLUMNAS ROJAS PARA JENNY
df_resultado_2['Días de Diferido 1']   =  ''
df_resultado_2['Ingresos Diferidos 1'] =  ''
df_resultado_2['Días de Diferido 2']   =  ''
df_resultado_2['Ingresos Diferidos 2'] =  ''

#%% COLUMNAS AZULES PARA EVALUAR LA MOROSIDAD DE DXP
#primera columna
df_resultado_2['Tipo de Producto 43/'] = df_resultado_2['Tipo de Producto 43/'].astype(int).astype(str)

def import_vencido_60_dxp(df_resultado_2):
    if (df_resultado_2['Tipo de Producto 43/'] in ['30','31','32','33','34','35','36','37','38','39']):
        if (df_resultado_2['Dias de Mora 33/'] > 90):
            return df_resultado_2['Saldo de colocaciones (créditos directos) 24/']
        elif (df_resultado_2['Dias de Mora 33/'] > 60):
            return df_resultado_2['Capital Vencido 29/']
        else:
            return 0
    else:
        return df_resultado_2['Capital en Cobranza Judicial 30/']
        
df_resultado_2['''Importe Vencido > 60d
(Solo DxP)'''] = df_resultado_2.apply(import_vencido_60_dxp, axis=1)

#%% segunda columna azul
def dias_venc_consumo(df_resultado_2):
    if (df_resultado_2['Tipo de Producto 43/'] in ['30','31','32','33','34','35','36','37','38','39']):
        return df_resultado_2['Dias de Mora 33/']
    else:
        return 0

df_resultado_2['Dias vencido (Solo DxP)'] = df_resultado_2.apply(dias_venc_consumo, axis=1)

#%% tercera columna azul
def porcion_vencida(df_resultado_2):
    if (df_resultado_2['Tipo de Producto 43/'] in ['30','31','32','33','34','35','36','37','38','39']):
        if (df_resultado_2['Dias de Mora 33/'] > 90) or \
            (df_resultado_2['Capital en Cobranza Judicial 30/'] > 0):
            return 'TOTAL'
        
        elif (df_resultado_2['Dias de Mora 33/'] > 60):
            return 'PARCIAL'
    else:
        return '--'
    
df_resultado_2['Porción Vencido'] = df_resultado_2.apply(porcion_vencida, axis=1)

#%% 4ta columna azul
def situacion_cred_consumo(df_resultado_2):
    if (df_resultado_2['Tipo de Producto 43/'] in ['30','31','32','33','34','35','36','37','38','39']):
        return df_resultado_2['Tipo Credito TXT']
    else:
        return ''
    
df_resultado_2['Situación del Credito (Solo DxP)'] = df_resultado_2.apply(situacion_cred_consumo, axis=1)

#%% ordenamiento
'''
x = df_resultado_2.columns
df_x = pd.DataFrame(x, columns=['columnas'])

# exportar el dataframe a un archivo de Excel
df_x.to_excel('columnas.xlsx', index=False)
'''

columnas_casi_final = ['''Socios al menos con un cred < 100 soles
amarillo =  cred <100
rosado =  cred >= 100
 PROV.REQUERIDA A SER EVALUADA.''',
'''Registro 1/''',
'''Apellidos y Nombres / Razón Social 2/''',
'''Fecha de Nacimiento 3/''',
'''Género 4/''',
'''Estado Civil 5/''',
'''Sigla de la Empresa 6/''',
'''Código Socio 7/''',
'''Partida Registral 8/''',
'''Tipo de Documento 9/''',
'''Número de Documento 10/''',
'''Tipo de Persona 11/''',
'''Domicilio 12/''',
'''Relación Laboral con la Cooperativa 13/''',
'''Tasa de Provisión SA''',
'''Tasa de Provisión''',
'''Clasificación del Deudor 14/''',
'''alineamiento 15 anterior''',
'''Clasificación del Deudor con Alineamiento 15/''',
'''Código de Agencia 16/''',
'''Moneda del crédito 17/''',
'''Numero de Crédito 18/''',
'''Tipo de Crédito 19/''',
'''Sub Tipo de Crédito 20/''',
'''Fecha de Desembolso 21/''',
'''Monto de Desembolso Origuinal TXT''',
'''Monto de Desembolso 22/''',
'''Tasa de Interés Anual 23/''',
'''Saldo de colocaciones (créditos directos) 24/''',
'''Cuenta Contable 25/''',
'''Capital Vigente 26/''',
'''Capital Reestrucutado 27/''',
'''Capital Refinanciado 28/''',
'''Capital Vencido 29/''',
'''Capital en Cobranza Judicial 30/''',
'''Cartera Atrasada''',
'''Capital Contingente 31/''',
'''Cuenta Contable Capital Contingente 32/''',
'''Dias de Mora 33/''',
'''Saldos de Garantías Preferidas 34/''',
'''Saldo de Garantías Autoliquidables 35/''',
'''Provisiones Requeridas 36/ SA''',
'''Provisiones Requeridas 36/''',
'''Provisiones Constituidas 37/''',
'''Saldos de Créditos Castigados 38/''',
'''Cuenta Contable Crédito Castigado 39/''',
'Rendimiento\nDevengado 40/',
'''Intereses en Suspenso 41/''',
'''Ingresos Diferidos 42/''',
'''Tipo de Producto 43/ original''',
'''Tipo de Producto 43/''',
'''Número de Cuotas Programadas 44/''',
'''Número de Cuotas Pagadas 45/''',
'''Periodicidad de la cuota 46/''',
'''Periodo de Gracia 47/''',
'''Fecha de Vencimiento Origuinal del Credito 48/''',
'''Fecha de Vencimiento Actual del Crédito 49/''',
'''Saldo de Créditos con Sustitución de Contraparte Crediticia 50/''',
'''Saldo de Créditos que no cuentan con cobertura 51/''',
'''Saldo Capital de Créditos Reprogramados 52/''',
'''Saldo Capital en Cuenta de Orden por efecto del Covid 53/''',
'''Subcuenta de orden 
54/
''',
'''Rendimiento Devengado por efecto del COVID 19 55/''',
'''Saldo de Garantías con Sustitución de Contraparte 56/''',
'''Saldo Capital de Créditos Reprogramados por efecto del COVID 19 57/''',
'''FEC_ULT_REPROG''', #PINTAR AZUL
'''PLAZO_REPR''', #PINTAR AZUL
'''TIPO_REPRO''', #PINTAR AZUL
'''PLAZO REPRO ACUMULADO''', #PINTAR AZUL
'''NRO CUOTAS REPROG CANCELADAS''', #PINTAR AZUL
'''NRO REPROG''', #PINTAR AZUL
'''fecha desemb (v)''', #PINTAR AMARILLO
'''fecha término de gracia por desembolso ["v" + dias gracia (av)]''', #PINTAR AMARILLO
'''periodo de gracia por Reprog inicio''', #PINTAR AMARILLO
'''periodo de gracia por Reprog Término''', #PINTAR AMARILLO
'''Fecha Venc de Ult Cuota Cancelada
(NVO)''', #PINTAR AMARILLO
'''Categoria TXT''',
'''Saldo Colocacion Con Capitalizacion de Intereses TXT''',
'''Fecha Castigo TXT''',
'''Dscto Enviado TXT''',
'''Desc Pagado TXT''',
'''Fecha Vencimiento 
Origuinal TXT''',
'''Fecha Vencimiento Actual TXT''',
'''Fecha Creacion Reprogramacion Nacimiento TXT''',
'''Fecha Creacion Reprogramacion Corte TXT''',
'''Nro Dias Gracia Corte RPG TXT''',
'''Nro Cuotas Canc Post Regro''',
'''Nro Prestamos X Deudor TXT''',
'''Fecha Ultimo 
Pago TXT''',
'''Tipo Reprogramacion TXT''',
'''Fecha Primer Cuota Gracia Nacimiento RPG TXT''',
'''Primer Fecha Cuota Gracia Corte RPG TXT''',
'''Nro Reprogramaciones TXT''',
'''Origen
 Prestamo''',
'''Nro Prestamo 
Fincore''',
'''Por Cobrar Mes Actual TXT''',
'''Reprogramado TXT''',
'''Funcionaria TXT''',
'''Nombre Empresa TXT''',
'''Nombre PlanillaTXT''',
'''Planilla Anterior TXT''',
'''Cod Usuario Pri Aprob''',
'''Cod Usuario Seg Aprob''',
'''Profesion''',
'''Ocupacion''',
'''Actividad Economica''',
'''Fecha Venc Ult Cuota Cancelada''',
'''Departamento''',
'''Provincia''',
'''Distrito''',
'''Tipo Credito TXT''',
'''TEA TXT''',
'''Refinanciado TXT''',
'''Situacion TXT''',
'''Fecha Situacion TXT''',
'''Abogado TXT''',
'''Fecha Asignacion Abogado TXT''',
'''Nro Expediente TXT''',
'''Fecha Expediente TXT''',
'''Tasa Clasificacion  Deudor con Alineamiento TXT''',
'''Monto de Garantías Preferidas''',
'''Monto de Garantías Autoliquidables''',
'''Importe Vencido > 60d
(Solo DxP)''',
'''Dias vencido (Solo DxP)''',
'''Porción Vencido''',
'''Situación del Credito (Solo DxP)''',
'''Tasa Diaria''',
'''Fecha Ultimo Pago''',
'''fecha término de gracia por desembolso''',
'''DD vs DF''',
'''Fecha Venc de Ult Cuota Cancelada Contabilidad''',
'''DG vs BW''',
'''DG vs BW con FVUCC''',
'''DH vs CS''',
'''rendimiento devengado''',
'dias int suspenso',
'''intereses en suspenso''',
'''Cartera Neta''',
'''FEC_REPROG''',
'TIPO DE PRODUCTO TXT',
'Días de Diferido 1',  #PINTAR DE ROJO
'Ingresos Diferidos 1',#PINTAR DE ROJO
'Días de Diferido 2',  #PINTAR DE ROJO
'Ingresos Diferidos 2',#PINTAR DE ROJO
col_devengado, #PINTAR DE COLOR VERDE
col_suspenso, #PINTAR DE COLOR VERDE
'Nombre Negocio',
'Domicilio Negocio',
'Distrito Negocio',
'Dpto Negocio',
'Provincia Negocio',
'Funcionario Origuinador',
'Funcionario Actual',
'Fecha Desembolso TXT',
'Saldo Colocacion Sin Capitalizacion de Intereses TXT',
'Saldo Capital Real',
'Interes Capital Real',
'Fecha Termino \nPeriodo Gracia',
'Flag Termino Periodo Gracia',
'Monto Desembolso\nSoles Fijo',
'9/MDREPRP/ Modalidad de reprogramación']

anexo06_casi = df_resultado_2[columnas_casi_final]

#%% BUSCADOR DE COLUMNAS POR TEXTO
#BUSCADOR DE ALGUNA COLUMNA SOLO CAMBIANDO EL TEXTO
x = list(df_resultado_2.columns)
result = [column for column in x if 'alineam' in column]

# Imprimir los elementos encontrados
for column in result:
    print(column)

#%% ordenamiento con columnas 58/ 59/
#agregando las 2 nuevas columnas establecidas por la sbs
#Saldo Capital en Cuenta de Orden Programa IMPULSO MYPERU 58/	Rendimiento Devengado por Programa IMPULSO MYPERU 59/

#al añadir estas columnas debemos modificar las formulas en excel
anexo06_casi['Saldo Capital en Cuenta de Orden Programa IMPULSO MYPERU 58/'] = '' 
anexo06_casi['Rendimiento Devengado por Programa IMPULSO MYPERU 59/'] = ''

#ORDENAMIENTO DE LAS COLUMNAS
lista_columnas = list(anexo06_casi.columns)

lista_columnas.remove('Saldo Capital en Cuenta de Orden Programa IMPULSO MYPERU 58/')
lista_columnas.remove('Rendimiento Devengado por Programa IMPULSO MYPERU 59/')
lista_columnas.remove('TIPO DE PRODUCTO TXT')

ordenamiento_final = lista_columnas[0:65] + ['Saldo Capital en Cuenta de Orden Programa IMPULSO MYPERU 58/',
                                             'Rendimiento Devengado por Programa IMPULSO MYPERU 59/'] + \
                                             lista_columnas[65:] + ['TIPO DE PRODUCTO TXT']

anexo06_casi = anexo06_casi[ordenamiento_final]

#%% CRÉDITOS EN EL RESTO DEL SISTEMA FINANCIERO
# AÑADIENDO EL NRO DE CRÉDITOS QUE TIENE EL SOCIO EN EL RESTO DEL SECTOR FINANCIERO
# NOS VAMOS AL SABIO DE EXPERIAN,

# esta vaina la voy a eliminar y reemplazar en el futuro por el alineamiento externo (●'◡'●)

# import pandas as pd
# import os

# ubicacion = 'C:\\Users\\sanmiguel38\\Desktop\\TRANSICION  ANEXO 6\\2023 MAYO'

# nro_creditos = pd.read_excel(ubicacion + '\\' + 'dashboard de experian.xlsx', 
#                              dtype=({'NUMERO DOCUMENTO': str})) #leemos el archivo

# nro_creditos['ENTIDADES ACREEDORAS REGULADAS']    = nro_creditos['ENTIDADES ACREEDORAS REGULADAS'].fillna(0)
# nro_creditos['ENTIDADES ACREEDORAS NO REGULADAS'] = nro_creditos['ENTIDADES ACREEDORAS NO REGULADAS'].fillna(0)

# nro_creditos['total en sistema(no incluye San Miguel)'] = nro_creditos['ENTIDADES ACREEDORAS REGULADAS'] + \
#                                                           nro_creditos['ENTIDADES ACREEDORAS NO REGULADAS']

# nro_creditos['total en sistema(no incluye San Miguel)'] = nro_creditos['total en sistema(no incluye San Miguel)'].astype(int)
# nro_creditos['total en sistema(incluye San Miguel)'] = nro_creditos['total en sistema(no incluye San Miguel)'] + 1

#print(nro_creditos['TIPO DOCUMENTO'].unique().tolist())
# def tipo_documento_para_merge(nro_creditos):
#     if nro_creditos['TIPO DOCUMENTO'] == 'C/E':
#         return '2'
#     elif nro_creditos['TIPO DOCUMENTO'] == 'DNI':
#         return '1'
#     elif nro_creditos['TIPO DOCUMENTO'] == 'RUC':
#         return '6'
#     else:
#         return 'investigar'

# nro_creditos['TIPO DOC TXT'] = nro_creditos.apply(tipo_documento_para_merge, axis=1)

# # para revisar si ha salido un caso para investigar, (sería otro tipo de documento por codificar)
# print('nro filas por investigar: ', str((nro_creditos[nro_creditos['TIPO DOC TXT'] == 'investigar']).shape[0]))

# #cambiando el nombre
# nro_creditos = nro_creditos.rename(columns = {"NUMERO DOCUMENTO": "NUMERO DOCUMENTO de experian"})

# #%%% MERGE
# #MERGE CON EL ANEXO06
# merge_nro_creditos = nro_creditos[["NUMERO DOCUMENTO de experian", 
#                                    'TIPO DOC TXT', 
#                                    'total en sistema(no incluye San Miguel)',
#                                    'total en sistema(incluye San Miguel)'
#                                    ]]

# #agregamos 14 ceros a la derecha al archivo del merge y al del anx06
# def agregar_ceros(valor, longitud):
#     return str(valor).zfill(longitud)
# merge_nro_creditos['documento rellenado'] = merge_nro_creditos["NUMERO DOCUMENTO de experian"].apply(agregar_ceros, 
#                                                                                                      longitud=14)

# anexo06_casi['documento rellenado anx06'] = anexo06_casi['Número de Documento 10/']

# anexo06_casi['documento rellenado anx06'] = anexo06_casi['documento rellenado anx06'].astype(str).str.strip().str.zfill(14)

# anexo06_casi['Tipo de Documento 9/'] = anexo06_casi['Tipo de Documento 9/'].astype(str)
# anexo06_casi['Tipo de Documento 9/'] = anexo06_casi['Tipo de Documento 9/'].str.strip()

# #MERGE
# ya_casi = anexo06_casi.merge(merge_nro_creditos, 
#                              left_on  = ['documento rellenado anx06', 'Tipo de Documento 9/'], 
#                              right_on = ['documento rellenado',       'TIPO DOC TXT']
#                              ,how     = 'left')

# anexo06_casi[['documento rellenado anx06',
#               'Tipo de Documento 9/']]

# merge_nro_creditos[['documento rellenado', 
#                     'TIPO DOC TXT']]

#%%% sin datos
#le ponemos sin datos en donde no ha matcheado

# ya_casi['total en sistema(no incluye San Miguel)'] = ya_casi['total en sistema(no incluye San Miguel)'].fillna('sin datos')
# ya_casi['total en sistema(incluye San Miguel)'] = ya_casi['total en sistema(incluye San Miguel)'].fillna('sin datos')

#%% CAMBIANDO DE TIPO DE DATO
#arreglamos la columna del Tipo de Documento 9/

ya_casi = anexo06_casi.copy()

ya_casi['Tipo de Documento 9/'] = ya_casi['Tipo de Documento 9/'].astype(float).astype(int)

#%% FORMATO DE FECHAS (convirtiéndolas a números enteros)
def convertir_formato_fecha(fecha):
    if fecha != '--':
        fecha = pd.to_datetime(fecha, format='%d-%m-%Y')
        fecha = fecha.strftime('%Y%m%d')
    else:
        fecha = 'investigar'
    return fecha

ya_casi['Fecha de Nacimiento 3/'] = ya_casi['Fecha de Nacimiento 3/'].apply(convertir_formato_fecha)

ya_casi['Fecha de Desembolso 21/'] = ya_casi['Fecha de Desembolso 21/'].apply(convertir_formato_fecha)

ya_casi['Fecha de Vencimiento Origuinal del Credito 48/'] = ya_casi['Fecha de Vencimiento Origuinal del Credito 48/'].apply(convertir_formato_fecha)

ya_casi['Fecha de Vencimiento Actual del Crédito 49/'] = ya_casi['Fecha de Vencimiento Actual del Crédito 49/'].apply(convertir_formato_fecha)


print('debe salir cero en todos las modificaciones de las fechas')
print('--------------------------------------')
print('nulos en Fecha de nacimiento:')
print(ya_casi[ya_casi['Fecha de Nacimiento 3/'] == 'investigar'].shape[0])
print('--------------------------------------')
print('nulos en Fecha de desembolso:')
print(ya_casi[ya_casi['Fecha de Desembolso 21/'] == 'investigar'].shape[0])
print('--------------------------------------')
print('nulos en Fecha de vencimiento original:')
print(ya_casi[ya_casi['Fecha de Vencimiento Origuinal del Credito 48/'] == 'investigar'].shape[0])
print('--------------------------------------')
print('nulos en Fecha de vencimiento actual:')
print(ya_casi[ya_casi['Fecha de Vencimiento Actual del Crédito 49/'] == 'investigar'].shape[0])
print('--------------------------------------')

#%% lo convertimos a int (a ver qué pasa)

ya_casi['Fecha de Nacimiento 3/']   = ya_casi['Fecha de Nacimiento 3/'].astype(int)
ya_casi['Fecha de Desembolso 21/']  = ya_casi['Fecha de Desembolso 21/'].astype(int)
ya_casi['Fecha de Vencimiento Origuinal del Credito 48/']   = ya_casi['Fecha de Vencimiento Origuinal del Credito 48/'].astype(int)
ya_casi['Fecha de Vencimiento Actual del Crédito 49/']      = ya_casi['Fecha de Vencimiento Actual del Crédito 49/'].astype(int)

#%% redondeamos la columna de la tasa de interés anual a 4 decimales

ya_casi['Tasa de Interés Anual 23/'] = ya_casi['Tasa de Interés Anual 23/'].round(4)

#%% COLUMNA DE LA PLANILLA CONSOLIDADA (HISTÓRICO)
ya_casi['PLANILLA CONSOLIDADA'] = ya_casi['Nombre PlanillaTXT']
def planilla_consolidada(ya_casi):
    if ya_casi['PLANILLA CONSOLIDADA'] == 'PLANILLA LIQUIDADOS':
        return ya_casi['Planilla Anterior TXT']
    else:
        return ya_casi['PLANILLA CONSOLIDADA']

ya_casi['PLANILLA CONSOLIDADA'] = ya_casi.apply(planilla_consolidada, 
                                                axis=1)

#%% RECÁLCULO DE LA COLUMNA NRO_REGISTRO
#por si acasito, corregimos la columna del nro Registro 1/
print(ya_casi.shape[0])
ya_casi.drop_duplicates(subset = 'Nro Prestamo \nFincore', inplace=True)
print(ya_casi.shape[0])
print('si sale menos es porque hubo algún duplicado')
# Obtener la cantidad total de filas en el DataFrame
total_filas = len(ya_casi)

# Crear la nueva columna con la secuencia numérica
ya_casi['Registro 1/'] = [f'{i+1:06}' for i in range(total_filas)]

#%% rename del anexo06 
#
anexo06_casi = ya_casi.copy()

#%% REORDENAMIENTO UNA VEZ MÁS:
COL = [
'''Socios al menos con un cred < 100 soles
amarillo =  cred <100
rosado =  cred >= 100
 PROV.REQUERIDA A SER EVALUADA.''',
'''Registro 1/''',
'''Apellidos y Nombres / Razón Social 2/''',
'''Fecha de Nacimiento 3/''',
'''Género 4/''',
'''Estado Civil 5/''',
'''Sigla de la Empresa 6/''',
'''Código Socio 7/''',
'''Partida Registral 8/''',
'''Tipo de Documento 9/''',
'''Número de Documento 10/''',
'''Tipo de Persona 11/''',
'''Domicilio 12/''',
'''Relación Laboral con la Cooperativa 13/''',
'''Tasa de Provisión SA''',
'''Tasa de Provisión''',
'''Clasificación del Deudor 14/''',
'''alineamiento 15 anterior''',
'''Clasificación del Deudor con Alineamiento 15/''',
'''Código de Agencia 16/''',
'''Moneda del crédito 17/''',
'''Numero de Crédito 18/''',
'''Tipo de Crédito 19/''',
'''Sub Tipo de Crédito 20/''',
'''Fecha de Desembolso 21/''',
'''Monto de Desembolso Origuinal TXT''',
'''Monto de Desembolso 22/''',
'''Tasa de Interés Anual 23/''',
'''Saldo de colocaciones (créditos directos) 24/''',
'''Cuenta Contable 25/''',
'''Capital Vigente 26/''',
'''Capital Reestrucutado 27/''',
'''Capital Refinanciado 28/''',
'''Capital Vencido 29/''',
'''Capital en Cobranza Judicial 30/''',
'''Cartera Atrasada''',
'''Capital Contingente 31/''',
'''Cuenta Contable Capital Contingente 32/''',
'''Dias de Mora 33/''',
'''Saldos de Garantías Preferidas 34/''',
'''Saldo de Garantías Autoliquidables 35/''',
'''Provisiones Requeridas 36/ SA''',
'''Provisiones Requeridas 36/''',
'''Provisiones Constituidas 37/''',
'''Saldos de Créditos Castigados 38/''',
'''Cuenta Contable Crédito Castigado 39/''',
'''Rendimiento
Devengado 40/''',
'''Intereses en Suspenso 41/''',
'''Ingresos Diferidos 42/''',
'''Tipo de Producto 43/ original''',
'''Tipo de Producto 43/''',
'''Número de Cuotas Programadas 44/''',
'''Número de Cuotas Pagadas 45/''',
'''Periodicidad de la cuota 46/''',
'''Periodo de Gracia 47/''',
'''Fecha de Vencimiento Origuinal del Credito 48/''',
'''Fecha de Vencimiento Actual del Crédito 49/''',
'''Saldo de Créditos con Sustitución de Contraparte Crediticia 50/''',
'''Saldo de Créditos que no cuentan con cobertura 51/''',
'''Saldo Capital de Créditos Reprogramados 52/''',
'''Saldo Capital en Cuenta de Orden por efecto del Covid 53/''',
'''Subcuenta de orden 
54/
''',
'''Rendimiento Devengado por efecto del COVID 19 55/''',
'''Saldo de Garantías con Sustitución de Contraparte 56/''',
'''Saldo Capital de Créditos Reprogramados por efecto del COVID 19 57/''',
'''Saldo Capital en Cuenta de Orden Programa IMPULSO MYPERU 58/''',
'''Rendimiento Devengado por Programa IMPULSO MYPERU 59/''',
'''FEC_ULT_REPROG''',
'''PLAZO_REPR''',
'''TIPO_REPRO''',
'''PLAZO REPRO ACUMULADO''',
'''NRO CUOTAS REPROG CANCELADAS''',
'''NRO REPROG''',
'''fecha desemb (v)''',
'''fecha término de gracia por desembolso ["v" + dias gracia (av)]''',
'''periodo de gracia por Reprog inicio''',
'''periodo de gracia por Reprog Término''',
'''Fecha Venc de Ult Cuota Cancelada
(NVO)''',
'''Categoria TXT''',
'''Saldo Colocacion Con Capitalizacion de Intereses TXT''',
'''Fecha Castigo TXT''',
'''Dscto Enviado TXT''',
'''Desc Pagado TXT''',
'''Fecha Vencimiento 
Origuinal TXT''',
'''Fecha Vencimiento Actual TXT''',
'''Fecha Creacion Reprogramacion Nacimiento TXT''',
'''Fecha Creacion Reprogramacion Corte TXT''',
'''Nro Dias Gracia Corte RPG TXT''',
'''Nro Cuotas Canc Post Regro''',
'''Nro Prestamos X Deudor TXT''',
'''Fecha Ultimo 
Pago TXT''',
'''Tipo Reprogramacion TXT''',
'''Fecha Primer Cuota Gracia Nacimiento RPG TXT''',
'''Primer Fecha Cuota Gracia Corte RPG TXT''',
'''Nro Reprogramaciones TXT''',
'''Origen
 Prestamo''',
'''Nro Prestamo 
Fincore''',
'''Por Cobrar Mes Actual TXT''',
'''Reprogramado TXT''',
'''Funcionaria TXT''',
'''Nombre Empresa TXT''',
'''Nombre PlanillaTXT''',
'''Planilla Anterior TXT''',
'''PLANILLA CONSOLIDADA''',
'''Cod Usuario Pri Aprob''',
'''Cod Usuario Seg Aprob''',
'''Profesion''',
'''Ocupacion''',
'''Actividad Economica''',
'''Fecha Venc Ult Cuota Cancelada''',
'''Departamento''',
'''Provincia''',
'''Distrito''',
'''Tipo Credito TXT''',
'''TEA TXT''',
'''Refinanciado TXT''',
'''Situacion TXT''',
'''Fecha Situacion TXT''',
'''Abogado TXT''',
'''Fecha Asignacion Abogado TXT''',
'''Nro Expediente TXT''',
'''Fecha Expediente TXT''',
'''Tasa Clasificacion  Deudor con Alineamiento TXT''',
'''Monto de Garantías Preferidas''',
'''Monto de Garantías Autoliquidables''',
'''Importe Vencido > 60d
(Solo DxP)''',
'''Dias vencido (Solo DxP)''',
'''Porción Vencido''',
'''Situación del Credito (Solo DxP)''',
'''Tasa Diaria''',
'''Fecha Ultimo Pago''',
'''fecha término de gracia por desembolso''',
'''Fecha Venc de Ult Cuota Cancelada Contabilidad''',
'''dias int suspenso''',
'''Cartera Neta''',
'''FEC_REPROG''',
# '''Días de Diferido 1''',
# '''Ingresos Diferidos 1''',
# '''Días de Diferido 2''',
# '''Ingresos Diferidos 2''',
col_devengado,
col_suspenso,
'''Nombre Negocio''',
'''Domicilio Negocio''',
'''Distrito Negocio''',
'''Dpto Negocio''',
'''Provincia Negocio''',
'''Funcionario Origuinador''',
'''Funcionario Actual''',
'''Fecha Desembolso TXT''',
'Saldo Colocacion Sin Capitalizacion de Intereses TXT',
'Saldo Capital Real',
'Interes Capital Real',
'Fecha Termino \nPeriodo Gracia',
'Flag Termino Periodo Gracia',
'Monto Desembolso\nSoles Fijo',
'''9/MDREPRP/ Modalidad de reprogramación''',
'''TIPO DE PRODUCTO TXT'''
]

anexo06_casi = anexo06_casi[COL]

#%%
#validación de que no haya intereses en suspenso si el crédito está castigado
suspenso_castigados = anexo06_casi[(anexo06_casi['Saldos de Créditos Castigados 38/'] > 0) & \
                                   (anexo06_casi['Intereses en Suspenso 41/'] > 0)]
if suspenso_castigados.shape[0] > 0:
    print('hay que quitar intereses en suspenso de los créditos castigados')
else:
    print('todo bien')

anexo06_casi.loc[anexo06_casi['Saldos de Créditos Castigados 38/'] > 0, 'Intereses en Suspenso 41/'] = 0

if suspenso_castigados.shape[0] > 0:
    print('hay que quitar intereses en suspenso de los créditos castigados')
else:
    print('todo bien')
    
#%% AJUSTE PUNTUAL DE VALORES, ANTES DE MANDARLO AL SUCAVE
anexo06_casi.loc[anexo06_casi['Nro Prestamo \nFincore'] == '00016472', 'Sub Tipo de Crédito 20/'] = '99'
anexo06_casi.loc[anexo06_casi['Nro Prestamo \nFincore'] == '00057366', 'Sub Tipo de Crédito 20/'] = '99'
anexo06_casi.loc[anexo06_casi['Nro Prestamo \nFincore'] == '00014355', 'Sub Tipo de Crédito 20/'] = '99'
anexo06_casi.loc[anexo06_casi['Nro Prestamo \nFincore'] == '00019911', 'Sub Tipo de Crédito 20/'] = '99'
anexo06_casi.loc[anexo06_casi['Nro Prestamo \nFincore'] == '00020153', 'Sub Tipo de Crédito 20/'] = '99'
anexo06_casi.loc[anexo06_casi['Nro Prestamo \nFincore'] == '00053525', 'Sub Tipo de Crédito 20/'] = '99'

#%% PARSEO DE LA FECHA DE LA COLUMNA 'Fecha Castigo TXT'
anexo06_casi['Fecha Castigo TXT'] = anexo06_casi['Fecha Castigo TXT'].str.strip()
#formatos en los cuales se tratará de convertir a DateTime
formatos = ['%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y',
            '%Y%m%d', '%Y-%m-%d', 
            '%Y-%m-%d %H:%M:%S', 
            '%Y/%m/%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S PM',
            '%Y-%m-%d %H:%M:%S AM',
            '%Y/%m/%d %H:%M:%S PM',
            '%Y/%m/%d %H:%M:%S AM']

# Función de análisis de fechas
def parse_dates(date_str):
    '''
    Parameters
    ----------
    date_str : Es el formato que va a analizar dentro de la columna del DataFrame.

    Returns
    -------
    Si el date_str tiene una estructura compatible con los formatos preestablecidos
    para su iteración, la convertirá en un DateTime

    '''
    for formato in formatos:
        try:
            return pd.to_datetime(date_str, format=formato)
        except ValueError:
            pass
    return pd.NaT

anexo06_casi['Fecha Castigo TXT'] = anexo06_casi['Fecha Castigo TXT'].apply(parse_dates)


#%% CREACIÓN DEL EXCEL

'CREACIÓN DEL EXCEL'
nombre = "Rpt_DeudoresSBS Anexo06 - " + fech_corte_txt + " - campos ampliados 02.xlsx"
try:
    ruta = nombre
    os.remove(ruta)
except FileNotFoundError:
    pass

anexo06_casi.to_excel(nombre,
                      sheet_name = fech_corte_txt,
                      index      = False)

#%% UBICACIÓN DE LOS ARCHIVOS
# POR SI NO SABEMOS DÓNDE ESTÁN LOS ARCHIVOS
# Obtener la ubicación actual
ubicacion_actual = os.getcwd()

# Imprimir la ubicación actual
print("La ubicación actual es: " + ubicacion_actual)

#%% PARTE 2
#######################################################
#██████╗  █████╗ ██████╗ ████████╗███████╗    ██████╗ #
#██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝██╔════╝    ╚════██╗#
#██████╔╝███████║██████╔╝   ██║   █████╗       █████╔╝#
#██╔═══╝ ██╔══██║██╔══██╗   ██║   ██╔══╝      ██╔═══╝ #
#██║     ██║  ██║██║  ██║   ██║   ███████╗    ███████╗#
#╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝    ╚══════╝#
#######################################################
'UNA VEZ QUE NOS PASEN EL ANEXO 06 CON LOS INTERESES DIFERIDOS:'

#%% PARÁMETROS INCIALES

# mes actual #####################################################
fecha_corte = 'Mayo 2024'  # se pone el corte actual
##################################################################

# mes anterior al que estamos trabajando actualmente
# formato de fecha para extraer datos desde SQL
##################################################################
fechacorte_mes_pasado = "20240430" # se pone la del corte anterior para obtener información de ellos
##################################################################

# Anexo 06 enviado por contabilidad (incluye ingresos diferidos)
##################################################################
anx06_contabilidad = 'Rpt_DeudoresSBS Anexo06 - Mayo 2024 - campos ampliados 02.xlsx'
##################################################################

# DIRECTORIO DE TRABAJO ##########################################
directorio_final = 'C:\\Users\\sanmiguel38\\Desktop\\TRANSICION  ANEXO 6\\2024\\2024 mayo\\fase 2'
##################################################################

lista_100_provisionales = ['00087481', '00100112', '00078588', '00096775',
                           '00093507', '00098725', '00094791', '00103282',
                           '00088637', '00080108', '00096417', '00097332',
                           '00098973', '00098454', '00082582', '00101711',
                           '00091367', '00099619', '00084311', '00098112',
                           '00102941', '00085287', '00073062', '00086998',
                           '00085544', '00088082', '00090487', '00097094',
                           '00102185', '00096808', '00099864', '00088644',
                           '00102177', '00085358', '00094227', '00102322',
                           '00084146', '00090588', '00099821', '00089733',
                           '00088497', '00101038', '00100125', '00101012',
                           '00102430', '00092802', '00097977', '00025678',
                           '00086775', '00009592', '00091004', '00091310',
                           '00092930', '00097354', '00101033', '00085161',
                           '00092292', '00091373', '00092595', '00099885',
                           '00082054', '00101699', '00086604', '00081400',
                           '00092060', '00095283', '00099348', '00098095',
                           '00095355', '00072746', '00084530', '00093694',
                           '00100895', '00095425', '00097641', '00067015',
                           '00092751', '00091010', '00085926', '00090392',
                           '00102370', '00088722', '00081477', '00103274',
                           '00103362', '00099863', '00082785', '00074648',
                           '00089889', '00094732', '00081776', '00101647',
                           '00093146', '00089808', '00100907', '00088965',
                           '00090835', '00096505', '00078869', '00095031',
                           '00099342', '00090816', '00099221', '00097237',
                           '00101581', '00084039', '00094083', '00072567',
                           '00087753', '00085628', '00087968', '00097960',
                           '00072999', '00099858', '00075441', '00098849',
                           '00100986', '00101057', '00093332', '00100957',
                           '00101875', '00090798', '00090764', '00078831',
                           '00088290', '00102535', '00081777', '00098957',
                           '00084306', '00099407', '00089822', '00090170',
                           '00102369', '00092291', '00092446', '00085151',
                           '00083856', '00081296', '00098963', '00088014',
                           '00074571', '00101726', '00085672', '00088666',
                           '00083585', '00099717',
                           
                           # provisiones al 100% para castigo en MAYO
                           '00082078', '00078440', '00081429', '00079212', '00092043', '00073380', '00074246', '00071054', '00077091', '00073431', '00078902', '00072027', '00078559', '00074103', '00078229', '00075409',
                           '00077607', '00094497', '00087174', '00077485', '00089272', '00090517', '00075715', '00077129', '00081857', '00076840', '00079925', '00083347', '00081365', '00080124', '00079613', '00080950',
                           '00095696', '00088276', '00094346', '00080889', '00096277', '00080658', '00071853', '00072376', '00074124', '00078609', '00078473', '00085465', '00086651', '00078561', '00080975', '00078819',
                           '00077936', '00089109', '00091412', '00095491', '00095778', '00085018', '00069335', '00080480', '00082492', '00078494', '00080992', '00084410', '00081796', '00081527', '00087444', '00078853',
                           '00083395', '00080864', '00066441', '00094906', '00075314', '00083836', '00085137', '00095724', '00086792', '00090583', '00091546', '00089429', '00093809', '00086392', '00078895', '00090911',
                           '00083020', '00087146', '00096886', '00088146', '00078877', '00093855', '00085401', '00087110', '00092119', '00082557', '00082689', '00088604', '00081763', '00088454', '00089027', '00088384',
                           '00085116', '00088942', '00079971', '00079594', '00085802', '00077046', '00093304', '00085661', '00085022', '00087483', '00092650', '00095102', '00095221', '00076505', '00097022', '00094614',
                           '00086532', '00086603', '00083098', '00085468', '00088767', '00092163', '00096217', '00078907', '00073091', '00093675', '00084115', '00076639', '00082660', '00084219', '00087502', '00094289',
                           '00094299', '00079577', '00087262', '00086260', '00090552', '00091692', '00095489', '00092317', '00086581', '00087227', '00091007', '00085300', '00079764', '00081828', '00093635', '00089737',
                           '00084845', '00082154', '00093599', '00074099', '00072824', '00075631', '00081434', '00077810', '00081846', '00087060', '00083944', '00087689', '00086815', '00086537', '00084520', '00082656',
                           '00093414', '00076472', '00084560', '00087373', '00082538', '00087745', '00074323', '00079371', '00082312', '00080702', '00081253', '00094280', '00089990', '00089483', '00086376', '00081947',
                           '00084670', '00096389', '00088063', '00074409', '00089677', '00088333', '00082558', '00085488', '00089503', '00079635', '00091610', '00082315', '00090606', '00095792', '00086941', '00074163',
                           '00085762', '00080554', '00084113', '00087683', '00081880', '00093953', '00084279', '00085696', '00089407', '00093546', '00082977', '00088569', '00091655', '00074277', '00080591', '00081368',
                           '00084088', '00087879', '00086408', '00083024', '00090004', '00085769', '00082485', '00083089', '00092176', '00073725', '00089810', '00082855', '00085113', '00087618', '00082542', '00086568',
                           '00079120', '00083260', '00091278', '00086067', '00078800', '00085446', '00094019', '00088924', '00084284', '00090546', '00084107', '00087933', '00082271', '00091056', '00082549', '00078839',
                           '00092676', '00086863', '00086270', '00081580', '00094806', '00078524', '00078829', '00083725', '00080773', '00094841', '00091749', '00093801', '00092192', '00085781', '00073135', '00094131',
                           '00091614', '00088695', '00085388', '00084165', '00086555', '00094524', '00083640', '00079879', '00092086', '00085897', '00077864', '00095191', '00085700', '00089894', '00082022', '00081340',
                           '00081657', '00091859', '00096372', '00092589', '00083316', '00075512', '00087562', '00087556', '00084539', '00079362', '00091629', '00092005', '00080731', '00085428', '00078634', '00086288',
                           '00080273', '00087791', '00090657', '00077380', '00091177', '00091164', '00088916', '00082434', '00094029', '00081727', '00088612', '00093672', '00074303', '00079482', '00087192', '00084089',
                           '00074237', '00095554', '00090620', '00093035', '00080660', '00086013', '00084416', '00061137', '00073990', '00082951', '00091922', '00096695', '00073904', '00094271', '00079283', '00090712',
                           '00090757', '00075658', '00095187', '00080895', '00094082', '00096702', '00093808', '00079279', '00095693', '00080244', '00078316', '00080851', '00088140', '00076049', '00069287', '00075203',
                           '00090519', '00070089', '00082672', '00081737', '00089157', '00073108', '00088993', '00084024', '00071393', '00083721', '00084865', '00095842', '00080605', '00089220', '00084371', '00084751',
                           '00094657', '00076608', '00087733', '00082794', '00087164', '00087688', '00087257', '00085414', '00084198', '00089848', '00088754', '00079677', '00090473', '00084758', '00094258', '00082165',
                           '00087792', '00079375', '00090822', '00084277', '00084249', '00095277', '00083002', '00072565', '00091863', '00080040', '00088397', '00096913', '00074570', '00092017', '00080659', '00086515',
                           '00084098', '00093944', '00088015', '00084364', '00095147', '00078824', '00088322', '00081419', '00093453', '00086085', '00089005', '00087513', '00087574', '00086338', '00083550', '00088170',
                           '00081115', '00070986', '00079659', '00083383', '00091129', '00090793', '00095557', '00085988', '00070931', '00090393', '00093170', '00082667', '00079202', '00088844', '00089290', '00073932',
                           '00084587', '00085028', '00084605', '00088590', '00089958', '00081287', '00090496', '00081003', '00080490', '00088385', '00079109', '00082899', '00069026', '00083455', '00077974', '00089202',
                           '00095253', '00088898', '00091508', '00068315', '00077433', '00093676', '00089056', '00077369', '00086860', '00090533', '00090247', '00079992', '00088947', '00094516', '00086431', '00070534',
                           '00094363', '00082875', '00096778', '00084841', '00087983', '00087072', '00085406', '00073309', '00082993', '00080559', '00092089', '00091175', '00076621', '00092348', '00085927', '00096223',
                           '00082251', '00088864', '00088366', '00086851', '00083005', '00088238', '00090295', '00091804', '00084091', '00077122', '00070130', '00083111', '00084272', '00090497', '00074234', '00083852',
                           '00086943', '00084327', '00081738', '00096724', '00085015', '00088330', '00085023', '00086363', '00090800', '00090163', '00091380', '00082000', '00090303', '00093732', '00079954', '00088412',
                           '00077434', '00088142', '00086802', '00096082', '00073619', '00086382', '00092265', '00087245', '00087224', '00094834', '00088222', '00093671', '00083549', '00074449', '00090627', '00094026',
                           '00079557', '00083847', '00080791', '00085712', '00085918', '00090780', '00090646', '00092023', '00092762', '00079956', '00073041', '00088100', '00086388', '00088711', '00086989', '00082830',
                           '00089887', '00089171', '00085949', '00085224', '00079505', '00084129', '00080823', '00091244', '00094199', '00097107', '00092347', '00086635', '00092077', '00077545', '00081149', '00097914',
                           '00091737', '00088074', '00090193', '00089606', '00091123', '00095864', '00081493', '00086432', '00092168', '00075227', '00090922', '00082933', '00097229', '00097200', '00086199', '00091337',
                           '00087973', '00092397', '00092737', '00085532', '00092377', '00092303', '00082409', '00087620', '00095849', '00090594', '00092408', '00095279', '00086022', '00089173', '00099190', '00094094',
                           '00073243', '00086226', '00086199', '00089493', '00098226', '00093078', '00088362', '00089495', '00085200', '00089450', '00089235', '00095847', '00097282', '00092674', '00089465', '00094482',
                           '00097262', '00093120', '00096704', '00089457', '00093117', '00097571', '00081804', '00081102', '00089013', '00090652', '00087920', '00090461', '00086386', '00084450', '00080631', '00066655',
                           '00096769', '00087113', '00094595', '00083365', '00075238', '00084549', '00084323', '00092655', '00087638', '00095327', '00092933', '00090581', '00092977', '00092994', '00086349', '00080523',
                           '00086955', '00091676', '00092649', '00086988', '00088202', '00090005', '00093040', '00088323', '00081299', '00084283', '00080927', '00076009', '00084281', '00082296', '00082052', '00091562',
                           '00091631', '00090039', '00088473', '00076399', '00079639', '00085040', '00090220', '00085808', '00087435', '00090224', '00082874', '00082668', '00080522', '00082758', '00082493', '00088328',
                           '00088379', '00088693', '00089657', '00079848', '00079772', '00087988', '00086422', '00089185', '00080748', '00083980', '00085441', '00086868', '00083582', '00081650', '00086185', '00086026',
                           '00087676', '00084335', '00084561', '00086310', '00077701', '00080907', '00088505', '00072298', '00087149', '00085592', '00086835', '00081817'
                           ]

#%% importación de módulos
import os
import pandas as pd
#%% Créditos de la lista de provisiones al 100% que no están castigados

# ubicados = df_diferidos[df_diferidos['Nro Prestamo \nFincore'].isin(lista_100_provisionales)]
# ubicados = ubicados[ubicados['Saldo de colocaciones (créditos directos) 24/'] > 0]
# print(list(ubicados['Nro Prestamo \nFincore']))

#%% IMPORTACIÓN DE ARCHIVOS
#leyendo el excel que nos envía CONTABILIDAD
os.chdir(directorio_final)

df_diferidos = pd.read_excel(anx06_contabilidad,
                 dtype = {'Registro 1/'               : object, 
                          'Fecha de Nacimiento 3/'    : object,
                          'Código Socio 7/'           : object, 
                          'Número de Documento 10/'   : object,
                          'Relación Laboral con la Cooperativa 13/'       : object, 
                          'Código de Agencia 16/'     : object,
                          'Moneda del crédito 17/'    : object, 
                          'Numero de Crédito 18/'     : object,
                          'Tipo de Crédito 19/'       : object,
                          'Sub Tipo de Crédito 20/'   : object,
                          'Fecha de Desembolso 21/'   : object,
                          'Cuenta Contable 25/'       : object,
                          'Tipo de Producto 43/'      : object,
                          'Fecha de Vencimiento Origuinal del Credito 48/': object,
                          'Fecha de Vencimiento Actual del Crédito 49/'   : object,
                          'Nro Prestamo \nFincore'    : str},
                         skiprows = 2
                             )

df_diferidos.dropna(subset = [# 'Apellidos y Nombres / Razón Social 2/', 
                              'Fecha de Nacimiento 3/',
                              'Número de Documento 10/',
                              'Domicilio 12/',
                              'Numero de Crédito 18/'], 
                    inplace = True, 
                    how     = 'all')

#%% #asignamos los diferidos
# df_diferidos['Ingresos Diferidos 2']    = df_diferidos['Ingresos Diferidos 2'].round(2)
# df_diferidos['Ingresos Diferidos 42/']  = df_diferidos['Ingresos Diferidos 2']
df_diferidos['Ingresos Diferidos 42/'] = df_diferidos['Ingresos Diferidos 42/'].round(2)
print('no debe salir cero: ' + str(df_diferidos['Ingresos Diferidos 42/'].sum()))

#%% CARTERA NETA FINAL

'AHORA QUE YA TENEMOS LOS INGRESOS DIFERIDOS'
#calculamos la cartera neta
def cartera_neta(df_diferidos):
    return df_diferidos['Saldo de colocaciones (créditos directos) 24/'] - \
        df_diferidos['Ingresos Diferidos 42/']
        
df_diferidos['Cartera Neta'] = df_diferidos.apply(cartera_neta, 
                                                  axis=1)
df_diferidos['Cartera Neta'] = df_diferidos['Cartera Neta'].round(2)
df_diferidos['Cartera Neta'].sum()

#%% PROVISIONES REQUERIDAS SIN ALINEAMIENTO
#cálculo de provisiones requeridas 36 SA

df_diferidos['Provisiones Requeridas 36/ SA'] = df_diferidos['Cartera Neta'] * \
                                                df_diferidos['Tasa de Provisión SA']

df_diferidos['Provisiones Requeridas 36/ SA'] = df_diferidos['Provisiones Requeridas 36/ SA'].round(2)
df_diferidos['Provisiones Requeridas 36/ SA'].sum()
                                                
#%% PROVISIONES REQUERIDAS
#cálculo de provisiones requeridas 36

df_diferidos['Provisiones Requeridas 36/'] = df_diferidos['Cartera Neta'] * \
                                             df_diferidos['Tasa de Provisión']
                                             
df_diferidos['Provisiones Requeridas 36/'] = df_diferidos['Provisiones Requeridas 36/'].round(2)
print(df_diferidos['Provisiones Requeridas 36/'].sum())
print(df_diferidos['Provisiones Requeridas 36/'].sum())

#%% Saldo de Créditos que no cuentan con cobertura 51/
# Saldo de Créditos que no cuentan con cobertura 51/
df_diferidos['Saldo de Créditos que no cuentan con cobertura 51/'] = df_diferidos['Cartera Neta'] - \
                                                                    (df_diferidos['Saldos de Garantías Preferidas 34/'] + \
                                                                     df_diferidos['Saldo de Garantías Autoliquidables 35/'])
                                                                        
df_diferidos['Saldo de Créditos que no cuentan con cobertura 51/'] = df_diferidos['Saldo de Créditos que no cuentan con cobertura 51/'].round(2)                                                                

#%% en este caso, añadir los créditos que mandó Harris
# POSIBLEMENTE SE VA A ELIMINAR EN EL FUTURO
'''
dxp_castigados = pd.read_excel('data para castigo junio 2023_vhf.xlsx',
                               dtype = {'Nro Prestamo \nFincore' : object}, 
                               skiprows = 2,
                               sheet_name = 'BD - Para Castigo')

dxp_castigados = list(dxp_castigados['Nro Prestamo \nFincore'])
'''

#%% EXTRACCIÓN DE DATOS DEL MES PASADO
#comparando provisiones constituidas contra el del mes pasado
'AQUI HAY QUE CAMBIAR LA FECHA PARA QUE VAYA DEL MES PASADO al que estamos elaborando'
import pyodbc

query = f'''

DECLARE @fechacorte as DATETIME
SET @fechacorte = '{fechacorte_mes_pasado}'

SELECT 
    SUM(ProvisionesConstituidas37) as 'ProvisionesConstituidas37' 
FROM 
    anexos_riesgos2..Anx06_preliminar
where FechaCorte1 = @fechacorte

'''

conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')
provisiones_mes_pasado = pd.read_sql_query(query, conn)

mes_pasado = provisiones_mes_pasado.loc[0, 'ProvisionesConstituidas37']

df_diferidos['Provisiones Requeridas 36/'].sum()

#%%
# =============================================================================
# CÁLCULO DE PROVISIONES CONSTITUIDAS
# =============================================================================

# ===========================
tasa_provision = 0.575 #0.553 #0.6048 #0.5951 #0.60 #0.575 #0.607 #0.5615 #0.60155
# =========================== aumentar 0.0040 al total, todos los meses

# cálculo de las provisiones constituidas 37/
df_diferidos['Nro Prestamo \nFincore'] = df_diferidos['Nro Prestamo \nFincore'].str.strip() #quitando espacios por si acaso
df_diferidos['Moneda del crédito 17/'] = df_diferidos['Moneda del crédito 17/'].str.strip()

# cambio de tipo de dato
df_diferidos['Tipo de Producto 43/'] = df_diferidos['Tipo de Producto 43/'].astype(int)

def prov_cons_37_FINAL(df_diferidos):
    if (df_diferidos['Nro Prestamo \nFincore'] in 
                lista_100_provisionales):
        return df_diferidos['Saldo de colocaciones (créditos directos) 24/'] * 1
    else:
        return df_diferidos['Provisiones Requeridas 36/'] * tasa_provision
    # elif df_diferidos['Moneda del crédito 17/'] == '01':
    #     return  df_diferidos['Provisiones Requeridas 36/'] * tasa_provision
    # elif df_diferidos['Moneda del crédito 17/'] == '02':
    #     return  df_diferidos['Provisiones Requeridas 36/'] * 0.52
    
df_diferidos['Provisiones Constituidas 37/'] = df_diferidos.apply(prov_cons_37_FINAL, axis = 1)

df_diferidos['Provisiones Constituidas 37/'] = df_diferidos['Provisiones Constituidas 37/'].round(2)

print('Provisiones Constituidas:')
print(df_diferidos['Provisiones Constituidas 37/'].sum().round(2))
print('')
print('Diferencia respecto al mes pasado:')
print(round((df_diferidos['Provisiones Constituidas 37/'].sum().round(2) - mes_pasado),2))

#%%
print('Morosidad:')
cartera  = df_diferidos['Saldo de colocaciones (créditos directos) 24/'].sum()
vencido  = df_diferidos['Capital Vencido 29/'].sum()
judicial = df_diferidos['Capital en Cobranza Judicial 30/'].sum()
print((vencido + judicial )/cartera)

#%%% VERIFICACIÓN DE RESULTADOS 1
'VERIFICACIÓN'
#LAS PROVISIONES CONSTITUIDAS DEL MES, DEBEN SER (EN MONTO) MAYORES A LA DEL MES PASADO
#Y LAS PROVISIONES CONSTITUIDAS DIVIDIDAS ENTRE LAS PROVISIONES REQUERIDAS DEBE SER > 60%

suma_requeridas = df_diferidos['Provisiones Requeridas 36/'].sum() #en base al 15(con alineamiento), (SA significa sin alineamiento)
suma_constituidas = df_diferidos['Provisiones Constituidas 37/'].sum()

div = suma_constituidas/suma_requeridas
print('EL PORCENTAJE de constituidas / requeridas es: ',"{:.2f}%".format(div*100))

suma_atrasada = df_diferidos['Cartera Atrasada'].sum()
div2 = suma_constituidas/suma_atrasada

print('COBERTURA DE PROVISIÓN : consti / atrasa: ',"{:.2f}%".format(div2*100))

print('variación de constituídas con el mes pasado', (suma_constituidas - float(mes_pasado)).round(2)) #aquí hacer una query para extraer los datos

print('provisiones constituidas: ' + str(suma_constituidas))

print('')
print('tasa de provisión general: ' ,"{:.2f}%".format(tasa_provision*100)) 

# %%
# SELECT
# 	SUM(ProvisionesRequeridas36)   AS 'REQUERIDAS',
# 	SUM(ProvisionesConstituidas37) AS 'CONSTITUIDAS',
# 	sum(ProvisionesConstituidas37) / sum(CapitalVencido29 + CapitalenCobranzaJudicial30),
# 	sum(ProvisionesConstituidas37) / sum(ProvisionesRequeridas36)
# FROM anexos_riesgos3..ANX06
# WHERE FechaCorte1 = '20240430'

#%%% VERIFICACIÓN DE RESULTADOS 2
print('saldo de provisiones constituidas')

if mes_pasado < suma_constituidas:
    print('todo bien')
    print('mes actual: ', int(suma_constituidas))
    print('mes pasado: ', int(mes_pasado))
else:
    print('todo mal')
    print('mes actual: ', int(suma_constituidas))
    print('mes pasado: ', int(mes_pasado))

diferencia_cons = suma_constituidas - mes_pasado
print('diferencia:  '+ str(round(diferencia_cons,2)))

calculo_que_pidio_enrique = suma_constituidas / (df_diferidos['Capital Vencido 29/'].sum() + df_diferidos['Capital en Cobranza Judicial 30/'].sum())
print("{:.2f}%".format(calculo_que_pidio_enrique*100))

#%% redondeamos provisiones consitutidas y provisiones requeridas

df_diferidos['Provisiones Constituidas 37/'] = df_diferidos['Provisiones Constituidas 37/'].round(2)
df_diferidos['Provisiones Requeridas 36/'] = df_diferidos['Provisiones Requeridas 36/'].round(2)

#%% DATAFRAME FINAL, CON LOS DATOS QUE VAMOS A MANDAR
#lo otro que podríamos hacer es crear un dataframe solo con las columnas que vamos a necesitar
df_diferidos_ampliado = df_diferidos.copy()
df_diferidos_columnas = df_diferidos[['Nro Prestamo \nFincore',
                                      'Cartera Neta', 
                                      'Ingresos Diferidos 42/', 
                                      'Provisiones Requeridas 36/ SA', 
                                      'Provisiones Requeridas 36/', 
                                      'Provisiones Constituidas 37/',
                                      'Saldo de Créditos que no cuentan con cobertura 51/']]

#%% INTEGRANDO MONTO DE DESEMBOLSO NETO
#%% CONECCIÓN A SQL PARA MONTO NETO
datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')

server    =  datos['DATOS'][0]
username  =  datos['DATOS'][2]
password  =  datos['DATOS'][3]

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'
conn = pyodbc.connect(conn_str)

query = '''
SELECT
	s.codigosocio,
	iif(s.CodTipoPersona =1, CONCAT(S.ApellidoPaterno,' ',S.ApellidoMaterno, ' ', S.Nombres),s.razonsocial) AS 'Socio',
	iif(s.CodTipoPersona =1, s.nroDocIdentidad, s.nroruc) AS 'Doc_Identidad',
	RIGHT(CONCAT('0000000',p.numero),8) as 'pagare_fincore',
	p.fechadesembolso,
	p.montosolicitado as 'Otorgado',
	DESCUENTO.valor as 'retención',
	p.montosolicitado - DESCUENTO.valor as 'MONTO NETO'

FROM prestamo AS p

INNER JOIN socio AS s             ON s.codsocio = p.codsocio
LEFT JOIN sociocontacto AS sc     ON sc.codsocio = s.codsocio
LEFT JOIN planilla AS pla         ON p.codplanilla = pla.codplanilla
INNER JOIN grupocab AS pro        ON pro.codgrupocab = p.codgrupocab
INNER JOIN distrito AS d          ON d.coddistrito = sc.coddistrito
INNER JOIN provincia AS pv        ON pv.codprovincia = d.codprovincia
INNER JOIN departamento AS dp     ON dp.coddepartamento = pv.coddepartamento
INNER JOIN tablaMaestraDet AS tm  ON tm.codtabladet = p.CodEstado
LEFT JOIN grupocab AS gpo         ON gpo.codgrupocab = pla.codgrupocab
LEFT JOIN tablaMaestraDet AS tm2  ON tm2.codtabladet = s.codestadocivil
LEFT JOIN tablaMaestraDet AS tm3  ON tm3.codtabladet = p.CodSituacion
--INNER JOIN tablaMaestraDet as tm3 on tm3.codtabladet = s.codcategoria
INNER JOIN pais                   ON pais.codpais = s.codpais
LEFT JOIN FINALIDAD AS FI         ON FI.CODFINALIDAD = P.CODFINALIDAD
LEFT JOIN TipoCredito AS TC       ON tc.CodTipoCredito = p.CodTipoCredito
INNER JOIN usuario AS u           ON p.CodUsuario = u.CodUsuario
INNER JOIN TablaMaestraDet AS tm4 ON s.codestado = tm4.CodTablaDet
--LEFT JOIN PrestamoCuota as pcu on p.CodPrestamo = pcu.CodPrestamo

LEFT JOIN SolicitudCredito AS SOLICITUD ON P.CodSolicitudCredito = SOLICITUD.CodSolicitudCredito
LEFT JOIN Usuario AS USUARIO            ON SOLICITUD.CodUsuarioSegAprob = USUARIO.CodUsuario

LEFT JOIN SolicitudCreditoOtrosDescuentos AS DESCUENTO ON P.CodSolicitudCredito = DESCUENTO.CodSolicitudCredito

WHERE CONVERT(VARCHAR(10),p.fechadesembolso,112) >= '20010101'
AND DESCUENTO.retencion = 'TOTAL RETENCIÓN'

AND s.codigosocio>0

ORDER BY RIGHT(CONCAT('0000000',p.numero),8)

'''

# SEGUIR CHEQUEANDO
df_monto_neto = pd.read_sql_query(query, conn)
df_monto_neto.drop_duplicates(subset = 'pagare_fincore', inplace = True)

df_monto_neto['Otorgado'] = df_monto_neto['Otorgado'].fillna(0)
df_monto_neto['retención'] = df_monto_neto['retención'].fillna(0)

df_monto_neto['Monto Neto'] = df_monto_neto['Otorgado'] - df_monto_neto['retención']

df_diferidos_columnas = df_diferidos_columnas.merge(df_monto_neto[['pagare_fincore', 'Monto Neto']],
                                                    left_on  = 'Nro Prestamo \nFincore',
                                                    right_on = 'pagare_fincore',
                                                    how      = 'left')
del df_diferidos_columnas['pagare_fincore']

#%% GENERACIÓN DEL EXCEL

'CREACIÓN DEL EXCEL'
nombre = "anx06 columnas parte 2 - " + fecha_corte + ".xlsx"
try:
    ruta = nombre
    os.remove(ruta)
except FileNotFoundError:
    pass

df_diferidos_columnas.to_excel(nombre,
                               index = False)

#%% UBICACIÓN DE LOS ARCHIVOS
# POR SI NO SABEMOS DÓNDE ESTÁN LOS ARCHIVOS
# Obtener la ubicación actual
ubicacion_actual = os.getcwd()

# Imprimir la ubicación actual
print("La ubicación actual es: " + ubicacion_actual)

#%% REPORTE DE BRECHAS
'##############################################################################'
'###########             BRECHAS DE UN MES A OTRO                ##############'
'##############################################################################'
df_diferidos = df_diferidos_ampliado.copy()
# EXTRAEMOS DATOS DEL MES PASADO

# Parámetros iniciales ==========================
# FECHA PARA EL NOMBRE DEL ARCHIVO ##############
fecha = 'Mayo 2024'
#################################################

# HAY QUE SELECCIONAR EL MES PASADO #############################################################
fecha_mes_pasado = '20240430' #esta fecha hay que ponerla en el formato requerido por SQL SERVER
#################################################################################################

#%%
import pyodbc
conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')

query = f'''
declare @fechacorte as datetime
set @fechacorte = '{fecha_mes_pasado}'

SELECT
	FechaCorte1, 
	Nro_Fincore,
	Saldodecolocacionescreditosdirectos24 AS 'SALDO CARTERA', 
	CapitalVigente26                      AS 'CAPITAL VIGENTE',
	nuevo_capitalvencido                  AS 'CAPITAL VENCIDO',
	CapitalenCobranzaJudicial30           AS 'COBRANZA JUDICIAL',
	SaldosdeCreditosCastigados38          AS 'SALDO CASTIGADO',
	TipodeCredito19                       AS 'TIPO DE CRÉDITO',
	TipodeProducto43                      AS 'TIPO DE PRODUCTO',
	Monedadelcredito17                    AS 'MONEDA',
	ProvisionesConstituidas37             AS 'PROVISIONES CONSTITUIDAS',
	ProvisionesRequeridas36               AS 'PROVISIONES REQUERIDAS',
	Rendimiento_Devengado40               AS 'INTERESES DEVENGADOS',
	InteresesenSuspenso41                 AS 'INTERESES EN SUSPENSO',
	IngresosDiferidos42                   AS 'INTERESES DIFERIDOS',
    Reprogramados52                       AS 'SALDO REPROGRAMADO',
	CASE
		WHEN TipodeProducto43 IN (34,35,36,37,38,39) THEN 'DXP'
		WHEN TipodeProducto43 IN (30,31,32,33) THEN 'LD'
		WHEN TipodeProducto43 IN (21,22,23,24,25,26,28,27,29) THEN 'MICRO'
		WHEN TipodeProducto43 IN (15,16,17,18,19) THEN 'PEQUEÑA'
		WHEN TipodeProducto43 IN (95,96,97,98,99) THEN 'MEDIANA'
		WHEN TipodeProducto43 IN (41,45) THEN 'HIPOTECARIA'
	END AS 'TIPO DE PRODUCTO TXT'
FROM 
	anexos_riesgos2..Anx06_preliminar
WHERE FechaCorte1 = @fechacorte
'''

anx06_mes_pasado = pd.read_sql_query(query, conn)

##################################################
COLUMNA_COMPARACION = 'TIPO DE PRODUCTO TXT'  ####
##################################################

pivot_mes_pasado = anx06_mes_pasado.pivot_table(index = [COLUMNA_COMPARACION],
                                       #columns=,
                                       values = ['SALDO CARTERA', 
                                                 'CAPITAL VENCIDO', 
                                                 'COBRANZA JUDICIAL', 
                                                 'SALDO CASTIGADO',
                                                 'PROVISIONES CONSTITUIDAS',
                                                 'PROVISIONES REQUERIDAS',
                                                 'INTERESES DEVENGADOS',
                                                 'INTERESES EN SUSPENSO',
                                                 'INTERESES DIFERIDOS',
                                                 'SALDO REPROGRAMADO'], 
                                       margins      = True, 
                                       margins_name = 'Total', #para sacar las sumatorias totales                                      
                                       aggfunc      = 'sum'
                                       )
#pivot_mes_pasado = pivot_mes_pasado.reset_index()
pivot_mes_pasado.fillna(0, inplace=True)

#%% orden de las columnas
ordenamiento_columnas = ['SALDO CARTERA', 
                         'CAPITAL VENCIDO', 
                         'COBRANZA JUDICIAL', 
                         'SALDO CASTIGADO',
                         'PROVISIONES CONSTITUIDAS',
                         'PROVISIONES REQUERIDAS',
                         'INTERESES DEVENGADOS',
                         'INTERESES EN SUSPENSO',
                         'INTERESES DIFERIDOS',
                         'SALDO REPROGRAMADO']

#%% filtración de columnas
pivot_mes_pasado = pivot_mes_pasado[ordenamiento_columnas]
#%% PIVOT DE ESTE MES

datos_actuales = df_diferidos[['Saldo de colocaciones (créditos directos) 24/',
                               'Capital Vencido 29/',
                               'Capital en Cobranza Judicial 30/',
                               'Saldos de Créditos Castigados 38/',
                               'Tipo de Producto 43/',
                               'TIPO DE PRODUCTO TXT',
                               'Tipo de Crédito 19/',
                               'Provisiones Constituidas 37/',
                               'Provisiones Requeridas 36/',
                               'Rendimiento\nDevengado 40/', 
                               'Intereses en Suspenso 41/', 
                               'Ingresos Diferidos 42/',
                               'Saldo Capital de Créditos Reprogramados 52/']]

pivot_mes_actual = datos_actuales.pivot_table(index=[COLUMNA_COMPARACION],
                                       #columns=,
                                       values=['Saldo de colocaciones (créditos directos) 24/', 
                                               'Capital Vencido 29/',
                                               'Capital en Cobranza Judicial 30/',
                                               'Saldos de Créditos Castigados 38/',
                                               'Provisiones Constituidas 37/',
                                               'Provisiones Requeridas 36/',
                                               'Rendimiento\nDevengado 40/', 
                                               'Intereses en Suspenso 41/', 
                                               'Ingresos Diferidos 42/',
                                               'Saldo Capital de Créditos Reprogramados 52/'], 
                                       margins      = True, 
                                       margins_name = 'Total', #para sacar las sumatorias totales                                      
                                       aggfunc      = 'sum'
                                       )
#pivot_mes_actual = pivot_mes_actual.reset_index()
pivot_mes_actual.fillna(0, inplace=True)

#%% pivot mes actual

pivot_mes_actual = pivot_mes_actual.rename(columns={#'Tipo de Crédito 19/'                           : 'TIPO DE CRÉDITO',
                                        'Saldo de colocaciones (créditos directos) 24/' : 'SALDO CARTERA',
                                        'Capital Vencido 29/'                           : 'CAPITAL VENCIDO',
                                        'Capital en Cobranza Judicial 30/'              : 'COBRANZA JUDICIAL',
                                        'Saldos de Créditos Castigados 38/'             : 'SALDO CASTIGADO',
                                        'Provisiones Constituidas 37/'                  : 'PROVISIONES CONSTITUIDAS',
                                        'Provisiones Requeridas 36/'                    : 'PROVISIONES REQUERIDAS',
                                        'Rendimiento\nDevengado 40/'                    : 'INTERESES DEVENGADOS', 
                                        'Intereses en Suspenso 41/'                     : 'INTERESES EN SUSPENSO',
                                        'Ingresos Diferidos 42/'                        : 'INTERESES DIFERIDOS',
                                        'Saldo Capital de Créditos Reprogramados 52/'   : 'SALDO REPROGRAMADO'})

pivot_mes_actual = pivot_mes_actual[ordenamiento_columnas]

#%% DIFERENCIAS DE UN MES A OTRO

diferencias = pivot_mes_actual - pivot_mes_pasado

#diferencias porcentuales
diferencias_porcentuales = diferencias.copy()

for columna in diferencias_porcentuales.columns:
    diferencias_porcentuales[columna] = (diferencias[columna] / pivot_mes_pasado[columna]) * 1
diferencias_porcentuales.fillna(0, inplace=True)

#%% exportación a excel

import pandas as pd

columna_inicio = 1

# Crea un objeto ExcelWriter para guardar los dataframes en un solo archivo
writer = pd.ExcelWriter(f'BRECHAS {fecha}.xlsx', engine = 'xlsxwriter')

# Define el espacio entre las tablas
espacio_entre_tablas = pd.DataFrame([''])

# Guarda los dataframes en el archivo Excel
pivot_mes_actual.to_excel(writer,
                          sheet_name = 'Brechas', 
                          startrow   = 0, 
                          startcol   = columna_inicio, 
                          index      = True)
writer.sheets['Brechas'].write(pivot_mes_actual.shape[0] + 1, #número de fila
                               columna_inicio,                #número de columna
                               'DATOS DEL MES ACTUAL')        #valor en esa fila y columna

pivot_mes_pasado.to_excel(writer, 
                          sheet_name = 'Brechas', 
                          startrow   = pivot_mes_actual.shape[0] + 3, 
                          startcol   = columna_inicio, 
                          index      = True)
writer.sheets['Brechas'].write(pivot_mes_actual.shape[0] + pivot_mes_pasado.shape[0] + 4, #número de fila
                               columna_inicio,                                            #número de columna
                               'DATOS DEL MES PASADO')                                    #valor en esa fila y columna

diferencias.to_excel(writer, 
                     sheet_name = 'Brechas', 
                     startrow   = pivot_mes_actual.shape[0] + pivot_mes_pasado.shape[0] + 6, 
                     startcol   = columna_inicio, 
                     index      = True)
writer.sheets['Brechas'].write(pivot_mes_actual.shape[0] + pivot_mes_pasado.shape[0] + diferencias.shape[0] + 7, #número de fila
                               columna_inicio,                                                                   #número de columna
                               'DIFERENCIAS DE UN MES A OTRO')                                                   #valor en esa fila y columna

diferencias_porcentuales.to_excel(writer, 
                                  sheet_name = 'Brechas', 
                                  startrow   = pivot_mes_actual.shape[0] + pivot_mes_pasado.shape[0] + diferencias.shape[0] + 9, 
                                  startcol   = columna_inicio, 
                                  index      = True)
writer.sheets['Brechas'].write(pivot_mes_actual.shape[0] + pivot_mes_pasado.shape[0] + diferencias.shape[0] + diferencias_porcentuales.shape[0] + 10, #número de fila
                               columna_inicio,                                                                                                        #número de columna
                               'DIFERENCIAS PORCENTUALES DE UN MES A OTRO')                                                                           #valor en esa fila y columna

# Guarda y cierra el archivo Excel
writer.save()
writer.close()

#%% UBICACIÓN DE LOS ARCHIVOS
# POR SI NO SABEMOS DÓNDE ESTÁN LOS ARCHIVOS
# Obtener la ubicación actual
ubicacion_actual = os.getcwd()

# Imprimir la ubicación actual
print("La ubicación actual es: " + ubicacion_actual)

