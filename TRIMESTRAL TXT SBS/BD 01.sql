
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

	/*------------------------------------------------------------*/
	CapitalVigente26              AS 'KVI',
	CASE
		WHEN CuentaContable25 IN (  '1411120600','1411130600',
									'1411020600','1411030612',
									'1411040601','1411120600',
									'1411130600','1411020600',
									'1411030604','1411040601'  )
        THEN  CuentaContable25 
		END AS 'CCVI', -- CUENTA CONTABLE
	/*------------------------------------------------------------*/
	CapitalRefinanciado28         AS 'KRF',
		CASE
		WHEN CuentaContable25 IN (  '1414120600','1414130600',
                                    '1414020600','1414030604',
                                    '1414040601','1414120600',
									'1414130600','1414020600',
									'1414030605','1414040601' )
        THEN  CuentaContable25 
        END AS 'CCRF', -- CUENTA CONTABLE
	/*------------------------------------------------------------*/
	CapitalVencido29              AS 'KVE',
		CASE
		WHEN CuentaContable25 IN (  '1425120600','1425130600',
                                    '1425020600','1425030604',
                                    '1425040601','1425120600',
									'1425130600','1425020600',
									'1425030612','1425040601')
        THEN  CuentaContable25 
        END AS 'CCVE', -- CUENTA CONTABLE
	/*------------------------------------------------------------*/
	CapitalenCobranzaJudicial30   AS 'KJU',
		CASE
		WHEN CuentaContable25 IN (  '1416120600','1416130600',
                                    '1416020600','1416030612',
                                    '1416040601','1426120600',
									'1426130600','1426020600',
									'1426030612','1426040601')
        THEN  CuentaContable25
		END AS 'CCJU', -- CUENTA CONTABLE
	/*------------------------------------------------------------*/

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
	FechadeVencimientoAnualdelCredito49 AS 'FVEP', -- FECHA DE VENCIMIENTO PUNTUAL
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
	
	WHERE FechaCorte1 = '20230131'
	
	AND SaldosdeCreditosCastigados38 = 0




