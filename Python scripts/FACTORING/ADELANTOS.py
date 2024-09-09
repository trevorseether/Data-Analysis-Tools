# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 12:04:29 2024

@author: sanmiguel38
"""

# =============================================================================
# FACTORING: REPORTE DE ADELANTOS
# =============================================================================
import pandas as pd
import os
import pyodbc

import warnings
warnings.filterwarnings('ignore')

#%%
tabla_nombre = 'FACTORING..[ADELANTOS_20240906]'

CARGA_SQL_SERVER = True

fecha_corte      = '2024-09-06'

tipo_de_cambio   = 3.78

os.chdir('C:\\Users\\sanmiguel38\\Desktop\\FACTORING\\ADELANTOS\\2024\\setiembvre\\09 09')

nombre     = 'Rpt_SolicitudesxPrestamoFactoringDetalleExtendidoadelantos06092024.xlsx'

filas_skip = 14

#%%
adelantos = pd.read_excel(io       = nombre, 
                          skiprows = filas_skip,
                          dtype = {'Solicitud Credito' : str,
                                   'Ruc Cliente'   : str,
                                   'Nro Factura'   : str,
                                   'Ruc Aceptante' : str,
                                   'N° Prestamo'   : str})

# Eliminación de columnas Unnamed
adelantos = adelantos.loc[:, ~adelantos.columns.str.contains('^Unnamed')]

adelantos.dropna(subset = ['Ruc Cliente', 
                           'Cliente'],
                 inplace = True,
                 how     = 'all')

adelantos.drop_duplicates(subset  = 'Solicitud Credito Macro',
                          inplace = True)

sin_adelanto = adelantos[(adelantos['Monto\nAdelanto'] == 0)      |
                         (pd.isna(adelantos['Monto\nAdelanto']))  |
                         (pd.isna(adelantos['Dias Adelantados'])) |
                         (pd.isna(adelantos['Fecha \nAdelanto']))
                         ]

if sin_adelanto.shape[0] > 0:
    print('Exiten casos sin adelanto:')
    print(sin_adelanto[['Solicitud Credito Macro','Aceptante']])
    sin_adelanto.to_excel('Casos sin adelanto.xlsx',
                          index = False)

adelantos = adelantos[~((adelantos['Monto\nAdelanto'] == 0)      |
                        (pd.isna(adelantos['Monto\nAdelanto']))  |
                        (pd.isna(adelantos['Dias Adelantados'])) |
                        (pd.isna(adelantos['Fecha \nAdelanto'])))
                         ]

#%%
adelantos['FechaCorte'] = pd.Timestamp(fecha_corte)

def tipo_prod(df):
    if pd.isna(df['Aceptante']):
        return 'Confirming'
    else:
        return 'Factoring'
adelantos['Tipo producto'] = adelantos.apply(tipo_prod, axis = 1)

def proveedor(df):
    if pd.isna(df['Aceptante']):
        return df['Cliente']
    else:
        return df['Aceptante']
adelantos['Deudor'] = adelantos.apply(proveedor, axis = 1)
adelantos['Deudor'] = adelantos['Deudor'].str.strip()

def ruc_deudor(df):
    if pd.isna(df['Ruc Aceptante']):
        return df['Ruc Cliente']
    else:
        return df['Ruc Aceptante']
adelantos['Ruc Deudor'] = adelantos.apply(ruc_deudor, axis = 1)
adelantos['Ruc Deudor'] = adelantos['Ruc Deudor'].str.strip()

#%% RECTIFICACIÓN DE NRO RUC
adelantos.loc[(adelantos['Deudor'] == 'SOCIEDAD MINERA CORONA S.A.') & \
          (1 == 1), 

          'Ruc Deudor'] = '20217427593'

def parse_dates(date_str):
    '''
    Parameters
    ----------
    date_str : Es el formato que va a analizar dentro de la columna del DataFrame.

    Returns
    -------
    Si el date_str tiene una estructura compatible con los formatos preestablecidos
    para su iteración, la convertirá en un DateTime

    '''
    #formatos en los cuales se tratará de convertir a DateTime
    formatos = [ '%d/%m/%Y %H:%M:%S',
                 '%d/%m/%Y',
                 '%Y%m%d', 
                 '%Y-%m-%d', 
                 '%Y-%m-%d %H:%M:%S', 
                 '%Y/%m/%d %H:%M:%S',
                 '%Y-%m-%d %H:%M:%S PM',
                 '%Y-%m-%d %H:%M:%S AM',
                 '%Y/%m/%d %H:%M:%S PM',
                 '%Y/%m/%d %H:%M:%S AM' ]

    for formato in formatos:
        try:
            return pd.to_datetime(date_str, format=formato)
        except ValueError:
            pass
    return pd.NaT

adelantos['Fecha Creacion']       = adelantos['Fecha Creacion'].apply(parse_dates)
adelantos['Fecha Envio Analista'] = adelantos['Fecha Envio Analista'].apply(parse_dates)
adelantos['Fecha \nAdelanto']     = adelantos['Fecha \nAdelanto'].apply(parse_dates)

#%%
adelantos['Ruc Cliente']   = adelantos['Ruc Cliente'].fillna('')
adelantos['Cliente']       = adelantos['Cliente'].fillna('')
adelantos['Ruc Aceptante'] = adelantos['Ruc Aceptante'].fillna('')
adelantos['Aceptante']     = adelantos['Aceptante'].fillna('')
adelantos['Proveedor']     = adelantos['Proveedor'].fillna('')

#%% RENAME DE COLUMNAS
adelantos = adelantos.rename(columns={'Monto\nAdelanto'   : 'Monto Adelanto'})

#%% SOLARIZANDO MONTOS EN DOLARES
adelantos['Tipo de Cambio'] = tipo_de_cambio
adelantos['MN'] = adelantos['MN'].str.strip()

def solarizacion_adelantos(adelantos):
    if adelantos['MN'] == 'US$':
        return adelantos['Monto Adelanto'] * tipo_de_cambio
    else:
        return adelantos['Monto Adelanto']
adelantos['Monto Adelanto SOLES'] = adelantos.apply(solarizacion_adelantos, axis = 1)

#%% SEGMENTANDO POR NRO DE DÍAS DE VENCIMIENTO
# col_monto = 'Monto Adelanto SOLES' #'Monto Financiado SOLES'

# def fi_0_30(adelantos):
#     if adelantos['Dias Vencidos'] <= 30:
#         return adelantos[col_monto]
#     else:
#         return 0
# adelantos[f'{col_monto} <= 30'] = adelantos.apply(fi_0_30, axis = 1)

# def fi_30_90(adelantos):
#     if (adelantos['Dias Vencidos'] > 30) and (adelantos['Dias Vencidos'] <= 90):
#         return adelantos[col_monto]
#     else:
#         return 0
# adelantos[f'{col_monto} entre 30 y 90'] = adelantos.apply(fi_30_90, axis = 1)

# def fi_90(adelantos):
#     if adelantos['Dias Vencidos'] > 90:
#         return adelantos[col_monto]
#     else:
#         return 0
# adelantos[f'{col_monto} >90'] = adelantos.apply(fi_90, axis = 1)

#%%
adelantos['Porcentaje Adelanto'] = adelantos['% Adelanto']/100

#%%
columnas_necesarias = ['FechaCorte', 
                       
                       'Solicitud Credito Macro',
                       'Solicitud Credito', 
                       'Ruc Cliente', 
                       'Cliente', 
                       'Ruc Aceptante',
                       'Aceptante', 
                       'Proveedor', 
                       'Nro Documentos', 
                       '% Anticipo', 
                       'MN',
                       'Monto Documento',
                       'Funcionario',
                       'Estado\nSolicitud', 
                       'Fecha \nAdelanto', 
                       'Monto Adelanto', 
                       '% Adelanto',
                       'Saldo por Abonar', 
                       'Dias Adelantados', 
                       'Tipo producto',
                       'Deudor', 
                       'Ruc Deudor', 
                       'Tipo de Cambio', 
                       'Monto Adelanto SOLES',
                       'Porcentaje Adelanto'
                       ]

adelantos = adelantos[columnas_necesarias]

#%%
if CARGA_SQL_SERVER == True:
    # Establecer la conexión con SQL Server
    cnxn = pyodbc.connect('DRIVER=SQL Server;SERVER=SM-DATOS;UID=SA;PWD=123;')
    cursor = cnxn.cursor()
    
    # nombre de la tabla en SQL
    tabla = tabla_nombre
    
    df = adelantos.copy()
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
    fecha_format_sql = fecha_corte[0:4] + fecha_corte[5:7] + fecha_corte[8:10]
    cursor.execute(f"DELETE FROM FACTORING..[ADELANTOS] WHERE FechaCorte = '{fecha_format_sql}'")
    cursor.execute(f"INSERT INTO FACTORING..[ADELANTOS] SELECT * FROM {tabla}")
    ###########################################################################

    # Confirmar los cambios y cerrar la conexión
    cnxn.commit()
    cursor.close()

    print(f'Se cargaron los datos a SQL SERVER {tabla}')
    print('Se cargaron los datos a SQL SERVER FACTORING..[ADELANTOS]')

else:
    print('No se ha cargado a SQL SERVER')


