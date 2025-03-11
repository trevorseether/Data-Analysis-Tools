update PrestamoCuota set FechaAnulacionCrono =null where CodEstado =346 and CuotaFija=0 and FechaAnulacionCrono is not null
update PrestamoCuota set FechaAnulacionCrono =null where CodEstado =22 and FechaAnulacionCrono is not null

 IF OBJECT_ID('tempdb.dbo.#TMP_SOCIOBLOQUEAR', 'U') IS NOT NULL
DROP TABLE #TMP_SOCIOBLOQUEAR;  
	SELECT CODSOCIO INTO #TMP_SOCIOBLOQUEAR FROM Socio   WHERE CodSocio IN (
	105,637,1409,1598,1650,1654,1685,1996,2135,2144,2534,4856,6621,10491,21815,34561,
	17206,1650,1654,293,470,508,509,578,582,622,623,625,
627,631,632,634,642,643,644,646,667,668,669,671,674,675,
676,679,680,699,704,4724,6642,7211,374,388,391,392,393,
394,396,397,398,399,400,405,412,413,414,415,416,417,
420,421,422,424,425,450,451,453)

--21	9	PENDIENTE
--22	9	CANCELADO
--23	9	AMORTIZADO
--24	9	ANULADO
--379	9	REPROGRAMADO
--1003	9	AMORTIZACION CAPITAL

DECLARE     @FechaPago                INT ='20250228'-- ULTIMO DIA DEL MES DE PROCESAMIENTO

DECLARE     @FechaConvert                SMALLDATETIME
SET         @FechaConvert                =    CONVERT(VARCHAR(8),@FechaPago,112)

 IF OBJECT_ID('tempdb.dbo.#tablaAmortizacion379', 'U') IS NOT NULL
DROP TABLE #tablaAmortizacion379;

select *   into #tablaAmortizacion379  from
(
select CodPrestamoCuota,'01/01/2024' as FechaCreacion  from PrestamoCuota where CodEstado =379 and FlagAxonCuotaReprogramada =1
union
 select PK as CodPrestamocuota,FechaActualizada as FechaCreacion
 from Auditoria WHERE NombreTabla ='Prestamocuota' and NuevoValor ='379' and NombreCampo ='CodEstado'  and YEAR(FechaActualizada)=2025 ) Tempo order by FechaCreacion 
 
-- select * from #tablaAmortizacion379

IF OBJECT_ID('tempdb.dbo.#TMP_COBRANZA', 'U') IS NOT NULL
DROP TABLE #TMP_COBRANZA;
    SELECT
        CD.CodPrestamoCuota,
        SUM(CD.Capital)                            AS Capital,
        SUM(CD.Interes)                            AS Interes,
        SUM(CD.Aporte)                            AS Aporte,
        SUM(CD.FondoContigencia)                AS Fondo
    INTO #TMP_COBRANZA
    FROM CobranzaDet CD
    INNER JOIN PrestamoCuota    PC    ON PC.CodPrestamoCuota    =CD.CodPrestamoCuota
    INNER JOIN CobranzaCab        CB    ON CD.CodCobranzaCab    =CB.CodCobranzaCab
    WHERE
        CONVERT(DATE,CB.Fecha)<=@FechaConvert AND    -- HASTA FECHA DE CORTE
        PC.CodEstado IN (21,22,23,379,1003)            -- ESTADO CUOTA DIF. ANULADO <>24
        AND CD.CodEstado = 377
        GROUP BY CD.CodPrestamoCuota



IF OBJECT_ID('tempdb.dbo.#TMP_PTMOG', 'U') IS NOT NULL
DROP TABLE #TMP_PTMOG;
   
   SELECT * INTO #TMP_PTMOG FROM 
   (
   SELECT
        PC.CodPrestamo,
        PC.CodPrestamoCuota,
        IIF((PC.Capital - IsNull(PC.DescuentoCapital,0))-IsNull(TC.Capital,0)<0,0,
        (PC.Capital - IsNull(PC.DescuentoCapital,0))- IsNull(TC.Capital,0))
        AS SaldoCapitalSoles,
		IIF((PC.Interes - IsNull(PC.DescuentoInteres,0))-IsNull(TC.Interes,0)<0,0,
        (PC.Interes - IsNull(PC.DescuentoInteres,0))- IsNull(TC.Interes,0))
        AS SaldoInteresSoles,
		IIF((PC.Aporte - IsNull(PC.DescuentoAporte,0))-IsNull(TC.Aporte,0)<0,0,
        (PC.Aporte - IsNull(PC.DescuentoAporte,0))- IsNull(TC.Aporte,0))
        AS SaldoAporteSoles,

		IIF(IsNull(PC.DescuentoCapital,0)+IsNull(TC.Capital,0)>PC.Capital,PC.Capital,IsNull(PC.DescuentoCapital,0)+IsNull(TC.Capital,0)) AS PAGOTCAPITAL,
		IIF(IsNull(PC.DescuentoInteres,0)+IsNull(TC.Interes,0)>PC.Interes,PC.Interes,IsNull(PC.DescuentoInteres,0)+IsNull(TC.Interes,0)) AS PAGOTINTERES,
		IIF(IsNull(PC.DescuentoAporte,0)+IsNull(TC.Aporte,0)>PC.Aporte,PC.Aporte,IsNull(PC.DescuentoAporte,0)+IsNull(TC.Aporte,0)) AS PAGOTAPORTE,
		IsNull(PC.DescuentoCapital,0) as DESCUENTOCAPITAL,
		IsNull(PC.DescuentoInteres,0) as DESCUENTOINTERES,
        PC.FechaVencimiento,
        P.CodSocio,
		PC.CodEstado,
        ROW_NUMBER() OVER(PARTITION BY P.CodPrestamo ORDER BY PC.CodPrestamoCuota ASC ) AS r
    
    FROM          PrestamoCuota PC
    INNER JOIN    Prestamo                    P    ON PC.CodPrestamo        = P.CodPrestamo
    LEFT  JOIN    #TMP_COBRANZA               TC   ON PC.CodPrestamoCuota    = TC.CodPrestamoCuota
    WHERE
        P.CodEstado NOT IN (563)                               -- TODOS LOS PRESTAMOS INCLUSO LOS CANCELADOS MENOS ANULADOS
        AND PC.CodEstado IN (21,22,23,24,346)             -- ESTADO CUOTA SE INCLUYE ANULADO PORQUE AL RETROCEDER POSIBLEMENTE AUN NO ESTE ANULADO se quito 1003 porque si debe figurar porque hay pago
        AND (CONVERT(DATE,PC.FechaCreacion)          IS NULL OR  CONVERT(DATE,PC.FechaCreacion)            <=@FechaConvert)
        AND (CONVERT(DATE,PC.FechaAnulacionCrono)    IS NULL OR  CONVERT(DATE,PC.FechaAnulacionCrono)    > @FechaConvert)
        AND CONVERT(DATE,P.FechaDesembolso) <=@FechaConvert       -- SOLO LOS PRESTAMOS MENORES A LA FECHA DE REPORTE

	 UNION
	
    SELECT
        PC.CodPrestamo,
        PC.CodPrestamoCuota,
        IIF((PC.Capital - IsNull(PC.DescuentoCapital,0))-IsNull(TC.Capital,0)<0,0,
        (PC.Capital - IsNull(PC.DescuentoCapital,0))- IsNull(TC.Capital,0))
        AS SaldoCapitalSoles,

		IIF((PC.Interes - IsNull(PC.DescuentoInteres,0))-IsNull(TC.Interes,0)<0,0,
        (PC.Interes - IsNull(PC.DescuentoInteres,0))- IsNull(TC.Interes,0))
        AS SaldoInteresSoles,

		IIF((PC.Aporte - IsNull(PC.DescuentoAporte,0))-IsNull(TC.Aporte,0)<0,0,
        (PC.Aporte - IsNull(PC.DescuentoAporte,0))- IsNull(TC.Aporte,0))
        AS SaldoAporteSoles,

		IIF(IsNull(PC.DescuentoCapital,0)+IsNull(TC.Capital,0)>PC.Capital,PC.Capital,IsNull(PC.DescuentoCapital,0)+IsNull(TC.Capital,0)) AS PAGOTCAPITAL,
		IIF(IsNull(PC.DescuentoInteres,0)+IsNull(TC.Interes,0)>PC.Interes,PC.Interes,IsNull(PC.DescuentoInteres,0)+IsNull(TC.Interes,0)) AS PAGOTINTERES,
		IIF(IsNull(PC.DescuentoAporte,0)+IsNull(TC.Aporte,0)>PC.Aporte,PC.Aporte,IsNull(PC.DescuentoAporte,0)+IsNull(TC.Aporte,0)) AS PAGOTAPORTE,
		IsNull(PC.DescuentoCapital,0) as DESCUENTOCAPITAL,
		IsNull(PC.DescuentoInteres,0) as DESCUENTOINTERES,
        PC.FechaVencimiento,
        P.CodSocio,
		PC.CodEstado,
        ROW_NUMBER() OVER(PARTITION BY P.CodPrestamo ORDER BY PC.CodPrestamoCuota ASC ) AS r
    
    FROM          PrestamoCuota PC
    INNER JOIN    Prestamo                    P    ON PC.CodPrestamo        = P.CodPrestamo
    LEFT  JOIN    #TMP_COBRANZA               TC   ON PC.CodPrestamoCuota    = TC.CodPrestamoCuota
    WHERE
        P.CodEstado NOT IN (563)                               -- TODOS LOS PRESTAMOS INCLUSO LOS CANCELADOS MENOS ANULADOS
        AND PC.CodEstado IN (379,1003)             -- ESTADO CUOTA SE INCLUYE ANULADO PORQUE AL RETROCEDER POSIBLEMENTE AUN NO ESTE ANULADO
        AND (CONVERT(DATE,PC.FechaCreacion)          IS NULL OR  CONVERT(DATE,PC.FechaCreacion)            <=@FechaConvert)
        AND CONVERT(DATE,P.FechaDesembolso) <=@FechaConvert       -- SOLO LOS PRESTAMOS MENORES A LA FECHA DE REPORTE
		) UNIONTABLA

--SELECT * FROM #TMP_PTMOG WHERE CodPrestamoCuota =302218


select
RIGHT(CONCAT('00000000',P.Numero),8) AS NroPrestamo,
ISNULL(CONVERT(VARCHAR(10),pc.FechaVencimiento,103),'')
  as FechaVencimiento,
ISNULL(pc.numerocuota,'') as numerocuota,

--ESTO ERA PORKE SI ES 0 VA SALDO Y SI ES 9 VA EL CRONOGRAMA PORKE ASI SOLICITA
--IIF(PC.CuotaFija=0,
--PC.Capital,
--IIF(TC2.PAGOTCAPITAL>=PC.Capital,PC.Capital,tc2.SaldoCapitalSoles)
--) AS CapitalPP2,
 
IIF(PC.CuotaFija=0,
PC.Capital,
IIF((TC2.PAGOTCAPITAL + TC2.PAGOTINTERES + TC2.PAGOTAPORTE)>=PC.CuotaFija ,PC.Capital,tc2.SaldoCapitalSoles)
) AS CapitalPP2,


IIF(PC.CuotaFija=0,
PC.Interes,
IIF((TC2.PAGOTCAPITAL + TC2.PAGOTINTERES + TC2.PAGOTAPORTE)>=PC.CuotaFija ,PC.Interes,tc2.SaldoInteresSoles)
) AS InteresPP2,


'0' as CargosGeneralesPP2,
'0' as CargosSeguroPP2,

IIF(PC.CuotaFija=0,
PC.Aporte,
IIF((TC2.PAGOTCAPITAL + TC2.PAGOTINTERES + TC2.PAGOTAPORTE)>=PC.CuotaFija ,PC.Aporte,tc2.SaldoAporteSoles)
) AS AportePP2,

IIF(PC.CuotaFija=0,
PC.Aporte,
IIF((TC2.PAGOTCAPITAL + TC2.PAGOTINTERES + TC2.PAGOTAPORTE)>=PC.CuotaFija ,PC.Aporte,tc2.SaldoAporteSoles)
) AS TotalCargoPP2,
 



--IIF(PC.CodEstado=346,0,
--IIF(PC.CuotaFija=0,0,

--IIF((TC2.PAGOTCAPITAL + TC2.PAGOTINTERES + TC2.PAGOTAPORTE)>=PC.CuotaFija,PC.CuotaFija,
--TC2.SaldoCapitalSoles + TC2.SaldoInteresSoles + TC2.SaldoAporteSoles)

--)) as TotalPago,---? COMO SERIA ACA ES EL TOTAL QUE VA A PAGAR EN EL GRONOGRAMA PERO SI YA CANCELO SERIA 0 PORQUE NO DEBE NADA O ES LA DEL PLAN DE PAGOS CAP + INT + APORTE Y EN CASO YA HAYA PAGADO SERIA LOS SALDOS

---porque sino el 346 el total seria 0 y eso no quieren
IIF(PC.CuotaFija=0,0,

IIF((TC2.PAGOTCAPITAL + TC2.PAGOTINTERES + TC2.PAGOTAPORTE)>=PC.CuotaFija,PC.CuotaFija,
TC2.SaldoCapitalSoles + TC2.SaldoInteresSoles + TC2.SaldoAporteSoles)

) as TotalPago,---? COMO SERIA ACA ES EL TOTAL QUE VA A PAGAR EN EL GRONOGRAMA PERO SI YA CANCELO SERIA 0 PORQUE NO DEBE NADA O ES LA DEL PLAN DE PAGOS CAP + INT + APORTE Y EN CASO YA HAYA PAGADO SERIA LOS SALDOS


0 as AhorrosPP2,

IIF(TA.CodPrestamocuota IS NULL,
IIF((TC2.PAGOTCAPITAL + TC2.PAGOTINTERES + TC2.PAGOTAPORTE)>=PC.CuotaFija,'9','0'),'9') as PagadoPP2,

pc.CodEstado AS CodEstadoPP2, 
pc.CodPrestamoCuota AS CodPrestamocuotaPP2,
pc.cuotafija AS CuotaFijaPP2,

-------------------------------------------------

IIF(PC.CodEstado<>379,pc.capital,CD.CAPITAL) AS CapitalCRONO,
IIF(PC.CodEstado<>379,pc.interes,CD.INTERES) AS InteresCRONO,
IIF(PC.CodEstado<>379,pc.Aporte,CD.APORTE) AS AporteCRONO,
IIF(PC.CodEstado<>379,pc.aporte,CD.APORTE) as TotalCargoCRONO,
'0' as CargosGeneralesCRONO,
'0' as CargosSeguroCRONO,
iif(pc.codestado=346,0,
IIF(PC.CodEstado<>379,(pc.Capital + pc.Interes + pc.FondoContigencia + pc.Aporte),CD.CAPITAL+CD.INTERES+CD.APORTE)) as TotalPagoCRONO,--cambio de joseph revisar
0 as AhorrosCRONO,
IIF(TA.CodPrestamocuota IS NULL,
IIF((TC2.PAGOTCAPITAL + TC2.PAGOTINTERES + TC2.PAGOTAPORTE)>=PC.CuotaFija,'9','0'),'9') as PagadoCrono,

pc.CodEstado, 
pc.CodPrestamoCuota,
pc.CodPrestamo,
pc.cuotafija,
------
TC2.PAGOTCAPITAL, 
TC2.DESCUENTOCAPITAL,
TC2.DESCUENTOINTERES 
INTO #ABC
from prestamocuota pc
inner join prestamo p on pc.CodPrestamo =p.CodPrestamo
inner join socio s on p.CodSocio =s.CodSocio
INNER JOIN    #TMP_PTMOG     TC2        ON    PC.CodPrestamoCuota            = TC2.CodPrestamoCuota
left join (select * from #tablaAmortizacion379 where CONVERT(DATE,FechaCreacion)<=@FechaConvert  ) TA ON pc.CodPrestamoCuota =TA.CodPrestamocuota
LEFT JOIN 
(SELECT SUM(CAPITAL) AS CAPITAL,SUM(INTERES) AS INTERES,SUM(APORTE) AS APORTE,CodPrestamoCuota FROM CobranzaDet GROUP BY CodPrestamoCuota) CD ON pc.CodPrestamoCuota =CD.CodPrestamoCuota
where
P.FECHAVENTACARTERA IS NULL and --cambiara
p.CodEstado <>563   and 
CONVERT(VARCHAR(10),pc.FechaVencimiento,103) is not null  
AND S.CodSocio  not in (select codsocio from #TMP_SOCIOBLOQUEAR) 
AND PC.CodPrestamoCuota NOT IN (
							 SELECT CodPrestamoCuota  FROM (
							select
							PC.CodPrestamoCuota,
							ISNULL(pc.numerocuota,'') as numerocuota,
							pc.interes,
							iif(pc.codestado=346,0,(pc.Capital + pc.Interes + pc.FondoContigencia + pc.Aporte)) as TotalPago
							from prestamocuota pc
							inner join prestamo p on pc.CodPrestamo =p.CodPrestamo
							inner join socio s on p.CodSocio =s.CodSocio
							where
							pc.CodEstado not in (24,379) and p.CodEstado <>563   and CONVERT(VARCHAR(10),pc.FechaVencimiento,103) is not null 
							 AND S.CodSocio  not in (select codsocio from #TMP_SOCIOBLOQUEAR) 
							 AND   P.FECHAVENTACARTERA IS NULL
							 ) TABLA 
							 WHERE numerocuota =0 AND Interes =0 AND TotalPago =0
 
 ) ---duda aun

order by pc.CodPrestamo,  pc.CodPrestamoCuota 

SELECT * FROM #ABC order by CodPrestamo, CodPrestamoCuota 
--SELECT * FROM #ABC where PagadoPP2 =9  order by CodPrestamo, CodPrestamoCuota 
--select * from #ABC where PagadoPP2 =0 order by CodPrestamo, CodPrestamoCuota 


--select *  from #ABC where NroPrestamo =132196
--select  SUM(capital) AS CAPITAL,CodEstado  from #ABC GROUP BY CodEstado,NroPrestamo having  NroPrestamo =132196

--para saber cuantos tienen ese mismo estado (cantidad)
--select COUNT(1),CodEstado  from #ABC GROUP BY CodEstado

--para saber cuantos tienen ese mismo estado (monto)
--select  SUM(CapitalPP2) AS CAPITAL,CodEstado  from #ABC GROUP BY CodEstado
--select NroPrestamo, SUM(CapitalPP2) from #ABC  where PagadoPP2=0  GROUP BY  NroPrestamo having SUM(CapitalPP2)>0   order by NroPrestamo 

   


DROP TABLE #TMP_PTMOG
DROP TABLE #ABC
 
