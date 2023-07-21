# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 10:40:15 2023

@author: sanmiguel38
"""

import pandas as pd
import os
import numpy as np

#%%
'Revisar que estén bien las fechas:'
#"Fecha Creacion Reprogramacion Nacimiento TXT"
#"Fecha Creacion Reprogramacion Corte TXT"
#'FEC_ULT_REPROG'

#%%
fecha_mes = 'JUNIO 2023'
fecha_corte = '2023-06-30'
#%%
#INSUMO PRINCIPAL, ANEXO06 SUPER PRELIMINAR
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\REPORTE DE REPROGRAMADOS\\2023 JUNIO')

bruto = pd.read_excel('Rpt_DeudoresSBS Anexo06  - Junio2023 - campos ampliados (original fincore).xlsx',
                      skiprows=4,
                      dtype=({'Registro 1/': object, 
                             'Fecha de Nacimiento 3/': object,
                             'Código Socio 7/':object,
                             'Número de Documento 10/': object,
                             'Relación Laboral con la Cooperativa 13/':object, 
                             'Código de Agencia 16/': object,
                             'Moneda del crédito 17/':object, 
                             'Numero de Crédito 18/': object,
                             'Tipo de Crédito 19/': object,
                             'Sub Tipo de Crédito 20/': object,
                             'Fecha de Desembolso 21/': object,
                             'Cuenta Contable 25/': object,
                             'Tipo de Producto 43/': object,
                             'Fecha de Vencimiento Origuinal del Credito 48/': object,
                             'Fecha de Vencimiento Actual del Crédito 49/': object,
                             '''Nro Prestamo 
Fincore''': object,
                             'Refinanciado TXT': object,
}))

menos_bruto = bruto.drop(columns=[col for col in bruto.columns if 'Unnamed' in col]) #elimina columnas Unnamed

menos_bruto.dropna(subset=['Apellidos y Nombres / Razón Social 2/', 
                   'Fecha de Nacimiento 3/',
                   'Número de Documento 10/',
                   'Domicilio 12/',
                   'Numero de Crédito 18/'], inplace=True, how='all') #eliminando las filas vacías

menos_bruto['Código Socio 7/'] = menos_bruto['Código Socio 7/'].str.strip()
menos_bruto['''Nro Prestamo 
Fincore'''] = menos_bruto['''Nro Prestamo 
Fincore'''].astype(int).astype(str).str.zfill(8) #agregando los 8 ceros

mask = menos_bruto['''Nro Prestamo 
Fincore'''].duplicated(keep=False)
df_duplicadoss = menos_bruto[mask]

print('filas duplicadas:')
print(df_duplicadoss.shape[0])
del df_duplicadoss

print(menos_bruto.shape[0])

menos_bruto = menos_bruto.drop_duplicates(subset='''Nro Prestamo 
Fincore''') #por si acaso eliminamos duplicados
print(menos_bruto.shape[0])
print('si sale menos en el segundo es porque hubo duplicados')

#%%
#BUSCAMOS DUPLICADOS
duplicados = menos_bruto[menos_bruto['''Nro Prestamo 
Fincore'''].duplicated()]
print(duplicados) #investigar si sale algo

#%%
#aquí el anexo06 del mes pasado, el que manda Cesar
ubicacion_anx06_anterior = 'C:\\Users\\sanmiguel38\\Desktop\\TRANSICION  ANEXO 6\\2023 MAYO\\ANEXO 06'

nombre_anx06 = 'Rpt_DeudoresSBS Anexo06  - Mayo2023 - campos ampliados.xlsx'

anx06_anterior = pd.read_excel(ubicacion_anx06_anterior + '\\' + nombre_anx06,
                               skiprows=2,
                               dtype={'Registro 1/': object, 
                                      'Fecha de Nacimiento 3/': object,
                                      'Código Socio 7/':object, 
                                      'Número de Documento 10/': object,
                                      'Relación Laboral con la Cooperativa 13/':object, 
                                      'Código de Agencia 16/': object,
                                      'Moneda del crédito 17/':object, 
                                      'Numero de Crédito 18/': object,
                                      'Tipo de Crédito 19/': object,
                                      'Sub Tipo de Crédito 20/': object,
                                      'Fecha de Desembolso 21/': object,
                                      'Cuenta Contable 25/': object,
                                      'Tipo de Producto 43/': object,
                                      'Fecha de Vencimiento Origuinal del Credito 48/': object,
                                      'Fecha de Vencimiento Actual del Crédito 49/': object,
                                      '''Nro Prestamo 
Fincore''': object,
                                      'Refinanciado TXT': object}) #no está funcionando esta vaina, debería leer en str
del ubicacion_anx06_anterior
del nombre_anx06

#agregando ceros al nro de fincore por si acaso
anx06_anterior['''Nro Prestamo 
Fincore'''] = anx06_anterior['''Nro Prestamo 
Fincore'''].astype(str).str.zfill(8)

mask = anx06_anterior['''Nro Prestamo 
Fincore'''].duplicated(keep=False)
df_duplicadossss = anx06_anterior[mask]
print(df_duplicadossss)

anx06_anterior.dropna(subset=['Apellidos y Nombres / Razón Social 2/', 
                   'Fecha de Nacimiento 3/',
                   'Número de Documento 10/',
                   'Domicilio 12/',
                   'Numero de Crédito 18/'], inplace=True, how='all') #eliminando las filas vacías

print(anx06_anterior.shape[0])

anx06_anterior = anx06_anterior.drop_duplicates(subset='''Nro Prestamo 
Fincore''') #por si acaso eliminamos duplicados
print(anx06_anterior.shape[0])
print('si sale menos en el segundo es porque hubo duplicados')

#%% ORDENAMIENTO DE LAS COLUMNAS

ordenado = menos_bruto[['Registro 1/',
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
'''Rendimiento
Devengado 40/''',
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
'''Subcuenta de orden 
54/
''',
'Rendimiento Devengado por efecto del COVID 19 55/',
'Saldo de Garantías con Sustitución de Contraparte 56/',
'Saldo Capital de Créditos Reprogramados por efecto del COVID 19 57/',
'Categoria TXT',
'Saldo Colocacion Sin Capitalizacion de Intereses TXT',
'Dscto Enviado TXT',
'Desc Pagado TXT',
'''Fecha Vencimiento 
Origuinal TXT''',
'Fecha Vencimiento Actual TXT',
'Mes Creacion Reprogramado Nacimiento TXT',
'Fecha Creacion Reprogramacion Nacimiento TXT',
'''Mes Creacion
Reprogramado Corte 
TXT''',
'Fecha Creacion Reprogramacion Corte TXT',
'Nro Dias Gracia Corte RPG TXT',
'Nro Cuotas Canc Post Regro',
'Nro Prestamos X Deudor TXT',
'''Fecha Ultimo 
Pago TXT''',
'TEM TXT',
'Nro Dias Gracia  Acumulado RPG TXT',
'Tipo Reprogramacion TXT',
'Fecha Primer Cuota Gracia Nacimiento RPG TXT',
'Primer Fecha Cuota Gracia Corte RPG TXT',
'Nro Reprogramaciones TXT',
'''Origen
 Prestamo''',
'''Nro Prestamo 
Fincore''',
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
'''Interes
Devengado Total''',
'''Interes 
Suspenso Total''',
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
'Fecha Castigo TXT'
]]

#%%
#PONEMOS LOS SALDOS DE GARANTÍAS DEL MES PASADO #chucha, tenemos que tener cuidado con esta huevada,
#estos datos debemos sacar del preliminar del anexo06, porque en el anexo 06 final ya se han cambiado estos datos y se han puesto en las columnas 'monto de garantías'

garantias = anx06_anterior[['''Nro Prestamo 
Fincore''','Saldos de Garantías Preferidas 34/', 'Saldo de Garantías Autoliquidables 35/']]

nuevos_nombres = {
    '''Nro Prestamo 
Fincore''':                                     'fincore para merge',
    'Saldos de Garantías Preferidas 34/':       'garantias pref mes pasado',
    'Saldo de Garantías Autoliquidables 35/':   'garantias autoli mes pasado'}

garantias = garantias.rename(columns=nuevos_nombres)
del nuevos_nombres

###################### merge para poner del mes pasado
ordenado = ordenado.merge(garantias, 
                         left_on=['''Nro Prestamo 
Fincore'''], 
                         right_on=['fincore para merge']
                         ,how='left')
                                  
ordenado['Saldos de Garantías Preferidas 34/'] = ordenado['garantias pref mes pasado']
ordenado['Saldos de Garantías Preferidas 34/'] = ordenado['Saldos de Garantías Preferidas 34/'].fillna(0)
ordenado['Saldo de Garantías Autoliquidables 35/'] = ordenado['garantias autoli mes pasado']
ordenado['Saldo de Garantías Autoliquidables 35/'] = ordenado['Saldo de Garantías Autoliquidables 35/'].fillna(0)

#eliminar columnas que ya no sirven
ordenado.drop(['garantias pref mes pasado','garantias autoli mes pasado','fincore para merge'], axis=1, inplace=True)

#verificación si hizo buen match
actual = ordenado['Saldos de Garantías Preferidas 34/'].sum()
anterior = garantias['garantias pref mes pasado'].sum()
if actual == anterior:
    print('todo bien en traer saldos de garantías del mes pasado')
else:
    print('habría que chequear si algún crédito se canceló \no quizás no hizo match')

#%%
###############################################################
## generamos el archivo para Oswald y/o Juan Carlos        ####
## para que nos ayuden con los certificados de depósitos   ####
###############################################################

#cambiar la fecha
filtrado_certificados = ordenado[ordenado['Fecha de Desembolso 21/'].astype(int) >= 20230601] #aquí cambiar la fecha
#cambiar la fecha

para_enviar = filtrado_certificados[filtrado_certificados['Monto de Desembolso 22/'] >= 90000]
para_enviar = para_enviar[['Apellidos y Nombres / Razón Social 2/',
                           'Fecha de Desembolso 21/',
                           'Monto de Desembolso 22/',
                           '''Nro Prestamo 
Fincore''']]

para_enviar['''Nro \nCert.Depósito \nFincore'''] = ''
para_enviar['''Moneda e \nImporte'''] = ''
para_enviar['Socio que Garantiza'] = ''

#reporte para enviar a Juan Carlos o a Oswald
try:
    ruta = f'Créditos Garantizados con CD {fecha_mes}.xlsx'
    os.remove(ruta)
except FileNotFoundError:
    pass

para_enviar.to_excel(ruta,
                      index=False)

#%%

#EL MONTO QUE ENVÍEN IRÁ EN GARANTÍA AUTOLIQUIDABLE
# puede que esté en dólares, hay que pasarlo a soles
# esto se añade después de generar este archivo, para generar el anexo06 final, no este
#%%
#ahora hay que calcular alineamiento interno y tasa de provisión requerida (como en el anexo06)
#arreglamos el saldo de cartera

ordenado['Saldo Colocacion Con Capitalizacion de Intereses TXT'] = ordenado['Saldo de colocaciones (créditos directos) 24/']
ordenado['Saldo de colocaciones (créditos directos) 24/'] = ordenado['Saldo Colocacion Sin Capitalizacion de Intereses TXT']
def negativos_saldo_cartera(ordenado):
    if ordenado['Saldo de colocaciones (créditos directos) 24/'] < 0:
        return ordenado['Saldo Colocacion Con Capitalizacion de Intereses TXT']
    else:
        return ordenado['Saldo de colocaciones (créditos directos) 24/']
ordenado['Saldo de colocaciones (créditos directos) 24/'] = ordenado.apply(negativos_saldo_cartera, axis=1)
    
ordenado['Código Socio 7/'] = ordenado['Código Socio 7/'].astype(str).str.strip()

ordenado['''Nro Prestamo 
Fincore'''] = ordenado['''Nro Prestamo 
Fincore'''].str.strip()

#%%
#verificación del tipo de producto 19/
#para créditos MYPE
ordenado['Tipo de Crédito 19/'] = ordenado['Tipo de Crédito 19/'].astype(str) #por si acasito

def etiqueta_mype(ordenado):
    if ordenado['Tipo de Crédito 19/'] in ['08', '09', '10']:
        return 'mype'
    else:
        return 'otros'
ordenado['etiqueta mype'] = ordenado.apply(etiqueta_mype, axis=1)

def asign_prod_19(ordenado):
    if (ordenado['etiqueta mype'] == 'mype') & \
    (ordenado['Monto de Desembolso 22/'] > 0) & \
    (ordenado['Monto de Desembolso 22/'] <= 20000):
        return '10'
    elif (ordenado['etiqueta mype'] == 'mype') & \
    (ordenado['Monto de Desembolso 22/'] > 20000) & \
    (ordenado['Monto de Desembolso 22/'] <= 300000):
        return '09'
    elif (ordenado['etiqueta mype'] == 'mype') & \
    (ordenado['Monto de Desembolso 22/'] > 300000):
        return '08'
    else:
        return ordenado['Tipo de Crédito 19/']

ordenado['tipo crédito 19 corregido'] = ordenado.apply(asign_prod_19, axis=1)
ordenado.drop(['etiqueta mype'], axis=1, inplace=True)
ordenado['Tipo de Crédito 19/ (original)'] = ordenado['Tipo de Crédito 19/']
ordenado['Tipo de Crédito 19/'] = ordenado['tipo crédito 19 corregido']
ordenado.drop(['tipo crédito 19 corregido'], axis=1, inplace=True)

filtrado_credito_19 = ordenado[ordenado['Tipo de Crédito 19/ (original)'] != ordenado['Tipo de Crédito 19/']]

filtrado_credito_19['Monto de Desembolso Origuinal TXT'] = filtrado_credito_19['Monto de Desembolso Origuinal TXT'].astype(float)
filtrado_credito_19 = filtrado_credito_19[['Registro 1/',
                                           'Apellidos y Nombres / Razón Social 2/',
                                           'Código Socio 7/',
                                           'Número de Documento 10/',
                                           '''Nro Prestamo 
Fincore''',
                                           'Tipo de Crédito 19/ (original)',
                                           'Tipo de Crédito 19/',
                                           'Monto de Desembolso Origuinal TXT',
                                           'Monto de Desembolso 22/',
                                           'Moneda del crédito 17/'
                                           ]]
ordenado.drop(['Tipo de Crédito 19/ (original)'], axis=1, inplace=True)
filtrado_credito_19 = filtrado_credito_19.rename(columns={'''Nro Prestamo 
Fincore''': "Fincore"})

#guardamos este excel para mandárselo a Cesar
try:
    ruta = "Corección Tipo de Crédito 19.xlsx"
    os.remove(ruta)
except FileNotFoundError:
    pass

filtrado_credito_19.to_excel(ruta, index=False)

#%%
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
print(nulos)
del nulos
revisar = ordenado[ordenado['Clasificación del Deudor 14/'] == 'revisar caso']
print(revisar)
del revisar

#%%
#calculamos alineamiento 15/
#primero que nada columnas auxiliares
saldo_total = ordenado.groupby('Código Socio 7/')['Saldo de colocaciones (créditos directos) 24/'].sum().reset_index()
saldo_total = saldo_total.rename(columns={"Código Socio 7/": "codigo para merge"})
saldo_total = saldo_total.rename(columns={"Saldo de colocaciones (créditos directos) 24/": "saldo para dividir"})

#merge
ordenado = ordenado.merge(saldo_total, 
                          how='left', 
                          left_on=['Código Socio 7/'], 
                          right_on=["codigo para merge"])

ordenado.drop(["codigo para merge"], axis=1, inplace=True)

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
uit = 4950 #valor de la uit en el año 2023  ###
###############################################
def monto_menor(ordenado):
    if (ordenado['Saldo de colocaciones (créditos directos) 24/'] < 100) or \
        ((ordenado['porcentaje del total'] < 0.01) and \
        (ordenado['Saldo de colocaciones (créditos directos) 24/'] < 3*uit)):
        return 'menor'
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

#%%
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

#%%
# cálculo de provisiones
# ya no

#%%
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

suma_saldo_cartera = ordenado['Saldo de colocaciones (créditos directos) 24/'].sum()

suma_otros = ordenado['Capital Vigente 26/'].sum() + \
             ordenado['Capital Reestrucutado 27/'].sum() + \
             ordenado['Capital Refinanciado 28/'].sum() + \
             ordenado['Capital Vencido 29/'].sum() + \
             ordenado['Capital en Cobranza Judicial 30/'].sum()
             
#VERIFICAR QUE ESTA COMPARACIÓN SALGA TRUE        
print(round(suma_saldo_cartera,2)  == round(suma_otros,2)) 

#%%
#NUEVA PARTE IMPORTANTE DE ESTE REPORTE, AÑADIREMOS UNAS 6 COLUMNAS IMPORTANTES
ordenado['FEC_ULT_REPROG']= ''
ordenado['PLAZO_REPR']= ''
ordenado['TIPO_REPRO']= ''
ordenado['PLAZO REPRO ACUMULADO']= ''
ordenado['NRO CUOTAS REPROG CANCELADAS']= ''
ordenado['NRO REPROG']= ''

columnas = list(ordenado.columns)

anx06_ordenado = ordenado[columnas[0:57]+['FEC_ULT_REPROG',
                                          'PLAZO_REPR',
                                          'TIPO_REPRO',
                                          'PLAZO REPRO ACUMULADO',
                                          'NRO CUOTAS REPROG CANCELADAS',
                                          'NRO REPROG'] + \
                          columnas[57:129]]
#%% ahora a sacar datos del mes pasado
#los 3 primeros
anterior_para_merge = anx06_anterior[['''Nro Prestamo 
Fincore''', 'FEC_ULT_REPROG', 'PLAZO_REPR', 'TIPO_REPRO']]

nuevos_nombres = {
    '''Nro Prestamo 
Fincore'''             :   'fincore para merge',
    'FEC_ULT_REPROG'   :   'FEC_ULT_REPROG para merge',
    'PLAZO_REPR'       :   'PLAZO_REPR para merge',
    'TIPO_REPRO'       :   'TIPO_REPRO para merge'}

anterior_para_merge = anterior_para_merge.rename(columns=nuevos_nombres)
del nuevos_nombres

anx06_ordenado = anx06_ordenado.merge(anterior_para_merge, 
                         left_on=['''Nro Prestamo 
Fincore'''], 
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


#%%
#añadimos datos a la col 4
def col4(anx06_ordenado):
    if anx06_ordenado['TIPO_REPRO'] != '--':
        return anx06_ordenado['Nro Dias Gracia  Acumulado RPG TXT']
    else:
        return anx06_ordenado['PLAZO REPRO ACUMULADO']
anx06_ordenado['PLAZO REPRO ACUMULADO'] = anx06_ordenado.apply(col4, axis=1)

#añadimos datos a la col 5
def col5(anx06_ordenado):
    if anx06_ordenado['TIPO_REPRO'] != '--':
        return anx06_ordenado['Nro Cuotas Canc Post Regro']
    else:
        return anx06_ordenado['NRO CUOTAS REPROG CANCELADAS']
anx06_ordenado['NRO CUOTAS REPROG CANCELADAS'] = anx06_ordenado.apply(col4, axis=1)

#añadimos datos a la col 6
def col6(anx06_ordenado):
    if anx06_ordenado['TIPO_REPRO'] != '--':
        return anx06_ordenado['Nro Reprogramaciones TXT']
    else:
        return anx06_ordenado['NRO REPROG']
anx06_ordenado['NRO REPROG'] = anx06_ordenado.apply(col4, axis=1)    

#%%
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

#%%
'##############################################################################'
#AÑADIENDO NUEVOS REPROGRAMADOS
#PONER AQUÍ EL INICIO DEL MES DE CORTE (habrá que cambiarlo cada mes)
mes_inicio = pd.to_datetime('2023-05-01')
#PONER AQUÍ EL FINAL DEL MES DE CORTE (habrá que cambiarlo cada mes)
mes_final = pd.to_datetime('2023-06-30')
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

#%%
#falta añadir las 3 columnas, pero para los nuevos

#%%
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

#%%
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

#%%
'aquí se me han duplicado créditos'
# CREACIÓN DE LA PESTAÑA DONDE ESTARÁN LOS CRÉDITOS CON CRÉDITOS MENORES A 100 SOLES

menores = anx06_ordenado[(anx06_ordenado['Saldo de colocaciones (créditos directos) 24/'] < 100) & \
                         (anx06_ordenado['Saldo de colocaciones (créditos directos) 24/'] > 0)]
menores = menores[['Código Socio 7/','Apellidos y Nombres / Razón Social 2/','''Nro Prestamo 
Fincore''']]

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
 
#%% eliminamos créditos no vigentes
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
            
anx06_ordenado['vigentes??'] = anx06_ordenado.apply(filtracion_E1_E2, axis=1)

anx06_ordenado = anx06_ordenado[anx06_ordenado['vigentes??'] == 'vigente']
anx06_ordenado.drop(['vigentes??'], axis=1, inplace=True)

#VERIFICACIÓN
print(anx06_ordenado[~pd.isna(anx06_ordenado['E2'])]['E2']) #con esto podemos ver que solo queden créditos con cancelaciones posteriores a la fecha de corte

#%% COLUMNAS PARA CONTABILIDAD

anx06_ordenado['''fecha desemb (v)'''] = np.nan
anx06_ordenado['''fecha término de gracia por desembolso ["v" + dias gracia (av)]'''] = np.nan
anx06_ordenado['''periodo de gracia por Reprog inicio'''] = np.nan
anx06_ordenado['''periodo de gracia por Reprog Término'''] = np.nan
anx06_ordenado['''Fecha Venc de Ult Cuota Cancelada
(NVO)'''] = np.nan

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
print(anx06_ordenado[['''fecha desemb (v)''', '''fecha término de gracia por desembolso ["v" + dias gracia (av)]''']])

#%%
#COL AMARILLA 3 y 4, primero datos del mes pasado

col3_4 = anx06_anterior[['''Nro Prestamo 
Fincore''', 'periodo de gracia por Reprog inicio', 
            'periodo de gracia por Reprog Término']]

#cambio de nombre de las columnas para hacer un merge sin ambiguedades
col3_4 = col3_4.rename(columns={'''Nro Prestamo 
Fincore''': "Fincore merge 3 y 4"})
col3_4 = col3_4.rename(columns={'periodo de gracia por Reprog inicio': "3 merge"})
col3_4 = col3_4.rename(columns={'periodo de gracia por Reprog Término': "4 merge"})

col3_4 = col3_4.drop_duplicates(subset="Fincore merge 3 y 4") #por si acaso eliminamos duplicados antes del merge
#colocando los del mes pasado:
anx06_ordenado = anx06_ordenado.merge(col3_4, 
                                      left_on=['''Nro Prestamo 
Fincore'''], 
                                     right_on=["Fincore merge 3 y 4"]
                                     ,how='left')
del col3_4
anx06_ordenado['periodo de gracia por Reprog inicio'] = anx06_ordenado["3 merge"]
anx06_ordenado['periodo de gracia por Reprog Término'] = anx06_ordenado["4 merge"]

anx06_ordenado.drop(["3 merge", #eliminación de columnas auxiliares que ya no sirven
                     "4 merge",
                     "Fincore merge 3 y 4"], axis=1, inplace=True)


anx06_ordenado[(anx06_ordenado['periodo de gracia por Reprog inicio'] != '--') & \
               (pd.isna(anx06_ordenado['periodo de gracia por Reprog inicio']))]['periodo de gracia por Reprog inicio']


#%% columna 5
anx06_ordenado['''Fecha Venc de Ult Cuota Cancelada
(NVO)'''] = anx06_ordenado['Fecha Venc Ult Cuota Cancelada']

anx06_ordenado['periodo de gracia por Reprog inicio'] = \
    anx06_ordenado['periodo de gracia por Reprog inicio'].fillna('--')
anx06_ordenado['periodo de gracia por Reprog Término'] = \
    anx06_ordenado['periodo de gracia por Reprog Término'].fillna('--')

anx06_ordenado['''Fecha Venc de Ult Cuota Cancelada
(NVO)'''] = anx06_ordenado['''Fecha Venc de Ult Cuota Cancelada
(NVO)'''].fillna('--')

print(anx06_ordenado[anx06_ordenado['periodo de gracia por Reprog inicio'] != '--']['periodo de gracia por Reprog inicio'])
#hasta aquí todo bien

#%% col amarillas 3 y 4

def col3_actuales(anx06_ordenado):
    if (anx06_ordenado["Fecha Creacion Reprogramacion Nacimiento TXT"] >= mes_inicio) & \
    (anx06_ordenado["Fecha Creacion Reprogramacion Nacimiento TXT"] <= mes_final):
        return anx06_ordenado['Fecha Primer Cuota Gracia Nacimiento RPG TXT'] - pd.to_timedelta(anx06_ordenado['Periodo de Gracia 47/'], unit='D')
    else:
        return anx06_ordenado['periodo de gracia por Reprog inicio']
    
anx06_ordenado['periodo de gracia por Reprog inicio'] = anx06_ordenado.apply(col3_actuales, axis=1)

print(anx06_ordenado[anx06_ordenado['periodo de gracia por Reprog inicio'] != '--']['periodo de gracia por Reprog inicio'])
#aparentemente todo bien

def col4_actuales(anx06_ordenado):
    if (anx06_ordenado["Fecha Creacion Reprogramacion Nacimiento TXT"] >= mes_inicio) & \
    (anx06_ordenado["Fecha Creacion Reprogramacion Nacimiento TXT"] <= mes_final):
        return anx06_ordenado['Fecha Primer Cuota Gracia Nacimiento RPG TXT'] - pd.to_timedelta(anx06_ordenado['Periodo de Gracia 47/'], unit='D')
    else:
        return anx06_ordenado['periodo de gracia por Reprog Término']
    
anx06_ordenado['periodo de gracia por Reprog Término'] = anx06_ordenado.apply(col4_actuales, axis=1)

print(anx06_ordenado[anx06_ordenado['periodo de gracia por Reprog Término'] != '--']['periodo de gracia por Reprog Término'])
#aparentemente todo bien

#%% 5ta columna amarilla

# hay que asegurarnos de que esta columna sea datetime 'Fecha Venc Ult Cuota Cancelada'

anx06_ordenado['''Fecha Venc de Ult Cuota Cancelada
(NVO)'''] = anx06_ordenado['Fecha Venc Ult Cuota Cancelada']

anx06_ordenado['''Fecha Venc de Ult Cuota Cancelada
(NVO)'''] = anx06_ordenado['''Fecha Venc de Ult Cuota Cancelada
(NVO)'''].fillna('--')

#%%
#por si acasito, corregimos la columna del nro Registro 1/

# Obtener la cantidad total de filas en el DataFrame
total_filas = len(anx06_ordenado)

# Crear la nueva columna con la secuencia numérica
anx06_ordenado['Registro 1/'] = [f'{i+1:06}' for i in range(total_filas)]

#%% por si acaso, convertimos la fecha de desembolso en int

anx06_ordenado['Fecha de Desembolso 21/'] = anx06_ordenado['Fecha de Desembolso 21/'].astype(int)

#%% verificación de los intereses en suspenso y devengados
print(' ')
print('intereses en suspenso1:')
print(anx06_ordenado['''Interes 
Suspenso Total'''].sum())

print('intereses devengados1:')
print(anx06_ordenado['''Interes
Devengado Total'''].sum())
#%% intereses en Suspenso + Devengados en caso de que tengan cero cuotas canceladas y tengan >30 días
#se suman los intereses en suspenso y devengados
anx06_ordenado['Dias de Mora 33/'] = anx06_ordenado['Dias de Mora 33/'].astype(int)

def int_suspenso_y_devengados(anx06_ordenado):
    if (1 == 1) & \
    (anx06_ordenado['Tipo de Crédito 19/'] == '08') & \
    (anx06_ordenado['Dias de Mora 33/'] > 15):
        return anx06_ordenado['''Interes 
Suspenso Total'''] + anx06_ordenado['''Interes
Devengado Total''']
    elif (anx06_ordenado['Número de Cuotas Pagadas 45/'] == 0) & \
    (anx06_ordenado['Tipo de Crédito 19/'] in ['09', '10', '11', '12', '13', 9, 10, 11, 12, 13]) & \
    (anx06_ordenado['Dias de Mora 33/'] > 30):
        return anx06_ordenado['''Interes 
Suspenso Total'''] + anx06_ordenado['''Interes
Devengado Total''']
    else:
        return anx06_ordenado['''Interes 
Suspenso Total''']

anx06_ordenado['''Interes 
Suspenso Total'''] = anx06_ordenado.apply(int_suspenso_y_devengados, axis=1)

anx06_ordenado['''Interes
Devengado Total'''] = anx06_ordenado['''Interes
Devengado Total'''].astype(float)

#se le pone cero a esos mismos devengados
def devengados_cero(anx06_ordenado):
    if (1 == 1) and \
    anx06_ordenado['Tipo de Crédito 19/'] == '08' and \
    anx06_ordenado['Dias de Mora 33/'] > 15:
        return 0
    elif (anx06_ordenado['Número de Cuotas Pagadas 45/'] == 0) and \
    anx06_ordenado['Tipo de Crédito 19/'] in ['09', '10', '11', '12', '13', 9, 10, 11, 12, 13] and \
    anx06_ordenado['Dias de Mora 33/'] > 30:
        return 0
    else:
        return anx06_ordenado['''Interes
Devengado Total''']

anx06_ordenado['''Interes
Devengado Total'''] = anx06_ordenado.apply(devengados_cero, axis=1)

print(' ')
print('intereses en suspenso2:')
print(anx06_ordenado['''Interes 
Suspenso Total'''].sum())
print('intereses devengados2:')
print(anx06_ordenado['''Interes
Devengado Total'''].sum())

#%% ASIGNACIÓN DE LOS DEVENGADOS A LAS COLUMNAS QUE SÍ IRÁN EN EL ANEXO 06 PARA LA SBS

anx06_ordenado['''Rendimiento
Devengado 40/'''] = anx06_ordenado['''Interes
Devengado Total''']

anx06_ordenado['Intereses en Suspenso 41/'] = anx06_ordenado['''Interes 
Suspenso Total''']

#%% ORDENAMIENTO DE LAS COLUMNAS ¿falta, no me acuerdo xd?
'#############################################################################'

#%%
#CREAMOS EL EXCEL
df_vacío = pd.DataFrame({' ': ['', '', ''], '  ': ['', '', '']})
try:
    ruta = 'anexo experimental.xlsx'
    os.remove(ruta)
except FileNotFoundError:
    pass

df_vacío.to_excel(ruta,
                      index=False)

##################### ESCRIBIMOS EN ESE EXCEL VACÍO #####################

# Crear un objeto ExcelWriter y especificar el archivo de salida
excel_writer = pd.ExcelWriter('anexo experimental.xlsx')

# Guardar cada DataFrame en una hoja (sheet) diferente
anx06_ordenado.to_excel(excel_writer, sheet_name = fecha_mes, index=False) ##
menores.to_excel(excel_writer, sheet_name='socios con cred < 100 soles', index=False)

# Guardar los cambios y cerrar el objeto ExcelWriter
excel_writer.save()
 
#%%
#YA ESTÁ
#filtramos créditos reprogramados NO castigados
reprogramados = anx06_repro[(anx06_repro['TIPO_REPRO'] != '--') & \
                            (anx06_repro['Saldos de Créditos Castigados 38/'] == 0)]

#%%
# CREACIÓN DEL EXCEL DE REPROGRAMADOS
try:
    ruta = f'Créditos Reprogramados {fecha_mes}.xlsx'
    os.remove(ruta)
except FileNotFoundError:
    pass

reprogramados.to_excel(ruta,
                      index=False)    

