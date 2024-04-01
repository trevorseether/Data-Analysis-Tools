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

'Directorio de trabajo'
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\socios buenos para sorteo')
#%%
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

base = base[['Socio','Doc_Identidad', 'Nro_Fincore', 'fechadesembolso', 'Otorgado']]
base = base.sort_values(by=['Socio'])

df_desembolsados = df_desembolsados.rename(columns = {'pagare_fincore' : 'Nro_Fincore'})
df_desembolsados = df_desembolsados[['Socio','Doc_Identidad', 'Nro_Fincore', 'fechadesembolso', 'Otorgado']]
df_desembolsados = df_desembolsados.sort_values(by=['Socio'])

base = pd.concat([base, df_desembolsados], ignore_index = True)

#%% eliminamos los créditos cancelados

base = base[~base['Nro_Fincore'].isin(df_cancelados['pagare_fincore'])]

#%% a excel

base.to_excel(f'Socios sin morosidad {fecha_hoy}.xlsx',
              index = False)
