# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 10:28:10 2024

@author: Joseph Montoya
"""

# =============================================================================
# SOCIOS SIN MOROSIDAD PARA EL SORTEO
# =============================================================================
import pandas as pd
import pyodbc
import os

#%%
fecha_corte = '20240229'

fecha_hoy = '20240331'

os.chdir('C:\\Users\\sanmiguel38\\Desktop\\socios buenos para sorteo\\anexo 06 febrero 2024')

# Cargar el último Anexo06 en el formato que se envía a los demás
nombre_anx06 = 'Rpt_DeudoresSBS Anexo06 - Febrero 2024 - campos ampliados v08.xlsx'

filas_skip   = 2

usar_sql     = False # True o False, si le das False, es obligatorio definir un excel de anexo06

#%%
if usar_sql == True:
    conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')

    query = f'''
    DECLARE @FECHACORTE AS DATETIME = '{fecha_corte}'
    
    SELECT 
    	ApellidosyNombresRazonSocial2,
    	NumerodeDocumento10,
    	TipodeDocumento9,
    	Nro_Fincore,
    	FechadeDesembolso21,
    	MontodeDesembolso22,
    	TipodeProducto43,
        CapitalVencido29 + CapitalenCobranzaJudicial30 + SaldosdeCreditosCastigados38 + CapitalRefinanciado28 + Reprogramados52 AS 'deteriorado'

    FROM anexos_riesgos3..ANX06
    WHERE FechaCorte1 = @FECHACORTE
    AND TipodePersona11 = 1
    '''

    anx06 = pd.read_sql_query(query, conn)

else:
    anx06 = pd.read_excel(io       = nombre_anx06,
                          skiprows = filas_skip,
                          dtype    = {'Nro Prestamo \nFincore'  : str,
                                      'Fecha de Desembolso 21/' : str})
    
    anx06.dropna(subset = [# 'Apellidos y Nombres / Razón Social 2/', 
                           'Fecha de Nacimiento 3/',
                           'Número de Documento 10/',
                           'Domicilio 12/',
                           'Numero de Crédito 18/'], inplace = True, how = 'all')

    
    anx06 = anx06[['Apellidos y Nombres / Razón Social 2/',
                   'Número de Documento 10/',
                   'Tipo de Documento 9/',
                   'Nro Prestamo \nFincore',
                   'Fecha de Desembolso 21/',
                   'Monto de Desembolso 22/',
                   'Tipo de Producto 43/',
                   
                   'Capital Vencido 29/',
                   'Capital en Cobranza Judicial 30/',
                   'Saldos de Créditos Castigados 38/',
                   'Capital Refinanciado 28/']]
    anx06['deteriorado'] = anx06['Capital Vencido 29/'] + anx06['Capital en Cobranza Judicial 30/'] + anx06['Saldos de Créditos Castigados 38/'] + anx06['Capital Refinanciado 28/']
    del anx06['Capital Vencido 29/']
    del anx06['Capital en Cobranza Judicial 30/']
    del anx06['Saldos de Créditos Castigados 38/']
    del anx06['Capital Refinanciado 28/']
    anx06.rename(columns = {'Apellidos y Nombres / Razón Social 2/' : 'ApellidosyNombresRazonSocial2',
                            'Número de Documento 10/'               : 'NumerodeDocumento10',
                            'Tipo de Documento 9/'                  : 'TipodeDocumento9',
                            'Nro Prestamo \nFincore'                : 'Nro_Fincore',
                            'Fecha de Desembolso 21/'               : 'FechadeDesembolso21',
                            'Monto de Desembolso 22/'               : 'MontodeDesembolso22',
                            'Tipo de Producto 43/'                  : 'TipodeProducto43'}, 
                 inplace = True)
    
    anx06['FechadeDesembolso21'] = anx06['FechadeDesembolso21'].astype(int)
    anx06['FechadeDesembolso21'] = anx06['FechadeDesembolso21'].astype(str)
    
    # from datetime import datetime
    
    # este parseador es perfecto y una de mis mejores creaciones de todos los tiempos
    formatos = ['%d/%m/%Y %H:%M:%S',
                '%d/%m/%Y',
                '%Y%m%d', 
                '%Y-%m-%d', 
                '%Y-%m-%d %H:%M:%S', 
                '%Y/%m/%d %H:%M:%S',
                '%Y-%m-%d %H:%M:%S PM',
                '%Y-%m-%d %H:%M:%S AM',
                '%Y/%m/%d %H:%M:%S PM',
                '%Y/%m/%d %H:%M:%S AM']  # Lista de formatos a analizar
    
    def parse_dates(date_str):
        '''
        Parameters
        ----------
        date_str : Es el formato que va a analizar dentro de la columna del DataFrame.
    
        Returns
        -------
        Si el date_str tiene una estructura compatible con los formatos preestablecidos
        para su iteración, la convertirá en un DateTime
    
        '''
        for formato in formatos:
            try:
                return pd.to_datetime(date_str, format=formato)
            except ValueError:
                pass
        return pd.NaT
    
    anx06['FechadeDesembolso21'] = anx06['FechadeDesembolso21'].apply(parse_dates)

#%% filtramos los créditos buenos del anexo06
buenos_y_malos = anx06.pivot_table(values = 'deteriorado',
                                    index = 'NumerodeDocumento10').reset_index()

# SOCIOS SIN MOROSIDAD
buenos = buenos_y_malos[buenos_y_malos['deteriorado'] == 0]

anx06 = anx06[anx06['NumerodeDocumento10'].isin(buenos['NumerodeDocumento10'])]

#%% desembolsados este mes
datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')

#%%

server      = datos['DATOS'][0]
username    = datos['DATOS'][2]
password    = datos['DATOS'][3]

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'

conn = pyodbc.connect(conn_str)

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

fecha_inicio = fecha_hoy[0:6] + '01'

query = f'''
SELECT

	iif(s.CodTipoPersona =1, CONCAT(S.ApellidoPaterno,' ',S.ApellidoMaterno, ' ', S.Nombres),s.razonsocial) AS 'Socio',
	iif(s.CodTipoPersona =1, s.nroDocIdentidad, s.nroruc) AS 'Doc_Identidad', 
	RIGHT(CONCAT('0000000',p.numero),8) as 'pagare_fincore', 
	iif(p.codmoneda=94,'S/','US$') as 'moneda', 
	p.fechadesembolso, 
	p.montosolicitado as 'Otorgado', 
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
CONVERT(VARCHAR(10),p.fechadesembolso,112) BETWEEN '{fecha_inicio}' AND '{fecha_hoy}' 
and s.codigosocio>0  and p.codestado = 341
AND s.CodTipoPersona =1
order by p.fechadesembolso DESC

'''
df_desembolsados = pd.read_sql_query(query, 
                                     conn,
                                     dtype = {'COD_FINALIDAD' : str})

#%% concatenamos ambas tablas (anexo 06 y desembolsos del mes actual)
base = anx06.rename(columns = {'ApellidosyNombresRazonSocial2' : 'Socio',
                               'NumerodeDocumento10'           : 'Doc_Identidad',
                               'FechadeDesembolso21'           : 'fechadesembolso',
                               'MontodeDesembolso22'           : 'Otorgado'})

base = base[['Socio',
             'Doc_Identidad',
             'Nro_Fincore',
             'fechadesembolso',
             'Otorgado']]
base = base.sort_values(by = ['Socio'])

df_desembolsados = df_desembolsados.rename(columns = {'pagare_fincore' : 'Nro_Fincore'})
df_desembolsados = df_desembolsados[['Socio',
                                     'Doc_Identidad', 
                                     'Nro_Fincore', 
                                     'fechadesembolso', 
                                     'Otorgado']]
df_desembolsados = df_desembolsados.sort_values(by = ['Socio'])

base = pd.concat([base, df_desembolsados], ignore_index = True)

#%% eliminamos los créditos cancelados

base = base[~base['Nro_Fincore'].isin(df_cancelados['pagare_fincore'])]

#%% a excel

base.to_excel(f'Socios sin morosidad {fecha_hoy}.xlsx',
              index = False)
