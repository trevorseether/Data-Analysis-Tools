
-- BD01

SELECT
	CodigoSocio7                  AS 'CIS',
	TipodeDocumento9              AS 'TID',
	NumerodeDocumento10           AS 'NID',
	ApellidosyNombresRazonSocial2 AS 'NSO',
	Nro_Fincore                   AS 'CCR',
	Monedadelcredito17            AS 'MON',
	MontodeDesembolso22           AS 'MORG',
	Saldodecolocacionescreditosdirectos24   AS 'SKCR',
	TipodeCredito19               AS 'TCR',
	ClasificaciondelDeudorconAlineamiento15 AS 'CAL',
	DiasdeMora33                  AS 'DAK',
	NULL                          AS 'DAKR', -- OJO, REVISAR ESTE CÁLCULO
	ProvisionesConstituidas37     AS 'PCI',
	CapitalVigente26              AS 'KVI',
	NULL                          AS 'CCVI', -- REVISAR CUENTA CONTABLE
	CapitalRefinanciado28         AS 'KRF',
	NULL                          AS 'CCRF', -- REVISAR CUENTA CONTABLE
	CapitalVencido29              AS 'KVE',
	NULL                          AS 'CCVE', -- REVISAR CUENTA CONTABLE
	CapitalenCobranzaJudicial30   AS 'KJU',
	NULL                          AS 'CCJU', -- REVISAR CUENTA CONTABLE
	0                             AS 'KCO',  -- REVISAR SALDO CONTINGENTE
	NULL                          AS 'CCCO', -- REVISAR CUENTA CONTABLE
	'FACTOR EQUIVALENTE RIESG CRED'         AS 'FCC', --REVISAR CON RIESGOS
	Rendimiento_Devengado40       AS 'SIN',
	NULL                          AS 'CCSIN', --REVISAR CUENTA CONTABLE
	IngresosDiferidos42           AS 'SID',
	NULL                          AS 'CCSID', -- REVISAR CUENTA CONTABLE
	InteresesenSuspenso41         AS 'SIS',
	NULL                          AS 'CCSIS', -- REVISAR CUENTA CONTABLE
	FechadeDesembolso21           AS 'FOT',
	NULL                          AS 'ESAM', -- ESQUEMA DE AMORTIZACIÓN
	PeriododeGracia47             AS 'DGR',
	NULL                          AS 'FPPK', -- FECHA PRIMER PAGO(VENCIMIENTO PRIMERA CUOTA?)
	FechadeVencimientoOriguinaldelCredito48 AS 'FVEG',
	NumerodeCuotasProgramadas44   AS 'NCPR',
	ROUND(TasadeInteresAnual23 * 100,2)     AS 'TEA',
	Periodicidaddelacuota46       AS 'PCUO',
	NULL                          AS 'FVEP', -- FECHA DE VENCIMIENTO PUNTUAL
	NumerodeCuotasPagadas45       AS 'NCPA',
	99                            AS 'SEC',
	MASTER.[dbo].[tipo_producto](TipodeProducto43) AS 'TPR',
	'01'                          AS 'CAGE',
	'USUARIO DESEMBOLSO'          AS 'UDES',
	'HORA DESEMBOLSO'             AS 'FOT_H',
	'MODALIDAD'                   AS 'MDCR', -- CREO QUE YO MISMO LO PUEDO HACER
	'FECHA ULT PAGO A CAPITAL'    AS 'FUK',
	'FECHA ULT PAGO A INT'        AS 'FUINT',
	'TOTAL INTERES'               AS 'TPINT',
	'# CAMBIOS CONTRACTUALES'     AS 'NRPRG',
	'CIIUU ACTIVIDAD ECONÓMICA'   AS 'CCSD',
	'OCUPACIÓN'                   AS 'OSD'

FROM anexos_riesgos3..ANX06
	WHERE FechaCorte1 = '20241231'
	AND SaldosdeCreditosCastigados38 = 0


