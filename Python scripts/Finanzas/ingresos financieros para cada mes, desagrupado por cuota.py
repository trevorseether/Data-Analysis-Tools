# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 09:31:13 2023

@author: Joseph Montoya
"""

# =============================================================================
# CÁLCULO DE INGRESOS FINANCIEROS (INT_CUOTA)
# =============================================================================

import pandas as pd
import os
import pyodbc
import warnings
warnings.filterwarnings('ignore')

#%% 
# FECHAS PARA LA RECAUDACIÓN:
fecha_corte = '20241231'   # FECHA CORTE DEL MES

#columnas nuevas solicitadas

# DIRECTORIO DE TRABAJO:
directorio = 'C:\\Users\\sanmiguel38\\Desktop\\ingresos financierso\\NUEVAS COLUMNAS'
os.chdir(directorio)

#%% QUERY
datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')

server    =  datos['DATOS'][0]
username  =  datos['DATOS'][2]
password  =  datos['DATOS'][3]

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'

conn = pyodbc.connect(conn_str)

query = f'''

SELECT 
	soc.codsocio, 
	soc.codigosocio, 
    
	iif(soc.CodTipoPersona =1,concat(soc.apellidopaterno,' ',soc.apellidomaterno,' ',soc.nombres),soc.razonsocial) as Socio, 
	
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

    EOMONTH(ccab.fecha) AS 'EOM_FVEN',
    EOMONTH(pre.fechaCancelacion)    AS 'EOM_FCAN',

	iif(cdet.CodMoneda='95','DÓLAR','SOLES') AS moneda, 
	ccab.fecha as fecha_cob, 
	cdet.Capital, 
	cdet.aporte as Aporte,
	cdet.interes AS INT_CUOTA, 
	cdet.InteresCompensatorio as IntCompVencido, 
	cdet.Mora AS INTCOMP_MORA, 
	cdet.GastoCobranza, 
	cdet.FondoContigencia+cdet.MoraAnterior+cdet.GastoTeleOperador+cdet.GastoJudicial+cdet.GastoLegal+cdet.GastoOtros AS GTO_OTROS,
	cdoc.numeroOperacion,
	cdoc.numeroOperacionDestino, --tmdet.descripcion as TipoDocmto, 
	gr.descripcion as Funcionario, 
	pla.descripcion as planilla, 
	tc.Descripcion as TipoCredito, 
	fin.codigo, 
	fin.Descripcion as 'FINALIDAD',  
	pre.FechaVentaCartera, 
	pre.FechaCastigo, 
	cdoc.codestado, 
	cDOC.NumeroOperacionDestino, 
	CCAB.CODMEDIOPAGO, 
	tmdet.descripcion as tipoPago, -- CDOC.CODCOBRANZADOCUMENTO,
	tmdet5.Descripcion as SituacCred, 
	pre.FechaAsignacionAbogado, 
	empl.NombreCompleto as Abogado, 

--IIF(CDDNC.NumeroOperacionDestino IS NULL,cdoc.NumeroOperacionDestino,CDDNC.NumeroOperacionDestino) AS NumeroOperacionDestino,
IIF(CDDNC.NumeroOperacionDestino IS NULL,CU.NumeroCuenta,CUNC.NumeroCuenta) AS NumeroCuenta,
--IIF(CDDNC.NumeroOperacionDestino IS NULL,NULL,CONCAT('NC-',RIGHT(CONCAT('000000',NC.Correlativo),6))) AS NroNotaCredito,
iif(cdet.FlagPonderosa=1,'POND','SM') as origen


FROM   CobranzaDet AS cdet INNER JOIN prestamoCuota AS precuo ON precuo.CodprestamoCuota = cdet.CodprestamoCuota
                           INNER JOIN CobranzaCab as ccab ON ccab.CodCobranzaCab = cdet.CodCobranzaCab
                           INNER JOIN Prestamo as pre ON pre.codPrestamo = precuo.CodPrestamo 
                           LEFT JOIN Planilla AS pla ON pre.CodPlanilla = pla.CodPlanilla
                           Inner Join Socio as soc ON soc.CodSocio = pre.CodSocio
                           inner join finalidad as fin on fin.CodFinalidad = pre.CodFinalidad
                           inner join TipoCredito as tc on tc.CodTipoCredito = fin.CodTipoCredito
                           LEFT JOIN grupoCab as gr on gr.codGrupoCab = pre.codGrupoCab
						   --   LEFT JOIN CobranzaDocumento as cdoc on ccab.CodCobranzaDocumento = cdoc.CodCobranzaDocumento
						   --   Inner Join TablaMaestraDet as tmdet on tmdet.CodTablaDet = cdoc.CodMedioPago (ORIGUINAL)
                           LEFT JOIN TablaMaestraDet as tmdet on tmdet.CodTablaDet = ccab.CodMedioPago --(NUEVO ACTIVAR)

                           LEFT JOIN Empleado as empl on pre.CodAbogado = empl.CodEmpleado
                           LEFT JOIN TablaMaestraDet as tmdet5 on pre.CodSituacion = tmdet5.CodTablaDet

                            -------
                            LEFT JOIN CobranzaDocumento cdoc ON ccab.CodCobranzaDocumento =cdoc.CodCobranzaDocumento
                            LEFT JOIN Cuenta  CU ON CU.CodCuenta  =cdoc.CodCuentaDestino
                            LEFT JOIN NotaCredito  NC ON ccab.CodNotaCredito =NC.CodNotaCredito
                            LEFT JOIN CobranzaDocumento CDDNC ON NC.CodCobranzaDocumento =CDDNC.CodCobranzaDocumento
                            LEFT JOIN Cuenta  CUNC ON CDDNC.CodCuentaDestino=CUNC.CodCuenta

                            --------
  
-- WHERE        (ccab.Fecha >= '01-01-2020' and ccab.Fecha <= '31-12-2020') and cdet.flagponderosa is null
-- where year(ccab.fecha)=2021 and cdet.CodEstado <> 376 -- and fin.codigo<30 and gr.descripcion like '%PROSEVA%'  
-- 376 Anulado 
-- and cdet.flagponderosa is null

Where EOMONTH(CONVERT(VARCHAR(10),ccab.fecha,112)) = '{fecha_corte}' 
and cdet.CodEstado <> 376
ORDER BY ccab.fecha, 'PagareFincore'

'''

df_cobranza = pd.read_sql_query(query, conn)
del conn

#%% Columna fecha corte respecto a la fecha de cobranza
from calendar import monthrange
from datetime import datetime

def ultimo_dia_del_mes(fecha):
    
    # Obtener el último día del mes
    ultimo_dia = monthrange(fecha.year, fecha.month)[1]

    # Crear una nueva fecha con el último día del mes
    ultimo_dia_del_mes = datetime(fecha.year, 
                                  fecha.month, 
                                  ultimo_dia)
    return ultimo_dia_del_mes

# Aplicar la función a la columna 'fecha_cob' de tu DataFrame
df_cobranza['mes corte'] = df_cobranza['fecha_cob'].apply(ultimo_dia_del_mes)
df_cobranza['mes corte numérica'] = df_cobranza['mes corte'].dt.strftime('%Y%m%d')
df_cobranza['mes corte numérica'] = df_cobranza['mes corte numérica'].astype(int)

#%%
# no incluimos retenciones
df_cobranza_sin_retenciones = df_cobranza[df_cobranza['tipoPago'] != 'RETENCIONES']

#%%
# columnas necesarias
pagos = df_cobranza_sin_retenciones[['PagareFincore', 
                                     "INT_CUOTA",
                                     'numerocuota', 
                                     'NroPlazos', 
                                     'FechaVencimiento',
                                     'fecha_cob',
                                     'fechaCancelacion',
                                     'Socio', 
                                     'planilla',
                                     'codigo',
                                     'TipoCredito',
                                     'FINALIDAD',
                                     'Funcionario',
                                     
                                     'EOM_FVEN',
                                     'EOM_FCAN']]

#%%
def cancelado_en_el_mes(pagos):
    if pagos['EOM_FVEN'] == pagos['EOM_FCAN']:
        return 'SI'
    else:
        return 'NO'
    
pagos['Cancelado en el mes'] = pagos.apply(cancelado_en_el_mes, axis = 1)
    
pagos = pagos[['PagareFincore', 
               "INT_CUOTA",
               'numerocuota', 
               'NroPlazos', 
               'FechaVencimiento',
               'fecha_cob',
               'fechaCancelacion',
               'Cancelado en el mes',
               'Socio', 
               'planilla',
               'codigo',
               'TipoCredito',
               'FINALIDAD',
               'Funcionario']]

#%% AÑADIENDO FUNCIONARIO Y SEDE

if 'admin_age' not in globals():
    conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')

    query = '''
    	SELECT 
    
    	Nro_Fincore, 
    	administrador,
    	master.dbo.[ObtenerAgenciaPorAdministrador](administrador, TipodeProducto43) as 'agencia',
    	FechaCorte1
    
    	FROM anexos_riesgos3..ANX06
    	WHERE Nro_Fincore IS NOT NULL
    	ORDER BY FechaCorte1 DESC
    '''
    
    admin_age = pd.read_sql_query(query, conn)
    conn.close()  # Es mejor cerrar la conexión en lugar de usar `del conn`

    del admin_age['FechaCorte1']  # Elimina la columna FechaCorte1

    admin_age = admin_age.drop_duplicates(subset=['Nro_Fincore'], keep='first')
    
#%%
pagos = pagos.merge(admin_age,
                    left_on  = 'PagareFincore',
                    right_on = 'Nro_Fincore',
                    how      = 'left')

def ajuste_func(pagos):
    if pd.notna(pagos['administrador']):
        return pagos['administrador']
    else:
        return pagos['Funcionario']
    
pagos['funcionario actual'] = pagos.apply(ajuste_func, axis = 1)

###############################################################################
def ajuste_proseva(pagos):
    if 'PROSEVA' in pagos['funcionario actual']:
        return pagos['funcionario actual']
    else:
        return pagos['agencia']

pagos['agencia'] = pagos.apply(ajuste_proseva, axis=1)

###############################################################################
def ajuste_agencia(pagos):
    if pagos['agencia'] in ['1.3 LIMA SALA3', 
                            '1.1 LIMA SALA1',
                            '4.OTROS',
                            '1.2 LIMA SALA2',
                            '1.LIMA',
                            'RESTO DE CARTERA LIMA',
                            '3. LIMA PROVINCIA',
                            'RESTO DE CARTERA PROVINCIA']:
        return 'MAGDALENA'
    elif pd.isna(pagos['agencia']):
        return 'MAGDALENA'
    else:
        return pagos['agencia']

pagos['agencia'] = pagos.apply(ajuste_agencia, axis=1)

#%% COLUMNAS FINALES

pagos = pagos[['PagareFincore', 
               "INT_CUOTA",
               'numerocuota', 
               'NroPlazos', 
               'FechaVencimiento',
               'fecha_cob',
               'fechaCancelacion',
               'Cancelado en el mes',
               'Socio', 
               'planilla',
               'codigo',
               'TipoCredito',
               'FINALIDAD',
               'agencia',
               'funcionario actual']]


#%%
# CREACIÓN DE DATAFRAMES PARA CADA MES

pagos.to_excel(f'df_{fecha_corte}.xlsx',
               index = False)

#%%
print('fin')
print(pagos.shape[0])
