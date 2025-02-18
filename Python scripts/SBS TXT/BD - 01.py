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
	0                             AS 'FCC', --REVISAR CON RIESGOS
	Rendimiento_Devengado40       AS 'SIN',
	NULL                          AS 'CCSIN', --REVISAR CUENTA CONTABLE
	IngresosDiferidos42           AS 'SID',
	NULL                          AS 'CCSID', -- REVISAR CUENTA CONTABLE
	InteresesenSuspenso41         AS 'SIS',
	NULL                          AS 'CCSIS', -- REVISAR CUENTA CONTABLE
	FORMAT(FechadeDesembolso21, 'dd/MM/yyyy')                     AS 'FOT',
	NULL                          AS 'ESAM', -- ESQUEMA DE AMORTIZACIÓN
	PeriododeGracia47             AS 'DGR',
	NULL                          AS 'FPPK', -- FECHA PRIMER PAGO(VENCIMIENTO PRIMERA CUOTA?)
    FORMAT(FechadeVencimientoOriguinaldelCredito48, 'dd/MM/yyyy') AS 'FVEG',
	NumerodeCuotasProgramadas44   AS 'NCPR',
	ROUND(TasadeInteresAnual23 * 100,2)                           AS 'TEA',
	Periodicidaddelacuota46       AS 'PCUO',
	FORMAT(FechadeVencimientoAnualdelCredito49, 'dd/MM/yyyy')     AS 'FVEP', -- FECHA DE VENCIMIENTO PUNTUAL
	NumerodeCuotasPagadas45       AS 'NCPA',
	99                            AS 'SEC',
	MASTER.[dbo].[tipo_producto](TipodeProducto43)                AS 'TPR',
	'01'                          AS 'CAGE',
    '150120'                      AS 'UAGE',
	'USUARIO DESEMBOLSO'          AS 'UDES',
	'HORA DESEMBOLSO'             AS 'FOT_H',
	TIPO_afil                     AS 'MDCR', -- CREO QUE YO MISMO LO PUEDO HACER
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

base = pd.read_sql_query(query, conn, dtype = str)

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

    df_cobranza = df_cobranza[df_cobranza['fecha_cob'] <= pd.Timestamp(fecha_corte)]


#%%
if 'df_desembolsos' not in globals():
    datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')
    
    server      = datos['DATOS'][0]
    username    = datos['DATOS'][2]
    password    = datos['DATOS'][3]
    
    conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'
    conn = pyodbc.connect(conn_str)
    
    query = '''
                SELECT
                
                	s.codigosocio, 
                	iif(s.CodTipoPersona =1, CONCAT(S.ApellidoPaterno,' ',S.ApellidoMaterno, ' ', S.Nombres),s.razonsocial) AS 'Socio',
                	RIGHT(CONCAT('0000000',p.numero),8) as 'pagare_fincore',
                	p.fechadesembolso,
                
                	FORMAT(p.fechadesembolso, 'yyyy-MM-dd') AS 'SoloFecha',
                    FORMAT(p.fechadesembolso, 'HH:mm:ss')   AS 'Hora_desembolso',
                
                	u.IdUsuario as 'User_Desemb'
                
                FROM prestamo AS p
                
                INNER JOIN socio AS s             ON s.codsocio = p.codsocio
                INNER JOIN usuario AS u           ON p.CodUsuario = u.CodUsuario
                INNER JOIN TablaMaestraDet AS tm4 ON s.codestado = tm4.CodTablaDet
                
                WHERE CONVERT(VARCHAR(10),p.fechadesembolso,112) >= '20000101'
                
                ORDER BY p.fechadesembolso DESC    
                '''
    
    df_desembolsos = pd.read_sql_query(query, conn)
    conn.close()
    
    df_desembolsos = df_desembolsos.drop_duplicates(subset = ['pagare_fincore'], keep = 'first')

    del query
#%%
if 'cuotas' not in globals():
    datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')
    
    server      = datos['DATOS'][0]
    username    = datos['DATOS'][2]
    password    = datos['DATOS'][3]
    
    conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'
    conn = pyodbc.connect(conn_str)
    
    create_temp_table_query = '''
    IF OBJECT_ID('tempdb.dbo.#TMP_SOCIOBLOQUEAR', 'U') IS NOT NULL
        DROP TABLE #TMP_SOCIOBLOQUEAR;  
	SELECT CODSOCIO INTO #TMP_SOCIOBLOQUEAR FROM Socio   
    WHERE CodSocio IN (
	105,637,1409,1598,1650,1654,1685,1996,2135,2144,2534,4856,6621,10491,21815,34561,
	17206,1650,1654,293,470,508,509,578,582,622,623,625,
    627,631,632,634,642,643,644,646,667,668,669,671,674,675,
    676,679,680,699,704,4724,6642,7211,374,388,391,392,393,
    394,396,397,398,399,400,405,412,413,414,415,416,417,
    420,421,422,424,425,450,451,453)
    '''
    conn.execute(create_temp_table_query)    
    
    query = '''
    	SELECT
        	RIGHT(CONCAT('00000000',P.Numero),8) AS NroPrestamo,
        	ISNULL(CONVERT(VARCHAR(10),pc.FechaVencimiento,103),'')
        	  as FechaVencimiento,
        	ISNULL(pc.numerocuota,'') as numerocuota,
        
        	IIF(PC.CodEstado<>379,pc.capital,CD.CAPITAL) AS capital,
        	IIF(PC.CodEstado<>379,pc.interes,CD.INTERES) AS interes,
        	'0' as CargosGenerales,
        	'0' as CargosSeguro,
        	IIF(PC.CodEstado<>379,pc.Aporte,CD.APORTE) AS Aporte,
        	IIF(PC.CodEstado<>379,pc.aporte,CD.APORTE) as TotalCargo,
        
        	iif(pc.codestado=346,0, IIF(PC.CodEstado <> 379,(pc.Capital + pc.Interes + pc.FondoContigencia + pc.Aporte),CD.CAPITAL+CD.INTERES+CD.APORTE)) as TotalPago,
        
        	0 as Ahorros,
        	iif(pc.CodEstado in (22,1003,379),'9','0') as Pagado,pc.CodEstado 

        --,pc.CodEstado as EstadoCuota,pc.CuotaFija,P.CodEstado as EstadoPrestamo,P.FechaVentaCartera,P.CodSocio,p.CodPrestamo,p.FechaDesembolso,pc.periodo   
        from prestamocuota pc
        inner join prestamo p on pc.CodPrestamo =p.CodPrestamo
        inner join socio s on p.CodSocio =s.CodSocio
        LEFT JOIN 
        (SELECT SUM(CAPITAL) AS CAPITAL,SUM(INTERES) AS INTERES,SUM(APORTE) AS APORTE,CodPrestamoCuota FROM CobranzaDet GROUP BY CodPrestamoCuota)
        CD ON pc.CodPrestamoCuota =CD.CodPrestamoCuota
        where
        pc.CodEstado not in (24) and p.CodEstado <>563   and CONVERT(VARCHAR(10),pc.FechaVencimiento,103) is not null --and (pc.Capital + pc.Interes + pc.FondoContigencia + pc.Aporte)>0
         AND S.CodSocio  not in (select codsocio from #TMP_SOCIOBLOQUEAR) 
         AND PC.CodPrestamoCuota NOT IN (
        							 SELECT CodPrestamoCuota  FROM (
        							select
        							PC.CodPrestamoCuota,
        							ISNULL(pc.numerocuota,'') as numerocuota,
        							pc.interes,
        							iif(pc.CodEstado in (22,1003),'9','0') as Pagado,
        							iif(pc.codestado=346,0,(pc.Capital + pc.Interes + pc.FondoContigencia + pc.Aporte)) as TotalPago
        							from prestamocuota pc
        							inner join prestamo p on pc.CodPrestamo =p.CodPrestamo
        							inner join socio s on p.CodSocio =s.CodSocio
        							where
        							pc.CodEstado not in (24,379) and p.CodEstado <>563   and CONVERT(VARCHAR(10),pc.FechaVencimiento,103) is not null 
        							 AND S.CodSocio  not in (select codsocio from #TMP_SOCIOBLOQUEAR) 
        							 AND   P.FECHAVENTACARTERA IS NULL
        							 ) TABLA 
        							 WHERE numerocuota =0 AND Interes =0 AND TotalPago =0
         
         )
        -- AND   P.FECHAVENTACARTERA IS NULL
        order by pc.CodPrestamo,  pc.CodPrestamoCuota 
                '''
    
    prppg_cuotas = pd.read_sql_query(query, conn)
    conn.close()

#%%  DAKR
df_dakr = df_cobranza[['PagareFincore', 'FechaVencimiento', 'fecha_cob']]
df_dakr = df_dakr.sort_values(by = ['fecha_cob', 'FechaVencimiento'], ascending = [False, False])
df_dakr = df_dakr.drop_duplicates(subset = ['PagareFincore'], keep='first')

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

#%% UDES      FOT_H 
base = base.merge(df_desembolsos[['pagare_fincore', 'User_Desemb', 'Hora_desembolso']],
                  left_on  = 'CCR',
                  right_on = 'pagare_fincore',
                  how      = 'left')

base['UDES']  = base['User_Desemb']
base['FOT_H'] = base['Hora_desembolso']

base['UDES']  = base['UDES'].fillna('')
base['FOT_H'] = base['FOT_H'].fillna('00:00:00')

del base['User_Desemb']
del base['Hora_desembolso']

alerta1 = base[pd.isna(base['pagare_fincore'])]
if alerta1.shape[0]:
    print('alerta, por alguna razón, falta algún crédito desembolsado')
    
del alerta1
del base['pagare_fincore']

#%% ESQUEMA DE AMORTIZACIÓN - ESAM
conteo_filas = prppg_cuotas.pivot_table(values = 'numerocuota',
                                        index  = 'NroPrestamo',
                                        aggfunc = 'count').reset_index()
conteo_filas.rename(columns = {'numerocuota':'conteo de cuotas'}, inplace = True)

prppg_cuotas = prppg_cuotas.merge(conteo_filas,
                                  on  = 'NroPrestamo',
                                  how = 'left')

pago_unico_de_capital_e_intereses_1 = prppg_cuotas[prppg_cuotas['conteo de cuotas'] == 1]

###############################################################################

cuotas_cap = prppg_cuotas[prppg_cuotas['capital'] > 0]
cuotas_int = prppg_cuotas[prppg_cuotas['interes'] > 0]

conteo_filas_cap = cuotas_cap.pivot_table(values = 'numerocuota',
                                        index    = 'NroPrestamo',
                                        aggfunc  = 'count').reset_index()
conteo_filas_cap.rename(columns = {'numerocuota':'conteo de cuotas con capital'}, inplace = True)

conteo_filas_int = cuotas_int.pivot_table(values  = 'numerocuota',
                                          index   = 'NroPrestamo',
                                          aggfunc = 'count').reset_index()
conteo_filas_int.rename(columns = {'numerocuota':'conteo de cuotas con interés'}, inplace = True)

prppg_cuotas = prppg_cuotas.merge(conteo_filas_cap,
                                  on  = 'NroPrestamo',
                                  how = 'left')

prppg_cuotas = prppg_cuotas.merge(conteo_filas_int,
                                  on  = 'NroPrestamo',
                                  how = 'left')

pago_unico_de_capital_pero_con_pago_intermedio_de_interes_2 = prppg_cuotas[(prppg_cuotas['conteo de cuotas con capital'] == 1)  &  (prppg_cuotas['conteo de cuotas con interés'] > 1)]

###############################################################################

def ESAM(base):
    if base['CCR'] in list(pago_unico_de_capital_e_intereses_1['NroPrestamo']):
        return '1'
    if base['CCR'] in list(pago_unico_de_capital_pero_con_pago_intermedio_de_interes_2['NroPrestamo']):
        return '2'
    else:
        return '3'

base['ESAM'] = base.apply(ESAM, axis = 1)

#%%    FPPK
prppg_cuotas_primer_pago = prppg_cuotas[prppg_cuotas['numerocuota'] == 1]
prppg_cuotas_primer_pago.drop_duplicates(subset  = 'NroPrestamo', 
                           inplace = True)

base = base.merge(prppg_cuotas_primer_pago[['NroPrestamo', 'FechaVencimiento']],
                  left_on  = 'CCR',
                  right_on = 'NroPrestamo',
                  how      = 'left')

alerta2 = base[pd.isna(base['NroPrestamo'])]
if alerta2.shape[0]:
    print('alerta, por alguna razón, falta algún crédito desembolsado')
    
del alerta2
del base['NroPrestamo']

base['FPPK'] = base['FechaVencimiento']

del base['FechaVencimiento']

#%% MDCR
base['MDCR'] = base['MDCR'].map({'NUEVO'            : '1',
                                 'AMPLIACION'       : '3',
                                 'REFINANCIAMIENTO' : '5'})

def MDCR_REPRO(base):
    if base['CCR'] in list(repro['Nro Prestamo \nFincore']):
        return '2'
    else:
        return base['MDCR']
base['MDCR'] = base.apply(MDCR_REPRO, axis = 1)

#%% FUK
ultimo_pago_capital = df_cobranza[['PagareFincore', 'Capital', 'fecha_cob']]

ultimo_pago_capital = ultimo_pago_capital.sort_values(by = ['fecha_cob'], ascending = [False])

ultimo_pago_capital = ultimo_pago_capital[ultimo_pago_capital['Capital'] > 0 ]

ultimo_pago_capital = ultimo_pago_capital.drop_duplicates(subset = ['PagareFincore'], keep = 'first')

ultimo_pago_capital['fecha_cob'] = ultimo_pago_capital['fecha_cob'].dt.strftime('%d/%m/%Y')

base = base.merge(ultimo_pago_capital[['PagareFincore', 'fecha_cob']],
                  left_on  = 'CCR',
                  right_on = 'PagareFincore',
                  how      = 'left' )

base['FUK'] = base['fecha_cob']

del base['PagareFincore']
del base['fecha_cob']

#%% FUINT
ultimo_pago_int = df_cobranza[['PagareFincore', 'INT_CUOTA', 'fecha_cob']]

ultimo_pago_int = ultimo_pago_int.sort_values(by = ['fecha_cob'], ascending = [False])

ultimo_pago_int = ultimo_pago_int[ultimo_pago_int['INT_CUOTA'] > 0 ]

ultimo_pago_int = ultimo_pago_int.drop_duplicates(subset = ['PagareFincore'], keep = 'first')

ultimo_pago_int['fecha_cob'] = ultimo_pago_int['fecha_cob'].dt.strftime('%d/%m/%Y')

base = base.merge(ultimo_pago_int[['PagareFincore', 'fecha_cob']],
                  left_on  = 'CCR',
                  right_on = 'PagareFincore',
                  how      = 'left' )

base['FUINT'] = base['fecha_cob']

del base['PagareFincore']
del base['fecha_cob']

#%% TPINT
total_pago_int = df_cobranza[['PagareFincore', 'INT_CUOTA', 'IntCompVencido', 'INTCOMP_MORA']]

total_pago_int['total_int'] = total_pago_int['INT_CUOTA'] + total_pago_int['IntCompVencido']  + total_pago_int['INTCOMP_MORA']

agg_pago_int = total_pago_int.pivot_table(values  = 'total_int',
                                          index   = 'PagareFincore',
                                          aggfunc = 'sum').reset_index()

base = base.merge(agg_pago_int,
                  left_on  = 'CCR',
                  right_on = 'PagareFincore',
                  how      = 'left')

base['TPINT'] = base['total_int']
base['TPINT'] = base['TPINT'].fillna(0)

del base['PagareFincore']
del base['total_int']

#%% NRPRG (nro de reprogramaciones)
nro_repros = repro[['Nro Prestamo \nFincore', 'NRO REPROG']]

base = base.merge(nro_repros,
                  left_on  = 'CCR',
                  right_on = 'Nro Prestamo \nFincore',
                  how      = 'left')

base['NRPRG'] = base['NRO REPROG']
base['NRPRG'] = base['NRPRG'].fillna(0)
base['NRPRG'] = base['NRPRG'].astype(int)

del base['Nro Prestamo \nFincore']
del base['NRO REPROG']

#%%
#%%
print('hora final:')
print(datetime.now().strftime("%H:%M:%S"))

base.columns

'''Nro Prestamo 
Fincore'''



