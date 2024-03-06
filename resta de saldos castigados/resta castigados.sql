
DECLARE @CORTE AS DATE = '20211231'
DECLARE @CORTE_ANTERIOR AS DATE = EOMONTH(DATEADD(DAY, -1, EOMONTH(DATEADD(MONTH, -1, @CORTE))));

DECLARE @uno as float =(select 
	--count(Nro_Fincore)  as 'actual'
	sum(SaldosdeCreditosCastigados38) as 'actual'
from anexos_riesgos3..ANX06
where FechaCorte1 = @CORTE
and SaldosdeCreditosCastigados38 > 0
AND ApellidosyNombresRazonSocial2 NOT like '%invers%grau%')
--and ApellidosyNombresRazonSocial2 like '%invers%grau%')

DECLARE @dos as float =(select 
	--count(Nro_Fincore) as 'anterior'
	sum(SaldosdeCreditosCastigados38) as 'anterior'
from anexos_riesgos3..ANX06
where FechaCorte1 = @CORTE_ANTERIOR
and SaldosdeCreditosCastigados38 > 0
AND ApellidosyNombresRazonSocial2 NOT like '%invers%grau%')
--and ApellidosyNombresRazonSocial2 like '%invers%grau%')

SELECT @uno - @dos AS 'VAR RECUPERACIONES'

----------------------------
DECLARE @uno1 as float =(select 
	--count(Nro_Fincore)  as 'actual'
	sum(SaldosdeCreditosCastigados38) as 'actual'
from anexos_riesgos3..ANX06
where FechaCorte1 = @CORTE
and SaldosdeCreditosCastigados38 > 0
--AND ApellidosyNombresRazonSocial2 NOT like '%invers%grau%')
and ApellidosyNombresRazonSocial2 like '%invers%grau%')

DECLARE @dos2 as float =(select 
	--count(Nro_Fincore) as 'anterior'
	sum(SaldosdeCreditosCastigados38) as 'anterior'
from anexos_riesgos3..ANX06
where FechaCorte1 = @CORTE_ANTERIOR
and SaldosdeCreditosCastigados38 > 0
--AND ApellidosyNombresRazonSocial2 NOT like '%invers%grau%')
and ApellidosyNombresRazonSocial2 like '%invers%grau%')

SELECT @uno1 - @dos2 AS 'VARIACIÓN INVERSIONES GRAU'

select sum(SaldosdeCreditosCastigados38) as 'castigado actual' from anexos_riesgos3..ANX06 where FechaCorte1 = @CORTE
select sum(SaldosdeCreditosCastigados38) as 'castigado anterior' from anexos_riesgos3..ANX06 where FechaCorte1 = @CORTE_ANTERIOR

select 'debe salir negativo para que se ponga el signo inverso en el excel'

select 11339446.1500 - 11525098.6000
select -1827.44999999995 - 183825
