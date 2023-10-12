# -*- coding: utf-8 -*-
"""
Created on Tue May 16 09:25:02 2023

@author: Joseph Montoya
"""

###############################################################################
##########     NUEVO REPORTE SEGMENTACIÓN     #################################
###############################################################################
# para Experian, la estructura es prácticamente la misma que del reporte de reprogramados
# antes este reporte era mensual, ahora es trimestral
# osea que elaboraremos de marzo, junio, setiembre y diciembre (en el mes siguiente)

#%% importación de módulos
import pandas as pd
import os 
import pyodbc

#%% FECHA DE CORTE, DIRECTORIO DE TRABAJO

mes = 'SETIEMBRE 2023'
# ubicación
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\SEGMENTACIONES\\2023 setiembre') 
#en esta ubicación debemos poner el archivo de reprogramados que se manda a principio del mes

## donde dice @fechacorte se debe poner el mes ################################
fecha_corte_sql = '20230930'                                                  #
###############################################################################
#este reporte es trimestral pero solo van los datos del último mes

## REPORTE DE REPROGRAMADOS QUE SE MANDA A EXPERIAN ###########################
repo_reprogramados = 'Setiembre Reprogramados - 2023.xlsx'
###############################################################################

#%% IMPORTACIÓN DEL ANEXO06 DEL SQL

conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')

QUERY = f'''
DECLARE @FECHA AS DATETIME
SET @FECHA = '{fecha_corte_sql}'

SELECT 
	CodigoSocio7 AS 'CODIGO SOCIO',
	TipodeDocumento9 AS 'TIPO DOCUMENTO',
	NumerodeDocumento10 AS 'NUMERO DOCUMENTO',
	TipodeCredito19 AS 'TIPO DE CREDITO',
	Saldodecolocacionescreditosdirectos24 - IngresosDiferidos42 as 'DEUDA DIRECTA',
	NULL as 'TIPO DE REPROGRAMACION',
	Reprogramados52 AS 'DEUDA REPROGRAMADA' 

FROM 
	anexos_riesgos2..Anx06_preliminar
WHERE 
	FechaCorte1 = @FECHA
ORDER BY ApellidosyNombresRazonSocial2           
                       '''
                       
df = pd.read_sql_query(QUERY, conn, dtype = {'TIPO DOCUMENTO' : str})
del conn  #para limpiar el explorador de variables

#%% DETECCIÓN DE ERRORES
#por si acaso hay que buscar si existe tipo de documento 0
errores= df[df['TIPO DOCUMENTO'] == 0]
#si hay, podemos corregir con un update en la misma base de datos
print(errores)

#%% STRIP DE TEXTO
df['CODIGO SOCIO'] = df['CODIGO SOCIO'].str.strip() 
df['NUMERO DOCUMENTO'] = df['NUMERO DOCUMENTO'].str.strip()

#%% IMPORTACIÓN DE LOS REPROGRAMADOS

reprogramados = pd.read_excel(repo_reprogramados,
                              skiprows = 1,
                              dtype = {'CODIGO SOCIO'    : object,
                                       'TIPO DOCUMENTO'  : str,
                                       'NUMERO DOCUMENTO': object,
                                       'TIPO DE CREDITO' : object})

#merge
para_merge = reprogramados[['CODIGO SOCIO','TIPO DE REPROGRAMACION']]
para_merge = para_merge.rename(columns = {'CODIGO SOCIO': 'cod para merge'})
para_merge = para_merge.rename(columns = {'TIPO DE REPROGRAMACION': 'tipo para merge'})

df_resultado = df.merge(para_merge, 
                         left_on  = ['CODIGO SOCIO'], 
                         right_on = ['cod para merge'],
                         how      = 'left')

df_resultado['TIPO DE REPROGRAMACION'] = df_resultado['tipo para merge']

df_resultado.drop(['cod para merge', 'tipo para merge'], axis=1, inplace=True)

#%% VERIFICACIÓN EL MERGE
#para comprobar si hizo buen match
#si la diferencia es diferente de cero hay que revisar
r = reprogramados['DEUDA REPROGRAMADA'].sum().round(2)
d = df_resultado['DEUDA REPROGRAMADA'].sum().round(2)

print('diferencia: ', r-d)
print('el resultado debe ser cero, sino no han hecho match todos los reprogramados del mes')

#%% CREACIÓN DEL EXCEL

nombre = 'SEGMENTACION '+ mes + ' Coopac San Miguel - Estructura Experian.xlsx'
try:
    ruta = nombre
    os.remove(ruta)
except FileNotFoundError:
    pass

df_resultado.to_excel(nombre,
                sheet_name=mes,
                index=False)


