select 	
	iif(s.CodTipoPersona =1, CONCAT(S.ApellidoPaterno,' ',S.ApellidoMaterno, ' ', S.Nombres),s.razonsocial) AS 'Socio',
	descuento.retencion,
	DESCUENTO.valor as 'retención',
	p.montosolicitado as 'Otorgado', 
	RIGHT(CONCAT('0000000',p.numero),8) as 'pagare_fincore', 
	FechaDesembolso,
	p.CodSolicitudCredito,
	p.flagrefinanciado, 
	P.CodSolicitudCredito,
	CASE
		WHEN p.flagrefinanciado = 1 or P.CodSolicitudCredito = 0 THEN 'REFINANCIADO'
		ELSE 'NO REFINANCIADO'
		END AS 'ETIQUETA REFINANCIADO',
	* 
from prestamo as p

INNER JOIN socio AS s ON s.codsocio = p.codsocio
LEFT JOIN SolicitudCreditoOtrosDescuentos AS DESCUENTO ON P.CodSolicitudCredito = DESCUENTO.CodSolicitudCredito
--where iif(s.CodTipoPersona =1, CONCAT(S.ApellidoPaterno,' ',S.ApellidoMaterno, ' ', S.Nombres),s.razonsocial) like '%HERRERA%GUERRERO%GIANINA%FABIOLA%'
-- AND RIGHT(CONCAT('0000000',p.numero),8) = 00117304 00102704
WHERE RIGHT(CONCAT('0000000',p.numero),8) = 00123579
