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
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\FACTORING\\Alertas\\2025\\febre\\14 02')
archivo         = 'C__inetpub_cliente__ExcelPano_Pano_2158968_45303354_217.txt'
fecha_añadido   = '2025-02-14' #yyyy-mm-dd
carga_sql       = True
tabla_principal = 'FACTORING.[dbo].[ALERTAS]'

'''/////////////////////////////////////////////////////////////////////////'''
delete_al_insertar = True  
        # True para hacer un delete de modo que no haya otra inserción con la misma fecha
        # False para tener varias inserciones con la misma fecha
'''/////////////////////////////////////////////////////////////////////////'''

#%%
# Lee el archivo .txt y conviértelo en un DataFrame
df = pd.read_csv(archivo,
                 delimiter = ',')

df = df.drop(index = 0)

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
    
    #df = df.copy()
    df = df.fillna(0)  # Rellenar NaNs con 0 si es necesario
    
    ###########################################################################
    fecha_formato = fecha_añadido[0:4] + fecha_añadido[5:7] + fecha_añadido[8:10]
    if delete_al_insertar == True:
        cursor.execute(f"DELETE FROM {tabla} WHERE [fecha añadido] = '{fecha_formato}' ")
    ###########################################################################
    
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
    print(f'Correspondiente a la fecha {fecha_añadido}')
    
#%%
# =============================================================================
#       VALIDACIÓN DE QUE LAS ALERTAS SEAN DE EMPRESAS CON DEUDA VIGENTE
# =============================================================================
# EMPRESAS NO REPORTADAS POR EXPERIAN
conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')
###############################################################################
query = '''
	SELECT
		DISTINCT
		[Ruc Deudor],
		Deudor 
	FROM FACTORING..[REPORTE_SEMANAL]
	WHERE FechaCorte = (SELECT MAX(DISTINCT FechaCorte)FROM FACTORING..[REPORTE_SEMANAL])
'''
semanal = pd.read_sql_query(query, 
                            conn, 
                            dtype = {'Ruc Deudor' : str})
semanal['Ruc Deudor'] = semanal['Ruc Deudor'].str.strip()

lista_vigentes = list(semanal['Ruc Deudor'])

#%% total alertas
# query = '''
# 	SELECT 
# 		[N# DOCUMENTO] AS 'Ruc Deudor',
#         [NOMBRE CPT]
# 	FROM FACTORING.[dbo].[ALERTAS]
# '''
# alertas_todo = pd.read_sql_query(query, 
#                                  conn, 
#                                  dtype = {'Ruc Deudor' : str})
# alertas_todo['Ruc Deudor'] = alertas_todo['Ruc Deudor'].str.strip()

# lista_vigentes = list(semanal['Ruc Deudor'])
# borrar_de_experian = alertas_todo[~alertas_todo['Ruc Deudor'].isin(lista_vigentes)]
# borrar_de_experian.to_excel('borrar de experian.xlsx',
#                             index = False)

#%%
alertas_actuales   = df[['N# DOCUMENTO', 'NOMBRE CPT']].copy()
borrar_de_experian = alertas_actuales[~alertas_actuales['N# DOCUMENTO'].isin(lista_vigentes)]

if borrar_de_experian.shape[0] > 0:
    borrar_de_experian.to_excel('borrar de experian (alerta última).xlsx',
                            index = False)
else:
    pass

