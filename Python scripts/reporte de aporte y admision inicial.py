# -*- coding: utf-8 -*-
"""
Created on Fri Aug 11 09:09:35 2023

@author: Joseph Montoya
"""

import pandas as pd
import os
import pyodbc
#%%

os.chdir('C:\\Users\\sanmiguel38\\Desktop\\REPORTE DE APORTE Y ADMISIO\\2023 AGOSTO') #si cambiamos de mes, creamos la carpeta manualmente
hora = '9am'

#%%
server = '172.16.1.19\SQL_SANMIGUEL'
username = 'USER_LECTURA'
password = '123456789@T'

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'

conn = pyodbc.connect(conn_str)
########################################################
###                CAMBIAR LAS FECHAS               ######
########################################################

fecha1 = '20230816' 
fecha2 = '20230816'
################################################################
## si estamos de martes a vienes, ponemos el día anterior en ambos
## si es lunes, ponemos la fecha del viernes(1) y sábado(2) anterior
##
################################################################
query = f'''
DECLARE @Fecha1 DATETIME='{fecha1}'
DECLARE @Fecha2 DATETIME='{fecha2}'
 
SELECT
	Cc.IDVOUCHER,
	CC.CodTipoCaja ,
    s.CodigoSocio ,
        LEFT(CONCAT(LEFT(CONCAT(
    LTRIM(RTRIM(REPLACE(REPLACE(REPLACE(REPLACE(
    REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
    IIF(S.CodTipoPersona=1,CONCAT(LTRIM(RTRIM(S.ApellidoPaterno)),SPACE(1),LTRIM(RTRIM(S.ApellidoMaterno)),SPACE(1), LTRIM(RTRIM(S.Nombres)))
    ,RTRIM(LTRIM(S.RazonSocial)))
    ,'=',''),'&',''),'/',''),'=',''),')',''),'#',''),'.',''),'Ñ','N'),'"',''),'(','')
        ,'Á','A'),'É','E'),'Í','I'),'Ó','O'),'Ú','U'
        ),CHAR(9),''),CHAR(10),''),CHAR(13),'')
        )),SPACE(150)),150),SPACE(150)),150) AS 'Socio',
        ISNULL(CONVERT(Varchar(10),CC.Fecha,103),' ') As 'FechaPago',
        CC.Concepto,CC.Total,
 
        AD.NumeroOperacionDestino, 
		EF.Descripcion AS 'Banco',
		C.NumeroCuenta,
        CC.FechaRegistro, 
		U.IdUsuario 

FROM  
	Socio AS S  
	INNER JOIN CajaCab CC ON S.CodSocio =CC.CodSocio 
	LEFT JOIN AdmisionDocumento AS AD ON CC.CodAdmisionDocumento =AD.CodAdmisionDocumento 
	LEFT JOIN TABLAMAESTRADET AS TM ON TM.CODTABLADET=AD.CODMONEDA
	LEFT JOIN EntidadFinanciera AS EF ON AD.CodBancoDestino =EF.CodEntidadFinanciera
	LEFT JOIN Usuario AS U ON CC.CodCajero =U.CodUsuario 
	LEFT JOIN  Cuenta AS C ON AD.CodCuentaDestino = C.CodCuenta 

WHERE
(CONVERT(Varchar(10),CC.Fecha,112)>=CONVERT(Varchar(10),@Fecha1,112) AND CONVERT(Varchar(10),CC.Fecha,112)<=CONVERT(Varchar(10),@Fecha2,112))
AND
--CC.Total>0 AND CC.Concepto LIKE 'APORTE INICIAL' 
CC.Total>0 AND (CC.Concepto LIKE 'APORTE%' or CC.Concepto LIKE 'CONCEPTO DE ADMISIÓN%')

ORDER BY CC.CONCEPTO, CC.Fecha 


----
--SELECT * FROM TablaMaestraDet WHERE CodTablaCab =97

--SELECT * FROM CajaCab WHERE IdVoucher ='I0577942'

'''
df_aporte_admision = pd.read_sql_query(query, conn,
                               dtype={'IDVOUCHER': str,
                                      'CodTipoCaja': str,
                                      'CodigoSocio': str,
                                      'Socio': str})
del conn

#%%
# GENERAMOS EL EXCEL
n1 = str(fecha1[6:])
n2 = str(fecha2[6:])

nombre_archivo = f'Aporte y Admision Inicial del {n1} al {n2}-08-23 - corte {hora}.xlsx'

df_aporte_admision.to_excel(nombre_archivo,
                            index=(False))
