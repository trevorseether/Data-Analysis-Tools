# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 10:27:24 2024

@author: sanmiguel38
"""

# =============================================================================
# TABLA DE TASAS Y COMISIONES
# =============================================================================
import pandas as pd
# import os
import pyodbc

import warnings
warnings.filterwarnings('ignore')

#%%
ubicacion        = 'C:\\Users\\sanmiguel38\\Desktop\\FACTORING\\TASAS Y COMISIONES\\2024\\noviembre'

nombre_excel     = 'Rpt_SolicitudesxPrestamoFactoringDetallenoviembre30112024.xlsx'

tipo_de_cambio   = 3.724

fecha_desembolso = '2024-11-30'

CARGA_SQL_SERVER = True

tabla_nombre     = 'FACTORING..[TEM_COMISION]'

#%%
tasas_comisiones = pd.read_excel(io       = ubicacion  + '\\' + nombre_excel, 
                                 skiprows = 14,
                                 dtype    = { 'Ruc Cliente'       : str,
                                              'Ruc Aceptante'     : str,
                                              'Fecha\nDesembolso' : str })

# Eliminación de columnas Unnamed
tasas_comisiones = tasas_comisiones.loc[:, ~tasas_comisiones.columns.str.contains('^Unnamed')]

tasas_comisiones.dropna(subset = ['Solicitud Credito', 
                                  'Ruc Cliente', 
                                  'Cliente'],
                        inplace = True,
                        how     = 'all')

tasas_comisiones.dropna(subset = ['Fecha\nDesembolso'],
                        inplace = True,
                        how     = 'all')

#%% ELIMINACIÓN DE DUPLICADOS
tasas_comisiones = tasas_comisiones.sort_values(by = 'Solicitud Credito')

tasas_comisiones = tasas_comisiones.drop_duplicates(subset = 'Solicitud Credito Macro', 
                                                    keep   = 'last')
#%% FORMATO DE FECHA
def get_first_day_of_month(last_day_of_month):
    
    last_day_of_month = pd.Timestamp(last_day_of_month)
    # Reemplazar el día por 1 para obtener el primer día del mes
    first_day_of_month = last_day_of_month.replace(day=1)
    return first_day_of_month

fecha_inicio = get_first_day_of_month(fecha_desembolso)
fecha_final  = pd.Timestamp(fecha_desembolso)
###############################################################################
def parse_date(date_str):
    # Lista de formatos a analizar
    formatos = [ '%Y-%m-%d %H:%M:%S']

    for formato in formatos:
        try:
            return pd.to_datetime(   arg = date_str, 
                                  format = formato,)
        except ValueError:
            pass
    return pd.NaT

tasas_comisiones['Fecha\nDesembolso'] = tasas_comisiones['Fecha\nDesembolso'].apply(parse_date)
tasas_comisiones = tasas_comisiones.rename(columns = {'Fecha\nDesembolso' : 'Fecha Desembolso'})

#%% FILTRADO DESEMBOLSADOS DEL MES
tasas_comisiones = tasas_comisiones[tasas_comisiones['Estado\nSolicitud'] == 'DESEMBOLSADO']

tasas_comisiones = tasas_comisiones[(tasas_comisiones['Fecha Desembolso'] >= fecha_inicio) &
                                    (tasas_comisiones['Fecha Desembolso'] <= fecha_final)]

#%% SOLARIZANDO MONTOS EN DOLARES
tasas_comisiones['Tipo de Cambio'] = tipo_de_cambio
tasas_comisiones['MN'] = tasas_comisiones['MN'].str.strip()

def solarizacion_MD(tasas_comisiones):
    if tasas_comisiones['MN'] == 'US$':
        return tasas_comisiones['Monto Documento'] * tipo_de_cambio
    else:
        return tasas_comisiones['Monto Documento']
tasas_comisiones['Monto Documento SOLES'] = tasas_comisiones.apply(solarizacion_MD, axis = 1)

def solarizacion_NA(tasas_comisiones):
    if tasas_comisiones['MN'] == 'US$':
        return tasas_comisiones['Neto Ajustado'] * tipo_de_cambio
    else:
        return tasas_comisiones['Neto Ajustado']
tasas_comisiones['Neto Ajustado SOLES'] = tasas_comisiones.apply(solarizacion_NA, axis = 1)

def solarizacion_comisiones(tasas_comisiones):
    if tasas_comisiones['MN'] == 'US$':
        return tasas_comisiones['Comision'] * tipo_de_cambio
    else:
        return tasas_comisiones['Comision']
tasas_comisiones['Comision'] = tasas_comisiones.apply(solarizacion_comisiones, axis = 1)
 
#%% COLUMNAS AUXILIARES
def tipo_prod(df):
    if (pd.isna(df['Aceptante'])) or (df['Aceptante'] == '-'):
        return 'Confirming'
    else:
        return 'Factoring'
tasas_comisiones['Tipo producto'] = tasas_comisiones.apply(tipo_prod, axis = 1)

def deudor(df):
    if (pd.isna(df['Aceptante'])) or (df['Aceptante'] == '-'):
        return df['Cliente']
    else:
        return df['Aceptante']
tasas_comisiones['Deudor'] = tasas_comisiones.apply(deudor, axis = 1)
tasas_comisiones['Deudor'] = tasas_comisiones['Deudor'].str.strip()

def ruc_deudor(df):
    if (pd.isna(df['Aceptante'])) or (df['Aceptante'] == '-'):
        return df['Ruc Cliente']
    else:
        return df['Ruc Aceptante']
tasas_comisiones['Ruc Deudor'] = tasas_comisiones.apply(ruc_deudor, axis = 1)
tasas_comisiones['Ruc Deudor'] = tasas_comisiones['Ruc Deudor'].str.strip()

#%% MES DESEMBOLSO
tasas_comisiones['MES_DESEMBOLSO'] = pd.Timestamp(fecha_desembolso)

#%% RECTIFICACIÓN DE NRO RUC
tasas_comisiones.loc[(tasas_comisiones['Deudor'] == 'SOCIEDAD MINERA CORONA S.A.') & \
          (1 == 1), 

          'Ruc Deudor'] = '20217427593'

#%%
columnas_necesarias = ['MES_DESEMBOLSO',
                       'Fecha Desembolso',
                       'Solicitud Credito Macro',
                       'Ruc Cliente',
                       'Cliente',
                       'Ruc Aceptante',
                       'Aceptante',
                       'Ruc Deudor',
                       'Deudor',
                       'Tipo de Cambio',
                       'MN',
                       'Monto Documento SOLES',
                       'Neto Ajustado SOLES',
                       'Comision',
                       'Gastos',
                       'Funcionario',
                       'TEM',
                       ]

tasas_comisiones = tasas_comisiones[columnas_necesarias]

#%% CREACIÓN DE TABLA
# if CARGA_SQL_SERVER == True:
#     # Establecer la conexión con SQL Server
#     cnxn = pyodbc.connect('DRIVER=SQL Server;SERVER=SM-DATOS;UID=SA;PWD=123;')
#     cursor = cnxn.cursor()
    
#     # nombre de la tabla en SQL
#     tabla = tabla_nombre
    
#     df = tasas_comisiones.copy()
#     df = df.fillna(0)
#     # AQUÍ SE DEBE APLICAR UN PROCESO DE LIMPIEZA DE LA TABLA PORQUE NO ACEPTA CELDAS CON VALORES NULOS
#     # EJEMPLO df = df.fillna(0)
#     # Limpiar/eliminar la tabla antes de insertar nuevos datos
#     cursor.execute(f"IF OBJECT_ID('{tabla}') IS NOT NULL DROP TABLE {tabla}")

#     # Generar la sentencia CREATE TABLE dinámicamente
#     create_table_query = f"CREATE TABLE {tabla} ("
#     for column_name, dtype in df.dtypes.items():
#         sql_type = ''
#         if dtype == 'int64':
#             sql_type = 'INT'
#         elif dtype == 'int32':
#             sql_type = 'INT'
#         elif dtype == 'float64':
#             sql_type = 'FLOAT'
#         elif dtype == 'object':
#             sql_type = 'NVARCHAR(255)'  # Ajusta el tamaño según tus necesidades
#         elif dtype == '<M8[ns]':
#             sql_type = 'DATETIME'  # Ajusta el tamaño según tus necesidades

#         create_table_query += f"[{column_name}] {sql_type}, "
        
#     create_table_query = create_table_query.rstrip(', ') + ")"  # Elimina la última coma y espacio

#     # Ejecutar la sentencia CREATE TABLE
#     cursor.execute(create_table_query)
    
#     # CREACIÓN DE LA QUERY DE INSERT INTO
#     # Crear la lista de nombres de columnas con corchetes
#     column_names = [f"[{col}]" for col in df.columns]
#     # Crear la lista de placeholders para los valores
#     value_placeholders = ', '.join(['?' for _ in df.columns])
#     # Crear la consulta de inserción con los nombres de columna y placeholders de valores
#     insert_query = f"INSERT INTO {tabla} ({', '.join(column_names)}) VALUES ({value_placeholders})"

#     # Iterar sobre las filas del DataFrame e insertar en la base de datos
#     for _, row in df.iterrows():
#         cursor.execute(insert_query, tuple(row))

#     ###########################################################################
#     fecha_format_sql = fecha_desembolso[0:4] + fecha_desembolso[5:7] + fecha_desembolso[8:10]
#     ###########################################################################
    
#     # Confirmar los cambios y cerrar la conexión
#     cnxn.commit()
#     cursor.close()

#     print(f'Se cargaron los datos a SQL SERVER {tabla}')

# else:
#     print('No se ha cargado a SQL SERVER')

#%% INSERTAR DATOS A LA TABLA
if CARGA_SQL_SERVER == True:
    # Establecer la conexión con SQL Server
    cnxn = pyodbc.connect('DRIVER=SQL Server;SERVER=SM-DATOS;UID=SA;PWD=123;')
    cursor = cnxn.cursor()
    
    # nombre de la tabla en SQL
    tabla = tabla_nombre  # Reemplaza con el nombre de tu tabla existente
    
    df = tasas_comisiones.copy()
    df = df.fillna(0)  # Rellenar NaNs con 0 si es necesario
    
    fecha_formato = fecha_desembolso[0:4] + fecha_desembolso[5:7] + fecha_desembolso[8:10]
    cursor.execute(f"DELETE FROM {tabla} WHERE [MES_Desembolso] = '{fecha_formato}' ")
    
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
    print(f'Correspondiente al {fecha_desembolso}')

