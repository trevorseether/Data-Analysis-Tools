# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 13:05:08 2024

@author: Joseph Montoya
"""

# =============================================================================
# SALDO DIARIO
# =============================================================================

import pandas as pd
import pyodbc
import os
import warnings
warnings.filterwarnings('ignore')

#%%
'Fecha de corte para el anexo06'####################
fecha_corte_anx06 = '20240430'                     #
####################################################

tabla_actual = 'saldos_diarios.dbo.[SALDOS_DIARIOS_2024_05]'
'Fechas para la cobranza y nuevos desembolsos'######
fecha_inicio = '20240501'                          #
fecha_hoy    = '20240531'                          ## se pone 4 días antes del día de hoy
####################################################

'Directorio de trabajo'#############################
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\saldos diarios')
####################################################

'Incremento de días mora'###########################
incremento = int(fecha_hoy[-2:])                   #
####################################################

#%%
if 'conn_anx06' not in locals():
    conn_anx06 = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')
else:
    print("La conexión ya existe. No se estableció una nueva conexión.")

#%% SELECCIÓN DE LA FECHA MÁS RECIENTE EN LA BASE DE DATOS
fecha_corte_cobranza = fecha_hoy
# Nombre del DataFrame
nombre_data_frame = 'anx06'

# Verifica si el DataFrame ya existe en el entorno de pandas
if nombre_data_frame in globals() and isinstance(globals()[nombre_data_frame], pd.DataFrame):
    print(f"El DataFrame '{nombre_data_frame}' ya existe. No se ejecutará la consulta SQL.")
    df_anx06 = globals()[nombre_data_frame]
else:

    # Ejecuta la consulta SQL y crea el DataFrame
    df_anx06 = pd.read_sql_query(f'''
        SELECT 
            FechaCorte1,
            Nro_Fincore,
            Saldodecolocacionescreditosdirectos24,
            MontodeDesembolso22,
            FechadeDesembolso21,
            CapitalVigente26,
            CapitalVencido29,
            CapitalenCobranzaJudicial30,
 			CapitalRefinanciado28,
            SaldosdeCreditosCastigados38,
            0 AS 'CUOTA',
            DiasdeMora33,
            TipodeProducto43,
            NumerodeCuotasPagadas45,
            CASE
                WHEN TipodeProducto43 IN (15,16,17,18,19)          THEN 'PEQUEÑA EMPRESA'
                WHEN TipodeProducto43 IN (21,22,23,24,25,27,28,29) THEN 'MICRO EMPRESA'
                WHEN TipodeProducto43 IN (26)                      THEN 'EMPRENDE MUJER'
                WHEN TipodeProducto43 IN (95,96,97,98,99)          THEN 'MEDIANA EMPRESA'
                WHEN TipodeProducto43 IN (34,35,36,37,38,39)       THEN 'DXP'
                WHEN TipodeProducto43 IN (30,31,33)                THEN 'LD'
                WHEN TipodeProducto43 IN (32)                      THEN 'MULTIOFICIOS'
                WHEN TipodeProducto43 IN (41,45)                   THEN 'HIPOTECARIO'
            END AS 'PRODUCTO TXT',
            PLANILLA_CONSOLIDADA,
            originador,
            administrador
        FROM anexos_riesgos3..ANX06
        WHERE FechaCorte1 = '{fecha_corte_anx06}'
    ''', conn_anx06)

    # Asigna el DataFrame a una variable global
    globals()[nombre_data_frame] = df_anx06

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

INNER JOIN socio as s on s.codsocio = p.codsocio
where CONVERT(VARCHAR(10),p.fechadesembolso,112) > '20100101' 
and s.codigosocio>0  
and p.codestado = 342
order by p.fechadesembolso desc

'''

df_cancelados = pd.read_sql_query(query, conn)

#%% CRÉDITOS DESEMBOLSADOS DURANTE EL PRESENTE MES
query = f'''
SELECT

	RIGHT(CONCAT('0000000',p.numero),8) as 'pagare_fincore',
	p.montosolicitado as 'MONTO_DESEMBOLSO',
    p.NroPlazos,
    0 as 'CUOTA',
    p.montosolicitado as 'saldo_cartera1',
	tm.descripcion as 'Estado',
	p.fechadesembolso,
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

    INNER JOIN socio              AS s    ON s.codsocio = p.codsocio
    LEFT JOIN sociocontacto       AS sc   ON sc.codsocio = s.codsocio
    LEFT JOIN planilla            AS pla  ON p.codplanilla = pla.codplanilla
    INNER JOIN grupocab           AS pro  ON pro.codgrupocab = p.codgrupocab
    INNER JOIN distrito           AS d    ON d.coddistrito = sc.coddistrito
    INNER JOIN provincia          AS pv   ON pv.codprovincia = d.codprovincia
    INNER JOIN departamento       AS dp   ON dp.coddepartamento = pv.coddepartamento
    INNER JOIN tablaMaestraDet    AS tm   ON tm.codtabladet = p.CodEstado
    LEFT JOIN grupocab            AS gpo  ON gpo.codgrupocab = pla.codgrupocab
    LEFT JOIN tablaMaestraDet     AS tm2  ON tm2.codtabladet = s.codestadocivil
    LEFT JOIN tablaMaestraDet     AS tm3  ON tm3.codtabladet = p.CodSituacion
    --INNER JOIN tablaMaestraDet  AS tm3  ON tm3.codtabladet = s.codcategoria
    INNER JOIN pais                       ON pais.codpais = s.codpais
    LEFT JOIN FINALIDAD           AS FI   ON FI.CODFINALIDAD = P.CODFINALIDAD
    LEFT JOIN TipoCredito         AS TC   ON tc.CodTipoCredito = p.CodTipoCredito
    INNER JOIN usuario            AS u    ON p.CodUsuario = u.CodUsuario
    INNER JOIN TablaMaestraDet    AS tm4  ON s.codestado = tm4.CodTablaDet
    --LEFT JOIN PrestamoCuota     AS pcu  ON p.CodPrestamo = pcu.CodPrestamo

where 
CONVERT(VARCHAR(10),p.fechadesembolso,112) BETWEEN '{fecha_inicio}' AND '{fecha_corte_cobranza}' 
and s.codigosocio>0  and p.codestado = 341
order by p.fechadesembolso DESC
'''
df_desembolsados = pd.read_sql_query(query, 
                                     conn,
                                     dtype = {'COD_FINALIDAD' : str})

# df_desembolsados['TipoCredito'] = df_desembolsados['TipoCredito'].astype(str)

#%% COBRANZA DEL MES
query = f'''
SELECT 
	right(concat('0000000',pre.numero),8)    AS 'PagareFincore',
	pre.FechaDesembolso                      AS 'FechaDesembolso',
	precuo.numerocuota                       AS 'numerocuota', 
	iif(cdet.CodMoneda='95','DÓLAR','SOLES') AS 'moneda', 
	ccab.fecha                               AS 'fecha_cob', 
	cdet.Capital                             AS 'Capital', 
	cdet.aporte                              AS 'Aporte',
	cdet.interes                             AS 'INT_CUOTA',
    fin.codigo                               AS 'codigo'
	
FROM   CobranzaDet AS cdet INNER JOIN prestamoCuota    AS precuo ON precuo.CodprestamoCuota = cdet.CodprestamoCuota
                           INNER JOIN CobranzaCab      AS ccab   ON ccab.CodCobranzaCab = cdet.CodCobranzaCab
                           INNER JOIN Prestamo         AS pre    ON pre.codPrestamo = precuo.CodPrestamo 
                           LEFT JOIN Planilla          AS pla    ON pre.CodPlanilla = pla.CodPlanilla
                           INNER JOIN Socio            AS soc    ON soc.CodSocio = pre.CodSocio
                           INNER JOIN finalidad        AS fin    ON fin.CodFinalidad = pre.CodFinalidad
                           INNER JOIN TipoCredito      AS tc     ON tc.CodTipoCredito = fin.CodTipoCredito
                           LEFT JOIN grupoCab          AS gr     ON gr.codGrupoCab = pre.codGrupoCab
						   --   LEFT JOIN CobranzaDocumento  AS cdoc  ON ccab.CodCobranzaDocumento = cdoc.CodCobranzaDocumento
						   --   INNER JOIN TablaMaestraDet   AS tmdet ON tmdet.CodTablaDet = cdoc.CodMedioPago (ORIGUINAL)
                           LEFT JOIN TablaMaestraDet         AS tmdet ON tmdet.CodTablaDet = ccab.CodMedioPago --(NUEVO ACTIVAR)

                           LEFT JOIN Empleado          AS empl    ON pre.CodAbogado = empl.CodEmpleado
                           LEFT JOIN TablaMaestraDet   AS tmdet5  ON pre.CodSituacion = tmdet5.CodTablaDet

                            -------
                            LEFT JOIN CobranzaDocumento  AS cdoc  ON ccab.CodCobranzaDocumento = cdoc.CodCobranzaDocumento
                            LEFT JOIN Cuenta             AS CU    ON CU.CodCuenta  = cdoc.CodCuentaDestino
                            LEFT JOIN NotaCredito        AS NC    ON ccab.CodNotaCredito = NC.CodNotaCredito
                            LEFT JOIN CobranzaDocumento  AS CDDNC ON NC.CodCobranzaDocumento = CDDNC.CodCobranzaDocumento
                            LEFT JOIN Cuenta             AS CUNC  ON CDDNC.CodCuentaDestino = CUNC.CodCuenta
                            --------

WHERE CONVERT(VARCHAR(10),ccab.fecha,112) BETWEEN '{fecha_inicio}' AND '{fecha_corte_cobranza}' and cdet.CodEstado <> 376   
ORDER BY ccab.fecha

'''
df_cobranza = pd.read_sql_query(query, conn)

#%% CRONOGRAMA DE LOS CRÉDITOS
query = '''
SELECT 	--TOP 1000
	RIGHT(CONCAT('0000000',A.numero),8) as 'pagare_fincore', 
	A.CodPrestamo,
	B.Periodo,
	B.NumeroCuota,
	B.NroPlazos,
	B.FechaVencimiento,
	B.FechaUltimoPago,
	B.Capital,
	B.Interes,
	B.Aporte,
	B.CuotaMensual
	 
FROM Prestamo AS A

LEFT JOIN PrestamoCuota AS B ON A.CodPrestamo = B.CodPrestamo
WHERE A.CodPrestamo	IS NOT NULL
AND a.codestado = 341
'''
df_cronograma = pd.read_sql_query(query, 
                                  conn)

#%%
# concatenamos los créditos del anexo06 con los nuevos desembolsos
desem_format = pd.DataFrame()

desem_format['Nro_Fincore']         = df_desembolsados['pagare_fincore'].copy()
desem_format['Saldodecolocacionescreditosdirectos24'] = df_desembolsados['MONTO_DESEMBOLSO'].copy()
desem_format['MontodeDesembolso22'] = df_desembolsados['MONTO_DESEMBOLSO'].copy()
desem_format['FechadeDesembolso21'] = df_desembolsados['fechadesembolso'].copy()
desem_format['CapitalVigente26']    = df_desembolsados['MONTO_DESEMBOLSO'].copy()
desem_format['CapitalVencido29']             = 0
desem_format['CapitalenCobranzaJudicial30']  = 0
desem_format['CapitalRefinanciado28']        = 0
desem_format['SaldosdeCreditosCastigados38'] = 0
desem_format['NumerodeCuotasPagadas45']      = 0
desem_format['CUOTA']                        = 0
desem_format['DiasdeMora33']                 = 0
desem_format['TipodeProducto43']     = df_desembolsados['COD_FINALIDAD'].copy()
desem_format['PRODUCTO TXT']         = ''
desem_format['PLANILLA_CONSOLIDADA'] = df_desembolsados['Planilla'].copy()
desem_format['originador']           = df_desembolsados['ORIGINADOR'].copy()
desem_format['administrador']        = df_desembolsados['ADMINISTRADOR'].copy()

#%%
desem_format.loc[desem_format['TipodeProducto43'] == '27', 'TipodeProducto43'] = '32'

prod_dxp  = ['34', '35', '36', '37', '38', '39']
prod_ld   = ['30', '31', '33']
prod_mic  = ['20', '21', '22', '23', '24', '25', '29']
prod_peq  = ['15', '16', '17', '18', '19']
prod_med  = ['95', '96', '97', '98', '99']
prod_hip  = ['41', '45']
prod_multi = ['32']
prod_empre = ['26']
def producto_txt(df):
    tipo_producto = df['TipodeProducto43']
    
    if tipo_producto in prod_dxp:
        return 'DXP'
    elif tipo_producto in prod_multi:
        return 'MULTIOFICIOS'
    elif tipo_producto in prod_empre:
        return 'EMPRENDE MUJER'
    elif tipo_producto in prod_ld:
        return 'LD'
    elif tipo_producto in prod_mic:
        return 'MICRO EMPRESA'
    elif tipo_producto in prod_peq:
        return 'PEQUEÑA EMPRESA'
    elif tipo_producto in prod_med:
        return 'MEDIANA EMPRESA'
    elif tipo_producto in prod_hip:
        return 'HIPOTECARIO'

desem_format['PRODUCTO TXT'] = desem_format.apply(producto_txt, axis = 1)

print('debe salir cero:')
print(desem_format[pd.isna(desem_format['PRODUCTO TXT'])].shape[0])

#%%
columnas = desem_format.columns

anx06_base = df_anx06[columnas]

df_concatenado = pd.concat([anx06_base, desem_format], ignore_index = True)

# quitamos créditos cancelados
df_concatenado = df_concatenado[~df_concatenado['Nro_Fincore'].isin(list(df_cancelados['pagare_fincore']))]

#%% calculamos la recaudación de los saldos de cartera
recau = df_cobranza.pivot_table(index   = 'PagareFincore',
                                values  = 'Capital',
                                aggfunc = 'sum') #mucho cuidado porque por defecto la función en 'avg'
recau = recau.reset_index()

# cobranza y sus productos
cob_cod_productos = df_cobranza[['PagareFincore', 'codigo']].drop_duplicates(subset = 'PagareFincore')

recau = recau.merge(cob_cod_productos,
                    on  = 'PagareFincore',
                    how = 'left')

recau = recau[['PagareFincore', 'Capital']]

#%% merge con la recaudación
df_mergeado = df_concatenado.merge(recau[['PagareFincore', 'Capital']],
                                   left_on  = 'Nro_Fincore',
                                   right_on = 'PagareFincore',
                                   how      = 'left')
del df_mergeado['PagareFincore']
df_mergeado['Capital'] = df_mergeado['Capital'].fillna(0)

#%%
# quitando la cobranza al saldo
def cob1(df):
    if (df['Saldodecolocacionescreditosdirectos24'] > 0):
        return df['Saldodecolocacionescreditosdirectos24'] - df['Capital']
    else:
        return df['Saldodecolocacionescreditosdirectos24']
        
df_mergeado['Saldodecolocacionescreditosdirectos24'] = df_mergeado.apply(cob1, axis = 1)

def vigentes(df):
    if (df['CapitalVigente26'] > 0) and \
       (df['CapitalVencido29'] == 0) and \
       (df['CapitalenCobranzaJudicial30'] == 0):
       return df['Saldodecolocacionescreditosdirectos24']
    else:
        return df['CapitalVigente26']
df_mergeado['CapitalVigente26'] = df_mergeado.apply(vigentes, axis=1)

#%% cuadramiento de valores negativos
cosas_que_no_cuadran = df_mergeado[df_mergeado['Saldodecolocacionescreditosdirectos24'] < 0]

print('SON CRÉDITOS QUE HAN AMORTIZADO MÁS CAPITAL QUE EL QUE TENÍAN PENDIENTE (⊙_⊙)？')
print(cosas_que_no_cuadran.shape[0])

fincore_no_cuadran = cosas_que_no_cuadran['Nro_Fincore']
df_mergeado.loc[df_mergeado['Nro_Fincore'].isin(list(fincore_no_cuadran)), 'Saldodecolocacionescreditosdirectos24'] = 0
df_mergeado.loc[df_mergeado['Nro_Fincore'].isin(list(fincore_no_cuadran)), 'CapitalVencido29'] = 0
df_mergeado.loc[df_mergeado['Nro_Fincore'].isin(list(fincore_no_cuadran)), 'CapitalenCobranzaJudicial30'] = 0
# pensándolo bien, mejor es eliminar estos créditos
df_mergeado = df_mergeado[~df_mergeado['Nro_Fincore'].isin(fincore_no_cuadran)]
#hasta aquí todo bien
#%%
df_mergeado.loc[(df_mergeado['CapitalVencido29'] > 0) & \
                (df_mergeado['CapitalRefinanciado28'] == 0),'CapitalVencido29'] = df_mergeado['CapitalVencido29'] - df_mergeado['Capital']
cosas_que_no_cuadran = df_mergeado[df_mergeado['CapitalVencido29'] < 0]

def cob2_vencidos(df):
    if (df['CapitalVencido29'] < 0) and\
        (df['CapitalRefinanciado28'] == 0):
        return df['CapitalVigente26'] + df['CapitalVencido29']
    else:
        return df['CapitalVigente26']
df_mergeado['CapitalVigente26'] = df_mergeado.apply(cob2_vencidos, axis=1)

df_mergeado.loc[df_mergeado['CapitalVencido29'] < 0,'CapitalVencido29'] = 0

#%% cap en cobranza judicial
df_mergeado.loc[df_mergeado['CapitalenCobranzaJudicial30'] > 0,'CapitalenCobranzaJudicial30'] = df_mergeado['CapitalenCobranzaJudicial30'] - df_mergeado['Capital']
# cosas_que_no_cuadran = df_mergeado[df_mergeado['CapitalenCobranzaJudicial30'] < 0]

def cob2_judicial(df):
    if (df['CapitalenCobranzaJudicial30'] < 0):
        return df['CapitalVigente26'] + df['CapitalenCobranzaJudicial30']
    else:
        return df['CapitalVigente26']
df_mergeado['CapitalVigente26'] = df_mergeado.apply(cob2_judicial, axis = 1)

#%% refinanciados
def refinanciados(df):
    if (df['CapitalRefinanciado28'] > 0) and \
       (df['CapitalVencido29'] == 0) and \
       (df['CapitalenCobranzaJudicial30'] == 0):
        return df['Saldodecolocacionescreditosdirectos24']
    else:
        return df['CapitalRefinanciado28']
df_mergeado['CapitalRefinanciado28'] = df_mergeado.apply(refinanciados, axis=1)

df_mergeado.loc[(df_mergeado['CapitalVencido29'] > 0) & \
                (df_mergeado['CapitalRefinanciado28'] > 0),'CapitalVencido29'] = df_mergeado['CapitalVencido29'] - df_mergeado['Capital']

def cob2_vencidos_refinanciados(df):
    if (df['CapitalVencido29'] < 0) and\
        (df['CapitalRefinanciado28'] > 0):
        return df['CapitalRefinanciado28'] + df['CapitalVencido29']
    else:
        return df['CapitalRefinanciado28']
df_mergeado['CapitalRefinanciado28'] = df_mergeado.apply(cob2_vencidos_refinanciados, axis=1)
df_mergeado.loc[df_mergeado['CapitalVencido29'] < 0,'CapitalVencido29'] = 0
    
# verificación
# decim = 10000
# wea = df_mergeado[(df_mergeado['Saldodecolocacionescreditosdirectos24']/decim).round(0) != \
#                   (df_mergeado['CapitalVigente26']/decim).round(0) + \
#                   (df_mergeado['CapitalVencido29']/decim).round(0) + \
#                   (df_mergeado['CapitalenCobranzaJudicial30']/decim).round(0) + \
#                   (df_mergeado['CapitalRefinanciado28']/decim).round(0)]

#%%
df_mergeado['FECHA_DÍA'] = pd.Timestamp(fecha_hoy)

#%% días de mora
def dias_mora(df):
    if (df['DiasdeMora33'] > 0) and \
       (df['CapitalVencido29'] > 0):
        return df['DiasdeMora33'] + incremento
    elif (df['DiasdeMora33'] > 0) and \
         (df['CapitalVencido29'] == 0):
        return 0
    else:
        return df['DiasdeMora33']
df_mergeado['DiasdeMora33'] = df_mergeado.apply(dias_mora, axis=1)

#%% incremento del capital vencido para MYPE
def aumento_vencido(df):
    if df['PRODUCTO TXT'] in ['MICRO EMPRESA', 'PEQUEÑA EMPRESA', 'MEDIANA EMPRESA']:
        if df['DiasdeMora33'] > 15:
            return df['Saldodecolocacionescreditosdirectos24']
        else:
            return df['CapitalVencido29']
    else:
        return df['CapitalVencido29']
df_mergeado['CapitalVencido29'] = df_mergeado.apply(aumento_vencido, axis=1)

df_mergeado.loc[(df_mergeado['CapitalVencido29'] > 0) & \
                (df_mergeado['PRODUCTO TXT'].isin(['MICRO EMPRESA', 'PEQUEÑA EMPRESA', 'MEDIANA EMPRESA'])),
                'CapitalVigente26'] = 0

df_mergeado.loc[(df_mergeado['CapitalVencido29'] > 0) & \
                (df_mergeado['PRODUCTO TXT'].isin(['MICRO EMPRESA', 'PEQUEÑA EMPRESA', 'MEDIANA EMPRESA'])),
                'CapitalRefinanciado28'] = 0

#%% INCREMENTO DEL CAPITAL VENCIDO PARA CONSUMO NO REVOLVENTE E HIPOTECARIO

df_mergeado['CapitalVencido29'] = df_mergeado['CapitalVencido29'].round(2)
df_mergeado['CapitalVigente26'] = df_mergeado['CapitalVigente26'].round(2)

#%%
# =============================================================================
# INCREMENTO DEL CAPITAL VENCIDO
# =============================================================================
# MERGE DE LOS CRONOGRAMAS CON LA CUOTA ACTUAL
df_mergeado.columns
crono_cap = df_cronograma.merge(df_mergeado[['Nro_Fincore', 'NumerodeCuotasPagadas45']],
                                left_on  = 'pagare_fincore',
                                right_on = 'Nro_Fincore',
                                how = 'left')

del crono_cap['Nro_Fincore']
crono_cap['NumerodeCuotasPagadas45'].fillna(0, inplace = True)

crono_cap['CUOTA SIGUIENTE'] = crono_cap['NumerodeCuotasPagadas45'] + 1

crono_1_cuota = crono_cap[crono_cap['NumeroCuota'] == crono_cap['CUOTA SIGUIENTE']]
crono_1_cuota = crono_1_cuota[['pagare_fincore', 'Capital']]
crono_1_cuota = crono_1_cuota.rename(columns = {'Capital' : 'Cap 1 cuota'})

crono_2_cuota = crono_cap[(crono_cap['NumeroCuota'] == crono_cap['CUOTA SIGUIENTE']) |
                          (crono_cap['NumeroCuota'] == crono_cap['CUOTA SIGUIENTE']+1)]
crono_2_cuota = crono_2_cuota[['pagare_fincore', 'Capital']]
crono_2_cuota = crono_2_cuota.rename(columns = {'Capital' : 'Cap 2 cuota'})

crono_2_cuota = crono_2_cuota.pivot_table(index   = 'pagare_fincore',
                                          values  = 'Cap 2 cuota',
                                          aggfunc = 'sum').reset_index()

crono_cuotas = crono_1_cuota.merge(crono_2_cuota,
                                   on  = 'pagare_fincore',
                                   how = 'left')

#%% INCREMENTO DEL CAPITAL VENCIDO PARA CONSUMO NO REVOLVENTE E HIPOTECARIO
df_mergeado = df_mergeado.merge(crono_cuotas,
                                left_on  = 'Nro_Fincore',
                                right_on = 'pagare_fincore',
                                how      = 'left')
del df_mergeado['pagare_fincore']

def vencido_real(df):
    if  (df['CapitalenCobranzaJudicial30']  == 0) and \
        (df['CapitalRefinanciado28']        == 0) and \
        (df['SaldosdeCreditosCastigados38'] == 0) and \
        (df['TipodeProducto43'] in ['30','31','32','33','34','35','36','37','38','39','41','45']):
        if (df['DiasdeMora33'] > 30) and (df['DiasdeMora33'] <= 60):
            return df['Cap 1 cuota']
        if (df['DiasdeMora33'] > 60) and (df['DiasdeMora33'] <= 90):
            return df['Cap 2 cuota']
        if (df['DiasdeMora33'] > 90):
            return df['Saldodecolocacionescreditosdirectos24']

        
df_mergeado.columns
df_mergeado['CapitalVencido29']      = df_mergeado['CapitalVencido29'].round(2)
df_mergeado['CapitalRefinanciado28'] = df_mergeado['CapitalRefinanciado28'].round(2)

'''
          [CapitalVigente26],
          [CapitalVencido29],
          [CapitalenCobranzaJudicial30],
          [CapitalRefinanciado28],
          [SaldosdeCreditosCastigados38],
'''

#%%
# REDUCCIÓN DEL SALDO CASTIGADO

def reduccion_castigado(df):
    if df['SaldosdeCreditosCastigados38'] > 0:
        if df['Capital'] > 0:
            return df['SaldosdeCreditosCastigados38'] - df['Capital']
        else:
            return df['SaldosdeCreditosCastigados38']
    else:
        return df['SaldosdeCreditosCastigados38']
    
df_mergeado['SaldosdeCreditosCastigados38'] = df_mergeado.apply(reduccion_castigado, axis = 1)

#%% SI QUEREMOS CONVERTIR EL DATAFRAME A EXCEL

# df_mergeado.to_excel(fecha_hoy + '.xlsx',
#                       index = False)

#%% COD PARA INCLUIR EL CORTE ANTERIOR O EL CÁLCULO DEL DÍA

# anx06_base['Capital'] = 0
# anx06_base['FECHA_DÍA'] = pd.Timestamp(fecha_corte_anx06)

# df = anx06_base.copy() #si deseamos incluir los datos del anexo06 (corte anterior)

###############################################################################
df_mergeado = df_mergeado.drop_duplicates(subset = 'Nro_Fincore', 
                                          keep   = 'first')

df  = df_mergeado.copy() #si deseamos incluir los datos de hoy

#%%

cnxn = pyodbc.connect('DRIVER=SQL Server;SERVER=SM-DATOS;UID=SA;PWD=123;')
cursor = cnxn.cursor()
# # Inserta el DataFrame en SQL Server
# # PARA QUE EL CÓDIGO FUNCIONE, debe existir la tabla, sino usar CREATE TABLE

for index, row in df.iterrows():
    cursor.execute(f"""
        INSERT INTO {tabla_actual} 
        ( [Nro_Fincore], 
          [Saldodecolocacionescreditosdirectos24],
          [MontodeDesembolso22],
          [FechadeDesembolso21], 
          [CapitalVigente26],
          [CapitalVencido29],
          [CapitalenCobranzaJudicial30],
          [CapitalRefinanciado28],
          [SaldosdeCreditosCastigados38],
          [CUOTA],
          [DiasdeMora33],
          [TipodeProducto43],
          [PRODUCTO TXT], 
          [PLANILLA_CONSOLIDADA], 
          [originador], 
          [administrador],
          [Capital],
          [FECHA_DÍA])
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    row['Nro_Fincore'],
    row['Saldodecolocacionescreditosdirectos24'],
    row['MontodeDesembolso22'],
    row['FechadeDesembolso21'],
    row['CapitalVigente26'],
    row['CapitalVencido29'],
    row['CapitalenCobranzaJudicial30'],
    row['CapitalRefinanciado28'],
    row['SaldosdeCreditosCastigados38'],
    row['CUOTA'],
    row['DiasdeMora33'],
    row['TipodeProducto43'],
    row['PRODUCTO TXT'],
    row['PLANILLA_CONSOLIDADA'],
    row['originador'],
    row['administrador'],
    row['Capital'],
    row['FECHA_DÍA']
    )

cnxn.commit()
cursor.close()

print('fecha cargada: ' + fecha_hoy)

#%% para unificar los nombres en el reporte de saldos diarios:
'''
update saldos_diarios..SALDOS_DIARIOS_2024_05
set administrador = 'MIGUEL TITO'
where administrador like '%MIGUEL%TITO%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set administrador = 'ALICIA OVIEDO'
where administrador like '%ALICIA OVIEDO%VELAS%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set administrador = 'ANDREA BILBAO'
where administrador like '%ANDREA BILBAO BRICEÑO%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set administrador = 'GIOVANNA HERRERA'
where administrador like '%GIOVANNA HERRERA MATH%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set administrador = 'MARGIORY ELIAS'
where administrador like '%MARGIORY ELIAS BENAVIDES%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set administrador = 'DAVID BORJA'
where administrador like '%DAVID BORJA%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set administrador = 'JULY OLGA'
where administrador like '%JULY GARCIA ALCANTARA%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set administrador = 'FIGARI VEGA'
where administrador like '%FIGARI VEGA AYQUIPA%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set administrador = 'KATHERIN RAMOS'
where administrador like '%KATHERIN RAMOS CCAMA%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set administrador = 'ROSA MALDONADO'
where administrador like '%ROSA MALDONADO FIGUREOA%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set administrador = 'ROXANA QUISPE'
where administrador like '%ROXANA QUISPE CHAVEZ%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set administrador = 'JOSE SANCHEZ'
where administrador like '%JOSE SANCHEZ F%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set originador = 'MIGUEL TITO'
where originador like '%MIGUEL%TITO%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set administrador = 'VICTOR VARGAS'
where administrador like '%VICTOR%VARGAS%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set originador = 'VICTOR VARGAS'
where originador like '%VICTOR%VARGAS%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set administrador = 'SUSAN ROJAS'
where administrador like '%SUSAN%ROJAS%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set administrador = 'GUSTAVO PALLETE'
where administrador like '%GUSTAVO%PALLETE%ALFERANO%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set originador = 'GUSTAVO PALLETE'
where originador like '%GUSTAVO%PALLETE%ALFERANO%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set administrador = 'AZUCENA OCHOA'
where administrador like '%AZUCENA OCHOA TERRY%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set originador = 'AZUCENA OCHOA'
where originador like '%AZUCENA OCHOA TERRY%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set originador = 'SUSAN ROJAS'
where originador like '%SUSAN%ROJAS%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set administrador = 'ELBER ALVARADO'
where administrador like '%ELBER%ALVARADO%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set originador = 'ELBER ALVARADO'
where originador like '%ELBER%ALVARADO%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set originador = 'DAVID BORJA'
where originador like '%DAVID%BORJA%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set originador = 'ALICIA OVIEDO'
where originador like '%ALICIA OVIEDO VELASQUEZ%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set originador = 'ANDREA BILBAO'
where originador like '%ANDREA BILBAO BRICEÑO%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set originador = 'EVELYN LOJA'
where originador like '%EVELYN LOJA PINEDO%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set originador = 'FIGARI VEGA'
where originador like '%FIGARI VEGA AYQUIPA%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set originador = 'GIOVANNA HERRERA'
where originador like '%GIOVANNA HERRERA MATHEWS%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set originador = 'GUSTAVO PALLETE'
where originador like '%GUSTAVO PALLETE ALFERANO%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set originador = 'JERSON ALVA'
where originador like '%JERSON ALVA FARFAN%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set originador = 'JIMN MENDOZA'
where originador like '%JIMN MENDOZA%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set originador = 'JONATHAN ESTRADA'
where originador like '%JONATHAN ESTRADA%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set originador = 'JOSE SANCHEZ'
where originador like '%JOSE SANCHEZ FLORES%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set originador = 'KATHERIN RAMOS'
where originador like '%KATHERIN RAMOS CCAMA%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set originador = 'LUIS BUSTAMANTE'
where originador like '%LUIS ALBERTO BUSTAMANTE GONZALES%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set originador = 'MARGIORY ELIAS'
where originador like '%MARGIORY ELIAS BENAVIDES%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set originador = 'MILTON JUAREZ'
where originador like '%MILTON MERLYN JUAREZ HORNA%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set originador = 'ROSA MALDONADO'
where originador like '%ROSA MALDONADO FIGUREOA%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set originador = 'ROXANA QUISPE'
where originador like '%ROXANA QUISPE CHAVEZ%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set originador = 'JULY OLGA'
where originador like '%JULY GARCIA ALCANTARA%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set originador = 'JULY OLGA'
where originador like '%JULY GARCIA%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set originador = 'PROSEVA CAÑETE'
where originador like '%CAÑETE%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set originador = 'MARIBEL PUCHO'
where originador like '%MARIBEL PUCHO%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set administrador = 'MARIBEL PUCHO'
where administrador like '%MARIBEL PUCHO%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set originador = 'JHONY SALDAÑA'
where originador like '%JONY SALDAÑA%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set administrador = 'JHONY SALDAÑA'
where administrador like '%JONY SALDAÑA%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set originador = 'MARIA CRISTINA MARTINEZ'
where originador like '%MARIA CRISTINA MARTINEZ%'

update saldos_diarios..SALDOS_DIARIOS_2024_05
set administrador = 'MARIA CRISTINA MARTINEZ'
where administrador like '%MARIA CRISTINA MARTINEZ%'
'''    
    
