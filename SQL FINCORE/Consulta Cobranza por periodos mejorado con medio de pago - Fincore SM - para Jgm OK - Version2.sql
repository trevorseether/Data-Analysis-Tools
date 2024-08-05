SELECT 
	soc.codsocio, 
	soc.codigosocio, 
	iif(soc.CodTipoPersona =1,concat(soc.apellidopaterno,' ',soc.apellidomaterno,' ',soc.nombres),soc.razonsocial) AS 'Socio',
		soc.apellidopaterno,
		soc.apellidomaterno,
		soc.nombres,
		soc.razonsocial,
	iif(soc.CodTipoPersona =1,soc.nrodocIdentidad,soc.nroRuc) AS 'doc_ident', 
--------------------------------------------------------------------
	right(concat('0000000',pre.numero),8)  AS 'PagareFincore',
	CASE 
		WHEN pre.CodPrestamoFox IS NOT NULL THEN
		RIGHT(CONCAT('000000',pre.CodPrestamoFox),6)
	ELSE RIGHT(CONCAT('0000000',pre.numero),8)
		END as 'pagare_fox', 
--------------------------------------------------------------------
	pre.FechaDesembolso,
	precuo.numerocuota, 
	iif(cdet.CodMoneda='95','DÓLAR','SOLES') AS 'moneda',
	
	--year(ccab.fecha) AS 'AÑO TC',month(ccab.fecha) AS 'MES TC',

	iif(cdet.CodMoneda='95', tcsbs.tcsbs, 1) as 'TC_SBS',

	ccab.fecha as 'fecha_cob', 
	cdet.Capital, 
	cdet.aporte as 'Aporte',
	cdet.interes AS 'INT_CUOTA', 
	cdet.InteresCompensatorio as 'IntCompVencido', 
	cdet.Mora AS 'INTCOMP_MORA', 
	cdet.GastoCobranza, 
	cdet.FondoContigencia+cdet.MoraAnterior+cdet.GastoTeleOperador+cdet.GastoJudicial+cdet.GastoLegal+cdet.GastoOtros AS 'GTO_OTROS',
	cdoc.numeroOperacion,
	cdoc.numeroOperacionDestino, --tmdet.descripcion as TipoDocmto, 
	gr.descripcion as 'Funcionario', 
	pla.descripcion as 'planilla', 
	tc.Descripcion as 'TipoCredito', 
	fin.codigo AS 'codigo', 
	fin.Descripcion as 'finalidad',  
	pre.FechaVentaCartera, 
	pre.FechaCastigo, 
	cdoc.codestado, 
	cDOC.NumeroOperacionDestino, 
	CCAB.CODMEDIOPAGO, 
	tmdet.descripcion as 'tipoPago', -- CDOC.CODCOBRANZADOCUMENTO,
	tmdet5.Descripcion as 'SituacCred', 
	pre.FechaAsignacionAbogado, 
	empl.NombreCompleto as 'Abogado', 

--IIF(CDDNC.NumeroOperacionDestino IS NULL,cdoc.NumeroOperacionDestino,CDDNC.NumeroOperacionDestino) AS NumeroOperacionDestino,
IIF(CDDNC.NumeroOperacionDestino IS NULL,CU.NumeroCuenta,CUNC.NumeroCuenta) AS 'NumeroCuenta',
--IIF(CDDNC.NumeroOperacionDestino IS NULL,NULL,CONCAT('NC-',RIGHT(CONCAT('000000',NC.Correlativo),6))) AS NroNotaCredito,
iif(cdet.FlagPonderosa=1,'POND','SM') as 'origen'


FROM   CobranzaDet AS cdet INNER JOIN prestamoCuota AS precuo ON precuo.CodprestamoCuota = cdet.CodprestamoCuota
                           INNER JOIN CobranzaCab as ccab ON ccab.CodCobranzaCab = cdet.CodCobranzaCab
                           Inner Join Prestamo as pre ON pre.codPrestamo = precuo.CodPrestamo 
                           Left Join Planilla AS pla ON pre.CodPlanilla = pla.CodPlanilla
                           Inner Join Socio as soc ON soc.CodSocio = pre.CodSocio
                           inner join finalidad as fin on fin.CodFinalidad = pre.CodFinalidad
                           inner join TipoCredito as tc on tc.CodTipoCredito = fin.CodTipoCredito
                           left join grupoCab as gr on gr.codGrupoCab = pre.codGrupoCab
						   --   LEFT JOIN CobranzaDocumento as cdoc on ccab.CodCobranzaDocumento = cdoc.CodCobranzaDocumento
						   --   Inner Join TablaMaestraDet as tmdet on tmdet.CodTablaDet = cdoc.CodMedioPago (ORIGUINAL)
                           LEft Join TablaMaestraDet as tmdet on tmdet.CodTablaDet = ccab.CodMedioPago --(NUEVO ACTIVAR)

                           left join Empleado as empl on pre.CodAbogado = empl.CodEmpleado
                           left join TablaMaestraDet as tmdet5 on pre.CodSituacion = tmdet5.CodTablaDet

                            -------
                            left join CobranzaDocumento  AS cdoc   ON ccab.CodCobranzaDocumento = cdoc.CodCobranzaDocumento
                            left join Cuenta             AS CU     ON CU.CodCuenta              = cdoc.CodCuentaDestino
                            left join NotaCredito        AS NC     ON ccab.CodNotaCredito       = NC.CodNotaCredito
                            left join CobranzaDocumento  AS CDDNC  ON NC.CodCobranzaDocumento   = CDDNC.CodCobranzaDocumento
                            left join Cuenta             AS CUNC   ON CDDNC.CodCuentaDestino    = CUNC.CodCuenta

                            --------
  
				left join TipoCambioSBS as tcsbs
				on (year(ccab.fecha) = tcsbs.Anno) and (month(ccab.fecha) = tcsbs.MES)

-- WHERE        (ccab.Fecha >= '01-01-2020' and ccab.Fecha <= '31-12-2020') and cdet.flagponderosa is null
-- where year(ccab.fecha)=2021 and cdet.CodEstado <> 376 -- and fin.codigo<30 and gr.descripcion like '%PROSEVA%'  -- 376 Anulado and cdet.flagponderosa is null

WHERE CONVERT(VARCHAR(10),ccab.fecha,112) BETWEEN '20240101' AND '20240630' and cdet.CodEstado <> 376  

--and right(concat('0000000',pre.numero),8)  = 00129322


ORDER BY socio, ccab.fecha




