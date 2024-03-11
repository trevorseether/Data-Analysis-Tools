# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 12:13:59 2024

@author: Joseph Montoya
"""

import pandas as pd
import pyodbc

import warnings
warnings.filterwarnings('ignore')

#%% PARÁMETROS INICIALES
tabla = 'Northwind..[EJEMPLO]'
CARGA_SQL_SERVER = True

#%% DATAFRAME DE EJEMPLO
data = {
    'Producto': ['A', 'B'],
    'Enero'   : [10, 20],
    'Febrero' : [15, 25],
    'Marzo'   : [12, 18],
    'Otro'    : [5, 8],
    'FECHA'   : ['1990-05-15', '1985-10-20']
       }
data['FECHA'] = pd.to_datetime(data['FECHA'])

df = pd.DataFrame(data)

#%%
if CARGA_SQL_SERVER == True:
    # Establecer la conexión con SQL Server
    cnxn = pyodbc.connect('DRIVER=SQL Server;SERVER=SM-DATOS;UID=SA;PWD=123;')
    cursor = cnxn.cursor()
    df = df.copy()
    # Limpiar/eliminar la tabla antes de insertar nuevos datos
    cursor.execute(f"IF OBJECT_ID('{tabla}') IS NOT NULL DROP TABLE {tabla}")    

    # Generar la sentencia CREATE TABLE dinámicamente
    create_table_query = f"CREATE TABLE {tabla} ("
    for column_name, dtype in df.dtypes.items():
        sql_type = ''
        if dtype == 'int64':
            sql_type = 'INT'
        elif dtype == 'float64':
            sql_type = 'FLOAT'
        elif dtype == 'object':
            sql_type = 'NVARCHAR(255)'  # Ajusta el tamaño según tus necesidades
        elif dtype == '<M8[ns]':
            sql_type = 'DATETIME'  # Ajusta el tamaño según tus necesidades

        create_table_query += f"[{column_name}] {sql_type}, "
        
    create_table_query = create_table_query.rstrip(', ') + ")"  # Elimina la última coma y espacio

    # Ejecutar la sentencia CREATE TABLE
    cursor.execute(create_table_query)

    # Preparar la consulta de inserción
    insert_query = f"INSERT INTO {tabla} ({', '.join(df.columns)}) VALUES ({', '.join(['?' for _ in df.columns])})"

    # Iterar sobre las filas del DataFrame e insertar en la base de datos
    for _, row in df.iterrows():
        cursor.execute(insert_query, tuple(row))

    # Confirmar los cambios y cerrar la conexión
    cnxn.commit()
    cursor.close()

    print(f'Se cargaron los datos a SQL SERVER {tabla}')

else:
    print('No se ha cargado a SQL SERVER')

