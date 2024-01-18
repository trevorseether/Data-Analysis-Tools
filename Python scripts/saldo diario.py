# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 13:05:08 2024

@author: sanmiguel38
"""

# =============================================================================
# SALDO DIARIO
# =============================================================================

import pandas as pd
import pyodbc

#%%
'Fecha de corte para el anexo06'####################
fecha_corte_anx06 = '20231231'                     #
####################################################

'Fechas para la cobranza y nuevos desembolsos'######
fecha_inicio         = '20240101'                  #
fecha_corte_cobranza = '20240131'                  #
####################################################
#%%
conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')

#%% SELECCIÓN DE LA FECHA MÁS RECIENTE EN LA BASE DE DATOS
anx06 = pd.read_sql_query(f'''
SELECT 
	FechaCorte1,
	Nro_Fincore,
	Saldodecolocacionescreditosdirectos24,
	MontodeDesembolso22,
	FechadeDesembolso21,
	CapitalVencido29,
	CapitalenCobranzaJudicial30,
	SaldosdeCreditosCastigados38,
	DiasdeMora33,
	TipodeProducto43,
	CASE
		WHEN TipodeProducto43 IN (15,16,17,18,19) THEN 'PEQUEÑA EMPRESA'
		WHEN TipodeProducto43 IN (21,22,23,24,25,26,27,28,29) THEN 'MICRO EMPRESA'
		WHEN TipodeProducto43 IN (95,96,97,98,99) THEN 'MEDIANA EMPRESA'
		WHEN TipodeProducto43 IN (34,35,36,37,38,39) THEN 'DXP'
		WHEN TipodeProducto43 IN (30,31,32,33) THEN 'LD'
		WHEN TipodeProducto43 IN (41,45) THEN 'HIPOTECARIO'
	END AS 'PRODUCTO TXT',
	PLANILLA_CONSOLIDADA,
	originador,
	administrador

FROM anexos_riesgos3..ANX06
WHERE FechaCorte1 = '{fecha_corte_anx06}' --(select distinct max(FechaCorte1) from anexos_riesgos3..ANX06)
''', 
    conn)

del conn

#%%
#%%
datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')

#%%

server      = datos['DATOS'][0]
username    = datos['DATOS'][2]
password    = datos['DATOS'][3]

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'

conn = pyodbc.connect(conn_str)

#%%
query = '''
SELECT

	RIGHT(CONCAT('0000000',p.numero),8) as 'pagare_fincore',
	p.fechaCancelacion

FROM prestamo as p

inner join socio as s on s.codsocio = p.codsocio
where CONVERT(VARCHAR(10),p.fechadesembolso,112) > '20100101' 
and s.codigosocio>0  and p.codestado = 342
order by p.fechadesembolso desc

'''

df_cancelados = pd.read_sql_query(query, conn)

#%% CRÉDITOS DESEMBOLSADOS DURANTE EL PRESENTE MES
query = f'''
SELECT

	RIGHT(CONCAT('0000000',p.numero),8) as 'pagare_fincore',
	p.montosolicitado as 'MONTO_DESEMBOLSO',
	tm.descripcion as 'Estado',
	iif(p.codcategoria=351,'NVO','AMPL') as 'tipo_pre', 
	p.flagrefinanciado, 
	pro.descripcion as 'ADMINISTRADOR',
    pro.descripcion as 'ORIGINADOR',
	pla.descripcion as 'Planilla', 
	iif(p.flagponderosa=1,'POND','SM') as 'origen', 
	tc.Descripcion as 'TipoCredito', 
	FI.CODIGO AS 'COD_FINALIDAD', 
	FI.DESCRIPCION AS 'FINALIDAD' 

FROM prestamo as p

    inner join socio as s on s.codsocio = p.codsocio
    LEFT join sociocontacto as sc on sc.codsocio = s.codsocio
    left join planilla as pla on p.codplanilla = pla.codplanilla
    inner join grupocab as pro on pro.codgrupocab = p.codgrupocab
    inner join distrito as d on d.coddistrito = sc.coddistrito
    inner join provincia as pv on pv.codprovincia = d.codprovincia
    inner join departamento as dp on dp.coddepartamento = pv.coddepartamento
    inner join tablaMaestraDet as tm on tm.codtabladet = p.CodEstado
    left join grupocab as gpo on gpo.codgrupocab = pla.codgrupocab
    left join tablaMaestraDet as tm2 on tm2.codtabladet = s.codestadocivil
    left join tablaMaestraDet as tm3 on tm3.codtabladet = p.CodSituacion
    --inner join tablaMaestraDet as tm3 on tm3.codtabladet = s.codcategoria
    inner join pais on pais.codpais = s.codpais
    LEFT JOIN FINALIDAD AS FI ON FI.CODFINALIDAD = P.CODFINALIDAD
    left join TipoCredito as TC on tc.CodTipoCredito = p.CodTipoCredito
    inner join usuario as u on p.CodUsuario = u.CodUsuario
    inner join TablaMaestraDet as tm4 on s.codestado = tm4.CodTablaDet
    --left join PrestamoCuota as pcu on p.CodPrestamo = pcu.CodPrestamo

where 
CONVERT(VARCHAR(10),p.fechadesembolso,112) BETWEEN '{fecha_inicio}' AND '{fecha_corte_cobranza}' 
and s.codigosocio>0  and p.codestado = 341
order by p.fechadesembolso desc
'''
df_desembolsados = pd.read_sql_query(query, conn)

#%% COBRANZA DEL MES
query = f'''
SELECT 
	right(concat('0000000',pre.numero),8)  AS 'PagareFincore',
	pre.FechaDesembolso,
	precuo.numerocuota, 
	iif(cdet.CodMoneda='95','DÓLAR','SOLES') AS 'moneda', 
	ccab.fecha as 'fecha_cob', 
	cdet.Capital, 
	cdet.aporte as 'Aporte',
	cdet.interes AS 'INT_CUOTA'
	
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
                            left join CobranzaDocumento cdoc ON ccab.CodCobranzaDocumento =cdoc.CodCobranzaDocumento
                            left join Cuenta  CU ON CU.CodCuenta  =cdoc.CodCuentaDestino
                            left join NotaCredito  NC ON ccab.CodNotaCredito =NC.CodNotaCredito
                            left join CobranzaDocumento CDDNC ON NC.CodCobranzaDocumento =CDDNC.CodCobranzaDocumento
                            left join Cuenta  CUNC ON CDDNC.CodCuentaDestino=CUNC.CodCuenta

                            --------

WHERE CONVERT(VARCHAR(10),ccab.fecha,112) BETWEEN '20240101' AND '20240131' and cdet.CodEstado <> 376   
ORDER BY ccab.fecha

'''
df_cobranza = pd.read_sql_query(query, conn)
