# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 09:49:03 2024

@author: sanmiguel38
"""

# =============================================================================
# PROCESAMIENTO DE METAS MYPE
# =============================================================================
# ojalá que no cambien la estructura del reporte de metas de mype o este script dejará de funcionar

import pandas as pd
import os
import pyodbc

import warnings
warnings.filterwarnings('ignore')

#%% PARÁMETROS INICIALES
ubi         =  'C:\\Users\\sanmiguel38\\Desktop\\metas mype\\2024 julio'
nombre      =  '07 Mype - Julio 2024.xlsx'
fecha_corte =  '2024-07-31'

carga_sql       = True
tabla_principal = 'FUNCIONARIOS.[dbo].[METAS_20240731]'

pestaña_excel   = '75%'

#%%
os.chdir(ubi)

metas = pd.read_excel(nombre, 
                      sheet_name = pestaña_excel)

metas.dropna(subset = ['Unnamed: 1',
                       'Unnamed: 2',
                       'Unnamed: 3'],
             inplace = True,
             how     = 'all')

metas.dropna(subset = ['Unnamed: 7',
                       'Unnamed: 8',
                       'Unnamed: 9'],
             inplace = True,
             how     = 'all')

metas = metas.dropna(axis=1, how='all')

#%% ELIMINACIÓN DE FILAS
print(metas.iloc[0].tolist())
print('el resultado debe ser los nombres de las columnas')
metas.columns = metas.iloc[0].tolist()

fila = metas.iloc[0].tolist()
metas = metas[~(metas == fila).all(axis=1)]

metas['FUNCIONARIO'] = metas['FUNCIONARIO'].str.upper()
metas['FUNCIONARIO'] = metas['FUNCIONARIO'].str.strip()

metas = metas[metas['FUNCIONARIO'] != 'TOTAL']
metas = metas[metas['FUNCIONARIO'] != 'FUNCIONARIO']
metas = metas[metas['FUNCIONARIO'] != 'SEDE']
metas = metas[metas['FUNCIONARIO'] != 'LIMA']
metas = metas[metas['FUNCIONARIO'] != 'PROVINCIA']

#%%
metas['FECHA_CORTE'] = pd.Timestamp(fecha_corte)

#%% rectificación de nombres
nombres = pd.read_excel(io = 'C:\\Users\\sanmiguel38\\Desktop\\metas mype\\NOMBRES FUNCIONARIOS PARA RECTIFICAR.xlsx', 
                        )
nombres['nombre reporte comercial'] = nombres['nombre reporte comercial'].str.strip()

#%% merge
mergeado = metas.merge(nombres,
                       left_on  = 'FUNCIONARIO',
                       right_on = 'nombre reporte comercial',
                       how      = 'left')

faltantes = mergeado[pd.isna(mergeado['nombre para merge'])]
if faltantes.shape[0] > 0:
    print('falta asignar nombre a los siguientes casos')
    print(faltantes)
    faltantes.to_excel('faltantes.xlsx')

#%% Columnas necesarias
df = pd.DataFrame()
df['FUNCIONARIO']            = mergeado['nombre para merge']
df['DESEMBOLSADO ANX06']     = 5
df['DESEMBOLSADO_comercial'] = 0
df['METAS_comercial']        = mergeado['META MONTO']
df['FECHA_CORTE']            = mergeado['FECHA_CORTE']

#%% Reporte para sql
if (faltantes.shape[0] == 0) and (carga_sql == True):
    # Establecer la conexión con SQL Server
    cnxn = pyodbc.connect('DRIVER=SQL Server;SERVER=SM-DATOS;UID=SA;PWD=123;')
    cursor = cnxn.cursor()
    
    # nombre de la tabla en SQL
    tabla = tabla_principal
    
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

    # ###########################################################################
    # fecha_format_sql = fecha_corte[0:4] + fecha_corte[5:7] + fecha_corte[8:10]
    # cursor.execute(f"DELETE FROM FACTORING..REPORTE_SEMANAL WHERE FechaCorte = '{fecha_format_sql}'")
    # cursor.execute(f"INSERT INTO FACTORING..REPORTE_SEMANAL SELECT * FROM {tabla}")
    # ###########################################################################

    # Confirmar los cambios y cerrar la conexión
    cnxn.commit()
    cursor.close()
    
    print(f'Se cargaron los datos a SQL SERVER {tabla}')
    
elif (faltantes.shape[0] > 0) and (carga_sql == True):
    print('no se han cargado los datos, falta corregir')
else:
    print('no se han cargado los datos')