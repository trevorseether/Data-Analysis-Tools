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
tabla_nombre = 'FACTORING..[EXPERIAN_2024_08_23]'
CARGA_SQL_SERVER = True #True

os.chdir('C:\\Users\\sanmiguel38\\Desktop\\FACTORING\\MENSUAL-EXPERIAN\\agosto 2024\\23 08')

nombre = 'experian deudas.xltx'
corte  = '2024-08-23'

#%% 
"LECTOR DE .TXT"
# experian_data = pd.read_csv(nombre,
#                             skiprows = 0,
#                             dtype    = {'N. DOCUMENTO' : str})

"LECTOR DE EXCEL"
experian_data = pd.read_excel(io       = nombre, 
                              skiprows = 0,
                              dtype    = {'N. DOCUMENTO' : str})

#%%%
experian_data['N. DOCUMENTO'] = experian_data['N. DOCUMENTO'].str.strip()
experian_data['FechaCorte'] = pd.Timestamp(corte)

experian_data = experian_data[['T. DOCUMENTO',
                               'N. DOCUMENTO', 
                               'NOMBRE CPT',
                               'DEUDA SBS',
                               '# ENTIDADES',
                               'SEM. ACT.',
                               'FechaCorte']]

experian_data['N. DOCUMENTO'] = experian_data['N. DOCUMENTO'].str.strip()

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
    print('Se cargaron los datos a SQL SERVER FACTORING..EXPERIAN')

else:
    print('No se ha cargado a SQL SERVER')

#%%
#%% EMPRESAS NO REPORTADAS POR EXPERIAN
conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')
###############################################################################
query = '''
	SELECT
		DISTINCT
		[Ruc Deudor],
		Deudor
	FROM FACTORING..[REPORTE_SEMANAL]
	WHERE FechaCorte = (SELECT MAX(FechaCorte) FROM FACTORING..[REPORTE_SEMANAL])
'''
semanal = pd.read_sql_query(query, conn, dtype = {'Ruc Deudor' : str})
semanal['Ruc Deudor'] = semanal['Ruc Deudor'].str.strip()
###############################################################################
query = '''
	SELECT
		DISTINCT
		[Ruc Deudor],
		Deudor 
	FROM FACTORING..[ADELANTOS]
	WHERE FechaCorte = (SELECT MAX(FechaCorte) FROM FACTORING..ADELANTOS)
'''
adelantos = pd.read_sql_query(query, conn, dtype = {'Ruc Deudor' : str})
adelantos['Ruc Deudor'] = adelantos['Ruc Deudor'].str.strip()
###############################################################################
query = '''
	SELECT
		DISTINCT
		[N. DOCUMENTO] AS 'Ruc Deudor',
		[NOMBRE CPT],
        FechaCorte
	FROM FACTORING..EXPERIAN
	WHERE FechaCorte = (select max(FechaCorte) from FACTORING..EXPERIAN)
'''
experian = pd.read_sql_query(query, conn, dtype = {'Ruc Deudor' : str})
experian['Ruc Deudor'] = experian['Ruc Deudor'].str.strip()
###############################################################################

#%% unión de datos generados por el fincore
base_fincore = pd.concat([semanal, 
                          adelantos], axis = 0)
base_fincore.drop_duplicates(subset  = ['Ruc Deudor', 'Deudor'],
                             inplace = True)
base_fincore.drop_duplicates(subset  = 'Ruc Deudor',
                             inplace = True)

#%% merge para ver cuales no están en la base que envía experian
mergeado = base_fincore.merge(experian,
                              on  = 'Ruc Deudor',
                              how = 'left')

no_reportados = mergeado[pd.isna(mergeado['NOMBRE CPT'])]

no_reportados = no_reportados[['Ruc Deudor', 'Deudor']]

#%%
# no_reportados.to_excel('no reportados por Experian.xlsx')

if no_reportados.shape[0] > 0:
    print(no_reportados)
    no_reportados.to_excel('no reportados por Experian.xlsx', index = False)
else:
    print('todo bien, todos están siendo reportados por Experian')
    
