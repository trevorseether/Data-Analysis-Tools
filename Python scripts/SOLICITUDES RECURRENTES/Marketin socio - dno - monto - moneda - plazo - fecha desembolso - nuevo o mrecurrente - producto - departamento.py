# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 09:29:02 2024

@author: sanmiguel38
"""
# =============================================================================
# socio / dno / monto / moneda / plazo / fecha desembolso / nuevo o mrecurrente / producto / departamento
# =============================================================================

import pandas as pd
import os
import pyodbc
import warnings
warnings.filterwarnings('ignore')

#%% 
# FECHAS PARA LA RECAUDACIÓN:
fecha_inicio = '20240101'   # recordar que tiene que ser el inicio del mes
fecha_final  = '20241130'

# DIRECTORIO DE TRABAJO:
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\MARKETING\\desembolsos 2024')

#%% QUERY
datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')

server    =  datos['DATOS'][0]
username  =  datos['DATOS'][2]
password  =  datos['DATOS'][3]

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'

conn = pyodbc.connect(conn_str)

query = f'''
-- p.codcategoria = 351 -> nuevo
-- p.codcategoria = 352 -> ampliacion
-- p.codestado = 563 -> anulado
-- p.codestado = 341 -> pendiente
-- p.codestado = 342 -> cancelado
-- tc.CODTIPOCREDITO -> ( 3=Cons.Ordinario / 1=Med.Empresa / 2=MicroEmp. / 9=Peq.Empresa)

SELECT
	RIGHT(CONCAT('0000000',p.numero),8) as 'pagare_fincore',
	iif(s.CodTipoPersona =1, CONCAT(S.ApellidoPaterno,' ',S.ApellidoMaterno, ' ', S.Nombres),s.razonsocial) AS 'Socio',
	iif(s.CodTipoPersona =1, s.nroDocIdentidad, s.nroruc) AS 'Doc_Identidad',
	iif(p.codmoneda=94,'S/','US$') as 'moneda', 
	p.montosolicitado as 'Otorgado', 
	iif(p.CodMoneda='95', tcsbs.tcsbs, 1) as 'TC_SBS',
	p.fechadesembolso, 
	p.montosolicitado * iif(p.CodMoneda='95', tcsbs.tcsbs, 1) AS 'Monto Otorgado en soles',
	p.NroPlazos, 
	p.fechadesembolso, 
	FI.CODIGO AS 'COD_FINALIDAD', 
	FI.DESCRIPCION AS 'FINALIDAD', 
	iif(p.codcategoria=351,'NVO','AMPL') as 'RECURRENCIA', 
	CASE
            WHEN FI.CODIGO IN (34,35,36,37,38,39) THEN 'DXP'
            WHEN FI.CODIGO IN (32) THEN 'MULTIOFICIOS'
            WHEN FI.CODIGO IN (26) THEN 'EMPRENDE MUJER'
            WHEN FI.CODIGO IN (30,31,33) THEN 'LIBRE DISPONIBILIDAD'
            WHEN FI.CODIGO IN (33) THEN 'LD - INDEPENDIENTE'
            WHEN FI.CODIGO IN (15,16,17,18,19) THEN 'PEQUEÑA EMPRESA'
            WHEN FI.CODIGO IN (21,22,23,24,25,27,28,29) THEN 'MICRO EMPRESA'
            WHEN FI.CODIGO IN (95,96,97,98,99) THEN 'MEDIANA EMPRESA'
            WHEN FI.CODIGO IN (41,45) THEN 'HIPOTECARIA'
		END AS 'PRODUCTO',
	dp.nombre  AS 'departamento'


FROM prestamo AS p

INNER JOIN socio AS s             ON s.codsocio = p.codsocio
LEFT JOIN sociocontacto AS sc     ON sc.codsocio = s.codsocio
LEFT JOIN planilla AS pla         ON p.codplanilla = pla.codplanilla
INNER JOIN grupocab AS pro        ON pro.codgrupocab = p.codgrupocab
INNER JOIN distrito AS d          ON d.coddistrito = sc.coddistrito
INNER JOIN provincia AS pv        ON pv.codprovincia = d.codprovincia
INNER JOIN departamento AS dp     ON dp.coddepartamento = pv.coddepartamento
INNER JOIN tablaMaestraDet AS tm  ON tm.codtabladet = p.CodEstado
LEFT JOIN grupocab AS gpo         ON gpo.codgrupocab = pla.codgrupocab
LEFT JOIN tablaMaestraDet AS tm2  ON tm2.codtabladet = s.codestadocivil
LEFT JOIN tablaMaestraDet AS tm3  ON tm3.codtabladet = p.CodSituacion
--INNER JOIN tablaMaestraDet as tm3 on tm3.codtabladet = s.codcategoria
INNER JOIN pais                   ON pais.codpais = s.codpais
LEFT JOIN FINALIDAD AS FI         ON FI.CODFINALIDAD = P.CODFINALIDAD
LEFT JOIN TipoCredito AS TC       ON tc.CodTipoCredito = p.CodTipoCredito
INNER JOIN usuario AS u           ON p.CodUsuario = u.CodUsuario
INNER JOIN TablaMaestraDet AS tm4 ON s.codestado = tm4.CodTablaDet
--LEFT JOIN PrestamoCuota as pcu on p.CodPrestamo = pcu.CodPrestamo

LEFT JOIN SolicitudCredito AS SOLICITUD ON P.CodSolicitudCredito = SOLICITUD.CodSolicitudCredito
LEFT JOIN Usuario AS USUARIO            ON SOLICITUD.CodUsuarioSegAprob = USUARIO.CodUsuario

-----------------------------------------------------
	LEFT JOIN TipoCambioSBS AS TCSBS
	on (year(p.fechadesembolso) = tcsbs.Anno) and (month(p.fechadesembolso) = tcsbs.MES)

-----------------------------------------------------
--LEFT JOIN SolicitudCreditoOtrosDescuentos AS DESCUENTO ON P.CodSolicitudCredito = DESCUENTO.CodSolicitudCredito

WHERE CONVERT(VARCHAR(10),p.fechadesembolso,112) BETWEEN '{fecha_inicio}' AND '{fecha_final}'
--AND DESCUENTO.retencion = 'TOTAL RETENCIÓN'

AND s.codigosocio     > 0
AND p.montosolicitado > 0
AND p.codestado <> 563 -- que no sea crédito anulado
--and p.codestado = 342

-- AND (p.CODTIPOCREDITO=2 or p.CODTIPOCREDITO=9) and pcu.NumeroCuota=1 and tm2.descripcion is null -- 341 PENDIENTES  /  p.codestado <> 563  anulados
-- WHERE year(p.fechadesembolso) >= 2021 and month(p.fechadesembolso) >= 1 and s.codigosocio>0 and p.codestado <> 563 AND tc.CODTIPOCREDITO <>3 
-- AND pro.Descripcion like '%WILLIAMS TRAUCO%' 
-- AND p.codcategoria=351
ORDER BY socio ASC, p.fechadesembolso DESC

'''

df_desembolsos = pd.read_sql_query(query, conn)
del conn

#%%

df_desembolsos.to_excel(f'Desembolsos 2024 - {fecha_final}.xlsx',
                        index = False)
