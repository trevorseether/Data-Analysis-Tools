
-- INSERTAR METAS A DXP y LD
update top (1) reportes_diana..DIANA_REPORTE
set  META_CUENTAS = 80,
	 META_MONTO   = 320000
----     select top 1 * from reportes_diana..DIANA_REPORTE
where FECHA_CORTE = '20240229'
and [ESTADO FINAL] = 'aprobado'
and funcionario like '%PROSEVA%TUMBES%'

----------------------------------------------------
-- LO MISMO PERO PARA MYPE
update top (1) reportes_diana..DIANA_MYPE
set  META_CUENTAS = 10,
	 META_MONTO   = 80000
----     select top 1 * from reportes_diana..DIANA_MYPE
where FECHA_CORTE = '20240229'
and [ESTADO FINAL] = 'aprobado'
and funcionario like '%jessica%piscoy%'

---------------------------------------------------------------------------
----------------------------------------------------------------------------
-------------codigo para añadir filas vacías
-- EL WHERE DE MICRO PARA TENERLO DE REFERENCIA
where (oficina LIKE '%micro%' OR PRODUCTO LIKE 'MYPE')
AND FUNCIONARIO NOT LIKE '%GERENCIA%'
and CONDICION not like '%administrativo%'
AND [ESTADO FINAL] LIKE 'APROBADO'
AND FECHA_CORTE > '20210101'
select * from reportes_diana..DIANA_REPORTE
------------------------------------------------------------
insert into reportes_diana..DIANA_mype
(FECHA_DESEMBOLSO, FUNCIONARIO, EMPRESA, CONDICION,
MESES, AÑO, MONTO_DESEMBOLSADO, META_CUENTAS, META_MONTO,
EMPRESA2, PLANILLA, [ESTADO FINAL], [CANAL OFICINA],
PRODUCTO,OFICINA, FECHA_CORTE)
values
('20230731', 'AMERICA CAMA', 'MICROEMPRESA', 'NO EXISTE',
'Junio', 
2023, 0, 8,50000, --estos son importantes, hay que cambiarlos según las metas
'MICROEMPRESA', 'MICROEMPRESA', 'APROBADO', 'MICROEMPRESA',
'MYPE', 'MICROEMPRESA', '20230731')

------------------------------------------
--añadir fila falsa a DXP
-- where del reporte DXP
where 
--(PRODUCTO IS NULL OR 
PRODUCTO LIKE '%DxP%'
--)
AND ([ESTADO FINAL] IS NULL OR [ESTADO FINAL] = 'APROBADO')
AND FECHA_CORTE >= '20210101'
AND FUNCIONARIO NOT LIKE '%ADMINISTRATIVO%'
AND FUNCIONARIO NOT LIKE '%GERENCIA%'
AND FUNCIONARIO NOT LIKE '%GRUPO%SAN%MIGU%'

---------- PARA INSERTAR DATOS ---------------------------------
INSERT INTO reportes_diana..DIANA_REPORTE 
(FECHA_DESEMBOLSO,
FUNCIONARIO,
CONDICION,
MESES,
AÑO,
MONTO_DESEMBOLSADO,
META_CUENTAS,
META_MONTO,
OFICINA,
[ESTADO FINAL],
[CANAL OFICINA],
PRODUCTO,
FECHA_CORTE)
VALUES
('20240131',
'LUIS JUSTO',
'NO EXISTE',
'Enero',
2024,
0,
20,
90000,
'OFIC. MAGDALENA',
'APROBADO',
'OFIC. MAGDALENA',
'DxP',
'20240131')

--------------------------------------