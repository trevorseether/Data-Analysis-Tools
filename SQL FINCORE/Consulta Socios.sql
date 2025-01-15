-- CONSULTA A NIVEL DE SOCIO, O CÓDIGO DE SOCIO

SELECT
	s.codigosocio, 
	iif(s.CodTipoPersona =1, CONCAT(S.ApellidoPaterno,' ',S.ApellidoMaterno, ' ', S.Nombres),s.razonsocial) AS 'Socio',
	
	iif(s.CodTipoPersona =1, s.nroDocIdentidad, s.nroruc) AS 'Doc_Identidad',
	CASE
		WHEN S.CodTipoDocIdentidad = 5 THEN 'DNI'
		WHEN S.CodTipoDocIdentidad = 100 THEN 'RUC'
		WHEN S.CodTipoDocIdentidad = 6 THEN 'C.E.'
		ELSE 'OTROS'
		END AS 'TIPO DOCUMENTO',
	iif(s.codigosocio>28790,'SOC.NVO', 'SOC.ANT') AS 'tipo_soc',
	pais.descripcion as 'pais', 
	s.FechaNacimiento, 
	s.profesion, 
	sc.celular1, 
	SC.TelefonoFijo1, 
	sc.Email, 
	tm2.descripcion as 'est_civil', 
	CONCAT(sc.nombrevia,' Nro ', sc.numerovia,' ', sc.nombrezona) as 'direcc_socio', 
	d.nombre as 'distrito', 
	pv.nombre as 'provincia', 
	dp.nombre as 'departamento', 
	s.FechaNacimiento, 
	s.fechaInscripcion

FROM SOCIO as S
	LEFT JOIN sociocontacto as sc     ON sc.codsocio = s.codsocio
	LEFT JOIN tablaMaestraDet as tm2  ON tm2.codtabladet = s.codestadocivil
	INNER JOIN pais                   ON pais.codpais = s.codpais
	INNER JOIN distrito as d          ON d.coddistrito = sc.coddistrito
	INNER JOIN provincia as pv        ON pv.codprovincia = d.codprovincia
	INNER JOIN departamento as dp     ON dp.coddepartamento = pv.coddepartamento


WHERE
	s.codigosocio in ('00031522','00032475')

	----

	select * from SOCIO


