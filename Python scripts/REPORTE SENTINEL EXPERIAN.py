# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 12:37:47 2023

@author: sanmiguel38
"""
#############################
#   reporte para sentinel   #
#############################
#ESTE ES EL REPORTE QUE NOS PASA DENISSE O CESAR

#%% módulos necesarios
import pandas as pd
import os
import pyodbc
import numpy as np

#import numpy as np

#%%
##############################################
#    NROS CREDITO, OBTENIDOS DEL SQL
##############################################
#añadiendo nro de fincore al reporte de sentinel
conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')


########################################################
###  donde dice @fechacorte se debe poner el mes  ######
########################################################

#extraemos una tabla con el NumerodeCredito18 y ponemos fecha de hace 2 meses (para que jale datos de 2 periodos)
df_fincore = pd.read_sql_query('''
declare @fechacorte datetime
set @fechacorte = '20230630' 

select 
    NumerodeCredito18, 
    Nro_Fincore
    
from 
    anexos_riesgos2..Anx06_preliminar

where 
    FechaCorte1 = @fechacorte
''', conn)
del conn
#%%
##############################################
#      REPORTE INSUMO PRINCIPAL
##############################################
#importamos el archivo sentinel bruto, que nos manda Cesar o Denisse
ubicacion = "C:\\Users\\sanmiguel38\\Desktop\\sentinel\\2023 JUNIO"
os.chdir(ubicacion) #aqui se cambia la ubicación


df_sentinel=pd.read_excel("descapitalizado SM_0623 - Sentinel-Experian Cart Vigente y Vencida - Junio-23.xlsx",    # aqui se cambia el nombre del archivo si es necesario
                  dtype={
'''Fecha del
Periodo
(*)''': object, 
'''Codigo
Entidad
(*)''': object,
'''Tipo
Documento
Identidad (*)''': object,
'''N° Documento
Identidad (*)  DNI o RUC''' : str,
'''Tipo Persona (*)''': object,
'''Modalidad de Credito (*)''': object})

df_sentinel.dropna(subset=['Cod. Prestamo', 
                   '''N° Documento
Identidad (*)  DNI o RUC''',
                   'Razon Social (*)',
                   'Apellido Paterno (*)'], inplace=True, how='all')

#%%
#descapitalizar saldos:
'ES SOLO SACAR ESTOS DATOS DEL ANEXO06'

#%%
#ya que todos los meses se duplican los datos del socio AGUILA	FEBRES	MIGUEL ALBERTO
#antes de eliminar sus datos duplicados, vamos a etiquetar su 'Tipo Documento Identidad(*)' = 1
df_sentinel.loc[(df_sentinel['''N° Documento
Identidad (*)  DNI o RUC'''] == '02803330') & \
                (df_sentinel['Apellido Paterno (*)'] == 'AGUILA') & \
                (df_sentinel['Apellido Paterno (*)'] == 'FEBRES'),
                '''Tipo
Documento
Identidad (*)'''] = '1' #no funciona esta huevada

#%%
#AQUI DEBEMOS VERIFICAR SI EXISTEN DUPLICADOS
#SI EXISTE DEBEMOS HACER UNA CORRECCIÓN MANUAL

# Encontrar las filas que tienen valores duplicados en la columna "nombre"
mask = df_sentinel['Cod. Prestamo'].duplicated(keep=False)

# Indexar el DataFrame original con la máscara booleana para obtener las filas correspondientes
df_duplicados = df_sentinel[mask]

# Imprimir el nuevo DataFrame
print(df_duplicados)

#si hay duplicados vamos a investigarlos y eliminarlos
#si hay duplicados posiblemente está mal la columna 'Tipo Documento Identidad(*)'
#debemos arreglarlo

#%%
#PROCEDEMOS A ELIMINAR DUPLICADOS
df_sentinel = df_sentinel.drop_duplicates(subset='Cod. Prestamo')

#%% avales
##############################################
#   AVALES: OBTENIDO DEL FINCORE
##############################################
# en la misma ubicación que tenemos el archivo en bruto, debemos poner los avales
# estos avales los sacamos del Fincore con los siguientes botones:
# REPORTES / CREDITO /PRESTAMOS OTORGADOS / REGISTRO DE AVALES Y-O GARANTÍAS 
ruta = "Rpt_Avales.xlsx"
df1=pd.read_excel(ruta,
                  dtype={'''Nro Docto
Aval''': object,
                            '''Nro Docto
Socio''': object,
'Numero':object},
                     skiprows=8)

#%%
##############################################
#     AVALES: COLUMNAS SEPARADAS
##############################################
# ARCHIVO DE AVALES QUE NOS MANDA CESAR, LOS APELLIDOS Y NOMBRES ESTÁN EN COLUMNAS
# es el archivo que contiene los datos de los avales, pero separados en columnas (apellido paterno, materno, nombres
# domicilio, distrito, provincia, dpto, celulares)
ruta = 'C:\\Users\\sanmiguel38\\Desktop\\sentinel\\2023 JUNIO'
avales_datos_separados = pd.read_excel(ruta + '\\' +'Avales - corte 12-07-23.xlsx',
                                       dtype={'NumeroDocIdentidad': object,
                                              'Celular1': str,
                                              'Celular2': str,
                                              'TelefonoFijo1': str})
del ruta
avales_datos_separados['NumeroDocIdentidad'] = avales_datos_separados['NumeroDocIdentidad'].str.strip()

#ELIMINAMOS LOS POSIBLES DUPLICADOS
avales_datos_separados = avales_datos_separados.drop_duplicates(subset='NumeroDocIdentidad')

#%%
##############################################
#      CALIFICACIÓN DE LOS CRÉDITOS
##############################################
#REALIZANDO UNA CALIFICACIÓN UNIFICADA PARA EL REPORTE DE SENTINEL, EXPERIAN, CALIFICACIÓN QUE SALE DEL ANEXO 06

os.chdir('C:\\Users\\sanmiguel38\\Desktop\\sentinel\\2023 JUNIO') #ponemos la ubicación del archivo de las calificaciones
calif_anx06 = pd.read_excel('calificacion para reporte experian.xlsx',
                            dtype={'cod socio para merge': str})

df_sentinel['cod socio para mergear'] = df_sentinel['Cod. Prestamo'].str.split('-', expand=True)[0] #potente este código ah

#merge
df_sentinel = df_sentinel.merge(calif_anx06,
                                left_on=['cod socio para mergear'], 
                                right_on=['cod socio para merge']
                                ,how='left')

df_sentinel.drop(['cod socio para merge'], axis=1, inplace=True)

os.chdir(ubicacion) #volvemos a la ruta de siempre
#try:
#    ruta = "verificacion.xlsx"
#    os.remove(ruta)
#except FileNotFoundError:
#    pass
#df_sentinel.to_excel('verificacion.xlsx', index=False)

#%% verificador de que estén bien las calificaciones
grouped = df_sentinel.groupby('cod socio para mergear').agg({'calificacion para merge': 'nunique'})
grouped.columns = ['DIFERENTES PRODUCTOS']

# Filtrar los grupos con más de un producto diferente
result = grouped[grouped['DIFERENTES PRODUCTOS'] > 1]
print(result) #si sale vacío significa que está todo bien

#%% EN CASO DE QUE LOS CRÉDITOS EN DÓLARES NO ESTÉN SOLARIZADOS
'MULTIPLICACIÓN DE LOS SALDOS EN DÓLARES POR EL TIPO DE CAMBIO DEL MES'

tipo_cambio = 3.628

df_sentinel['ME Deuda Directa Vigente (*)'] = \
df_sentinel['ME Deuda Directa Vigente (*)'].fillna(0) * tipo_cambio
df_sentinel['ME Deuda Directa Refinanciada (*)'] = \
df_sentinel['ME Deuda Directa Refinanciada (*)'].fillna(0) * tipo_cambio
df_sentinel['ME Deuda Directa Venvida < = 30 (*)'] = \
df_sentinel['ME Deuda Directa Venvida < = 30 (*)'].fillna(0) * tipo_cambio
df_sentinel['ME Deuda Directa Vencida > 30 (*)'] = \
df_sentinel['ME Deuda Directa Vencida > 30 (*)'].fillna(0) * tipo_cambio
df_sentinel['ME Deuda Directa Cobranza Judicial (*)'] = \
df_sentinel['ME Deuda Directa Cobranza Judicial (*)'].fillna(0) * tipo_cambio
df_sentinel['ME Deuda Indirecta (avales,cartas fianza,credito) (*)'] = \
df_sentinel['ME Deuda Indirecta (avales,cartas fianza,credito) (*)'].fillna(0) * tipo_cambio
df_sentinel['ME Deuda Avalada (*)'] = \
df_sentinel['ME Deuda Avalada (*)'].fillna(0) * tipo_cambio
df_sentinel['ME Linea de Credito (*)'] = \
df_sentinel['ME Linea de Credito (*)'].fillna(0) * tipo_cambio
df_sentinel['ME Creditos Cartigados (*)'] = \
df_sentinel['ME Creditos Cartigados (*)'].fillna(0) * tipo_cambio


#%%
#pues parece que ya está 😅

def calificacion(df_sentinel):
    if pd.isnull(df_sentinel['calificacion para merge']):
        return df_sentinel['Calificación(*)']
    else:
        return df_sentinel['calificacion para merge']
df_sentinel['calificacion final'] = df_sentinel.apply(calificacion, axis=1)    
    
df_sentinel['Calificación(*)'] = df_sentinel['calificacion final'] #esto importanteeeeeeeeeeeeeeeeeee

df_sentinel.drop(["cod socio para mergear"], axis=1, inplace=True)
df_sentinel.drop(["calificacion para merge"], axis=1, inplace=True)
df_sentinel.drop(['calificacion final'], axis=1, inplace=True)

#%%
#realizamos la suma horizontal
#primero para MN

df_sentinel['MN Deuda Directa Venvida < = 30 (*)'] = 0

mask = df_sentinel['MN Deuda Directa Cobranza Judicial (*)'] > 0
df_sentinel.loc[mask, 'MN Deuda Directa Cobranza Judicial (*)']    = \
    df_sentinel.loc[mask, 'MN Deuda Directa Cobranza Judicial (*)'] + \
    df_sentinel.loc[mask, 'MN Deuda Directa Vencida > 30 (*)']      + \
    df_sentinel.loc[mask, 'MN Deuda Directa Venvida < = 30 (*)']    + \
    df_sentinel.loc[mask, 'MN Deuda Directa Refinanciada (*)']      + \
    df_sentinel.loc[mask, 'MN Deuda Directa Vigente (*)']
df_sentinel.loc[mask, 'MN Deuda Directa Vencida > 30 (*)']    = 0
df_sentinel.loc[mask, 'MN Deuda Directa Venvida < = 30 (*)']  = 0
df_sentinel.loc[mask, 'MN Deuda Directa Refinanciada (*)']    = 0
df_sentinel.loc[mask, 'MN Deuda Directa Vigente (*)']         = 0

    
mask = df_sentinel['MN Deuda Directa Vencida > 30 (*)'] > 0
df_sentinel.loc[mask, 'MN Deuda Directa Vencida > 30 (*)']    = \
    df_sentinel.loc[mask, 'MN Deuda Directa Vencida > 30 (*)']      + \
    df_sentinel.loc[mask, 'MN Deuda Directa Venvida < = 30 (*)']    + \
    df_sentinel.loc[mask, 'MN Deuda Directa Refinanciada (*)']      + \
    df_sentinel.loc[mask, 'MN Deuda Directa Vigente (*)'] 
df_sentinel.loc[mask, 'MN Deuda Directa Venvida < = 30 (*)']  = 0
df_sentinel.loc[mask, 'MN Deuda Directa Refinanciada (*)']    = 0
df_sentinel.loc[mask, 'MN Deuda Directa Vigente (*)']         = 0

mask = df_sentinel['MN Deuda Directa Venvida < = 30 (*)'] > 0
df_sentinel.loc[mask, 'MN Deuda Directa Venvida < = 30 (*)']       = \
    df_sentinel.loc[mask, 'MN Deuda Directa Venvida < = 30 (*)']    + \
    df_sentinel.loc[mask, 'MN Deuda Directa Refinanciada (*)']      + \
    df_sentinel.loc[mask, 'MN Deuda Directa Vigente (*)']
df_sentinel.loc[mask, 'MN Deuda Directa Refinanciada (*)']    = 0
df_sentinel.loc[mask, 'MN Deuda Directa Vigente (*)']         = 0
    
mask = df_sentinel['MN Deuda Directa Refinanciada (*)'] > 0
df_sentinel.loc[mask, 'MN Deuda Directa Refinanciada (*)']         = \
    df_sentinel.loc[mask, 'MN Deuda Directa Refinanciada (*)']      + \
    df_sentinel.loc[mask, 'MN Deuda Directa Vigente (*)']    
df_sentinel.loc[mask, 'MN Deuda Directa Vigente (*)']         = 0
    
#%%
#realizamos la suma horizontal para ME
mask = df_sentinel['ME Deuda Directa Cobranza Judicial (*)'] > 0
df_sentinel.loc[mask, 'ME Deuda Directa Cobranza Judicial (*)']    = \
    df_sentinel.loc[mask, 'ME Deuda Directa Cobranza Judicial (*)'] + \
    df_sentinel.loc[mask, 'ME Deuda Directa Vencida > 30 (*)']      + \
    df_sentinel.loc[mask, 'ME Deuda Directa Venvida < = 30 (*)']    + \
    df_sentinel.loc[mask, 'ME Deuda Directa Refinanciada (*)']      + \
    df_sentinel.loc[mask, 'ME Deuda Directa Vigente (*)']
df_sentinel.loc[mask, 'ME Deuda Directa Vencida > 30 (*)']    = 0
df_sentinel.loc[mask, 'ME Deuda Directa Venvida < = 30 (*)']  = 0
df_sentinel.loc[mask, 'ME Deuda Directa Refinanciada (*)']    = 0
df_sentinel.loc[mask, 'ME Deuda Directa Vigente (*)']         = 0
    
mask = df_sentinel['ME Deuda Directa Vencida > 30 (*)'] > 0
df_sentinel.loc[mask, 'ME Deuda Directa Vencida > 30 (*)']    = \
    df_sentinel.loc[mask, 'ME Deuda Directa Vencida > 30 (*)']      + \
    df_sentinel.loc[mask, 'ME Deuda Directa Venvida < = 30 (*)']    + \
    df_sentinel.loc[mask, 'ME Deuda Directa Refinanciada (*)']      + \
    df_sentinel.loc[mask, 'ME Deuda Directa Vigente (*)'] 
df_sentinel.loc[mask, 'ME Deuda Directa Venvida < = 30 (*)']  = 0
df_sentinel.loc[mask, 'ME Deuda Directa Refinanciada (*)']    = 0
df_sentinel.loc[mask, 'ME Deuda Directa Vigente (*)']         = 0

mask = df_sentinel['ME Deuda Directa Venvida < = 30 (*)'] > 0
df_sentinel.loc[mask, 'ME Deuda Directa Venvida < = 30 (*)']       = \
    df_sentinel.loc[mask, 'ME Deuda Directa Venvida < = 30 (*)']    + \
    df_sentinel.loc[mask, 'ME Deuda Directa Refinanciada (*)']      + \
    df_sentinel.loc[mask, 'ME Deuda Directa Vigente (*)']
df_sentinel.loc[mask, 'ME Deuda Directa Refinanciada (*)']    = 0
df_sentinel.loc[mask, 'ME Deuda Directa Vigente (*)']         = 0
    
mask = df_sentinel['ME Deuda Directa Refinanciada (*)'] > 0
df_sentinel.loc[mask, 'ME Deuda Directa Refinanciada (*)']         = \
    df_sentinel.loc[mask, 'ME Deuda Directa Refinanciada (*)']      + \
    df_sentinel.loc[mask, 'ME Deuda Directa Vigente (*)']    
df_sentinel.loc[mask, 'ME Deuda Directa Vigente (*)']         = 0

#%%
#SUMA DE LOS CASTIGADOS, y le ponemos cero a los que están en dólares
df_sentinel['MN Creditos Cartigados (*)'] = df_sentinel['MN Creditos Cartigados (*)'] + df_sentinel['ME Creditos Cartigados (*)']
df_sentinel['ME Creditos Cartigados (*)'] = 0

#%%
# colocamos todos los valores en la columna de MN,
# y ponemos ceros en las columnas ME
df_sentinel['MN Deuda Directa Cobranza Judicial (*)'] = df_sentinel['MN Deuda Directa Cobranza Judicial (*)'] + \
    df_sentinel['ME Deuda Directa Cobranza Judicial (*)']
df_sentinel['ME Deuda Directa Cobranza Judicial (*)'] = 0

df_sentinel['MN Deuda Directa Vencida > 30 (*)'] = df_sentinel['MN Deuda Directa Vencida > 30 (*)'] + \
    df_sentinel['ME Deuda Directa Vencida > 30 (*)']
df_sentinel['ME Deuda Directa Vencida > 30 (*)'] = 0

df_sentinel['MN Deuda Directa Venvida < = 30 (*)'] = df_sentinel['MN Deuda Directa Venvida < = 30 (*)'] + \
    df_sentinel['ME Deuda Directa Venvida < = 30 (*)']
df_sentinel['ME Deuda Directa Venvida < = 30 (*)'] = 0

df_sentinel['MN Deuda Directa Refinanciada (*)'] = df_sentinel['MN Deuda Directa Refinanciada (*)'] + \
    df_sentinel['ME Deuda Directa Refinanciada (*)']
df_sentinel['ME Deuda Directa Refinanciada (*)'] = 0

df_sentinel['MN Deuda Directa Vigente (*)'] = df_sentinel['MN Deuda Directa Vigente (*)'] + \
    df_sentinel['ME Deuda Directa Vigente (*)']
df_sentinel['ME Deuda Directa Vigente (*)'] = 0

#%%
# ponemos ceros a las columnas donde van los montos de los avales
df_sentinel['MN Deuda Indirecta (avales,cartas fianza,credito) (*)'] = 0
df_sentinel['MN Deuda Avalada (*)'] = 0

#%%
#para concatenar las columnas, nos quedamos con un archivo que solo servirá para el merge

#aqui estamos creando una columna que va a tener el nombre del aval + el numero del crédito,
#servirá para quedarnos con los valores únicos, ya que se repiten los avales en algunos casos
df1['concatenacion'] = df1['Aval'].apply(str) + ' ' + df1['Numero'].apply(str)

#creamos un nuevo dataframe solo con estas columnas
df1_filtrado = df1[['''Nro Docto
Aval''','Aval', 'Numero','''Nro Docto
Socio''', 'concatenacion']]

#le cambiamos de nombre a dos columnas
df1_filtrado = df1_filtrado.rename(columns={'''Nro Docto
Aval''': 'Dni - Asociado - indirecta2'})
df1_filtrado = df1_filtrado.rename(columns={'''Nro Docto
Socio''': 'dni socio'})

#eliminamos las filas duplicadas en función de la columna 'concatenación'
valores_unicos = df1_filtrado.drop_duplicates(subset='concatenacion', keep='first')

#creamos la columna fincore en función del nro de crédito en la columna 'Numero',
#la cual tiene texto en el siguiente formado: '01-00079529' y nos quedaremos con '00079529'
valores_unicos.loc[:, 'fincore'] = valores_unicos['Numero'].str.split('-').str[1]

#eliminamos las filas donde haya NAN en las columnas 'Dni - Asociado - indirecta2' y 'Aval'
valores_unicos = valores_unicos.dropna(subset=['Dni - Asociado - indirecta2', 'Aval'])

#valores_unicos['fincore']

#%% merge que servirá para poner numero de fincore al reporte de sentinel (solo tiene credito18)
'aqui está el problema'
'aqui está el gran problema'

#tenemos una columna que tiene esta estrucutra de datos '00000007-00099116'
#lo que hacemos es quedarnos con la segunda parte, que corresponde con el nro de crédito
df_sentinel.loc[:, 'credito18'] = df_sentinel['Cod. Prestamo'].str.split('-').str[1]

#aqui le quitamos posibles espacios vacíos en el nombre
df_sentinel['credito18'] = df_sentinel['credito18'].str.strip()

#ahora que tenemos el número de crédito 18, le hacemos un merge con la columna fincore
df_sentinel_fincore = df_sentinel.merge(df_fincore, ##########################################################
                         left_on=['credito18'], 
                         right_on=['NumerodeCredito18']
                         ,how='left')

#df_sentinel_fincore.columns
#df_sentinel_fincore.to_excel('333.xlsx', index=False)

#PARA VER ALGUNAS COSAS
#df_fincore[df_fincore['NumerodeCredito18'] == '004663']

#%%

#codigo para verificar que haya habido un match completo
match_incompleto = df_sentinel_fincore.loc[df_sentinel_fincore['Nro_Fincore'].isna()]
print(match_incompleto)
#si sale Empty DataFrame significa que hizo el match correctamente

#si hay datos, hay que investigar quiapasau

#%%
'todo bien actualmente'
#hacemos un merge que solo nos dejará con la tabla de avales
df_resultado = df_sentinel_fincore.merge(valores_unicos, 
                         left_on=['Nro_Fincore'], 
                         right_on=['fincore']
                         ,how='inner')

#%%
#ESTA ES LA PARTE EN LA QUE ARREGLAMOS EL DNI DEL AVAL, CREO QUE AQUÍ TAMBIÉN DEBERÍAMOS PONER
#LOS DATOS PERSONALES DE LOS AVALES CUANDO TENGAMOS ESE REPORTE
#
df_resultado['''N° Documento
Identidad (*)  DNI o RUC'''] = df_resultado['Dni - Asociado - indirecta2']

#%%
#a esta tabla de avales le ponemos 3 en 'Tipo Persona (*)'
df_resultado['Tipo Persona (*)'] = '3'

df_resultado['''Tipo
Documento
Identidad (*)'''] = '1'
#df_resultado = df_resultado.drop_duplicates(subset=['Cod. Prestamo', '''N° Documento
#Identidad (*)  DNI o RUC'''], keep='first')



#%%
#colocamos el monto de la deuda en la columna 'MN Deuda Avalada (*)'
df_resultado['MN Deuda Avalada (*)'] = df_resultado['MN Deuda Directa Vigente (*)'] + \
                                       df_resultado['MN Deuda Directa Refinanciada (*)'] + \
                                       df_resultado['MN Deuda Directa Venvida < = 30 (*)'] + \
                                       df_resultado['MN Deuda Directa Vencida > 30 (*)'] + \
                                       df_resultado['MN Deuda Directa Cobranza Judicial (*)']
df_resultado['MN Deuda Directa Vigente (*)']           = 0
df_resultado['MN Deuda Directa Refinanciada (*)']      = 0
df_resultado['MN Deuda Directa Venvida < = 30 (*)']    = 0
df_resultado['MN Deuda Directa Vencida > 30 (*)']      = 0
df_resultado['MN Deuda Directa Cobranza Judicial (*)'] = 0


#%% ordenando
columnas = ['Fecha del\nPeriodo\n(*)', 'Codigo\nEntidad\n(*)', 'Cod. Prestamo',
       'Tipo\nDocumento\nIdentidad (*)',
       'N° Documento\nIdentidad (*)  DNI o RUC', 'Razon Social (*)',
       'Apellido Paterno (*)', 'Apellido Materno (*)', 'Nombres (*)',
       'Tipo Persona (*)', 'Modalidad de Credito (*)',
       'MN Deuda Directa Vigente (*)', 'MN Deuda Directa Refinanciada (*)',
       'MN Deuda Directa Venvida < = 30 (*)',
       'MN Deuda Directa Vencida > 30 (*)',
       'MN Deuda Directa Cobranza Judicial (*)',
       'MN Deuda Indirecta (avales,cartas fianza,credito) (*)',
       'MN Deuda Avalada (*)', 'MN Linea de Credito (*)',
       'MN Creditos Cartigados (*)', 'ME Deuda Directa Vigente (*)',
       'ME Deuda Directa Refinanciada (*)',
       'ME Deuda Directa Venvida < = 30 (*)',
       'ME Deuda Directa Vencida > 30 (*)',
       'ME Deuda Directa Cobranza Judicial (*)',
       'ME Deuda Indirecta (avales,cartas fianza,credito) (*)',
       'ME Deuda Avalada (*)', 'ME Linea de Credito (*)',
       'ME Creditos Cartigados (*)', 'Calificación(*)',
       'N° de Días Vencidos o Morosos ( * )', 'Dirección', 'Distrito',
       'Provincia', 'Departamento', 'Telefono', 'Estado',
       'Fecha de Vencimiento (*)']

df_avales = df_resultado[columnas]

df_sentinel = df_sentinel[columnas]

#%%
# ahora vamos a asignar el monto de la columna 'MN Deuda Avalada (*)' al reporte original

df_avales_copia = df_avales.copy()
df_avales_copia = df_avales_copia.drop_duplicates(subset='Cod. Prestamo', keep='first')
df_avales_reducido = df_avales_copia[['Cod. Prestamo', 'MN Deuda Avalada (*)']]
df_avales_reducido = df_avales_reducido.rename(columns={'Cod. Prestamo': 
                                                        'Cod. Prestamo_avales'})
df_avales_reducido = df_avales_reducido.rename(columns={'MN Deuda Avalada (*)': 
                                                        'MN Deuda Avalada (*)_avales'})


#hacemos el merge para asignar esa columna al otro
df_sentinel_avales = df_sentinel.merge(df_avales_reducido, ##########################################################
                         left_on=['Cod. Prestamo'], 
                         right_on=['Cod. Prestamo_avales']
                         ,how='left')

df_sentinel_avales['MN Deuda Avalada (*)_avales'].fillna(0, inplace=True)
df_sentinel_avales['MN Deuda Avalada (*)'] = df_sentinel_avales['MN Deuda Avalada (*)_avales']

#%%
#antes de la unión, eliminamos posibles espacios en blanco porque los he detectado

'este código lo he comentado porque por alguna razón eliminaba el dni :c'
#df_sentinel_avales['''N° Documento
#Identidad (*)  DNI o RUC'''] = df_sentinel_avales['''N° Documento
#Identidad (*)  DNI o RUC'''].str.strip()


df_avales['''N° Documento
Identidad (*)  DNI o RUC'''] = df_avales['''N° Documento
Identidad (*)  DNI o RUC'''].str.strip()

#%%

'aqui tenemos que modificar la columna de los avales de la MN Deuda Avalada (*), porque aquí debe ir todo, incluyendo los saldos castigados'

df_avales['MN Deuda Avalada (*)'] = df_avales['MN Deuda Avalada (*)']  + df_avales['MN Creditos Cartigados (*)']
df_avales['MN Creditos Cartigados (*)'] = 0

#%%
'hasta aquí ya está todo lo numérico, solo falta reemplazar los datos personales de los avales'
#limpiamos los datos
df_avales['Razon Social (*)'] = ''
df_avales['''N° Documento
Identidad (*)  DNI o RUC'''] = df_avales['''N° Documento
Identidad (*)  DNI o RUC'''].str.strip()

#CAMBIAMOS LOS NOMBRES PARA QUE NO HAYA NINGUNA AMBIGUEDAD
avales_datos_separados = avales_datos_separados.rename(columns={'NumeroDocIdentidad': 'dni para merge'})
avales_datos_separados = avales_datos_separados.rename(columns={'ApellidoPaterno': 'A paterno para merge'})
avales_datos_separados = avales_datos_separados.rename(columns={'ApellidoMaterno': 'A materno para merge'})
avales_datos_separados = avales_datos_separados.rename(columns={'Nombres': 'nombres para merge'})
avales_datos_separados = avales_datos_separados.rename(columns={'NombreDomicilioDNI': 'domicilio para merge'})
avales_datos_separados = avales_datos_separados.rename(columns={'Distrito': 'distrito para merge'})
avales_datos_separados = avales_datos_separados.rename(columns={'Provincia': 'provincia para merge'})
avales_datos_separados = avales_datos_separados.rename(columns={'Dpto': 'dpto para merge'})

#UNIMOS LOS DATAFRAMES
df_avales_mergeado = df_avales.merge(avales_datos_separados,
                                     left_on=['''N° Documento
Identidad (*)  DNI o RUC'''], 
                                     right_on=['dni para merge']
                                     ,how='left')
                                              
#ASIGNAMOS LOS DATOS DE LOS AVALES A LAS COLUMNAS CORRESPONDIENTES                                    
df_avales_mergeado['Apellido Paterno (*)'] = df_avales_mergeado['A paterno para merge']                                        
df_avales_mergeado['Apellido Materno (*)'] = df_avales_mergeado['A materno para merge']                                        
df_avales_mergeado['Nombres (*)'] = df_avales_mergeado['nombres para merge']                                        
df_avales_mergeado['Dirección'] = df_avales_mergeado['domicilio para merge']                                        
df_avales_mergeado['Distrito'] = df_avales_mergeado['distrito para merge']                                        
df_avales_mergeado['Provincia'] = df_avales_mergeado['provincia para merge']                                        
df_avales_mergeado['Departamento'] = df_avales_mergeado['dpto para merge']                                        
df_avales_mergeado['Telefono'] = df_avales_mergeado['Celular1']                                        

#eliminamos las columnas que ya no necesitamos
df_avales_mergeado.drop(['dni para merge'], axis=1, inplace=True)
df_avales_mergeado.drop(['A paterno para merge'], axis=1, inplace=True)
df_avales_mergeado.drop(['A materno para merge'], axis=1, inplace=True)
df_avales_mergeado.drop(['nombres para merge'], axis=1, inplace=True)
df_avales_mergeado.drop(['domicilio para merge'], axis=1, inplace=True)
df_avales_mergeado.drop(['distrito para merge'], axis=1, inplace=True)
df_avales_mergeado.drop(['provincia para merge'], axis=1, inplace=True)
df_avales_mergeado.drop(['dpto para merge'], axis=1, inplace=True)
df_avales_mergeado.drop(['Celular1'], axis=1, inplace=True)
df_avales_mergeado.drop(['Celular2'], axis=1, inplace=True)
df_avales_mergeado.drop(['TelefonoFijo1'], axis=1, inplace=True)

#%%
#unimos todo

reporte = pd.concat([df_sentinel_avales,df_avales_mergeado], ignore_index=True)

#%%
#hay dos columnas al final que debemos eliminar
reporte.drop(["Cod. Prestamo_avales"], axis=1, inplace=True)
reporte.drop(["MN Deuda Avalada (*)_avales"], axis=1, inplace=True)

#%%
#Arreglando la columna final de fechas de vencimiento:

# Convertir la columna 'Fecha de Vencimiento (*)' a objetos de fecha
reporte['Fecha de Vencimiento (*)'] = pd.to_datetime(reporte['Fecha de Vencimiento (*)'])

# Aplicar formato de fecha específico
reporte['Fecha de Vencimiento (*)'] = reporte['Fecha de Vencimiento (*)'].dt.strftime('%d/%m/%Y')

#%% ojo con esto
df_sentinel = reporte.copy()

#%%
#correcciones variadas (datos malardos)
#esta primera parte sirve para crear un dataframe y verificar si está filtrando bien
#para usarlo meter todo lo que está en paréntesis

#STRIP DE TEXTO PARA ELIMINAR LOS ESPACIOS VACÍOS
df_sentinel['Apellido Paterno (*)'] = df_sentinel['Apellido Paterno (*)'].str.strip()
df_sentinel['Apellido Materno (*)'] = df_sentinel['Apellido Materno (*)'].str.strip()
df_sentinel['Nombres (*)'] = df_sentinel['Nombres (*)'].str.strip()
df_sentinel['''N° Documento
Identidad (*)  DNI o RUC'''] = df_sentinel['''N° Documento
Identidad (*)  DNI o RUC'''].str.strip()

x_nulos = df_sentinel[df_sentinel['''N° Documento
Identidad (*)  DNI o RUC'''].isnull()]

x = (df_sentinel['Apellido Paterno (*)'] == 'HUANCA') & \
    (df_sentinel['Apellido Materno (*)'] == 'TREVEJO') & \
    (df_sentinel['Nombres (*)'] == 'MIGUEL ANGEL')
                
X = df_sentinel[x]
###############
# a partir de aquí hay correcciones
df_sentinel.loc[(df_sentinel['Apellido Paterno (*)'] == 'HUANCA') & \
                (df_sentinel['Apellido Materno (*)'] == 'TREVEJO') & \
                (df_sentinel['Nombres (*)'] == 'MIGUEL ANGEL'), '''N° Documento
Identidad (*)  DNI o RUC'''] = '72618103'

df_sentinel.loc[(df_sentinel['Apellido Paterno (*)'] == 'CASTRO') & \
                (df_sentinel['Apellido Materno (*)'] == 'CAMALA') & \
                (df_sentinel['Nombres (*)'] == 'CIRIACO'), '''N° Documento
Identidad (*)  DNI o RUC'''] = '23909762'

df_sentinel.loc[(df_sentinel['Apellido Paterno (*)'] == 'AGUILAR') & \
                (df_sentinel['Apellido Materno (*)'] == 'PUMA') & \
                (df_sentinel['Nombres (*)'] == 'DAJHAN EDILIA'), '''N° Documento
Identidad (*)  DNI o RUC'''] = '46232628'

df_sentinel.loc[(df_sentinel['Apellido Paterno (*)'] == 'CORRALES') & \
                (df_sentinel['Apellido Materno (*)'] == 'RADO') & \
                (df_sentinel['Nombres (*)'] == 'ROMEL CESAR'), '''N° Documento
Identidad (*)  DNI o RUC'''] = '42112578' #ESTE NO FUNCIONÓ POR ALGUNA RAZÓN

df_sentinel.loc[(df_sentinel['''N° Documento
Identidad (*)  DNI o RUC'''] == '41012851') & \
                (df_sentinel['Apellido Materno (*)'] == 'VASQUEZ') & \
                (df_sentinel['Nombres (*)'] == 'RINA LORENA'),
                'Apellido Paterno (*)'] = 'VILLARROEL'

df_sentinel.loc[(df_sentinel['''N° Documento
Identidad (*)  DNI o RUC'''] == '72152634') & \
                (df_sentinel['Apellido Paterno (*)'] == 'DAVILA') & \
                (df_sentinel['Apellido Materno (*)'] == 'GARCIA'),
                'Apellido Paterno (*)'] = 'ANALUCIA'

df_sentinel.loc[(df_sentinel['''N° Documento
Identidad (*)  DNI o RUC'''] == '41161598') & \
                (df_sentinel['Apellido Materno (*)'] == 'DEZA') & \
                (df_sentinel['Nombres (*)'] == 'VANIA FABIOLA'),
                'Apellido Paterno (*)'] = 'GONZALEZ'
                 
df_sentinel.loc[(df_sentinel['''N° Documento
Identidad (*)  DNI o RUC'''] == '43552557') & \
                (df_sentinel['Apellido Materno (*)'] == 'ÑAUPAS') & \
                (df_sentinel['Nombres (*)'] == 'ELIAZAR'),
                'Apellido Paterno (*)'] = 'GARGORIVICHE'
                 
df_sentinel.loc[(df_sentinel['Apellido Paterno (*)'] == 'JUMBO') & \
                (df_sentinel['Apellido Materno (*)'] == 'OTERO') & \
                (df_sentinel['''N° Documento
Identidad (*)  DNI o RUC'''] == '42908481'), 'Nombres (*)'] = 'DARWIN'

#CAMBIANDO EL AVAL DE UN CRÉDITO EN ESPECÍFICO
mascara_booleana =  (df_sentinel['Apellido Paterno (*)'] == 'DURAND') & \
                    (df_sentinel['Apellido Materno (*)'] == 'SERNAQUE') & \
                    (df_sentinel['Nombres (*)'] == 'MARIA ISABEL') & \
                    (df_sentinel['Cod. Prestamo'] == '00031413-00079529')
                    
df_sentinel.loc[mascara_booleana, ['''N° Documento
Identidad (*)  DNI o RUC''', 
                                    'Apellido Paterno (*)', 
                                    'Apellido Materno (*)',
                                    'Nombres (*)',
                                    'Dirección',
                                    'Distrito',
                                    'Provincia',
                                    'Departamento',
                                    'Telefono']] = ['18125475', 
                            'GUEVARA', 
                            'RODRIGUEZ DE MUÑOZ',
                            'RUBY LIZ',
                            'NULL',
                            'NULL',
                            'NULL',
                            'NULL',
                            'NULL'] #ESTO TAMPOCO HA FUNCIONADO, INVESTIGAR

#%% arreglo de ME Deuda Avalada (*) estaba quedando este valor para los no avales

df_sentinel['Tipo Persona (*)'] = df_sentinel['Tipo Persona (*)'].astype(str).str.strip()

def arreglo_me_deuda_avalada(df_sentinel):
    if df_sentinel['Tipo Persona (*)'] in ['1', '2']:
        return 0
    else:
        return df_sentinel['MN Deuda Avalada (*)']
    
df_sentinel['MN Deuda Avalada (*)'] = df_sentinel.apply(arreglo_me_deuda_avalada, axis=1)

#%% debe ir 1 en Estado
# si es castigado

def estado_castigado(df_sentinel):
    if df_sentinel['MN Creditos Cartigados (*)'] > 0:
        return 1
    else:
        return ""
    
df_sentinel['Estado'] = df_sentinel.apply(estado_castigado, axis=1)

#%%

try:
    ruta = "sentinel.xlsx"
    os.remove(ruta)
except FileNotFoundError:
    pass


df_sentinel.to_excel('sentinel.xlsx', index=False)


#NO HA FUNCIONADO PONER LOS DATOS DE LOS AVALES
