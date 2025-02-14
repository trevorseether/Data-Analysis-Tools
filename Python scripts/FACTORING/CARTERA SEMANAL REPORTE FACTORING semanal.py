# -*- coding: utf-8 -*-
"""
Created on Thu May 23 12:35:04 2024

@author: sanmiguel38
"""

# =============================================================================
# REPORTE FACTORING
# =============================================================================
# falta automatizar la carga a FACTORING..[REPORTE_SEMANAL]

import pandas as pd
import os
import pyodbc

import warnings
warnings.filterwarnings('ignore')

#%% PARÁMETROS INICIALES
tabla_nombre = 'FACTORING..[FACTORING_SEMANAL_20250213]'

CARGA_SQL_SERVER = True # True or False

fecha_corte = '2025-02-13' # AAAA-MM-DD

os.chdir('C:\\Users\\sanmiguel38\\Desktop\\FACTORING\\CARTERA SEMANAL\\2025\\febrero\\13 02')

excel = 'Rpt_FacturasxPrestamoFactotingXClienteXAceptante14022025.xlsx'

tipo_de_cambio = 3.716

facturas_para_omitir = ['FN01-00004114']

#%%
datos = pd.read_excel(io       = excel, 
                      skiprows = 12,
                      dtype = { 'RUC\nCliente'   : str,
                                'Nro Factura'    : str,
                                'Ruc\nAceptante' : str,
                                'N° Prestamo'    : str  })

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
datos['Deudor'] = datos['Deudor'].str.strip()

def ruc_deudor(df):
    if pd.isna(df['Ruc\nAceptante']):
        return df['RUC\nCliente']
    else:
        return df['Ruc\nAceptante']
datos['Ruc Deudor'] = datos.apply(ruc_deudor, axis = 1)
datos['Ruc Deudor'] = datos['Ruc Deudor'].str.strip()

#%% RECTIFICACIÓN DE NRO RUC
datos.loc[(datos['Deudor'] == 'SOCIEDAD MINERA CORONA S.A.') & \
          (1 == 1), 

          'Ruc Deudor'] = '20217427593'

#%%

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

#%% RENAME DE COLUMNAS
datos = datos.rename(columns={'RUC\nCliente'   : 'RUC Cliente',
                              'Ruc\nAceptante' : 'RUC Aceptante'})

#%% SOLARIZANDO MONTOS EN DOLARES
datos['Tipo de Cambio'] = tipo_de_cambio
datos['MN'] = datos['MN'].str.strip()

def solarizacion_MF(datos):
    if datos['MN'] == 'US$':
        return datos['Monto Financiado'] * tipo_de_cambio
    else:
        return datos['Monto Financiado']
datos['Monto Financiado SOLES'] = datos.apply(solarizacion_MF, axis = 1)

def solarizacion_VFN(datos):
    if datos['MN'] == 'US$':
        return datos['Valor Facial Neto'] * tipo_de_cambio
    else:
        return datos['Valor Facial Neto']
datos['Valor Facial Neto SOLES'] = datos.apply(solarizacion_VFN, axis = 1)

#%% ELIMINACIÓN DE FACTURAS

datos = datos[~datos['Nro Factura'].isin(facturas_para_omitir)]

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

    ###########################################################################
    fecha_format_sql = fecha_corte[0:4] + fecha_corte[5:7] + fecha_corte[8:10]
    cursor.execute(f"DELETE FROM FACTORING..REPORTE_SEMANAL WHERE FechaCorte = '{fecha_format_sql}'")
    cursor.execute(f"INSERT INTO FACTORING..REPORTE_SEMANAL SELECT * FROM {tabla}")
    ###########################################################################

    # Confirmar los cambios y cerrar la conexión
    cnxn.commit()
    cursor.close()

    print(f'Se cargaron los datos a SQL SERVER {tabla}')
    print('Se cargaron los datos a FACTORING..REPORTE_SEMANAL')
else:
    print('No se ha cargado a SQL SERVER')

