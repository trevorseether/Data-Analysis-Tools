
update top (1) reportes_diana..DIANA_REPORTE
set  META_CUENTAS = 12,
	 META_MONTO = 25000
----     select top 1 * from reportes_diana..DIANA_REPORTE
where FECHA_CORTE = '20230630'
and [ESTADO FINAL] = 'aprobado'
and funcionario like '%ZAIRA%ASCUE%'
----------------------------------------------------
-- LO MISMO PERO PARA MYPE
update top (1) reportes_diana..DIANA_MYPE
set  META_CUENTAS = 8,
	 META_MONTO = 60000
----     select top 1 * from reportes_diana..DIANA_MYPE
where FECHA_CORTE = '20230630'
and [ESTADO FINAL] = 'aprobado'
and funcionario like '%cesar%mer%'


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
('20230630', 'AMERICA CAMA', 'MICROEMPRESA', 'NO EXISTE',
'Junio', 
2023, 0, 8,50000, --estos son importantes, hay que cambiarlos según las metas
'MICROEMPRESA', 'MICROEMPRESA', 'APROBADO', 'MICROEMPRESA',
'MYPE', 'MICROEMPRESA', '20230630')
