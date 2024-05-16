# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 16:35:26 2024

@author: sanmiguel38
"""
# =============================================================================
#                          DASHBOARD PARA MARKETING
# =============================================================================
import os
import pandas as pd
import pyodbc

import warnings
warnings.filterwarnings('ignore')

#%% LECTURA ANEXO06

ubi              = 'C:\\Users\\sanmiguel38\\Desktop\\TRANSICION  ANEXO 6\\2024\\2024 FEBRERO\\FINAL AHORA SÍ'
anx06            = 'Rpt_DeudoresSBS Anexo06 - Febrero 2024 - campos ampliados v08.xlsx'
fecha_corte      = '2024-02-29'
CARGA_SQL_SERVER = True
tabla            = 'MARKETING..[MARKETING]'

#%%
anexo_06 = pd.read_excel(ubi + '\\' + anx06,
                         skiprows = 2,
                         dtype = {'Nro Prestamo \nFincore' : str,
                                  'Código Socio 7/'        : str,
                                  'Número de Documento 10/': str,
                                  'Numero de Crédito 18/'  : str})

anexo_06.dropna(subset = [# 'Apellidos y Nombres / Razón Social 2/', 
                          'Fecha de Nacimiento 3/',
                          'Número de Documento 10/',
                          'Domicilio 12/',
                          'Numero de Crédito 18/'], inplace = True, how = 'all')

#%%
columnas = ['Apellidos y Nombres / Razón Social 2/',
            'Fecha de Nacimiento 3/',
            'Género 4/',
            'Estado Civil 5/',
            'Código Socio 7/',
            'Tipo de Documento 9/',
            'Número de Documento 10/',
            'Tipo de Persona 11/',
            'Domicilio 12/',
            'Relación Laboral con la Cooperativa 13/',
            'Moneda del crédito 17/',
            'Tipo de Crédito 19/',
            'Fecha de Desembolso 21/',
            'Monto Desembolso\nSoles Fijo',
            'Saldo de colocaciones (créditos directos) 24/',
            'Dias de Mora 33/',
            'Tipo de Producto 43/',
            'TIPO_REPRO',
            'Categoria TXT',
            'Nro Prestamo \nFincore',
            'PLANILLA CONSOLIDADA',
            'Profesion',
            'Ocupacion',
            'Actividad Economica',
            'Departamento', 'Provincia', 'Distrito'            
            ]
#%%
data = anexo_06[columnas]
data = data[data['Dias de Mora 33/'] < 90]
data = data.rename(columns = {'Monto Desembolso\nSoles Fijo' : "Monto Otorgado"})

data['PLANILLA CONSOLIDADA'] = data['PLANILLA CONSOLIDADA'].str.strip()
data['Profesion'] = data['Profesion'].str.strip()
data['Ocupacion'] = data['Ocupacion'].str.strip()
data['Actividad Economica'] = data['Actividad Economica'].str.strip()

#%% CONECCIÓN A SQL SERVER FINCORE
datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')

server    =  datos['DATOS'][0]
username  =  datos['DATOS'][2]
password  =  datos['DATOS'][3]

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'
conn = pyodbc.connect(conn_str)

query = '''
SELECT
	C.INGRESOBRUTO,
	B.DESCRIPCION AS 'GRADO DE INSTRUCCIÓN',
	A.CodigoSocio
FROM SOCIO AS A
LEFT JOIN tablaMaestraDet AS B
ON A.CODINSTRUCCION = B.CODTABLADET

LEFT JOIN PLANILLASOCIO AS C
ON A.CODSOCIO = C.CODSOCIO
'''

df_ingreso_instruccion = pd.read_sql_query(query, conn)
df_ingreso_instruccion = df_ingreso_instruccion.sort_values(by='INGRESOBRUTO', ascending=False)
df_ingreso_instruccion.drop_duplicates(subset='CodigoSocio', inplace = True)


df_ingreso_instruccion.columns
#%% MERGE
data = data.merge(df_ingreso_instruccion,
                  left_on  = 'Código Socio 7/',
                  right_on = 'CodigoSocio',
                  how      = 'left')

del data['CodigoSocio']

#%% FECHA CORTE
data['FECHA CORTE'] = pd.Timestamp(fecha_corte)

#%% FORMATO DE FECHAS
data['EDAD'] = int(fecha_corte[0:4]) - data['Fecha de Nacimiento 3/'].astype(str).str[0:4].astype(int)

data['Fecha de Nacimiento 3/'] = data['Fecha de Nacimiento 3/'].astype(str).str[0:8]

def parse_date(date_str):
    formatos = ['%Y%m%d']
    for formato in formatos:
        try:
            return pd.to_datetime(date_str, format = formato)
        except ValueError:
            pass
    return pd.NaT
data['Fecha de Nacimiento 3/'] = data['Fecha de Nacimiento 3/'].apply(parse_date)
data['Fecha de Desembolso 21/'] = data['Fecha de Desembolso 21/'].apply(parse_date)

#%%
if CARGA_SQL_SERVER == True:
    # Establecer la conexión con SQL Server
    cnxn = pyodbc.connect('DRIVER=SQL Server;SERVER=SM-DATOS;UID=SA;PWD=123;')
    cursor = cnxn.cursor()
    
    df = data.copy()
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

    # Confirmar los cambios y cerrar la conexión
    cnxn.commit()
    cursor.close()

    print(f'Se cargaron los datos a SQL SERVER {tabla}')

else:
    print('No se ha cargado a SQL SERVER')

