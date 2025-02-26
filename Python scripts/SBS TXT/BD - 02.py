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
cuotas = pd.read_csv('prppg 12-2024.csv',
                     dtype = str)

cuotas.dropna(subset = [ 'MCUO' ,
                         'SIC'  ,
                         'SCOM' ,
                         'TCUO'   ],
            inplace = True  ,
            how     = 'all')

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
					p.montosolicitado as 'Otorgado', 
					iif(p.CodMoneda='95', tcsbs.tcsbs, 1) as 'TC_SBS',
					p.montosolicitado * iif(p.CodMoneda='95', tcsbs.tcsbs, 1) AS 'Monto Otorgado en soles',
					--------------------------------------------------------------<
					p.TEM, 
					p.NroPlazos, 
					p.CuotaFija,  
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

				LEFT JOIN TipoCambioSBS AS TCSBS
				on (year(p.fechadesembolso) = tcsbs.Anno) and (month(p.fechadesembolso) = tcsbs.MES)

                WHERE CONVERT(VARCHAR(10),p.fechadesembolso,112) >= '20000101'
                
                ORDER BY p.fechadesembolso DESC    
                
                
                '''
    
    df_desembolsos = pd.read_sql_query(query, conn)
    conn.close()
    del conn
    
    df_desembolsos = df_desembolsos.drop_duplicates(subset = ['pagare_fincore'], keep = 'first')

    del query

dolares = df_desembolsos[df_desembolsos['moneda'] == '2']


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
    	precuo.CodprestamoCuota,

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
df_cobranza['CodprestamoCuota'] = df_cobranza['CodprestamoCuota'].astype(str)

f_cob = df_cobranza[['PagareFincore', 'numerocuota', 'fecha_cob', 'CodprestamoCuota', 'tipoPago']]
f_cob = f_cob.sort_values(by = ['fecha_cob'], ascending = [False])
f_cob = f_cob.drop_duplicates(subset = ['CodprestamoCuota'], keep = 'first')

cuotas = cuotas.merge(f_cob[['CodprestamoCuota', 'fecha_cob', 'tipoPago']],
                      on  = 'CodprestamoCuota',
                      how = 'left')

def FCAN1(cuotas):
    if cuotas['Pagado'] == '9':
        return cuotas['fecha_cob']
    else: 
        return '00/00/0000'
cuotas['FCAN'] = cuotas.apply(FCAN1, axis = 1)
del cuotas['fecha_cob']

def FCAN2(cuotas):
    if cuotas['CodEstado'] == '1003':
        return cuotas['FechaCreacionTXT']
    else:
        return cuotas['FCAN']
cuotas['FCAN'] = cuotas.apply(FCAN2, axis = 1)

#%% DAKC
f_corte = fecha_corte[6:8] + '/' + fecha_corte[4:6] + '/' + fecha_corte[0:4]

def safe_to_datetime(series):
    return pd.to_datetime(series.replace("00/00/0000", f_corte), format="%d/%m/%Y", errors="coerce")

# Reemplazando nulos en FCAN por FVEP (son cuotas con condonaciones)
cuotas["FCAN"] = cuotas["FCAN"].fillna(cuotas["FVEP"])

# Aplicar la conversión a datetime
cuotas["FCAN dt"] = safe_to_datetime(cuotas["FCAN"])
cuotas["FVEP dt"] = safe_to_datetime(cuotas["FVEP"])

# Calcular la diferencia en días
cuotas["DIFERENCIA_DIAS"] = (cuotas["FCAN dt"] - cuotas["FVEP dt"]).dt.days

# Reemplazar valores negativos por 0
cuotas["DIFERENCIA_DIAS"] = cuotas["DIFERENCIA_DIAS"].clip(lower=0)
cuotas["DIFERENCIA_DIAS"] = cuotas["DIFERENCIA_DIAS"].astype(int)

cuotas['DAKC'] = cuotas["DIFERENCIA_DIAS"]

#%% FOCAN forma de cancelación

# def FOCAN(cuotas):
#     if cuotas['tipoPago'] in ['EFECTIVO']:
#         return '1'
#     if cuotas['tipoPago'] in ['DEPOSITO', 'TRANSFERENCIA']:
#         return '2'
#     if cuotas['tipoPago'] in ['REFINANCIAMIENTO']:
#         return '3'
#     if cuotas['tipoPago'] in ['NOTA DE CREDITO']:
#         return '4'
#     if cuotas['tipoPago'] in ['RETENCIONES', 'OTROS', 'CHEQUE', 'FONDO PREVISIONAL', 'RECIBO']:
#         return '5'
# cuotas['FOCAN'] = cuotas.apply(FOCAN, axis = 1)

# Diccionario de mapeo
tipo_pago_mapeo = {
    'EFECTIVO': '1',
    'DEPOSITO': '2', 'TRANSFERENCIA': '2',
    'REFINANCIAMIENTO': '3',
    'NOTA DE CREDITO': '4',
    'RETENCIONES': '5', 'OTROS': '5', 'CHEQUE': '5',
    'FONDO PREVISIONAL': '5', 'RECIBO': '5'
}

# Aplicar el mapeo de forma vectorizada para mejorar rendimiento
cuotas['FOCAN'] = cuotas['tipoPago'].map(tipo_pago_mapeo)

#%%%
# Parte 2 eliminación de cuotas con cero en capital e interés
cuotas['MCUO'] = cuotas['MCUO'].astype(float)
cuotas['SIC']  = cuotas['SIC'].astype(float)
cuotas['SCOM'] = cuotas['SCOM'].astype(float)
cuotas['TCUO'] = cuotas['TCUO'].astype(float)

def eliminacion(cuotas):
    # if (cuotas['NCUO'] == '0') and (cuotas['MCUO'] == 0) and (cuotas['SIC'] == 0) and (cuotas['SCOM'] == 0) and (cuotas['TCUO'] == 0):
    #     return 'eliminar'
    if (cuotas['NCUO'] != '0') and(cuotas['MCUO'] == 0) and (cuotas['SIC'] == 0) and (cuotas['SCOM'] == 0) and (cuotas['TCUO'] == 0):
        return 'eliminar'

    else:
        return 'mantener'
cuotas['fil_1'] = cuotas.apply(eliminacion, axis = 1)

# cuotas = cuotas[cuotas['fil_1'] == 'mantener']
eliminados = cuotas[cuotas['fil_1'] == 'eliminar']
# aver = cuotas[cuotas['CCR'] == '00000333' ]

#%% agregando filas
cuotas['orden original'] = range(1, len(cuotas) + 1)

# reenumeración de cuotas
cuotas['nro cuota generado'] = cuotas.groupby('CCR').cumcount()

# créditos a los que le falta la cuota cero
con_cuota_cero = cuotas[ (cuotas['NCUO'] == '0') & (cuotas['nro cuota generado'] == 0) & (cuotas['MCUO'] == 0)]

sin_cuotas = cuotas[~cuotas['CCR'].isin(list(con_cuota_cero['CCR']))]
sin_cuotas = sin_cuotas.drop_duplicates(subset = ['CCR'], keep = 'first')

cuotas = cuotas[~cuotas['orden original'].isin(con_cuota_cero['orden original'])]

sin_cuotas['NCUO']  = '0'
sin_cuotas['MCUO']  =  0
sin_cuotas['SIC']   =  0
sin_cuotas['SCOM']  =  0
sin_cuotas['TCUO']  =  0
sin_cuotas['FVEP']  = '00/00/0000'
sin_cuotas['FCAN']  = '00/00/0000'
sin_cuotas['DAKC']  =  0
sin_cuotas['FOCAN'] = ''

cuotas_cero = pd.concat([sin_cuotas, con_cuota_cero], ignore_index = True)

cuotas_cero['FCAN']  = '00/00/0000'


###############################################################################
def arreglo_negativos(cuotas):
    if cuotas['SIC'] < 0:
        return cuotas['MCUO'] + cuotas['SIC']
    else:
        return cuotas['MCUO']
cuotas['MCUO'] = cuotas.apply(arreglo_negativos, axis = 1)
cuotas['SIC']  = cuotas['SIC'].clip(lower = 0)

###############################################################################
suma_cap = cuotas.pivot_table(index   = 'CCR',
                              values  = 'MCUO',
                              aggfunc = 'sum').reset_index()
suma_cap.rename(columns = {'MCUO':'sumMCUO'}, inplace = True)

suma_cap = suma_cap.merge(df_desembolsos[['pagare_fincore', 'Otorgado']],
                          left_on  = 'CCR',
                          right_on = 'pagare_fincore',
                          how      = 'left')

alerta = suma_cap[pd.isna(suma_cap['Otorgado'])]
if alerta.shape[0] > 0:
    print('algún crédito no aparece en la base de datos')

suma_cap['Dif cuadre cap'] = suma_cap['sumMCUO'] - suma_cap['Otorgado']

alerta_dif_cuadre = suma_cap[suma_cap['Dif cuadre cap'] < 0]
if alerta_dif_cuadre.shape[0] > 0:
    print('el cuadre resulta negativo')

# aver = cuotas[cuotas['CCR'] == '00118890']
aver2 = suma_cap[suma_cap['pagare_fincore'] == '00118890']

#%%
print('fin')

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
