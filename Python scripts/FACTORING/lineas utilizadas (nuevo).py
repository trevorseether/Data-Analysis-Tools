# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 18:07:32 2024

@author: sanmiguel38
"""

# =============================================================================
# LÍNEA ASIGNADA VS LÍNEA CONSUMIDA
# =============================================================================

import pandas as pd
import os
import pyodbc

import warnings
warnings.filterwarnings('ignore')

#%%
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\FACTORING\\lineas consumidas\\2025\\marzo\\07 03')
nombre           = 'Rpt_LineaAsignadaXLineaConsumidaXFechalineas10032025.xlsx'
filas_skip       = 8
tipo_cambio      = 3.656
fecha_corte      = '2025-03-07'
CARGA_SQL_SERVER = True
tabla_nombre     = 'FACTORING.DBO.[LINEAS_20250307_v2]' # le dejé el v2 para diferenciar del modelo anterior 

#%%
lineas = pd.read_excel(io       = nombre, 
                       skiprows = filas_skip)

# Eliminación de columnas Unnamed
lineas = lineas.loc[:, ~lineas.columns.str.contains('^Unnamed')]

lineas.dropna(subset = ['Fecha Reporte',
                        'Producto'],
             inplace = True,
             how     = 'all')

#%% SUMA DE LA LÍNEA ASIGNADA Y DE LA LÍNEA OCUPADA

lineas['Deudor'] = lineas['Deudor'].str.strip()
lineas = lineas.dropna(subset = ['Deudor'])

#%%
lineas = lineas.fillna(0)

#%%
formatos = [ '%d/%m/%Y %H:%M:%S',
             '%d/%m/%Y',
             '%Y%m%d',
             '%Y-%m-%d',
             '%Y-%m-%d %H:%M:%S',
             '%Y/%m/%d %H:%M:%S',
             '%Y-%m-%d %H:%M:%S PM',
             '%Y-%m-%d %H:%M:%S AM',
             '%Y/%m/%d %H:%M:%S PM',
             '%Y/%m/%d %H:%M:%S AM' ]     # Lista de formatos a analizar

def parse_date(date_str):
    for formato in formatos:
        try:
            return pd.to_datetime(   arg = date_str, 
                                  format = formato,)
        except ValueError:
            pass
    return pd.NaT

lineas['Fecha Reporte'] = lineas['Fecha Reporte'].apply(parse_date)
lineas['FechaCorte_linea'] = pd.Timestamp(fecha_corte)

#%%
if CARGA_SQL_SERVER == True:
    # Establecer la conexión con SQL Server
    cnxn = pyodbc.connect('DRIVER=SQL Server;SERVER=SM-DATOS;UID=SA;PWD=123;')
    cursor = cnxn.cursor()
    
    # nombre de la tabla en SQL
    tabla = tabla_nombre
    
    df = lineas.copy()
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
    f_corte_formato = fecha_corte[0:4] + fecha_corte[5:7] + fecha_corte[8:10]
    cursor.execute(f"DELETE FROM FACTORING..[LINEAS_v2] WHERE FechaCorte_linea = '{f_corte_formato}'")
    cursor.execute(f"INSERT INTO FACTORING..[LINEAS_v2] SELECT * FROM {tabla_nombre}")
    ###########################################################################

    # Confirmar los cambios y cerrar la conexión
    cnxn.commit()
    cursor.close()

    print(f'Se cargaron los datos a SQL SERVER {tabla}')
    print('Se cargaron los datos a SQL SERVER FACTORING..[LINEAS_v2]')

else:
    print('No se ha cargado a SQL SERVER')


