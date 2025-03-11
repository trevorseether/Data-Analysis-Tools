# -*- coding: utf-8 -*-
"""
Created on Wed Mar  5 10:56:51 2025

@author: sanmiguel38
"""

# =============================================================================
#                                 BD - 04
# =============================================================================

import pandas as pd
import os
import pyodbc
from datetime import datetime

import warnings
warnings.filterwarnings('ignore')

#%%
fecha_corte = '20241231'

#%%
datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')

server      = datos['DATOS'][0]
username    = datos['DATOS'][2]
password    = datos['DATOS'][3]

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
	s.codigosocio                                                                                           AS 'CIS_C',
	iif(s.CodTipoPersona =1, CONCAT(S.ApellidoPaterno,' ',S.ApellidoMaterno, ' ', S.Nombres),s.razonsocial) AS 'NSO_C',
	CASE
		WHEN S.CodTipoDocIdentidad = 5    THEN '1'
		WHEN S.CodTipoDocIdentidad = 100  THEN '6'
		WHEN S.CodTipoDocIdentidad = 6    THEN '2'
		ELSE 'CASO NO ASIGNADO'
		END                                                                                                 AS 'TID_C',
	iif(s.CodTipoPersona =1, s.nroDocIdentidad, s.nroruc)                                                   AS 'NID_C',
	RIGHT(CONCAT('0000000',p.numero),8)                                                                     AS 'CCR_C',
	''                                                                                                      AS 'TCR_C',
	iif(p.codmoneda=94,'1','2')                                                                             AS 'MON_C', 
	p.montosolicitado                                                                                       AS 'MORG_C', 
	p.NroPlazos                                                                                             AS 'NCPR_C', 
	FORMAT(p.fechadesembolso, 'dd/MM/yyyy')                                                                 AS 'FOT_C',
	FORMAT(p.fechaCancelacion, 'dd/MM/yyyy')                                                                AS 'FCAN_C',
	''                                                                                                      AS 'NCPA_C',
	''                                                                                                      AS 'MCK_C',
	''                                                                                                      AS 'MCI_C',
	''                                                                                                      AS 'SIM_C',
	''                                                                                                      AS 'MCT_C',
	''                                                                                                      AS 'CAL_C', -- ANEXO 06
	''                                                                                                      AS 'DAK_C', -- ANEXO 06
	''                                                                                                      AS 'NCAD_C', -- COBRANZA?
	''                                                                                                      AS 'TPR_C',
	IIF(S.CodSexo = 4, 'FEMENINO',
		IIF(S.CodSexo = 3, 'MASCULINO','EMPRESA')) AS 'SEXO',
		--------------------------------------------------------------
	CASE 
		WHEN p.CodPrestamoFox IS NOT NULL THEN
		RIGHT(CONCAT('000000',p.CodPrestamoFox),6)
	ELSE RIGHT(CONCAT('0000000',p.numero),8)
		END as 'pagare_fox', 
	-------------------------------------------------------------------
	------------------------------------------------------------------<
	iif(p.CodMoneda='95', tcsbs.tcsbs, 1) as 'TC_SBS',
	p.montosolicitado * iif(p.CodMoneda='95', tcsbs.tcsbs, 1) AS 'Monto Otorgado en soles',
	--------------------------------------------------------------<
	p.TEM, 
	p.CuotaFija,  
	--p.codestado, 
	tm.descripcion as 'Estado',
	iif(p.codcategoria=351,'NVO','AMPL') as 'tipo_pre', 
--------------------------------------<<<<<<<<<<<<<<<<<<<<	
	p.flagrefinanciado,
	CASE
		WHEN (P.CodEstado<>563) and (flagRefinanciado=1 or (p.CodSolicitudCredito =0)) THEN 'REFINANCIADO'
		ELSE 'normal'
		END AS 'REFINANCIAMIENTO',
--------------------------------------<<<<<<<<<<<<<<<<<<<<	
	pro.CodGrupoCab,
	pro.descripcion as 'Funcionario',
	pla.descripcion as 'Planilla', 
	gpo.descripcion as 'func_pla',
	CONCAT(sc.nombrevia,' Nro ', sc.numerovia,' ', sc.nombrezona) as 'direcc_socio',
	sc.ReferenciaDomicilio,
	d.nombre   AS 'distrito', 
	pv.nombre  AS 'provincia', 
	dp.nombre  AS 'departamento',
	sc.ReferenciaDomicilio,
	iif(s.codigosocio>28790,'SOC.NVO', 'SOC.ANT') AS 'tipo_soc',
	tm2.descripcion  AS 'est_civil', 
	pais.descripcion AS 'pais', 
	s.fechanacimiento, 
	s.profesion, 
	sc.celular1, 
	SC.TelefonoFijo1, 
	sc.Email, 
	p.CodSituacion, 
	tm3.Descripcion as 'Situacion', 
	p.fechaventacartera,
	P.FechaCastigo, 
	iif(p.flagponderosa=1,'POND','SM') as 'origen', 
	tc.CODTIPOCREDITO AS 'ClaseTipoCredito', 
	tc.Descripcion as 'TipoCredito', 
	FI.CODIGO AS 'COD_FINALIDAD', 
	FI.DESCRIPCION AS 'FINALIDAD', 
	s.FechaNacimiento, 
	s.fechaInscripcion, 
	u.IdUsuario as 'User_Desemb', 
	tm4.descripcion as 'EstadoSocio',
	USUARIO.IdUsuario AS 'USUARIO APROBADOR',
	ENFI.Descripcion AS 'banco del socio',
	--CASE
	--	WHEN (CJC.BancoADepositar IS NULL) AND CJC.Documento LIKE '%N° ORDEN PAGO : ' THEN 'SCOTIABANK PERÚ'
	--	ELSE CJC.BancoADepositar
	--	END AS 'BANCO DEPÓSITO',

		AE.CIIU

	--,
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

LEFT JOIN SocioTransferencia AS SOT  ON SOLICITUD.CodSocioTransferencia = SOT.CodSocioTransferencia
LEFT JOIN EntidadFinanciera AS ENFI  ON SOT.CodEntidadFinanciera = ENFI.CodEntidadFinanciera

--LEFT JOIN CajaCab AS CJC ON CJC.CodPrestamo = P.CodPrestamo

LEFT JOIN ActividadEconomica AS AE ON S.CodActividadEconomica = AE.CodActividad
-----------------------------------------------------
	LEFT JOIN TipoCambioSBS AS TCSBS
	on (year(p.fechadesembolso) = tcsbs.Anno) and (month(p.fechadesembolso) = tcsbs.MES)

-----------------------------------------------------
--LEFT JOIN SolicitudCreditoOtrosDescuentos AS DESCUENTO ON P.CodSolicitudCredito = DESCUENTO.CodSolicitudCredito

WHERE EOMONTH(p.fechaCancelacion) = '20241231'

--AND DESCUENTO.retencion = 'TOTAL RETENCIÓN'

AND s.codigosocio       >  0
AND p.montosolicitado   >  0
AND p.codestado <> 563 -- que no sea crédito anulado
--and p.codestado = 342
--AND FI.CODIGO IN (34,35,36,37,38,39)
--and p.flagponderosa <> 1

-- AND (p.CODTIPOCREDITO=2 or p.CODTIPOCREDITO=9) and pcu.NumeroCuota=1 and tm2.descripcion is null -- 341 PENDIENTES  /  p.codestado <> 563  anulados
-- WHERE year(p.fechadesembolso) >= 2021 and month(p.fechadesembolso) >= 1 and s.codigosocio>0 and p.codestado <> 563 AND tc.CODTIPOCREDITO <>3 
-- AND pro.Descripcion like '%WILLIAMS TRAUCO%' 
-- AND p.codcategoria=351
ORDER BY p.fechadesembolso DESC

/*

SELECT a.CodUsuarioPriAprob, a.CodUsuarioSegAprob, b.IdUsuario FROM SolicitudCredito as a
	LEFT JOIN Usuario as b
	on a.CodUsuarioSegAprob = b.CodUsuario

select CodSolicitudCredito,* from prestamo

*/            

            '''

df_desembolsos = pd.read_sql_query(query, conn)
conn.close()

df_desembolsos = df_desembolsos.drop_duplicates(subset = ['pagare_fincore'], keep = 'first')

del query



