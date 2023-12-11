# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 16:50:14 2023

@author: Joseph Montoya
"""

# =========================================================================== #
#                                                                             #  
#              AUTOMATIZACIÓN DE RECAUDACIÓN DE PLANILLAS                     #
#                                                                             #
# =========================================================================== #

import pandas as pd
import os
import pyodbc
from colorama import Back # , Style, init, Fore

#%%
# FECHA CORTE PARA SQL ========================================================
fecha_corte = '20231031'
# =============================================================================

# DIRECTORIO DE TRABAJO =======================================================
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\RECAUDACIÓN\\2023 octubre')
# =============================================================================

# RECAUDACIÓN DEL MES =========================================================
nombre = '10 - OCTUBRE 2023 (CIERRE).xlsx'
# =============================================================================

# # UBICACIÓN DEL ANEXO 06=======================================================
# En caso de usar el anexo06 debemos reemplazar la conección a sql server (línea 150)
# ubi_anx = 'C:\\Users\\sanmiguel38\\Desktop'
# # =============================================================================

# # NOMBRE DEL ANEXO 06 =========================================================
# anexo_06 = 'Rpt_DeudoresSBS Anexo06 - Setiembre 2023 - campos ampliados v04.xlsx'
# # =============================================================================

# AQUÍ AÑADIMOS O QUITAMOS LAS PESTAÑAS DEL EXCEL, en el primero va el nombre de la columna
datos = {'cs': ['Masivo - CS'],
         'ml': ['Masivo - ML'],
         'av': ['Masivo - AV'],
         'kt': ['Masivo - KT'],
         }
# ============================================================================= 
#%%
# Convertimos el diccionario en dataframe
datos = pd.DataFrame(datos)

dataframes = {}  # Diccionario para almacenar los DataFrames
# Creación de diccionario donde estarán almacenados los DataFrames
for columna in datos.columns:
    nombre_df = columna  # Utilizamos el nombre de la columna como nombre del DataFrame
    dataframes[nombre_df] = pd.read_excel(io         = nombre, 
                                          sheet_name = datos[columna][0], 
                                          skiprows   = 4, # todas las sheets deben tener 4 filas para skip 
                                          dtype      = {})

# =============================================================================
# cs = pd.read_excel(nombre,
#                    sheet_name = 'Masivo - CS',
#                    skiprows   = 4,
#                    dtype      = {})
# 
# ml = pd.read_excel(nombre,
#                    sheet_name = 'Masivo - ML',
#                    skiprows   = 4,
#                    dtype      = {})
# 
# av = pd.read_excel(nombre,
#                    sheet_name = 'Masivo - AV',
#                    skiprows   = 4,
#                    dtype      = {})
# 
# kt = pd.read_excel(nombre,
#                    sheet_name = 'Masivo - KT',
#                    skiprows   = 4,
#                    dtype      = {})
# 
# =============================================================================
# con el tiempo habría que añadir y/o retirar algunas de estas sheets de excel
# =============================================================================

#%% nos quedamos con las columnas necesarias y luego concatenamos los dataframes
columnas = ['PLANILLA',
            #'PROSEVA',
            'MONTO ENVIADO',
            'MONTO DEL MES',
            'RECIBIDO MASIVO',
            #'PAGO INDEPENDIENTE',
            'REINTEGROS',
            'SALDO',
            '% COBRANZA']

# Metemos los dataframes en una lista luego de filtrar las columnas necesarias para poder concatenarlos:
dataframes_filtrados = []
for nombre_columna, dataframe in dataframes.items():
    # Filtra las columnas en cada DataFrame
    dataframe_filtrado = dataframe[columnas]
    
    # Agrega el DataFrame filtrado a la lista
    dataframes_filtrados.append(dataframe_filtrado)
    
# Concatenamos
df_concatenado = pd.concat(dataframes_filtrados, 
                           ignore_index = True)
# Mayúsculas
df_concatenado['PLANILLA'] = df_concatenado['PLANILLA'].str.upper()

# Reemplazos recurrentes
df_concatenado.loc[df_concatenado['PLANILLA'] == 'MINISTERIO DE JUSTICIA - RECAS',       'PLANILLA'] = 'MINISTERIO DE JUSTICIA Y DERECHOS HUMANOS - RECAS'
df_concatenado.loc[df_concatenado['PLANILLA'] == 'MINISTERIO DE JUSTICIA - PENSIONISTA', 'PLANILLA'] = 'MINISTERIO DE JUSTICIA Y DERECHOS HUMANOS - PENSIONISTA'
df_concatenado.loc[df_concatenado['PLANILLA'] == 'MINISTERIO DE JUSTICIA - NOMBRADOS',   'PLANILLA'] = 'MINISTERIO DE JUSTICIA Y DERECHOS HUMANOS - NOMBRADOS'

# debemos revisar si hay duplicados
duplicados = df_concatenado[df_concatenado.duplicated(subset = 'PLANILLA', 
                                                      keep   = False)]
if duplicados.shape[0] == 0:
    print(Back.GREEN + 'SIN DUPLICADOS')
else:
    print(Back.RED + '🚨 PLANILLAS DUPLICADAS 🚨')
    print(duplicados['PLANILLA'])

# ====== por si necesitamos exportalo a excel (no creo) =======================
# df_concatenado.to_excel('concatenado.xlsx',
#                         index = False)
# =============================================================================
#%% CONECCIÓN AL SQL
conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')

base = pd.read_sql_query(f'''
DECLARE @fechacorte as datetime
SET @fechacorte = '{fecha_corte}'
---------------
SELECT 
	Nro_Fincore, CodigoSocio7, NumerodeCredito18, 
	Monedadelcredito17, ApellidosyNombresRazonSocial2,
	Saldodecolocacionescreditosdirectos24, CapitalenCobranzaJudicial30,
	CapitalVencido29, A.NUEVA_PLANILLA, A.PLANILLA,
    CASE
		WHEN A.PLANILLA = 'PLANILLA LIQUIDADOS' THEN A.NUEVA_PLANILLA
		ELSE A.PLANILLA
		END AS 'PLANILLA BIEN',
	a.Departamento, a.[Dpto Negocio],
	Situacion_Credito, Origen_Coopac, 
	P.EMPRESA, P.PLANILLA_CORREGIDA as 'PLANILLA_CORREGIDA',
	a.Departamento

FROM  
	anexos_riesgos2..Anx06_preliminar A

LEFT JOIN Anexos_Riesgos..PLANILLA2 P
	ON (LTRIM(RTRIM(A.NUEVA_PLANILLA)) =  LTRIM(RTRIM(P.NUEVA_PLANILLA)))
	WHERE FechaCorte1 = @fechacorte

''', conn)

del conn

# base = pd.read_excel(ubi_anx + '\\' + anexo_06,
#                      skiprows = 2,
#                      dtype    = {'Nro Prestamo \nFincore' : str})
# 
# base.rename(columns={'PLANILLA CONSOLIDADA'  : 'PLANILLA BIEN',
#                      'Planilla Anterior TXT' : 'PLANILLA',
#                      'Nombre PlanillaTXT'    : 'NUEVA_PLANILLA'}, inplace = True)

#%% Reemplazos recurrentes
base.loc[base['PLANILLA BIEN'] == 'MINISTERIO DE JUSTICIA - RECAS',       'PLANILLA BIEN'] = 'MINISTERIO DE JUSTICIA Y DERECHOS HUMANOS - RECAS'
base.loc[base['PLANILLA BIEN'] == 'MINISTERIO DE JUSTICIA - PENSIONISTA', 'PLANILLA BIEN'] = 'MINISTERIO DE JUSTICIA Y DERECHOS HUMANOS - PENSIONISTA'
base.loc[base['PLANILLA BIEN'] == 'MINISTERIO DE JUSTICIA - NOMBRADOS',   'PLANILLA BIEN'] = 'MINISTERIO DE JUSTICIA Y DERECHOS HUMANOS - NOMBRADOS'


#%% MERGE
df_concatenado.rename(columns={'PLANILLA': 'PLANILLA COBRANZAS'}, inplace = True)

df_resultado = base.merge(df_concatenado[['PLANILLA COBRANZAS',
                                          'MONTO ENVIADO',
                                          'MONTO DEL MES',
                                          'RECIBIDO MASIVO',
                                          #'PAGO INDEPENDIENTE',
                                          'REINTEGROS',
                                          '% COBRANZA']], #AÑADIR LAS COLUMNAS QUE PODRÍAN SER NECESARIAS
                         left_on  = ['PLANILLA BIEN'], 
                         right_on = ['PLANILLA COBRANZAS'],
                         how      = 'left')

# vemos qué planillas del reporte de recaudación NO hacen match
# no_match = df_concatenado[~df_concatenado['PLANILLA COBRANZAS'].isin(base['PLANILLA BIEN'])] # coincidencia exacta

base_sin_duplicados = base[['PLANILLA BIEN', 'PLANILLA', 'NUEVA_PLANILLA']].drop_duplicates(subset = ['PLANILLA BIEN'])
no_match = df_concatenado.merge(base_sin_duplicados, #AÑADIR LAS COLUMNAS QUE PODRÍAN SER NECESARIAS
                                left_on  = ['PLANILLA COBRANZAS'], 
                                right_on = ['PLANILLA BIEN'],
                                how      = 'left')
    
no_match = no_match[pd.isna(no_match['PLANILLA BIEN'])]

no_match[['PLANILLA COBRANZAS',
          'MONTO ENVIADO',
          'MONTO DEL MES',
          'RECIBIDO MASIVO',
          #'PAGO INDEPENDIENTE',
          'REINTEGROS',
          'SALDO',
          '% COBRANZA']].to_excel('NO HACEN MATCH.xlsx', 
                                  index = False)
                                  
#%% buscador del nombre de las planillas para corregirlas

busqueda = 'poder judicial'
planillas_masomenos_ese_nombre = base_sin_duplicados[base_sin_duplicados['PLANILLA BIEN'].str.contains(busqueda)]['PLANILLA BIEN']
'revisar las planillas que masomenos contienen ese nombre'
#%% BUSCADOR DE NOMBRE DE LAS PLANILLAS
texto = 'tli alma'
aver = no_match[no_match['PLANILLA COBRANZAS'].str.contains(texto.upper(), 
                                                            na = False)]

#%% VERIFICACIÓN DE LOS QUE NO HACEN MATCH
# investigar = df_resultado[pd.isna(df_resultado['PLANILLA COBRANZAS'])]

# investigar.drop_duplicates(subset = 'PLANILLA BIEN', inplace = True)
# investigar = investigar[(investigar['PLANILLA BIEN'] != 'LIBRE DISPONIBILIDAD') &
#                         (investigar['PLANILLA BIEN'] != 'MICROEMPRESA')         &
#                         (investigar['PLANILLA BIEN'] != 'PEQUEÑA EMPRESA')]

# investigar.to_excel('NO HACEN MATCH.xlsx',
#                     index = False)
#%%
conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')

query_final = f'''
        declare @fechacorte as datetime
        set @fechacorte = '{fecha_corte}'

        SELECT  
	         FechaCorte1        as 'FechaCorte',
	         CodigoSocio7		as 'CodSocio',
	         NumerodeCredito18	as 'CodCredito',
	         Monedadelcredito17	as 'CodMoneda',
	         '' as 'Desc_Envio',
	         '' as 'Desc_pago',
	         '' as 'recaudacion',
	    Nro_Fincore as 'Nro_Fincore'

        FROM  anexos_riesgos2..Anx06_preliminar A
        WHERE FechaCorte1 = @fechacorte'''

base_final = pd.read_sql_query(query_final, conn)
del conn

#%%

df_resultado['MONTO DEL MES']      = df_resultado['MONTO DEL MES'].astype(float)
df_resultado['RECIBIDO MASIVO']    = pd.to_numeric(df_resultado['RECIBIDO MASIVO'], errors = 'coerce')
df_resultado['RECIBIDO MASIVO']    = df_resultado['RECIBIDO MASIVO'].fillna(0)
#df_resultado['PAGO INDEPENDIENTE'] = df_resultado['PAGO INDEPENDIENTE'].astype(float)
df_resultado['REINTEGROS']         = df_resultado['REINTEGROS'].astype(float)
df_resultado['REINTEGROS']         = pd.to_numeric(df_resultado['REINTEGROS'], errors = 'coerce')

base_final2 = base_final.merge(df_resultado[['Nro_Fincore',
                                             'MONTO DEL MES',
                                             'RECIBIDO MASIVO',
                                             #'PAGO INDEPENDIENTE',
                                             'REINTEGROS',
                                             '% COBRANZA']], #AÑADIR LAS COLUMNAS QUE PODRÍAN SER NECESARIAS
                         left_on  = ['Nro_Fincore'], 
                         right_on = ['Nro_Fincore'],
                         how      = 'left')
print(base_final2.shape[0])
base_final2.drop_duplicates(subset = 'Nro_Fincore', inplace = True)
print(base_final2.shape[0])
print('si sale menos en el segundo, es porque hubo duplicados')

base_final2['MONTO DEL MES'] = base_final2['MONTO DEL MES'].fillna(0)
base_final2['RECIBIDO MASIVO'] = base_final2['RECIBIDO MASIVO'].fillna(0)
# base_final2['PAGO INDEPENDIENTE'] = base_final2['PAGO INDEPENDIENTE'].fillna(0)
base_final2['REINTEGROS'] = base_final2['REINTEGROS'].fillna(0)

base_final2['Desc_Envio']   = base_final2['MONTO DEL MES']
base_final2['Desc_pago']    = base_final2['RECIBIDO MASIVO'] +  - base_final2['REINTEGROS'] # + base_final2['PAGO INDEPENDIENTE']
base_final2['recaudacion']  = base_final2['% COBRANZA']

# Convertimos a numérico:
base_final2['recaudacion'] = pd.to_numeric(base_final2['recaudacion'], 
                                           errors = 'coerce')

# Reemplaza NaN con cero:
base_final2['recaudacion'].fillna(0,
                                  inplace = True)
base_final2['Desc_pago'].fillna(0,
                                inplace = True)
base_final2['Desc_Envio'].fillna(0,
                                 inplace = True)

base_final3 = base_final2[['FechaCorte',
                           'CodSocio',
                           'CodCredito',
                           'CodMoneda',
                           'Desc_Envio',
                           'Desc_pago',
                           'recaudacion',
                           'Nro_Fincore']]

#%% to excellllllll
base_final3.to_excel(f'recaudación para sql {fecha_corte}.xlsx',
                     index = False)

#%%
# AQUÍ PONERLE EL RESULTADO DEL OTRO, HACER UN MERGE

# = Para insertar la recaudación una vez creada ===============================
# insert into RECAUDACION..Cabecera_Pagos
# select * from RECAUDACION..recaudacion20230930
# =============================================================================

# añadir las planillas faltantes a la lista de planillas ======================





