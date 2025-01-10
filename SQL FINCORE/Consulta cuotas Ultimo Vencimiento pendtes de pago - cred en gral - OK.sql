select 
	--p.codprestamo,
	SC.CodigoSocio,
	iif(sc.CodTipoPersona =1,CONCAT(SC.ApellidoPaterno,' ',SC.ApellidoMaterno, ' ', SC.Nombres),sc.razonsocial) AS Socio, SC.NroDocIdentidad, SC.FechaNacimiento,
	CONCAT('',RIGHT(CONCAT('00000000',rtrim(P.Numero)),8)) AS NroPrestamoFincore, 
	--codprestamoFox, 
	FechaDesembolso, 
	PC.FechaVencimiento,   
	p.cuotaFija as CuotaMensual,
	--Cuota_mensual, 
	--estado_cuo as estado_cuota,
	--p.CodEstado as Estado_pre, 
	FI.CODIGO AS COD_FINALIDAD, 
	FI.DESCRIPCION AS FINALIDAD, 
	plla.Descripcion as planilla, 
	gc.descripcion as Funcionario, 
	FechaVentaCartera, 
	FechaCastigo
	,sco.Celular1, sco.CelularContacto, sco.Email as Correo
from prestamo p
inner join socio sc on p.codsocio=sc.codsocio
LEFT JOIN TablaMaestraDet EE ON P.CodEstado  =EE.CodTablaDet
LEFT join Planilla as plla on p.CodPlanilla =plla.codplanilla
LEFT JOIN FINALIDAD AS FI ON P.CODFINALIDAD=FI.CODFINALIDAD 
left join grupocab as gc on p.codgrupocab = gc.codgrupocab
inner join SocioContacto sco on sc.codsocio = sco.CodSocio

inner join 
 
( select * from (SELECT CodPrestamo,MAX(FechaVencimiento) As FechaVencimiento  FROM PrestamoCuota
WHERE CodEstado IN (21,23)  -- 21 Pend, 23 Amort, 22 Canc
GROUP BY CodPrestamo) as r ) pc
on p.CodPrestamo =pc.CodPrestamo

where  
p.codestado =341  --and p.numero='00032891'
--pc.estado_cuo in (21,23) and 
AND CONVERT(VARCHAR(10),pc.FechaVencimiento,112) like '%202206%' and p.codEstado <>563  -- CONVERT(DATE,pc.fechaprimerdescuento)   =CONVERT(VARCHAR(8),'20210831',112)
order by nroprestamofincore
