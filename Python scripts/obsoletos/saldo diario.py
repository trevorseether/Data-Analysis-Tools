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
fecha_corte_anx06 = '20231231'                     #
####################################################

'Fechas para la cobranza y nuevos desembolsos'######
fecha_inicio = '20240101'                          #
fecha_hoy    = '20240129'                          ## se pone la fecha de hoy ##
####################################################

'Directorio de trabajo'#############################
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\saldos diarios')
####################################################

'Incremento de días mora'###########################
incremento = int(fecha_hoy[-2:])
####################################################

# appendeado = pd.DataFrame()
# appendeado = pd.concat([appendeado, df_mergeado], ignore_index=True)
# appendeado.to_excel('append.xlsx', index = False)

#%%
conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')

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
            isnull(ROUND((MontodeDesembolso22 / NumerodeCuotasProgramadas44),2),0) AS 'CUOTA',
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
        WHERE FechaCorte1 = '{fecha_corte_anx06}'
    ''', conn)

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
    p.NroPlazos,
    isnull(ROUND((p.montosolicitado / p.NroPlazos),2),0) as 'CUOTA',
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
df_desembolsados = pd.read_sql_query(query, conn,
                                     dtype = {'COD_FINALIDAD' : str})

# df_desembolsados['TipoCredito'] = df_desembolsados['TipoCredito'].astype(str)

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
                            left join CobranzaDocumento cdoc ON ccab.CodCobranzaDocumento = cdoc.CodCobranzaDocumento
                            left join Cuenta  CU ON CU.CodCuenta  = cdoc.CodCuentaDestino
                            left join NotaCredito  NC ON ccab.CodNotaCredito = NC.CodNotaCredito
                            left join CobranzaDocumento CDDNC ON NC.CodCobranzaDocumento = CDDNC.CodCobranzaDocumento
                            left join Cuenta  CUNC ON CDDNC.CodCuentaDestino = CUNC.CodCuenta
                            --------

WHERE CONVERT(VARCHAR(10),ccab.fecha,112) BETWEEN '{fecha_inicio}' AND '{fecha_corte_cobranza}' and cdet.CodEstado <> 376   
ORDER BY ccab.fecha

'''
df_cobranza = pd.read_sql_query(query, conn)

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
desem_format['CUOTA']                        = df_desembolsados['CUOTA']
desem_format['DiasdeMora33']                 = 0
desem_format['TipodeProducto43']     = df_desembolsados['COD_FINALIDAD'].copy()
desem_format['PRODUCTO TXT']         = ''
desem_format['PLANILLA_CONSOLIDADA'] = df_desembolsados['Planilla'].copy()
desem_format['originador']           = df_desembolsados['ORIGINADOR'].copy()
desem_format['administrador']        = df_desembolsados['ADMINISTRADOR'].copy()

#%%
desem_format.loc[desem_format['TipodeProducto43'] == '27', 'TipodeProducto43'] = '32'

prod_dxp  = ['34', '35', '36', '37', '38', '39']
prod_ld   = ['30', '31', '32', '33']
prod_mic  = ['20', '21', '22', '23', '24', '25', '26', '29']
prod_peq  = ['15', '16', '17', '18', '19']
prod_med  = ['95', '96', '97', '98', '99']
prod_hip  = ['41', '45']

def producto_txt(df):
    tipo_producto = df['TipodeProducto43']
    
    if tipo_producto in prod_dxp:
        return 'DXP'
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

print(desem_format[pd.isna(desem_format['PRODUCTO TXT'])].shape[0])
print('debe salir cero')

#%%
columnas = desem_format.columns

anx06_base = df_anx06[columnas]

df_concatenado = pd.concat([anx06_base, desem_format], ignore_index = True)

# quitamos créditos cancelados
df_concatenado = df_concatenado[~df_concatenado['Nro_Fincore'].isin(list(df_cancelados['pagare_fincore']))]

#%% calculamos la recaudación de los saldos de cartera
recau = df_cobranza.pivot_table(index  = 'PagareFincore',
                                values = 'Capital')
recau = recau.reset_index()

#%% merge con la recaudación
df_mergeado = df_concatenado.merge(recau,
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
print(cosas_que_no_cuadran.shape[0])
print('debe salir un número bajo (<20)')
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
df_mergeado['CapitalVigente26'] = df_mergeado.apply(cob2_judicial, axis=1)

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
# faltan otras cosas
'''
prom_ld = 1.2
def vencid_consumo_ld(df):
    if df['PRODUCTO TXT'] in ['LD']: # no cambiaremos DXP, mejor esperaremos al anexo 06 
        if (df['DiasdeMora33'] > 30) and \
           (df['DiasdeMora33'] <= 60) and \
           (df['CapitalVencido29'] == 0) and \
           (df['Saldodecolocacionescreditosdirectos24'] > df['CUOTA']):
            return df['CUOTA'] * prom_ld #este 1.2 y 2.4 son aproximaciones del promedio respecto a la cuota vencida aplicada con la división entre el monto desembolsado y el número de cuotas
        elif (df['DiasdeMora33'] > 30) and \
             (df['DiasdeMora33'] <= 60) and \
             (df['CapitalVencido29'] > 0):
            return df['CapitalVencido29']

        elif (df['DiasdeMora33'] > 60) and \
             (df['DiasdeMora33'] <= 90):
            return df['CUOTA'] * prom_ld * 2

        elif (df['DiasdeMora33'] > 90):
            return df['Saldodecolocacionescreditosdirectos24']
        else:
            return df['CapitalVencido29']
    else:
        return df['CapitalVencido29']
df_mergeado['CapitalVencido29'] = df_mergeado.apply(vencid_consumo_ld, axis = 1)
'''

df_mergeado['CapitalVencido29'] = df_mergeado['CapitalVencido29'].round(2)
df_mergeado['CapitalVigente26'] = df_mergeado['CapitalVigente26'].round(2)

#%% INCREMENTO DEL CAPITAL VENCIDO PARA CONSUMO NO REVOLVENTE E HIPOTECARIO
# faltan otras cosas
prom_ld = 1.2
def vencid_consumo_ld(row):
    if row['CapitalRefinanciado28'] == 0:
        if row['PRODUCTO TXT'] in ['LD']: 
            if (row['DiasdeMora33'] > 30) and \
               (row['DiasdeMora33'] <= 60) and \
               (row['CapitalVencido29'] == 0) and \
               (row['CapitalRefinanciado28'] == 0) and \
               (row['Saldodecolocacionescreditosdirectos24'] > row['CUOTA']):
                   
                row['CapitalVencido29'] = row['CUOTA'] * prom_ld
                row['CapitalVigente26'] = row['CapitalVigente26'] - (row['CUOTA'] * prom_ld)
                
            if (row['DiasdeMora33'] > 30) and \
               (row['DiasdeMora33'] <= 60) and \
               (row['CapitalVencido29'] > 0):
                 
                row['CapitalVencido29'] = row['CapitalVencido29']
                
            if (row['DiasdeMora33'] > 60) and \
               (row['DiasdeMora33'] <= 90):
                   
                row['CapitalVencido29'] = row['CUOTA'] * prom_ld * 2
                row['CapitalVigente26'] = row['CapitalVigente26'] - (row['CUOTA'] * prom_ld * 2)
                
            if (row['DiasdeMora33'] > 90):
                
                row['CapitalVencido29'] = row['Saldodecolocacionescreditosdirectos24']
                row['CapitalVigente26'] = 0
            
    return row
df_mergeado = df_mergeado.apply(vencid_consumo_ld, axis = 1)

df_mergeado['CapitalVencido29'] = df_mergeado['CapitalVencido29'].round(2)
df_mergeado['CapitalVigente26'] = df_mergeado['CapitalVigente26'].round(2)

#%%
'''
prom_hipo = 1.118
def vencid_consumo_hipo(df):
    if df['PRODUCTO TXT'] in ['HIPOTECARIO']: # no cambiaremos DXP, mejor esperaremos al anexo 06 
        if (df['DiasdeMora33'] > 30) and \
           (df['DiasdeMora33'] <= 60) and \
           (df['CapitalVencido29'] == 0) and \
           (df['Saldodecolocacionescreditosdirectos24'] > df['CUOTA']):
            return df['CUOTA'] * prom_hipo
        elif (df['DiasdeMora33'] > 30) and \
             (df['DiasdeMora33'] <= 60) and \
             (df['CapitalVencido29'] > 0):
            return df['CapitalVencido29']

        elif (df['DiasdeMora33'] > 60) and \
             (df['DiasdeMora33'] <= 90):
            return df['CUOTA'] * prom_hipo * 2

        elif (df['DiasdeMora33'] > 90):
            return df['Saldodecolocacionescreditosdirectos24']
        else:
            return df['CapitalVencido29']
    else:
        return df['CapitalVencido29']
df_mergeado['CapitalVencido29'] = df_mergeado.apply(vencid_consumo_hipo, axis = 1)
'''
#%% INCREMENTO DEL CAPITAL VENCIDO PARA HIPOTECARIO
prom_hipo = 1.118
def vencid_consumo_hipo(row):
    if row['CapitalRefinanciado28'] == 0:
        if row['PRODUCTO TXT'] in ['HIPOTECARIO']: 
            if (row['DiasdeMora33'] > 30) and \
               (row['DiasdeMora33'] <= 60) and \
               (row['CapitalVencido29'] == 0) and \
               (row['Saldodecolocacionescreditosdirectos24'] > row['CUOTA']):
                   
                row['CapitalVencido29'] = row['CUOTA'] * prom_hipo
                row['CapitalVigente26'] = row['CapitalVigente26'] - (row['CUOTA'] * prom_hipo)
                
            if (row['DiasdeMora33'] > 30) and \
               (row['DiasdeMora33'] <= 60) and \
               (row['CapitalVencido29'] > 0):
                 
                row['CapitalVencido29'] = row['CapitalVencido29']
                
            if (row['DiasdeMora33'] > 60) and \
               (row['DiasdeMora33'] <= 90):
                   
                row['CapitalVencido29'] = row['CUOTA'] * prom_hipo * 2
                row['CapitalVigente26'] = row['CapitalVigente26'] - (row['CUOTA'] * prom_hipo * 2)
                
            if (row['DiasdeMora33'] > 90):
                row['CapitalVencido29'] = row['Saldodecolocacionescreditosdirectos24']
                row['CapitalVigente26'] = 0
    return row

df_mergeado = df_mergeado.apply(vencid_consumo_hipo, axis = 1)

df_mergeado['CapitalVencido29'] = df_mergeado['CapitalVencido29'].round(2)
df_mergeado['CapitalVigente26'] = df_mergeado['CapitalVigente26'].round(2)

#%% ahora para refinanciados LD
prom_ld = 1.2
def vencid_consumo_ld_ref(row):
    if row['CapitalRefinanciado28'] > 0:
        if row['PRODUCTO TXT'] in ['LD']: 
            if (row['DiasdeMora33'] > 30) and \
               (row['DiasdeMora33'] <= 60) and \
               (row['CapitalVencido29'] == 0) and \
               (row['CapitalRefinanciado28'] == 0) and \
               (row['Saldodecolocacionescreditosdirectos24'] > row['CUOTA']):
                   
                row['CapitalVencido29'] = row['CUOTA'] * prom_ld
                row['CapitalRefinanciado28'] = row['CapitalRefinanciado28'] - (row['CUOTA'] * prom_ld)
                
            if (row['DiasdeMora33'] > 30) and \
               (row['DiasdeMora33'] <= 60) and \
               (row['CapitalVencido29'] > 0):
                 
                row['CapitalVencido29'] = row['CapitalVencido29']
                
            if (row['DiasdeMora33'] > 60) and \
               (row['DiasdeMora33'] <= 90):
                   
                row['CapitalVencido29'] = row['CUOTA'] * prom_ld * 2
                row['CapitalRefinanciado28'] = row['CapitalRefinanciado28'] - (row['CUOTA'] * prom_ld * 2)
                
            if (row['DiasdeMora33'] > 90):
                
                row['CapitalVencido29'] = row['Saldodecolocacionescreditosdirectos24']
                row['CapitalRefinanciado28'] = 0
            
    return row
df_mergeado = df_mergeado.apply(vencid_consumo_ld_ref, axis = 1)

df_mergeado['CapitalVencido29'] = df_mergeado['CapitalVencido29'].round(2)
df_mergeado['CapitalRefinanciado28'] = df_mergeado['CapitalRefinanciado28'].round(2)

#%%
prom_hipo = 1.118
def vencid_consumo_hipo_ref(row):
    if row['CapitalRefinanciado28'] > 0:
        if row['PRODUCTO TXT'] in ['HIPOTECARIO']: 
            if (row['DiasdeMora33'] > 30) and \
               (row['DiasdeMora33'] <= 60) and \
               (row['CapitalVencido29'] == 0) and \
               (row['Saldodecolocacionescreditosdirectos24'] > row['CUOTA']):
                   
                row['CapitalVencido29'] = row['CUOTA'] * prom_hipo
                row['CapitalRefinanciado28'] = row['CapitalRefinanciado28'] - (row['CUOTA'] * prom_hipo)
                
            if (row['DiasdeMora33'] > 30) and \
               (row['DiasdeMora33'] <= 60) and \
               (row['CapitalVencido29'] > 0):
                 
                row['CapitalVencido29'] = row['CapitalVencido29']
                
            if (row['DiasdeMora33'] > 60) and \
               (row['DiasdeMora33'] <= 90):
                   
                row['CapitalVencido29'] = row['CUOTA'] * prom_hipo * 2
                row['CapitalRefinanciado28'] = row['CapitalRefinanciado28'] - (row['CUOTA'] * prom_hipo * 2)
                
            if (row['DiasdeMora33'] > 90):
                row['CapitalVencido29'] = row['Saldodecolocacionescreditosdirectos24']
                row['CapitalRefinanciado28'] = 0
    return row

df_mergeado = df_mergeado.apply(vencid_consumo_hipo_ref, axis = 1)

df_mergeado['CapitalVencido29'] = df_mergeado['CapitalVencido29'].round(2)
df_mergeado['CapitalRefinanciado28'] = df_mergeado['CapitalRefinanciado28'].round(2)

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

#%% SI QUEREMOS CONVERTI EL DATAFRAME A EXCEL

# df_mergeado.to_excel(fecha_hoy + '.xlsx',
#                       index = False)

#%%
# import pyodbc
# import pandas as pd

# df  = df_mergeado.copy()

# cnxn = pyodbc.connect('DRIVER=SQL Server;SERVER=SM-DATOS;UID=SA;PWD=123;')
# cursor = cnxn.cursor()
# # # Inserta el DataFrame en SQL Server
# # # PARA QUE EL CÓDIGO FUNCIONE, debe existir la tabla, sino usar CREATE TABLE

# for index, row in df.iterrows():
#     cursor.execute("""
#         INSERT INTO saldos_diarios.dbo.[SALDOS_DIARIOS] 
#         ( [Nro_Fincore], 
#           [Saldodecolocacionescreditosdirectos24],
#           [MontodeDesembolso22],
#           [FechadeDesembolso21], 
#           [CapitalVigente26],
#           [CapitalVencido29],
#           [CapitalenCobranzaJudicial30],
#           [CapitalRefinanciado28],
#           [SaldosdeCreditosCastigados38],
#           [CUOTA],
#           [DiasdeMora33],
#           [TipodeProducto43],
#           [PRODUCTO TXT], 
#           [PLANILLA_CONSOLIDADA], 
#           [originador], 
#           [administrador],
#           [Capital],
#           [FECHA_DÍA])
#         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#     """,
#     row['Nro_Fincore'],
#     row['Saldodecolocacionescreditosdirectos24'],
#     row['MontodeDesembolso22'],
#     row['FechadeDesembolso21'],
#     row['CapitalVigente26'],
#     row['CapitalVencido29'],
#     row['CapitalenCobranzaJudicial30'],
#     row['CapitalRefinanciado28'],
#     row['SaldosdeCreditosCastigados38'],
#     row['CUOTA'],
#     row['DiasdeMora33'],
#     row['TipodeProducto43'],
#     row['PRODUCTO TXT'],
#     row['PLANILLA_CONSOLIDADA'],
#     row['originador'],
#     row['administrador'],
#     row['Capital'],
#     row['FECHA_DÍA']
#     )

# cnxn.commit()
# cursor.close()

# print('fecha cargada: ' + fecha_hoy)
