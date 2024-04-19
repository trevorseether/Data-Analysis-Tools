# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 18:58:42 2023

@author: Joseph Montoya
"""

import pyodbc
import pandas as pd
import os

os.chdir('C:\\Users\\sanmiguel38\\Desktop\\mype no morosos')
#%%
datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')

server      = datos['DATOS'][0]
username    = datos['DATOS'][2]
password    = datos['DATOS'][3]

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'
conn = pyodbc.connect(conn_str)

query = '''SELECT
/*
	s.codigosocio, 
	iif(s.CodTipoPersona =1, CONCAT(S.ApellidoPaterno,' ',S.ApellidoMaterno, ' ', S.Nombres),s.razonsocial) AS 'Socio',
	iif(s.CodTipoPersona =1, s.nroDocIdentidad, s.nroruc) AS 'Doc_Identidad',
	IIF(S.CodSexo = 4, 'FEMENINO',
		IIF(S.CodSexo = 3, 'MASCULINO','EMPRESA')) AS 'SEXO',
		*/
        
	iif(s.CodTipoPersona =1, s.nroDocIdentidad, s.nroruc) AS 'Doc_Identidad',
	RIGHT(CONCAT('0000000',p.numero),8) as 'pagare_fincore',
	s.fechaInscripcion,
	p.fechadesembolso,
	pais.descripcion as 'pais', 
	sc.celular1, 
	SC.TelefonoFijo1, 
	sc.Email
	-- ,
	-- DESCUENTO.valor as 'retención',
	-- p.montosolicitado - DESCUENTO.valor as 'MONTO NETO'

-- pcu.FechaVencimiento as Fecha1raCuota, pcu.NumeroCuota, pcu.SaldoInicial,
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

--LEFT JOIN SolicitudCreditoOtrosDescuentos AS DESCUENTO ON P.CodSolicitudCredito = DESCUENTO.CodSolicitudCredito

--LEFT JOIN PAIS AS PAIS ON S.CodPais = PAIS.CODPAIS

WHERE CONVERT(VARCHAR(10),p.fechadesembolso,112) >= '20010101'

--AND DESCUENTO.retencion = 'TOTAL RETENCIÓN'

--AND s.codigosocio>0

--and p.codestado = 342
--AND FI.CODIGO IN (15,16,17,18,19,20,21,22,23,24,25,29)

-- AND (p.CODTIPOCREDITO=2 or p.CODTIPOCREDITO=9) and pcu.NumeroCuota=1 and tm2.descripcion is null -- 341 PENDIENTES  /  p.codestado <> 563  anulados
-- WHERE year(p.fechadesembolso) >= 2021 and month(p.fechadesembolso) >= 1 and s.codigosocio>0 and p.codestado <> 563 AND tc.CODTIPOCREDITO <>3 
-- AND pro.Descripcion like '%WILLIAMS TRAUCO%' 
-- AND p.codcategoria=351
ORDER BY iif(s.CodTipoPersona =1, s.nroDocIdentidad, s.nroruc) ASC, p.fechadesembolso DESC

'''

df_fincore = pd.read_sql_query(query, conn)

del conn

#%%
df_fincore.to_excel('datos total.xlsx',
                    index = False)

pivot_fincore = df_fincore.pivot_table(values = 'pagare_fincore',
                                       index = 'Doc_Identidad',
                                       aggfunc= 'count')


pivot_fincore.to_excel('nro creditos.xlsx')

