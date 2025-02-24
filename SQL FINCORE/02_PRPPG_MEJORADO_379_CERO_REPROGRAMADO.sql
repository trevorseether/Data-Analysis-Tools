
--Estados:
--select * from TablaMaestraDet where CodTablaDet  =563
--select * from TablaMaestraDet where CodTablacab=9

--ejemplos :
--select * from PrestamoCuota where CodPrestamo =97413 order by CodPrestamoCuota  
--select * from PrestamoCuota where CodPrestamo =25197 order by CodPrestamoCuota  
--select * from PrestamoCuota where CodPrestamo =10496 order by CodPrestamoCuota  
--select * from PrestamoCuota where CodPrestamo =75305 order by CodPrestamoCuota  
--select * from PrestamoCuota where CodPrestamo =122181 order by CodPrestamoCuota  
 
 IF OBJECT_ID('tempdb.dbo.#TMP_SOCIOBLOQUEAR', 'U') IS NOT NULL
DROP TABLE #TMP_SOCIOBLOQUEAR;  
	SELECT CODSOCIO INTO #TMP_SOCIOBLOQUEAR FROM Socio   WHERE CodSocio IN (
	105,637,1409,1598,1650,1654,1685,1996,2135,2144,2534,4856,6621,10491,21815,34561,
	17206,1650,1654,293,470,508,509,578,582,622,623,625,
	627,631,632,634,642,643,644,646,667,668,669,671,674,675,
	676,679,680,699,704,4724,6642,7211,374,388,391,392,393,
	394,396,397,398,399,400,405,412,413,414,415,416,417,
	420,421,422,424,425,450,451,453)


	select
	RIGHT(CONCAT('00000000',P.Numero),8) AS NroPrestamo,
	ISNULL(CONVERT(VARCHAR(10),pc.FechaVencimiento,103),'')
	  as FechaVencimiento,
	ISNULL(pc.numerocuota,'') as numerocuota,

	IIF(PC.CodEstado<>379,pc.capital,CD.CAPITAL) AS capital,
	IIF(PC.CodEstado<>379,pc.interes,CD.INTERES) AS interes,
	'0' as CargosGenerales,
	'0' as CargosSeguro,
	IIF(PC.CodEstado<>379,pc.Aporte,CD.APORTE) AS Aporte,
	IIF(PC.CodEstado<>379,pc.aporte,CD.APORTE) as TotalCargo,

	iif(pc.codestado=346,0, IIF(PC.CodEstado <> 379,(pc.Capital + pc.Interes + pc.FondoContigencia + pc.Aporte),CD.CAPITAL+CD.INTERES+CD.APORTE)) as TotalPago,

	0 as Ahorros,
	iif(pc.CodEstado in (22,1003,379),'9','0') as Pagado,pc.CodEstado 

--,pc.CodEstado as EstadoCuota,pc.CuotaFija,P.CodEstado as EstadoPrestamo,P.FechaVentaCartera,P.CodSocio,p.CodPrestamo,p.FechaDesembolso,pc.periodo   
from prestamocuota pc
inner join prestamo p on pc.CodPrestamo =p.CodPrestamo
inner join socio s on p.CodSocio =s.CodSocio
LEFT JOIN 
(SELECT SUM(CAPITAL) AS CAPITAL,SUM(INTERES) AS INTERES,SUM(APORTE) AS APORTE,CodPrestamoCuota FROM CobranzaDet GROUP BY CodPrestamoCuota)
CD ON pc.CodPrestamoCuota =CD.CodPrestamoCuota
where
pc.CodEstado not in (24) and p.CodEstado <>563   and CONVERT(VARCHAR(10),pc.FechaVencimiento,103) is not null --and (pc.Capital + pc.Interes + pc.FondoContigencia + pc.Aporte)>0
 AND S.CodSocio  not in (select codsocio from #TMP_SOCIOBLOQUEAR) 
 AND PC.CodPrestamoCuota NOT IN (
							 SELECT CodPrestamoCuota  FROM (
							select
							PC.CodPrestamoCuota,
							ISNULL(pc.numerocuota,'') as numerocuota,
							pc.interes,
							iif(pc.CodEstado in (22,1003),'9','0') as Pagado,
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
 
 )
-- AND   P.FECHAVENTACARTERA IS NULL
order by pc.CodPrestamo,  pc.CodPrestamoCuota 


