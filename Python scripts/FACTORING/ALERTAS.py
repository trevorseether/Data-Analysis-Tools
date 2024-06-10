# -*- coding: utf-8 -*-
"""
Created on Tue May 28 11:08:17 2024

@author: sanmiguel38
"""
# =============================================================================
# ALERTAS PARA REPORTE DE FACTORING
# =============================================================================
import pandas as pd
import os
import pyodbc

#%%
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\FACTORING\\Alertas\\05 06')
archivo = 'C__inetpub_cliente__ExcelPano_Pano_2158968_45303354_215.txt'
fecha_añadido = '2024-06-05'
carga_sql = True
tabla_principal = 'FACTORING.[dbo].[ALERTAS]'

#%%
# Lee el archivo .txt y conviértelo en un DataFrame
df = pd.read_csv(archivo, 
                 delimiter = ',')

df = df.drop(index=0)

df.drop_duplicates(inplace = True)

#%%
columnas = ['ITEM',
            'FECHA PROCESO',
            'T. DOCUMENTO',
            'N. DOCUMENTO',
            'NOMBRE CPT',
            'CIIU',
            'DEUDA VENCIDOS SBS',
            'CRÉDITO VEHICULAR',
            'CRÉDITO HIPOTECARIO',
            'PROTESTO',
            'DEUDA TRIBUTARIA',
            'DEUDA LABORAL',
            'DOCUMENTOS IMPAGOS',
            'VARIACIÓN'
            ]

df = df[columnas]

df['fecha añadido'] = pd.Timestamp(fecha_añadido)
df = df.rename(columns={'T. DOCUMENTO' : 'T# DOCUMENTO',
                        'N. DOCUMENTO' : 'N# DOCUMENTO'})

#%%
if carga_sql == True:
    # Establecer la conexión con SQL Server
    cnxn = pyodbc.connect('DRIVER=SQL Server;SERVER=SM-DATOS;UID=SA;PWD=123;')
    cursor = cnxn.cursor()
    
    # nombre de la tabla en SQL
    tabla = tabla_principal  # Reemplaza con el nombre de tu tabla existente
    
    df = df.copy()
    df = df.fillna(0)  # Rellenar NaNs con 0 si es necesario
    
    fecha_formato = fecha_añadido[0:4] + fecha_añadido[5:7] + fecha_añadido[8:10]
    cursor.execute(f"DELETE FROM {tabla} WHERE [fecha añadido] = '{fecha_formato}' ")
    
    # CREACIÓN DE LA QUERY DE INSERT INTO
    # Crear la lista de nombres de columnas con corchetes
    column_names = [f"[{col}]" for col in df.columns]
    # Crear la lista de placeholders para los valores
    value_placeholders = ', '.join(['?' for _ in df.columns])
    # Crear la consulta de inserción con los nombres de columna y placeholders de valores
    insert_query = f"INSERT INTO {tabla} ({', '.join(column_names)}) VALUES ({value_placeholders})"
    
    # Iterar sobre las filas del DataFrame e insertar en la base de datos
    for _, row in df.iterrows():
        cursor.execute(insert_query, tuple(row))
    
    # Confirmar los cambios y cerrar la conexión
    cnxn.commit()
    cursor.close()
    
    print(f'Se cargaron los datos a SQL SERVER {tabla}')
    
