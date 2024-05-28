# -*- coding: utf-8 -*-
"""
Created on Mon May 27 16:09:05 2024

@author: sanmiguel38
"""

# =============================================================================
# DATOS EXPERIAN PARA FACTORING
# =============================================================================

import pandas as pd
import os
import pyodbc

import warnings
warnings.filterwarnings('ignore')

#%% PARÁMETROS INICIALES
tabla_nombre = 'FACTORING..[EXPERIAN_2024_04]'
CARGA_SQL_SERVER = True

os.chdir('C:\\Users\\sanmiguel38\\Desktop\\FACTORING\\MENSUAL-EXPERIAN\\ABRIL 2024')

nombre = 'EXPERIAN DATA.xlsx'
corte = '2024-04-30'

#%%
experian_data = pd.read_excel(io = nombre, 
                              skiprows = 0,
                              dtype = {'N. DOCUMENTO' : str})

experian_data['N. DOCUMENTO'] = experian_data['N. DOCUMENTO'].str.strip()
experian_data['FechaCorte'] = pd.Timestamp(corte)

experian_data = experian_data[['T. DOCUMENTO',
                               'N. DOCUMENTO', 
                               'NOMBRE CPT',
                               'DEUDA SBS',
                               '# ENTIDADES',
                               'SEM. ACT.',
                               'FechaCorte']]


#%%
if CARGA_SQL_SERVER == True:
    # Establecer la conexión con SQL Server
    cnxn = pyodbc.connect('DRIVER=SQL Server;SERVER=SM-DATOS;UID=SA;PWD=123;')
    cursor = cnxn.cursor()
    
    # nombre de la tabla en SQL
    tabla = tabla_nombre
    
    df = experian_data.copy()
    df = df.fillna(0)
    # AQUÍ SE DEBE APLICAR UN PROCESO DE LIMPIEZA DE LA TABLA PORQUE NO ACEPTA CELDAS CON VALORES NULOS
    # EJEMPLO df = df.fillna(0)
    
    # Limpiar/eliminar la tabla antes de insertar nuevos datos
    cursor.execute(f"IF OBJECT_ID('{tabla}') IS NOT NULL DROP TABLE {tabla}")

    # Generar la sentencia CREATE TABLE dinámicamente
    create_table_query = f"CREATE TABLE {tabla} ("
    for column_name, dtype in df.dtypes.items():
        sql_type = ''
        if dtype == 'int64':
            sql_type = 'INT'
        elif dtype == 'int32':
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


    ###########################################################################
    f_corte_formato = corte[0:4] + corte[5:7] + corte[8:10]
    cursor.execute(f"DELETE FROM FACTORING..EXPERIAN WHERE FechaCorte = '{f_corte_formato}'")
    cursor.execute(f"INSERT INTO FACTORING..EXPERIAN SELECT * FROM {tabla_nombre}")
    ###########################################################################


    # Confirmar los cambios y cerrar la conexión
    cnxn.commit()
    cursor.close()

    print(f'Se cargaron los datos a SQL SERVER {tabla}')

else:
    print('No se ha cargado a SQL SERVER')

