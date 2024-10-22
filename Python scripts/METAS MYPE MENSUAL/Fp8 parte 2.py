# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 12:39:54 2024

@author: sanmiguel38
"""

# =============================================================================
#  PARTE 2 DEL FP8, unión de los datos obtenidos en ambas fechas
# =============================================================================

import pandas as pd
import os

import pyodbc

import warnings
warnings.filterwarnings('ignore')


#%%
# asumiendo que elaboramos el fp8 justo después de procesar el de la fecha 20
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\fp8\\2024\\setiembre')

primero = 'fp8_2024-09-05.xlsx'
segundo = 'fp8_2024-09-20.xlsx'

cargar_SQL = True
tabla_nombre = 'FUNCIONARIOS.[dbo].[Fp8_20240930]'

#%%
df_primero = pd.read_excel(io = primero)
df_segundo = pd.read_excel(io = segundo)

#%% MERGE
unido = df_primero.merge(df_segundo,
                         left_on  = 'Funcionario p1',
                         right_on = 'Funcionario p2',
                         how      = 'outer')

def funcionario_ajuste(df):
    if pd.isna(df['Funcionario p1']):
        return df['Funcionario p2']
    else:
        return df['Funcionario p1']
    
unido['Funcionario'] = unido.apply(funcionario_ajuste, axis = 1)
del unido['Funcionario p1']
del unido['Funcionario p2']

#%%
unido = unido.fillna(0)

unido['numerador']   = unido['cancelado hasta 8 días p1'] + unido['cancelado hasta 8 días p2']
unido['denominador'] = unido['numerador'] + unido['pendiente p1'] + unido['pendiente p2']

unido['Fp8'] = unido['numerador'] / unido['denominador']

#%% NOMBRES PARA UNIÓN CON REPORTES GERENCIALES
nombres_funcionarios = pd.read_excel(io = 'C:\\Users\\sanmiguel38\\Desktop\\fp8\\nombre de los funcionarios.xlsx', 
                                     dtype = str)
nombres_funcionarios.rename(columns={'reporte de cobranza': 'Funcionario'}, inplace=True)

unido_cols = unido[['Funcionario', 'numerador', 'denominador', 'Fp8']]

unido_cols = unido_cols.merge(nombres_funcionarios,
                              on  = 'Funcionario',
                              how = 'left')

no_match = unido_cols[pd.isna(unido_cols['nombres para merge'])]
if no_match.shape[0] > 0:
    print('añadir a la lista:')
    print(no_match['Funcionario'])

unido_cols.columns


#%% CARGA A SQL SERVER
if cargar_SQL == True:
    # Establecer la conexión con SQL Server
    cnxn = pyodbc.connect('DRIVER=SQL Server;SERVER=SM-DATOS;UID=SA;PWD=123;')
    cursor = cnxn.cursor()
    
    # nombre de la tabla en SQL
    tabla = tabla_nombre
    
    df = unido_cols[['nombres para merge', 'numerador', 'denominador', 'Fp8']].copy()
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
else:
    print('No se ha cargado a SQL SERVER')

#%%
unido.to_excel('fp8 de las 2 fechas.xlsx',
               index = False)

