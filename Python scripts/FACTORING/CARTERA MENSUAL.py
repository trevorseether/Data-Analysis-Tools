# -*- coding: utf-8 -*-
"""
Created on Wed May 29 14:42:09 2024

@author: sanmiguel38
"""

# =============================================================================
# CARTERA FACTORING MENSUAL
# =============================================================================

import pandas as pd
import os
import pyodbc

import warnings
warnings.filterwarnings('ignore')

#%% PARÁMETROS INICIALES
tabla_nombre     = 'FACTORING..[CARTERA_2024_10]'

CARGA_SQL_SERVER = True

fecha_corte      = '2024-10-31'

os.chdir('C:\\Users\\sanmiguel38\\Desktop\\FACTORING\\MENSUAL-EXPERIAN\\octubre\\05 11')

nombre           = 'Rpt_FacturasxPrestamoFactotingXClienteXAceptante31102024CIERREMES.xlsx'

tipo_de_cambio   = 3.768

facturas_para_omitir = ['FN01-00004114']

#%%
datos = pd.read_excel(io       = nombre, 
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

def deudor(df):
    if pd.isna(df['Aceptante']):
        return df['Cliente']
    else:
        return df['Aceptante']
datos['Deudor'] = datos.apply(deudor, axis = 1)
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

#%% SEGMENTANDO MONTO FINANCIADO POR NRO DE DÍAS DE VENCIMIENTO
def fi_0_30(datos):
    if datos['Dias Vencidos'] <= 30:
        return datos['Monto Financiado SOLES']
    else:
        return 0
datos['Monto Financiado <= 30'] = datos.apply(fi_0_30, axis = 1)

def fi_30_90(datos):
    if (datos['Dias Vencidos'] > 30) and (datos['Dias Vencidos'] <= 90):
        return datos['Monto Financiado SOLES']
    else:
        return 0
datos['Monto Financiado entre 30 y 90'] = datos.apply(fi_30_90, axis = 1)

def fi_90(datos):
    if datos['Dias Vencidos'] > 90:
        return datos['Monto Financiado SOLES']
    else:
        return 0
datos['Monto Financiado >90'] = datos.apply(fi_90, axis = 1)

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
    cursor.execute(f"DELETE FROM FACTORING..[CARTERA] WHERE FECHACORTE = '{fecha_format_sql}'")
    cursor.execute(f"INSERT INTO FACTORING..[CARTERA] SELECT * FROM {tabla}")
    ###########################################################################
    
    # Confirmar los cambios y cerrar la conexión
    cnxn.commit()
    cursor.close()

    print(f'Se cargaron los datos a SQL SERVER {tabla}')
    print('Se cargaron los datos a FACTORING..[CARTERA]')
else:
    print('No se ha cargado a SQL SERVER')
    
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# =============================================================================
# CALCULANDO CONCENTRACIÓN DE DEUDORES EN LA CARTERA MENSUAL DE FACTORING
# =============================================================================

import pandas as pd
import pyodbc
import os

import warnings
warnings.filterwarnings('ignore')

#%%
CARGA_SQL_SERVER = True
tabla_nombre     = 'FACTORING..top_deudores'

#%%
conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')

query = '''
SELECT
	FechaCorte,
	[Ruc Deudor], 
	Deudor,
	[Monto Financiado SOLES],
	MN,
	[Nro Factura],
	[Valor Facial Neto SOLES] 
FROM FACTORING..[CARTERA]
'''
base = pd.read_sql_query(query, conn)

del conn

#%% pivot agrupamiento
pivot = base.pivot_table( values  = 'Monto Financiado SOLES',
                          index   = ['FechaCorte', 'Ruc Deudor'],
                          #columns = ,
                          aggfunc = 'sum').reset_index()

df = pivot.sort_values(by=['FechaCorte', 'Monto Financiado SOLES'], ascending=[True, False])

# Paso 2: Crear una función para asignar los rankings y etiquetar por grupos (top 1, top 5, top 10)
def clasificar_top(row):
    if row['rank'] == 1:
        return 'top 1'
    elif row['rank'] <= 5:
        return 'top 5'
    elif row['rank'] <= 10:
        return 'top 10'
    elif row['rank'] <= 20:
        return 'top 20'
    else:
        return 'fuera del top 20'

# Paso 3: Usar rank dentro de cada grupo de FechaCorte
df['rank'] = df.groupby('FechaCorte')['Monto Financiado SOLES'].rank(method='first', ascending=False)

# Paso 4: Aplicar la función clasificar_top a la nueva columna rank
df['clasificación'] = df.apply(clasificar_top, axis=1)
df['Monto Financiado SOLES'] = df['Monto Financiado SOLES'].round(2)

df.columns = ['FechaCorteTOP', 'Ruc DeudorTOP', 'Monto Financiado SOLESTOP', 'rankTOP', 'clasificaciónTOP']

#%% CARGA A SQL SERVER
if CARGA_SQL_SERVER == True:
    # Establecer la conexión con SQL Server
    cnxn = pyodbc.connect('DRIVER=SQL Server;SERVER=SM-DATOS;UID=SA;PWD=123;')
    cursor = cnxn.cursor()
    
    # nombre de la tabla en SQL
    tabla = tabla_nombre
    
    df = df[['FechaCorteTOP', 'Ruc DeudorTOP', 'rankTOP', 'clasificaciónTOP']].copy()
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

    print('Top deudores actualizado')
else:
    print('No se ha cargado a SQL SERVER')
