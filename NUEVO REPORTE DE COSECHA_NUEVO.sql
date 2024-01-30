--------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------
-----------------------PARA AÑADIR LO QUE FALTA AL REPORTE DE cosecha..cosecha_nuevo--------------
--------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------
--query para reparar el reporte si algo sale mal

use COSECHA
go
/*

drop table cosecha..cosecha_nuevo

select * 
into cosecha..cosecha_nuevo
from anexos_riesgos2..Anx06_preliminar where FechaCorte1 >= '20220731'

update cosecha..cosecha_nuevo ----esta parte creo que no hace falta ejecutarla, (investigar si hace falta recuperar los castigados incluyendo los vendidos)
set MCastigadoxM = 0 ---
--    [DESEMBOLSO_AGREGADO]
*/

----------------------------------------------------------------------------------------------------
----ahora se debe crear una nueva columna que servirá para el filtro de los montos desembolsados----
----------------------------------------------------------------------------------------------------
/*
alter table cosecha..cosecha_nuevo
add desembolso_para_filtros numeric(16,4)
go

update cosecha..cosecha_nuevo
set desembolso_para_filtros = MontodeDesembolso22

*/

--añadiendo vencido, judicial, y castigado para filtros
/*
alter table cosecha..cosecha_nuevo
add vencido_auxiliar numeric(16,4)
alter table cosecha..cosecha_nuevo
add judicial_auxiliar numeric(16,4)
alter table cosecha..cosecha_nuevo
add castigado_auxiliar numeric(16,4)
alter table cosecha..cosecha_nuevo
add cuotas_pagadas_auxiliar int
*/
------------------------------------------------------------------------------------
----AÑADIMOS LOS DE MESES PASADOS PARA REALIZAR LA COMPARACIÓN INTERTEMPORAL--------
------------------------------------------------------------------------------------

declare @fechaactual as datetime
set @fechaactual = '20220731' ---- hay que añadir los datos desde adelante hasta atrás, por un año
---- tema pendiente, aprender a usar cursores para añadir estos resultados
INSERT INTO cosecha_nuevo (
nro_fincore,
FechadeDesembolso21,
FechaCorte1,
ApellidosyNombresRazonSocial2,
Saldodecolocacionescreditosdirectos24, ---aqui va cero
CapitalVencido29, ------------------------aqui va cero
nuevo_capitalvencido, --------------------aqui va cero
CapitalenCobranzaJudicial30,--------------aqui va cero
MontodeDesembolso22,----------------------aqui va cero
desembolso_para_filtros,
MDesembolsadoxM,
TipodeProducto43,
PROMOTOR,
NUEVO_PROMOTOR,
administrador,
--MCastigadoxM,
MtotalDesembolsadoxM,
Departamento,
provincia,
Distrito,
NumerodeCredito18,
Refinanciado,
Reprogramados52,
Monedadelcredito17,
TipodeDocumento9,
NumerodeDocumento10,
originador,
NumerodeCuotasProgramadas44,
NumerodeCuotasPagadas45,
TIPO_afil,
[Distrito Negocio],
[Dpto Negocio],
[Provincia Negocio])

select
a.nro_fincore,
a.FechadeDesembolso21,
@fechaactual, ---aqui va la fecha de corte en la que se van a insertar datos
a.ApellidosyNombresRazonSocial2,
0, ----SALDO DE CRÉDITO 24
0, ----CAPITAL VENCIDO 29
0, ----NUEVO CAP VENCIDO (DESPUÉS DEL CAMBIO DE METODOLOGÍA PARA MYPE)
0, ----CAPITAL EN COBRANZA JUDICIAL 30
0, ---- MONTO DESEMBOLSADO 22
a.MontodeDesembolso22,
A.MDesembolsadoxM,
a.TipodeProducto43,
a.PROMOTOR,
a.NUEVO_PROMOTOR,
a.administrador,
--a.MCastigadoxM,
a.MtotalDesembolsadoxM,
a.Departamento,
a.provincia,
a.Distrito,
a.NumerodeCredito18,
a.Refinanciado,
a.Reprogramados52,
A.Monedadelcredito17,
A.TipodeDocumento9,
A.NumerodeDocumento10,
a.originador,
a.NumerodeCuotasProgramadas44,
a.NumerodeCuotasPagadas45,
a.TIPO_afil,
a.[Distrito Negocio],
a.[Dpto Negocio],
a.[Provincia Negocio]

FROM 
	anexos_riesgos2..Anx06_preliminar AS A

where
	DATENAME(MONTH,a.FechaCorte1) = DATENAME(MONTH,a.FechadeDesembolso21)
	and year(a.FechaCorte1) = year(a.FechadeDesembolso21)
	and a.fechacorte1 < @fechaactual
order by FechaCorte1


--------------------------------------------------------------------------------------------------------------
-----añadimos los montos de capital vencido, judicial, castigado, solo para que sirva en algunos filtros------
--------------------------------------------------------------------------------------------------------------
---ejecutar este código demora casi 4 minutos
/*
update a
set a.vencido_auxiliar = b.nuevo_capitalvencido
from cosecha_nuevo as a
left join anexos_riesgos2..Anx06_preliminar as b
on ((a.nro_fincore = b.nro_fincore) and (a.fechacorte1 = b.fechacorte1))
where a.vencido_auxiliar is null

update a
set a.judicial_auxiliar = b.CapitalenCobranzaJudicial30
from cosecha_nuevo as a
left join anexos_riesgos2..Anx06_preliminar as b
on ((a.nro_fincore = b.nro_fincore) and (a.fechacorte1 = b.fechacorte1))
where a.judicial_auxiliar is null

update a
set a.castigado_auxiliar = b.SaldosdeCreditosCastigados38
from cosecha_nuevo as a
left join anexos_riesgos2..Anx06_preliminar as b
on ((a.nro_fincore = b.nro_fincore) and (a.fechacorte1 = b.fechacorte1))
where a.castigado_auxiliar is null

update a
set a.cuotas_pagadas_auxiliar = b.NumerodeCuotasPagadas45
from cosecha_nuevo as a
left join anexos_riesgos2..Anx06_preliminar as b
on ((a.nro_fincore = b.nro_fincore) and (a.fechacorte1 = b.fechacorte1))
where a.cuotas_pagadas_auxiliar is null
*/
--------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------
------------------------HASTA AQUI SE HA INGRESADO TODO MENOS MtotalCastigadoxM-------------
--------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------

---AHORA SÍ, PROCEDEMOS CON EL PASO FINAL
--declare @fechaactual as datetime
--set @fechaactual = '20221130'
/*
INSERT INTO COSECHA..COSECHA_nuevo (
FechadeDesembolso21,
NRO_FINCORE,
MCastigadoxM,
FechaCorte1,
ApellidosyNombresRazonSocial2,
TipodeProducto43,
PROMOTOR,
NUEVO_PROMOTOR,
administrador,
Departamento,
provincia,
Distrito,
NumerodeCredito18,
Refinanciado,
Reprogramados52,
Monedadelcredito17,
TipodeDocumento9,
NumerodeDocumento10,
originador
)
SELECT 
a.FechadeDesembolso21,
A.NRO_FINCORE, 
A.MCastigadoxM,
@fechaactual,
A.ApellidosyNombresRazonSocial2,
A.TipodeProducto43,
A.PROMOTOR,
A.NUEVO_PROMOTOR,
A.administrador,
a.Departamento,
a.provincia,
a.Distrito,
a.NumerodeCredito18,
a.Refinanciado,
a.Reprogramados52,
A.Monedadelcredito17,
A.TipodeDocumento9,
A.NumerodeDocumento10,
a.originador

FROM experimentos..copiapruebajuanjose AS A
where MCastigadoxM > 0

*/