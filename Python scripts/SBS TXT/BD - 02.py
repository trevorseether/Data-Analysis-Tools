# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 18:06:24 2025

@author: sanmiguel38
"""

# =============================================================================
#                                   BD - 02
# =============================================================================

import pandas as pd
import os
import pyodbc
# from datetime import datetime

import warnings
warnings.filterwarnings('ignore')

#%%
os.chdir('R:/REPORTES DE GESTIÓN/Insumo para Analisis/prppgs, cortes trimestrales')

fecha_corte = '20241231' # FÓRMATO SQL

#%%
cuotas = pd.read_csv('prppg 2024-12-31.csv',
                     dtype = str)

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
                	iif(p.codmoneda=94,'1','2') as 'moneda', 

                	FORMAT(p.fechadesembolso, 'yyyy-MM-dd') AS 'SoloFecha',
                    FORMAT(p.fechadesembolso, 'HH:mm:ss')   AS 'Hora_desembolso',
	
					pla.descripcion as 'Planilla', 
                	u.IdUsuario as 'User_Desemb',
                    AE.CIIU
                
                FROM prestamo AS p
                
                INNER JOIN socio AS s             ON s.codsocio = p.codsocio
                LEFT JOIN usuario AS u           ON p.CodUsuario = u.CodUsuario
                LEFT JOIN planilla AS pla         ON p.codplanilla = pla.codplanilla
                LEFT JOIN ActividadEconomica AS AE ON S.CodActividadEconomica = AE.CodActividad

                WHERE CONVERT(VARCHAR(10),p.fechadesembolso,112) >= '20000101'
                
                ORDER BY p.fechadesembolso DESC    
                '''
    
    df_desembolsos = pd.read_sql_query(query, conn)
    conn.close()
    del conn
    
    df_desembolsos = df_desembolsos.drop_duplicates(subset = ['pagare_fincore'], keep = 'first')

    del query

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
        FORMAT(precuo.FechaCreacion, 'dd/MM/yyyy'),
        precuo.CodEstado as 'Estado cuota',
    	
     	iif(cdet.CodMoneda='95','DÓLAR','SOLES') AS 'moneda',
    	
     	iif(cdet.CodMoneda = '95', tcsbs.tcsbs, 1) AS 'TC_SBS',
    
     	FORMAT(ccab.fecha, 'dd/MM/yyyy') AS 'fecha_cob', 
     	ccab.fecha AS 'fecha_cob_datetime',
        cdet.Capital, 
     	cdet.aporte as 'Aporte',
     	cdet.interes AS 'INT_CUOTA', 
     	cdet.InteresCompensatorio as 'IntCompVencido', 
     	cdet.Mora AS 'INTCOMP_MORA', 
     	cdet.GastoCobranza, 
     	cdet.FondoContigencia+cdet.MoraAnterior+cdet.GastoTeleOperador+cdet.GastoJudicial+cdet.GastoLegal+cdet.GastoOtros AS 'GTO_OTROS',
     	cdoc.numeroOperacion,
     	cdoc.numeroOperacionDestino, --tmdet.descripcion as TipoDocmto, 
     	pre.FechaVentaCartera, 
     	pre.FechaCastigo, 
     	cdoc.codestado, 
     	cDOC.NumeroOperacionDestino, 
     	CCAB.CODMEDIOPAGO, 
     	tmdet.descripcion as 'tipoPago'    
    
FROM CobranzaDet AS cdet 
		INNER JOIN prestamoCuota     AS precuo  ON precuo.CodprestamoCuota = cdet.CodprestamoCuota
		INNER JOIN CobranzaCab       AS ccab    ON ccab.CodCobranzaCab = cdet.CodCobranzaCab
		INNER JOIN Prestamo          AS pre     ON pre.codPrestamo = precuo.CodPrestamo 
		LEFT JOIN TipoCambioSBS      AS tcsbs   ON (YEAR(ccab.fecha) = tcsbs.Anno) AND (MONTH(ccab.fecha) = tcsbs.MES)
		LEFT JOIN CobranzaDocumento  AS cdoc    ON ccab.CodCobranzaDocumento = cdoc.CodCobranzaDocumento	
		LEFT JOIN TablaMaestraDet    AS tmdet   ON tmdet.CodTablaDet = ccab.CodMedioPago

WHERE CONVERT(VARCHAR(10), ccab.fecha, 112) <= '{fecha_corte}'

ORDER BY ccab.fecha DESC;	


    '''
    
    df_cobranza = pd.read_sql_query(query, conn)
    
    conn.close()
    del query

    df_cobranza = df_cobranza[df_cobranza['fecha_cob_datetime'] <= pd.Timestamp(fecha_corte)]

#%% CIS y MON

filas_original1 = cuotas[['CCR', 'NCUO']]
filas_original1 = cuotas['CCR'].unique()

cod_socios = df_desembolsos[['pagare_fincore', 'codigosocio', 'moneda']]
cod_socios = cod_socios[~pd.isna(cod_socios['codigosocio'])]

cuotas = cuotas.merge(cod_socios,
                      left_on  = 'CCR',
                      right_on = 'pagare_fincore',
                      how      = 'inner')             # ojo que puede que estemos eliminando a algunos
cuotas = cuotas[~pd.isna(cuotas['codigosocio'])]

filas_original2 = cuotas[['CCR', 'NCUO']]
filas_original2 = cuotas['CCR'].unique()

if filas_original1.shape[0] - filas_original2.shape[0] > 0:
    print('créditos eliminados (investigar): ')
    diferencia = list(set(filas_original1) - set(filas_original2))
    print(diferencia)

cuotas['CIS'] = cuotas['codigosocio']
cuotas['MON'] = cuotas['moneda']

del cuotas['codigosocio']
del cuotas['pagare_fincore']
del cuotas['moneda']

#%% FCAN fecha de cancelación
cuotas['id'] = cuotas['CCR'] + '-' + cuotas['NCUO']

f_cob       = df_cobranza[['PagareFincore', 'numerocuota', 'fecha_cob']]
f_cob       = f_cob.sort_values(by = ['fecha_cob'], ascending = [False])
f_cob['id'] = f_cob['PagareFincore'] + '-' + f_cob['numerocuota'].astype(str)
f_cob       = f_cob.drop_duplicates(subset = ['id'], keep = 'first')

cuotas = cuotas.merge(f_cob[['id', 'fecha_cob']],
                      on  = 'id',
                      how = 'left')

def FCAN1(cuotas):
    if cuotas['Pagado'] == '9':
        return cuotas['fecha_cob']
    else: 
        return '00/00/0000'
cuotas['FCAN'] = cuotas.apply(FCAN1, axis = 1)
del cuotas['fecha_cob']

###############################################################################
# f_crea       = df_cobranza[['PagareFincore', 'numerocuota', 'fecha_cob']]
# f_crea       = f_cob.sort_values(by = ['fecha_cob'], ascending = [False])
# f_crea['id'] = f_cob['PagareFincore'] + '-' + f_cob['numerocuota'].astype(str)
# f_crea       = f_cob.drop_duplicates(subset = ['id'], keep = 'first')

# cuotas = cuotas.merge(f_cob[['id', 'fecha_cob']],
#                       on  = 'id',
#                       how = 'left')

# def FCAN1(cuotas):
#     if cuotas['Pagado'] == '9':
#         return cuotas['fecha_cob']
#     else: 
#         return '00/00/0000'
# cuotas['FCAN'] = cuotas.apply(FCAN1, axis = 1)
# del cuotas['fecha_cob']












'''



select top 1000 CodEstado,* from PrestamoCuota
where CodEstado = 1003

CodEstado = 22 -- cancelado
1003 = -- cuota cero amortización de capital

---- para los 1003 (cuotas reprogramadas)
select * from PrestamoCuota
where CodPrestamo = 1890
and CodEstado not in ( 379 , 24)
order by CodPrestamoCuota




'''







