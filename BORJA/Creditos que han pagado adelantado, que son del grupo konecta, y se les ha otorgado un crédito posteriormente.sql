-----crecaión de tabla que nos servirá de auxiliar
--drop table experimentos2..konecta_max_fecha
select Nro_Fincore, max(FechaCorte1) as 'FechaCorte1'
--into experimentos2..konecta_max_fecha
from anexos_riesgos2.dbo.Anx06_preliminar
where FechaCorte1 > '20220101'
and (empresa like '%konect%'
	or PLANILLA like '%konec%'
	or NUEVA_PLANILLA like '%konect%'
	or empresa like '%allu%'
	or PLANILLA like '%allu%'
	or NUEVA_PLANILLA like '%allu%'
	or empresa like '%stratto%'
	or PLANILLA like '%stratto%'
	or NUEVA_PLANILLA like '%stratto%'
	or empresa like '%telemark%'
	or PLANILLA like '%telemark%'
	or NUEVA_PLANILLA like '%telemark%'
	or empresa like '%agencia%b12%'
	or PLANILLA like '%agencia%b12%'
	or NUEVA_PLANILLA like '%agencia%b12%'
	or empresa like '%ecomdata%'
	or PLANILLA like '%ecomdata%'
	or NUEVA_PLANILLA like '%ecomdata%'

	)
group by Nro_Fincore


---estos son los créditos que han adelantado sus pagos
select 
a.FechaCorte1, a.Nro_Fincore, ApellidosyNombresRazonSocial2, CodigoSocio7, 
FechadeDesembolso21, NumerodeCuotasPagadas45, NumerodeCuotasProgramadas44
--into experimentos2..konecta_pagos_adelantados
from anexos_riesgos2..Anx06_preliminar as a
inner join experimentos2..konecta_max_fecha as b
on (a.Nro_Fincore = b.Nro_Fincore 
	and a.FechaCorte1 = b.FechaCorte1) 
and (NumerodeCuotasProgramadas44 - NumerodeCuotasPagadas45) >1
and CapitalVencido29 = 0
and a.FechaCorte1 < '20230331'
order by a.FechaCorte1

-----------------------
---le hacemos un inner join con los que tienen créditos
---cuyo desembolso es posterior a la última fecha de corte
select a.FechaCorte1, a.Nro_Fincore, a.ApellidosyNombresRazonSocial2, a.CodigoSocio7, 
a.FechadeDesembolso21, a.NumerodeCuotasPagadas45, a.NumerodeCuotasProgramadas44
, b.Nro_Fincore as 'CREDITO POSTERIOR', b.FechadeDesembolso21 as 'FECHA DESEMBOLSO POSTERIOR'
from 
experimentos2..konecta_pagos_adelantados as a
inner join anexos_riesgos2..Anx06_preliminar as b
on (a.CodigoSocio7 = b.CodigoSocio7)
where b.FechadeDesembolso21 > a.fechacorte1

