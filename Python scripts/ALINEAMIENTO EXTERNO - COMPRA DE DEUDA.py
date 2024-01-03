# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 14:04:26 2023

@author: Joseph Montoya
"""

#EXTRACCIÓN DE DATOS PEDIDOS PARA EL ALINEAMIENTO EXTERNO

#%%
import pandas as pd
import pyodbc
import os
import warnings
warnings.filterwarnings('ignore')

#%%
# COLUMNA_ALINEAMIENTO = 'ALINEAMIENTO EXTERNO SBS RCC NOVIEMBRE 2023' # Columna 32 en el excel (no incluye NO REGULADAS)

CORTE_SQL = '20231130'

os.chdir('C:\\Users\\sanmiguel38\\Desktop\\ALINEAMIENTO EXTERNO\\2023 nov')

NOMBRE_AL_EXTERNO = 'exceldoc_AlinCartera_2171967_42734875_21202410273_1.csv'

#%%

conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')

query = f'''
SELECT
	FechaCorte1,
	C.Nro_Fincore, 
	ApellidosyNombresRazonSocial2,NumerodeDocumento10,
	MontodeDesembolso22,
	FechadeDesembolso21,
	Saldodecolocacionescreditosdirectos24,
	Saldodecolocacionescreditosdirectos24 - IngresosDiferidos42 AS 'CARTERA NETA',
	CapitalVencido29,
	CapitalenCobranzaJudicial30,
	SaldosdeCreditosCastigados38,
	ClasificaciondelDeudorconAlineamiento15,
	TipodeCredito19, 
	DiasdeMora33, 
	SaldosdeGarantiasPreferidas34, SaldodeGarantiasAutoliquidables35,
	ProvisionesConstituidas37,
	ProvisionesRequeridas36,
CASE 
	WHEN B.FDN_DRIVE IS NULL THEN c.originador ELSE B.FDN_DRIVE END AS 'originador',
	
	
	administrador,
	LTRIM(RTRIM(P.NUEVA_PLANILLA_creada)) AS 'Planilla',
	TipodeProducto43,
	CASE
		WHEN TipodeProducto43 IN (34,35,36,37,38,39) THEN 'DXP'
		WHEN TipodeProducto43 IN (30,31,32,33) THEN 'LD'
		WHEN TipodeProducto43 IN (15,16,17,18,19) THEN 'PEQUEÑA EMPRESA'
		WHEN TipodeProducto43 IN (20,21,22,23,24,25,29) THEN 'MICRO EMPRESA'
		WHEN TipodeProducto43 IN (95,96,97,98,99) THEN 'MEDIANA EMPRESA'
		WHEN TipodeProducto43 IN (41,45) THEN 'HIPOTECARIA'
		END AS 'PRODUCTO TXT'
FROM
	anexos_riesgos3.dbo.anx06 as C

LEFT JOIN 
    Anexos_Riesgos..planilla2 P 
    ON (LTRIM(RTRIM(C.NUEVA_PLANILLA)) =  LTRIM(RTRIM(P.NUEVA_PLANILLA)))

LEFT JOIN anexos_riesgos2..ORIGINADOR_ENERO_2023 AS B ON (C.Nro_Fincore = B.NRO_FINCORE)

WHERE	
    FechaCorte1 = '{CORTE_SQL}'
'''

base = pd.read_sql_query(query, 
                         conn,
                         dtype = {'NumerodeDocumento10'  : str,
                                  'TipodeCredito19'      : str}
                         )

del conn

base['NumerodeDocumento10'] = base['NumerodeDocumento10'].str.strip()
#%%

al_externo = pd.read_csv(NOMBRE_AL_EXTERNO,
                           dtype = {'NUMERO DE DOCUMENTO' : str},
                           skiprows = 1
                           )

#%% SI LA ESTRUCTURA SE MANTIENE este debería ser una columna tipo 'ALINEAMIENTO EXTERNO SBS RCC NOVIEMBRE 2023'
COLUMNA_ALINEAMIENTO = al_externo.columns[31]
print(COLUMNA_ALINEAMIENTO)
print('''el nombre de la columna debe ser algo como 'ALINEAMIENTO EXTERNO SBS RCC NOVIEMBRE 2023' ''')

#%%
x = al_externo.columns

a_e_filtrado = al_externo[['TIPO DE DOCUMENTO',
                           'NUMERO DE DOCUMENTO',
                           #'APELLIDO PATERNO',
                           #'APELLIDO MATERNO',
                           #'NOMBRE',
                           'NIVEL DE RIESGO',
                           'NUMERO DE ENTIDADES SBS REPORTADAS',
                           'DEUDA TOTAL EN NO REGULADAS',
                           'DEUDA TOTAL EN SBS',
                           COLUMNA_ALINEAMIENTO]]

a_e_filtrado['DOC ORIGINAL'] = a_e_filtrado['NUMERO DE DOCUMENTO']

#%% ARREGLAMOS LOS NROS DE DOCUMENTO DE LOS SOCIOS
a_e_filtrado['NUMERO DE DOCUMENTO'] = a_e_filtrado['NUMERO DE DOCUMENTO'].str.lstrip('0') #ELIMINACIÓN DE CEROS A LA IZQUIERDA

def enteros(a_e_filtrado):
    return int(a_e_filtrado['NUMERO DE DOCUMENTO'])
a_e_filtrado['NUMERO DE DOCUMENTO'] = a_e_filtrado.apply(enteros, axis=1)

a_e_filtrado['NUMERO DE DOCUMENTO'] = a_e_filtrado['NUMERO DE DOCUMENTO'].astype(str)

def correccion_documento(a_e_filtrado):
    if a_e_filtrado['TIPO DE DOCUMENTO'] == 'CARNET DE EXTRANJERIA':
        return a_e_filtrado['NUMERO DE DOCUMENTO'].zfill(9)
    
    elif a_e_filtrado['TIPO DE DOCUMENTO'] == 'DNI':
        return a_e_filtrado['NUMERO DE DOCUMENTO'].zfill(8)
    
    elif a_e_filtrado['TIPO DE DOCUMENTO'] == 'RUC':
        return a_e_filtrado['NUMERO DE DOCUMENTO'].zfill(11)
    else:
        return 'investigar caso'

a_e_filtrado['NUMERO DOC CORREGIDO'] = a_e_filtrado.apply(correccion_documento, axis=1)

print('NÚMERO DE FILAS QUE SE HAN CORREGIDO MAL:')
print(a_e_filtrado[a_e_filtrado['NUMERO DOC CORREGIDO'] == 'investigar caso'].shape[0])
print(a_e_filtrado[a_e_filtrado['NUMERO DOC CORREGIDO'] == '000000000'].shape[0])
print(a_e_filtrado[a_e_filtrado['NUMERO DOC CORREGIDO'] == '00000000'].shape[0])
print(a_e_filtrado[a_e_filtrado['NUMERO DOC CORREGIDO'] == '00000000000'].shape[0])

#%% ALINEAMIENTO EXTERNO EN NUMÉRICO:
def alineamiento_numerico(a_e_filtrado):
    if a_e_filtrado[COLUMNA_ALINEAMIENTO] == 'NORMAL':
        return 0
    elif a_e_filtrado[COLUMNA_ALINEAMIENTO] == 'CPP':
        return 1
    elif a_e_filtrado[COLUMNA_ALINEAMIENTO] == 'DEFICIENTE':
        return 2
    elif a_e_filtrado[COLUMNA_ALINEAMIENTO] == 'DUDOSO':
        return 3
    elif a_e_filtrado[COLUMNA_ALINEAMIENTO] == 'PERDIDA':
        return 4
    else:
        return 'investigar caso'

a_e_filtrado['ALINEAMIENTO EXTERNO'] = a_e_filtrado.apply(alineamiento_numerico, axis=1)
   
print('NÚMERO DE FILAS QUE NO HACEN MATCH:')
print(a_e_filtrado[a_e_filtrado['ALINEAMIENTO EXTERNO'] == 'investigar caso'].shape[0])
    
#%% MERGE
UNION = base.merge(a_e_filtrado, 
                   left_on  = ['NumerodeDocumento10'],
                   right_on = ['NUMERO DOC CORREGIDO'],
                   how      = 'left')

print(UNION[pd.isna(UNION['NUMERO DOC CORREGIDO'])]['ApellidosyNombresRazonSocial2'])
print('sale null en aquellos registros que Experian no procesa')

#%% Correción de nulos(se reemplaza por el alineamiento interno)

mask = pd.isna(UNION['ALINEAMIENTO EXTERNO'])

UNION.loc[mask, 'ALINEAMIENTO EXTERNO'] = UNION.loc[mask, 'ClasificaciondelDeudorconAlineamiento15']

print(UNION[pd.isna(UNION['ALINEAMIENTO EXTERNO'])]['ApellidosyNombresRazonSocial2'])
print(UNION[pd.isna(UNION['ALINEAMIENTO EXTERNO'])]['ApellidosyNombresRazonSocial2'].shape[0])
print('si sale más de cero, hay que investigar')
print('sale null en aquellos registros que Experian no procesa')

#%% máximo alineamiento:
    
def max_clasificacion(UNION):
    if UNION['ALINEAMIENTO EXTERNO'] > UNION['ClasificaciondelDeudorconAlineamiento15']:
        return UNION['ALINEAMIENTO EXTERNO']
    else:
        return UNION['ClasificaciondelDeudorconAlineamiento15']

UNION['MAX CALIFICACION'] = UNION.apply(max_clasificacion, axis=1)

#%% CÁLCULO DE PROVISIONES REQUERIDAS:
def prov_alineadas_externamente(UNION):
    if UNION['MAX CALIFICACION'] == 0:
        if UNION['TipodeCredito19'] in ['12','11','10', '09','08', 12,11,10,9,8]:                                                   
            return 0.01
        elif UNION['TipodeCredito19'] in ['13', '07', '06', 13,7,6]:
            return 0.007
    elif UNION['SaldodeGarantiasAutoliquidables35'] > 0:
        if UNION['MAX CALIFICACION'] in [1,2,3,4]:
            return 0.01
    elif UNION['SaldosdeGarantiasPreferidas34'] > 0:
        if UNION['MAX CALIFICACION'] == 1:
            return 0.025
        if UNION['MAX CALIFICACION'] == 2:
            return 0.125
        if UNION['MAX CALIFICACION'] == 3:
            return 0.30
        if UNION['MAX CALIFICACION'] == 4:
            return 0.60
    elif (UNION['SaldosdeGarantiasPreferidas34'] == 0) and \
        (UNION['SaldodeGarantiasAutoliquidables35'] == 0):
        if UNION['MAX CALIFICACION'] == 1:
            return 0.05
        if UNION['MAX CALIFICACION'] == 2:
            return 0.25
        if UNION['MAX CALIFICACION'] == 3:
            return 0.6
        if UNION['MAX CALIFICACION'] == 4:
            return 1.00
    else:
        return ''

UNION['TASA PROV. CON AL. EXTERNO'] = UNION.apply(prov_alineadas_externamente, axis=1)

print(UNION[UNION['TASA PROV. CON AL. EXTERNO'] == ''].shape[0])

UNION['Provisiones Requeridas A.EXTERNO'] = UNION['CARTERA NETA'] * \
                                            UNION['TASA PROV. CON AL. EXTERNO']
                                            
UNION['Provisiones Requeridas A.EXTERNO'] = UNION['Provisiones Requeridas A.EXTERNO'].round(2)

print('Provisiones constituidas:')
print(UNION['ProvisionesConstituidas37'].sum())
print('')

print('Provisiones requeridas:')
print(UNION['ProvisionesRequeridas36'].sum())
print('')

print('Provisiones requeridas con al. externo:')
print(UNION['Provisiones Requeridas A.EXTERNO'].sum())

#%% COLUMNAS PARA EL SQL

para_sql = UNION[['Nro_Fincore',
                  'NumerodeDocumento10',
                  'NUMERO DE ENTIDADES SBS REPORTADAS',
                  'DEUDA TOTAL EN NO REGULADAS',
                  'ALINEAMIENTO EXTERNO',
                  'MAX CALIFICACION',
                  'TASA PROV. CON AL. EXTERNO',
                  'Provisiones Requeridas A.EXTERNO',
                  #'ENTIDAD FINANCIERA CON PEOR CALIFICACIÓN',
                  #'DEUDA TOTAL EN LA ENTIDAD',
                  #'CATEGORÍA DE RIESGO EN LA ENTIDAD FINANCIERA',
                  #'PROV. REQUERIDAS AL. EXTERNO AGRUPADO',
                  'FechaCorte1']]

nombre = f'AL. EXTERNO {CORTE_SQL} SQL.xlsx'

para_sql.to_excel(nombre,
                  index = False,
                  sheet_name = 'AL. EXTERNO SQL')
del nombre

#LO SUBES A SQL Y USAS EL SIGUIENTE CÓDIGO:
'''
    INSERT INTO anexos_riesgos3.[ALINEAMIENTO EXTERNO].[AL_EXTERNO] 
--(columna1, columna2, columna3, ...)
SELECT 
	NRO_fincore, 
	NumerodeDocumento10,
	[NUMERO DE ENTIDADES SBS REPORTADAS],
	[ALINEAMIENTO EXTERNO],
	[MAX CALIFICACION],
	[TASA PROV# CON AL# EXTERNO],
	[Provisiones Requeridas A#EXTERNO],
	NULL AS 'ENTID FINANC CON PEOR CALIF',
	NULL AS 'DEUDA TOTAL EN LA ENTIDAD',
	NULL AS 'CATEGORIA DE RIESGO EN LA ENTIDAD',
	NULL AS 'PROV REQUERID EXTERNO AGRUPADO',
	[FechaCorte1]
FROM 
	anexos_riesgos3.[ALINEAMIENTO EXTERNO].[OCT_2023]
'''
#%% FILTRADOS DXP PARA COMPRA DE DEUDA

#filtrados_dxp = UNION[UNION['PRODUCTO TXT'] == 'DXP']
UNION['ClasificaciondelDeudorconAlineamiento15'] = UNION['ClasificaciondelDeudorconAlineamiento15'].astype(int)
UNION['ALINEAMIENTO EXTERNO'] = UNION['ALINEAMIENTO EXTERNO'].astype(int)


# filtrados_COMPRA_DEUDA = UNION[(UNION['ClasificaciondelDeudorconAlineamiento15'] == 0) & \
#                                (UNION['ALINEAMIENTO EXTERNO'] == 3)]

# este código de aquí abajo lo podemos comentar si queremos aplicar el filtro
# y des-comentamos el filtrado anterior si es que necesitamos filtrar
filtrados_COMPRA_DEUDA = UNION.copy()

#%% columnas necesarias:

filtrados_COMPRA_DEUDA = filtrados_COMPRA_DEUDA[['FechaCorte1',
                                                 'Nro_Fincore',
                                                 'ApellidosyNombresRazonSocial2',
                                                 'NumerodeDocumento10',
                                                 'MontodeDesembolso22',
                                                 'FechadeDesembolso21',
                                                 'Saldodecolocacionescreditosdirectos24',
                                                 'CARTERA NETA',
                                                 'CapitalVencido29',
                                                 'CapitalenCobranzaJudicial30',
                                                 'SaldosdeCreditosCastigados38',
                                                 'ClasificaciondelDeudorconAlineamiento15',
                                                 'TipodeCredito19',
                                                 'DiasdeMora33',
                                                 'SaldosdeGarantiasPreferidas34',
                                                 'SaldodeGarantiasAutoliquidables35',
                                                 'ProvisionesConstituidas37',
                                                 'ProvisionesRequeridas36',
                                                 'originador',
                                                 'administrador',
                                                 'Planilla',
                                                 'TipodeProducto43',
                                                 'PRODUCTO TXT',
                                                 'TIPO DE DOCUMENTO',
                                                 #'NUMERO DE DOCUMENTO',
                                                 'NIVEL DE RIESGO',
                                                 'NUMERO DE ENTIDADES SBS REPORTADAS',
                                                 'DEUDA TOTAL EN NO REGULADAS',
                                                 'DEUDA TOTAL EN SBS',
                                                 COLUMNA_ALINEAMIENTO,
                                                 #'DOC ORIGINAL',
                                                 #'NUMERO DOC CORREGIDO',
                                                 'ALINEAMIENTO EXTERNO',
                                                 'MAX CALIFICACION',
                                                 'TASA PROV. CON AL. EXTERNO',
                                                 'Provisiones Requeridas A.EXTERNO'
                                                 ]]
#%% EXPORTACIÓN A EXCEL
print('guardando excel')
filtrados_COMPRA_DEUDA.to_excel(f'COMPRA DE DEUDA cartera total - {CORTE_SQL}.xlsx',
                                index = False,
                                sheet_name = 'COMPRA DE DEUDA')
print('guardado concluido')

#UNION.shape[0]

#%% UBICACIÓN DE LOS ARCHIVOS
# POR SI NO SABEMOS DÓNDE ESTÁN LOS ARCHIVOS
# Obtener la ubicación actual
ubicacion_actual = os.getcwd()

# Imprimir la ubicación actual
print("La ubicación actual es: " + ubicacion_actual)

#%%%

#EL QUE SE SUBE A SQL SE INSERTA CON EL SIGUIENTE CÓDIGO:
'''
    INSERT INTO anexos_riesgos3.[ALINEAMIENTO EXTERNO].[AL_EXTERNO] 
--(columna1, columna2, columna3, ...)
SELECT 
	NRO_fincore, 
	NumerodeDocumento10,
	[NUMERO DE ENTIDADES SBS REPORTADAS],
	[ALINEAMIENTO EXTERNO],
	[MAX CALIFICACION],
	[TASA PROV# CON AL# EXTERNO],
	[Provisiones Requeridas A#EXTERNO],
	NULL AS 'ENTID FINANC CON PEOR CALIF',
	NULL AS 'DEUDA TOTAL EN LA ENTIDAD',
	NULL AS 'CATEGORIA DE RIESGO EN LA ENTIDAD',
	NULL AS 'PROV REQUERID EXTERNO AGRUPADO',
	[FechaCorte1]
FROM 
	anexos_riesgos3.[ALINEAMIENTO EXTERNO].[2023_11]
'''
