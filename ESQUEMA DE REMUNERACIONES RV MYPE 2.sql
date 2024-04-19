/*-----------------------------------------------------------------------------
                               REMUNERACIONES MYPE
*/-----------------------------------------------------------------------------

-- Declarar la variable con la fecha inicial
DECLARE @fechacorte AS VARCHAR(8) = '20240331';

-- Obtener el �ltimo d�a del mes anterior
DECLARE @fechaAnterior AS DATETIME;
SET @fechaAnterior = EOMONTH(DATEADD(MONTH, -1, EOMONTH(CONVERT(DATETIME, @fechacorte, 112))));

DECLARE @fecha12MESES AS DATETIME;
SET @fecha12MESES = EOMONTH(DATEADD(MONTH, -11, EOMONTH(CONVERT(DATETIME, @fechacorte, 112))));

;

/*
-- COD PARA CREAR EL REPORTE CON LA COLUMNA ORIGINADOR CORREGIDA
--drop table ANEXOS_RIESGOS3..ANX06
--SELECT * 
--INTO ANEXOS_RIESGOS3..ANX06
--FROM ANEXOS_RIESGOS2..ANX06_PRELIMINAR

INSERT INTO ANEXOS_RIESGOS3..ANX06 
SELECT * FROM ANEXOS_RIESGOS2..ANX06_PRELIMINAR
WHERE FECHACORTE1 = '20240331'

UPDATE A
SET A.ORIGINADOR = B.FDN_DRIVE
FROM anexos_riesgos3..ANX06 AS A
INNER JOIN anexos_riesgos2..ORIGINADOR_ENERO_2023 AS B
ON A.NRO_FINCORE = B.NRO_FINCORE
*/

WITH 
ACTUAL AS (
    SELECT 
        ADMINISTRADOR, 
		ISNULL(SUM(Saldodecolocacionescreditosdirectos24),0) AS 'SALDO_CARTERA',
        ISNULL((SUM(Saldodecolocacionescreditosdirectos24) + SUM(0/*SaldosdeCreditosCastigados38*/)),0) AS 'SALDO_TOTAL',
		COUNT(Nro_Fincore) AS 'NRO_CRED_VIGENTES_ACTUAL',
		SUM(isnull(CapitalVencido29,0) + isnull(CapitalenCobranzaJudicial30,0) + isnull(0/*SaldosdeCreditosCastigados38*/,0)) AS 'VENCIDO_ACTUAL',
		(SUM(CapitalVencido29) + SUM(CapitalenCobranzaJudicial30) + isnull(SUM(0/*SaldosdeCreditosCastigados38*/),0)) / 
		SUM(ISNULL(Saldodecolocacionescreditosdirectos24,0) + isnull(0/*SaldosdeCreditosCastigados38*/,0)) AS 'MORA_ACTUAL'
		--SUM(TasadeInteresAnual23 * Saldodecolocacionescreditosdirectos24) /SUM(Saldodecolocacionescreditosdirectos24) AS TASA_INT
    FROM 
        ANEXOS_RIESGOS3..ANX06
    WHERE 
		FechaCorte1 = @fechacorte -------------------------------------------------fecha actual
		--and TipodeProducto43 in (15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33)
		and Saldodecolocacionescreditosdirectos24 > 0
    GROUP BY ADMINISTRADOR --ORDER BY originador
),
DEL_MES AS (
	SELECT 
		originador, 
		ISNULL(COUNT(Nro_Fincore),0)  AS N�MERO_DESEMBOLSOS,
		SUM(MontodeDesembolso22) AS MONTO_DESEMBOLSADO,
		SUM(TasadeInteresAnual23 * MontodeDesembolso22) / SUM(MontodeDesembolso22) AS TPPM
	FROM 
		ANEXOS_RIESGOS3..ANX06
	WHERE
		FechaCorte1 = @fechacorte -------------------------------------------------fecha actual
		AND FechaCorte1 = EOMONTH(FechadeDesembolso21)
		--AND TipodeProducto43 in (15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33)
	GROUP BY originador
),
ANTERIOR AS (   
				SELECT 
					ADMINISTRADOR, 
					COUNT(Nro_Fincore) AS 'NRO_CRED_VIGENTES_ANTERIOR',
					SUM(Saldodecolocacionescreditosdirectos24) 
					-- + SUM(SaldosdeCreditosCastigados38)
					AS SALDO_TOTAL_ANTERIOR,
						SUM(isnull(CapitalVencido29,0) + 
						isnull(CapitalenCobranzaJudicial30,0) + 
						isnull(0/*SaldosdeCreditosCastigados38*/,0)) 
						AS 'VENCIDO_ANTERIOR',
				(SUM(CapitalVencido29) + SUM(CapitalenCobranzaJudicial30) + isnull(SUM(0/*SaldosdeCreditosCastigados38*/),0)) / 
				SUM(ISNULL(Saldodecolocacionescreditosdirectos24,0) + isnull(0/*SaldosdeCreditosCastigados38*/,0)) AS 'MORA_ANTERIOR'

				FROM ANEXOS_RIESGOS3..ANX06
				WHERE FechaCorte1 = @fechaAnterior --------------------------------------------------------------FECHA CORTE ANTERIOR
				--AND TipodeProducto43 in (15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33)
				AND Saldodecolocacionescreditosdirectos24 > 0
				GROUP BY ADMINISTRADOR
				),

actual_distinct as (
	select 
		administrador, 
		count(distinct NumerodeDocumento10)  as NRO_SOCIOS_ACTUAL
	from anexos_riesgos3..anx06	
	where FechaCorte1 = @fechacorte -------------------------------------------------fecha actual
	--AND TipodeProducto43 IN (15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33)
	Group by administrador
	),
anterior_distinct as (
	select 
		ADMINISTRADOR, 
		count(distinct NumerodeDocumento10)  AS NRO_SOCIOS_ANTERIOR
	from anexos_riesgos3..anx06	
	where FechaCorte1 = @fechaAnterior --------------------------------------------------------------FECHA CORTE ANTERIOR
	--AND TipodeProducto43 in (15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33)
	group by ADMINISTRADOR
	),

ult_12_meses as 
(
select 
	originador, 
	(SUM(CapitalVencido29) + SUM(CapitalenCobranzaJudicial30) + SUM(0/*SaldosdeCreditosCastigados38*/)) / 
	SUM(Saldodecolocacionescreditosdirectos24 + SaldosdeCreditosCastigados38) AS MORA_12

from anexos_riesgos3..ANX06
where FechaCorte1 = @fechacorte -------------------------------------------------fecha actual
and DATEDIFF(MONTH, FechadeDesembolso21, FechaCorte1) < 12
and Saldodecolocacionescreditosdirectos24 > 0
AND TipodeProducto43 IN (15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33)

group by originador
),
CAIDAS AS (
SELECT 
    ORIGINADOR,
    SUM(CASE
        WHEN NumerodeCuotasPagadas45 = 0 THEN 1
        ELSE 0
    END) AS CERO_CUOTAS,

    SUM(CASE
        WHEN NumerodeCuotasPagadas45 = 1 THEN 1
        ELSE 0
    END) AS UNA_CUOTA,

    SUM(CASE
        WHEN NumerodeCuotasPagadas45 = 2 THEN 1
        ELSE 0
    END) AS DOS_CUOTAS,

    SUM(CASE
        WHEN NumerodeCuotasPagadas45 > 2 THEN 1
        ELSE 0
    END) AS MAYOR_DOS_CUOTAS

FROM anexos_riesgos3..ANX06
	WHERE FechaCorte1 = @fechacorte -------------------------------------------------fecha actual
	AND DATEDIFF(MONTH, FechadeDesembolso21, FechaCorte1) < 12
    AND (CapitalVencido29 > 0 OR CapitalenCobranzaJudicial30 > 0)
    AND TipodeProducto43 IN (15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33)
    AND NumerodeCuotasPagadas45 <= 2
GROUP BY ORIGINADOR


), 
nro_desembolsos as (

select 
	ADMINISTRADOR, 
	count(Nro_Fincore) as NRO_DESEMBOLSOS_12
from 
	anexos_riesgos3..ANX06
where 
	FechaCorte1 = EOMONTH(FechadeDesembolso21)
and 
	FechaCorte1 >= @fecha12MESES
AND 
	TipodeProducto43 IN (15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33)
group by 
	ADMINISTRADOR
)

SELECT 
    a.originador,
	ACTUAL.SALDO_CARTERA,
	/*
	CASE
		WHEN ACTUAL.SALDO_CARTERA <= 300000 AND AF.NIVEL = 'JUNIOR'		THEN 70000
		WHEN ACTUAL.SALDO_CARTERA <= 300000 AND AF.NIVEL = 'INTERMEDIO' THEN 80000
		WHEN (ACTUAL.SALDO_CARTERA BETWEEN 300000 AND 500000) AND (AF.NIVEL = 'JUNIOR')		THEN 85000
		WHEN (ACTUAL.SALDO_CARTERA BETWEEN 300000 AND 500000) AND (AF.NIVEL = 'INTERMEDIO') THEN 90000

		WHEN (ACTUAL.SALDO_CARTERA BETWEEN 500000 AND 800000) AND (AF.NIVEL = 'JUNIOR')			THEN 100000
		WHEN (ACTUAL.SALDO_CARTERA BETWEEN 500000 AND 800000) AND (AF.NIVEL = 'INTERMEDIO')		THEN 110000
		WHEN (ACTUAL.SALDO_CARTERA BETWEEN 500000 AND 800000) AND (AF.NIVEL = 'SENIOR')			THEN 120000

		WHEN (ACTUAL.SALDO_CARTERA BETWEEN 800000 AND 1000000) AND (AF.NIVEL = 'INTERMEDIO')		THEN 125000
		WHEN (ACTUAL.SALDO_CARTERA BETWEEN 800000 AND 1000000) AND (AF.NIVEL = 'SENIOR')			THEN 130000

		WHEN (ACTUAL.SALDO_CARTERA BETWEEN 1000000 AND 1200000) AND (AF.NIVEL = 'INTERMEDIO')		THEN 140000
		WHEN (ACTUAL.SALDO_CARTERA BETWEEN 1000000 AND 1200000) AND (AF.NIVEL = 'SENIOR')			THEN 145000

		WHEN (ACTUAL.SALDO_CARTERA BETWEEN 1200000 AND 1500000) AND (AF.NIVEL = 'SENIOR')			THEN 160000

		WHEN (ACTUAL.SALDO_CARTERA > 1500000) AND (AF.NIVEL = 'SENIOR')			THEN 180000

		END AS METAS_FUNCIONARIOS,*/
		---------
		metas.METAS_comercial as 'METAS_FUNCIONARIOS',
		---------
		--DEL_MES.MONTO_DESEMBOLSADO AS 'MONTO DESEMBOLSADO',
		metas.desembolsado_comercial AS 'MONTO DESEMBOLSADO',

		--CASE
		--WHEN metas.METAS_comercial > 0 THEN metas.desembolsado_comercial / metas.METAS_comercial
		--WHEN metas.METAS_comercial = 0 THEN 1
		--END AS 'FACTOR MONTO DESEMBOLSADO (FMD)',
		 CASE 
			WHEN metas.METAS_comercial = 0 THEN 0
		    ELSE metas.desembolsado_comercial / metas.METAS_comercial 
		 END AS 'FACTOR MONTO DESEMBOLSADO (FMD)',


    ACTUAL.SALDO_TOTAL,
	ANTERIOR.SALDO_TOTAL_ANTERIOR,
    ISNULL(ACTUAL.SALDO_TOTAL,0) - ISNULL(ANTERIOR.SALDO_TOTAL_ANTERIOR,0)  AS 'VARIACI�N SALDO',
	ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0)  AS 'N�MERO DE DESEMBOLSOS',
	--ACTUAL.NRO_CRED_VIGENTES_ACTUAL AS 'NRO VIGENTES ACTUAL',
	--ISNULL(ANTERIOR.NRO_CRED_VIGENTES_ANTERIOR,0)  AS 'NRO VIGENTES ANTERIOR',
	--ISNULL(ACTUAL.NRO_CRED_VIGENTES_ACTUAL,0) - ISNULL(ANTERIOR.NRO_CRED_VIGENTES_ANTERIOR,0) AS 'VARIACI�N CR�DITOS',
	ISNULL(actual_distinct.NRO_SOCIOS_ACTUAL,0) AS 'NRO SOCIOS ACTUAL',
	ISNULL(anterior_distinct.NRO_SOCIOS_ANTERIOR,0) AS 'NRO SOCIOS ANTERIOR',
	ISNULL(actual_distinct.NRO_SOCIOS_ACTUAL,0) - ISNULL(anterior_distinct.NRO_SOCIOS_ANTERIOR,0) AS 'VARIACI�N SOCIOS',
	CASE
		WHEN (ISNULL(actual_distinct.NRO_SOCIOS_ACTUAL,0) - ISNULL(anterior_distinct.NRO_SOCIOS_ANTERIOR,0)) <= -3 THEN 0.5
		WHEN (ISNULL(actual_distinct.NRO_SOCIOS_ACTUAL,0) - ISNULL(anterior_distinct.NRO_SOCIOS_ANTERIOR,0)) BETWEEN -2 AND -1  THEN 0.7
		WHEN (ISNULL(actual_distinct.NRO_SOCIOS_ACTUAL,0) - ISNULL(anterior_distinct.NRO_SOCIOS_ANTERIOR,0)) BETWEEN 0 AND 2    THEN 0.9
		WHEN (ISNULL(actual_distinct.NRO_SOCIOS_ACTUAL,0) - ISNULL(anterior_distinct.NRO_SOCIOS_ANTERIOR,0)) BETWEEN 3 AND 5    THEN 1
		WHEN (ISNULL(actual_distinct.NRO_SOCIOS_ACTUAL,0) - ISNULL(anterior_distinct.NRO_SOCIOS_ANTERIOR,0)) BETWEEN 6 AND 8    THEN 1.1
		WHEN (ISNULL(actual_distinct.NRO_SOCIOS_ACTUAL,0) - ISNULL(anterior_distinct.NRO_SOCIOS_ANTERIOR,0)) BETWEEN 9 AND 11   THEN 1.2
		WHEN (ISNULL(actual_distinct.NRO_SOCIOS_ACTUAL,0) - ISNULL(anterior_distinct.NRO_SOCIOS_ANTERIOR,0)) >= 12   THEN 1.3
		ELSE 'REVISAR CASO'
		END AS 'FACTOR CRECIMIENTO DE SOCIOS (FCS)',
	ISNULL(ACTUAL.VENCIDO_ACTUAL,0) AS 'VENCIDO ACTUAL',
	ISNULL(ANTERIOR.VENCIDO_ANTERIOR,0) AS 'VENCIDO ANTERIOR',
	CASE
		when ACTUAL.SALDO_TOTAL = 0 then 0
		else (ISNULL(ACTUAL.VENCIDO_ACTUAL,0) - ISNULL(ANTERIOR.VENCIDO_ANTERIOR,0))/NULLIF(ACTUAL.SALDO_TOTAL,0)
		end as 'VAR VENCIDO',

		--ACTUAL.SALDO_TOTAL,
		--((ISNULL(ACTUAL.VENCIDO_ACTUAL,0) - ISNULL(ANTERIOR.VENCIDO_ANTERIOR,0))/ACTUAL.SALDO_TOTAL),

	CASE
		when ACTUAL.SALDO_TOTAL = 0 then 0
		when ((ISNULL(ACTUAL.VENCIDO_ACTUAL,0) - ISNULL(ANTERIOR.VENCIDO_ANTERIOR,0))/ACTUAL.SALDO_TOTAL) > 0.02					then 0.5
		when ((ISNULL(ACTUAL.VENCIDO_ACTUAL,0) - ISNULL(ANTERIOR.VENCIDO_ANTERIOR,0))/ACTUAL.SALDO_TOTAL) between 0.01 AND 0.01999  then 0.6
		when ((ISNULL(ACTUAL.VENCIDO_ACTUAL,0) - ISNULL(ANTERIOR.VENCIDO_ANTERIOR,0))/ACTUAL.SALDO_TOTAL) between 0    AND 0.003	 then 1

		WHEN ACTUAL.SALDO_TOTAL < 500000 AND
		((ISNULL(ACTUAL.VENCIDO_ACTUAL,0) - ISNULL(ANTERIOR.VENCIDO_ANTERIOR,0))/ACTUAL.SALDO_TOTAL) BETWEEN 0.006 AND 0.01	then 0.7
		WHEN ACTUAL.SALDO_TOTAL >= 500000 AND
		((ISNULL(ACTUAL.VENCIDO_ACTUAL,0) - ISNULL(ANTERIOR.VENCIDO_ANTERIOR,0))/ACTUAL.SALDO_TOTAL) BETWEEN 0.006 AND 0.01	then 0.8

		WHEN ACTUAL.SALDO_TOTAL < 500000 AND
		((ISNULL(ACTUAL.VENCIDO_ACTUAL,0) - ISNULL(ANTERIOR.VENCIDO_ANTERIOR,0))/ACTUAL.SALDO_TOTAL) BETWEEN 0.003 AND 0.006  then 0.8
		WHEN ACTUAL.SALDO_TOTAL >= 500000 AND
		((ISNULL(ACTUAL.VENCIDO_ACTUAL,0) - ISNULL(ANTERIOR.VENCIDO_ANTERIOR,0))/ACTUAL.SALDO_TOTAL) BETWEEN 0.003 AND 0.006  then 0.9

		WHEN ACTUAL.SALDO_TOTAL < 500000 AND
		((ISNULL(ACTUAL.VENCIDO_ACTUAL,0) - ISNULL(ANTERIOR.VENCIDO_ANTERIOR,0))/ACTUAL.SALDO_TOTAL) BETWEEN -0.005 AND 0 then 1
		WHEN ACTUAL.SALDO_TOTAL >= 500000 AND
		((ISNULL(ACTUAL.VENCIDO_ACTUAL,0) - ISNULL(ANTERIOR.VENCIDO_ANTERIOR,0))/ACTUAL.SALDO_TOTAL) BETWEEN -0.005 AND 0 then 1.05

		WHEN ACTUAL.SALDO_TOTAL < 500000 AND
		((ISNULL(ACTUAL.VENCIDO_ACTUAL,0) - ISNULL(ANTERIOR.VENCIDO_ANTERIOR,0))/ACTUAL.SALDO_TOTAL) BETWEEN -0.01 AND -0.005 then 1.05
		WHEN ACTUAL.SALDO_TOTAL >= 500000 AND
		((ISNULL(ACTUAL.VENCIDO_ACTUAL,0) - ISNULL(ANTERIOR.VENCIDO_ANTERIOR,0))/ACTUAL.SALDO_TOTAL) BETWEEN -0.01 AND -0.005 then 1.10

		WHEN ACTUAL.SALDO_TOTAL < 500000 AND
		((ISNULL(ACTUAL.VENCIDO_ACTUAL,0) - ISNULL(ANTERIOR.VENCIDO_ANTERIOR,0))/ACTUAL.SALDO_TOTAL) < -0.01 then 1.1
		WHEN ACTUAL.SALDO_TOTAL >= 500000 AND
		((ISNULL(ACTUAL.VENCIDO_ACTUAL,0) - ISNULL(ANTERIOR.VENCIDO_ANTERIOR,0))/ACTUAL.SALDO_TOTAL) < -0.01 then 1.15
		END AS 'FACTOR DETERIORO DE CARTERA (FDC)',

	ACTUAL.MORA_ACTUAL AS 'MORA ACTUAL',
	ANTERIOR.MORA_ANTERIOR AS 'MORA ANTERIOR',
	ACTUAL.MORA_ACTUAL - ANTERIOR.MORA_ANTERIOR AS 'VAR MORA',
	AF.ACTIVIDAD, AF.NIVEL, AF.SEGMENTO,
	DATEDIFF(MONTH, AF.FECHA_INICIO, @fechacorte) AS 'ANTIGUEDAD MESES',
	ult_12_meses.MORA_12 as 'MORA 12 MESES',
	CASE 
		WHEN ult_12_meses.MORA_12 > 0.05 THEN 'SIN RV'
		WHEN (DATEDIFF(MONTH, AF.FECHA_INICIO, @fechacorte) <= 3) AND ult_12_meses.MORA_12 > 0 THEN 'SIN RV'
		WHEN metas.METAS_comercial = 0 THEN 'SIN RV'
		WHEN metas.desembolsado_comercial / metas.METAS_comercial < 0.8 THEN 'SIN RV'
		ELSE 'RV'
		END AS 'CORRESPONDE RV',
	CASE
		WHEN (DATEDIFF(MONTH, AF.FECHA_INICIO, @fechacorte) <= 3) AND (ult_12_meses.MORA_12 = 0) THEN 1
		WHEN (DATEDIFF(MONTH, AF.FECHA_INICIO, @fechacorte) <= 3) AND (ult_12_meses.MORA_12 > 0) THEN 0
		WHEN (DATEDIFF(MONTH, AF.FECHA_INICIO, @fechacorte) BETWEEN  4 AND 6)  AND (ult_12_meses.MORA_12 BETWEEN 0 AND 0.005  ) THEN 1.1
		WHEN (DATEDIFF(MONTH, AF.FECHA_INICIO, @fechacorte) BETWEEN  7 AND 10) AND (ult_12_meses.MORA_12 BETWEEN 0 AND 0.015  ) THEN 1.1
		WHEN (DATEDIFF(MONTH, AF.FECHA_INICIO, @fechacorte) >= 11)             AND (ult_12_meses.MORA_12 BETWEEN 0 AND 0.029  ) THEN 1.1

		WHEN (DATEDIFF(MONTH, AF.FECHA_INICIO, @fechacorte) BETWEEN  4 AND 6)  AND (ult_12_meses.MORA_12 BETWEEN 0.005 AND 0.01 ) THEN 1
		WHEN (DATEDIFF(MONTH, AF.FECHA_INICIO, @fechacorte) BETWEEN  7 AND 10) AND (ult_12_meses.MORA_12 BETWEEN 0.015 AND 0.02 ) THEN 1
		WHEN (DATEDIFF(MONTH, AF.FECHA_INICIO, @fechacorte) >= 11)             AND (ult_12_meses.MORA_12 BETWEEN 0.03  AND 0.035) THEN 1

		WHEN (DATEDIFF(MONTH, AF.FECHA_INICIO, @fechacorte) BETWEEN  4 AND 6)  AND (ult_12_meses.MORA_12 BETWEEN 0.01 AND 0.015) THEN 0.8
		WHEN (DATEDIFF(MONTH, AF.FECHA_INICIO, @fechacorte) BETWEEN  7 AND 10) AND (ult_12_meses.MORA_12 BETWEEN 0.02 AND 0.025) THEN 0.8
		WHEN (DATEDIFF(MONTH, AF.FECHA_INICIO, @fechacorte) >= 11)             AND (ult_12_meses.MORA_12 BETWEEN 0.035 AND 0.04) THEN 0.8

		WHEN (DATEDIFF(MONTH, AF.FECHA_INICIO, @fechacorte) BETWEEN  4 AND 6)  AND (ult_12_meses.MORA_12 BETWEEN 0.015 AND 0.02) THEN 0.5
		WHEN (DATEDIFF(MONTH, AF.FECHA_INICIO, @fechacorte) BETWEEN  7 AND 10) AND (ult_12_meses.MORA_12 BETWEEN 0.025 AND 0.03) THEN 0.5
		WHEN (DATEDIFF(MONTH, AF.FECHA_INICIO, @fechacorte) >= 11)             AND (ult_12_meses.MORA_12 BETWEEN 0.04  AND 0.05) THEN 0.5

		WHEN (DATEDIFF(MONTH, AF.FECHA_INICIO, @fechacorte) BETWEEN  4 AND 6)  AND (ult_12_meses.MORA_12 > 0.02) THEN 0
		WHEN (DATEDIFF(MONTH, AF.FECHA_INICIO, @fechacorte) BETWEEN  7 AND 10) AND (ult_12_meses.MORA_12 > 0.03) THEN 0
		WHEN (DATEDIFF(MONTH, AF.FECHA_INICIO, @fechacorte) >= 11)             AND (ult_12_meses.MORA_12 > 0.05) THEN 0
		
		ELSE 'INVESTIGAR'
			END AS 'FACTOR MORA PROPIA (FMP) ANTIGUEDAD Y MOROSIDAD 12 MESES',
	--MORA DE LOS �LTIMOS 12 MESES,
	--FALLIDO 1,
	--FALLIDO 2,
	--FALLIDO 3,
	DEL_MES.TPPM AS 'TPP DEL MES', 
	--ACTUAL.TASA_INT AS 'TASA ANUAL PROMEDIO'
	CAIDAS.CERO_CUOTAS, 
	CAIDAS.UNA_CUOTA, 
	CAIDAS.DOS_CUOTAS, 
	nro_desembolsos.NRO_DESEMBOLSOS_12 as 'NRO DESEMBOLSOSO 12 MESES',
	(ISNULL(CAIDAS.CERO_CUOTAS,0.0)  + ISNULL(CAIDAS.UNA_CUOTA,0.0)  + ISNULL(CAIDAS.DOS_CUOTAS,0.0)) / CAST(nro_desembolsos.NRO_DESEMBOLSOS_12 AS DECIMAL(10, 2))
	AS 'PROPORCI�N DE FALLIDOS',
	CASE
		WHEN (ISNULL(CAIDAS.CERO_CUOTAS,0.0)  + ISNULL(CAIDAS.UNA_CUOTA,0.0)  + ISNULL(CAIDAS.DOS_CUOTAS,0.0)) / CAST(nro_desembolsos.NRO_DESEMBOLSOS_12 AS DECIMAL(10, 2)) <= 0.01 THEN 1.1
		WHEN (ISNULL(CAIDAS.CERO_CUOTAS,0.0)  + ISNULL(CAIDAS.UNA_CUOTA,0.0)  + ISNULL(CAIDAS.DOS_CUOTAS,0.0)) / CAST(nro_desembolsos.NRO_DESEMBOLSOS_12 AS DECIMAL(10, 2)) BETWEEN 0.01 AND 0.025 THEN 1
		WHEN (ISNULL(CAIDAS.CERO_CUOTAS,0.0)  + ISNULL(CAIDAS.UNA_CUOTA,0.0)  + ISNULL(CAIDAS.DOS_CUOTAS,0.0)) / CAST(nro_desembolsos.NRO_DESEMBOLSOS_12 AS DECIMAL(10, 2)) BETWEEN 0.025 AND 0.03 THEN 0.8
		WHEN (ISNULL(CAIDAS.CERO_CUOTAS,0.0)  + ISNULL(CAIDAS.UNA_CUOTA,0.0)  + ISNULL(CAIDAS.DOS_CUOTAS,0.0)) / CAST(nro_desembolsos.NRO_DESEMBOLSOS_12 AS DECIMAL(10, 2)) BETWEEN 0.03 AND 0.05 THEN 0.7
		WHEN (ISNULL(CAIDAS.CERO_CUOTAS,0.0)  + ISNULL(CAIDAS.UNA_CUOTA,0.0)  + ISNULL(CAIDAS.DOS_CUOTAS,0.0)) / CAST(nro_desembolsos.NRO_DESEMBOLSOS_12 AS DECIMAL(10, 2)) > 0.05 THEN 0.5
	END AS 'FACTOR FALLIDOS (FF)'
	,
	CASE
		WHEN metas.METAS_comercial = 0 THEN 0
		WHEN metas.desembolsado_comercial / metas.METAS_comercial < 0.8 AND metas.METAS_comercial > 0 THEN 0
		WHEN ult_12_meses.MORA_12 > 0.05                                                              THEN 0
		WHEN (DATEDIFF(MONTH, AF.FECHA_INICIO, @fechacorte) <= 3) AND ult_12_meses.MORA_12 > 0        THEN 0
		WHEN ((DEL_MES.TPPM <= 0.30) AND (DEL_MES.TPPM > 0.28)) AND (ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0) BETWEEN 7 AND 10) THEN 500
		WHEN ((DEL_MES.TPPM <= 0.34) AND (DEL_MES.TPPM > 0.30)) AND (ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0) BETWEEN 7 AND 10) THEN 600
		WHEN ((DEL_MES.TPPM <= 0.37) AND (DEL_MES.TPPM > 0.34)) AND (ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0) BETWEEN 7 AND 10) THEN 700
		WHEN ((DEL_MES.TPPM <= 0.41) AND (DEL_MES.TPPM > 0.37)) AND (ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0) BETWEEN 7 AND 10) THEN 900
		WHEN ((DEL_MES.TPPM <= 0.45) AND (DEL_MES.TPPM > 0.41)) AND (ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0) BETWEEN 7 AND 10) THEN 1100
		WHEN ((DEL_MES.TPPM > 0.45)) AND (ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0) BETWEEN 7 AND 10) THEN 1300

		WHEN ((DEL_MES.TPPM <= 0.30) AND (DEL_MES.TPPM > 0.28)) AND (ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0) BETWEEN 11 AND 13) THEN 600
		WHEN ((DEL_MES.TPPM <= 0.34) AND (DEL_MES.TPPM > 0.30)) AND (ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0) BETWEEN 11 AND 13) THEN 800
		WHEN ((DEL_MES.TPPM <= 0.37) AND (DEL_MES.TPPM > 0.34)) AND (ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0) BETWEEN 11 AND 13) THEN 1000
		WHEN ((DEL_MES.TPPM <= 0.41) AND (DEL_MES.TPPM > 0.37)) AND (ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0) BETWEEN 11 AND 13) THEN 1200
		WHEN ((DEL_MES.TPPM <= 0.45) AND (DEL_MES.TPPM > 0.41)) AND (ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0) BETWEEN 11 AND 13) THEN 1400
		WHEN ((DEL_MES.TPPM > 0.45)) AND (ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0) BETWEEN 11 AND 13) THEN 1600

		WHEN ((DEL_MES.TPPM <= 0.30) AND (DEL_MES.TPPM > 0.28)) AND (ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0) BETWEEN 14 AND 16) THEN 900
		WHEN ((DEL_MES.TPPM <= 0.34) AND (DEL_MES.TPPM > 0.30)) AND (ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0) BETWEEN 14 AND 16) THEN 1100
		WHEN ((DEL_MES.TPPM <= 0.37) AND (DEL_MES.TPPM > 0.34)) AND (ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0) BETWEEN 14 AND 16) THEN 1300
		WHEN ((DEL_MES.TPPM <= 0.41) AND (DEL_MES.TPPM > 0.37)) AND (ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0) BETWEEN 14 AND 16) THEN 1500
		WHEN ((DEL_MES.TPPM <= 0.45) AND (DEL_MES.TPPM > 0.41)) AND (ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0) BETWEEN 14 AND 16) THEN 1700
		WHEN ((DEL_MES.TPPM > 0.45)) AND (ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0) BETWEEN 14 AND 16) THEN 1900
		
		WHEN ((DEL_MES.TPPM <= 0.30) AND (DEL_MES.TPPM > 0.28)) AND (ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0) BETWEEN 17 AND 19) THEN 1200
		WHEN ((DEL_MES.TPPM <= 0.34) AND (DEL_MES.TPPM > 0.30)) AND (ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0) BETWEEN 17 AND 19) THEN 1400
		WHEN ((DEL_MES.TPPM <= 0.37) AND (DEL_MES.TPPM > 0.34)) AND (ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0) BETWEEN 17 AND 19) THEN 1600
		WHEN ((DEL_MES.TPPM <= 0.41) AND (DEL_MES.TPPM > 0.37)) AND (ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0) BETWEEN 17 AND 19) THEN 1800
		WHEN ((DEL_MES.TPPM <= 0.45) AND (DEL_MES.TPPM > 0.41)) AND (ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0) BETWEEN 17 AND 19) THEN 2000
		WHEN ((DEL_MES.TPPM > 0.45)) AND (ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0) BETWEEN 17 AND 19) THEN 2200

		WHEN ((DEL_MES.TPPM <= 0.30) AND (DEL_MES.TPPM > 0.28)) AND (ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0) >= 20) THEN 1500
		WHEN ((DEL_MES.TPPM <= 0.34) AND (DEL_MES.TPPM > 0.30)) AND (ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0) >= 20) THEN 1700
		WHEN ((DEL_MES.TPPM <= 0.37) AND (DEL_MES.TPPM > 0.34)) AND (ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0) >= 20) THEN 1900
		WHEN ((DEL_MES.TPPM <= 0.41) AND (DEL_MES.TPPM > 0.37)) AND (ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0) >= 20) THEN 2100
		WHEN ((DEL_MES.TPPM <= 0.45) AND (DEL_MES.TPPM > 0.41)) AND (ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0) >= 20) THEN 2300
		WHEN ((DEL_MES.TPPM > 0.45)) AND (ISNULL(DEL_MES.N�MERO_DESEMBOLSOS,0) >= 20) THEN 2500
			ELSE 0
			END AS 'BASE FUNCIONARIO' 

FROM 
	ANEXOS_RIESGOS3..ANX06 AS A
	LEFT JOIN ACTUAL ON A.originador    = ACTUAL.ADMINISTRADOR--------------- ACTUAL.ORIGINADOR
	LEFT JOIN DEL_MES ON A.originador	= DEL_MES.originador
	LEFT JOIN ANTERIOR ON A.originador	= ANTERIOR.ADMINISTRADOR ------------ ANTERIOR.ORIGINADOR
	LEFT JOIN FUNCIONARIOS..FUNCIONARIOS_ACTIVIDAD as AF 
			on a.originador = AF.FUNCIONARIO

	LEFT JOIN actual_distinct ON A.ORIGINADOR    = actual_distinct.administrador ---actual_distinct.originador
	LEFT JOIN anterior_distinct ON A.ORIGINADOR  = ANTERIOR_distinct.administrador ----ANTERIOR_distinct.ORIGINADOR
	LEFT JOIN ult_12_meses ON A.originador = ult_12_meses.originador
	LEFT JOIN CAIDAS ON A.originador = CAIDAS.originador
	LEFT JOIN nro_desembolsos ON A.originador = nro_desembolsos.ADMINISTRADOR

	------------------------------------------------------------------------------------------
	LEFT JOIN FUNCIONARIOS.[dbo].[METAS_20240331] AS METAS ON A.originador = METAS.FUNCIONARIO
	------------------------------------------------------------------------------------------
WHERE a.FechaCorte1 = @fechacorte -------------------------------------------------fecha actual
	and Saldodecolocacionescreditosdirectos24 > 0
	
	/*AND (A.ORIGINADOR IN (		SELECT DISTINCT ORIGINADOR FROM anexos_riesgos3..ANX06
								WHERE FechaCorte1 = @fechacorte
								AND TipodeProducto43 IN (15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,32)   )
		OR A.administrador IN (		SELECT DISTINCT ORIGINADOR FROM anexos_riesgos3..ANX06
									WHERE FechaCorte1 = @fechacorte
									AND TipodeProducto43 IN (15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,32)   )
		)  */
	AND TipodeProducto43 in (15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33)
	AND (AF.ACTIVIDAD != 'INACTIVO' OR AF.ACTIVIDAD = NULL)
	AND (AF.SEGMENTO = 'MYPE')

GROUP BY 
	a.originador, 
	ACTUAL.SALDO_TOTAL, 
	DEL_MES.N�MERO_DESEMBOLSOS, 
	ACTUAL.NRO_CRED_VIGENTES_ACTUAL, 
	ANTERIOR.NRO_CRED_VIGENTES_ANTERIOR,
	ACTUAL.VENCIDO_ACTUAL,
	ANTERIOR.SALDO_TOTAL_ANTERIOR,
	ANTERIOR.VENCIDO_ANTERIOR, 
	ACTUAL.MORA_ACTUAL,
	ANTERIOR.MORA_ANTERIOR,
	DEL_MES.MONTO_DESEMBOLSADO,
	DEL_MES.TPPM,
	AF.ACTIVIDAD, AF.NIVEL, AF.SEGMENTO, AF.FECHA_INICIO,
	actual_distinct.NRO_SOCIOS_ACTUAL,
	anterior_distinct.NRO_SOCIOS_ANTERIOR,
	ult_12_meses.MORA_12,
	ACTUAL.SALDO_CARTERA,
	CAIDAS.CERO_CUOTAS, CAIDAS.UNA_CUOTA, CAIDAS.DOS_CUOTAS,
	nro_desembolsos.NRO_DESEMBOLSOS_12,

	metas.METAS_comercial,
	metas.desembolsado_comercial