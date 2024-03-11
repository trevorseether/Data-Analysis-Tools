# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 09:28:40 2024

@author: sanmiguel38
"""
# =============================================================================
# Preparador del excel para comercial
# =============================================================================
import os
import pandas as pd

import pyodbc

import warnings
warnings.filterwarnings('ignore')

#%% PARÁMETROS INICIALES
tabla_LIMA    = '[reportes_diana]..[DXP_LD_24_02]'
tabla_PROSEVA = '[reportes_diana].[PROSEVAS].[2024_02]'
tabla_fincore = '[reportes_diana].[MYPE].[2024_02]'

CARGA_SQL_SERVER = True

#%%
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\DIANA LORENA\\2024 febrero\\descomprimidos')

lima       = 'CIERRE DRIVE LIMA_FEBRERO24.xlsx'
lima_sheet = 'FEBRERO24'

proseva       = 'CIERRE DRIVE PROSEVA_FEBRERO24.xlsx'
proseva_sheet = 'FEBRERO24'

fincore       = 'CIERRE FINCORE_FEBRERO24.xlsx'
fincore_sheet = 'Rpt_ResumenPrestamosXFuncionari'

fecha_corte = '2024-02-29'

#%%
lima_df = pd.read_excel(io = lima,
                        sheet_name = lima_sheet,
                        dtype = {'MONTO  PRESTAMO' : float})

lima_df = lima_df[['FECHA DESEMBOLSO',
                   'FUNCIONARIO/SEDE',
                   'EMPRESA',
                   'CONDICION',
                   'SOCIO',
                   'DOC (DNI/CE/RUC)',
                   'MONTO  PRESTAMO',
                   'CANAL OFICINA',
                   'FECHA DE REVISION',
                   'ANALISTA',
                   'ESTADO FINAL',
                   'PRODUCTO'
                   ]]

mask = lima_df['ESTADO FINAL'] == 'APROBADO'
lima_df['FECHA DESEMBOLSO'] = lima_df.loc[mask, 'FECHA DESEMBOLSO'].fillna(pd.to_datetime(fecha_corte))
lima_df['FECHA DE REVISION'] = lima_df['FECHA DE REVISION'].fillna(pd.to_datetime(fecha_corte))
lima_df['MONTO  PRESTAMO'] =pd.to_numeric(lima_df['MONTO  PRESTAMO'])

lima_df['MONTO  PRESTAMO'] = pd.to_numeric(lima_df['MONTO  PRESTAMO'], errors = 'coerce')

lima_df.dropna(subset = ['PRODUCTO', 
                         'FUNCIONARIO/SEDE',
                         'CONDICION',
                         'MONTO  PRESTAMO',
                         'ESTADO FINAL'], inplace = True, how = 'all')

cantidad_nulos = lima_df['ESTADO FINAL'].isnull().sum()

print("Cantidad de valores nulos en 'ESTADO FINAL':", cantidad_nulos)

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

# Función de análisis de fechas
def parse_dates(date_str):
    for formato in formatos:
        try:
            return pd.to_datetime(date_str, format=formato)
        except ValueError:
            pass
    return pd.NaT

lima_df['FECHA DESEMBOLSO'] = lima_df['FECHA DESEMBOLSO'].apply(parse_dates)
lima_df['FECHA DE REVISION'] = lima_df['FECHA DE REVISION'].apply(parse_dates)

#%%
proseva_df = pd.read_excel(io = proseva,
                           sheet_name = proseva_sheet,
                           dtype = {'DOC (DNI/CE/RUC)' : str})

proseva_df = proseva_df[['FECHA DESEMBOLSO',
                         'FUNCIONARIO/SEDE',
                         'EMPRESA',
                         'CONDICION',
                         'SOCIO',
                         'DOC (DNI/CE/RUC)',
                         'MONTO PRESTAMO',
                         'FECHA DE REVISION',
                         'ANALISTA',
                         'ESTADO FINAL',
                         'CANAL OFICINA',
                         'PRODUCTO'
                         ]]

proseva_df['DOC (DNI/CE/RUC)']    = proseva_df['DOC (DNI/CE/RUC)'].str.strip()

mask = proseva_df['ESTADO FINAL'] == 'APROBADO'
proseva_df['FECHA DESEMBOLSO']    = proseva_df.loc[mask, 'FECHA DESEMBOLSO'].fillna(pd.to_datetime(fecha_corte))

proseva_df['FECHA DE REVISION']   = proseva_df['FECHA DE REVISION'].fillna(pd.to_datetime(fecha_corte))

proseva_df['FECHA DESEMBOLSO']    = proseva_df['FECHA DESEMBOLSO'].apply(parse_dates)
proseva_df['FECHA DE REVISION']   = proseva_df['FECHA DE REVISION'].apply(parse_dates)

proseva_df['MONTO PRESTAMO']      = pd.to_numeric(proseva_df['MONTO PRESTAMO'], errors = 'coerce')

proseva_df.dropna(subset = ['PRODUCTO', 
                            'FUNCIONARIO/SEDE',
                            'CONDICION',
                            'MONTO PRESTAMO',
                            'ESTADO FINAL'], inplace = True, how = 'all')

cantidad_nulos = proseva_df['ESTADO FINAL'].isnull().sum()

print("Cantidad de valores nulos en 'ESTADO FINAL':", cantidad_nulos)

#%%
# creación de carpeta
nombre_carpeta = 'carpeta para sql'

if not os.path.exists(nombre_carpeta):
    os.makedirs(nombre_carpeta)
else:
    print('la carpeta ya existe')
    

# creación de los excels
lima_df.to_excel(f'carpeta para sql\\DXP_LD_{lima_sheet}.xlsx', index = False)

proseva_df.to_excel(f'carpeta para sql\\prosevas_{lima_sheet}.xlsx', index = False)

#%% CARGA A SQL

if CARGA_SQL_SERVER == True:
    # Establecer la conexión con SQL Server
    cnxn = pyodbc.connect('DRIVER=SQL Server;SERVER=SM-DATOS;UID=SA;PWD=123;')
    cursor = cnxn.cursor()
    df = lima_df.copy()
    df['FECHA DESEMBOLSO']  = df['FECHA DESEMBOLSO'].fillna(pd.Timestamp(fecha_corte))
    df['FECHA DE REVISION'] = df['FECHA DE REVISION'].fillna(pd.Timestamp(fecha_corte))
    df['MONTO  PRESTAMO']   = df['MONTO  PRESTAMO'].fillna(0)
    df = df.fillna('')
    
    # Limpiar/eliminar la tabla antes de insertar nuevos datos
    cursor.execute(f"IF OBJECT_ID('{tabla_LIMA}') IS NOT NULL DROP TABLE {tabla_LIMA}")    

    # Generar la sentencia CREATE TABLE dinámicamente
    create_table_query = f"CREATE TABLE {tabla_LIMA} ("
    for column_name, dtype in df.dtypes.items():
        sql_type = ''
        if dtype == 'int64':
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
    insert_query = f"INSERT INTO {tabla_LIMA} ({', '.join(column_names)}) VALUES ({value_placeholders})"

    # Iterar sobre las filas del DataFrame e insertar en la base de datos
    for _, row in df.iterrows():
        cursor.execute(insert_query, tuple(row))

    # Confirmar los cambios y cerrar la conexión
    cnxn.commit()
    cursor.close()

    print(f'Se cargaron los datos a SQL SERVER {tabla_LIMA}')

else:
    print('No se ha cargado a SQL SERVER')

###############################################################################

if CARGA_SQL_SERVER == True:
    # Establecer la conexión con SQL Server
    cnxn = pyodbc.connect('DRIVER=SQL Server;SERVER=SM-DATOS;UID=SA;PWD=123;')
    cursor = cnxn.cursor()
    df = proseva_df.copy()
    df['FECHA DESEMBOLSO']  = df['FECHA DESEMBOLSO'].fillna(pd.Timestamp(fecha_corte))
    df['FECHA DE REVISION'] = df['FECHA DE REVISION'].fillna(pd.Timestamp(fecha_corte))
    df['MONTO PRESTAMO']    = df['MONTO PRESTAMO'].fillna(0)
    df = df.fillna('')

    # Limpiar/eliminar la tabla antes de insertar nuevos datos
    cursor.execute(f"IF OBJECT_ID('{tabla_PROSEVA}') IS NOT NULL DROP TABLE {tabla_PROSEVA}")    

    # Generar la sentencia CREATE TABLE dinámicamente
    create_table_query = f"CREATE TABLE {tabla_PROSEVA} ("
    for column_name, dtype in df.dtypes.items():
        sql_type = ''
        if dtype == 'int64':
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
    insert_query = f"INSERT INTO {tabla_PROSEVA} ({', '.join(column_names)}) VALUES ({value_placeholders})"

    # Iterar sobre las filas del DataFrame e insertar en la base de datos
    for _, row in df.iterrows():
        cursor.execute(insert_query, tuple(row))

    # Confirmar los cambios y cerrar la conexión
    cnxn.commit()
    cursor.close()

    print(f'Se cargaron los datos a SQL SERVER {tabla_PROSEVA}')

else:
    print('No se ha cargado a SQL SERVER')

#%% LECTURA DEL ARCHIVO DE FINCORE

fincore_df = pd.read_excel(io         = fincore,
                           sheet_name = fincore_sheet,
                           dtype      = {'MONTO  PRESTAMO' : float,
                                         'N°\nPréstamo'    : str,
                                         'Código Socio'    : str,
                                         'N° DNI'          : str,
                                         'Celular'         : str},
                           skiprows   =	0)

fincore_df['Fecha\nPréstamo'] = fincore_df['Fecha\nPréstamo'].apply(parse_dates)

#%% CARGA DEL ARCHIVO DE FINCORE, DESTINADO A SER MYPE

if CARGA_SQL_SERVER == True:
    
    cnxn   = pyodbc.connect('DRIVER=SQL Server;SERVER=SM-DATOS;UID=SA;PWD=123;') 
    cursor = cnxn.cursor()
    df     = fincore_df.copy()
    tabla  = tabla_fincore
    df     = df.fillna(0)
    df     = df.rename(columns = {'Fecha\nPréstamo': "Fecha_Préstamo"})
    
    # Limpiar/eliminar la tabla antes de insertar nuevos datos
    cursor.execute(f"IF OBJECT_ID('{tabla}') IS NOT NULL DROP TABLE {tabla}")    

    # Generar la sentencia CREATE TABLE dinámicamente
    create_table_query = f"CREATE TABLE {tabla} ("
    for column_name, dtype in df.dtypes.items():
        sql_type = ''
        if dtype == 'int64':
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

#%%

