# -*- coding: utf-8 -*-
"""
Created on Thu May 23 12:35:04 2024

@author: sanmiguel38
"""

# =============================================================================
# REPORTE FACTORING
# =============================================================================

import pandas as pd
import os
import pyodbc

import warnings
warnings.filterwarnings('ignore')

#%% PARÁMETROS INICIALES
tabla_nombre = 'FACTORING..[EJEMPLO]'

CARGA_SQL_SERVER = True

fecha_corte = '2024-05-23' # AAAA-MM-DD

os.chdir('C:\\Users\\sanmiguel38\\Desktop\\FACTORING\\MAYO\\23 05 2024')

excel = 'Rpt_FacturasxPrestamoFactotingXClienteXAceptanteTRABAJO.xlsx'

#%%
datos = pd.read_excel(io       = excel, 
                      skiprows = 12,
                      dtype = {'RUC\nCliente'   : str,
                               'Nro Factura'    : str,
                               'Ruc\nAceptante' : str,
                               'N° Prestamo'    : str})

# Eliminación de columnas Unnamed
datos = datos.loc[:, ~datos.columns.str.contains('^Unnamed')]

datos.dropna(subset = ['Estado', 
                       'RUC\nCliente', 
                       'Cliente'],
             inplace = True,
             how     = 'all')

#%%
datos['FechaCorte'] = pd.Timestamp(fecha_corte)

def tipo_prod(df):
    if pd.isna(df['Aceptante']):
        return 'Confirming'
    else:
        return 'Factoring'
datos['Tipo producto'] = datos.apply(tipo_prod, axis = 1)

def proveedor(df):
    if pd.isna(df['Aceptante']):
        return df['Cliente']
    else:
        return df['Aceptante']
datos['Deudor'] = datos.apply(proveedor, axis = 1)

# def cartera_vig_30(df):
#     if df['Dias Vencidos'] <= 30:
#         return df['Monto Financiado']
#     else:
#         return 0
# datos['Cartera Vigente + 30 días vencido'] = datos.apply(cartera_vig_30, axis = 1)
# desactivado porque mejor lo hago en la query

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
    formatos = ['%d/%m/%Y %H:%M:%S',
                '%d/%m/%Y',
                '%Y%m%d', '%Y-%m-%d', 
                '%Y-%m-%d %H:%M:%S', 
                '%Y/%m/%d %H:%M:%S',
                '%Y-%m-%d %H:%M:%S PM',
                '%Y-%m-%d %H:%M:%S AM',
                '%Y/%m/%d %H:%M:%S PM',
                '%Y/%m/%d %H:%M:%S AM']

    for formato in formatos:
        try:
            return pd.to_datetime(date_str, format=formato)
        except ValueError:
            pass
    return pd.NaT

datos['Fecha Desembolso']  = datos['Fecha Desembolso'].apply(parse_dates)
datos['Fecha Vencimiento'] = datos['Fecha Vencimiento'].apply(parse_dates)
datos['Fecha Ultimo Pago'] = datos['Fecha Ultimo Pago'].apply(parse_dates)

#%%
datos['RUC\nCliente']   = datos['RUC\nCliente'].fillna('')
datos['Cliente']        = datos['Cliente'].fillna('')
datos['Ruc\nAceptante'] = datos['Ruc\nAceptante'].fillna('')
datos['Aceptante']      = datos['Aceptante'].fillna('')
datos['Proveedor']      = datos['Proveedor'].fillna('')

#%% CARGA A SQL SERVER
if CARGA_SQL_SERVER == True:
    # Establecer la conexión con SQL Server
    cnxn = pyodbc.connect('DRIVER=SQL Server;SERVER=SM-DATOS;UID=SA;PWD=123;')
    cursor = cnxn.cursor()
    
    # nombre de la tabla en SQL
    tabla = tabla_nombre
    
    df = datos.copy()
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
