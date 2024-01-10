----------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------
-----------------------------ESTO SOLO AÑADE LA DATA QUE NO ES PROSEVA------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------
------TENER MUCHO CUIDADO AL EJECUTAR ESTOS CÓDIGO, SOLO SE PUEDE HACER UNA VEZ

/* -- CODIGO PARA AÑADIR COLUMNAS SI ES QUE HACE FALTA
ALTER TABLE reportes_diana..DIANA_REPORTE
ADD [FECHA_CORTE] DATETIME NULL
*/

-----------------------------------------------------------
--------PROCEDEMOS A INSERTAR TODOS MENOS PROSEVA----------SELECT * FROM reportes_diana..DXP_LD_nov23
-----------------------------------------------------------

DECLARE @FECHACORTE AS DATETIME
SET @FECHACORTE = '20231231'-------------------------------------------------------NO OLVIDAR PONER LA FECHA DEL MES


INSERT INTO reportes_diana..DIANA_REPORTE (
[FECHA_DESEMBOLSO],----check
[FUNCIONARIO],----check
[EMPRESA],
[CONDICION],
[MESES],
[AÑO],
[NOMBRE_SOCIO],
[DNI],
[MONTO_DESEMBOLSADO],
[META_CUENTAS], ----tendrá nulos
[META_MONTO], ------tendrá nulos
[OFICINA], --ACTUALMENTE NULL
[FECHA_REVISION], --también tendrá nulos
[ANALISTA], --------ese también
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

from reportes_diana..DXP_LD_dic23 as A
--where [ESTADO FINAL] = 'APROBADO'

----------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------
-----------------------------ESTO SÍ AÑADE LA DATA DE LAS PROSEVAS----------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------

DECLARE @FECHACORTE AS DATETIME
SET @FECHACORTE = '20231231'-------------------------------------------------------NO OLVIDAR PONER LA FECHA DEL MES

INSERT INTO reportes_diana..DIANA_REPORTE (
[FECHA_DESEMBOLSO],----check
[FUNCIONARIO],----check
[EMPRESA],
[CONDICION],
[MESES],
[AÑO],
[NOMBRE_SOCIO],
[DNI],
[MONTO_DESEMBOLSADO],
[META_CUENTAS], ----tendrá nulos
[META_MONTO], ------tendrá nulos
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
	WHEN [FUNCIONARIO/SEDE] LIKE '%CAÑETE%' THEN 'OFICINA INFORMATIVA'
	ELSE 'OTROS' END--OFICINA
,A.[FECHA DE REVISION]
,A.ANALISTA
,a.[EMPRESA]
,A.[EMPRESA] -------todo check hasta planilla
,0
,A.[ESTADO FINAL]
,A.[CANAL OFICINA]
,A.[PRODUCTO]
,@FECHACORTE

from reportes_diana.PROSEVAS.DIC23 as A
--where [estado final] = 'APROBADO'

--------------------------------------------------------------------
--- CODIGO PARA AÑADIR LOS MYPE
--- esto genera una ramificación de los reportes a partir de mayo del 2023
DECLARE @FECHACORTE AS DATETIME
SET @FECHACORTE = '20231231'-------------------------------------------------------NO OLVIDAR PONER LA FECHA DEL MES

INSERT INTO reportes_diana..DIANA_MYPE (
	[FECHA_DESEMBOLSO],----check
	[FUNCIONARIO],----check
	[EMPRESA],
	[CONDICION],
	[MESES],
	[AÑO],
	[NOMBRE_SOCIO],
	[DNI],
	[MONTO_DESEMBOLSADO],
	[META_CUENTAS], ----tendrá nulos
	[META_MONTO], ------tendrá nulos
	[OFICINA],
	[FECHA_REVISION], --también tendrá nulos
	[ANALISTA], --------ese también
	[EMPRESA2],
	[PLANILLA],
	[N_funcionario],
	[ESTADO FINAL],
	[CANAL OFICINA],
	[PRODUCTO],
	FECHA_CORTE
)
SELECT 
	a.[Fecha_Préstamo]
	,a.[Funcionario]
	,a.[Tipo]
	,a.[Categoria]
	,datename(month,a.[Fecha_Préstamo])
	,year(a.[Fecha_Préstamo])
	,A.[Socio]
	,A.[N° DNI]
	,A.[MONT]
	,NULL --META CUENTAS
	,NULL --META MONTO
	,A.[Canal] -- ANTERIORMENTE A.OFICINA
	,A.[Fecha_Préstamo]
	,A.Desembolsado --se refiere al analista de crédito
	,A.[Tipo]
	,A.[Tipo]
	,0
	,'APROBADO'	--A.[ESTADO FINAL]
	,A.[Canal]
	,'MYPE'
	,@FECHACORTE

from 
	reportes_diana.MYPE.[2023_12] as A
WHERE 
	Prooducto LIKE '%MULTIPRODUCTO%'
	AND ([Tipo ] LIKE '%MICRO%'
	OR [Tipo ] LIKE '%PEQUEÑA%')

