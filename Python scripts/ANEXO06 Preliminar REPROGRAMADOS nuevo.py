# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 10:40:15 2023

@author: Joseph Montoya
"""

###############################################################################
####              ANEXO 06 PRELIMINAR Y REPROGRAMADOS                      ####
###############################################################################

#%% IMPORTACIÓN DE LIBRERÍAS
import pandas as pd
import os
import numpy as np
from colorama import Back # , Style, init, Fore
import pyodbc

import warnings
warnings.filterwarnings('ignore')

#%% INDICACIONES PRELIMINARES
'Revisar que estén bien las fechas:'
# "Fecha Creacion Reprogramacion Nacimiento TXT"
# "Fecha Creacion Reprogramacion Corte TXT"

# Fecha Primer Cuota Gracia Nacimiento RPG TXT
# Primer Fecha Cuota Gracia Corte RPG TXT

# Fecha Ultimo 
# Pago TXT
# 'Fecha Ultimo \nPago TXT'

# Fecha Vencimiento Actual TXT

# Fecha Vencimiento 
# Origuinal TXT

# Fecha Venc Ult Cuota Cancelada

# E2

#%% ESTABLECER FECHA DEL MES

fecha_mes               = 'Julio 2024'  # Mes Año
fecha_corte             = '2024-07-31' # año-mes-día
fecha_corte_inicial     = '2024-07-01' # año-mes-día

#%%
columna_devengados  = 'Interes Devengado Nuevo'
columna_in_suspendo = 'Interes Suspenso Nuevo'

#%% UIT actual
uit = 5150

#%%
generar_excels = True #booleano True o False

#%% ARCHIVOS

# ESTABLECER EL DIRECTORIO ACTUAL ##########################################################
directorio = 'C:\\Users\\sanmiguel38\\Desktop\\REPORTE DE REPROGRAMADOS (primer paso del anexo06)\\2024\\2024 julio'
############################################################################################

# NOMBRE DE INSUMO ACTUAL ##################################################################
anx06_actual = 'Rpt_DeudoresSBS Anexo06 - Julio 2024 - campos ampliados- Insumo.xlsx'
############################################################################################

# DATOS DEL MES PASADO
# ubicación del ANX 06 del mes pasado ######################################################
#aquí el anexo06 del mes pasado, el preliminar (el que se genera para reprogramados)
ubicacion_anx06_anterior = 'C:\\Users\\sanmiguel38\\Desktop\\REPORTE DE REPROGRAMADOS (primer paso del anexo06)\\2024\\2024 junio'
############################################################################################

# ANX06 PRELIMINAR DEL MES PASADO ##########################################################
nombre_anx06 = 'Rpt_DeudoresSBS Anexo06 - Junio 2024 - campos ampliados procesado 01.xlsx'
############################################################################################

# filas a omitir del anexo actual ##########################################################
skip_rows_actual   = 4
############################################################################################

# filas a omitir del anexo anterior ########################################################
skip_rows_anterior = 2
############################################################################################

#%%
#%% IMPORTACIÓN DE INSUMO PRINCIPAL, ANEXO06 PRIMIGENIO

os.chdir(directorio)

bruto = pd.read_excel(anx06_actual,
                      skiprows = skip_rows_actual,
                      dtype = ({'Registro 1/'              : object, 
                                'Fecha de Nacimiento 3/'   : object,
                                'Código Socio 7/'          : object,
                                'Número de Documento 10/'  : object,
                                'Relación Laboral con la Cooperativa 13/'        :object, 
                                'Código de Agencia 16/'    : object,
                                'Moneda del crédito 17/'   : object, 
                                'Numero de Crédito 18/'    : object,
                                'Tipo de Crédito 19/'      : object,
                                'Sub Tipo de Crédito 20/'  : object,
                                'Fecha de Desembolso 21/'  : object,
                                'Cuenta Contable 25/'      : object,
                                'Tipo de Producto 43/'     : object,
                                'Fecha de Vencimiento Origuinal del Credito 48/' : object,
                                'Fecha de Vencimiento Actual del Crédito 49/'    : object,
                                'Nro Prestamo \nFincore'   : object,
                                'Refinanciado TXT'         : object }))

menos_bruto = bruto.drop(columns=[col for col in bruto.columns if 'Unnamed' in col]) #elimina columnas Unnamed

menos_bruto.dropna(subset=['Apellidos y Nombres / Razón Social 2/', 
                           'Fecha de Nacimiento 3/',
                           'Número de Documento 10/',
                           'Domicilio 12/',
                           'Numero de Crédito 18/'], inplace = True, how = 'all') #eliminando las filas vacías

menos_bruto['Código Socio 7/']         = menos_bruto['Código Socio 7/'].str.strip()
menos_bruto['Apellidos y Nombres / Razón Social 2/'] = menos_bruto['Apellidos y Nombres / Razón Social 2/'].str.strip()
menos_bruto['Profesion']               = menos_bruto['Profesion'].str.strip()
menos_bruto['Ocupacion']               = menos_bruto['Ocupacion'].str.strip()
menos_bruto['Actividad Economica']     = menos_bruto['Actividad Economica'].str.strip()
menos_bruto['Nro Prestamo \nFincore']  = menos_bruto['Nro Prestamo \nFincore'].astype(int).astype(str).str.zfill(8) #agregando los 8 ceros
menos_bruto['Numero de Crédito 18/']   = menos_bruto['Numero de Crédito 18/'].str.strip()

menos_bruto['Funcionario Origuinador'] = menos_bruto['Funcionario Origuinador'].str.strip()
menos_bruto['Funcionario Actual']      = menos_bruto['Funcionario Actual'].str.strip()
menos_bruto['Funcionaria TXT']         = menos_bruto['Funcionaria TXT'].str.strip()

#conteo de duplicados
mask = menos_bruto['Nro Prestamo \nFincore'].duplicated(keep=False)
df_duplicadoss = menos_bruto[mask]

print('filas duplicadas:')
print(df_duplicadoss.shape[0])
del df_duplicadoss

print(menos_bruto.shape[0])

menos_bruto = menos_bruto.drop_duplicates(subset = 'Nro Prestamo \nFincore') #por si acaso eliminamos duplicados
print(menos_bruto.shape[0])
print('si sale menos en el segundo es porque hubo duplicados')

#%% asignación del saldo castigado con capitalización de intereses en el saldo capital castigado
    
if menos_bruto['Saldos de Créditos Castigados 38/'].sum() < menos_bruto['Saldo Credito Castigado Con Capitalizacion'].sum():
    menos_bruto['Saldos de Créditos Castigados 38/'] = menos_bruto['Saldo Credito Castigado Con Capitalizacion']
    print('se reasignó el saldo de créditos castigados')
else:
    print('investigar')

#%% CÓDIGO ELIMINADOR DE CRÉDITOS SI ES QUE HACE FALTA ELIMINARLOS:

# cartera vendida EN FEBRERO 2024
# menos_bruto['Nro Prestamo \nFincore'] = menos_bruto['Nro Prestamo \nFincore'].str.strip()
# print(menos_bruto.shape[0])
# eliminar = ['00000681',
#             '00025314',
#             '00051147',
#             '00021245',
#             '00019565',
#             '00019911',
#             '00059920',
#             '00052890',
#             '00020153',
#             '00055472',
#             '00061987',
#             '00010827',
#             '00021016',
#             '00023215',
#             '00014819',
#             '00058140',
#             '00057592',
#             '00060249',
#             '00016572'
#             ]
# menos_bruto = menos_bruto[~menos_bruto['Nro Prestamo \nFincore'].isin(eliminar)]
# print(menos_bruto.shape[0])

#%% VERIFICAR SI HAY DUPLICADOS EN EL CÓDIGO DE SOCIO (de la base de datos)

datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')
server      = datos['DATOS'][0]
username    = datos['DATOS'][2]
password    = datos['DATOS'][3]
conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'
conn = pyodbc.connect(conn_str)

query = '''
SELECT 
	CodigoSocio, COUNT(*) AS CODIGO_DUPLICADOS 
FROM 
	Socio
WHERE 
	CodigoSocio IS NOT NULL
GROUP BY 
	CodigoSocio
HAVING COUNT(*) > 1

'''

cod_socio_duplicados = pd.read_sql_query(query, conn)
cod_socio_duplicados['CodigoSocio'] = cod_socio_duplicados['CodigoSocio'].str.strip()
cod_socio_duplicados = cod_socio_duplicados[cod_socio_duplicados['CodigoSocio'] != '']

if cod_socio_duplicados.shape[0] > 0:
    print(Back.RED + 'existen duplicados, notificar a Oscar y Cesar')
    print(cod_socio_duplicados)
    print(Back.RESET + '')
    
#%% AJUSTE DE PRODUCTO
# hay dos nuevos productos, el 26 y el 27
# el 26 es emprendimiento mujer (microempresa)
# el 27 es multioficios(hay que pasarlo a 32)
menos_bruto['Tipo de Producto 43/'] = menos_bruto['Tipo de Producto 43/'].astype(str)
menos_bruto['Tipo de Producto 43/'] = menos_bruto['Tipo de Producto 43/'].str.strip()
menos_bruto.loc[menos_bruto['Tipo de Producto 43/'] == '27', 'Tipo de Producto 43/'] = '32'
menos_bruto.loc[menos_bruto['Tipo de Producto 43/'] == '26', 'Tipo Credito TXT'] = 'EMPRENDE MUJER'
menos_bruto.loc[menos_bruto['Tipo de Producto 43/'] == '32', 'Tipo Credito TXT'] = 'LD-MULTIOFICIOS'
menos_bruto.loc[menos_bruto['Tipo de Producto 43/'] == '32', 'Tipo de Crédito 19/']  = '12'

print(menos_bruto[menos_bruto['Tipo de Producto 43/'] == '27'].shape[0])
print('debe salir cero')

#%% ELIMINACIÓN DE CRÉDITOS VENDIDOS (por si acaso)

vendidos = ['00001346' ,
            '00050796' ,
            '00000633' ,
            '00000942' ,
            '00020154' ,
            '00054955' ,
            '00001147' ,
            '00001287' ]

def eliminar(menos_bruto):
    if menos_bruto['Nro Prestamo \nFincore'] in vendidos:
        return 'eliminar'

menos_bruto['CRÉDITOS VENDIDOS (ELIMINAR)'] = menos_bruto.apply(eliminar, axis=1)

print(menos_bruto.shape[0])

menos_bruto = menos_bruto[menos_bruto['CRÉDITOS VENDIDOS (ELIMINAR)'] != 'eliminar']
menos_bruto = menos_bruto.drop('CRÉDITOS VENDIDOS (ELIMINAR)', axis = 1) # eliminación de columnas innecesaria

print('')
print(menos_bruto.shape[0])

df_mes_actual_copia = menos_bruto.copy()

#%% validación de los 'Nro Prestamo \nFincore' y 'Numero de Crédito 18/'
# si tienen 8 digitos deben ser iguales
def flag_investigar(row):
    prestamo_str_len = len(row['Nro Prestamo \nFincore'])
    credito_str_len  = len(row['Numero de Crédito 18/'])
    
    if prestamo_str_len == credito_str_len and (row['Nro Prestamo \nFincore'] != row['Numero de Crédito 18/']):
        return 'diferentes, investigar'
    else:
        return ''

# Aplicar la función a cada fila del DataFrame
menos_bruto['incorrespondencia'] = menos_bruto.apply(flag_investigar, axis=1)

investigar_con_cesar = menos_bruto[menos_bruto['incorrespondencia'] == 'diferentes, investigar']
if investigar_con_cesar.shape[0] > 0:
    print('Investigar el nro fincore')
    print(investigar_con_cesar[[ 'Apellidos y Nombres / Razón Social 2/',
                                 'Numero de Crédito 18/',
                                 'Nro Prestamo \nFincore' ]])

#%% ANEXO PRELIMINAR DEL MES PASADO

anx06_anterior = pd.read_excel(ubicacion_anx06_anterior + '\\' + nombre_anx06,
                               skiprows = skip_rows_anterior,
                               dtype = {'Registro 1/'                 : object,
                                        'Fecha de Nacimiento 3/'      : object,
                                        'Código Socio 7/'             : object,
                                        'Número de Documento 10/'     : object,
                                        'Relación Laboral con la Cooperativa 13/'         : object, 
                                        'Código de Agencia 16/'       : object,
                                        'Moneda del crédito 17/'      : object,
                                        'Numero de Crédito 18/'       : object,
                                        'Tipo de Crédito 19/'         : object,
                                        'Sub Tipo de Crédito 20/'     : object,
                                        'Fecha de Desembolso 21/'     : object,
                                        'Cuenta Contable 25/'         : object,
                                        'Tipo de Producto 43/'        : object,
                                        'Fecha de Vencimiento Origuinal del Credito 48/'  : object,
                                        'Fecha de Vencimiento Actual del Crédito 49/'     : object,
                                        'Nro Prestamo \nFincore'      : object,
                                        'Refinanciado TXT'            : object}) #no está funcionando esta vaina, debería leer en str
del ubicacion_anx06_anterior
del nombre_anx06

#agregando ceros al nro de fincore por si acaso
anx06_anterior['Nro Prestamo \nFincore'] = anx06_anterior['Nro Prestamo \nFincore'].astype(str).str.zfill(8)

mask = anx06_anterior['Nro Prestamo \nFincore'].duplicated(keep=False)
df_duplicadossss = anx06_anterior[mask]
print(df_duplicadossss.shape[0])

anx06_anterior.dropna(subset=['Apellidos y Nombres / Razón Social 2/', 
                   'Fecha de Nacimiento 3/',
                   'Número de Documento 10/',
                   'Domicilio 12/',
                   'Numero de Crédito 18/'], inplace=True, how='all') #eliminando las filas vacías

print(anx06_anterior.shape[0])

anx06_anterior = anx06_anterior.drop_duplicates(subset = 'Nro Prestamo \nFincore') #por si acaso eliminamos duplicados
print(anx06_anterior.shape[0])
print('si sale menos en el segundo es porque hubo duplicados')

#%% ORDENAMIENTO DE LAS COLUMNAS

ordenado = menos_bruto[[
    'Registro 1/',
    'Apellidos y Nombres / Razón Social 2/',
    'Fecha de Nacimiento 3/',
    'Género 4/',
    'Estado Civil 5/',
    'Sigla de la Empresa 6/',
    'Código Socio 7/',
    'Partida Registral 8/',
    'Tipo de Documento 9/',
    'Número de Documento 10/',
    'Tipo de Persona 11/',
    'Domicilio 12/',
    'Relación Laboral con la Cooperativa 13/',
    'Clasificación del Deudor 14/',
    'Clasificación del Deudor con Alineamiento 15/',
    'Código de Agencia 16/',
    'Moneda del crédito 17/',
    'Numero de Crédito 18/',
    'Tipo de Crédito 19/',
    'Sub Tipo de Crédito 20/',
    'Fecha de Desembolso 21/',
    'Monto de Desembolso 22/',
    'Tasa de Interés Anual 23/',
    'Saldo de colocaciones (créditos directos) 24/',
    'Cuenta Contable 25/',
    'Capital Vigente 26/',
    'Capital Reestrucutado 27/',
    'Capital Refinanciado 28/',
    'Capital Vencido 29/',
    'Capital en Cobranza Judicial 30/',
    'Capital Contingente 31/',
    'Cuenta Contable Capital Contingente 32/',
    'Dias de Mora 33/',
    'Saldos de Garantías Preferidas 34/',
    'Saldo de Garantías Autoliquidables 35/',
    'Provisiones Requeridas 36/',
    'Provisiones Constituidas 37/',
    'Saldos de Créditos Castigados 38/',
    'Cuenta Contable Crédito Castigado 39/',
    'Rendimiento\nDevengado 40/',
    'Intereses en Suspenso 41/',
    'Ingresos Diferidos 42/',
    'Tipo de Producto 43/',
    'Número de Cuotas Programadas 44/',
    'Número de Cuotas Pagadas 45/',
    'Periodicidad de la cuota 46/',
    'Periodo de Gracia 47/',
    'Fecha de Vencimiento Origuinal del Credito 48/',
    'Fecha de Vencimiento Actual del Crédito 49/',
    'Saldo de Créditos con Sustitución de Contraparte Crediticia 50/',
    'Saldo de Créditos que no cuentan con cobertura 51/',
    'Saldo Capital de Créditos Reprogramados 52/',
    'Saldo Capital en Cuenta de Orden por efecto del Covid 53/',
    'Subcuenta de orden \n54/\n',
    'Rendimiento Devengado por efecto del COVID 19 55/',
    'Saldo de Garantías con Sustitución de Contraparte 56/',
    'Saldo Capital de Créditos Reprogramados por efecto del COVID 19 57/',
    'Categoria TXT',
    'Saldo Colocacion Sin Capitalizacion de Intereses TXT',
    'Dscto Enviado TXT',
    'Desc Pagado TXT',
    'Fecha Vencimiento \nOriguinal TXT',
    'Fecha Vencimiento Actual TXT',
    'Mes Creacion Reprogramado Nacimiento TXT',
    'Fecha Creacion Reprogramacion Nacimiento TXT',
    'Mes Creacion\nReprogramado Corte \nTXT',
    'Fecha Creacion Reprogramacion Corte TXT',
    'Nro Dias Gracia Corte RPG TXT',
    'Nro Cuotas Canc Post Regro',
    'Nro Prestamos X Deudor TXT',
    'Fecha Ultimo \nPago TXT',
    'TEM TXT',
    'Nro Dias Gracia  Acumulado RPG TXT',
    'Tipo Reprogramacion TXT',
    'Fecha Primer Cuota Gracia Nacimiento RPG TXT',
    'Primer Fecha Cuota Gracia Corte RPG TXT',
    'Nro Reprogramaciones TXT',
    'Origen\n Prestamo',
    'Nro Prestamo \nFincore',
    'Por Cobrar Mes Actual TXT',
    'Reprogramado TXT',
    'Funcionaria TXT',
    'Nombre Empresa TXT',
    'Nombre PlanillaTXT',
    'Planilla Anterior TXT',
    'Cod Usuario Pri Aprob',
    'Cod Usuario Seg Aprob',
    'Profesion',
    'Ocupacion',
    'Actividad Economica',
    'Fecha Venc Ult Cuota Cancelada',
    'E1',
    'E2',
    'Afecta Todos',
    'Mayor100',
    'Mayor UIT',
    'Mayor UXC',
    columna_devengados,
    columna_in_suspendo,
    'Departamento',
    'Provincia',
    'Distrito',
    'Nombre Negocio',
    'Domicilio Negocio',
    'Distrito Negocio',
    'Dpto Negocio',
    'Provincia Negocio',
    'Funcionario Origuinador',
    'Funcionario Actual',
    'Fecha Desembolso TXT',
    'Total de Dias Entre Cuotas',
    'Dias Entre Ultima Cuota al Corte',
    'Dias Entre DSB y (Corte / Primera Cuota)',
    'TED',
    'Tasa Clasificacion  Deudor con Alineamiento TXT',
    'Tipo Credito TXT',
    'Sub Tipo Credito TXT',
    'TEA TXT',
    'Monto de Desembolso Origuinal TXT',
    'Refinanciado TXT',
    'Situacion TXT',
    'Fecha Situacion TXT',
    'Abogado TXT',
    'Fecha Asignacion Abogado TXT',
    'Nro Expediente TXT',
    'Fecha Expediente TXT',
    'Vendido TXT',
    'Fecha Castigo TXT',
    'Saldo Capital Real',
    'Interes Capital Real',
    'Fecha Termino \nPeriodo Gracia',
    'Flag Termino Periodo Gracia',
    'Monto Desembolso\nSoles Fijo'
    ]]

#%% REASIGNANDO FUNCIONARIO ADMINISTRADOR: (COMPROBAR SI AÚN ES NECESARIO ESTE BLOQUE DE CÓDIGO)
columna_funcionario = 'Funcionario Actual'
# modificación del funcionario administrador JOSÉ SANCHEZ
fincore_delf = ['00113801', '00104004', '00117340', '00095947', '00116920', '00110128', '00105401', '00111826', '00113403', 
                '00108586', '00109499', '00112633', '00103151', '00104750', '00110157', '00114475', '00111036', '00114489', 
                '00114089', '00102018', '00101618', '00112232', '00114833', '00113081', '00103685', '00114880', '00100061', 
                '00116058', '00112347', '00116108', '00111174', '00112916', '00115669', '00115075', '00097157', '00102188', 
                '00114241', '00109368', '00106285', '00111039', '00111652', '00106899', '00098991']
administrador_delf = ['ENRIQUE IVAN DELFINO BAYLON'] * 43

data = {"fincore": fincore_delf, "administrador": administrador_delf}
delfin = pd.DataFrame(data)
###############################################################################
fincore_truj = ['00085200', '00082052', '00082532', '00082493', '00087920', '00083856', '00100779', '00093786', '00080124', 
                '00078609', '00079639', '00105716', '00080950', '00099281', '00081650', '00086835', '00086955', '00081102', 
                '00084561', '00087435', '00105779', '00082874', '00106349', '00079613', '00087113', '00107949', '00090798']
administrador_truj = ['ADMINISTRADOR TRUJILLO'] * 27
data = {"fincore": fincore_truj, "administrador": administrador_truj}
trujillo = pd.DataFrame(data)
###############################################################################

def admin_reasignacion(df):
    if df['Nro Prestamo \nFincore'] in list(delfin['fincore']):
        return 'ENRIQUE IVAN DELFINO BAYLON'
    elif df['Nro Prestamo \nFincore'] in list(trujillo['fincore']):
        return 'ADMINISTRADOR TRUJILLO'
    else:
        return df[columna_funcionario]

ordenado[columna_funcionario] = ordenado.apply(admin_reasignacion, axis = 1)

###############################################################################

# cred_andrea_bilbao = pd.read_excel(io = 'ORIGINADOR ANDREA BILBAO.xlsx', 
#                                     dtype = {'nro_fincore' : str})
# columna_funcionario = 'Funcionario Origuinador'
# def originador_reasignacion(df):
#     if df['Nro Prestamo \nFincore'] in list(cred_andrea_bilbao['nro_fincore']):
#         return 'ANDREA BILBAO BRICEÑO'
#     else:
#         return df[columna_funcionario]

# ordenado[columna_funcionario] = ordenado.apply(originador_reasignacion, axis = 1)

#%% ORIGINADOR CORRECTO
# (modificar a partir del otro mes, para que el originador se saque del anexo06 preliminar de ahora en adelante)

# originador_df = anx06_anterior[['Nro Prestamo \nFincore', 'Funcionario Origuinador']]
# rename

originador_df = pd.read_excel(io    = 'C:\\Users\\sanmiguel38\\Desktop\\REPORTE DE REPROGRAMADOS (primer paso del anexo06)\\ORIGINADOR BASE DE DATOS DE REPORTES GERENCIALES.xlsx', 
                              dtype = {'Nro_Fincore_originador' : str,
                                       'Nro Prestamo \nFincore' : str},
                              sheet_name = 'originador validado')

originador_df['Nro Prestamo \nFincore']   = originador_df['Nro Prestamo \nFincore'].str.strip()
originador_df['rectificación de nombre']  = originador_df['rectificación de nombre'].str.strip()

ordenado = ordenado.merge(originador_df,
                          left_on  = 'Nro Prestamo \nFincore',
                          right_on = 'Nro Prestamo \nFincore',    #modificar
                          how      = 'left')

def originador_mes_anterior(ordenado):
    if pd.isna(ordenado['rectificación de nombre']):
        return ordenado['Funcionario Origuinador']
    else:
        return ordenado['rectificación de nombre']
    
ordenado['Funcionario Origuinador'] = ordenado.apply(originador_mes_anterior, axis = 1)

print('rectificar este código, aprox línea 520, porque se debe adaptar a que se saque datos del anexo06 preliminar cada mes')
del ordenado['rectificación de nombre']

#%% SALDO DE GARANTÍA DEL MES PASADO
# PONEMOS LOS SALDOS DE GARANTÍAS DEL MES PASADO, tenemos que tener cuidado con estO,
# estos datos debemos sacar del preliminar del anexo06, porque en el anexo 06 final 
# ya se han cambiado estos datos y se han puesto en las columnas 'monto de garantías'

garantias = anx06_anterior[['Nro Prestamo \nFincore',
                            'Saldos de Garantías Preferidas 34/', 
                            'Saldo de Garantías Autoliquidables 35/',
                            'Partida Registral 8/']]

nuevos_nombres = {
                'Nro Prestamo \nFincore'                 :  'fincore para merge',
                'Saldos de Garantías Preferidas 34/'     :  'garantias pref mes pasado',
                'Saldo de Garantías Autoliquidables 35/' :  'garantias autoli mes pasado',
                'Partida Registral 8/'                   :  'part registral mes pasado'
                 }

garantias = garantias.rename(columns = nuevos_nombres)
del nuevos_nombres

###################### merge para poner del mes pasado
ordenado = ordenado.merge(garantias, 
                         left_on   = ['Nro Prestamo \nFincore'], 
                         right_on  = ['fincore para merge'],
                         how       = 'left')
                                  
ordenado['Saldos de Garantías Preferidas 34/'] = ordenado['garantias pref mes pasado']
ordenado['Saldos de Garantías Preferidas 34/'] = ordenado['Saldos de Garantías Preferidas 34/'].fillna(0)
ordenado['Saldo de Garantías Autoliquidables 35/'] = ordenado['garantias autoli mes pasado']
ordenado['Saldo de Garantías Autoliquidables 35/'] = ordenado['Saldo de Garantías Autoliquidables 35/'].fillna(0)

#eliminar columnas que ya no sirven
ordenado.drop(['garantias pref mes pasado','garantias autoli mes pasado','fincore para merge'], axis=1, inplace=True)

#verificación si hizo buen match
actual = ordenado['Saldos de Garantías Preferidas 34/'].sum()
anterior = garantias['garantias pref mes pasado'].sum()

print('saldo de garantías preferidas actual '   + str(actual))
print('saldo de garantías preferidas anterior ' + str(anterior))
print('es normal que mes a mes se reduzca un poquito')
if actual == anterior:
    print('todo bien en traer saldos de garantías del mes pasado')
else:
    print('habría que chequear si algún crédito se canceló \no quizás no hizo match')
    
#%% colocando bien las partidas registrales que se jalan desde el mes pasado
# probar si funciona
ordenado['Partida Registral 8/'] = ordenado['Partida Registral 8/'].fillna('')
ordenado['Partida Registral 8/'] = ordenado['Partida Registral 8/'].str.strip()

ordenado['part registral mes pasado'] = ordenado['part registral mes pasado'].fillna('')
ordenado['part registral mes pasado'] = ordenado['part registral mes pasado'].str.strip()

def partidas_registrales(ordenado):
    if ordenado['Partida Registral 8/'] != '':
        return ordenado['Partida Registral 8/']
    elif ordenado['Partida Registral 8/'] == '':
        return ordenado['part registral mes pasado']

print(ordenado['Partida Registral 8/'].unique().shape[0])
ordenado['Partida Registral 8/'] = ordenado.apply(partidas_registrales, axis = 1)
print(ordenado['Partida Registral 8/'].unique().shape[0])
print('en la segunda debe salir más')
del ordenado['part registral mes pasado']

#%%% strip de texto
ordenado['Apellidos y Nombres / Razón Social 2/'] = ordenado['Apellidos y Nombres / Razón Social 2/'].str.strip()

#%% CRÉDITOS GARANTIZADOS PARA OSWALD
###############################################################
## generamos el archivo para Oswald y/o Juan Carlos        ####
## para que nos ayuden con los certificados de depósitos   ####
###############################################################

fecha_corte_inicial_int = int(fecha_corte_inicial[0:4] + fecha_corte_inicial[5:7] + fecha_corte_inicial[8:10])

filtrado_certificados = ordenado[ordenado['Fecha de Desembolso 21/'].astype(int) >= fecha_corte_inicial_int]

para_enviar = filtrado_certificados[filtrado_certificados['Monto de Desembolso 22/'] >= 90000]
para_enviar = para_enviar[['Apellidos y Nombres / Razón Social 2/',
                           'Fecha de Desembolso 21/',
                           'Monto de Desembolso 22/',
                           'Nro Prestamo \nFincore']]

para_enviar['''Nro \nCert.Depósito \nFincore'''] = ''
para_enviar['''Moneda e \nImporte'''] = ''
para_enviar['Socio que Garantiza'] = ''

#reporte para enviar a Juan Carlos o a Oswald
if generar_excels == True:
    try:
        ruta = f'Créditos Garantizados con CD {fecha_mes}.xlsx'
        os.remove(ruta)
    except FileNotFoundError:
        pass

    para_enviar.to_excel(ruta,
                         index = False)

#%% INDICACIONES sobre los créditos con garantía
# =============================================================================
# # ===========================================================================
# # # el código que envíe va en partida registral
# # # EL MONTO QUE ENVÍEN IRÁ EN 'Saldo de Garantías Autoliquidables 35/'
# # # puede que esté en dólares, hay que pasarlo a soles
# # # esto se añade después de generar este archivo, para generar el anexo06 final, no en el preliminar
# # ===========================================================================
# =============================================================================

#%% AJUSTE SALDO SIN CAPITALIZAR (actualmente saldo real)
# HAY CASOS EN LOS QUE EL SALDO SIN CAPITALIZACIÓN ES MAYOR AL CAPITALIZADO, VAMOS A VER QUÉ HACER AL RESPECTO

ordenado['Saldo Colocacion Con Capitalizacion de Intereses TXT'] = ordenado['Saldo de colocaciones (créditos directos) 24/']
ordenado['Saldo Colocacion Con Capitalizacion de Intereses TXT'] = ordenado['Saldo Colocacion Con Capitalizacion de Intereses TXT'].astype(float).round(2)
ordenado['Saldo Capital Real']      = ordenado['Saldo Capital Real'].astype(float)
ordenado['Monto de Desembolso 22/'] = ordenado['Monto de Desembolso 22/'].astype(float)

# ajuste del saldo real para que no tenga 1 céntimo de más de ciertos casitos
def parse_dates(date_str):
    formatos = ['%Y%m%d']
    for formato in formatos:
        try:
            return pd.to_datetime(date_str, format=formato)
        except ValueError:
            pass
    return pd.NaT
ordenado['f desembolso auxiliar'] = ordenado['Fecha de Desembolso 21/'].apply(parse_dates)

def obtener_fecha_anterior_tres_meses(fecha):
    # Convertir la fecha de cadena a un objeto pd.Timestamp
    fecha_actual = pd.Timestamp(fecha)    
    # Obtener la fecha tres meses antes
    fecha_anterior_tres_meses = fecha_actual - pd.DateOffset(months = 2)
    # Obtener el primer día del mes
    primer_dia_mes_anterior = fecha_anterior_tres_meses.replace(day = 1)
    return primer_dia_mes_anterior
hace_3_meses = obtener_fecha_anterior_tres_meses(fecha_corte)

def ajuste_real(ordenado):
    # ajuste de créditos que tienen unos cuántos céntimos de diferencia de más
    if (abs(ordenado['Saldo Capital Real'] - ordenado['Monto de Desembolso 22/']) < 0.50) & \
       (ordenado['Flag Termino Periodo Gracia']  == 'NO') & \
       (ordenado['Número de Cuotas Pagadas 45/'] == 0) & \
       (ordenado['f desembolso auxiliar'] >= hace_3_meses):
        return ordenado['Monto de Desembolso 22/']
    else:
        return ordenado['Saldo Capital Real']
ordenado['Saldo Capital Real'] = ordenado.apply(ajuste_real, axis = 1)

ordenado['Saldo de colocaciones (créditos directos) 24/'] = ordenado['Saldo Capital Real']
ordenado['Saldo de colocaciones (créditos directos) 24/'] = ordenado['Saldo de colocaciones (créditos directos) 24/'].round(2)

print('Debe salir cero')
print(ordenado[ordenado['Saldo de colocaciones (créditos directos) 24/'] < 0].shape[0])
if (ordenado[ordenado['Saldo de colocaciones (créditos directos) 24/'] < 0].shape[0]) > 0:
    print('investigar, significa que hay un saldo de cartera negativo')

# print(ordenado['Saldo de colocaciones (créditos directos) 24/'].sum())
# print(ordenado['Capital Vigente 26/'].sum())
# print(ordenado['Capital Vencido 29/'].sum())
# print(ordenado['Capital en Cobranza Judicial 30/'].sum())
# print(ordenado['Saldos de Créditos Castigados 38/'].sum())

del ordenado['f desembolso auxiliar']

#%% diferencia negativa
def negativos_saldo_cartera(ordenado):
    if ordenado['Saldo de colocaciones (créditos directos) 24/'] < 0:
        return ordenado['Saldo Colocacion Con Capitalizacion de Intereses TXT']
    else:
        return ordenado['Saldo de colocaciones (créditos directos) 24/']
    
ordenado['Saldo de colocaciones (créditos directos) 24/'] = ordenado.apply(negativos_saldo_cartera, axis = 1)

#%% un poco de limpieza de texto
ordenado['Código Socio 7/'] = ordenado['Código Socio 7/'].astype(str).str.strip()

ordenado['Nro Prestamo \nFincore'] = ordenado['Nro Prestamo \nFincore'].str.strip()

#%%CORRECCIÓN TIPO DE CRÉDITO 19/
#verificación del tipo de producto 19/
#para créditos MYPE
ordenado['Tipo de Crédito 19/'] = ordenado['Tipo de Crédito 19/'].astype(str) #por si acasito
ordenado['Tipo de Crédito 19/'] = ordenado['Tipo de Crédito 19/'].str.strip()

def etiqueta_mype(ordenado):
    if ordenado['Tipo de Crédito 19/'] in ['08', '09', '10', 8, 9, 10]:
        return 'mype'
    else:
        return 'otros'
ordenado['etiqueta mype'] = ordenado.apply(etiqueta_mype, axis=1)

###############################################################################
# LECTURA DE INFORMACIÓN DE LOS 6 ÚLTIMOS MESES
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
	SaldosdeCreditosCastigados38,
	Saldodecolocacionescreditosdirectos24 + SaldosdeCreditosCastigados38 as 'SALDO TOTAL',
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
            
		END AS 'TIPO_PRODUCTO',

	TipodeCredito19,
	CASE
		WHEN TipodeCredito19 = 06 THEN 'CORPORATIVO'
		WHEN TipodeCredito19 = 07 THEN 'GRAN EMPRESA'
		WHEN TipodeCredito19 = 08 THEN 'MEDIANA EMPRESA'
		WHEN TipodeCredito19 = 09 THEN 'PEQUEÑA EMPRESA'
		WHEN TipodeCredito19 = 10 THEN 'MICRO EMPRESA'
		WHEN TipodeCredito19 = 11 THEN 'CONSUMO REVOLVENTE'
		WHEN TipodeCredito19 = 12 THEN 'CONSUMO NO REVOLVENTE'
		WHEN TipodeCredito19 = 13 THEN 'HIPOTECARIO PARA VIVIENDA'
			ELSE 'OTROS'

		END AS 'TIPO_CRÉDITO'	
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
tipo_cred_mype = [8, 9, 10, '8', '08', '09', '10']

base_6meses = base_6meses[base_6meses['TipodeCredito19'].isin(tipo_cred_mype)]

pivot_6meses = base_6meses.pivot_table( values  = 'SALDO TOTAL',
                                        index   = 'CodigoSocio7',
                                        columns = 'FechaCorte1',
                                        aggfunc = 'sum').reset_index()
pivot_6meses = pivot_6meses.fillna(0)

########## HASTA AQUÍ YA SE SUMÓ TODO EL SALDO CAPITAL DE 5 MESES ATRÁS #######

df_corto = ordenado[['Tipo de Crédito 19/',
                     'Saldos de Créditos Castigados 38/',
                     'Saldo de colocaciones (créditos directos) 24/',
                     'Código Socio 7/',
                     
                     'Nro Prestamo \nFincore']]

#sumamos saldo de cartera y saldo castigado
df_corto.loc[:, 'monto mype'] = df_corto['Saldo de colocaciones (créditos directos) 24/'] + df_corto['Saldos de Créditos Castigados 38/']

#filtrado
corto_filtrado = df_corto.loc[df_corto['Tipo de Crédito 19/'].isin(tipo_cred_mype)]
#tabla resumen de sumarización						                                          
tabla_resumen = corto_filtrado.groupby('Código Socio 7/')['monto mype'].sum()
tabla_resumen = tabla_resumen.reset_index()

#rename
tabla_resumen = tabla_resumen.rename(columns={"Código Socio 7/": "CodigoSocio7"})

tabla_resumen = tabla_resumen.merge( pivot_6meses,
                                     left_on  = "CodigoSocio7",
                                     right_on = 'CodigoSocio7',
                                     how      = 'left')

tabla_resumen.fillna(0, inplace = True)

def verificar_mype(fila):
    #  08 MEDIANA EMPRESA
    #  09 PEQUEÑA EMPRESA
    #  10 MICRO EMPRESA
    if any(valor > 300000 for valor in fila[1:]):
        return '08'
    elif any(valor > 20220 for valor in fila[1:]):
        return '09'
    else:
        return '10'
    
tabla_resumen['tipo mype'] = tabla_resumen.apply(verificar_mype, axis = 1)

# ESTA TABLA AUXILIAR CONTIENE EL VERDADERO TIPO DE CÓDIGO QUE DEBE CORRESPONDER AL CRÉDITO

#%% merge con la tabla auxiliar
ordenado = ordenado.merge(tabla_resumen[['CodigoSocio7', 'tipo mype']],
                          left_on  = 'Código Socio 7/',
                          right_on = 'CodigoSocio7',
                          how      = 'left')
del ordenado['CodigoSocio7']

def asign_prod_19(ordenado):
    if pd.isna(ordenado['tipo mype']):
        return ordenado['Tipo de Crédito 19/']
    elif (~pd.isna(ordenado['tipo mype'])) and (ordenado['Tipo de Crédito 19/'] not in tipo_cred_mype):
        return ordenado['Tipo de Crédito 19/']
    else:
        return ordenado['tipo mype']
ordenado['tipo crédito 19 corregido'] = ordenado.apply(asign_prod_19, axis=1)

# def asign_prod_19(ordenado):
#     if (ordenado['etiqueta mype'] == 'mype') & \
#     (ordenado['Monto de Desembolso 22/'] > 0) & \
#     (ordenado['Monto de Desembolso 22/'] <= 20000):
#         return '10'
#     elif (ordenado['etiqueta mype'] == 'mype') & \
#     (ordenado['Monto de Desembolso 22/'] > 20000) & \
#     (ordenado['Monto de Desembolso 22/'] <= 300000):
#         return '09'
#     elif (ordenado['etiqueta mype'] == 'mype') & \
#     (ordenado['Monto de Desembolso 22/'] > 300000):
#         return '08'
#     else:
#         return ordenado['Tipo de Crédito 19/']

# ordenado['tipo crédito 19 corregido'] = ordenado.apply(asign_prod_19, axis=1)

ordenado.drop(['etiqueta mype'], axis=1, inplace=True)
ordenado.drop(['tipo mype'], axis=1, inplace=True)

ordenado['Tipo de Crédito 19/ (original)'] = ordenado['Tipo de Crédito 19/']
ordenado['Tipo de Crédito 19/'] = ordenado['tipo crédito 19 corregido']
ordenado.drop(['tipo crédito 19 corregido'], axis=1, inplace=True)

filtrado_credito_19 = ordenado[ordenado['Tipo de Crédito 19/ (original)'] != ordenado['Tipo de Crédito 19/']]

filtrado_credito_19['Monto de Desembolso Origuinal TXT'] = filtrado_credito_19['Monto de Desembolso Origuinal TXT'].astype(float)
filtrado_credito_19 = filtrado_credito_19[['Registro 1/',
                                           'Apellidos y Nombres / Razón Social 2/',
                                           'Código Socio 7/',
                                           'Número de Documento 10/',
                                           'Nro Prestamo \nFincore',
                                           'Tipo de Crédito 19/ (original)',
                                           'Tipo de Crédito 19/',
                                           'Monto de Desembolso Origuinal TXT',
                                           'Monto de Desembolso 22/',
                                           'Moneda del crédito 17/'
                                           ]]
ordenado.drop(['Tipo de Crédito 19/ (original)'], axis=1, inplace=True)
filtrado_credito_19 = filtrado_credito_19.rename(columns={'Nro Prestamo \nFincore': "Fincore"})

#guardamos este excel para mandárselo a Cesar
if generar_excels == True:
    try:
        ruta = "Corrección Tipo de Crédito 19.xlsx"
        os.remove(ruta)
    except FileNotFoundError:
        pass

    filtrado_credito_19.to_excel(ruta, 
                                 index=False)
else:
    pass

#%% CLASIFICACIÓN SIN ALINEAMIENTO 14/
#calculamos alineamiento 14/
#arreglamos la columna de los refinanciados
ordenado['Refinanciado TXT'] = ordenado['Refinanciado TXT'].str.upper()
ordenado['Refinanciado TXT'] = ordenado['Refinanciado TXT'].str.strip()
ordenado['Refinanciado TXT'] = ordenado['Refinanciado TXT'].astype(str)
print(ordenado['Refinanciado TXT'].unique())

#calculamos clasificación con alineamiento interno
#por si acaso convertirmo el tipo de dato a numero
ordenado['Dias de Mora 33/'] = ordenado['Dias de Mora 33/'].astype(int)
def alineamiento14(ordenado):
#    if ('REFINANCIADO' not in ordenado['Refinanciado TXT'] or 'Refinanciado' not in ordenado['Refinanciado TXT']):
        if ordenado['Tipo de Crédito 19/'] in ['06', '07', '08']:
            if ordenado['Dias de Mora 33/'] <=15:
                return '0'
            elif ordenado['Dias de Mora 33/'] <=60:
                return '1'
            elif ordenado['Dias de Mora 33/'] <=120:
                return '2'
            elif ordenado['Dias de Mora 33/'] <=365:
                return '3'
            elif ordenado['Dias de Mora 33/'] >365:
                return '4'
        elif ordenado['Tipo de Crédito 19/'] in ['09', '10', '11','12']:
            if ordenado['Dias de Mora 33/'] <=8:
                return '0'
            elif ordenado['Dias de Mora 33/'] <=30:
                return '1'
            elif ordenado['Dias de Mora 33/'] <=60:
                return '2'
            elif ordenado['Dias de Mora 33/'] <=120:
                return '3'
            elif ordenado['Dias de Mora 33/'] >120:
                return '4'
        elif ordenado['Tipo de Crédito 19/'] in ['13']:
            if ordenado['Dias de Mora 33/'] <=30:
                return '0'
            elif ordenado['Dias de Mora 33/'] <=60:
                return '1'
            elif ordenado['Dias de Mora 33/'] <=120:
                return '2'
            elif ordenado['Dias de Mora 33/'] <=365:
                return '3'
            elif ordenado['Dias de Mora 33/'] >365:
                return '4'
#    elif ('REFINANCIADO' in ordenado['Refinanciado TXT'] or 'Refinanciado' in ordenado['Refinanciado TXT']):
#        return ordenado['Clasificación del Deudor 14/'].astype(int).astype(str)
        else:
            return 'revisar caso'

#aplicamos la función
ordenado['alineamiento14 provisional'] = ordenado.apply(alineamiento14, axis=1)

#convertimos esa columna a numerica
ordenado['alineamiento14 provisional'] = ordenado['alineamiento14 provisional'].astype(int)

#este resultado se debería asignar a la columna 14/
ordenado['Clasificación del Deudor 14/'] = ordenado['alineamiento14 provisional']
ordenado.drop(['alineamiento14 provisional'], axis=1, inplace=True)

nulos = ordenado[pd.isna(ordenado['Clasificación del Deudor 14/'])]
print(nulos.shape[0])
del nulos
revisar = ordenado[ordenado['Clasificación del Deudor 14/'] == 'revisar caso']
print(revisar.shape[0])
print('revisar si sale más de cero')
del revisar

#%% CLASIFICACIÓN CON ALINEAMIENTO 15/

#primero que nada columnas auxiliares
saldo_total = ordenado.groupby('Código Socio 7/')['Saldo de colocaciones (créditos directos) 24/'].sum().reset_index()
saldo_total = saldo_total.rename(columns={"Código Socio 7/": "codigo para merge"})
saldo_total = saldo_total.rename(columns={"Saldo de colocaciones (créditos directos) 24/": "saldo para dividir"})

#merge
ordenado = ordenado.merge(saldo_total, 
                          how      = 'left', 
                          left_on  = ['Código Socio 7/'], 
                          right_on = ["codigo para merge"])

ordenado.drop(["codigo para merge"], 
              axis    = 1, 
              inplace = True)

#verificamos si hay nulos
#todo bien si sale un dataframe vacío
df_nulos_alineamiento = ordenado[ordenado["saldo para dividir"].isnull()] 

#división
ordenado['porcentaje del total'] =  ordenado['Saldo de colocaciones (créditos directos) 24/']/ \
                                    ordenado["saldo para dividir"]
#parte 1 concluída
###############################################################################                                        
#%% PARTE 2 ALINEAMIENTO 15/
#creamos función que crea columna auxiliar para escoger los que sirven para el alineamiento
###############################################
# uit = 4950 #valor de la uit en el año 2023  ###
###############################################
def monto_menor(ordenado):
    if ((ordenado['Saldo de colocaciones (créditos directos) 24/'] < 100) and \
        (ordenado['porcentaje del total'] < 0.01)) or \
        ((ordenado['porcentaje del total'] < 0.01) and \
        (ordenado['Saldo de colocaciones (créditos directos) 24/'] < 3*uit)):
        return 'menor'
    # elif ordenado['porcentaje del total'] >= 0.01:
    #     return 'mayor'
    else:
        return 'mayor'
ordenado['credito menor'] = ordenado.apply(monto_menor, axis=1)

#procedemos a filtrar los que son mayores
df_filtro_alineamiento = ordenado[ordenado['credito menor'] == 'mayor']
df_filtro_alineamiento = df_filtro_alineamiento[['Clasificación del Deudor 14/', "Código Socio 7/"]]

#agrupamos por código y máximo alineamiento
calificacion = df_filtro_alineamiento.groupby("Código Socio 7/")['Clasificación del Deudor 14/'].max().reset_index()
calificacion = calificacion.rename(columns={"Código Socio 7/": 'cod socio para merge'})
calificacion = calificacion.rename(columns={'Clasificación del Deudor 14/': 'calificacion para merge'})

#hora del merge
ordenado = ordenado.merge(calificacion, 
                                  how='left', 
                                  left_on=['Código Socio 7/'], 
                                  right_on=['cod socio para merge'])
#hasta aquí ya hemos asignado el tipo de producto, de manera general, debería estar todo unificado. falta poner las excepciones,
ordenado.drop(['cod socio para merge'], axis=1, inplace=True)

# =============================================================================
# para hacer pruebitas con el excel
# ordenado.to_excel('asdasd.xlsx',
#                   index = False)
# =============================================================================
#%% ASIGNACIÓN ALINEMIENTO 15/ CONDICIONAL
#finalmente, función para asignar el alineamiento 15/
def asignacion_15(ordenado):
    if ordenado['credito menor'] == 'mayor':
        return ordenado['calificacion para merge']
    elif ordenado['credito menor'] == 'menor':
        return ordenado['Clasificación del Deudor 14/']
    else:
        return 'investigar caso'
ordenado['alineamiento 15 por joseph'] = ordenado.apply(asignacion_15, axis=1)
filtrado_investigar = ordenado[ordenado['alineamiento 15 por joseph'] == 'investigar caso']
del filtrado_investigar

ordenado['Clasificación del Deudor con Alineamiento 15/'] = ordenado['alineamiento 15 por joseph']

ordenado.drop(['saldo para dividir',
               'porcentaje del total',
               'credito menor',
               'calificacion para merge',
               'alineamiento 15 por joseph'], axis=1, inplace=True)

#%% CORRECCIÓN DEL VIGENTE, REFINANCIADO, VENCIDO Y JUDICIAL
#creamos algoritmo para arreglar Vigente, Refinanciado, Vencido, judicial
def arreglo1(ordenado):
    if (ordenado['Capital Refinanciado 28/'] == 0) & \
    (ordenado['Capital en Cobranza Judicial 30/'] == 0):
        return ordenado['Saldo de colocaciones (créditos directos) 24/'] - \
        ordenado['Capital Vencido 29/']
    else:
        return ordenado['Capital Vigente 26/']
ordenado['Capital Vigente 26/'] = ordenado.apply(arreglo1, axis=1)

def arreglo1_2(ordenado):
    if ordenado['Capital Vigente 26/'] < 0:
        return ordenado['Saldo de colocaciones (créditos directos) 24/']
    else:
        return ordenado['Capital Vencido 29/']
ordenado['Capital Vencido 29/'] = ordenado.apply(arreglo1_2, axis=1)

def arreglo1_3(ordenado):
    if ordenado['Capital Vigente 26/'] < 0:
        return 0
    else:
        return ordenado['Capital Vigente 26/']
ordenado['Capital Vigente 26/'] = ordenado.apply(arreglo1_3, axis=1)

def arreglo2(ordenado):
    if (ordenado['Capital Vigente 26/'] == 0) & \
    (ordenado['Capital en Cobranza Judicial 30/'] == 0) & \
    (ordenado['Capital Refinanciado 28/'] > 0):
        return ordenado['Saldo de colocaciones (créditos directos) 24/'] - \
        ordenado['Capital Vencido 29/']
    else:
        return ordenado['Capital Refinanciado 28/']
ordenado['Capital Refinanciado 28/'] = ordenado.apply(arreglo2, axis=1)
    
def arreglo2_2(ordenado):
    if ordenado['Capital Refinanciado 28/'] < 0:
        return ordenado['Saldo de colocaciones (créditos directos) 24/']
    else:
        return ordenado['Capital Vencido 29/']
ordenado['Capital Vencido 29/'] = ordenado.apply(arreglo2_2, axis=1)

def arreglo2_3(ordenado):
    if ordenado['Capital Refinanciado 28/'] < 0:
        return 0
    else:
        return ordenado['Capital Refinanciado 28/']
ordenado['Capital Refinanciado 28/'] = ordenado.apply(arreglo2_3, axis=1)

print(ordenado['Saldo de colocaciones (créditos directos) 24/'].sum())
print(ordenado['Capital Vigente 26/'].sum())
print(ordenado['Capital Vencido 29/'].sum())
print(ordenado['Capital en Cobranza Judicial 30/'].sum())
print(ordenado['Saldos de Créditos Castigados 38/'].sum())

#%% Eliminación de duplicados

print(ordenado.shape[0])
ordenado = ordenado.drop_duplicates(subset = 'Nro Prestamo \nFincore')
print(ordenado.shape[0])
print('si sale menos es porque hubo duplicados')

#%% SALDOS CASTIGADOS NEGATIVOS LUEGO DE DESCAPITALIZAR:
# buscar en CRONOGRAMA DE PRÉSTAMO si aparece alguno:
revisar_en_fincore = ordenado[ordenado['Saldos de Créditos Castigados 38/'] < 0]
print(revisar_en_fincore.shape[0])
print('debe salir cero, sino hay que reemplazar el monto castigado por su saldo que aparece en el Fincore')

# corregimos, poniendo el saldo capital en el monto de saldo
#en este caso estoy poniendo el saldo castigado de un caso recurrente
if 'CHUCUYA HERNANDEZ CLELIA MARIA' in list(revisar_en_fincore['Apellidos y Nombres / Razón Social 2/']):
    ordenado.loc[(ordenado['Apellidos y Nombres / Razón Social 2/'] == 'CHUCUYA HERNANDEZ CLELIA MARIA') & \
                 (ordenado['Nro Prestamo \nFincore'] == '00073897'), 
                 'Saldos de Créditos Castigados 38/'] = 39.22
        
if 'RIOS GOMEZ RONALD' in list(revisar_en_fincore['Apellidos y Nombres / Razón Social 2/']):
    ordenado.loc[(ordenado['Apellidos y Nombres / Razón Social 2/'] == 'RIOS GOMEZ RONALD') & \
                 (ordenado['Nro Prestamo \nFincore'] == '00059697'), 
                 'Saldos de Créditos Castigados 38/'] = 7

revisar_en_fincore = ordenado[ordenado['Saldos de Créditos Castigados 38/'] < 0]
print(revisar_en_fincore.shape[0])
print('debe salir cero, sino hay que reemplazar el monto castigado por su saldo')

'''
print(ordenado['Saldo de colocaciones (créditos directos) 24/'].sum())
print(ordenado['Capital Vigente 26/'].sum())
print(ordenado['Capital Vencido 29/'].sum())
print(ordenado['Capital en Cobranza Judicial 30/'].sum())
print(ordenado['Saldos de Créditos Castigados 38/'].sum())
'''
#%%
def añadiendo_cuenta_contable(ordenado):
    if ordenado['Saldos de Créditos Castigados 38/'] > 0:
        return '811302'
    else:
        return ordenado['Cuenta Contable Crédito Castigado 39/']
    
ordenado['Cuenta Contable Crédito Castigado 39/'] = ordenado.apply(añadiendo_cuenta_contable, axis=1)    

#arreglando la Cuenta Contable Crédito Castigado 39/ (811302 ->  8113020000)
ordenado['Cuenta Contable Crédito Castigado 39/'] = ordenado['Cuenta Contable Crédito Castigado 39/'].str.strip()

def cuenta_contable_castigados(ordenado):
    if '811302' in ordenado['Cuenta Contable Crédito Castigado 39/']:
        return '8113020000'
    else:
        ''
ordenado['Cuenta Contable Crédito Castigado 39/'] = ordenado.apply(cuenta_contable_castigados, axis=1)

print(ordenado['Cuenta Contable Crédito Castigado 39/'].unique())
print('''si sale ['8113020000' None] entonces todo bien''')
print(ordenado[ordenado['Cuenta Contable Crédito Castigado 39/'] == '8113020000'].shape[0])
print(ordenado[ordenado['Saldos de Créditos Castigados 38/'] > 0].shape[0])
print('debe salir el mismo número, sino hay que investigar, porque habrían castigados sin cuenta contable o viceversa')

#%% AJUSTE EN CASO TENGAMOS QUE CORREGIR LOS CRÉDITOS QUE TIENEN VIGENTE A PESAR DE TENER MUCHOS DÍAS DE MORA

###############################################################################
# ahora sí nos aseguramos de quitar alguna vaina que no cuadra
mask_castigado = ordenado['Saldos de Créditos Castigados 38/'] > 0

ordenado.loc[mask_castigado, 'Saldo de colocaciones (créditos directos) 24/'] = 0
ordenado.loc[mask_castigado, 'Capital Vigente 26/']                           = 0
ordenado.loc[mask_castigado, 'Capital Reestrucutado 27/']                     = 0
ordenado.loc[mask_castigado, 'Capital Refinanciado 28/']                      = 0
ordenado.loc[mask_castigado, 'Capital Vencido 29/']                           = 0
ordenado.loc[mask_castigado, 'Capital en Cobranza Judicial 30/']              = 0

###############################################################################
def caso_mediana_vencido1(ordenado):
    if ordenado['Tipo de Crédito 19/'] in ['06', '07', '08']    \
    and ordenado['Dias de Mora 33/']        > 15                \
    and ordenado['Capital Vencido 29/']     > 0                 \
    and ordenado['Capital en Cobranza Judicial 30/'] == 0       \
    and ordenado['Capital Vigente 26/']     > 0:
        return ordenado['Capital Vigente 26/'] + ordenado['Capital Vencido 29/']
    else:
        return ordenado['Capital Vencido 29/']

ordenado['Capital Vencido 29/'] = ordenado.apply(caso_mediana_vencido1, axis=1)

def caso_mediana_vencido2(ordenado):
    if ordenado['Tipo de Crédito 19/'] in ['06', '07', '08']    \
    and ordenado['Dias de Mora 33/']        > 15                \
    and ordenado['Capital Vencido 29/']     > 0                 \
    and ordenado['Capital en Cobranza Judicial 30/'] == 0       \
    and ordenado['Capital Vigente 26/']     > 0:
        return 0
    else:
        return ordenado['Capital Vigente 26/']

ordenado['Capital Vigente 26/'] = ordenado.apply(caso_mediana_vencido2, axis=1)
###############################################################################
def caso_mediana_judicial1(ordenado):
    if ordenado['Tipo de Crédito 19/'] in ['06', '07', '08']    \
    and ordenado['Dias de Mora 33/']        > 15                \
    and ordenado['Capital Vencido 29/']     == 0                \
    and ordenado['Capital en Cobranza Judicial 30/'] > 0        \
    and ordenado['Capital Vigente 26/']     > 0:
        return ordenado['Capital Vigente 26/'] + ordenado['Capital en Cobranza Judicial 30/']
    else:
        return ordenado['Capital en Cobranza Judicial 30/']

ordenado['Capital en Cobranza Judicial 30/'] = ordenado.apply(caso_mediana_judicial1, axis=1)

def caso_mediana_judicial2(ordenado):
    if ordenado['Tipo de Crédito 19/'] in ['06', '07', '08']    \
    and ordenado['Dias de Mora 33/']        > 15                \
    and ordenado['Capital Vencido 29/']     == 0                \
    and ordenado['Capital en Cobranza Judicial 30/'] > 0        \
    and ordenado['Capital Vigente 26/']     > 0:
        return 0
    else:
        return ordenado['Capital Vigente 26/']

ordenado['Capital Vigente 26/'] = ordenado.apply(caso_mediana_judicial2, axis=1)

###############################################################################
def caso_mype_vencid1(ordenado):
    if ordenado['Tipo de Crédito 19/'] in ['09', '10']      \
    and ordenado['Dias de Mora 33/']        > 30            \
    and ordenado['Capital Vencido 29/']     > 0             \
    and ordenado['Capital en Cobranza Judicial 30/'] == 0   \
    and ordenado['Capital Vigente 26/']     > 0:
        return ordenado['Capital Vigente 26/'] + ordenado['Capital Vencido 29/']
    else:
        return ordenado['Capital Vencido 29/']
    
ordenado['Capital Vencido 29/'] = ordenado.apply(caso_mype_vencid1, axis=1)

def caso_mype_vencid2(ordenado):
    if ordenado['Tipo de Crédito 19/'] in ['09', '10']      \
    and ordenado['Dias de Mora 33/']        > 30            \
    and ordenado['Capital Vencido 29/']     > 0             \
    and ordenado['Capital en Cobranza Judicial 30/'] == 0   \
    and ordenado['Capital Vigente 26/']     > 0:
        return 0
    else:
        return ordenado['Capital Vigente 26/']

ordenado['Capital Vigente 26/'] = ordenado.apply(caso_mype_vencid2, axis=1)

###############################################################################
def caso_mype_judicial1(ordenado):
    if ordenado['Tipo de Crédito 19/'] in ['09', '10']      \
    and ordenado['Dias de Mora 33/']        > 30            \
    and ordenado['Capital Vencido 29/']     == 0            \
    and ordenado['Capital en Cobranza Judicial 30/'] > 0    \
    and ordenado['Capital Vigente 26/']     > 0:
        return ordenado['Capital Vigente 26/'] + ordenado['Capital en Cobranza Judicial 30/']
    else:
        return ordenado['Capital en Cobranza Judicial 30/']

ordenado['Capital en Cobranza Judicial 30/'] = ordenado.apply(caso_mype_judicial1, axis=1)

def caso_mype_judicial2(ordenado):
    if ordenado['Tipo de Crédito 19/'] in ['09', '10']      \
    and ordenado['Dias de Mora 33/']        > 30            \
    and ordenado['Capital Vencido 29/']     == 0            \
    and ordenado['Capital en Cobranza Judicial 30/'] > 0    \
    and ordenado['Capital Vigente 26/']     > 0:
        return 0
    else:
        return ordenado['Capital Vigente 26/']

ordenado['Capital Vigente 26/'] = ordenado.apply(caso_mype_judicial2, axis=1)

###############################################################################
def caso_consum_vencido1(ordenado):
    if ordenado['Tipo de Crédito 19/'] in ['11', '12', '13']\
    and ordenado['Dias de Mora 33/']        > 90            \
    and ordenado['Capital Vencido 29/']     >  0            \
    and ordenado['Capital en Cobranza Judicial 30/'] == 0   \
    and ordenado['Capital Vigente 26/']     > 0:
        return ordenado['Capital Vigente 26/'] + ordenado['Capital Vencido 29/']
    else:
        return ordenado['Capital Vencido 29/']

ordenado['Capital Vencido 29/'] = ordenado.apply(caso_consum_vencido1, axis=1)

def caso_consum_vencido2(ordenado):
    if ordenado['Tipo de Crédito 19/'] in ['11', '12', '13']\
    and ordenado['Dias de Mora 33/']        > 90            \
    and ordenado['Capital Vencido 29/']     > 0             \
    and ordenado['Capital en Cobranza Judicial 30/'] == 0   \
    and ordenado['Capital Vigente 26/']     > 0:
        return 0
    else:
        return ordenado['Capital Vigente 26/']

ordenado['Capital Vigente 26/'] = ordenado.apply(caso_consum_vencido2, axis=1)

###############################################################################
def caso_consum_judicial1(ordenado):
    if ordenado['Tipo de Crédito 19/'] in ['11', '12', '13']\
    and ordenado['Dias de Mora 33/']        > 90            \
    and ordenado['Capital Vencido 29/']     == 0            \
    and ordenado['Capital en Cobranza Judicial 30/'] > 0    \
    and ordenado['Capital Vigente 26/']     > 0:
        return ordenado['Capital Vigente 26/'] + ordenado['Capital en Cobranza Judicial 30/']
    else:
        return ordenado['Capital en Cobranza Judicial 30/']

ordenado['Capital en Cobranza Judicial 30/'] = ordenado.apply(caso_consum_judicial1, axis=1)

def caso_consum_judicial2(ordenado):
    if ordenado['Tipo de Crédito 19/'] in ['11', '12', '13']\
    and ordenado['Dias de Mora 33/']        > 90            \
    and ordenado['Capital Vencido 29/']     > 0             \
    and ordenado['Capital en Cobranza Judicial 30/'] == 0   \
    and ordenado['Capital Vigente 26/']     > 0:
        return 0
    else:
        return ordenado['Capital Vigente 26/']

ordenado['Capital Vigente 26/'] = ordenado.apply(caso_consum_judicial2, axis=1)

print(ordenado['Saldo de colocaciones (créditos directos) 24/'].sum())
print(ordenado['Capital Vigente 26/'].sum())
print(ordenado['Capital Vencido 29/'].sum())
print(ordenado['Capital en Cobranza Judicial 30/'].sum())
print(ordenado['Saldos de Créditos Castigados 38/'].sum())

#%% ajustecitos:
def jud_cap_real(ordenado):
    if  ordenado['Capital Vigente 26/']       == 0 \
    and ordenado['Capital Reestrucutado 27/'] == 0 \
    and ordenado['Capital Refinanciado 28/']  == 0 \
    and ordenado['Capital Vencido 29/']       == 0 \
    and ordenado['Saldos de Créditos Castigados 38/'] == 0 \
    and ordenado['Capital en Cobranza Judicial 30/'] < ordenado['Saldo de colocaciones (créditos directos) 24/']:
        return ordenado['Saldo de colocaciones (créditos directos) 24/']
    else:
        return ordenado['Capital en Cobranza Judicial 30/']

ordenado['Capital en Cobranza Judicial 30/'] = ordenado.apply(jud_cap_real, axis=1)
   
#%% VERIFICACIÓN DE QUE SE CUMPLA LA SUMA CORRECTAMENTE
suma_saldo_cartera = ordenado['Saldo de colocaciones (créditos directos) 24/'].sum()

suma_otros = ordenado['Capital Vigente 26/'].sum() + \
             ordenado['Capital Reestrucutado 27/'].sum() + \
             ordenado['Capital Refinanciado 28/'].sum() + \
             ordenado['Capital Vencido 29/'].sum() + \
             ordenado['Capital en Cobranza Judicial 30/'].sum()
             
#VERIFICAR QUE ESTA COMPARACIÓN SALGA TRUE
print('DEBE SALIR TRUE:') 
print(round(suma_saldo_cartera,2)  == round(suma_otros,2)) 

#%%
# k = ordenado[['Saldo de colocaciones (créditos directos) 24/',
#               'Capital Vigente 26/',
#               'Capital Reestrucutado 27/',
#               'Capital Refinanciado 28/',
#               'Capital Vencido 29/',
#               'Capital en Cobranza Judicial 30/']]
# k.to_excel('verificar.xlsx',
#            index = False)

#%% las 6 columnas azules de las reprogramaciones
#NUEVA PARTE IMPORTANTE DE ESTE REPORTE, AÑADIREMOS UNAS 6 COLUMNAS IMPORTANTES
ordenado['FEC_ULT_REPROG'] = ''
ordenado['PLAZO_REPR']     = ''
ordenado['TIPO_REPRO']     = ''
ordenado['PLAZO REPRO ACUMULADO']        = ''
ordenado['NRO CUOTAS REPROG CANCELADAS'] = ''
ordenado['NRO REPROG']     = ''

# CUIDADO AL AÑADIR COLUMNAS
columnas = list(ordenado.columns)
largo_6  = len(columnas) - 6

anx06_ordenado = ordenado[columnas[0:57]+['FEC_ULT_REPROG',
                                          'PLAZO_REPR',
                                          'TIPO_REPRO',
                                          'PLAZO REPRO ACUMULADO',
                                          'NRO CUOTAS REPROG CANCELADAS',
                                          'NRO REPROG'] + \
                          columnas[57:largo_6]]
    
#%% ahora a sacar datos del mes pasado
#los 3 primeros
anterior_para_merge = anx06_anterior[['Nro Prestamo \nFincore', 
                                      'FEC_ULT_REPROG', 
                                      'PLAZO_REPR', 
                                      'TIPO_REPRO']]

nuevos_nombres = {
    'Nro Prestamo \nFincore'  :   'fincore para merge',
    'FEC_ULT_REPROG'          :   'FEC_ULT_REPROG para merge',
    'PLAZO_REPR'              :   'PLAZO_REPR para merge',
    'TIPO_REPRO'              :   'TIPO_REPRO para merge'}

anterior_para_merge = anterior_para_merge.rename(columns=nuevos_nombres)
del nuevos_nombres

anx06_ordenado = anx06_ordenado.merge(anterior_para_merge, 
                         left_on=['Nro Prestamo \nFincore'], 
                         right_on=['fincore para merge']
                         ,how='left')

anx06_ordenado['FEC_ULT_REPROG'] = anx06_ordenado['FEC_ULT_REPROG para merge']
anx06_ordenado['PLAZO_REPR'] = anx06_ordenado['PLAZO_REPR para merge']
anx06_ordenado['TIPO_REPRO'] = anx06_ordenado['TIPO_REPRO para merge']

anx06_ordenado['FEC_ULT_REPROG'] = \
anx06_ordenado['FEC_ULT_REPROG'].fillna('--')

anx06_ordenado['PLAZO_REPR'] = \
anx06_ordenado['PLAZO_REPR'].fillna('--')

anx06_ordenado['TIPO_REPRO'] = \
anx06_ordenado['TIPO_REPRO'].fillna('--')

anx06_ordenado.drop(['fincore para merge',
                     'FEC_ULT_REPROG para merge',
                     'PLAZO_REPR para merge',
                     'TIPO_REPRO para merge'], axis=1, inplace=True)


#%% columnas 4, 5 y 6
#añadimos datos a la col 4
def col4(anx06_ordenado):
    if anx06_ordenado['TIPO_REPRO'] != '--':
        return anx06_ordenado['Nro Dias Gracia  Acumulado RPG TXT']
    else:
        return anx06_ordenado['PLAZO REPRO ACUMULADO']
anx06_ordenado['PLAZO REPRO ACUMULADO'] = anx06_ordenado.apply(col4, 
                                                               axis=1)

#añadimos datos a la col 5
def col5(anx06_ordenado):
    if anx06_ordenado['TIPO_REPRO'] != '--':
        return anx06_ordenado['Nro Cuotas Canc Post Regro']
    else:
        return anx06_ordenado['NRO CUOTAS REPROG CANCELADAS']
anx06_ordenado['NRO CUOTAS REPROG CANCELADAS'] = anx06_ordenado.apply(col5, 
                                                                      axis=1)

#añadimos datos a la col 6
def col6(anx06_ordenado):
    if anx06_ordenado['TIPO_REPRO'] != '--':
        return anx06_ordenado['Nro Reprogramaciones TXT']
    else:
        return anx06_ordenado['NRO REPROG']
anx06_ordenado['NRO REPROG'] = anx06_ordenado.apply(col6, 
                                                    axis=1)    

#%% REPROGRAMADOS DEL MES
#AÑADIENDO LOS REPROGRAMADOS DEL MES
columna = anx06_ordenado["Fecha Creacion Reprogramacion Nacimiento TXT"]
filas_no_nan = columna.count()

# PARSEANDO FECHAS
anx06_ordenado["Fecha Creacion Reprogramacion Nacimiento TXT"] = \
    pd.to_datetime(anx06_ordenado["Fecha Creacion Reprogramacion Nacimiento TXT"], dayfirst=True)

#contar las filas NO nulas
nuevo_conteo_filas = anx06_ordenado[~pd.isna(anx06_ordenado["Fecha Creacion Reprogramacion Nacimiento TXT"])].shape[0]

if filas_no_nan == nuevo_conteo_filas:
    print("Fecha Creacion Reprogramacion Nacimiento TXT")
    print('perfecto: ', filas_no_nan, ' y ', nuevo_conteo_filas)
else:
    print("Fecha Creacion Reprogramacion Nacimiento TXT")
    print('algo se ha perdido en el parseo: ', filas_no_nan ,' y ', nuevo_conteo_filas)
###############################################################################
#AÑADIENDO LOS REPROGRAMADOS DEL MES
columna = anx06_ordenado["Fecha Creacion Reprogramacion Corte TXT"]
filas_no_nan = columna.count()

# PARSEANDO FECHAS
anx06_ordenado["Fecha Creacion Reprogramacion Corte TXT"] = \
    pd.to_datetime(anx06_ordenado["Fecha Creacion Reprogramacion Corte TXT"], dayfirst=True)

#contar las filas NO nulas
nuevo_conteo_filas = anx06_ordenado[~pd.isna(anx06_ordenado["Fecha Creacion Reprogramacion Corte TXT"])].shape[0]

if filas_no_nan == nuevo_conteo_filas:
    print("Fecha Creacion Reprogramacion Corte TXT")
    print('perfecto: ', filas_no_nan, ' y ', nuevo_conteo_filas)
else:
    print("Fecha Creacion Reprogramacion Corte TXT")
    print('algo se ha perdido en el parseo: ', filas_no_nan ,' y ', nuevo_conteo_filas)
print('######################################################')
print(' también chequear que en ambas columnas salga igual')
print('######################################################')

#%% NUEVAS REPROGRAMACIONES
'##############################################################################'
#AÑADIENDO NUEVOS REPROGRAMADOS
#PONER AQUÍ EL INICIO DEL MES DE CORTE (es el dato que se solicita al principio)
mes_inicio = pd.to_datetime(fecha_corte_inicial)
#PONER AQUÍ EL FINAL DEL MES DE CORTE (es el dato que se solicita al principio)
mes_final = pd.to_datetime(fecha_corte)
'##############################################################################'

def nueva_fec_ult_reprog(anx06_ordenado):
    if (anx06_ordenado["Fecha Creacion Reprogramacion Nacimiento TXT"] >= mes_inicio) & \
    (anx06_ordenado["Fecha Creacion Reprogramacion Nacimiento TXT"] <= mes_final):
        return anx06_ordenado["Fecha Creacion Reprogramacion Corte TXT"]
    else:
        return anx06_ordenado['FEC_ULT_REPROG']
anx06_ordenado['FEC_ULT_REPROG'] = anx06_ordenado.apply(nueva_fec_ult_reprog, axis=1)
    
def nueva_plazo_reprog(anx06_ordenado):
    if (anx06_ordenado["Fecha Creacion Reprogramacion Nacimiento TXT"] >= mes_inicio) & \
    (anx06_ordenado["Fecha Creacion Reprogramacion Nacimiento TXT"] <= mes_final):
        return anx06_ordenado["Nro Dias Gracia Corte RPG TXT"]
    else:
        return anx06_ordenado['PLAZO_REPR']
anx06_ordenado['PLAZO_REPR'] = anx06_ordenado.apply(nueva_plazo_reprog, axis=1)

def nuevo_tipo_reprog(anx06_ordenado):
    if (anx06_ordenado["Fecha Creacion Reprogramacion Nacimiento TXT"] >= mes_inicio) & \
    (anx06_ordenado["Fecha Creacion Reprogramacion Nacimiento TXT"] <= mes_final):
        return anx06_ordenado["Tipo Reprogramacion TXT"]
    else:
        return anx06_ordenado['TIPO_REPRO']
anx06_ordenado['TIPO_REPRO'] = anx06_ordenado.apply(nuevo_tipo_reprog, axis=1)

#%%% indicaciones
#falta añadir las 3 columnas, pero para los nuevos

#%% COLUMNAS 4, 5 Y 6 NUEVAMNETE
#NUEVAMENTE añadimos datos a la col 4
def col4(anx06_ordenado):
    if (anx06_ordenado['TIPO_REPRO'] != '--') & \
    (anx06_ordenado['PLAZO REPRO ACUMULADO'] == ''):
        return anx06_ordenado['Nro Dias Gracia  Acumulado RPG TXT']
    else:
        return anx06_ordenado['PLAZO REPRO ACUMULADO']
anx06_ordenado['PLAZO REPRO ACUMULADO'] = anx06_ordenado.apply(col4, axis=1)

#añadimos datos a la col 5
def col5(anx06_ordenado):
    if (anx06_ordenado['TIPO_REPRO'] != '--') & \
    (anx06_ordenado['NRO CUOTAS REPROG CANCELADAS'] == ''):
        return anx06_ordenado['Nro Cuotas Canc Post Regro']
    else:
        return anx06_ordenado['NRO CUOTAS REPROG CANCELADAS']
anx06_ordenado['NRO CUOTAS REPROG CANCELADAS'] = anx06_ordenado.apply(col5, axis=1)

#añadimos datos a la col 6
def col6(anx06_ordenado):
    if (anx06_ordenado['TIPO_REPRO'] != '--') & \
    (anx06_ordenado['NRO REPROG'] == ''):
        return anx06_ordenado['Nro Reprogramaciones TXT']
    else:
        return anx06_ordenado['NRO REPROG']
anx06_ordenado['NRO REPROG'] = anx06_ordenado.apply(col6, axis=1)

#%% PARSEO DE FECHAS DE ÚLTIMA REPROGAMACIÓN
#arreglamos las fechas de la columna ['FEC_ULT_REPROG']
anx06_ordenado['FEC_ULT_REPROG'] = anx06_ordenado['FEC_ULT_REPROG'].astype(str)  # Convierte los valores en la columna 'c' a cadenas

formatos = ['%d/%m/%Y',
            '%Y-%m-%d %H:%M:%S']  # Lista de formatos a analizar
def parse_dates(date_str):
    for formato in formatos:
        try:
            return pd.to_datetime(date_str, format=formato)
        except ValueError:
            pass
    return pd.NaT

anx06_ordenado['FEC_ULT_REPROG'] = anx06_ordenado['FEC_ULT_REPROG'].apply(parse_dates)
anx06_ordenado['FEC_ULT_REPROG'] = anx06_ordenado['FEC_ULT_REPROG'].fillna('--')

#%% AÑADIMOS LA COLUMNA 'Relación Laboral con la Cooperativa 13/'
# esto también se hace en el código posterior, pero por si acaso lo hago desde aquí también
anx06_ordenado['Nombre PlanillaTXT'] = anx06_ordenado['Nombre PlanillaTXT'].str.strip()
anx06_ordenado['Nombre PlanillaTXT'] = anx06_ordenado['Nombre PlanillaTXT'].fillna('')

def creditos_administrativos(anx06_ordenado):
    if anx06_ordenado['Nombre PlanillaTXT'] in ['COOPERATIVA DE AHORRO Y CREDITO SAN MIGUEL LTDA.']:
        return '2'
    elif 'coopac san miguel' in anx06_ordenado['Nombre PlanillaTXT']: #este método no funciona cuando hay NaN en la columna
        return '2'
    else:
        return '0'

anx06_ordenado['Relación Laboral con la Cooperativa 13/'] = anx06_ordenado.apply(creditos_administrativos, axis=1)

#nos deben salir algunas filas
print(anx06_ordenado[anx06_ordenado['Relación Laboral con la Cooperativa 13/'] == '2']
      [['Apellidos y Nombres / Razón Social 2/','Nombre PlanillaTXT']])

print(str(anx06_ordenado[anx06_ordenado['Relación Laboral con la Cooperativa 13/'] == '2'].shape[0])  + ' filas')

# así comprobamos que ha funcionado

anx06_repro = anx06_ordenado.copy() #creando una copia para el reporte de reprogramados

#%% CRÉDITOS MENORES A 100 SOLES
'aquí se me han duplicado créditos alguna vez'
# CREACIÓN DE LA PESTAÑA DONDE ESTARÁN LOS CRÉDITOS CON CRÉDITOS MENORES A 100 SOLES

menores = anx06_ordenado[(anx06_ordenado['Saldo de colocaciones (créditos directos) 24/'] < 100) & \
                         (anx06_ordenado['Saldo de colocaciones (créditos directos) 24/'] > 0)]
menores = menores[['Código Socio 7/',
                   'Apellidos y Nombres / Razón Social 2/',
                   'Nro Prestamo \nFincore']]

# AÑADIMOS LA COLUMNITA DE CRÉDITOS MENORES AL PRINCIPIO
menores_para_merge = menores[['Código Socio 7/','Apellidos y Nombres / Razón Social 2/']]
menores_para_merge = menores_para_merge.rename(columns={'Código Socio 7/': "codigo merge"})
menores_para_merge = menores_para_merge.rename(columns={'Apellidos y Nombres / Razón Social 2/': 
                                                        "apellidos para eliminar"})
    
lista_columnas = list(anx06_ordenado.columns)

#eliminamos duplicados, porque el socio podría tener más de un crédito con menos de 100 soles
menores_para_merge = menores_para_merge.drop_duplicates(subset = "codigo merge")

anx06_ordenado = anx06_ordenado.merge(menores_para_merge, 
                                      left_on=['Código Socio 7/'], 
                                      right_on=["codigo merge"],
                                      how='left')

anx06_ordenado = anx06_ordenado.rename(columns={"codigo merge": "Socios al menos con un cred < 100 soles"})

anx06_ordenado = anx06_ordenado[["Socios al menos con un cred < 100 soles"] + lista_columnas]
anx06_ordenado["Socios al menos con un cred < 100 soles"] = anx06_ordenado["Socios al menos con un cred < 100 soles"].fillna("--")
anx06_ordenado = anx06_ordenado.rename(columns={"Socios al menos con un cred < 100 soles": 
'''Socios al menos con un cred < 100 soles
amarillo =  cred <100
rosado =  cred >= 100
 PROV.REQUERIDA A SER EVALUADA.'''})
 
#%% ELIMINACIÓN DE CRÉDITOS NO VIGENTES
#es decir , créditos que tengan E1 = 342 y E2 <= FECHA DE CORTE
anx06_ordenado['E1'] = anx06_ordenado['E1'].astype(int)
anx06_ordenado['E2'] = anx06_ordenado['E2'].astype(str)
formatos = ['%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S PM',
            '%Y-%m-%d %H:%M:%S AM',
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y',
            '%Y%m%d', '%Y-%m-%d',            
            '%Y/%m/%d %H:%M:%S',
            '%Y/%m/%d %H:%M:%S PM',
            '%Y/%m/%d %H:%M:%S AM']  # Lista de formatos a analizar

def parse_dates(date_str):
    for formato in formatos:
        try:
            return pd.to_datetime(date_str, format=formato)
        except ValueError:
            pass
    return pd.NaT

anx06_ordenado['E2'] = anx06_ordenado['E2'].apply(parse_dates)
#limpieza de las fechas en E2
def filtracion_E1_E2(anx06_ordenado):
    if (anx06_ordenado['E1'] == 342) & \
        (anx06_ordenado['E2'] <= pd.to_datetime(fecha_corte)):
        return 'cancelado'
    else:
        return 'vigente'
            
anx06_ordenado['vigentes??'] = anx06_ordenado.apply(filtracion_E1_E2, 
                                                    axis = 1)

anx06_ordenado = anx06_ordenado[anx06_ordenado['vigentes??'] == 'vigente']
anx06_ordenado.drop(['vigentes??'], 
                    axis = 1, 
                    inplace = True)

#VERIFICACIÓN
print(anx06_ordenado[~pd.isna(anx06_ordenado['E2'])]['E2']) #con esto podemos ver que solo queden créditos con cancelaciones posteriores a la fecha de corte

#%% COLUMNAS PARA CONTABILIDAD

anx06_ordenado['''fecha desemb (v)'''] = np.nan
anx06_ordenado['''fecha término de gracia por desembolso ["v" + dias gracia (av)]'''] = np.nan
anx06_ordenado['''periodo de gracia por Reprog inicio''']       = np.nan
anx06_ordenado['''periodo de gracia por Reprog Término''']      = np.nan
anx06_ordenado['''Fecha Venc de Ult Cuota Cancelada\n(NVO)''']  = np.nan

# COL 1
formatos = ['%d/%m/%Y',
            '%Y%m%d', '%Y-%m-%d',            
            '%Y/%m/%d %H:%M:%S',
            '%Y/%m/%d %H:%M:%S PM',
            '%Y/%m/%d %H:%M:%S AM',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S PM',
            '%Y-%m-%d %H:%M:%S AM',
            '%d/%m/%Y %H:%M:%S']  # Lista de formatos a analizar
def parse_dates(date_str):
    for formato in formatos:
        try:
            return pd.to_datetime(date_str, format=formato)
        except ValueError:
            pass
    return pd.NaT

anx06_ordenado['fecha desemb (v)'] = anx06_ordenado['Fecha de Desembolso 21/'].apply(parse_dates)

# COL 2 (tener cuidado con esta parte)
anx06_ordenado['Periodo de Gracia 47/'] = pd.to_numeric(anx06_ordenado['Periodo de Gracia 47/'])
anx06_ordenado['fecha desemb (v)'] = pd.to_datetime(anx06_ordenado['fecha desemb (v)'])

anx06_ordenado['''fecha término de gracia por desembolso ["v" + dias gracia (av)]'''] = \
    anx06_ordenado['''fecha desemb (v)'''] + pd.to_timedelta(anx06_ordenado['Periodo de Gracia 47/'], unit='D')

# print para verificar que haya funcionado, esta vaina está medio rara    
print(anx06_ordenado[['fecha desemb (v)', 
                      'fecha término de gracia por desembolso ["v" + dias gracia (av)]']])

#%% COL AMARILLA 3 y 4, primero datos del mes pasado

col3_4 = anx06_anterior[['Nro Prestamo \nFincore', 
                         'periodo de gracia por Reprog inicio', 
                         'periodo de gracia por Reprog Término']]

#cambio de nombre de las columnas para hacer un merge sin ambiguedades
col3_4 = col3_4.rename(columns={'Nro Prestamo \nFincore'                : "Fincore merge 3 y 4"})
col3_4 = col3_4.rename(columns={'periodo de gracia por Reprog inicio'   : "3 merge"})
col3_4 = col3_4.rename(columns={'periodo de gracia por Reprog Término'  : "4 merge"})

col3_4 = col3_4.drop_duplicates(subset = "Fincore merge 3 y 4") #por si acaso eliminamos duplicados antes del merge
#colocando los del mes pasado:
anx06_ordenado = anx06_ordenado.merge(col3_4, 
                                      left_on  = ['Nro Prestamo \nFincore'], 
                                      right_on = ["Fincore merge 3 y 4"],
                                      how      = 'left')
del col3_4
anx06_ordenado['periodo de gracia por Reprog inicio']  = anx06_ordenado["3 merge"]
anx06_ordenado['periodo de gracia por Reprog Término'] = anx06_ordenado["4 merge"]

anx06_ordenado.drop(["3 merge", #eliminación de columnas auxiliares que ya no sirven
                     "4 merge",
                     "Fincore merge 3 y 4"], 
                        axis    = 1, 
                        inplace = True)


# print(anx06_ordenado[(anx06_ordenado['periodo de gracia por Reprog inicio'] != '--') & \
#                      (pd.isna(anx06_ordenado['periodo de gracia por Reprog inicio']))]['periodo de gracia por Reprog inicio'])

#%%% columna 5
anx06_ordenado['''Fecha Venc de Ult Cuota Cancelada
(NVO)'''] = anx06_ordenado['Fecha Venc Ult Cuota Cancelada']

anx06_ordenado['periodo de gracia por Reprog inicio'] = \
    anx06_ordenado['periodo de gracia por Reprog inicio'].fillna('--')
anx06_ordenado['periodo de gracia por Reprog Término'] = \
    anx06_ordenado['periodo de gracia por Reprog Término'].fillna('--')

anx06_ordenado['''Fecha Venc de Ult Cuota Cancelada
(NVO)'''] = anx06_ordenado['''Fecha Venc de Ult Cuota Cancelada
(NVO)'''].fillna('--')

x = (anx06_ordenado[anx06_ordenado['periodo de gracia por Reprog inicio'] != '--']['periodo de gracia por Reprog inicio'])
# print(x.shape[0])
#hasta aquí todo bien

#%%% col amarillas 3 y 4

def col3_actuales(anx06_ordenado):
    if (anx06_ordenado["Fecha Creacion Reprogramacion Nacimiento TXT"] >= mes_inicio) & \
    (anx06_ordenado["Fecha Creacion Reprogramacion Nacimiento TXT"] <= mes_final):
        return anx06_ordenado['Fecha Primer Cuota Gracia Nacimiento RPG TXT'] - pd.to_timedelta(anx06_ordenado['Periodo de Gracia 47/'], unit='D')
    else:
        return anx06_ordenado['periodo de gracia por Reprog inicio']
    
anx06_ordenado['periodo de gracia por Reprog inicio'] = anx06_ordenado.apply(col3_actuales, axis=1)

print(anx06_ordenado[anx06_ordenado['periodo de gracia por Reprog inicio'] != '--'].shape[0])
print('para que esté bien, debe salir un número ligeramente menor cada mes')

def col4_actuales(anx06_ordenado):
    if (anx06_ordenado["Fecha Creacion Reprogramacion Nacimiento TXT"] >= mes_inicio) & \
    (anx06_ordenado["Fecha Creacion Reprogramacion Nacimiento TXT"] <= mes_final):
        return anx06_ordenado['Fecha Primer Cuota Gracia Nacimiento RPG TXT'] - pd.to_timedelta(anx06_ordenado['Periodo de Gracia 47/'], unit='D')
    else:
        return anx06_ordenado['periodo de gracia por Reprog Término']
    
anx06_ordenado['periodo de gracia por Reprog Término'] = anx06_ordenado.apply(col4_actuales, axis=1)

print(anx06_ordenado[anx06_ordenado['periodo de gracia por Reprog Término'] != '--'].shape[0])
print('para que esté bien, debe salir un número ligeramente menor cada mes')
print('Si sale igual, es porque no hubo reprogramaciones este mes, o faltó añadirlas (error en las fechas de inicio y fin establecidas)')
#aparentemente todo bien

#%%% 5ta columna amarilla

# hay que asegurarnos de que esta columna sea datetime 'Fecha Venc Ult Cuota Cancelada'

anx06_ordenado['Fecha Venc de Ult Cuota Cancelada\n(NVO)'] = anx06_ordenado['Fecha Venc Ult Cuota Cancelada']

anx06_ordenado['''Fecha Venc de Ult Cuota Cancelada
(NVO)'''] = anx06_ordenado['''Fecha Venc de Ult Cuota Cancelada
(NVO)'''].fillna('--')

#%% RECALCULACIÓN DE LA COLUMNA NRO REGISTRO 1/

# Obtener la cantidad total de filas en el DataFrame
total_filas = len(anx06_ordenado)

# Crear la nueva columna con la secuencia numérica
anx06_ordenado['Registro 1/'] = [f'{i+1:06}' for i in range(total_filas)]

#%% por si acaso, convertimos la fecha de desembolso en int

anx06_ordenado['Fecha de Desembolso 21/'] = anx06_ordenado['Fecha de Desembolso 21/'].astype(int)

#%% verificación de los intereses en suspenso y devengados

print(' ')
print('intereses en suspenso1:')
print(anx06_ordenado[columna_in_suspendo].sum())

print('intereses devengados1:')
print(anx06_ordenado[columna_devengados].sum())
print('suma total (1):')
print(round(anx06_ordenado[columna_in_suspendo].sum() + anx06_ordenado[columna_devengados].sum(),2))
val1_original = round(anx06_ordenado[columna_in_suspendo].sum() + anx06_ordenado[columna_devengados].sum(),2)

#%% intereses en Suspenso + Devengados en caso de que tengan cero cuotas canceladas y tengan >30 días
#se suman los intereses en suspenso y devengados

anx06_ordenado['Dias de Mora 33/'] = anx06_ordenado['Dias de Mora 33/'].astype(int)

def int_suspenso_y_devengados(anx06_ordenado):
    if (1 == 1) & \
    (anx06_ordenado['Tipo de Crédito 19/'] in ['08', 8]) & \
    (anx06_ordenado['Dias de Mora 33/'] > 15):
        return anx06_ordenado[columna_in_suspendo] + anx06_ordenado[columna_devengados]
    elif (1 == 1) & \
    (anx06_ordenado['Tipo de Crédito 19/'] in ['09', '10', '11', '12', '13', 9, 10, 11, 12, 13]) & \
    (anx06_ordenado['Dias de Mora 33/'] > 30):
        return anx06_ordenado[columna_in_suspendo] + anx06_ordenado[columna_devengados]
    else:
        return anx06_ordenado[columna_in_suspendo]

anx06_ordenado[columna_in_suspendo] = anx06_ordenado.apply(int_suspenso_y_devengados, axis=1)

anx06_ordenado[columna_devengados] = anx06_ordenado[columna_devengados].astype(float)

#se le pone cero a esos mismos devengados
def devengados_cero(anx06_ordenado):
    if (1 == 1) and \
    (anx06_ordenado['Tipo de Crédito 19/'] in ['08', 8]) and \
    (anx06_ordenado['Dias de Mora 33/'] > 15):
        return 0
    elif (1 == 1) and \
    (anx06_ordenado['Tipo de Crédito 19/'] in ['09', '10', '11', '12', '13', 9, 10, 11, 12, 13]) and \
    (anx06_ordenado['Dias de Mora 33/'] > 30):
        return 0
    else:
        return anx06_ordenado[columna_devengados]

anx06_ordenado[columna_devengados] = anx06_ordenado.apply(devengados_cero, axis=1)

print(' ')
print('intereses en suspenso2:')
print(anx06_ordenado[columna_in_suspendo].sum())
print('intereses devengados2:')
print(anx06_ordenado[columna_devengados].sum())
print('suma total (2):')
print(round(anx06_ordenado[columna_in_suspendo].sum() + anx06_ordenado[columna_devengados].sum(),2))
print('')
print('la suma total de (1) y (2) debe ser la misma')
val2_nuevo = round(anx06_ordenado[columna_in_suspendo].sum() + anx06_ordenado[columna_devengados].sum(),2)

if val1_original == val2_nuevo:
    print('todo bien')
else:
    print('difiere')

#%% ASIGNACIÓN DE LOS DEVENGADOS A LAS COLUMNAS QUE SÍ IRÁN EN EL ANEXO 06 PARA LA SBS
# con esto hemos modificado el rendimiento devengado (cero) y hemos colocado todo el interés en el int suspenso
anx06_ordenado['Rendimiento\nDevengado 40/'] = anx06_ordenado[columna_devengados].round(2)

print(anx06_ordenado['Rendimiento\nDevengado 40/'].sum())
# anx06_ordenado[['Rendimiento\nDevengado 40/', 'Intereses en Suspenso 41/',
#                 'Número de Cuotas Pagadas 45/',
#                 'Fecha de Desembolso 21/',
#                 'Flag Termino Periodo Gracia',
#                 'Nro Prestamo \nFincore',
#                 'Dias de Mora 33/']].to_excel('devengados1.xlsx', index = False)

anx06_ordenado['Intereses en Suspenso 41/'] = anx06_ordenado[columna_in_suspendo].round(2)

#%% cálculo extra de DEVENGADO 40/
# por solicitud de contabilidad (HELIO)
def ajuste_devengados(anx06_ordenado):
    saldo_cartera  = anx06_ordenado['Saldo de colocaciones (créditos directos) 24/']
    tasa_diaria    = (((1 + anx06_ordenado['Tasa de Interés Anual 23/'])**(1/360))-1)
    dias_devengado = (mes_final - anx06_ordenado['Fecha Termino \nPeriodo Gracia']).days
    
    if (anx06_ordenado['Número de Cuotas Pagadas 45/'] == 0) and \
       (anx06_ordenado['Fecha de Desembolso 21/'] >= 20230101) and \
       (anx06_ordenado['Flag Termino Periodo Gracia'] == 'SI'):
           
        return round(((saldo_cartera * ((1 + tasa_diaria)**dias_devengado)) - saldo_cartera), 2)
    else:
        return anx06_ordenado['Rendimiento\nDevengado 40/']
anx06_ordenado['Rendimiento\nDevengado 40/'] = anx06_ordenado.apply(ajuste_devengados, axis=1)

print(anx06_ordenado['Rendimiento\nDevengado 40/'].sum())

# anx06_ordenado[['Rendimiento\nDevengado 40/', 'Intereses en Suspenso 41/',
#                 'Número de Cuotas Pagadas 45/',
#                 'Fecha de Desembolso 21/',
#                 'Flag Termino Periodo Gracia',
#                 'Nro Prestamo \nFincore',
#                 'Dias de Mora 33/']].to_excel('devengados2.xlsx', index = False)

def flag_devengado_recalculado(anx06_ordenado):
    # saldo_cartera  = anx06_ordenado['Saldo de colocaciones (créditos directos) 24/']
    # tasa_diaria    = (((1 + anx06_ordenado['Tasa de Interés Anual 23/'])**(1/360))-1)
    # dias_devengado = (mes_final - anx06_ordenado['Fecha Termino \nPeriodo 0Gracia']).days
    
    if (anx06_ordenado['Número de Cuotas Pagadas 45/'] == 0) and \
       (anx06_ordenado['Fecha de Desembolso 21/'] >= 20230101) and \
       (anx06_ordenado['Flag Termino Periodo Gracia'] == 'SI'):
           
        return 'si'
    else:
        return ''
anx06_ordenado['Flag Devengado Recalculado'] = anx06_ordenado.apply(ajuste_devengados, axis = 1)

#%% CORRIGIENDO SI EL NUEVO INTERÉS DEVENGADO EXISTE A LA VEZ QUE EL INTERÉS EN SUSPENSO
# EN ESTE CASO SE REEMPLAZA EL INTERÉS EN SUSPENSO POR EL INTERÉS DEVENGADO
# Y SE PONE INTERÉS DEVENGADO EN CERO

def suspenso_flag(anx06_ordenado): #(anx06_ordenado['Flag Devengado Recalculado'] == 'si') and \
    if (1 == 1) and \
       (anx06_ordenado['Rendimiento\nDevengado 40/'] > 0) and \
       (anx06_ordenado['Intereses en Suspenso 41/'] > 0):
        return 'si'
    else:
        return ''
anx06_ordenado['Flag Suspenso Recalculado'] = anx06_ordenado.apply(suspenso_flag, axis = 1)

def suspenso_recalculado(anx06_ordenado):
    if anx06_ordenado['Flag Suspenso Recalculado'] == 'si':
        return anx06_ordenado['Rendimiento\nDevengado 40/']
    else:
        return anx06_ordenado['Intereses en Suspenso 41/']
anx06_ordenado['Intereses en Suspenso 41/'] = anx06_ordenado.apply(suspenso_recalculado, axis = 1)

def devengado_cero(anx06_ordenado):
    if ((anx06_ordenado['Flag Suspenso Recalculado'] == 'si') and \
       (anx06_ordenado['Intereses en Suspenso 41/'] > 0))     or  \
       (anx06_ordenado['Refinanciado TXT'] == 'REFINANCIADO'):
        return 0
    else:
        return anx06_ordenado['Rendimiento\nDevengado 40/']
anx06_ordenado['Rendimiento\nDevengado 40/'] = anx06_ordenado.apply(devengado_cero, axis = 1)

print(anx06_ordenado[(anx06_ordenado['Rendimiento\nDevengado 40/'] >0) & (anx06_ordenado['Intereses en Suspenso 41/'] >0)])

print(anx06_ordenado['Rendimiento\nDevengado 40/'].sum())

# anx06_ordenado[['Rendimiento\nDevengado 40/', 'Intereses en Suspenso 41/',
#                 'Número de Cuotas Pagadas 45/',
#                 'Fecha de Desembolso 21/',
#                 'Flag Termino Periodo Gracia',
#                 'Nro Prestamo \nFincore',
#                 'Dias de Mora 33/']].to_excel('devengados3.xlsx', index = False)

#%% por si acaso, eliminamos duplicados ( ´･･)ﾉ(._.`)
print(anx06_ordenado.shape[0])
anx06_ordenado = anx06_ordenado.drop_duplicates(subset = 'Nro Prestamo \nFincore') #por si acaso eliminamos duplicados
print(anx06_ordenado.shape[0])
print('si sale menos, es porque hubo duplicados')

#%% CONTEO DE 
DEBE_SER_CERO = anx06_ordenado

#%% ORDENAMIENTO DE LAS COLUMNAS LAS ÚLTIMAS 5 AÑADIDAS PARA CONTABILIDAD
'#############################################################################'
columnas  = anx06_ordenado.columns
largo_fin = len(columnas) - 5

columnas_ordenadas = list(columnas[0:64]) + ['fecha desemb (v)',
                                             'fecha término de gracia por desembolso ["v" + dias gracia (av)]', #esta columna se está duplicando
                                             'periodo de gracia por Reprog inicio',
                                             'periodo de gracia por Reprog Término',
                                             'Fecha Venc de Ult Cuota Cancelada\n(NVO)'] + list(columnas[64:largo_fin])

anx06_ordenado = anx06_ordenado[columnas_ordenadas]

#%% AÑADIENDO MODIFICACIONES A LAS COLUMNAS 52, 53, 54, 55

anx06_ordenado['9/MDREPRP/ Modalidad de reprogramación']  = anx06_ordenado["TIPO_REPRO"]

anx06_ordenado['9/MDREPRP/ Modalidad de reprogramación'] = anx06_ordenado['9/MDREPRP/ Modalidad de reprogramación'].map(
                                                                          {"TIPO 1": '1', #REEMPLAZANDO LOS VALORES
                                                                           "TIPO 2": '2',
                                                                           "TIPO 3": '1'},
                                                                           na_action = None) #EN CASO DE NULO NO HACER NADA

anx06_ordenado["FEC_ULT_REPROG2"] = pd.to_datetime(anx06_ordenado["FEC_ULT_REPROG"], 
                                                   errors='coerce')

def correccion_modalidad_repro(anx06_ordenado):
    if anx06_ordenado["FEC_ULT_REPROG2"] >= pd.Timestamp('2023-01-01'):
        return '3'
    else:
        return anx06_ordenado['9/MDREPRP/ Modalidad de reprogramación']

anx06_ordenado['9/MDREPRP/ Modalidad de reprogramación'] = anx06_ordenado.apply(correccion_modalidad_repro, 
                                                                                axis=1)

#%%% COLUMNA 52/

print(anx06_ordenado['TIPO_REPRO'].unique())
def calculo_52(anx06_ordenado):
    if anx06_ordenado['TIPO_REPRO'] != '--': 
        return anx06_ordenado['Saldo de colocaciones (créditos directos) 24/']
    else:
        return 0

anx06_ordenado['Saldo Capital de Créditos Reprogramados 52/'] = anx06_ordenado.apply(calculo_52, 
                                                                                     axis=1)

anx06_ordenado['Saldo Capital de Créditos Reprogramados 52/'] = anx06_ordenado['Saldo Capital de Créditos Reprogramados 52/'].round(2)
# print(anx06_ordenado['Saldo Capital de Créditos Reprogramados 52/'].sum())
suma_saldo_reprogramados = anx06_ordenado['Saldo Capital de Créditos Reprogramados 52/'].sum()

#%% COLUMNA 53/
def calculo_53(anx06_ordenado):
    if anx06_ordenado['9/MDREPRP/ Modalidad de reprogramación'] in ['1', '2']:
        return anx06_ordenado['Saldo de colocaciones (créditos directos) 24/']
    else:
        return 0

anx06_ordenado['Saldo Capital en Cuenta de Orden por efecto del Covid 53/'] = anx06_ordenado.apply(calculo_53, 
                                                                                                   axis = 1)

anx06_ordenado['Saldo Capital en Cuenta de Orden por efecto del Covid 53/'] = 0 # desactivar esta línea si queremos volver a calcular

#%% COLUMNA 54/
def calculo_54(anx06_ordenado): #probar esta vaina
    if anx06_ordenado['Saldo de Créditos que no cuentan con cobertura 51/'] > 0 or \
        anx06_ordenado['Saldo Capital de Créditos Reprogramados 52/'] > 0:
        if anx06_ordenado['9/MDREPRP/ Modalidad de reprogramación'] in ['1', '2']:
            return '8109240000'
        elif anx06_ordenado['9/MDREPRP/ Modalidad de reprogramación'] in ['3']:
            return '8109230000'
        else:
            return None
    else:
        return None
    
anx06_ordenado['Subcuenta de orden \n54/\n'] = anx06_ordenado.apply(calculo_54,
                                                                    axis = 1)

#%% COLUMNA 55/
def calculo_55(anx06_ordenado):
    if anx06_ordenado['9/MDREPRP/ Modalidad de reprogramación'] in ['1', '2']:
        return anx06_ordenado[columna_devengados]
    else:
        return None

anx06_ordenado['Rendimiento Devengado por efecto del COVID 19 55/'] = anx06_ordenado.apply(calculo_55,
                                                                                           axis = 1)

anx06_ordenado['Rendimiento Devengado por efecto del COVID 19 55/'] = 0 # desactivar esta línea si queremos volver a calcular

#%% Reemplazar solo el ';' por una cadena vacía en la columna 'Domicilio 12/' 
anx06_ordenado['Domicilio 12/'] = anx06_ordenado['Domicilio 12/'].str.replace(';', '', regex = False)

#%% ALERTA, SI EL CRÉDITO TIENE TIPO DE CRÉDITO 12 (CONSUMO NO REVOLVENTE)
# Y AL MISMO TIEMPO TIENE GARANTÍAS PREFERIDAS, NO DEBE TENER

alertaaa = anx06_ordenado[(anx06_ordenado['Tipo de Crédito 19/'] == '12') & \
                          (anx06_ordenado['Saldos de Garantías Preferidas 34/'] > 0)]

if alertaaa.shape[0] > 0:
    print('ALERTAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 🚨🚨🚨🚨')
    print(alertaaa['Nro Prestamo \nFincore'])
else:
    print('todo bien q(≧▽≦q)')

#%% corrigiendo por si acaso    
anx06_ordenado.loc[(anx06_ordenado['Apellidos y Nombres / Razón Social 2/'] == 'BRICENO PAJUELO JAIME GUILLERMO') & \
                   (anx06_ordenado['Nro Prestamo \nFincore'] == '00021989'), 
                   'Tipo de Crédito 19/'] = '09'
    
alertaaa = anx06_ordenado[(anx06_ordenado['Tipo de Crédito 19/'] == '12') & \
                          (anx06_ordenado['Saldos de Garantías Preferidas 34/'] > 0)]
    
if alertaaa.shape[0] > 0:
    print(Back.RED + 'ALERTAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 🚨🚨🚨🚨')
    print('Un Tipo 12 NO puede tener garantía preferida')
    # no hay espacio en el Anexo 05 para que un tipo 12 ponga el monto de la garantía preferida, haciendo imposible subir el anexo 05
else:
    print(Back.GREEN + 'todo bien q(≧▽≦q)')

#%% CREACIÓN DEL EXCEL
df_vacío = pd.DataFrame({' ' : ['', '', ''], 
                         '  ': ['', '', '']})

nombre = f'Rpt_DeudoresSBS Anexo06 - {fecha_mes} - campos ampliados procesado 01.xlsx'
if generar_excels == True:
    
    try:
        ruta = nombre
        os.remove(ruta)
    except FileNotFoundError:
        pass
    df_vacío.to_excel(ruta,
                      index = False)
else:
    pass

##################### ESCRIBIMOS EN ESE EXCEL VACÍO #####################

# Crear un objeto ExcelWriter y especificar el archivo de salida
excel_writer = pd.ExcelWriter(nombre)

# Guardar cada DataFrame en una hoja (sheet) diferente
anx06_ordenado.to_excel(excel_writer, 
                        sheet_name = fecha_mes, 
                        index = False) ##

menores.to_excel(excel_writer, 
                 sheet_name = 'socios con cred < 100 soles', 
                 index = False)

# Guardar los cambios y cerrar el objeto ExcelWriter
excel_writer.save()
excel_writer.close()

#%% FILTRADO DE CRÉDITOS REPROGRAMADOS
anx06_repro = anx06_ordenado.copy()
#filtramos créditos reprogramados NO castigados
reprogramados = anx06_repro[(anx06_repro['TIPO_REPRO'] != '--') & \
                            (anx06_repro['Saldos de Créditos Castigados 38/'] == 0)]

print(suma_saldo_reprogramados)
print(reprogramados['Saldo de colocaciones (créditos directos) 24/'].sum())

#%% pequeña alerta detectada
investigar = reprogramados[pd.isna(reprogramados['TIPO_REPRO'])]

print(investigar.shape[0])
print('debe salir cero, sino investigar (falta tipo de reprogramación)')
print(investigar['Nro Prestamo \nFincore'])

#%% CREACIÓN DEL EXCEL DE REPROGRAMADOS
if generar_excels == True:

    try:
        ruta = f'Rpt_DeudoresSBS Créditos Reprogramados {fecha_mes} no incluye castigados.xlsx'
        os.remove(ruta)
    except FileNotFoundError:
        pass

    reprogramados.to_excel(ruta,
                           index=False)
else:
    pass

ubicacion_actual = os.getcwd()

# Imprimir la ubicación actual
print("La ubicación actual es: " + ubicacion_actual)

#%%
# =============================================================================
# 
# #%% VERIFICACIONES ADICIONALES, CRÉDITOS QUE APARECIERON ESTE MES PERO NO EN ALGÚN MES ANTERIOR
# 
# =============================================================================
###############################################################################
######     verificamos si algún crédito no apareció el mes pasado        ######
###############################################################################
import pyodbc

df_mes_actual_copia #original antes de procesarlo

conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')
#donde dice @fechacorte se debe poner el mes

# FECHAS EN FORMATO SQL =======================================================
fecha_corte_actual  = '20240731' #mes actual
fecha_corte_menos_1 = '20240630' #mes anterior
fecha_corte_menos_2 = '20240531' #mes anterior del anterior
# =============================================================================

#%%
query_sql = f'''
SELECT 
	FechaCorte1 as 'FECHA CORTE',
	Nro_Fincore AS 'NRO FINCORE',
	ApellidosyNombresRazonSocial2 AS 'SOCIO',
	Saldodecolocacionescreditosdirectos24 AS 'SALDO CARTERA'
FROM 
	anexos_riesgos2..Anx06_preliminar
WHERE FechaCorte1 = '{fecha_corte_menos_1}' --SE PONE LA DE HACE 3 MESES'''

df_menos1 = pd.read_sql_query(query_sql, conn)

query_sql = f'''
SELECT 
	FechaCorte1 as 'FECHA CORTE',
	Nro_Fincore AS 'NRO FINCORE',
	ApellidosyNombresRazonSocial2 AS 'SOCIO',
	Saldodecolocacionescreditosdirectos24 AS 'SALDO CARTERA'
FROM 
	anexos_riesgos2..Anx06_preliminar
WHERE FechaCorte1 = '{fecha_corte_menos_2}' --SE PONE LA DE HACE 3 MESES'''

df_menos2 = pd.read_sql_query(query_sql, conn)
del conn  #para limpiar el explorador de variables

#%% créditos que aparecen hace 2 meses, pero NO el més pasado

creditos_en_3_meses = df_mes_actual_copia.loc[df_mes_actual_copia['Nro Prestamo \nFincore'].str.strip().isin(list(df_menos2['NRO FINCORE'].str.strip()))]

creditos_no_aparecidos = creditos_en_3_meses[~creditos_en_3_meses['Nro Prestamo \nFincore'].str.strip().isin(list(df_menos1['NRO FINCORE'].str.strip()))]

print(creditos_no_aparecidos)
print(creditos_no_aparecidos['Nro Prestamo \nFincore'])
#%% ahora vamos a buscar respecto al excel original antes de eliminar los cancelados
'FILTRAMOS AQUELLOS CRÉDITOS QUE TENGAN FECHA DE DESEMBOLSO DE HACE DOS MESES AL CORTE ACTUAL'
antiguos_aparecen = df_mes_actual_copia[df_mes_actual_copia['Fecha de Desembolso 21/'].astype(int) <= int(fecha_corte_menos_2)]

no_aparecen = antiguos_aparecen[~antiguos_aparecen['Nro Prestamo \nFincore'].str.strip().isin(list(df_menos1['NRO FINCORE'].str.strip()))]

para_reporte = no_aparecen[['Registro 1/', 'Apellidos y Nombres / Razón Social 2/',
                            'Nro Prestamo \nFincore', 'Saldo de colocaciones (créditos directos) 24/']]

#%% ahora vamos a buscar respecto al anexo06 final
'FILTRAMOS AQUELLOS CRÉDITOS QUE TENGAN FECHA DE DESEMBOLSO DE HACE DOS MESES AL CORTE ACTUAL'
antiguos_aparecen = anx06_ordenado[anx06_ordenado['Fecha de Desembolso 21/'].astype(int) <= int(fecha_corte_menos_2)]

no_aparecen = antiguos_aparecen[~antiguos_aparecen['Nro Prestamo \nFincore'].str.strip().isin(list(df_menos1['NRO FINCORE'].str.strip()))]

para_reporte = no_aparecen[['Registro 1/', 'Apellidos y Nombres / Razón Social 2/',
                            'Nro Prestamo \nFincore', 'Saldo de colocaciones (créditos directos) 24/']]

print(para_reporte)
print('este dataframe debe salir vacío, sino hay que reportarlo a Cesar, son créditos que han aparecido')

#%%
# =========================================================================== #
# =========================================================================== #
#             🅱🆁🅴🅲🅷🅰🆂 🅳🅴 🆁🅴🅿🆁🅾🅶🆁🅰🅼🅰🅲🅸🅾🅽🅴🆂                     #
# =========================================================================== #
# =========================================================================== #

import pandas as pd
import os

#%%
# REPROGRAMADOS ACTUALES SI ES QUE CONTINUAMOS EN LA MISMA SESIÓN =============
actual = reprogramados.copy()
# =============================================================================

# REPROGRAMADOS ACTUALES (si ya no tenemos abierto el dataframe reprogramados)=
# repro_actual   = 'Rpt_DeudoresSBS Créditos Reprogramados Febrero 2024 no incluye castigados NUEVO.xlsx'
# ubi_actual     = 'C:\\Users\\sanmiguel38\\Desktop\\REPORTE DE REPROGRAMADOS (primer paso del anexo06)\\2024\\2024 FEB\\producto verdadero'
# =============================================================================

# REPROGRAMADOS DEL MES PASADO ================================================
repro_anterior = 'Rpt_DeudoresSBS Créditos Reprogramados Junio 2024 no incluye castigados.xlsx'
ubi_anterior   = 'C:\\Users\\sanmiguel38\\Desktop\\REPORTE DE REPROGRAMADOS (primer paso del anexo06)\\2024\\2024 junio\\productos'
# =============================================================================

# NOMBRES PARA LAS COLUMNA DEL REPORTE ========================================
mes_actual_txt   = 'Jul-24'
mes_anterior_txt = 'Jun-24'
# =============================================================================
#%% LECTURA

# Lectura de los archivos de reprogramados

# descomentamos este fragmento de código si es que no estamos continuando con el reporte de reprogramados
# os.chdir(ubi_actual)
# actual = pd.read_excel(ubi_actual + '\\' + repro_actual,
#                         skiprows = 2,
#                         dtype = {'Tipo de Crédito 19/'   : str,
#                                 'Nro Prestamo \nFincore': str})
# =============================================================================

anterior = pd.read_excel(ubi_anterior + '\\' + repro_anterior,
                         skiprows = 2,
                         dtype = {'Tipo de Crédito 19/'   : str,
                                  'Nro Prestamo \nFincore': str})

#%% FILTRADO DE COLUMNAS
columnas = ['Tipo de Crédito 19/',
            'PLAZO_REPR',
            'TIPO_REPRO',
            'Saldo de colocaciones (créditos directos) 24/',
            'Nro Prestamo \nFincore']

actual   = actual[columnas]
anterior = anterior[columnas]

actual['Tipo de Crédito 19/'] = actual['Tipo de Crédito 19/'].astype(str).str.strip()
anterior['Tipo de Crédito 19/'] = anterior['Tipo de Crédito 19/'].astype(str).str.strip()

#%% COLUMNAS AUXILIARES PARA REALIZAR LA TABLA PIVOT
def tipo_credito(df):
    if df['Tipo de Crédito 19/'] in ['06', '07', '08', '6', '7', '8', 6, 7, 8]:
        return 'No minorista'
    elif df['Tipo de Crédito 19/'] in ['09' , '9', 9]:
        return 'Pequeña Empresa'
    elif df['Tipo de Crédito 19/'] in ['10', 10]:
        return 'Microempresa'
    elif df['Tipo de Crédito 19/'] in ['11', 11]:
        return 'Consumo Revolvente'
    elif df['Tipo de Crédito 19/'] in ['12', 12]:
        return 'Consumo No Revolvente'
    elif df['Tipo de Crédito 19/'] in ['13', 13]:
        return 'Hipotecario'
    else:
        return 'investigar caso'

actual['Tipo de Crédito'] = actual.apply(tipo_credito, axis=1)
anterior['Tipo de Crédito'] = anterior.apply(tipo_credito, axis=1)

def dias_plazo(df):
    if df['PLAZO_REPR']   <= 60:
        return '60 días'
    elif df['PLAZO_REPR'] <= 90:
        return '90 días'
    elif df['PLAZO_REPR'] <= 120:
        return '120 días'
    elif df['PLAZO_REPR'] <= 180:
        return '180 días'
    elif df['PLAZO_REPR'] >  180:
        return 'Más de 180 días'
    
actual['Plazo'] = actual.apply(dias_plazo, axis=1)

anterior['PLAZO_REPR'] = pd.to_numeric(anterior['PLAZO_REPR'], errors='coerce')
anterior['Plazo'] = anterior.apply(dias_plazo, axis=1)

#%% Listas para el ordenamiento de los índices
credito_lista = ['No minorista',
                 'Pequeña Empresa',
                 'Microempresa',
                 #'Consumo Revolvente',
                 'Consumo No Revolvente',
                 'Hipotecario',
                 'Total']

plazo_lista = ['60 días',
               '90 días',
               '120 días',
               '180 días',
               'Más de 180 días',
               'Total']

repro_lista = ['TIPO 1',
               'TIPO 2',
               'TIPO 3',
               'Total']

#%% PIVOT TABLES TABLAS ACTUALES
NUEVO_NOMBRE_FINCORE = 'Nro. Operaciones'
NUEVO_NOMBRE_SALDO   = 'Saldo Cartera'

actual.rename(columns ={'Nro Prestamo \nFincore': NUEVO_NOMBRE_FINCORE},
              inplace = True)
actual.rename(columns ={'Saldo de colocaciones (créditos directos) 24/': NUEVO_NOMBRE_SALDO},
              inplace = True)
anterior.rename(columns ={'Nro Prestamo \nFincore': NUEVO_NOMBRE_FINCORE},
              inplace = True)
anterior.rename(columns ={'Saldo de colocaciones (créditos directos) 24/': NUEVO_NOMBRE_SALDO},
              inplace = True)

actual_tipo_credito = actual.pivot_table(#columns = ,
                                         values  = [NUEVO_NOMBRE_SALDO,
                                                    NUEVO_NOMBRE_FINCORE],
                                         index   = 'Tipo de Crédito',
                                         margins = True,
                                         margins_name = 'Total',
                                         aggfunc = {NUEVO_NOMBRE_SALDO : 'sum',
                                                    NUEVO_NOMBRE_FINCORE : 'count'}
                                        )
actual_tipo_credito = actual_tipo_credito[[NUEVO_NOMBRE_SALDO,
                                           NUEVO_NOMBRE_FINCORE]]

actual_tipo_credito = actual_tipo_credito.reindex(credito_lista).loc[credito_lista].fillna(0)
# =============================================================================
actual_plazo = actual.pivot_table(#columns = ,
                                  values  = [NUEVO_NOMBRE_SALDO,
                                             NUEVO_NOMBRE_FINCORE],
                                  index   = 'Plazo',
                                  margins = True,
                                  margins_name = 'Total',
                                  aggfunc = {NUEVO_NOMBRE_SALDO : 'sum',
                                             NUEVO_NOMBRE_FINCORE : 'count'}
                                 )
actual_plazo = actual_plazo[[NUEVO_NOMBRE_SALDO,
                             NUEVO_NOMBRE_FINCORE]]

actual_plazo = actual_plazo.reindex(plazo_lista).loc[plazo_lista].fillna(0)
# =============================================================================
actual_tipo_repro = actual.pivot_table(#columns = ,
                                       values  = [NUEVO_NOMBRE_SALDO,
                                                  NUEVO_NOMBRE_FINCORE],
                                       index   = 'TIPO_REPRO',
                                       margins = True,
                                       margins_name = 'Total',
                                       aggfunc = {NUEVO_NOMBRE_SALDO : 'sum',
                                                  NUEVO_NOMBRE_FINCORE : 'count'}
                                      )
actual_tipo_repro = actual_tipo_repro[[NUEVO_NOMBRE_SALDO,
                                       NUEVO_NOMBRE_FINCORE]]

actual_tipo_repro = actual_tipo_repro.reindex(repro_lista).loc[repro_lista].fillna(0)

#%% PIVOT TABLES TABLAS ANTERIORES
anterior_tipo_credito = anterior.pivot_table(#columns = ,
                                             values  = [NUEVO_NOMBRE_SALDO,
                                                        NUEVO_NOMBRE_FINCORE],
                                             index   = 'Tipo de Crédito',
                                             margins = True,
                                             margins_name = 'Total',
                                             aggfunc = {NUEVO_NOMBRE_SALDO : 'sum',
                                                        NUEVO_NOMBRE_FINCORE : 'count'}
                                             )
anterior_tipo_credito = anterior_tipo_credito[[NUEVO_NOMBRE_SALDO,
                                               NUEVO_NOMBRE_FINCORE]]
anterior_tipo_credito = anterior_tipo_credito.reindex(credito_lista).loc[credito_lista].fillna(0)
# =============================================================================
anterior_plazo = anterior.pivot_table(#columns = ,
                                      values  = [NUEVO_NOMBRE_SALDO,
                                                 NUEVO_NOMBRE_FINCORE],
                                      index   = 'Plazo',
                                      margins = True,
                                      margins_name = 'Total',
                                      aggfunc = {NUEVO_NOMBRE_SALDO : 'sum',
                                                 NUEVO_NOMBRE_FINCORE : 'count'}
                                      )
anterior_plazo = anterior_plazo[[NUEVO_NOMBRE_SALDO,
                                 NUEVO_NOMBRE_FINCORE]]
anterior_plazo = anterior_plazo.reindex(plazo_lista).loc[plazo_lista].fillna(0)
# =============================================================================
anterior_tipo_repro = anterior.pivot_table(#columns = ,
                                           values  = [NUEVO_NOMBRE_SALDO,
                                                      NUEVO_NOMBRE_FINCORE],
                                           index   = 'TIPO_REPRO',
                                           margins = True,
                                           margins_name = 'Total',
                                           aggfunc = {NUEVO_NOMBRE_SALDO : 'sum',
                                                      NUEVO_NOMBRE_FINCORE : 'count'}
                                           )
anterior_tipo_repro = anterior_tipo_repro[[NUEVO_NOMBRE_SALDO,
                                           NUEVO_NOMBRE_FINCORE]]
anterior_tipo_repro = anterior_tipo_repro.reindex(repro_lista).loc[repro_lista].fillna(0)

#%% resta de la variación en los 
# =============================================================================
dif_credi = actual_tipo_credito - anterior_tipo_credito
dif_plazo = actual_plazo        - anterior_plazo
dif_repro = actual_tipo_repro   - anterior_tipo_repro
# =============================================================================

# =============================================================================
# #%% CREACIÓN DEL EXCEL
writer = pd.ExcelWriter(f'BRECHAS DE REPROGRAMADOS {mes_actual_txt}.xlsx', engine='xlsxwriter')
# =============================================================================
sheet = 'BrechasReprogramados'
fila_inicial = 3

anterior_tipo_credito.to_excel(writer,
                               sheet_name = sheet, 
                               startrow   = fila_inicial, 
                               startcol   = 0, 
                               index      = True)
# este cuadro de texto solo funciona si va debajo del código anterior (ಠಿ_ಠ)
writer.sheets[sheet].write(0, #número de fila
                           1, #número de columna
                           f'{mes_anterior_txt}')
writer.sheets[sheet].write(1, #número de fila
                           0, #número de columna
                           'Cuadro N°1: Reprogramaciones por Tipo de Crédito')

anterior_plazo.to_excel(writer,
                        sheet_name = sheet, 
                        startrow   = anterior_tipo_credito.shape[0] + fila_inicial + 3, 
                        startcol   = 0, 
                        index      = True)
writer.sheets[sheet].write(anterior_tipo_credito.shape[0] + fila_inicial + 2, #número de fila
                           0, #número de columna
                           'Cuadro N°2: Reprogramaciones según plazo')

anterior_tipo_repro.to_excel(writer,
                             sheet_name = sheet, 
                             startrow   = anterior_tipo_credito.shape[0] + anterior_plazo.shape[0] + fila_inicial + 6, 
                             startcol   = 0, 
                             index      = True)
writer.sheets[sheet].write(anterior_tipo_credito.shape[0] + anterior_plazo.shape[0] + fila_inicial + 5, #número de fila
                           0, #número de columna
                           'Cuadro N°3: Reprogramaciones según tipo de rprogramación')
# =============================================================================
actual_tipo_credito.to_excel(writer, 
                             sheet_name = sheet, 
                             startrow   = fila_inicial, 
                             startcol   = 4, 
                             index      = True)
writer.sheets[sheet].write(0, #número de fila
                           5, #número de columna
                           f'{mes_actual_txt}')
writer.sheets[sheet].write(1, #número de fila
                           4, #número de columna
                           'Cuadro N°1: Reprogramaciones por Tipo de Crédito')

actual_plazo.to_excel(writer, 
                      sheet_name = sheet, 
                      startrow   = actual_tipo_credito.shape[0] + fila_inicial + 3, 
                      startcol   = 4, 
                      index      = True)
writer.sheets[sheet].write(anterior_tipo_credito.shape[0] + fila_inicial + 2, #número de fila
                           4, #número de columna
                           'Cuadro N°2: Reprogramaciones según plazo')

actual_tipo_repro.to_excel(writer, 
                           sheet_name = sheet, 
                           startrow   = actual_tipo_credito.shape[0] + actual_plazo.shape[0]+ fila_inicial + 6, 
                           startcol   = 4, 
                           index      = True)
writer.sheets[sheet].write(anterior_tipo_credito.shape[0] + anterior_plazo.shape[0] + fila_inicial + 5, #número de fila
                           4, #número de columna
                           'Cuadro N°3: Reprogramaciones según tipo de rprogramación')

# =============================================================================
dif_credi.to_excel(writer, 
                   sheet_name = sheet, 
                   startrow   = fila_inicial, 
                   startcol   = 8, 
                   index      = True)
writer.sheets[sheet].write(1, #número de fila
                           9, #número de columna
                           'DIFERENCIAS')

dif_plazo.to_excel(writer, 
                   sheet_name = sheet, 
                   startrow   = actual_tipo_credito.shape[0] + fila_inicial + 3, 
                   startcol   = 8, 
                   index      = True)

dif_repro.to_excel(writer, 
                   sheet_name = sheet, 
                   startrow   = actual_tipo_credito.shape[0] + actual_plazo.shape[0] + fila_inicial + 6, 
                   startcol   = 8, 
                   index      = True)

writer.save()
writer.close()

#%%
ubicacion_actual = os.getcwd()

# Imprimir la ubicación actual
print("La ubicación actual es: " + ubicacion_actual)

#%% REPROGRAMADOS PARA EXPERIAN

tabla1 = reprogramados.copy()

#eliminación de filas vacías si es que las hay
tabla1.dropna(subset = ['Apellidos y Nombres / Razón Social 2/',
                        'Fecha de Nacimiento 3/',
                        'Número de Documento 10/',
                        'Domicilio 12/',
                        'Numero de Crédito 18/'], inplace = True, how = 'all')

df = pd.DataFrame()  #CREANDO INSTANCIA DATA FRAME

df['CODIGO SOCIO']      = tabla1['Código Socio 7/']
df['TIPO DOCUMENTO']    = tabla1['Tipo de Documento 9/']
df['NUMERO DOCUMENTO']  = tabla1["Número de Documento 10/"]
df['TIPO DE CREDITO']   = tabla1["Tipo de Crédito 19/"]
df['DEUDA DIRECTA']     = tabla1["Saldo de colocaciones (créditos directos) 24/"]
df['TIPO DE REPROGRAMACION']  = tabla1["TIPO_REPRO"]
df['DEUDA REPROGRAMADA']      = tabla1["Saldo de colocaciones (créditos directos) 24/"]

df['TIPO DE CREDITO'] = df['TIPO DE CREDITO'].astype(int)
df['TIPO DE CREDITO'] = df['TIPO DE CREDITO'].map({9  : '09', #REEMPLAZANDO LOS VALORES POR STRINGS CON CEROS
                                                   8  : '08',
                                                   10 : '10',
                                                   11 : '11',
                                                   12 : '12',
                                                   13 : '13'},
                                                 na_action = None) #EN CASO DE NULO NO HACER NADA

df['CODIGO SOCIO']      = df['CODIGO SOCIO'].str.strip()
df['NUMERO DOCUMENTO']  = df['NUMERO DOCUMENTO'].str.strip()

#%% NOMBRE

lista_fecha = fecha_mes.split()
X = lista_fecha[0]
Y = lista_fecha[1]
resultado = (str(X.lower().capitalize()) + " " + "Reprogramados - " +str(Y)) #métodos string para crear el nombre del archivo
nombre = str(resultado)+".xlsx"

#%% EXCEL
try:
    ruta = nombre
    os.remove(ruta)
except FileNotFoundError:
    pass

df.to_excel(nombre, 
            index = False,
            startrow = 1,
            startcol = 1,
            sheet_name=str(X.lower().capitalize() + "-"+str(Y)))

