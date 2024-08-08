SELECT 	
	iif(A.CodTipoPersona =1, A.nroDocIdentidad, A.nroruc) AS 'Doc_Identidad',
	A.ApellidoPaterno,
	A.ApellidoMaterno,
	A.Nombres,
	A.razonsocial,
--B.FechaObservacion,
A.FechaInscripcion,
A.FechaNacimiento,
	CASE
		WHEN B.CodValorNuevo = 301 THEN 'INHABIL'
        WHEN B.CodValorNuevo = 532 THEN 'FALLECIDO'
	ELSE ''
	END AS 'OBSERVACIÓN',

	CASE
		WHEN B.CodValorNuevo IN (301,532) THEN B.FechaObservacion
	ELSE ''
	END AS	'fecha_egreso'
FROM 
	Socio AS A
LEFT JOIN 
	SocioObservacion AS B ON A.CODSOCIO = B.CODSOCIO
--WHERE
--	B.CodValorNuevo IN (301,532)

	---and iif(A.CodTipoPersona =1, A.nroDocIdentidad, A.nroruc) = '21861040'
--AND 
--	B.FechaObservacion BETWEEN '20230101' AND '20231231'

---------------------------------------------------------
SELECT TOP 100 * FROM SocioObservacion
WHERE CodValorNuevo IN (301,532)
---------------------------------------------------------
SELECT * FROM TablaMaestraDet
WHERE CodTablaCAB = 41
---------------------------------------------------------
