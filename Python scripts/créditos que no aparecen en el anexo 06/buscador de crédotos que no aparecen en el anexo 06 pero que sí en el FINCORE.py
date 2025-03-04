# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 14:47:56 2023

@author: sanmiguel38
"""

# =============================================================================
# VERIFICACIÓN DE CRÉDITOS CON EL FINCORE
# =============================================================================

#%%
import pandas as pd
import os
import pyodbc

#%%
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\TRANSICION  ANEXO 6\\2025\\enero\\parte 2')

anexo06 = 'Rpt_DeudoresSBS Anexo06 - Enero 2025 - campos ampliados 03.xlsx'

fecha_inicio = '20210101' #formato para sql (no cambiar)
fecha_corte  = '20250131' #formato para sql

#%%
df_anx06 = pd.read_excel(io         = anexo06, 
                         skiprows   = 2,
                         dtype      = {'Nro Prestamo \nFincore'  : str})

df_anx06.dropna(subset = ['Apellidos y Nombres / Razón Social 2/', 
                          'Fecha de Nacimiento 3/',
                          'Número de Documento 10/',
                          'Domicilio 12/',
                          'Numero de Crédito 18/'], 
                inplace = True, 
                how     = 'all')

df_anx06 = df_anx06[['Nro Prestamo \nFincore',
                     'Fecha de Desembolso 21/',
                     'Apellidos y Nombres / Razón Social 2/',
                     'Saldo de colocaciones (créditos directos) 24/']]

df_anx06['Nro Prestamo \nFincore'] = df_anx06['Nro Prestamo \nFincore'].str.strip()

# nans = df_anx06[pd.isna(df_anx06['Fecha de Desembolso 21/'])]
df_anx06['Fecha de Desembolso 21/'] = df_anx06['Fecha de Desembolso 21/'].astype(float).astype(int)

# nos quedamos solo con los créditos desembolsados posteriormente a la fecha que hemos establecido
df_anx06 = df_anx06[df_anx06['Fecha de Desembolso 21/'] >= int(fecha_inicio)]

#%%
datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')

server      = datos['DATOS'][0]
username    = datos['DATOS'][2]
password    = datos['DATOS'][3]

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'

conn = pyodbc.connect(conn_str)

########################################################
###                CAMBIAR LA FECHA               ######
########################################################

#extraemos una tabla con el NumerodeCredito18 y ponemos fecha de hace 2 meses (para que jale datos de 2 periodos)
query = f'''

-- p.codcategoria = 351 -> nuevo
-- p.codcategoria = 352 -> ampliacion
-- p.codestado = 563 -> anulado
-- p.codestado = 341 -> pendiente
-- p.codestado = 342 -> cancelado
-- tc.CODTIPOCREDITO -> ( 3=Cons.Ordinario / 1=Med.Empresa / 2=MicroEmp. / 9=Peq.Empresa)

SELECT
	s.codigosocio, 
	iif(s.CodTipoPersona =1, CONCAT(S.ApellidoPaterno,' ',S.ApellidoMaterno, ' ', S.Nombres),s.razonsocial) AS 'Socio',
	iif(s.CodTipoPersona =1, s.nroDocIdentidad, s.nroruc) AS 'Doc_Identidad', 
	RIGHT(CONCAT('0000000',p.numero),8) as 'pagare_fincore', 
	iif(p.codmoneda=94,'S/','US$') as 'moneda', 
	p.fechadesembolso, 
	p.montosolicitado as 'Otorgado', 
	p.TEM, 
	p.NroPlazos, 
	p.CuotaFija,  
	--p.codestado, 
	tm.descripcion as 'Estado',
	p.fechaCancelacion, 
	P.FechaCastigo,
	P.FechaVentaCartera,
	iif(p.codcategoria=351,'NVO','AMPL') as 'tipo_pre', 
	p.flagrefinanciado, 
	pro.descripcion as 'Funcionario',
	CASE
		WHEN pro.descripcion LIKE '%PROSEVA%' THEN pro.descripcion
		WHEN 
		(PRO.DESCRIPCION LIKE '%ADOLFO%HUAMAN%'
		OR PRO.DESCRIPCION LIKE '%CESAR%MEDINA%'
		OR PRO.DESCRIPCION LIKE '%DAYANA%CHIRA%'
		OR PRO.DESCRIPCION LIKE '%ESTHER%RAMIR%'
		OR PRO.DESCRIPCION LIKE '%JESSICA%SOLOR%'
		OR PRO.DESCRIPCION LIKE '%JESICA%SOLOR%'
		OR PRO.DESCRIPCION LIKE '%JORGE%ARAG%'
		OR PRO.DESCRIPCION LIKE '%MARIBEL%PUCH%') THEN 'AREQUIPA'
		WHEN
		(PRO.DESCRIPCION LIKE '%ALEJANDRO%HUAMAN%'
		OR PRO.DESCRIPCION LIKE '%ANA%GUERR%'
		OR PRO.DESCRIPCION LIKE '%ANT%OSORIO%'
		OR PRO.DESCRIPCION LIKE '%EDUAR%TITO%'
		OR PRO.DESCRIPCION LIKE '%ELBER%ALVA%'
		OR PRO.DESCRIPCION LIKE '%FIGARI%VEG%'
		OR PRO.DESCRIPCION LIKE '%GINO%PALO%'
		OR PRO.DESCRIPCION LIKE '%GRICERIO%NU%'
		OR PRO.DESCRIPCION LIKE '%JEAN%BRAV%'
		OR PRO.DESCRIPCION LIKE '%JIMN%MENDO%'
		OR PRO.DESCRIPCION LIKE '%KELLY%HUAM%'
		OR PRO.DESCRIPCION LIKE '%MAR%MARTINE%'
		OR PRO.DESCRIPCION LIKE '%MARTIN%VILCA%'
		OR PRO.DESCRIPCION LIKE '%PAMELA%GARC%'
		OR PRO.DESCRIPCION LIKE '%SUSAN%ROJAS%'
		OR PRO.DESCRIPCION LIKE '%VICTOR%FARFA%'
		OR PRO.DESCRIPCION LIKE '%YESENIA%POTENC%'
		--OR PRO.DESCRIPCION LIKE '%YULAISE%MOREANO%'
		OR PRO.DESCRIPCION LIKE '%GERENCIA%'
		OR PRO.DESCRIPCION LIKE '%LUIS%BUSTAMAN%'
		OR PRO.DESCRIPCION LIKE '%JONAT%ESTRADA%'
		OR PRO.DESCRIPCION LIKE '%GRUPO%'
		OR PRO.DESCRIPCION LIKE '%DAVID%BORJ%'
		OR PRO.DESCRIPCION LIKE '%VICTOR%VARGA%'
		OR PRO.DESCRIPCION LIKE '%BORIS%CAMARGO%'
		) THEN 'LIMA'
				WHEN
		(PRO.DESCRIPCION LIKE '%YULAISE%MOREANO%'
		OR PRO.DESCRIPCION LIKE '%JESUS%CERVERA%'
		OR PRO.DESCRIPCION LIKE '%EDISON%FLORES%'
		) THEN 'SANTA ANITA'
		WHEN 
		(PRO.DESCRIPCION LIKE '%JESSICA%PISCOYA%'
		OR PRO.DESCRIPCION LIKE '%JOSE%SANCHE%'
		OR PRO.DESCRIPCION LIKE '%MILTON%JUARE%'
		OR PRO.DESCRIPCION LIKE '%PAULO%SARE%'
		OR PRO.DESCRIPCION LIKE '%ROY%NARVAE%'
		) THEN 'TRUJILLO'
				WHEN 
		(PRO.DESCRIPCION LIKE '%CESAR%MERA%'
		OR PRO.DESCRIPCION LIKE '%WILLIAMS%TRAUCO%'
		) THEN 'TARAPOTO'
				WHEN 
		(PRO.DESCRIPCION LIKE '%JHONY%SALDA%'
		) THEN 'RESTO DE CARTERA PROVINCIA'
	ELSE 'REVISAR CASO'
		END AS 'ZONAS',
	pla.descripcion as 'Planilla', 
	gpo.descripcion as 'func_pla',
	CONCAT(sc.nombrevia,' Nro ', sc.numerovia,' ', sc.nombrezona) as 'direcc_socio', 
	d.nombre as 'distrito', 
	pv.nombre as 'provincia', 
	dp.nombre as 'departamento', 
	iif(s.codigosocio>28790,'SOC.NVO', 'SOC.ANT') AS 'tipo_soc',
	tm2.descripcion as 'est_civil', 
	pais.descripcion as 'pais', 
	s.fechanacimiento, 
	s.profesion, 
	sc.celular1, 
	SC.TelefonoFijo1, 
	sc.Email, 
	p.CodSituacion, 
	tm3.Descripcion as 'Situacion', 
	p.fechaventacartera, 
	iif(p.flagponderosa=1,'POND','SM') as 'origen', 
	tc.CODTIPOCREDITO AS 'ClaseTipoCredito', 
	tc.Descripcion as 'TipoCredito', 
	FI.CODIGO AS 'COD_FINALIDAD', 
	FI.DESCRIPCION AS 'FINALIDAD', 
	s.FechaNacimiento, 
	s.fechaInscripcion, 
	u.IdUsuario as 'User_Desemb', 
	tm4.descripcion as 'EstadoSocio'


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
LEFT JOIN PrestamosVendidos AS VENDIDOSS ON P.CodPrestamoPND = VENDIDOSS.CodPrestamoPND

where 
CONVERT(VARCHAR(10),p.fechadesembolso,112) BETWEEN '{fecha_inicio}' and '{fecha_corte}' 

and s.codigosocio>0  and p.codestado = 341
--and tm4.descripcion = 'HABIL'
and VENDIDOSS.CodPrestamoPND IS NULL
--AND FI.CODIGO IN (15,16,17,18,19,20,21,22,23,24,25,29)
-- and (p.CODTIPOCREDITO=2 or p.CODTIPOCREDITO=9) and pcu.NumeroCuota=1 and tm2.descripcion is null 
-- 341 PENDIENTES  /  p.codestado <> 563  anulados
--where year(p.fechadesembolso) >= 2021 and month(p.fechadesembolso) >= 1 and s.codigosocio>0 and p.codestado <> 563 AND tc.CODTIPOCREDITO <>3 -- and pro.Descripcion like '%WILLIAMS TRAUCO%' --  and p.codcategoria=351
order by socio asc, p.fechadesembolso desc

'''

df_fincore = pd.read_sql_query(query, conn)
del conn

df_fincore = df_fincore[['pagare_fincore'  , 
                         'Socio'           , 
                         'fechadesembolso' , 
                         'Otorgado'        , 
                         'Planilla'        , 
                         'FechaVentaCartera']]

df_fincore = df_fincore[ pd.isna(df_fincore['FechaVentaCartera']) | (df_fincore['FechaVentaCartera'] >= pd.Timestamp(fecha_corte))]

#%%

filas_filtradas = df_fincore[~df_fincore['pagare_fincore'].isin(df_anx06['Nro Prestamo \nFincore']) & # no están en el anexo06
                             (df_fincore['Planilla'] != 'PLANILLA FALLECIDOS')   ]                    # no sean PLANILLA FALLECIDOS

'incluyendo fallecidos:'
incluye_fallecidos = df_fincore[~df_fincore['pagare_fincore'].isin(df_anx06['Nro Prestamo \nFincore'])]

# incluye_fallecidos.to_excel('mueltos.xlsx',
#                             index = False)

