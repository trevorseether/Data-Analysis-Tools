DECLARE @FechaCorte datetime
SET @FechaCorte = '20230430'

-------------------------------------------------------
SELECT FechaCorte1, Nro_Fincore, MontodeDesembolso22, TipodeProducto43,'MICROEMPRESA?' as 'CODIGO DE',
case when MontodeDesembolso22 > 20000 and MontodeDesembolso22 <= 300000 then 'PEQUEÑA EMPRESA(15 AL 19)'
		ELSE 'MEDIANA EMPRESA (95 AL 99)' 
		END AS 'TIPO CORRECTO'
FROM anexos_riesgos2..Anx06_preliminar
WHERE FechaCorte1 = @FECHACORTE
and TipodeProducto43 in (21,22,23,24,25,29)
and MontodeDesembolso22 > 20000
order by MontodeDesembolso22
---------------------------------------------------------
SELECT FechaCorte1, Nro_Fincore, MontodeDesembolso22, TipodeProducto43,'PEQUEÑA EMPRESA?' as 'CODIGO DE',
CASE WHEN MontodeDesembolso22 <= 20000 THEN 'MICROEMPRESA (21 AL 29)'
	ELSE 'MEDIANA EMPRESA (95 AL 99)' END AS 'TIPO CORRECTO'
FROM anexos_riesgos2..Anx06_preliminar
WHERE FechaCorte1 = @FECHACORTE
and TipodeProducto43 in (15,16,17,18,19)
and MontodeDesembolso22 < 20001
AND MontodeDesembolso22 > 0
---------------------------------------------------------
SELECT FechaCorte1, Nro_Fincore, MontodeDesembolso22, TipodeProducto43,'PEQUEÑA EMPRESA?' as 'CODIGO DE'
FROM anexos_riesgos2..Anx06_preliminar
WHERE FechaCorte1 = @FECHACORTE
and TipodeProducto43 in (15,16,17,18,19)
and MontodeDesembolso22 > 300000

SELECT FechaCorte1, Nro_Fincore, MontodeDesembolso22, TipodeProducto43,'MEDIANA EMPRESA?' as 'CODIGO DE'
FROM anexos_riesgos2..Anx06_preliminar
WHERE FechaCorte1 = @FECHACORTE
and TipodeProducto43 in (95,96,97,98,99)
and MontodeDesembolso22 < 300001

---

select TipodeProducto43,Saldodecolocacionescreditosdirectos24,* from anexos_riesgos2..Anx06_preliminar
where Nro_Fincore = 94540
order by FechaCorte1

-----------------------------------------------------------------------------------------------------------
------ para revisar si está bien alineado l tipo de producto 43
select  NumerodeDocumento10, count(distinct TipodeProducto43) as 'DIFERENTES PRODUCTOS'
from anexos_riesgos2..Anx06_preliminar a
where FechaCorte1 = '20230430'
----     and TipodeProducto43 in (15,16,17,18,19,21,22,23,24,25,29,95,96,97,98,99)
group by NumerodeDocumento10
having count(distinct a.TipodeProducto43) > 1

select Nro_Fincore,Saldodecolocacionescreditosdirectos24,TipodeProducto43,* 
from anexos_riesgos2..Anx06_preliminar as a
where FechaCorte1 = '20230430'
and NumerodeDocumento10 = '10540169'
order by FechaCorte1, a.Nro_Fincore
--------------------------------------------------------------------------------------------------------
select  NumerodeDocumento10, count(distinct ClasificaciondelDeudorconAlineamiento15) as 'DIFERENTES CALIFICACIONES'
from anexos_riesgos2..Anx06_preliminar a
where FechaCorte1 = '20230430'
----     and TipodeProducto43 in (15,16,17,18,19,21,22,23,24,25,29,95,96,97,98,99)
group by NumerodeDocumento10
having count(distinct a.ClasificaciondelDeudorconAlineamiento15) > 1

select Nro_Fincore,Saldodecolocacionescreditosdirectos24,ClasificaciondelDeudorconAlineamiento15,* 
from anexos_riesgos2..Anx06_preliminar as a
where FechaCorte1 = '20230430'
and NumerodeDocumento10 = '10540169' ---NO HAY CRÉDITOS MAL ALINEADOS
order by FechaCorte1, a.ClasificaciondelDeudorconAlineamiento15
