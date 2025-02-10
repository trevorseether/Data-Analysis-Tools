# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 12:12:36 2025

@author: sanmiguel38
"""

# =============================================================================
#                                  BD - 01
# =============================================================================

#MÓDULOS NECESARIOS:
import pandas as pd
import pyodbc
import os

import warnings
warnings.filterwarnings('ignore')

#%%
fecha_corte = '20241231'

os.chdir('C:\\Users\\sanmiguel38\\Desktop\\SBS REPORTES TXT\\BD 01')

crear_TXT = True

#%%

conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')

query = f'''
-- BD01

SELECT
	CodigoSocio7                  AS 'CIS'  ,
	TipodeDocumento9              AS 'TID'  ,
	NumerodeDocumento10           AS 'NID'  ,
	ApellidosyNombresRazonSocial2 AS 'NSO'  ,
	Nro_Fincore                   AS 'CCR'  ,
	Monedadelcredito17            AS 'MON'  ,
	MontodeDesembolso22           AS 'MORG' ,
	Saldodecolocacionescreditosdirectos24   AS 'SKCR',
	TipodeCredito19               AS 'TCR'  ,
	ClasificaciondelDeudorconAlineamiento15 AS 'CAL',
	DiasdeMora33                  AS 'DAK'  ,
	DiasdeMora33                  AS 'DAKR' , -- OJO, REVISAR ESTE CÁLCULO
	ProvisionesConstituidas37     AS 'PCI'  ,
	CapitalVigente26              AS 'KVI'  ,
	NULL                          AS 'CCVI' , -- REVISAR CUENTA CONTABLE
	CapitalRefinanciado28         AS 'KRF'  ,
	NULL                          AS 'CCRF' , -- REVISAR CUENTA CONTABLE
	CapitalVencido29              AS 'KVE'  ,
	NULL                          AS 'CCVE' , -- REVISAR CUENTA CONTABLE
	CapitalenCobranzaJudicial30   AS 'KJU'  ,
	NULL                          AS 'CCJU' , -- REVISAR CUENTA CONTABLE
	0                             AS 'KCO'  , -- REVISAR SALDO CONTINGENTE
	NULL                          AS 'CCCO' , -- REVISAR CUENTA CONTABLE
	'FACTOR EQUIVALENTE RIESG CRED'         AS 'FCC', --REVISAR CON RIESGOS
	Rendimiento_Devengado40       AS 'SIN'  ,
	NULL                          AS 'CCSIN', --REVISAR CUENTA CONTABLE
	IngresosDiferidos42           AS 'SID'  ,
	NULL                          AS 'CCSID', -- REVISAR CUENTA CONTABLE
	InteresesenSuspenso41         AS 'SIS'  ,
	NULL                          AS 'CCSIS', -- REVISAR CUENTA CONTABLE
	FechadeDesembolso21           AS 'FOT'  ,
	NULL                          AS 'ESAM' , -- ESQUEMA DE AMORTIZACIÓN
	PeriododeGracia47             AS 'DGR'  ,
	NULL                          AS 'FPPK' , -- FECHA PRIMER PAGO(VENCIMIENTO PRIMERA CUOTA?)
	NULL                          AS 'FVEG' , -- FECHA VENCIMIENTO GENERAL
	NumerodeCuotasProgramadas44   AS 'NCPR' ,
	ROUND(TasadeInteresAnual23 * 100,2)     AS 'TEA',
	Periodicidaddelacuota46       AS 'PCUO' ,
	NULL                          AS 'FVEP' , -- FECHA DE VENCIMIENTO PUNTUAL
	NumerodeCuotasPagadas45       AS 'NCPA' ,
	'SECTOR DEL CRÉDITO'          AS 'SEC'  ,
	MASTER.[dbo].[tipo_producto](TipodeProducto43) AS 'TPR',
	'CODIGO AGENCIA'              AS 'CAGE' ,
	'USUARIO DESEMBOLSO'          AS 'UDES' ,
	'HORA DESEMBOLSO'             AS 'FOT_H',
	'MODALIDAD'                   AS 'MDCR' , -- CREO QUE YO MISMO LO PUEDO HACER
	'FECHA ULT PAGO A CAPITAL'    AS 'FUK'  ,
	'FECHA ULT PAGO A INT'        AS 'FUINT',
	'TOTAL INTERES'               AS 'TPINT',
	'# CAMBIOS CONTRACTUALES'     AS 'NRPRG',
	'CIIUU ACTIVIDAD ECONÓMICA'   AS 'CCSD' ,
	'OCUPACIÓN'                   AS 'OSD'

FROM anexos_riesgos3..ANX06
	WHERE FechaCorte1 = '{fecha_corte}'
	AND SaldosdeCreditosCastigados38 = 0

'''

datos_anx06 = pd.read_sql_query(query, conn)

#%%



#%%
if crear_TXT == True:
    datos_anx06.to_csv('output.txt', sep='\t', index=False)

#%%
print('fin')
