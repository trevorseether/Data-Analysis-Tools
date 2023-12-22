# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 10:46:51 2023

@author: Joseph Montoya Muñoz
"""
'''
###############################################################################
##          CRUCE DE BAJAS DE KONECTA
###############################################################################
'''
#%% IMPORTACIÓN DE MÓDULOS

import pandas as pd
import os
import pyodbc
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')
from colorama import Back # , Style, init, Fore

#%% DIRECTORIO DE TRABAJO, fecha actual

'AQUI SE PONE LA FECHA DE HOY' #############################################
FECHATXT = '26-12-2023'  # FORMATO DÍA-MES-AÑO
############################################################################

'directorio de trabajo' ####################################################
directorio = 'C:\\Users\\sanmiguel38\\Desktop\\BAJAS KONECTA\\2023 diciembre\\18 dic\\Nueva carpeta'
############################################################################

'NOMBRE DEL ARCHIVO DE BAJAS ENVIADO' ######################################
nombre_archivo = '3ER INFORME DE BAJAS GRUPO.xlsx'
############################################################################

'filas a skipear' ######################
filas_skip = 0
########################################

#%%
server   = '172.16.1.19\SQL_SANMIGUEL'
username = 'USER_LECTURA'
password = '123456789@TT'

#%% IMPORTANDO EL INFORME DE BAJAS

os.chdir(directorio)

bajas = pd.read_excel(nombre_archivo,
                      skiprows = filas_skip,
                      dtype    = ({'Documento': object}))

bajas['Documento'] = bajas['Documento'].astype(str)
bajas['Documento'] = bajas['Documento'].str.strip()

doc_nulos = bajas[pd.isna(bajas['Documento'])]
print('Documentos que se hayan convertido en Null:')
print(doc_nulos.shape[0])
bajas['Documento original'] = bajas['Documento']
bajas['Documento'] = bajas['Documento'].str.zfill(14)
print('Documentos que se hayan convertido en Null:')

if doc_nulos.shape[0] > 0:
    print(doc_nulos)
    print(Back.RED + 'investigar qué ha pasado')
else:
    print(doc_nulos.shape[0])
    del doc_nulos
    print(Back.GREEN + 'todo bien')

#%% LECTURA DE LAS CREDENCIALES
# =============================================================================
# datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')
# 
# #%% CREACIÓN DE LA CONECCIÓN A SQL
# 
# server      = datos['DATOS'][0]
# username    = datos['DATOS'][2]
# password    = datos['DATOS'][3]
# 
# =============================================================================

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'

conn = pyodbc.connect(conn_str)

#%% QUERY, créditos vigentes

def convertir_fecha(fecha_str):
    try:
        # Parsea la fecha de entrada en formato 'dd-mm-yyyy'
        fecha = datetime.strptime(fecha_str, '%d-%m-%Y')
        # Formatea la fecha en el formato 'yyyymmdd'
        fecha_formateada = fecha.strftime('%Y%m%d')
        return fecha_formateada
    except ValueError:
        return "Formato de fecha incorrecto. Debe ser 'dd-mm-yyyy'."

fecha_formateada = convertir_fecha(FECHATXT)

###############################################################################
fecha_hoy = fecha_formateada ######### AQUÍ VA LA FECHA DE HOY
###############################################################################
query = f'''
SELECT
    s.codigosocio,
    IIF(s.CodTipoPersona = 1, CONCAT(S.ApellidoPaterno, ' ', S.ApellidoMaterno, ' ', S.Nombres), s.razonsocial) AS 'Socio',
    IIF(s.CodTipoPersona = 1, s.nroDocIdentidad, s.nroruc) AS 'Doc_Identidad',
    RIGHT(CONCAT('0000000', p.numero), 8) AS 'pagare_fincore',
    p.fechadesembolso,
    p.CuotaFija,
    tm.descripcion AS 'Estado',
    pla.descripcion AS 'Planilla'
FROM prestamo AS p
INNER JOIN socio AS s ON s.codsocio = p.codsocio
LEFT JOIN sociocontacto AS sc ON sc.codsocio = s.codsocio
LEFT JOIN planilla AS pla ON p.codplanilla = pla.codplanilla
INNER JOIN tablaMaestraDet AS tm ON tm.codtabladet = p.CodEstado
LEFT JOIN pais ON pais.codpais = s.codpais
LEFT JOIN FINALIDAD AS FI ON FI.CODFINALIDAD = P.CODFINALIDAD
INNER JOIN usuario AS u ON p.CodUsuario = u.CodUsuario
WHERE CONVERT(VARCHAR(10), p.fechadesembolso, 112) BETWEEN '20110101' AND '{fecha_formateada}'
    AND s.codigosocio > 0
    AND p.codestado = 341
ORDER BY socio ASC, p.fechadesembolso DESC;
'''
vigentes = pd.read_sql_query(query, 
                             conn, 
                             dtype = {'Doc_Identidad'  : object,
                                      'codigosocio'    : object,
                                      'pagare_fincore' : object,
                                      'fechadesembolso': object
                                      })

del conn
#%% PARSEO DE FECHAS

formatos = ['%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y',
            '%Y%m%d', 
            '%Y-%m-%d', 
            '%Y-%m-%d %H:%M:%S', 
            '%Y/%m/%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S PM',
            '%Y-%m-%d %H:%M:%S AM']  # Lista de formatos a analizar
def parse_dates(date_str):
    for formato in formatos:
        try:
            return pd.to_datetime(date_str, format = formato)
        except ValueError:
            pass
    return pd.NaT

vigentes['fechadesembolso'] = vigentes['fechadesembolso'].apply(parse_dates)

#%% FILTRAMOS ESTADO = PENDIENTE
'por si acaso, nos quedamos solo con los que tienen estado = pendiente'

vigentes["Estado"] = vigentes["Estado"].str.strip() #quitamos espacios
vigentes["Estado"] = vigentes["Estado"].str.upper() #mayúsculas

vigentes = vigentes[vigentes["Estado"] == 'PENDIENTE']

#%% 14 ceros para merge
'agregamos 14 ceros al reporte EXTRAIDO CON SQL'
vigentes["Doc_Identidad"] = vigentes["Doc_Identidad"].astype(str)
vigentes["DOC_IDENTIDAD_ceros"] = vigentes["Doc_Identidad"].str.zfill(14)

#%%SELECCIÓN DE COLUMNAS
'nos quedamos solo con las columnas necesarias'

vigentes2 = vigentes[["DOC_IDENTIDAD_ceros", 
                      "Socio", 
                      "fechadesembolso", 
                      "pagare_fincore", 
                      "CuotaFija", 
                      "Planilla"]]

vigentes2 = vigentes2.rename(columns = {"Doc_Identidad"   : "DOC_IDENTIDAD",
                                        "Socio"           : "SOCIO",
                                        "fechadesembolso" : "FECHA_DESEMBOLSO",
                                        "pagare_fincore"  : "PAGARE_FINCORE",
                                        "CuotaFija"       : "CUOTA MENSUAL",
                                        "Planilla"        : "EMPRESA/PLANILLA"})

bajas2 = bajas[['Documento', 'Documento original']]

#%% INNER JOIN
'inner join usando '
df_resultado = vigentes2.merge(bajas2, 
                               left_on  = ["DOC_IDENTIDAD_ceros"], 
                               right_on = ['Documento'],
                               how      = 'inner')

#%% DATAFRAME FINAL
'''creamos el archivo final'''

#df_resultado['SALDO A DESCONTAR'] = np.nan
#df_resultado['# CUOTAS'] = np.nan

final = df_resultado[['Documento original',
                      'SOCIO', 
                      'FECHA_DESEMBOLSO', 
                      #'SALDO A DESCONTAR', 
                      #'# CUOTAS',
                      "CUOTA MENSUAL",
                      'PAGARE_FINCORE', 
                      "EMPRESA/PLANILLA"]]

final = final.rename(columns = {'Documento original' : 'Documento'})

# POR SI ACASO, ELIMINAMOS DUPLICADOS
final.drop_duplicates(subset = 'PAGARE_FINCORE', inplace = True)

#%% CREACIÓN DE EXCEL

NOMBRE = 'BAJAS '+ FECHATXT + '.xlsx'

try:
    os.remove(NOMBRE)
except FileNotFoundError:
    pass

final.to_excel(NOMBRE, index=False,
               sheet_name=FECHATXT)


