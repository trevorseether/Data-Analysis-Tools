-- p.codcategoria = 351 -> nuevo
-- p.codcategoria = 352 -> ampliacion
-- p.codestado = 563 -> anulado
-- p.codestado = 341 -> pendiente
-- p.codestado = 342 -> cancelado
-- tc.CODTIPOCREDITO -> ( 3=Cons.Ordinario / 1=Med.Empresa / 2=MicroEmp. / 9=Peq.Empresa)

SELECT
	s.codigosocio, 
	iif(s.CodTipoPersona =1, CONCAT(S.ApellidoPaterno,' ',S.ApellidoMaterno, ' ', S.Nombres),s.razonsocial) AS 'Socio',
--------------------------------------------------------------------------------------------------------------------
	iif(s.CodTipoPersona =1, s.nroDocIdentidad, s.nroruc) AS 'Doc_Identidad',
	CASE
		WHEN S.CodTipoDocIdentidad = 5    THEN 'DNI'
		WHEN S.CodTipoDocIdentidad = 100  THEN 'RUC'
		WHEN S.CodTipoDocIdentidad = 6    THEN 'C.E.'
		ELSE 'OTROS'
		END AS 'TIPO DOCUMENTO TXT',

	CASE
		WHEN S.CodTipoDocIdentidad = 5    THEN '1'
		WHEN S.CodTipoDocIdentidad = 100  THEN '6'
		WHEN S.CodTipoDocIdentidad = 6    THEN '2'
		ELSE 'OTROS'
		END AS 'TIPO DOCUMENTO SBS',
--------------------------------------------------------------------------------------------------------------------
	IIF(S.CodSexo = 4, 'FEMENINO',
		IIF(S.CodSexo = 3, 'MASCULINO','EMPRESA')) AS 'SEXO',
		--------------------------------------------------------------
	RIGHT(CONCAT('0000000',p.numero),8) as 'pagare_fincore',
	CASE 
		WHEN p.CodPrestamoFox IS NOT NULL THEN
		RIGHT(CONCAT('000000',p.CodPrestamoFox),6)
	ELSE RIGHT(CONCAT('0000000',p.numero),8)
		END as 'pagare_fox', 
		--------------------------------------------------------------
	iif(p.codmoneda=94,'S/','US$') as 'moneda', 
	p.fechadesembolso, 
	--------------------------------------------------------------<
	p.montosolicitado as 'Otorgado', 
	iif(p.CodMoneda='95', tcsbs.tcsbs, 1) as 'TC_SBS',
	p.montosolicitado * iif(p.CodMoneda='95', tcsbs.tcsbs, 1) AS 'Monto Otorgado en soles',
	--------------------------------------------------------------<
	p.TEM, 
	p.NroPlazos, 
	p.CuotaFija,  
	--p.codestado, 
	tm.descripcion as 'Estado',
	p.fechaCancelacion, 
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
	CASE
		WHEN pro.descripcion LIKE '%PROSEVA%' THEN pro.descripcion
		WHEN 
		(PRO.DESCRIPCION LIKE '%ADOLFO%HUAMAN%'
		OR PRO.DESCRIPCION LIKE '%CESAR%MEDINA%'
		OR PRO.DESCRIPCION LIKE '%DAYANA%CHIRA%'
		OR PRO.DESCRIPCION LIKE '%ESTHER%RAMIR%'
		OR PRO.DESCRIPCION LIKE '%JESSICA%SOLOR%'
		OR PRO.DESCRIPCION LIKE '%JESICA%SOLOR%'
		OR PRO.DESCRIPCION LIKE '%JORGE%ARAG%'
		OR PRO.DESCRIPCION LIKE '%MARIBEL%PUCH%') THEN 'AREQUIPA'
		WHEN
		(PRO.DESCRIPCION LIKE '%ALEJANDRO%HUAMAN%'
		OR PRO.DESCRIPCION LIKE '%ANA%GUERR%'
		OR PRO.DESCRIPCION LIKE '%ANT%OSORIO%'
		OR PRO.DESCRIPCION LIKE '%EDUAR%TITO%'
		OR PRO.DESCRIPCION LIKE '%ELBER%ALVA%'
		OR PRO.DESCRIPCION LIKE '%FIGARI%VEG%'
		OR PRO.DESCRIPCION LIKE '%GINO%PALO%'
		OR PRO.DESCRIPCION LIKE '%GRICERIO%NU%'
		OR PRO.DESCRIPCION LIKE '%JEAN%BRAV%'
		OR PRO.DESCRIPCION LIKE '%JIMN%MENDO%'
		OR PRO.DESCRIPCION LIKE '%KELLY%HUAM%'
		OR PRO.DESCRIPCION LIKE '%MAR%MARTINE%'
		OR PRO.DESCRIPCION LIKE '%MARTIN%VILCA%'
		OR PRO.DESCRIPCION LIKE '%PAMELA%GARC%'
		OR PRO.DESCRIPCION LIKE '%SUSAN%ROJAS%'
		OR PRO.DESCRIPCION LIKE '%VICTOR%FARFA%'
		OR PRO.DESCRIPCION LIKE '%YESENIA%POTENC%'
		--OR PRO.DESCRIPCION LIKE '%YULAISE%MOREANO%'
		OR PRO.DESCRIPCION LIKE '%GERENCIA%'
		OR PRO.DESCRIPCION LIKE '%LUIS%BUSTAMAN%'
		OR PRO.DESCRIPCION LIKE '%JONAT%ESTRADA%'
		OR PRO.DESCRIPCION LIKE '%GRUPO%'
		OR PRO.DESCRIPCION LIKE '%DAVID%BORJ%'
		OR PRO.DESCRIPCION LIKE '%VICTOR%VARGA%'
		OR PRO.DESCRIPCION LIKE '%BORIS%CAMARGO%'
		) THEN 'LIMA'
				WHEN
		(PRO.DESCRIPCION LIKE '%YULAISE%MOREANO%'
		OR PRO.DESCRIPCION LIKE '%JESUS%CERVERA%'
		OR PRO.DESCRIPCION LIKE '%EDISON%FLORES%'
		) THEN 'SANTA ANITA'
		WHEN 
		(PRO.DESCRIPCION LIKE '%JESSICA%PISCOYA%'
		OR PRO.DESCRIPCION LIKE '%JOSE%SANCHE%'
		OR PRO.DESCRIPCION LIKE '%MILTON%JUARE%'
		OR PRO.DESCRIPCION LIKE '%PAULO%SARE%'
		OR PRO.DESCRIPCION LIKE '%ROY%NARVAE%'
		) THEN 'TRUJILLO'
				WHEN 
		(PRO.DESCRIPCION LIKE '%CESAR%MERA%'
		OR PRO.DESCRIPCION LIKE '%WILLIAMS%TRAUCO%'
		) THEN 'TARAPOTO'
				WHEN 
		(PRO.DESCRIPCION LIKE '%JHONY%SALDA%'
		) THEN 'RESTO DE CARTERA PROVINCIA'
	ELSE 'REVISAR CASO'
		END AS 'ZONAS',
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
	USUARIO.IdUsuario AS 'USUARIO APROBADOR'
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

-----------------------------------------------------
	LEFT JOIN TipoCambioSBS AS TCSBS
	on (year(p.fechadesembolso) = tcsbs.Anno) and (month(p.fechadesembolso) = tcsbs.MES)

-----------------------------------------------------
--LEFT JOIN SolicitudCreditoOtrosDescuentos AS DESCUENTO ON P.CodSolicitudCredito = DESCUENTO.CodSolicitudCredito

WHERE CONVERT(VARCHAR(10),p.fechadesembolso,112) >= '20220101'
--AND DESCUENTO.retencion = 'TOTAL RETENCIÓN'

AND s.codigosocio     > 0
AND p.montosolicitado > 0
AND p.codestado <> 563 -- que no sea crédito anulado
--and p.codestado = 342
AND FI.CODIGO IN (34,35,36,37,38,39)
and p.flagponderosa <> 1

-- AND (p.CODTIPOCREDITO=2 or p.CODTIPOCREDITO=9) and pcu.NumeroCuota=1 and tm2.descripcion is null -- 341 PENDIENTES  /  p.codestado <> 563  anulados
-- WHERE year(p.fechadesembolso) >= 2021 and month(p.fechadesembolso) >= 1 and s.codigosocio>0 and p.codestado <> 563 AND tc.CODTIPOCREDITO <>3 
-- AND pro.Descripcion like '%WILLIAMS TRAUCO%' 
-- AND p.codcategoria=351
ORDER BY socio ASC, p.fechadesembolso DESC

/*

SELECT a.CodUsuarioPriAprob, a.CodUsuarioSegAprob, b.IdUsuario FROM SolicitudCredito as a
	LEFT JOIN Usuario as b
	on a.CodUsuarioSegAprob = b.CodUsuario

select CodSolicitudCredito,* from prestamo

*/
