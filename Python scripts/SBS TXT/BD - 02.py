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
from datetime import datetime

import warnings
warnings.filterwarnings('ignore')

#%%
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\SBS TXT\\BD-02\\prppgs (insumo)')

prppg       = 'prppg 03-2023.csv'
fecha_corte = '20230331' # FÓRMATO SQL

bd01 = 'C:/Users/sanmiguel38/Desktop/SBS TXT/BD-01/2023 03 31/20523941047_BD01_202303.txt'

CREAR_TXT = True

#%% hora inicio
print('hora inicio:')
print(datetime.now().strftime("%H:%M:%S"))

#%%
cuotas = pd.read_csv(prppg,
                     dtype = str)

cuotas.dropna(subset = [  'MCUO' ,
                          'SIC'  ,
                          'SCOM' ,
                          'TCUO'   ],
            inplace = True  ,
            how     = 'all')

cuotas = cuotas[cuotas['CodEstado'] != '346'] # eliminando cuotas de capitalización de interés (porque ya lo estoy generando yo)

cuotas.rename(columns = { "CodPrestamoCuota" : "CodprestamoCuota"}, inplace = True)
cuotas.rename(columns = { "PagadoPP2"        : "Pagado"}, inplace = True)

#%%
base01 = pd.read_csv(bd01,
                     dtype = str,
                     sep = "\t")
 
#%%
if 'df_desembolsos' not in globals():
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
                	RIGHT(CONCAT('0000000',p.numero),8) as 'pagare_fincore',
                	p.fechadesembolso,
					p.montosolicitado as 'Otorgado', 
					iif(p.CodMoneda='95', tcsbs.tcsbs, 1) as 'TC_SBS',
					p.montosolicitado * iif(p.CodMoneda='95', tcsbs.tcsbs, 1) AS 'Monto Otorgado en soles',
					--------------------------------------------------------------<
					p.TEM, 
					p.NroPlazos, 
					p.CuotaFija,  
                	iif(p.codmoneda = 94,'1','2') as 'moneda', 

                	FORMAT(p.fechadesembolso, 'yyyy-MM-dd') AS 'SoloFecha',
                    FORMAT(p.fechadesembolso, 'HH:mm:ss')   AS 'Hora_desembolso',
	
					pla.descripcion as 'Planilla', 
                	u.IdUsuario as 'User_Desemb',
                    AE.CIIU,

					p.fechaventacartera,
					P.FechaCastigo,
                    
                    p.fechaCancelacion

                FROM prestamo AS p
                
                INNER JOIN socio AS s              ON s.codsocio = p.codsocio
                LEFT JOIN usuario AS u             ON p.CodUsuario = u.CodUsuario
                LEFT JOIN planilla AS pla          ON p.codplanilla = pla.codplanilla
                LEFT JOIN ActividadEconomica AS AE ON S.CodActividadEconomica = AE.CodActividad

				LEFT JOIN TipoCambioSBS AS TCSBS
				ON (year(p.fechadesembolso) = tcsbs.Anno) and (month(p.fechadesembolso) = tcsbs.MES)

                WHERE CONVERT(VARCHAR(10),p.fechadesembolso,112) <= '{fecha_corte}'
                
                ORDER BY p.fechadesembolso DESC    

                '''
    
    df_desembolsos = pd.read_sql_query(query, conn)
    conn.close()
    del conn
    
    df_desembolsos = df_desembolsos.drop_duplicates(subset = ['pagare_fincore'], keep = 'first')

    del query

    # dolares = df_desembolsos[df_desembolsos['moneda'] == '2']
    # FILTRACIÓN DE CASTIGADOS Y VENDIDOS
    castigados_vendidos = df_desembolsos[ (~pd.isna(df_desembolsos['fechaventacartera'])) |  (~pd.isna(df_desembolsos['FechaCastigo']))]
    castigados_vendidos = castigados_vendidos[(castigados_vendidos['fechaventacartera'] <= pd.Timestamp(fecha_corte))  |  (castigados_vendidos['FechaCastigo'] <= pd.Timestamp(fecha_corte))]

    desembolsados_posteriores = df_desembolsos[df_desembolsos['fechadesembolso'] > pd.Timestamp(fecha_corte)]
    
#%% eliminando castigados y vendidos de las cuotas
cuotas = cuotas[ ~cuotas['CCR'].isin(castigados_vendidos['pagare_fincore'])]    
  
cuotas = cuotas[ ~cuotas['CCR'].isin(desembolsados_posteriores['pagare_fincore'])]  

cancelados = df_desembolsos[ ~pd.isna(df_desembolsos['fechaCancelacion']) ]

#%% COBRANZA

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

#%% FECHA_CREACIÓN

if 'df_cuotas_fecha_creacion_txt' not in globals():
    datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')
    
    server      = datos['DATOS'][0]
    username    = datos['DATOS'][2]
    password    = datos['DATOS'][3]
    
    conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'
    conn = pyodbc.connect(conn_str)
    
    query = '''
    SELECT  top 1000
    
    	CodPrestamoCuota                    AS 'CodprestamoCuota', 
        FechaCreacion,
        FORMAT(FechaCreacion, 'dd/MM/yyyy') AS 'FechaCreacionTXT'
    
    FROM PrestamoCuota

    '''
    
    df_fdc_txt = pd.read_sql_query(query, conn,dtype = str,)
    
    conn.close()
    del query

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

cuotas = cuotas.merge(f_cob[[    'CodprestamoCuota', 'fecha_cob', 'tipoPago']],
                      left_on  = 'CodprestamoCuota',
                      right_on = 'CodprestamoCuota',
                      how = 'left')

cuotas = cuotas.merge(df_fdc_txt[['CodprestamoCuota', 'FechaCreacionTXT']],
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

def FCAN3(cuotas):
    if (cuotas['Pagado'] == '9') and (pd.isna(cuotas['FCAN'])):
        return cuotas["FVEP"]
    else:
        return cuotas['FCAN']
cuotas['FCAN'] = cuotas.apply(FCAN3, axis = 1)

contiene_guion = cuotas['FCAN'].astype(str).apply(lambda x: "-" in x)
cont = cuotas[contiene_guion]
if cont.shape[0] > 0:
    print('''alerta, FCAN contiene guiones (debe ser solo separado por "/")''')
canc_nul= cuotas[pd.isna(cuotas["FCAN"])]
if canc_nul.shape[0] > 0:
    print('alerta, hay fechas de cancelación nulas, revisar')
del contiene_guion

#%% DAKC
f_corte = fecha_corte[6:8] + '/' + fecha_corte[4:6] + '/' + fecha_corte[0:4]

def safe_to_datetime(series):
    return pd.to_datetime(series.replace("00/00/0000", f_corte), format = "%d/%m/%Y", errors = "coerce")

cuotas["FCAN2"] = safe_to_datetime(cuotas["FCAN"])
cuotas["FVEP2"] = safe_to_datetime(cuotas["FVEP"])

fechas_vencimiento_nulas = cuotas[pd.isna(cuotas["FVEP2"])]
if fechas_vencimiento_nulas.shape[0] > 0:
    print('alerta, hay fechas de vencimiento nulas, revisar')
fechas_vencimiento_nulas = cuotas[pd.isna(cuotas["FCAN2"])]
if fechas_vencimiento_nulas.shape[0] > 0:
    print('alerta, hay fechas de cancelación nulas, revisar')

# Calcular la diferencia en días
cuotas["DIFERENCIA_DIAS"] = (cuotas["FCAN2"] - cuotas["FVEP2"]).dt.days

del cuotas["FCAN2"]
cuotas.rename(columns = {"FVEP2":'FVEP dt'}, inplace = True)

# Reemplazar valores negativos por 0
cuotas["DIFERENCIA_DIAS"] = cuotas["DIFERENCIA_DIAS"].clip(lower = 0)
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
    'EFECTIVO':         '1',
    'DEPOSITO':         '2', 
    'TRANSFERENCIA':    '2',
    'REFINANCIAMIENTO': '3',
    'NOTA DE CREDITO':  '4',
    'RETENCIONES':      '5', 
    'OTROS':            '5', 
    'CHEQUE':           '5',
    'FONDO PREVISIONAL':'5', 
    'RECIBO':           '5'
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

cuotas = cuotas[cuotas['fil_1'] == 'mantener']

# eliminados = cuotas[cuotas['fil_1'] == 'eliminar'] # en teoría esto no sirve para nada
# aver = cuotas[cuotas['CCR'] == '00000333' ]

#%% agregando filas
cuotas['orden original'] = range(1, len(cuotas) + 1)

# reenumeración de cuotas
cuotas['nro cuota generado'] = cuotas.groupby('CCR').cumcount()

# créditos a los que le falta la cuota cero
con_cuota_cero = cuotas[ (cuotas['NCUO'] == '0') & (cuotas['nro cuota generado'] == 0) & (cuotas['MCUO'] == 0) & (cuotas['Pagado'] != '9')]

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
sin_cuotas['Pagado']= '0'

## FECHA DE VENCIMIENTO PARA LAS CUOTAS CERO GENERADAS
min_fecha = cuotas.pivot_table(values  = 'FVEP dt',
                               index   = 'CCR',
                               aggfunc = 'min').reset_index()
min_fecha.rename(columns = {'FVEP dt':'fecha mínima'}, inplace = True)
###################################################################################
from datetime import timedelta                                                   ##
from dateutil.relativedelta import relativedelta                                 ##
                                                                                 ##
def restar_30_dias(fecha):                                                       ##
    # Restar 30 días directamente a objetos datetime/Timestamp                   ##
    nueva_fecha = fecha - timedelta(days = 30)                                   ##
    return nueva_fecha                                                           ##
                                                                                 ##
def restar_un_mes(fecha):                                                        ##
    # Restar un mes completo usando relativedelta                                ##
    nueva_fecha = fecha - relativedelta(months = 1)                              ##
    return nueva_fecha                                                           ##
                                                                                 ##
min_fecha['Fecha un mes antes'] = min_fecha['fecha mínima'].apply(restar_un_mes) ##
###################################################################################
# ahora procedemos a compararlo con la fecha de desembolso
m_desem = df_desembolsos[['pagare_fincore', 'fechadesembolso']]
min_fecha = min_fecha.merge(df_desembolsos[['pagare_fincore', 'fechadesembolso']],
                            left_on  = 'CCR',
                            right_on = 'pagare_fincore',
                            how      = 'left')
def fecha_cuota_cero(min_cuota):
    if min_cuota['Fecha un mes antes'] > min_cuota['fechadesembolso']:
        return min_cuota['Fecha un mes antes']
    else:
        return min_cuota['fechadesembolso']
min_fecha['fecha cuota cero'] = min_fecha.apply(fecha_cuota_cero, axis = 1)

sin_cuotas = sin_cuotas.merge(min_fecha[['CCR', 'fecha cuota cero']],
                              on  = 'CCR',
                              how = 'left')
if sin_cuotas[pd.isna(sin_cuotas['fecha cuota cero'])].shape[0] > 0:
    print('revisar, aquí debe haber match completo')

sin_cuotas['FVEP'] = sin_cuotas['fecha cuota cero'].dt.strftime('%d/%m/%Y')

###############################################################################
cuotas_cero = pd.concat([sin_cuotas, con_cuota_cero], ignore_index = True)

# cuotas_cero['FCAN']       = '00/00/0000'
cuotas_cero['EsFaltante'] = True

###############################################################################
def arreglo_negativos(cuotas):
    if cuotas['SIC'] < 0:
        return cuotas['MCUO'] + cuotas['SIC']
    else:
        return cuotas['MCUO']
cuotas['MCUO'] = cuotas.apply(arreglo_negativos, axis = 1)
cuotas['SIC']  = cuotas['SIC'].clip(lower = 0) # coloca cero en interés negativo

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
suma_cap["Dif cuadre cap"] = suma_cap["Dif cuadre cap"].round(2)
suma_cap["Dif cuadre cap"] = suma_cap["Dif cuadre cap"].apply(lambda x: 0 if abs(x) < 1e-10 else x)

alerta_dif_cuadre = suma_cap[suma_cap['Dif cuadre cap'] < 0]
if alerta_dif_cuadre.shape[0] > 0:
    print('el cuadre resulta negativo')
# aver = cuotas[cuotas['CCR'] == '00118890']
# aver2 = suma_cap[suma_cap['pagare_fincore'] == '00118890']

# =============================================================================
#  SE REQUIERE AJUSTE PUNTUAL para solucionar negativos <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# ajuste
alerta_dif_cuadre["Dif cuadre cap"] = alerta_dif_cuadre["Dif cuadre cap"].abs()
para_corregir = cuotas[cuotas['CCR'].isin(alerta_dif_cuadre['CCR'])]
para_corregir = para_corregir.drop_duplicates(subset = ['CCR'], keep = 'first')

cuotas = cuotas[~cuotas['orden original'].isin(list(para_corregir['orden original']))]
para_corregir = para_corregir.merge(alerta_dif_cuadre[['CCR', "Dif cuadre cap"]],
                                    on  = 'CCR',
                                    how = 'left')
para_corregir['MCUO'] = para_corregir['MCUO'] +  para_corregir['Dif cuadre cap']
para_corregir['TCUO'] = para_corregir['TCUO'] +  para_corregir['Dif cuadre cap']

print('negativos corregidos')
###############################################################################
cuotas_cero = cuotas_cero.merge(suma_cap[['CCR', 'Dif cuadre cap']],
                                on  = 'CCR',
                                how = 'left')

if cuotas_cero[pd.isna(cuotas_cero['Dif cuadre cap'])].shape[0] > 0:
    print('alerta, aquí siempre debe haber match completo')
    
cuotas_cero['SIC'] = cuotas_cero['Dif cuadre cap']
del cuotas_cero['Dif cuadre cap']
# =============================================================================

# UNIÓN TOTAL CON LAS CUOTAS CERO
cuotas = pd.concat([cuotas, cuotas_cero, para_corregir], ignore_index = True)
# para esta parte ya debería estar cuadrado todo

# ORDENAMIENTO
cuotas = cuotas.sort_values(by = ['CCR', 'EsFaltante', 'orden original'], ascending = [True, False, True])

#%% reenumeración final
cuotas['CodEstado'].unique()

def calcular_nueva_numeracion(grupo):
    nueva_numeracion = []
    contador = 0
    for index, row in grupo.iterrows():
        if (row['NCUO'] == '0' and row['nro cuota generado'] == 0) or \
        (row['NCUO'] == '0' and row["CodEstado"] in [ '1003', 
                                                      '379' 
                                                      ]):  
            # Si se cumplen todas las condiciones, reiniciamos la numeración
            nueva_numeracion.append(0)
        else:
            # Si no, incrementamos la numeración desde donde se quedó
            contador += 1
            nueva_numeracion.append(contador)
    
    grupo["nueva_numeracion"] = nueva_numeracion
    return grupo

cuotas = cuotas.groupby("CCR", group_keys=False).apply(calcular_nueva_numeracion)

cuotas['numeración original prppg'] = cuotas['NCUO']

cuotas['NCUO'] = cuotas["nueva_numeracion"]

#%%
bd02a = cuotas[cuotas['CCR'].isin(base01['CCR'])]

#%% EXCEL DE LA BD02-A
if CREAR_TXT == True:
    nombre = '20523941047_BD02A_' + fecha_corte[0:6]
    
    bd02a[['CIS',  'CCR',   'NCUO',  'MON',  'MCUO', 
           'SIC',  'SCOM',  'SEGS',  'SIM',  'TCUO', 
           'FVEP', 'FCAN',  'SCONK', 'SCONINT', 
           'DAKC', 'FOCAN', 'SCA']].to_csv(nombre + '.txt', 
                                           sep      = '\t', 
                                           index    = False, 
                                           encoding = 'utf-8')
    print('BD02A creado')
    print('')

    print(datetime.now().strftime("%H:%M:%S"))
else:
    print('no se ha creado BD02A')

#%%
# =============================================================================
#  BD 02 - B
# =============================================================================
 
cuotas_c = cuotas[ ~cuotas['CCR'].isin(base01['CCR']) ]
cuotas_c = cuotas_c.rename(columns = lambda col: col + "_C")

cuotas_c = cuotas_c[['CIS_C',     'CCR_C',    'NCUO_C',   'MON_C',   'MCUO_C', 
                     'SIC_C',     'SCOM_C',   'SEGS_C',   'SIM_C',   'TCUO_C', 
                     'FVEP_C',    'FCAN_C',   'DAKC_C',   'SCA_C',   'SCONK_C', 
                     'SCONINT_C', 'FOCAN_C',  'numeración original prppg_C']]

cuotas_c = cuotas_c.merge(cancelados[['pagare_fincore' ,'fechaCancelacion']],
                          left_on  = 'CCR_C',
                          right_on = 'pagare_fincore',
                          how      = 'inner') # esto eliminaría algunos créditos que no aparecen ni el la bd01 ni como cancelados

def fecha_canc(cuotas_c):
    if cuotas_c['FCAN_C'] == '00/00/0000':
        return cuotas_c['FVEP_C']
    else:
        return cuotas_c['FCAN_C']
cuotas_c['FCAN_C'] = cuotas_c.apply(fecha_canc, axis = 1)

def forma_can(cuotas_c):
    if pd.isna(cuotas_c['FOCAN_C']):
        return '5'
    else:
        return cuotas_c['FOCAN_C']
cuotas_c['FOCAN_C'] = cuotas_c.apply(fecha_canc, axis = 1)

#%% EXCEL DE LA BD02-A
if CREAR_TXT == True:
    nombre = '20523941047_BD02B_' + fecha_corte[0:6]
    
    cuotas_c[['CIS_C',     'CCR_C',    'NCUO_C',   'MON_C',   'MCUO_C', 
              'SIC_C',     'SCOM_C',   'SEGS_C',   'SIM_C',   'TCUO_C', 
              'FVEP_C',    'FCAN_C',   'DAKC_C',   'SCA_C',   'SCONK_C', 
              'SCONINT_C', 'FOCAN_C']].to_csv(nombre + '.txt', 
                                       sep      = '\t', 
                                       index    = False, 
                                       encoding = 'utf-8')
    print('BD02B creado')
    print('')

    print(datetime.now().strftime("%H:%M:%S"))
    print(f'TXT correspondientes a {fecha_corte}')
else:
    print('no se ha creado BD02B')

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



