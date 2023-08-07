----------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------
-----------------------------ESTO SOLO A�ADE LA DATA QUE NO ES PROSEVA------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------
------TENER MUCHO CUIDADO AL EJECUTAR ESTOS C�DIGO, SOLO SE PUEDE HACER UNA VEZ

/* -- CODIGO PARA A�ADIR COLUMNAS SI ES QUE HACE FALTA
ALTER TABLE reportes_diana..DIANA_REPORTE
ADD [FECHA_CORTE] DATETIME NULL
*/

----C�DIGO PARA ASIGNAR FECHA A ESAS COLUMNAS,
--- SE TIENE QUE ARREGLAR LOS DATOS PORQUE DIANA ES COJUDA
update reportes_diana..DIANA_JULIO23
set [FECHA DE REVISION] = [FECHA DESEMBOLSO]
WHERE [FECHA DE REVISION] IS NULL
AND [FECHA DESEMBOLSO] IS NOT NULL

update reportes_diana..DIANA_JULIO23
set [FECHA DESEMBOLSO] = [FECHA DE REVISION]
WHERE [FECHA DESEMBOLSO] IS NULL
AND [FECHA DE REVISION] IS NOT NULL

--CON ESTO REVISAS LAS FECHAS
SELECT * FROM reportes_diana..DIANA_JULIO23
WHERE ([FECHA DE REVISION] IS NULL
OR [FECHA DESEMBOLSO] IS NULL
OR [FECHA DESEMBOLSO] IS NULL)

-----------------------------------------------------------
--------PROCEDEMOS A INSERTAR TODOS MENOS PROSEVA----------
-----------------------------------------------------------
DECLARE @FECHACORTE AS DATETIME
SET @FECHACORTE = '20230731'-------------------------------------------------------NO OLVIDAR PONER LA FECHA DEL MES


INSERT INTO reportes_diana..DIANA_REPORTE (
[FECHA_DESEMBOLSO],----check
[FUNCIONARIO],----check
[EMPRESA],
[CONDICION],
[MESES],
[A�O],
[NOMBRE_SOCIO],
[DNI],
[MONTO_DESEMBOLSADO],
[META_CUENTAS], ----tendr� nulos
[META_MONTO], ------tendr� nulos
[OFICINA], --ACTUALMENTE NULL
[FECHA_REVISION], --tambi�n tendr� nulos
[ANALISTA], --------ese tambi�n
[EMPRESA2],
[PLANILLA],
[N_funcionario],
[ESTADO FINAL],
[CANAL OFICINA],
[PRODUCTO],
FECHA_CORTE
)
SELECT 
a.[FECHA DESEMBOLSO]-----correcto
,a.[FUNCIONARIO/SEDE] -------correcto
,a.[EMPRESA] ------creo que si
,a.[CONDICION]------------correcto
,datename(month,a.[FECHA DESEMBOLSO])
,year(a.[FECHA DESEMBOLSO])
,A.[SOCIO] --AQUI VA EL NOMBRE DEL SOCIO
,A.[DOC (DNI/CE/RUC)]
,A.[MONTO  PRESTAMO]
,NULL --META CUENTAS
,NULL --META MONTO
,A.[CANAL OFICINA] -- ANTERIORMENTE A.OFICINA
,A.[FECHA DE REVISION]
,A.ANALISTA
,A.[EMPRESA]
,A.[EMPRESA] -------todo check hasta planilla
,0
,A.[ESTADO FINAL]
,A.[CANAL OFICINA]
,A.[PRODUCTO]
,@FECHACORTE

from reportes_diana..DIANA_JULIO23 as A
--where [ESTADO FINAL] = 'APROBADO'

----------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------
-----------------------------ESTO S� A�ADE LA DATA DE LAS PROSEVAS----------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------

DECLARE @FECHACORTE AS DATETIME
SET @FECHACORTE = '20230731'-------------------------------------------------------NO OLVIDAR PONER LA FECHA DEL MES

INSERT INTO reportes_diana..DIANA_REPORTE (
[FECHA_DESEMBOLSO],----check
[FUNCIONARIO],----check
[EMPRESA],
[CONDICION],
[MESES],
[A�O],
[NOMBRE_SOCIO],
[DNI],
[MONTO_DESEMBOLSADO],
[META_CUENTAS], ----tendr� nulos
[META_MONTO], ------tendr� nulos
[OFICINA],
[FECHA_REVISION], 
[ANALISTA], 
[EMPRESA2],
[PLANILLA],
[N_funcionario],
[ESTADO FINAL],
[CANAL OFICINA],
[PRODUCTO],
FECHA_CORTE
)
SELECT 
a.[FECHA DESEMBOLSO]-----correcto
,a.[FUNCIONARIO/SEDE] -------correcto
,a.[EMPRESA] ------creo que si
,a.[CONDICION]------------correcto
,datename(month,a.[FECHA DESEMBOLSO])
,year(a.[FECHA DESEMBOLSO])
,A.[SOCIO] --AQUI VA EL NOMBRE DEL SOCIO
,A.[DOC (DNI/CE/RUC)]
,A.[MONTO PRESTAMO]
,NULL
,NULL
,CASE
	WHEN [FUNCIONARIO/SEDE] LIKE '%PROSEVA%' THEN 'SALA PROSEVA'
	WHEN [FUNCIONARIO/SEDE] LIKE '%CA�ETE%' THEN 'OFICINA INFORMATIVA'
	ELSE 'OTROS' END--OFICINA
,A.[FECHA REVISION]
,A.ANALISTA
,a.[EMPRESA]
,A.[EMPRESA] -------todo check hasta planilla
,0
,A.[ESTADO FINAL]
,A.[CANAL OFICINA]
,A.[PRODUCTO]
,@FECHACORTE

from reportes_diana..prosevas_diana_JUL23 as A
--where [estado final] = 'APROBADO'
--and sede like '%piura%'

--------------------------------------------------------------------
--- CODIGO PARA A�ADIR LOS MYPE
--- esto genera una ramificaci�n de los reportes a partir de mayo del 2023
DECLARE @FECHACORTE AS DATETIME
SET @FECHACORTE = '20230731'-------------------------------------------------------NO OLVIDAR PONER LA FECHA DEL MES


INSERT INTO reportes_diana..DIANA_MYPE (
	[FECHA_DESEMBOLSO],----check
	[FUNCIONARIO],----check
	[EMPRESA],
	[CONDICION],
	[MESES],
	[A�O],
	[NOMBRE_SOCIO],
	[DNI],
	[MONTO_DESEMBOLSADO],
	[META_CUENTAS], ----tendr� nulos
	[META_MONTO], ------tendr� nulos
	[OFICINA],
	[FECHA_REVISION], --tambi�n tendr� nulos
	[ANALISTA], --------ese tambi�n
	[EMPRESA2],
	[PLANILLA],
	[N_funcionario],
	[ESTADO FINAL],
	[CANAL OFICINA],
	[PRODUCTO],
	FECHA_CORTE
)
SELECT 
	a.[Fecha_Pr�stamo]
	,a.[Funcionario]
	,a.[Tipo]
	,a.[Categoria]
	,datename(month,a.[Fecha_Pr�stamo])
	,year(a.[Fecha_Pr�stamo])
	,A.[Socio]
	,A.[N� DNI]
	,A.[MONTO]
	,NULL --META CUENTAS
	,NULL --META MONTO
	,A.[Canal] -- ANTERIORMENTE A.OFICINA
	,A.[Fecha_Pr�stamo]
	,A.Desembolsado --se refiere al analista de cr�dito
	,A.[Tipo]
	,A.[Tipo]
	,0
	,'APROBADO'	--A.[ESTADO FINAL]
	,A.[Canal]
	,'MYPE'
	,@FECHACORTE

from 
	reportes_diana.MYPE.[2023_JULIO] as A
WHERE 
	Prooducto LIKE '%MULTIPRODUCTO%'
	AND ([Tipo ] LIKE '%MICRO%'
	OR [Tipo ] LIKE '%PEQUE�A%')


