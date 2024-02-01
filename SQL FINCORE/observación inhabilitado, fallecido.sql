SELECT 	
iif(A.CodTipoPersona =1, A.nroDocIdentidad, A.nroruc) AS 'Doc_Identidad',
B.FechaObservacion,
*
FROM 
	Socio AS A
LEFT JOIN 
	SocioObservacion AS B ON A.CODSOCIO = B.CODSOCIO
WHERE 
	B.CodValorNuevo IN (301,532)
AND 
	B.FechaObservacion BETWEEN '20230101' AND '20231231'

SELECT TOP 100 * FROM SocioObservacion
WHERE CodValorNuevo IN (301,532)

SELECT * FROM TablaMaestraDet
WHERE CodTablaCAB = 41
