# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 12:37:47 2023

@author: Joseph Montoya
"""
'''
#####################################
#   REPORTE PARA SENTINEL-EXPERIAN  #
#####################################
'''

#%% importación de módulos
import pandas as pd
import os
import numpy as np

#%% ANEXO 06 PARA SACAR ALGUNOS DATOS DE AQUÍ
FECHA_CORTE = 'AGOSTO 2023'
ubi = 'C:\\Users\\sanmiguel38\\Desktop\\TRANSICION  ANEXO 6\\2023 AGOSTO\\fase 3'
nombre = 'Rpt_DeudoresSBS Anexo06 - AGOSTO 2023 PROCESADO 03 FINAL.xlsx'
filas_para_skip = 2
#%% DATOS DEL REPORTE INSUMO PRINCIPAL
directorio = "C:\\Users\\sanmiguel38\\Desktop\\SENTINEL EXPERIAN\\2023 AGOSTO"

insumo_principal = "SM_0823 - SENTINEL-EXPERIAN CART VIGENTE Y VENCIDA - AGOSTO-23 - INSUMO.xlsx"

# en la misma ubicación que tenemos el archivo en bruto, debemos poner los avales
# estos avales los sacamos del Fincore con los siguientes botones:
# REPORTES / CREDITO /PRESTAMOS OTORGADOS / REGISTRO DE AVALES Y-O GARANTÍAS 
avales = 'Rpt_Avales.xlsx'

# AVALES SEPARADOS QUE ENVÍA CESAR #esto vamos a cambiarlo por una lectura SQL
ubi_avales_separados = 'C:\\Users\\sanmiguel38\\Desktop\\SENTINEL EXPERIAN\\2023 AGOSTO'

avales_separados = 'Avales SM - corte 08-09-23.xlsx'

#%% CALIFICACIÓN CON ALINEAMIENTO, PROVENIENTE DEL ANEXO 06
ubicacion_calificacion = 'C:\\Users\\sanmiguel38\\Desktop\\TRANSICION  ANEXO 6\\2023 AGOSTO'

nombre_calif_experian = 'calificacion para reporte experian.xlsx'
#%% IMPORTACIÓN DE ARCHIVOS
df_fincore = pd.read_excel(ubi + '\\'  + nombre,
                           dtype = {'Nro Prestamo \nFincore' : object,
                                    'Numero de Crédito 18/'  : object},
                           skiprows = filas_para_skip)

df_fincore.dropna(subset=['Nro Prestamo \nFincore',
                          'Numero de Crédito 18/'], 
                  inplace = True, 
                  how     = 'all')

#LIMPIEZA DE ESPACIOS
df_fincore['Nro Prestamo \nFincore'] = df_fincore['Nro Prestamo \nFincore'].astype(str)
df_fincore['Nro Prestamo \nFincore'] = df_fincore['Nro Prestamo \nFincore'].str.strip()
df_fincore['Numero de Crédito 18/']  = df_fincore['Numero de Crédito 18/'].astype(str)
df_fincore['Numero de Crédito 18/']  = df_fincore['Numero de Crédito 18/'].str.strip()

#generamos el anexo para las saldos descapitalizados
anexo_06_descap = df_fincore[['Nro Prestamo \nFincore',
                              'Numero de Crédito 18/',
                              'Capital Vigente 26/',
                              'Capital Refinanciado 28/',
                              'Capital Vencido 29/',
                              'Capital en Cobranza Judicial 30/',
                              'Saldos de Créditos Castigados 38/']]

#anexo para relacionar nro fincore con nro crédito 18/
df_fincore['NumerodeCredito18'] = df_fincore['Numero de Crédito 18/']
df_fincore['Nro_Fincore'] = df_fincore['Nro Prestamo \nFincore']

df_fincore = df_fincore[['NumerodeCredito18', 'Nro_Fincore']]

df_fincore['NumerodeCredito18'] = df_fincore['NumerodeCredito18'].str.strip()
df_fincore['Nro_Fincore'] = df_fincore['Nro_Fincore'].str.strip()

del ubi
del nombre

#%% LECTURA DEL REPORTE EN BRUTO
##############################################
#      REPORTE INSUMO PRINCIPAL
##############################################
#importamos el archivo sentinel bruto, que nos manda Cesar o Denisse
ubicacion = directorio
os.chdir(ubicacion) #aqui se cambia el directorio de trabajo

df_sentinel=pd.read_excel(insumo_principal,    # aqui se cambia el nombre del archivo si es necesario
                  dtype={
                      'Fecha del\nPeriodo\n(*)'         : object, 
                      'Codigo\nEntidad\n(*)'            : object,
                      'Tipo\nDocumento\nIdentidad (*)'  : object,
                      'N° Documento\nIdentidad (*)  DNI o RUC' : str,
                      'Tipo Persona (*)'                : object,
                      'Modalidad de Credito (*)'        : object
                        })

#limpieza de filas vacías
df_sentinel.dropna(subset=['Cod. Prestamo', 
                           'N° Documento\nIdentidad (*)  DNI o RUC',
                           'Razon Social (*)',
                           'Apellido Paterno (*)'], 
                   inplace = True, 
                   how     = 'all')

#eliminación de duplicados
df_sentinel = df_sentinel.drop_duplicates(subset='Cod. Prestamo')


#para segurarnos que sea STR (no parece que sea muy necesario)

df_sentinel['Fecha del\nPeriodo\n(*)']          = df_sentinel['Fecha del\nPeriodo\n(*)'].astype(str)
df_sentinel['Codigo\nEntidad\n(*)']             = df_sentinel['Codigo\nEntidad\n(*)'].astype(str)
df_sentinel['Tipo\nDocumento\nIdentidad (*)']   = df_sentinel['Tipo\nDocumento\nIdentidad (*)'].astype(str)
df_sentinel['N° Documento\nIdentidad (*)  DNI o RUC'] = df_sentinel['N° Documento\nIdentidad (*)  DNI o RUC'].astype(str)
df_sentinel['Modalidad de Credito (*)']         = df_sentinel['Modalidad de Credito (*)'].astype(str)

df_sentinel['Apellido Paterno (*)'] = df_sentinel['Apellido Paterno (*)'].astype(str)
df_sentinel['Apellido Materno (*)'] = df_sentinel['Apellido Materno (*)'].astype(str)
df_sentinel['Nombres (*)']          = df_sentinel['Nombres (*)'].astype(str)

df_sentinel['Apellido Paterno (*)'] = df_sentinel['Apellido Paterno (*)'].str.strip()
df_sentinel['Apellido Materno (*)'] = df_sentinel['Apellido Materno (*)'].str.strip()
df_sentinel['Nombres (*)']          = df_sentinel['Nombres (*)'].str.strip()

#%% DESCAPITALIZACIÓN DE LOS SALDOS

df_fincore = df_fincore.rename(columns={'NumerodeCredito18': 
                                        'cod pres para merge'})
    
df_sentinel['Cod. Prestamo'] = df_sentinel['Cod. Prestamo'].str.strip()
df_fincore['cod pres para merge'] = df_fincore['cod pres para merge'].str.strip()

# columna solo con el nro de prestamos 18/
df_sentinel['cod pres para merge'] = df_sentinel['Cod. Prestamo'].str.split('-', expand=True)[1] #potente este código ah

df_sentinel['cod pres para merge'] = df_sentinel['cod pres para merge'].str.strip()

#merge
df_sentinel = df_sentinel.merge(df_fincore, 
                                on='cod pres para merge', 
                                how='left')

df_sentinel.drop(['cod pres para merge'], axis=1, inplace=True)

#%%% verifiación de nulos

sin_match = df_sentinel[pd.isna(df_sentinel['Nro_Fincore'])]
print(sin_match.shape[0])
print("si sale más de cero hay que revisar, pues signfica que hay espacios vacíos en la columna Nro_Fincore")
if sin_match.shape[0] > 0:
    print(sin_match)
else:
    ''

# código para eliminar los que no han hecho match (no están en el anexo 06)
df_sentinel = df_sentinel.dropna(subset=['Nro_Fincore'])

#%% AÑADIENDO SALDOS DESCAPITALIZADOS
anexo_06_descap = anexo_06_descap.rename(columns={'Nro Prestamo \nFincore': 
                                                  'Nro_Fincore'})
df_sentinel = df_sentinel.merge(anexo_06_descap, 
                                on='Nro_Fincore', 
                                how='left')

df_sentinel['ME Deuda Directa Vigente (*)'] =                   0
df_sentinel['ME Deuda Directa Refinanciada (*)'] =              0
df_sentinel['ME Deuda Directa Venvida < = 30 (*)'] =            0
df_sentinel['ME Deuda Directa Vencida > 30 (*)'] =              0
df_sentinel['ME Deuda Directa Cobranza Judicial (*)'] =         0
df_sentinel['ME Deuda Indirecta (avales,cartas fianza,credito) (*)'] = 0
df_sentinel['ME Deuda Avalada (*)'] =               0
df_sentinel['ME Linea de Credito (*)'] =            ''
df_sentinel['ME Creditos Cartigados (*)'] =         0


df_sentinel['MN Deuda Directa Vigente (*)']         = df_sentinel['Capital Vigente 26/'] 
df_sentinel['MN Deuda Directa Refinanciada (*)']    = df_sentinel['Capital Refinanciado 28/'] 
df_sentinel['MN Deuda Directa Venvida < = 30 (*)']  = 0 
df_sentinel['MN Deuda Directa Vencida > 30 (*)']    = df_sentinel['Capital Vencido 29/'] 
df_sentinel['MN Deuda Directa Cobranza Judicial (*)'] = df_sentinel['Capital en Cobranza Judicial 30/'] 
df_sentinel['MN Deuda Indirecta (avales,cartas fianza,credito) (*)'] = 0 
df_sentinel['MN Deuda Avalada (*)']                 = 0
df_sentinel['MN Linea de Credito (*)']              = ''
df_sentinel['MN Creditos Cartigados (*)']           = df_sentinel['Saldos de Créditos Castigados 38/']

#%% ELIMINAMOS LAS COLUMNAS QUE YA NO NECESITAMOS
df_sentinel.drop(["Nro_Fincore"],                       axis=1, inplace=True)
df_sentinel.drop(["Numero de Crédito 18/"],             axis=1, inplace=True)
df_sentinel.drop(["Capital Vigente 26/"],               axis=1, inplace=True)
df_sentinel.drop(["Capital Refinanciado 28/"],          axis=1, inplace=True)
df_sentinel.drop(["Capital Vencido 29/"],               axis=1, inplace=True)
df_sentinel.drop(["Capital en Cobranza Judicial 30/"],  axis=1, inplace=True)
df_sentinel.drop(["Saldos de Créditos Castigados 38/"], axis=1, inplace=True)

#%%% cambio de nombre
df_fincore = df_fincore.rename(columns={'cod pres para merge': 
                                        'NumerodeCredito18'})

#%%% corrección recurrente
#ya que todos los meses se duplican los datos del socio AGUILA	FEBRES	MIGUEL ALBERTO
#antes de eliminar sus datos duplicados, vamos a etiquetar su 'Tipo Documento Identidad(*)' = 1
df_sentinel.loc[(df_sentinel['N° Documento\nIdentidad (*)  DNI o RUC'] == '02803330') & \
                (df_sentinel['Apellido Paterno (*)'] == 'AGUILA') & \
                (df_sentinel['Apellido Materno (*)'] == 'FEBRES'),
                'Tipo\nDocumento\nIdentidad (*)'] = '1'

print('si sale más de cero, es porque hay espacios vacíos en la columna TIPO DOCUMENTO IDENTIDAD:')
print(df_sentinel[pd.isna(df_sentinel['Tipo\nDocumento\nIdentidad (*)'])].shape[0])
    
#%%% verificación de duplicados
#AQUI DEBEMOS VERIFICAR SI EXISTEN DUPLICADOS
#SI EXISTE DEBEMOS HACER UNA CORRECCIÓN MANUAL

# Encontrar las filas que tienen valores duplicados en la columna "nombre"
mask = df_sentinel['Cod. Prestamo'].duplicated(keep = False)

# Indexar el DataFrame original con la máscara booleana para obtener las filas correspondientes
df_duplicados = df_sentinel[mask]

# Imprimir el nuevo DataFrame
print(df_duplicados.shape[0])

#si hay duplicados vamos a investigarlos y eliminarlos
#si hay duplicados posiblemente está mal la columna 'Tipo Documento Identidad(*)'
#debemos arreglarlo

#%%% eliminación de duplicados

df_sentinel = df_sentinel.drop_duplicates(subset='Cod. Prestamo')

#%% IMPORTACIÓN DE LOS AVALES
##############################################
#   AVALES: OBTENIDO DEL FINCORE
##############################################
# en la misma ubicación que tenemos el archivo en bruto, debemos poner los avales
# estos avales los sacamos del Fincore con los siguientes botones:
# REPORTES / CREDITO /PRESTAMOS OTORGADOS / REGISTRO DE AVALES Y-O GARANTÍAS 
ruta = avales
df1=pd.read_excel(ruta,
                  dtype={'Nro Docto\nAval': object,
                         'Nro Docto\nSocio': object,
                         'Numero':object},
                         skiprows=8)

#%% EL REPORTE DE AVALES QUE ENVÍA CESAR, con columnas separadas (REEMPLAZAR POR SQL)
##############################################
#      AVALES: COLUMNAS SEPARADAS
##############################################
# ARCHIVO DE AVALES QUE NOS MANDA CESAR, LOS APELLIDOS Y NOMBRES ESTÁN EN COLUMNAS
# es el archivo que contiene los datos de los avales, pero separados en columnas (apellido paterno, materno, nombres
# domicilio, distrito, provincia, dpto, celulares)
ruta = ubi_avales_separados
avales_datos_separados = pd.read_excel(ruta + '\\' + avales_separados,
                                       dtype={'NumeroDocIdentidad': str,
                                              'Celular1': str,
                                              'Celular2': str,
                                              'TelefonoFijo1': str})
del ruta
avales_datos_separados['NumeroDocIdentidad'] = avales_datos_separados['NumeroDocIdentidad'].str.strip()

#ELIMINAMOS LOS POSIBLES DUPLICADOS
avales_datos_separados = avales_datos_separados.drop_duplicates(subset='NumeroDocIdentidad')

#%% importando la calificación del anexo06 del mismo mes
##############################################
#      CALIFICACIÓN DE LOS CRÉDITOS
##############################################
#REALIZANDO UNA CALIFICACIÓN UNIFICADA PARA EL REPORTE DE SENTINEL, EXPERIAN, CALIFICACIÓN QUE SALE DEL ANEXO 06

calif_experian_importacion = ubicacion_calificacion + '\\' + nombre_calif_experian

calif_anx06 = pd.read_excel(calif_experian_importacion,
                            dtype={'cod socio para merge': str})

df_sentinel['cod socio para mergear'] = df_sentinel['Cod. Prestamo'].str.split('-', expand=True)[0] #potente este código ah

#merge
df_sentinel = df_sentinel.merge(calif_anx06,
                                left_on  = ['cod socio para mergear'], 
                                right_on = ['cod socio para merge'],
                                how      = 'left')

df_sentinel.drop(['cod socio para merge'], 
                 axis=1, 
                 inplace=True)

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

#%% (desactivado)EN CASO DE QUE LOS CRÉDITOS EN DÓLARES NO ESTÉN SOLARIZADOS
#456'MULTIPLICACIÓN DE LOS SALDOS EN DÓLARES POR EL TIPO DE CAMBIO DEL MES'

#456tipo_cambio = 3.628

#456df_sentinel['ME Deuda Directa Vigente (*)'] = \
#456df_sentinel['ME Deuda Directa Vigente (*)'].fillna(0) * tipo_cambio
#456df_sentinel['ME Deuda Directa Refinanciada (*)'] = \
#456df_sentinel['ME Deuda Directa Refinanciada (*)'].fillna(0) * tipo_cambio
#456df_sentinel['ME Deuda Directa Venvida < = 30 (*)'] = \
#456df_sentinel['ME Deuda Directa Venvida < = 30 (*)'].fillna(0) * tipo_cambio
#456df_sentinel['ME Deuda Directa Vencida > 30 (*)'] = \
#456df_sentinel['ME Deuda Directa Vencida > 30 (*)'].fillna(0) * tipo_cambio
#456df_sentinel['ME Deuda Directa Cobranza Judicial (*)'] = \
#456df_sentinel['ME Deuda Directa Cobranza Judicial (*)'].fillna(0) * tipo_cambio
#456df_sentinel['ME Deuda Indirecta (avales,cartas fianza,credito) (*)'] = \
#456df_sentinel['ME Deuda Indirecta (avales,cartas fianza,credito) (*)'].fillna(0) * tipo_cambio
#456df_sentinel['ME Deuda Avalada (*)'] = \
#456df_sentinel['ME Deuda Avalada (*)'].fillna(0) * tipo_cambio
#456df_sentinel['ME Linea de Credito (*)'] = \
#456df_sentinel['ME Linea de Credito (*)'].fillna(0) * tipo_cambio
#456df_sentinel['ME Creditos Cartigados (*)'] = \
#456df_sentinel['ME Creditos Cartigados (*)'].fillna(0) * tipo_cambio

#%% ASIGNACIÓN DE CALIFICACIÓN
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

df_sentinel['Calificación(*)'] = df_sentinel['Calificación(*)'].astype(int)

#%% SUMA HORIZONTAL MN
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
    
#%% SUMA HORIZONTAL ME
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

#%% SUMA DE CASTIGADOS Y TODO LO PONEMOS EN MONEDA NACIONAL
#SUMA DE LOS CASTIGADOS, y le ponemos cero a los que están en dólares
df_sentinel['MN Creditos Cartigados (*)'] = df_sentinel['MN Creditos Cartigados (*)'] + df_sentinel['ME Creditos Cartigados (*)']
df_sentinel['ME Creditos Cartigados (*)'] = 0

#%% PASANDO VALORES A LA MONEDA NACIONAL 
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

#%% COLOCANDO CEROS
# ponemos ceros a las columnas donde van los montos de los avales
df_sentinel['MN Deuda Indirecta (avales,cartas fianza,credito) (*)'] = 0
df_sentinel['MN Deuda Avalada (*)'] = 0

#%% preparación para el merge
#para concatenar las columnas, nos quedamos con un archivo que solo servirá para el merge

#aqui estamos creando una columna que va a tener el nombre del aval + el numero del crédito,
#servirá para quedarnos con los valores únicos, ya que se repiten los avales en algunos casos
df1['concatenacion'] = df1['Aval'].apply(str) + ' ' + df1['Numero'].apply(str)

#creamos un nuevo dataframe solo con estas columnas
df1_filtrado = df1[['Nro Docto\nAval',
                    'Aval', 
                    'Numero',
                    'Nro Docto\nSocio', 
                    'concatenacion']]

#le cambiamos de nombre a dos columnas
df1_filtrado = df1_filtrado.rename(columns={'Nro Docto\nAval': 
                                            'Dni - Asociado - indirecta2'})
df1_filtrado = df1_filtrado.rename(columns={'Nro Docto\nSocio': 
                                            'dni socio'})

#eliminamos las filas duplicadas en función de la columna 'concatenación'
valores_unicos = df1_filtrado.drop_duplicates(subset = 'concatenacion', 
                                              keep   = 'first')

#creamos la columna fincore en función del nro de crédito en la columna 'Numero',
#la cual tiene texto en el siguiente formado: '01-00079529' y nos quedaremos con '00079529'
valores_unicos.loc[:, 'fincore'] = valores_unicos['Numero'].str.split('-').str[1]

#eliminamos las filas donde haya NAN en las columnas 'Dni - Asociado - indirecta2' y 'Aval'
valores_unicos = valores_unicos.dropna(subset=['Dni - Asociado - indirecta2', 'Aval'])

#valores_unicos['fincore']

#%% merge que servirá para poner numero de fincore al reporte de sentinel (solo tiene credito18)
'aqui podrían duplicarse créditos'

#tenemos una columna que tiene esta estrucutra de datos '00000007-00099116'
#lo que hacemos es quedarnos con la segunda parte, que corresponde con el nro de crédito
df_sentinel.loc[:, 'credito18'] = df_sentinel['Cod. Prestamo'].str.split('-').str[1]

#aqui le quitamos posibles espacios vacíos en el nombre
df_sentinel['credito18'] = df_sentinel['credito18'].str.strip()

#ahora que tenemos el número de crédito 18, le hacemos un merge con la columna fincore
    
df_sentinel_fincore = df_sentinel.merge(df_fincore, ##########################################################
                                        left_on   = ['credito18'], 
                                        right_on  = ['NumerodeCredito18'],
                                        how       = 'left')

#df_sentinel_fincore.columns
#df_sentinel_fincore.to_excel('333.xlsx', index=False)

#PARA VER ALGUNAS COSAS
#df_fincore[df_fincore['NumerodeCredito18'] == '004663']

#%% verificación match completo

#codigo para verificar que haya habido un match completo
match_incompleto = df_sentinel_fincore.loc[df_sentinel_fincore['Nro_Fincore'].isna()]
print(match_incompleto.shape[0])
print('si sale 0 significa que hizo el match correctamente')
if match_incompleto.shape[0] > 0:
    print('investigar, no hubo match completo')
#si hay datos, hay que investigar quiapasau

#%% MERGE CON AVALES
'todo bien actualmente'
#hacemos un merge que solo nos dejará con la tabla de avales
df_resultado = df_sentinel_fincore.merge(valores_unicos, 
                                         left_on  = ['Nro_Fincore'], 
                                         right_on = ['fincore'],
                                         how      = 'inner')

#%% dni avales
#ESTA ES LA PARTE EN LA QUE ARREGLAMOS EL DNI DEL AVAL, CREO QUE AQUÍ TAMBIÉN DEBERÍAMOS PONER
#LOS DATOS PERSONALES DE LOS AVALES CUANDO TENGAMOS ESE REPORTE
#
df_resultado['N° Documento\nIdentidad (*)  DNI o RUC'] = df_resultado['Dni - Asociado - indirecta2']

#%% tipo de persona
#a esta tabla de avales le ponemos 3 en 'Tipo Persona (*)'
df_resultado['Tipo Persona (*)'] = '3'

df_resultado['Tipo\nDocumento\nIdentidad (*)'] = '1'
#df_resultado = df_resultado.drop_duplicates(subset=['Cod. Prestamo', '''N° Documento
#Identidad (*)  DNI o RUC'''], keep='first')

#%% MONTO DE LA DEUDA AVALADA
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


#%% ORDENAMIENTO DE COLUMNAS

df_resultado['Estado'] = ''
df_sentinel['Estado']  = ''
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

#%% MONTO DE LA DEUDA AVALADA
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

#%% eliminación de espacios vacíos
#antes de la unión, eliminamos posibles espacios en blanco porque los he detectado

'este código lo he comentado porque por alguna razón eliminaba el dni :c'
#df_sentinel_avales['''N° Documento
#Identidad (*)  DNI o RUC'''] = df_sentinel_avales['''N° Documento
#Identidad (*)  DNI o RUC'''].str.strip()

df_avales['N° Documento\nIdentidad (*)  DNI o RUC'] = df_avales['N° Documento\nIdentidad (*)  DNI o RUC'].str.strip()

#%% TAMBIÉN PONEMOS EL MONTO CASTIGADOS EN EL MONTO AVALADO SI ES QUE TIENEN AVALES

'aqui tenemos que modificar la columna de los avales de la MN Deuda Avalada (*), porque aquí debe ir todo, incluyendo los saldos castigados'

df_avales['MN Deuda Avalada (*)'] = df_avales['MN Deuda Avalada (*)']  + df_avales['MN Creditos Cartigados (*)']
df_avales['MN Creditos Cartigados (*)'] = 0

#%% DATOS PERSONALES DE LOS AVALES
'hasta aquí ya está todo lo numérico, solo falta reemplazar los datos personales de los avales'
#limpiamos los datos
df_avales['Razon Social (*)'] = ''
df_avales['N° Documento\nIdentidad (*)  DNI o RUC'] = df_avales['N° Documento\nIdentidad (*)  DNI o RUC'].str.strip()

#CAMBIAMOS LOS NOMBRES PARA QUE NO HAYA NINGUNA AMBIGUEDAD
avales_datos_separados = avales_datos_separados.rename(columns={'NumeroDocIdentidad': 'dni para merge'})
avales_datos_separados = avales_datos_separados.rename(columns={'ApellidoPaterno'   : 'A paterno para merge'})
avales_datos_separados = avales_datos_separados.rename(columns={'ApellidoMaterno'   : 'A materno para merge'})
avales_datos_separados = avales_datos_separados.rename(columns={'Nombres'           : 'nombres para merge'})
avales_datos_separados = avales_datos_separados.rename(columns={'NombreDomicilioDNI': 'domicilio para merge'})
avales_datos_separados = avales_datos_separados.rename(columns={'Distrito'          : 'distrito para merge'})
avales_datos_separados = avales_datos_separados.rename(columns={'Provincia'         : 'provincia para merge'})
avales_datos_separados = avales_datos_separados.rename(columns={'Dpto'              : 'dpto para merge'})

#UNIMOS LOS DATAFRAMES

df_avales['dni para merge'] = df_avales['N° Documento\nIdentidad (*)  DNI o RUC'].astype(int).astype(str)
avales_datos_separados['dni para merge'] = avales_datos_separados['dni para merge'].astype(int).astype(str)

df_avales_mergeado = df_avales.merge(avales_datos_separados,
                                     left_on  = ['dni para merge'], 
                                     right_on = ['dni para merge'],
                                     how      = 'left')
                                              
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

#%% CONCATENAMOS LOS AVALES CON LA LISTA DE CRÉDITOS

#eliminamos duplicados por si acaso
df_sentinel_avales = df_sentinel_avales.drop_duplicates(subset = 'Cod. Prestamo')

#ahora sí la unión
reporte = pd.concat([df_sentinel_avales,df_avales_mergeado], ignore_index=True)

#%% eliminación de columnas
reporte.drop(["Cod. Prestamo_avales"], axis=1, inplace=True)
reporte.drop(["MN Deuda Avalada (*)_avales"], axis=1, inplace=True)

#%% PARSEO DE FECHAS
#Arreglando la columna final de fechas de vencimiento:

# Convertir la columna 'Fecha de Vencimiento (*)' a objetos de fecha
reporte['Fecha de Vencimiento (*)'] = pd.to_datetime(reporte['Fecha de Vencimiento (*)'])

# Aplicar formato de fecha específico
reporte['Fecha de Vencimiento (*)'] = reporte['Fecha de Vencimiento (*)'].dt.strftime('%d/%m/%Y')

#%% copia
df_sentinel = reporte.copy()

#%% correcciones variadas (datos malardos)

#esta primera parte sirve para crear un dataframe y verificar si está filtrando bien
#para usarlo meter todo lo que está en paréntesis

#STRIP DE TEXTO PARA ELIMINAR LOS ESPACIOS VACÍOS
df_sentinel['Apellido Paterno (*)'] = df_sentinel['Apellido Paterno (*)'].str.strip()
df_sentinel['Apellido Materno (*)'] = df_sentinel['Apellido Materno (*)'].str.strip()
df_sentinel['Nombres (*)'] = df_sentinel['Nombres (*)'].str.strip()
df_sentinel['N° Documento\nIdentidad (*)  DNI o RUC'] = df_sentinel['N° Documento\nIdentidad (*)  DNI o RUC'].str.strip()

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

df_sentinel.loc[(df_sentinel['Apellido Paterno (*)'] == 'RAMIREZ') & \
                (df_sentinel['Apellido Materno (*)'] == 'VILA') & \
                (df_sentinel['''N° Documento
Identidad (*)  DNI o RUC'''] == '06594892'), 'N° Documento\nIdentidad (*)  DNI o RUC'] = '06594882'

#CAMBIANDO EL AVAL DE UN CRÉDITO EN ESPECÍFICO
mascara_booleana =  (df_sentinel['Apellido Paterno (*)'] == 'DURAND') & \
                    (df_sentinel['Apellido Materno (*)'] == 'SERNAQUE') & \
                    (df_sentinel['Nombres (*)'] == 'MARIA ISABEL') & \
                    (df_sentinel['Cod. Prestamo'] == '00031413-00079529')
                    
df_sentinel.loc[mascara_booleana, ['N° Documento\nIdentidad (*)  DNI o RUC', 
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
    if df_sentinel['Tipo Persona (*)'] in ['1', '2', 1, 2]:
        return 0
    else:
        return df_sentinel['MN Deuda Avalada (*)']
    
df_sentinel['MN Deuda Avalada (*)'] = df_sentinel.apply(arreglo_me_deuda_avalada, axis=1)

#%% ESTADO 1 PARA LOS CRÉDITOS CASTIGADOS

def estado_castigado(df_sentinel):
    if df_sentinel['MN Creditos Cartigados (*)'] > 0:
        return 1
    else:
        return ""
    
df_sentinel['Estado'] = df_sentinel.apply(estado_castigado, axis=1)

#%% eliminación de los nan que son texto:
mask = df_sentinel['Apellido Paterno (*)'] == 'nan'
df_sentinel.loc[mask, 'Apellido Paterno (*)'] = ''

mask = df_sentinel['Apellido Materno (*)'] == 'nan'
df_sentinel.loc[mask, 'Apellido Materno (*)'] = ''

mask = df_sentinel['Nombres (*)'] == 'nan'
df_sentinel.loc[mask, 'Nombres (*)'] = ''

#%% especificaciones finales

'finalmente este archivo se llena al formato MIC_RUC_FECHA que envía Experian'
'se debe subir a HÁBITO PAGO'

#%% CREACIÓN DEL EXCEL
nombre_archivo = 'sentinel_experian kho'+ str(FECHA_CORTE) +'.xlsx'
try:
    ruta = nombre_archivo
    os.remove(ruta)
except FileNotFoundError:
    pass

df_sentinel.to_excel(nombre_archivo, index=False)

#%% UBICACIÓN ACTUAL

ubicacion_actual = os.getcwd()

# Imprimir la ubicación actual
print("La ubicación actual es: " + ubicacion_actual)

