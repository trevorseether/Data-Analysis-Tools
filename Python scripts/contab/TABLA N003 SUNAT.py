# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 15:24:34 2024

@author: sanmiguel38
"""

# =============================================================================
# Req Sunat - Tabla N 003
# =============================================================================

import pyodbc
import pandas as pd
import os

import warnings
warnings.filterwarnings('ignore')

#%%
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\pedidos\\contabilidad\\requerimiento sunat\\003 diciembre 2024')

excel_enviado_por_contabilidad = 'Tabla N 003 - 2024S2.xlsx'

skip_filas = 0

fecha_inicio = '20240701' # en formato para SQLserver
fecha_fin    = '20241231' # en formato para SQLserver

#%%
columna_nro_identificador_del_credito = 'NumerodeCredito18'

df_para_completar = pd.read_excel(io       = excel_enviado_por_contabilidad, 
                                  skiprows = skip_filas,
                                  dtype    = {columna_nro_identificador_del_credito        : str,
                                              'RUC'                                        : str,
                                              'Número de Documento de identidad del socio' : str,
                                              'Tipo de préstamo'                           : str,
                                              'Tipo de moneda'                             : str})

df_para_completar[columna_nro_identificador_del_credito] = df_para_completar[columna_nro_identificador_del_credito].str.strip()

#%%
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
	right(concat('0000000',pre.numero),8)  AS 'PagareFincore',
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
	iif(cdet.CodMoneda='95','DÓLAR','SOLES') AS 'moneda', 
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
                            left join CobranzaDocumento cdoc ON ccab.CodCobranzaDocumento =cdoc.CodCobranzaDocumento
                            left join Cuenta  CU ON CU.CodCuenta  =cdoc.CodCuentaDestino
                            left join NotaCredito  NC ON ccab.CodNotaCredito =NC.CodNotaCredito
                            left join CobranzaDocumento CDDNC ON NC.CodCobranzaDocumento =CDDNC.CodCobranzaDocumento
                            left join Cuenta  CUNC ON CDDNC.CodCuentaDestino=CUNC.CodCuenta

                            --------
  
-- WHERE        (ccab.Fecha >= '01-01-2020' and ccab.Fecha <= '31-12-2020') and cdet.flagponderosa is null
-- where year(ccab.fecha)=2021 and cdet.CodEstado <> 376 -- and fin.codigo<30 and gr.descripcion like '%PROSEVA%'  -- 376 Anulado and cdet.flagponderosa is null

WHERE CONVERT(VARCHAR(10),ccab.fecha,112) BETWEEN '{fecha_inicio}' AND '{fecha_fin}' and cdet.CodEstado <> 376   
ORDER BY socio, ccab.fecha

'''

df_fincore = pd.read_sql_query(query, conn)
df_fincore['pagare_fox'] = df_fincore['pagare_fox'].str.strip()

#%% CAPITAL AMORTIZADO, INTERÉS PAGADO
capital_interes = df_fincore.pivot_table(values  = ['Capital', 'INT_CUOTA'],
                                         index   = 'pagare_fox',
                                         aggfunc = 'sum').reset_index()

#%% APELLIDOS Y NOMBRES
datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')

server      = datos['DATOS'][0]
username    = datos['DATOS'][2]
password    = datos['DATOS'][3]

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'
conn = pyodbc.connect(conn_str)

query = f'''
SELECT
	s.codigosocio, 
	iif(s.CodTipoPersona =1, CONCAT(S.ApellidoPaterno,' ',S.ApellidoMaterno, ' ', S.Nombres),s.razonsocial) AS 'Socio',
		S.ApellidoPaterno,
		S.ApellidoMaterno,
		S.Nombres,
		s.razonsocial,
	iif(s.CodTipoPersona =1, s.nroDocIdentidad, s.nroruc) AS 'Doc_Identidad',
	IIF(S.CodSexo = 4, 'FEMENINO',
		IIF(S.CodSexo = 3, 'MASCULINO','EMPRESA')) AS 'SEXO',
		--------------------------------------------------------------
	RIGHT(CONCAT('0000000',p.numero),8) as 'pagare_fincore',
	CASE 
		WHEN p.CodPrestamoFox IS NOT NULL THEN
		RIGHT(CONCAT('000000',p.CodPrestamoFox),6)
	ELSE RIGHT(CONCAT('0000000',p.numero),8)
		END as 'pagare_fox'
		--------------------------------------------------------------
FROM prestamo AS p

INNER JOIN socio AS s             ON s.codsocio = p.codsocio
LEFT JOIN sociocontacto AS sc     ON sc.codsocio = s.codsocio
LEFT JOIN planilla AS pla         ON p.codplanilla = pla.codplanilla
INNER JOIN grupocab AS pro        ON pro.codgrupocab = p.codgrupocab
INNER JOIN distrito AS d          ON d.coddistrito = sc.coddistrito
INNER JOIN provincia AS pv        ON pv.codprovincia = d.codprovincia
INNER JOIN departamento AS dp     ON dp.coddepartamento = pv.coddepartamento
INNER JOIN tablaMaestraDet AS tm  ON tm.codtabladet = p.CodEstado
LEFT JOIN grupocab AS gpo         ON gpo.codgrupocab = pla.codgrupocab
LEFT JOIN tablaMaestraDet AS tm2  ON tm2.codtabladet = s.codestadocivil
LEFT JOIN tablaMaestraDet AS tm3  ON tm3.codtabladet = p.CodSituacion
--INNER JOIN tablaMaestraDet as tm3 on tm3.codtabladet = s.codcategoria
INNER JOIN pais                   ON pais.codpais = s.codpais
LEFT JOIN FINALIDAD AS FI         ON FI.CODFINALIDAD = P.CODFINALIDAD
LEFT JOIN TipoCredito AS TC       ON tc.CodTipoCredito = p.CodTipoCredito
INNER JOIN usuario AS u           ON p.CodUsuario = u.CodUsuario
INNER JOIN TablaMaestraDet AS tm4 ON s.codestado = tm4.CodTablaDet
--LEFT JOIN PrestamoCuota as pcu on p.CodPrestamo = pcu.CodPrestamo

LEFT JOIN SolicitudCredito AS SOLICITUD ON P.CodSolicitudCredito = SOLICITUD.CodSolicitudCredito
LEFT JOIN Usuario AS USUARIO            ON SOLICITUD.CodUsuarioSegAprob = USUARIO.CodUsuario

--LEFT JOIN SolicitudCreditoOtrosDescuentos AS DESCUENTO ON P.CodSolicitudCredito = DESCUENTO.CodSolicitudCredito

WHERE CONVERT(VARCHAR(10),p.fechadesembolso,112) >= '20010101'
--AND DESCUENTO.retencion = 'TOTAL RETENCIÓN'

AND s.codigosocio     > 0
AND p.montosolicitado > 0
--and p.codestado = 342
--AND FI.CODIGO IN (15,16,17,18,19,20,21,22,23,24,25,29)

-- AND (p.CODTIPOCREDITO=2 or p.CODTIPOCREDITO=9) and pcu.NumeroCuota=1 and tm2.descripcion is null -- 341 PENDIENTES  /  p.codestado <> 563  anulados
-- WHERE year(p.fechadesembolso) >= 2021 and month(p.fechadesembolso) >= 1 and s.codigosocio>0 and p.codestado <> 563 AND tc.CODTIPOCREDITO <>3 
-- AND pro.Descripcion like '%WILLIAMS TRAUCO%' 
-- AND p.codcategoria=351
ORDER BY socio ASC, p.fechadesembolso DESC
'''

total_cred = pd.read_sql_query(query, conn)
total_cred.drop_duplicates(subset  = 'pagare_fox',
                           inplace = True)

total_cred['pagare_fox'] = total_cred['pagare_fox'].str.strip()

datos_soc = total_cred[['pagare_fox',
                        'ApellidoPaterno',
                        'ApellidoMaterno',
                        'Nombres',
                        'razonsocial']]

#%% MERGE con los datos de los socios, separados
df_completado_1 = df_para_completar.merge(datos_soc,
                                          left_on  = columna_nro_identificador_del_credito,
                                          right_on = 'pagare_fox',
                                          how      = 'left')

investigar = df_completado_1[pd.isna(df_completado_1['pagare_fox'])]
if investigar.shape[0] > 0:
    print('investigar, hay algunos créditos que no han aparecido con la query, pero que sí están en el archivo de sunat enviado por contabilidad')
else:
    print('todo ok')

#%% MERGE CON EL CAPITAL E INTERESES
print('solo proceder si todo sale ok en la celda anterior')
df_completado_2 = df_completado_1.merge(capital_interes,
                                        on  = 'pagare_fox',
                                        how = 'left')

#%% limpieza de nulos
df_completado_2['Capital'].fillna(0, inplace = True)
df_completado_2['INT_CUOTA'].fillna(0, inplace = True)

df_completado_2['Capital'] = df_completado_2['Capital'].round(2)
df_completado_2['INT_CUOTA'] = df_completado_2['INT_CUOTA'].round(2)

#%% creación de excel
df_completado_2[[columna_nro_identificador_del_credito,
                 'ApellidoPaterno',
                 'ApellidoMaterno', 
                 'Nombres', 
                 'razonsocial', 
                 'Capital', 
                 'INT_CUOTA']].to_excel('Tabla N 003 SUNAT.xlsx',
                                        index = False)
                                        
df_completado_2.columns

