--CÓDIGO PARA VERIFICAR SI HAY LAGÚN ALINEAMIENTO DEL PRODUCTO 43/ O DE LA CLASIFICACIÓN ALINEAMIENTO 15/ 
------ para revisar si está bien alineado l tipo de producto 43


select  NumerodeDocumento10, count(distinct TipodeProducto43) as 'DIFERENTES PRODUCTOS'
from anexos_riesgos2..Anx06_preliminar a
where FechaCorte1 = '20230430'
     and TipodeProducto43 in (15,16,17,18,19,21,22,23,24,25,29,95,96,97,98,99)
group by NumerodeDocumento10
having count(distinct a.TipodeProducto43) > 1

select Nro_Fincore,Saldodecolocacionescreditosdirectos24,TipodeProducto43,* 
from anexos_riesgos2..Anx06_preliminar as a
where FechaCorte1 = '20230430'
and NumerodeDocumento10 = '10540169' ---NO HAY CRÉDITOS MAL ALINEADOS
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

