----------CÓDIGO PARA ACTUALIZAR EL REPORTE DE ANABEL
-------ANABEL AGREGA DATOS DE MANERA INTERDIARIA A SU EXCEL
--https://docs.google.com/spreadsheets/d/1Y9HWMmZevH5wP6HdgqpCPV6a725_u5jqDZTPVHhtj2Q/edit#gid=0
--ESTE EXCEL LO DESCARGAMOS Y LO PROCESAMOS POR EL CÓDIGO DE PYTHON, 'código para procesar la data de anabel.py'
--porque al descargardo sale dañado, y no sube bien al sql, una vez procesado, guardarlo en formato .xls
--y subirlo
--select * from anabel_reportes..datos_20230221 ORDER BY [FFECHA ]
--SELECT * FROM ANABEL_REPORTES..LLAMADAS ORDER BY [FFECHA ]
----PRIMERO ELIMINAR LAS FECHAS ANTIGUAS
update anabel_reportes.JULIO.datos_20230725--------------------------------ESTO PODRÍA REQUERIR CAMBIOS CADA VEZ QUE SE ACTUALIZA
set [FECHA DESEMBOLSO] = NULL
WHERE [FECHA DESEMBOLSO] < '20010101'
----SEGUNDO UNIFICAR 'ERROR DE BASE', DE LA COLUMNA CONTACTO
update anabel_reportes.JULIO.datos_20230725--------------------------------ESTO PODRÍA REQUERIR CAMBIOS CADA VEZ QUE SE ACTUALIZA
SET CONTACTO = 'ERROR DE BASE'
WHERE CONTACTO LIKE '%ERROR%DE%BASE%'
----TERCERO PONER FALTA GESTIONAR, DONDE HAY NULLS DE LA COLUMNA CONTACTO
update anabel_reportes.JULIO.datos_20230725--------------------------------ESTO PODRÍA REQUERIR CAMBIOS CADA VEZ QUE SE ACTUALIZA
SET CONTACTO = 'FALTA GESTIONAR'
WHERE CONTACTO IS NULL
----cuarto UNIFICAR 'CONTACTADO' DE LA COLUMNA CONTACTO
update anabel_reportes.JULIO.datos_20230725--------------------------------ESTO PODRÍA REQUERIR CAMBIOS CADA VEZ QUE SE ACTUALIZA
SET CONTACTO = 'CONTACTADO'
WHERE CONTACTO LIKE '% CONTACTADO %'

----ELIMINANDO TODO
DELETE FROM ANABEL_REPORTES..LLAMADAS
----INSERTANDO LA NUEVA BASE
INSERT INTO ANABEL_REPORTES..LLAMADAS
SELECT * FROM anabel_reportes.JULIO.datos_20230725

--lo dejo porque podría estar mal los datos proximamente
/*
SELECT * FROM anabel_reportes.JULIO.datos_20230725
where [nombre socio] like '%MOGOLLON PALOMINO MARIO YOVANY%'

update anabel_reportes.JULIO.datos_20230725
set [fecha desembolso] = null
where [nombre socio] like '%MOGOLLON PALOMINO MARIO YOVANY%'
*/


------------------------------
-- creación de schema
------------------------------
/*
use ANABEL_REPORTES
go

create schema JULIO
*/
