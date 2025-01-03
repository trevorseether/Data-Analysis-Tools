# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 12:12:18 2024

@author: sanmiguel38
"""

# =============================================================================
# INFORMACIÓN DE DEPARTAMENTO Y SECTOR ECONÓMICO
# =============================================================================

import pandas as pd
import os
import pyodbc

#%%
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\FACTORING\\DEPARTAMENTO Y ACTIVIDAD ECONÓMICA\\2024 12\\24 12')
archivo     = 'cartera vigente.xlsx'
fecha_corte = '2024-12-24'
carga_sql   = True

#%%
datos_dep_sect = pd.read_excel(archivo,
                               dtype    = str,
                               skiprows = 0)

datos_dep_sect['Ruc Deudor'] = datos_dep_sect['Ruc Deudor'].str.strip()
datos_dep_sect['FechaCorte'] = pd.Timestamp(fecha_corte)

#%% CARGA A SQL SERVER
if carga_sql== True:
    # Establecer la conexión con SQL Server
    cnxn = pyodbc.connect('DRIVER=SQL Server;SERVER=SM-DATOS;UID=SA;PWD=123;')
    cursor = cnxn.cursor()
    
    # nombre de la tabla en SQL
    tabla = 'FACTORING..[DEP_SECTOR]'
    
    df = datos_dep_sect.copy()
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
    # fecha_format_sql = fecha_corte[0:4] + fecha_corte[5:7] + fecha_corte[8:10]
    # cursor.execute(f"DELETE FROM FACTORING..REPORTE_SEMANAL WHERE FechaCorte = '{fecha_format_sql}'")
    # cursor.execute(f"INSERT INTO FACTORING..REPORTE_SEMANAL SELECT * FROM {tabla}")
    ###########################################################################

    # Confirmar los cambios y cerrar la conexión
    cnxn.commit()
    cursor.close()

    print(f'Se cargaron los datos a SQL SERVER {tabla}')
    # print('Se cargaron los datos a FACTORING..REPORTE_SEMANAL')
else:
    print('No se ha cargado a SQL SERVER')





