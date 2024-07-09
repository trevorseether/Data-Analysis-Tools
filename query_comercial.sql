--#################################################################################
-- PRIMER REPORTE GERENCIAL DEL MES, PRIMERO PORQUE AQUÍ SE INSERTAN LOS DATOS
-- REPORTE DE GERENCIA COMERCIAL
--#################################################################################
-- NO OLVIDAR QUE [COMERCIAL]..[ANX06] también sirve de copia de respaldo
/*
ahora todos los anexos estarán en anexos_riesgos3
*/
use Comercial
go
/*
los anexos06 actuales son

ANEXOS_RIESGOS2..Anx06_preliminar
ANEXOS_RIESGOS3..Anx06
*/

--en el excel, primero eliminar filas y columnas vacías, por si acaso
--segundo, aplicar formato texto desde D hasta K, y desde M hasta T
--arreglar la fecha de desembolso con esta fórmula, creando una columna a su derecha:
--=AÑO(V2)&DERECHA("00"&MES(V2);2)&DERECHA("00"&DIA(V2);2)
--------------------------------------------------------------------------------------------------
--una vez subido el anexo06 del mes, nos vamos a ejecutar el procedimiento almacenado
--este anexo debe estar como dbo.Anx06_20230930

---------------------------------Aquí creando una copia por si se malogra la tabla 'Cabecera'

--drop table anexos_riesgos3..cabecera_copia_abril2024
select *
into anexos_riesgos3..cabecera_copia_mayo2024 ---aqui hay una copia de la cabecera
from anexos_riesgos2..cabecera order by FechaCorte1

--drop table anexos_riesgos2..cabecera
--select *
--into  anexos_riesgos2..cabecera ----renovando la tabla cabecera si es que salió mal
--from anexos_riesgos2..cabecera_copia_abril2023

------------------------------------------------------------------------------------------------

-- debemos abrir este procedimiento y reemplazar el nombre de la tabla
-- para que funcione, deben estar en formato de fecha las siguientes columnas:
/*
> Fecha de Nacimiento 3/
> Fecha de Desembolso 21/
> Fecha de Vencimiento Origuinal del Credito 48/
> Fecha de Vencimiento Actual del Crédito 49/
*/

-- hay que modificar este procedimiento almacenado SIEMPRE
exec [Anexos_Riesgos2].[dbo].[SP_Cabecera] '20240630'  ---- en el corte de setiembre ha funcionado, sino hay que abrir y meterlo desde adentro uwu
exec [Anexos_Riesgos2].[dbo].[SP_HELPNRO_CABECERA] '20240630'
-------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------
if OBJECT_ID('TEMPDB..#T')IS NOT NULL 
DROP TABLE #T
select 
	a.NumerodeCredito18,
	Monedadelcredito17,
	a.NUEVO_PROMOTOR,
	a.PROMOTOR,
	a.NUEVA_PLANILLA,
	TIPO, 
	Nro_Fincore,
	ADMINISTRADOR, 
	TipodeProducto43,
	a.empresa
INTO #T
from Anexos_Riesgos2..Anx06_preliminar a 
where a.FechaCorte1 = '20240531' -- aqui se pone el de hace 2 meses

--codigo para eliminar si es que hay mes actual y salió mal
delete from Anexos_Riesgos2..Anx06_preliminar 
where FechaCorte1 = '20240630'--AQUI SE PONE EL MES PASADO

INSERT INTO Anexos_Riesgos2..Anx06_preliminar (
	   [FechaCorte1]
      ,[ApellidosyNombresRazonSocial2]
      ,[FechadeNacimiento3]
      ,[Genero4]
      ,[EstadoCivil5]
      ,[SigladelaEmpresa6]
      ,[CodigoSocio7]
      ,[PartidaRegistral8]
      ,[TipodeDocumento9]
      ,[NumerodeDocumento10]
      ,[TipodePersona11]
      ,[Domicilio12]
      ,[RelacionLaboralconlaCooperativa13]
      ,[ClasificaciondelDeudor14]
      ,[ClasificaciondelDeudorconAlineamiento15]
      ,[CodigodeAgencia16]
      ,[Monedadelcredito17]
      ,[NumerodeCredito18]
      ,[TipodeCredito19]
      ,[SubTipodeCredito20]
      ,[FechadeDesembolso21]
      ,[MontodeDesembolso22]
      ,[TasadeInteresAnual23]
      ,[Saldodecolocacionescreditosdirectos24]
      ,[CuentaContable25]
      ,[CapitalVigente26]
      ,[CapitalReestrucutado27]
      ,[CapitalRefinanciado28]
      ,[CapitalVencido29]
      ,[CapitalenCobranzaJudicial30]
      ,[CarteraAtrasada]
      ,[CapitalContingente31]
      ,[CuentaContableCapitalContingente32]
      ,[DiasdeMora33]
      ,[SaldosdeGarantiasPreferidas34]
      ,[SaldodeGarantiasAutoliquidables35]
      ,[ProvisionesRequeridas36]
      ,[ProvisionesConstituidas37]
      ,[SaldosdeCreditosCastigados38]
      ,[CuentaContableCreditoCastigado39]
      ,[Rendimiento_Devengado40]
      ,[InteresesenSuspenso41]
      ,[IngresosDiferidos42]
      ,[TipodeProducto43]
      ,[NumerodeCuotasProgramadas44]
      ,[NumerodeCuotasPagadas45]
      ,[Periodicidaddelacuota46]
      ,[PeriododeGracia47]
      ,[FechadeVencimientoOriguinaldelCredito48]
      ,[FechadeVencimientoAnualdelCredito49]
      ,[SITUAC]
      ,[FEC_SIT]
      ,[TIPO_afil]
      ,[AMORTIZA]
      ,[PROMOTOR]---------------------------
      ,[PLANILLA]
      ,[REGIMEN_LABORAL]
      ,[ESTADO]
      ,[CAMPAÑA]
      ,[EMPRESA]
      ,[IMPORTE_A_DESCONTAR]
      ,[IMPORTE_PAGADO]
      ,[Nro]
      ,[Reprogramados]
      ,[MDesembolsadoxM]
      ,[mora]
     -- ,[NUEVO_PROMOTOR]
      --,[Situacion_Credito]
      --,[TIPO]
	  ,Origen_Coopac
	  ,[Nro_Fincore]
	  ,Departamento
	  ,Provincia
	  ,Distrito
	  ,Reprogramados52
	  ,Refinanciado
	  ,nuevo_capitalvencido
	  ,originador
	  ,[Funcionario Actual]
	  ,[Nombre Negocio]
	  ,[Domicilio Negocio]
	  ,[Distrito Negocio]
	  ,[Dpto Negocio] 
	  ,[Provincia Negocio]
	  ,[PLANILLA_CONSOLIDADA]
	  ,[Fecha_castigo])
SELECT c.[FechaCorte1]
      ,c.[ApellidosyNombresRazonSocial2]
      ,c.[FechadeNacimiento3]
      ,c.[Genero4]
      ,c.[EstadoCivil5]
      ,c.[SigladelaEmpresa6]
      ,c.[CodigoSocio7]
      ,c.[PartidaRegistral8]
      ,c.[TipodeDocumento9]
      ,c.[NumerodeDocumento10]
      ,c.[TipodePersona11]
      ,c.[Domicilio12]
      ,c.[RelacionLaboralconlaCooperativa13]
      ,c.[ClasificaciondelDeudor14]
      ,c.[ClasificaciondelDeudorconAlineamiento15]
      ,c.[CodigodeAgencia16]
      ,c.[Monedadelcredito17]
      ,c.[NumerodeCredito18]
      ,c.[TipodeCredito19]
      ,c.[SubTipodeCredito20]
      ,c.[FechadeDesembolso21]
      ,c.[MontodeDesembolso22]
      ,c.[TasadeInteresAnual23]
      ,c.[Saldodecolocacionescreditosdirectos24]
      ,c.[CuentaContable25]
      ,c.[CapitalVigente26]
      ,c.[CapitalReestrucutado27]
      ,c.[CapitalRefinanciado28]
      ,c.[CapitalVencido29]
      ,c.[CapitalenCobranzaJudicial30]
      ,c.[CarteraAtrasada]
      ,c.[CapitalContingente31]
      ,c.[CuentaContableCapitalContingente32]
      ,c.[DiasdeMora33]
      ,c.[SaldosdeGarantiasPreferidas34]
      ,c.[SaldodeGarantiasAutoliquidables35]
      ,c.[ProvisionesRequeridas36]
      ,c.[ProvisionesConstituidas37]
      ,c.[SaldosdeCreditosCastigados38]
      ,c.[CuentaContableCreditoCastigado39]
      ,c.[Rendimiento_Devengado40]
      ,c.[InteresesenSuspenso41]
      ,c.[IngresosDiferidos42]
      ,c.[TipodeProducto43]
      ,c.[NumerodeCuotasProgramadas44]
      ,c.[NumerodeCuotasPagadas45]
      ,c.[Periodicidaddelacuota46]
      ,c.[PeriododeGracia47]
      ,c.[FechadeVencimientoOriguinaldelCredito48]
      ,c.[FechadeVencimientoAnualdelCredito49]
      ,c.[SITUAC]
      ,c.[FEC_SIT]
      ,c.[TIPO_afil]
      ,c.[AMORTIZA]
      ,c.[PROMOTOR]
      ,c.[PLANILLA]
      ,c.[REGIMEN_LABORAL]
      ,c.[ESTADO]
      ,c.[CAMPAÑA]
      ,c.[EMPRESA]
      ,c.[IMPORTE_A_DESCONTAR]
      ,c.[IMPORTE_PAGADO]
      ,c.[Nro]
      ,c.[Reprogramados]
      ,c.[MDesembolsadoxM]
      ,c.[mora]
	  ,c.Origen_Coopac
	  ,c.[Nro_Fincore]
	  ,c.Departamento
	  ,c.Provincia
	  ,c.Distrito
	  ,c.Reprogramados52
	  ,c.Refinanciado
	  ,c.[CapitalVencido29]
	  ,c.[Funcionario Originador]
	  ,c.[Funcionario Actual]
	  ,c.[Nombre Negocio]
	  ,c.[Domicilio Negocio]
	  ,c.[Distrito Negocio]
	  ,c.[Dpto Negocio] 
	  ,c.[Provincia Negocio]
	  ,C.[PLANILLA_CONSOLIDADA]
	  ,C.[Fecha_castigo] ---EXPERIMENTAL

  FROM [Anexos_Riesgos2]..[Cabecera] as c 
  LEFT JOIN Anexos_Riesgos2..Anx06_preliminar as a
   on (C.Nro_Fincore = A.Nro_Fincore 
		AND c.NumerodeCredito18 = a.NumerodeCredito18 
		and c.Monedadelcredito17 = a.Monedadelcredito17 
		and c.FechaCorte1 = a.FechaCorte1)
where c.FechaCorte1 = '20240630' and a.NumerodeCredito18 IS NULL ------SE PONE MES PASADO

----------------- EJECUTAR ANTES DEL PROCEDURE DE COSECHA ------------------------------------

IF OBJECT_ID('TEMPDB..#BASE1') IS NOT NULL 
DROP TABLE #BASE1
SELECT 
	NumerodeCredito18,Monedadelcredito17,
	NUEVO_PROMOTOR,Nro_Fincore,ADMINISTRADOR,TipodeProducto43, originador,
--TipodeProducto43,
--TipodeCredito19,
NUEVA_PLANILLA 
INTO #BASE1
FROM Anexos_Riesgos2..Anx06_preliminar WHERE FechaCorte1 = '20240531' --se pone el de hace 2 meses

/*
este es el código al que más hay que echarle el ojo, porque copia y pega los 
NUEVO_PROMOTOR, NUEVA_PLANILLA, ADMINISTRADOR, del mes pasado, para 'evitar' volver 
a hacer correcciones, el problema es que si está mal, sigue arrastrando errores mes a mes
*/

UPDATE A SET ---esto podría ser algo raro
A.NUEVO_PROMOTOR=B.NUEVO_PROMOTOR,
--A.TipodeProducto43=B.TipodeProducto43,
--A.TipodeCredito19=B.TipodeCredito19,
A.NUEVA_PLANILLA  = B.NUEVA_PLANILLA,
A.ADMINISTRADOR   = B.ADMINISTRADOR,
A.originador      = B.originador
--      SELECT A.NumerodeCredito18,A.Monedadelcredito17,A.PROMOTOR,A.NUEVO_PROMOTOR,B.NUEVO_PROMOTOR,a.TipodeProducto43,b.TipodeProducto43 
FROM Anexos_Riesgos2..Anx06_preliminar A 
JOIN #BASE1 B ON (A.Nro_Fincore = B.Nro_Fincore 
					AND A.NumerodeCredito18  =  B.NumerodeCredito18 
					AND A.Monedadelcredito17 =  B.Monedadelcredito17)
WHERE A.FechaCorte1 = '20240630' --- SE PONE EL MES PASADO

---------------------------------------------------------------------------------

update a
set a.NUEVA_PLANILLA='PEQUEÑA EMPRESA'
--			SELECT NRO_FINCORE, PLANILLA, NUEVA_PLANILLA,*
from Anexos_Riesgos2..Anx06_preliminar a
where FechaCorte1 = '20240630'
and TipodeProducto43 in (15,16,17,18,19)
and (PLANILLA not like '%pequeña%'
or NUEVA_PLANILLA not like '%pequeña%'
or NUEVA_PLANILLA not like '%independiente%'
or NUEVA_PLANILLA not like '%cooperativa%san%miguel%')

UPDATE A SET
A.NUEVO_PROMOTOR=A.PROMOTOR
--			SELECT PLANILLA,PROMOTOR,NUEVO_PROMOTOR  
FROM Anexos_Riesgos2..Anx06_preliminar A WHERE A.FechaCorte1='20240630' AND A.NUEVO_PROMOTOR is null
AND A.TipodeProducto43 IN (34,35,36,37,38,39) AND PROMOTOR LIKE '%PROSEVA%'

-------------------------------

UPDATE A SET
A.NUEVO_PROMOTOR = f.funcionario_fox 
--				SELECT a.PLANILLA,a.PROMOTOR,a.NUEVO_PROMOTOR,f.funcionario_fox  
FROM Anexos_Riesgos2..Anx06_preliminar as A 
JOIN [Anexos_Riesgos]..BASE_FUNCIONARIOS as F 
ON (A.PROMOTOR=F.Funcionaria_fincore)
WHERE A.FechaCorte1='20240630' AND A.NUEVO_PROMOTOR is null
AND A.TipodeProducto43 IN (34,35,36,37,38,39)

UPDATE A SET
A.NUEVO_PROMOTOR = f.CORRECION_FUNCIONARIOS 
--               SELECT a.PLANILLA,a.PROMOTOR,a.NUEVO_PROMOTOR,f.CORRECION_FUNCIONARIOS  
FROM Anexos_Riesgos2..Anx06_preliminar A 
JOIN [Anexos_Riesgos]..[Funcionarios_nombres_20220331] F 
ON (A.PROMOTOR=F.FUNCIONARIO)
WHERE A.FechaCorte1='20240630' AND A.NUEVO_PROMOTOR is null
AND A.TipodeProducto43 IN (34,35,36,37,38,39)

--select Nro_Fincore, ApellidosyNombresRazonSocial2, NUEVA_PLANILLA
--from Anexos_Riesgos2..Anx06_preliminar
--where FechaCorte1 = '20221031'
--and NUEVA_PLANILLA is null
--and TipodeProducto43 in (15,16,17,18, 19)

UPDATE A SET
A.administrador=f.CORRECION_FUNCIONARIOS 
--					SELECT a.PLANILLA,a.PROMOTOR,a.administrador,f.CORRECION_FUNCIONARIOS  
FROM Anexos_Riesgos2..Anx06_preliminar A JOIN [Anexos_Riesgos]..[Funcionarios_nombres_20220331] F 
ON (A.administrador=F.FUNCIONARIO)
WHERE A.FechaCorte1='20240630' 
AND A.NUEVO_PROMOTOR is null
AND A.TipodeProducto43 IN (34,35,36,37,38,39)

UPDATE A SET
A.NUEVO_PROMOTOR = A.PROMOTOR
--					SELECT a.PLANILLA,a.PROMOTOR,a.NUEVO_PROMOTOR 
FROM Anexos_Riesgos2..Anx06_preliminar A 
WHERE A.FechaCorte1='20240630' 
AND A.NUEVO_PROMOTOR IS NULL
AND A.TipodeProducto43 IN (34,35,36,37,38,39)

update A
set a.NUEVO_PROMOTOR =a.PROMOTOR
--					select a.nro_fincore, a.ApellidosyNombresRazonSocial2,a.TipodeProducto43, a.PROMOTOR, a.NUEVO_PROMOTOR,a.planilla, a.nueva_planilla 
from Anexos_Riesgos2..Anx06_preliminar a
where a.FechaCorte1='20240630'
and a.NUEVO_PROMOTOR is null

UPDATE A
SET A.NUEVO_PROMOTOR=f.CORRECION_FUNCIONARIOS 
--					SELECT a.PLANILLA,a.PROMOTOR,a.NUEVO_PROMOTOR,f.CORRECION_FUNCIONARIOS  
FROM Anexos_Riesgos2..Anx06_preliminar A 
JOIN [Anexos_Riesgos]..[Funcionarios_nombres_20220331] F 
ON (A.NUEVO_PROMOTOR=F.FUNCIONARIO)
WHERE A.FechaCorte1='20240630' 

update c set 
c.NUEVA_PLANILLA=C.PLANILLA
--c.planilla=t.planilla
--			select C.FechadeDesembolso21,c.PROMOTOR,c.PLANILLA,C.NUEVO_PROMOTOR,t.NUEVA_PLANILLA,C.PLANILLA,C.Saldodecolocacionescreditosdirectos24
from Anexos_Riesgos2..Anx06_preliminar c 
join #T t on (c.nro_fincore=t.nro_fincore and   c.NumerodeCredito18=t.NumerodeCredito18 and c.Monedadelcredito17=t.Monedadelcredito17)
where c.FechaCorte1='20240630' AND C.NUEVA_PLANILLA IS NULL AND C.TipodeProducto43 IN (34,35,36,37,38,39)

update c set 
c.NUEVA_PLANILLA=C.PLANILLA
--				select C.FechadeDesembolso21, C.NRO_FINCORE, c.ApellidosyNombresRazonSocial2, c.PROMOTOR,c.TipodeProducto43,C.NUEVO_PROMOTOR,C.Saldodecolocacionescreditosdirectos24 , C.PLANILLA , c.NUEVA_PLANILLA
from Anexos_Riesgos2..Anx06_preliminar c 
where c.FechaCorte1='20240630' AND C.NUEVA_PLANILLA IS NULL

update a
set a.NUEVA_PLANILLA='PEQUEÑA EMPRESA',
a.EMPRESA='PEQUEÑA EMPRESA',
a.PLANILLA='PEQUEÑA EMPRESA'
--				select Nro_Fincore,ApellidosyNombresRazonSocial2, MontodeDesembolso22, FechadeDesembolso21, TipodeProducto43, EMPRESA, PLANILLA, NUEVA_PLANILLA
from Anexos_Riesgos2..Anx06_preliminar a
where FechaCorte1='20240630'
and PLANILLA is null
and NUEVA_PLANILLA is null
and TipodeProducto43 in (15,16,17,18,19)

/************************************************SEGUIMOS************************************/
/****VIGENTE A TODO *****/
update c set
c.Situacion_Credito='VIGENTE'
--		select c.NUEVO_PROMOTOR,c.PROMOTOR,c.FechadeDesembolso21,c.Situacion_Credito,* 
from Anexos_Riesgos2..Anx06_preliminar c where C.FechaCorte1='20240630' 
--and c.TipodeProducto43 in (34,39) 
and c.Saldodecolocacionescreditosdirectos24>0 

/****VENCIDO****/
update c set
c.Situacion_Credito='VENCIDOS'
--select c.NUEVO_PROMOTOR,c.PROMOTOR,c.FechadeDesembolso21,c.Situacion_Credito,* 
from Anexos_Riesgos2..Anx06_preliminar c where C.FechaCorte1='20240630' 
--and c.TipodeProducto43 in (34,39) 
and c.Saldodecolocacionescreditosdirectos24>0 
AND isnull(c.CapitalVencido29,0)+isnull(c.CapitalenCobranzaJudicial30,0)>0


/***REFINANCIADOS**/
update c set
c.Situacion_Credito='REFINANCIADO'
--select c.NUEVO_PROMOTOR,c.PROMOTOR,c.FechadeDesembolso21,c.Situacion_Credito,* 
from Anexos_Riesgos2..Anx06_preliminar c where C.FechaCorte1='20240630' 
--and c.TipodeProducto43 in (34,39)
 and c.Saldodecolocacionescreditosdirectos24>0 AND isnull(c.CapitalRefinanciado28,0) > 0--ISNULL(C.TIPO_afil,'XX') LIKE '%REF%'

/******JUDICIAL******/
update c set
c.Situacion_Credito='JUDICIAL'
--select c.NUEVO_PROMOTOR,c.PROMOTOR,c.FechadeDesembolso21,c.Situacion_Credito,* 
from Anexos_Riesgos2..Anx06_preliminar c where C.FechaCorte1='20240630' 
--and c.TipodeProducto43 in (34,39)
 and c.Saldodecolocacionescreditosdirectos24>0 AND ISNULL(c.CapitalenCobranzaJudicial30,0) > 0--ISNULL(C.SITUAC,'XX') LIKE '%JU%'

/******CASTIGADO******/
update c set
c.Situacion_Credito='CASTIGADO'
--select c.NUEVO_PROMOTOR,c.PROMOTOR,c.FechadeDesembolso21,c.Situacion_Credito,* 
from Anexos_Riesgos2..Anx06_preliminar c where C.FechaCorte1='20240630' 
--and c.TipodeProducto43 in (34,39)
AND c.Situacion_Credito is null
and c.SaldosdeCreditosCastigados38>0

/**************AHORA EMPEZAMOS CON EL TIPO*************/

UPDATE C 
set c.TIPO = CASE 
			WHEN c.TIPO_afil LIKE '%NUEVO%' THEN 'NVO'
			WHEN c.TIPO_afil LIKE '%AMPLIACION%' THEN 'AMP' 
			WHEN c.TIPO_afil LIKE '%REFINANCIAMIENTO%' THEN 'REF'
			END 
from Anexos_Riesgos2..Anx06_preliminar c where C.FechaCorte1='20240630' 

/*ACTUALIZAR LA EMPRESA DE ANEXO06 DEL MES*/
update c
set C.EMPRESA=B.Empresa
--			select c.Empresa, B.empresa
from Anexos_Riesgos2..Anx06_preliminar C
LEFT JOIN  Anexos_Riesgos..planilla2 B
ON (C.NUEVA_PLANILLA=B.NUEVA_PLANILLA)
where c.FechaCorte1='20240630'
and c.Empresa is null

update a
set a.administrador = a.PROMOTOR -----a.nuevo_promotor
--		select *
from Anexos_Riesgos2..Anx06_preliminar a
where FechaCorte1 = '20240630'
and administrador is null


UPDATE A SET
A.administrador=f.CORRECION_FUNCIONARIOS 
--			SELECT a.PLANILLA,a.PROMOTOR,a.administrador,f.CORRECION_FUNCIONARIOS  
FROM Anexos_Riesgos2..Anx06_preliminar A JOIN [Anexos_Riesgos]..[Funcionarios_nombres_20220331] F 
ON (A.administrador=F.FUNCIONARIO)
WHERE A.FechaCorte1 ='20240630' 
AND A.NUEVO_PROMOTOR is null

--SELECT * FROM [Anexos_Riesgos]..[Funcionarios_nombres_20220331]

/*****FIN DE PROCESO*********/

--select nro_fincore, ApellidosyNombresRazonSocial2, MontodeDesembolso22, TipodeProducto43,PLANILLA,  FechadeDesembolso21, FechaCorte1
--from Anexos_Riesgos2..Anx06_preliminar
--where Nro_Fincore = '00079098'
--order by FechaCorte1

--select * from Anexos_Riesgos2..Anx06_preliminar
--where administrador is null
--and FechaCorte1 = '20220930'

update Anexos_Riesgos2..Anx06_preliminar set
administrador = 'PROSEVA CAÑETE',
nuevo_promotor = 'PROSEVA CAÑETE'
FROM Anexos_Riesgos2..Anx06_preliminar
WHERE FECHACORTE1 = '20240630'
AND ADMINISTRADOR LIKE '%CAÑETE%'

------------------------------------------------------------------------------------
---------------------CODIGO PARA ARREGLAR A PROSEVA CAÑETE
UPDATE A
SET A.administrador = 'PROSEVA CAÑETE',
A.NUEVO_PROMOTOR = 'PROSEVA CAÑETE'
FROM Anexos_Riesgos2..Anx06_preliminar AS  A -- AQUÍ VA LA TABLA
WHERE FechaCorte1 = '20240630'
AND ADMINISTRADOR LIKE '%CAÑETE%'

--------------------------------------------------------------------------------------

--buscando columnas en las que el administrador está vacío por razones misteriosas
select *,Nro_Fincore,TipodeProducto43,PROMOTOR,NUEVO_PROMOTOR,administrador 
from Anexos_Riesgos2..Anx06_preliminar 
where FechaCorte1 = '20240630'
and administrador is null

---------------------------------------------------------------------------------delete from Anexos_Riesgos2..Anx06_preliminar  where Nro_Fincore is null
--aqui relleno ese espacio duplicando lo que hay en nuevo promotor
UPDATE A
SET a.administrador = a.promotor --a.nuevo_promotor
from Anexos_Riesgos2..Anx06_preliminar a
where a.administrador is null
and FechaCorte1 = '20240630'

-----------------------------------------------------------------------------------
--codigo para añadir más originadores en caso de null
---CREANDO TABLA TEMPORAL Y AÑADIENDO EL ORIGINADOR DEL MES PASADO
--ESTO YA NO HACE FALTA
/*
if OBJECT_ID('TEMPDB..#TEMP_ORIGINADOR')IS NOT NULL 
DROP TABLE #TEMP_ORIGINADOR
SELECT Nro_Fincore, Originador, min(a.FechaCorte1) as 'fecha corte' 
FROM Anexos_Riesgos2..Anx06_preliminar as a
WHERE originador is not null
AND a.FechaCorte1 = '20240630' ----------------------AQUI SE PONE EL DE HACE 2 MESES
group by Nro_Fincore, originador

UPDATE A
SET A.ORIGINADOR = B.ORIGINADOR,
	A.ADMINISTRADOR = B.ADMINISTRADOR
FROM  Anexos_Riesgos2..Anx06_preliminar AS A
JOIN TEMPDB..#TEMP_ORIGINADOR AS B
ON (A.NRO_FINCORE = B.NRO_FINCORE)
WHERE A.FECHACORTE1  = '20240630'
*/
-----------------------------------------------------------------------------------

---------------------------------------------------------
---hora de llenar espacios en blanco en PLANILLA, NUEVA_PLANILLA, EMPRESA
select 
	empresa, planilla, NUEVA_PLANILLA,TipodeProducto43,MontodeDesembolso22,* 
from Anexos_Riesgos2..Anx06_preliminar
where FechaCorte1 = '20240630'
and (planilla is null
or NUEVA_PLANILLA is null
or empresa is null)

---------------------------------------------------------------------------MICRO
UPDATE Anexos_Riesgos2..Anx06_preliminar
SET EMPRESA = 'MICROEMPRESA'
where EMPRESA IS NULL
AND TipodeProducto43 IN (21,22,23,24,25,26,27,28,29)
UPDATE Anexos_Riesgos2..Anx06_preliminar
SET PLANILLA = 'MICROEMPRESA'
where PLANILLA IS NULL
AND TipodeProducto43 IN (21,22,23,24,25,26,27,28,29)
UPDATE Anexos_Riesgos2..Anx06_preliminar
SET NUEVA_PLANILLA = 'MICROEMPRESA'
where NUEVA_PLANILLA IS NULL
AND TipodeProducto43 IN (21,22,23,24,25,26,27,28,29)
--------------------------------------------------------------------------PEQUEÑA
UPDATE Anexos_Riesgos2..Anx06_preliminar
SET EMPRESA = 'PEQUEÑA EMPRESA'
where EMPRESA IS NULL
AND TipodeProducto43 IN (15,16,17,18,19)
UPDATE Anexos_Riesgos2..Anx06_preliminar
SET PLANILLA = 'PEQUEÑA EMPRESA'
where PLANILLA IS NULL
AND TipodeProducto43 IN (15,16,17,18,19)
UPDATE Anexos_Riesgos2..Anx06_preliminar
SET NUEVA_PLANILLA = 'PEQUEÑA EMPRESA'
where NUEVA_PLANILLA IS NULL
AND TipodeProducto43 IN (15,16,17,18,19)
--------------------------------------------------------------------------MEDIANA
UPDATE Anexos_Riesgos2..Anx06_preliminar
SET EMPRESA = 'MEDIANA EMPRESA'
where EMPRESA IS NULL
AND TipodeProducto43 IN (95,96,97,98,99)
UPDATE Anexos_Riesgos2..Anx06_preliminar
SET PLANILLA = 'MEDIANA EMPRESA'
where PLANILLA IS NULL
AND TipodeProducto43 IN (95,96,97,98,99)
UPDATE Anexos_Riesgos2..Anx06_preliminar
SET NUEVA_PLANILLA = 'MEDIANA EMPRESA'
where NUEVA_PLANILLA IS NULL
AND TipodeProducto43 IN (95,96,97,98,99)

----------------------------------------------------------------------------------
----------------------------------------------------------------------------------
update A ---------QUE ESTA PARTE ESTÉ EN PRUEBAS
set A.EMPRESA = B.EMPRESA
--      SELECT A.EMPRESA,A.PLANILLA,A.NUEVA_PLANILLA,A.PLANILLA_CONSOLIDADA, *
FROM anexos_riesgos2..Anx06_preliminar AS A
LEFT JOIN anexos_riesgos2..cabecera AS B
ON (A.Nro_Fincore = B.Nro_Fincore AND A.FechaCorte1 = B.FechaCorte1)
WHERE A.EMPRESA IS NULL
AND A.FechaCorte1 = '20240630'
AND B.FechaCorte1 = '20240630'
AND A.TipodeProducto43 IN (34,35,36,37,38,39)
------------------------------------------------------------------------------
update A ---------QUE ESTA PARTE ESTÉ EN PRUEBAS
set A.EMPRESA = B.EMPRESA
--      SELECT A.EMPRESA,A.PLANILLA,A.NUEVA_PLANILLA,A.PLANILLA_CONSOLIDADA, *
FROM anexos_riesgos2..Anx06_preliminar AS A
LEFT JOIN anexos_riesgos2..cabecera AS B
ON (A.Nro_Fincore = B.Nro_Fincore AND A.FechaCorte1 = B.FechaCorte1)
WHERE A.EMPRESA IS NULL
AND A.FechaCorte1 = '20240630'
AND B.FechaCorte1 = '20240630'
AND A.TipodeProducto43 IN (34,35,36,37,38,39)

----------------------------------------------------------------------------------
----------------------------------------------------------------------------------
--libres disponibilidad
update anexos_riesgos2..Anx06_preliminar
set EMPRESA = 'LIBRE DISPONIBILIDAD'
where EMPRESA is null
and FechaCorte1 = '20240630'
and TipodeProducto43 in (30,31,32,33)

update anexos_riesgos2..Anx06_preliminar
set PLANILLA = 'LIBRE DISPONIBILIDAD'
where PLANILLA is null
and FechaCorte1 = '20240630'
and TipodeProducto43 in (30,31,32,33)

update anexos_riesgos2..Anx06_preliminar
set NUEVA_PLANILLA = 'LIBRE DISPONIBILIDAD'
where NUEVA_PLANILLA is null
and FechaCorte1 = '20240630'
and TipodeProducto43 in (30,31,32,33)
----------------------------------------------------------------------------------

--para unificar los nombres de los funcionarios::::
--ajustes puntuales
/*
update A
SET A.administrador = B.[Funcionario Actual]
FROM anexos_riesgos2..Anx06_preliminar AS A
LEFT JOIN anexos_riesgos2..cabecera AS B
ON (A.Nro_Fincore = B.Nro_Fincore AND A.FechaCorte1 = B.FechaCorte1)
WHERE A.FechaCorte1 = '20240630'
AND B.FechaCorte1 = '20240630' 

update A
SET A.administrador = 'DAVID BORJA'
FROM anexos_riesgos2..Anx06_preliminar AS A
where a.FechaCorte1 >= '20240630'
and a.Nro_Fincore in ('00069753', '00068425')

update A
SET A.administrador = 'KATHERIN RAMOS'
FROM anexos_riesgos2..Anx06_preliminar AS A
where a.FechaCorte1 >= '20240630'
and a.Nro_Fincore in ('00070130', '00073904')

update A
SET A.administrador = 'EVELYN LOJA'
FROM anexos_riesgos2..Anx06_preliminar AS A
where a.FechaCorte1 >= '20240630'
and a.administrador = 'ALEXANDRE SALDAÑA LOPEZ'
*/

------------------------------------------------------
update anexos_riesgos2..Anx06_preliminar
set administrador = 'MIGUEL TITO'
where administrador like '%MIGUEL%TITO%'

update anexos_riesgos2..Anx06_preliminar
set administrador = 'ALICIA OVIEDO'
where administrador like '%ALICIA OVIEDO%VELAS%'

update anexos_riesgos2..Anx06_preliminar
set administrador = 'ANDREA BILBAO'
where administrador like '%ANDREA BILBAO BRICEÑO%'

update anexos_riesgos2..Anx06_preliminar
set administrador = 'GIOVANNA HERRERA'
where administrador like '%GIOVANNA HERRERA MATH%'

update anexos_riesgos2..Anx06_preliminar
set administrador = 'MARGIORY ELIAS'
where administrador like '%MARGIORY ELIAS BENAVIDES%'

update anexos_riesgos2..Anx06_preliminar
set administrador = 'DAVID BORJA'
where administrador like '%DAVID BORJA%'

update anexos_riesgos2..Anx06_preliminar
set administrador = 'JULY OLGA'
where administrador like '%JULY GARCIA ALCANTARA%'

update anexos_riesgos2..Anx06_preliminar
set administrador = 'FIGARI VEGA'
where administrador like '%FIGARI VEGA AYQUIPA%'

update anexos_riesgos2..Anx06_preliminar
set administrador = 'KATHERIN RAMOS'
where administrador like '%KATHERIN RAMOS CCAMA%'

update anexos_riesgos2..Anx06_preliminar
set administrador = 'ROSA MALDONADO'
where administrador like '%ROSA MALDONADO FIGUREOA%'

update anexos_riesgos2..Anx06_preliminar
set administrador = 'ROXANA QUISPE'
where administrador like '%ROXANA QUISPE CHAVEZ%'

update anexos_riesgos2..Anx06_preliminar
set administrador = 'JOSE SANCHEZ'
where administrador like '%JOSE SANCHEZ F%'

update anexos_riesgos2..Anx06_preliminar
set originador = 'MIGUEL TITO'
where originador like '%MIGUEL%TITO%'

update anexos_riesgos2..Anx06_preliminar
set administrador = 'VICTOR VARGAS'
where administrador like '%VICTOR%VARGAS%'

update anexos_riesgos2..Anx06_preliminar
set originador = 'VICTOR VARGAS'
where originador like '%VICTOR%VARGAS%'

update anexos_riesgos2..Anx06_preliminar
set administrador = 'SUSAN ROJAS'
where administrador like '%SUSAN%ROJAS%'

update anexos_riesgos2..Anx06_preliminar
set administrador = 'GUSTAVO PALLETE'
where administrador like '%GUSTAVO%PALLETE%ALFERANO%'

update anexos_riesgos2..Anx06_preliminar
set originador = 'GUSTAVO PALLETE'
where originador like '%GUSTAVO%PALLETE%ALFERANO%'

update anexos_riesgos2..Anx06_preliminar
set administrador = 'AZUCENA OCHOA'
where administrador like '%AZUCENA OCHOA TERRY%'

update anexos_riesgos2..Anx06_preliminar
set originador = 'AZUCENA OCHOA'
where originador like '%AZUCENA OCHOA TERRY%'

update anexos_riesgos2..Anx06_preliminar
set originador = 'SUSAN ROJAS'
where originador like '%SUSAN%ROJAS%'

update anexos_riesgos2..Anx06_preliminar
set administrador = 'ELBER ALVARADO'
where administrador like '%ELBER%ALVARADO%'

update anexos_riesgos2..Anx06_preliminar
set originador = 'ELBER ALVARADO'
where originador like '%ELBER%ALVARADO%'

update anexos_riesgos2..Anx06_preliminar
set originador = 'DAVID BORJA'
where originador like '%DAVID%BORJA%'

update anexos_riesgos2..Anx06_preliminar
set originador = 'ALICIA OVIEDO'
where originador like '%ALICIA OVIEDO VELASQUEZ%'

update anexos_riesgos2..Anx06_preliminar
set originador = 'ANDREA BILBAO'
where originador like '%ANDREA BILBAO BRICEÑO%'

update anexos_riesgos2..Anx06_preliminar
set originador = 'EVELYN LOJA'
where originador like '%EVELYN LOJA PINEDO%'

update anexos_riesgos2..Anx06_preliminar
set originador = 'FIGARI VEGA'
where originador like '%FIGARI VEGA AYQUIPA%'

update anexos_riesgos2..Anx06_preliminar
set originador = 'GIOVANNA HERRERA'
where originador like '%GIOVANNA HERRERA MATHEWS%'

update anexos_riesgos2..Anx06_preliminar
set originador = 'GUSTAVO PALLETE'
where originador like '%GUSTAVO PALLETE ALFERANO%'

update anexos_riesgos2..Anx06_preliminar
set originador = 'JERSON ALVA'
where originador like '%JERSON ALVA FARFAN%'

update anexos_riesgos2..Anx06_preliminar
set originador = 'JIMN MENDOZA'
where originador like '%JIMN MENDOZA%'

update anexos_riesgos2..Anx06_preliminar
set originador = 'JONATHAN ESTRADA'
where originador like '%JONATHAN ESTRADA%'

update anexos_riesgos2..Anx06_preliminar
set originador = 'JOSE SANCHEZ'
where originador like '%JOSE SANCHEZ FLORES%'

update anexos_riesgos2..Anx06_preliminar
set originador = 'KATHERIN RAMOS'
where originador like '%KATHERIN RAMOS CCAMA%'

update anexos_riesgos2..Anx06_preliminar
set originador = 'LUIS BUSTAMANTE'
where originador like '%LUIS ALBERTO BUSTAMANTE GONZALES%'

update anexos_riesgos2..Anx06_preliminar
set originador = 'MARGIORY ELIAS'
where originador like '%MARGIORY ELIAS BENAVIDES%'

update anexos_riesgos2..Anx06_preliminar
set originador = 'MILTON JUAREZ'
where originador like '%MILTON MERLYN JUAREZ HORNA%'

update anexos_riesgos2..Anx06_preliminar
set originador = 'ROSA MALDONADO'
where originador like '%ROSA MALDONADO FIGUREOA%'

update anexos_riesgos2..Anx06_preliminar
set originador = 'ROXANA QUISPE'
where originador like '%ROXANA QUISPE CHAVEZ%'

update anexos_riesgos2..Anx06_preliminar
set originador = 'JULY OLGA'
where originador like '%JULY GARCIA ALCANTARA%'

update anexos_riesgos2..Anx06_preliminar
set originador = 'JULY OLGA'
where originador like '%JULY GARCIA%'

update anexos_riesgos2..Anx06_preliminar
set originador = 'PROSEVA CAÑETE'
where originador like '%CAÑETE%'

update anexos_riesgos2..Anx06_preliminar
set originador = 'MARIBEL PUCHO'
where originador like '%MARIBEL PUCHO%'

update anexos_riesgos2..Anx06_preliminar
set administrador = 'MARIBEL PUCHO'
where administrador like '%MARIBEL PUCHO%'

update anexos_riesgos2..Anx06_preliminar
set originador = 'JHONY SALDAÑA'
where originador like '%JONY SALDAÑA%'

update anexos_riesgos2..Anx06_preliminar
set administrador = 'JHONY SALDAÑA'
where administrador like '%JONY SALDAÑA%'

update anexos_riesgos2..Anx06_preliminar
set originador = 'MARIA CRISTINA MARTINEZ'
where originador like '%MARIA CRISTINA MARTINEZ%'

update anexos_riesgos2..Anx06_preliminar
set administrador = 'MARIA CRISTINA MARTINEZ'
where administrador like '%MARIA CRISTINA MARTINEZ%'
