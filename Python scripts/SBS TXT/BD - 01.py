# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 10:26:33 2025

@author: sanmiguel38
"""

# =============================================================================
#                                   BD - 01
# =============================================================================

import pandas as pd
import os
import pyodbc
from datetime import datetime

import warnings
warnings.filterwarnings('ignore')

#%%
fecha_corte = '20241231'

os.chdir('C:\\Users\\sanmiguel38\\Desktop\\SBS TXT\\BD-01')

reprogramados_mismo_mes = 'C:/Users/sanmiguel38/Desktop/REPORTE DE REPROGRAMADOS (primer paso del anexo06)/2024/2024 diciembre/productos/Rpt_DeudoresSBS Créditos Reprogramados Diciembre 2024 no incluye castigados.xlsx'

#%% hora inicio
print('hora inicio:')
print(datetime.now().strftime("%H:%M:%S"))

#%%

conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')

query = f'''
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
	
	WHERE FechaCorte1 = '{fecha_corte}'
	
	AND SaldosdeCreditosCastigados38 = 0

'''

base = pd.read_sql_query(query, conn)

conn.close()

del conn
del query

#%% REPROGRAMADOS

repro = pd.read_excel(io = reprogramados_mismo_mes, 
                   dtype = {'Registro 1/'                   : object, 
                            'Fecha de Nacimiento 3/'        : object,
                            'Código Socio 7/'               : object,
                            'Tipo de Documento 9/'          : object,
                            'Número de Documento 10/'       : object,
                            'Relación Laboral con la Cooperativa 13/'       : object, 
                            'Código de Agencia 16/'         : object,
                            'Moneda del crédito 17/'        : object, 
                            'Numero de Crédito 18/'         : object,
                            'Tipo de Crédito 19/'           : object,
                            'Sub Tipo de Crédito 20/'       : object,
                            'Fecha de Desembolso 21/'       : object,
                            'Cuenta Contable 25/'           : object,
                            'Cuenta Contable Crédito Castigado 39/'         : object,
                            'Tipo de Producto 43/'          : object,
                            'Fecha de Vencimiento Origuinal del Credito 48/': object,
                            'Fecha de Vencimiento Actual del Crédito 49/'   : object,
                            'Nro Prestamo \nFincore'        : object,
                            'Refinanciado TXT'              : object
                            },
                   skiprows = 2)

#%% COBRANZAAAA (18 minutos)
if 'df_cobranza' not in globals():
    datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')
    
    server      = datos['DATOS'][0]
    username    = datos['DATOS'][2]
    password    = datos['DATOS'][3]
    
    conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'
    conn = pyodbc.connect(conn_str)
    
    query = f'''
    
    SELECT 
    	soc.codsocio, 
    	soc.codigosocio, 
    	iif(soc.CodTipoPersona =1,concat(soc.apellidopaterno,' ',soc.apellidomaterno,' ',soc.nombres),soc.razonsocial) AS 'Socio',
    		soc.apellidopaterno,
    		soc.apellidomaterno,
    		soc.nombres,
    		soc.razonsocial,
    	iif(soc.CodTipoPersona =1,soc.nrodocIdentidad,soc.nroRuc) AS 'doc_ident', 
    --------------------------------------------------------------------
    	right(concat('0000000',pre.numero),8)  AS 'PagareFincore',
    	CASE 
    		WHEN pre.CodPrestamoFox IS NOT NULL THEN
    		RIGHT(CONCAT('000000',pre.CodPrestamoFox),6)
    	ELSE RIGHT(CONCAT('0000000',pre.numero),8)
    		END as 'pagare_fox', 
    --------------------------------------------------------------------
    	pre.FechaDesembolso,
    
    	precuo.numerocuota,
    	precuo.NroPlazos,
    	precuo.FechaVencimiento,
    	precuo.FechaUltimoPago,
    	pre.fechaCancelacion,
    	
    	iif(cdet.CodMoneda='95','DÓLAR','SOLES') AS 'moneda',
    	
    	--year(ccab.fecha) AS 'AÑO TC',month(ccab.fecha) AS 'MES TC',
    
    	iif(cdet.CodMoneda = '95', tcsbs.tcsbs, 1) as 'TC_SBS',
    
    	ccab.fecha as 'fecha_cob', 
    	cdet.Capital, 
    	cdet.aporte as 'Aporte',
    	cdet.interes AS 'INT_CUOTA', 
    	cdet.InteresCompensatorio as 'IntCompVencido', 
    	cdet.Mora AS 'INTCOMP_MORA', 
    	cdet.GastoCobranza, 
    	cdet.FondoContigencia+cdet.MoraAnterior+cdet.GastoTeleOperador+cdet.GastoJudicial+cdet.GastoLegal+cdet.GastoOtros AS 'GTO_OTROS',
    	cdoc.numeroOperacion,
    	cdoc.numeroOperacionDestino, --tmdet.descripcion as TipoDocmto, 
    	gr.descripcion as 'Funcionario', 
    	pla.descripcion as 'planilla', 
    	tc.Descripcion as 'TipoCredito', 
    	fin.codigo AS 'codigo', 
    	fin.Descripcion as 'finalidad',  
    	pre.FechaVentaCartera, 
    	pre.FechaCastigo, 
    	cdoc.codestado, 
    	cDOC.NumeroOperacionDestino, 
    	CCAB.CODMEDIOPAGO, 
    	tmdet.descripcion as 'tipoPago', -- CDOC.CODCOBRANZADOCUMENTO,
    	tmdet5.Descripcion as 'SituacCred', 
    	pre.FechaAsignacionAbogado, 
    	empl.NombreCompleto as 'Abogado', 
    
    --IIF(CDDNC.NumeroOperacionDestino IS NULL,cdoc.NumeroOperacionDestino,CDDNC.NumeroOperacionDestino) AS NumeroOperacionDestino,
    IIF(CDDNC.NumeroOperacionDestino IS NULL,CU.NumeroCuenta,CUNC.NumeroCuenta) AS 'NumeroCuenta',
    --IIF(CDDNC.NumeroOperacionDestino IS NULL,NULL,CONCAT('NC-',RIGHT(CONCAT('000000',NC.Correlativo),6))) AS NroNotaCredito,
    iif(cdet.FlagPonderosa=1,'POND','SM') as 'origen'
    
    
    FROM   CobranzaDet AS cdet INNER JOIN prestamoCuota AS precuo ON precuo.CodprestamoCuota = cdet.CodprestamoCuota
                               INNER JOIN CobranzaCab as ccab ON ccab.CodCobranzaCab = cdet.CodCobranzaCab
                               Inner Join Prestamo as pre ON pre.codPrestamo = precuo.CodPrestamo 
                               Left Join Planilla AS pla ON pre.CodPlanilla = pla.CodPlanilla
                               Inner Join Socio as soc ON soc.CodSocio = pre.CodSocio
                               inner join finalidad as fin on fin.CodFinalidad = pre.CodFinalidad
                               inner join TipoCredito as tc on tc.CodTipoCredito = fin.CodTipoCredito
                               left join grupoCab as gr on gr.codGrupoCab = pre.codGrupoCab
    						   --   LEFT JOIN CobranzaDocumento as cdoc on ccab.CodCobranzaDocumento = cdoc.CodCobranzaDocumento
    						   --   Inner Join TablaMaestraDet as tmdet on tmdet.CodTablaDet = cdoc.CodMedioPago (ORIGUINAL)
                               LEft Join TablaMaestraDet as tmdet on tmdet.CodTablaDet = ccab.CodMedioPago --(NUEVO ACTIVAR)
    
                               left join Empleado as empl on pre.CodAbogado = empl.CodEmpleado
                               left join TablaMaestraDet as tmdet5 on pre.CodSituacion = tmdet5.CodTablaDet
    
                                -------
                                left join CobranzaDocumento  AS cdoc   ON ccab.CodCobranzaDocumento = cdoc.CodCobranzaDocumento
                                left join Cuenta             AS CU     ON CU.CodCuenta              = cdoc.CodCuentaDestino
                                left join NotaCredito        AS NC     ON ccab.CodNotaCredito       = NC.CodNotaCredito
                                left join CobranzaDocumento  AS CDDNC  ON NC.CodCobranzaDocumento   = CDDNC.CodCobranzaDocumento
                                left join Cuenta             AS CUNC   ON CDDNC.CodCuentaDestino    = CUNC.CodCuenta
    
                                --------
      
    				left join TipoCambioSBS as tcsbs
    				on (year(ccab.fecha) = tcsbs.Anno) and (month(ccab.fecha) = tcsbs.MES)
    
    -- WHERE        (ccab.Fecha >= '01-01-2020' and ccab.Fecha <= '31-12-2020') and cdet.flagponderosa is null
    -- where year(ccab.fecha)=2021 and cdet.CodEstado <> 376 -- and fin.codigo<30 and gr.descripcion like '%PROSEVA%'  -- 376 Anulado and cdet.flagponderosa is null
    
    WHERE CONVERT(VARCHAR(10),ccab.fecha,112) < '{fecha_corte}'
    
    --and right(concat('0000000',pre.numero),8)  = 00129322
    
    
    --ORDER BY socio, ccab.fecha
    '''
    
    df_cobranza = pd.read_sql_query(query, conn)
    
    conn.close()
    del query

#%%
df_dakr = df_cobranza[['PagareFincore', 'FechaVencimiento', 'fecha_cob']]
df_dakr = df_dakr.sort_values(by=['fecha_cob', 'FechaVencimiento'], ascending = [False, False])
df_dakr = df_dakr.drop_duplicates(subset=['PagareFincore'], keep='first')

df_dakr["diferencia_dias"] = (df_dakr["fecha_cob"] - df_dakr["FechaVencimiento"]).dt.days

def dakr (df_dakr):
    if df_dakr["diferencia_dias"] < 0:
        return 0
    else:
        return df_dakr["diferencia_dias"]
df_dakr['DAKR_generado'] = df_dakr.apply(dakr, axis = 1)

###################### UNIÓN #########
base = base.merge(df_dakr[['PagareFincore', 'DAKR_generado']],
                  left_on  = 'CCR',
                  right_on = 'PagareFincore',
                  how      = 'left')

base['DAKR'] = base['DAKR_generado']
base['DAKR'] = base['DAKR'].fillna(0)
base['DAKR'] = base['DAKR'].astype(int)

del base['PagareFincore']
del base['DAKR_generado']


#%%
print('hora final:')
print(datetime.now().strftime("%H:%M:%S"))

