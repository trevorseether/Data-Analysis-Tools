# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 18:58:42 2023

@author: Joseph Montoya
"""

import pyodbc
import pandas as pd

#%%
datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')

#%%

server      = datos['DATOS'][0]
username    = datos['DATOS'][2]
password    = datos['DATOS'][3]

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'

conn = pyodbc.connect(conn_str)

########################################################
###                CAMBIAR LA FECHA               ######
########################################################

#extraemos una tabla con el NumerodeCredito18 y ponemos fecha de hace 2 meses (para que jale datos de 2 periodos)
fecha_hoy = '20230807'
query = f'''
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
	p.codestado, 
	tm.descripcion as 'Estado',
	p.fechaCancelacion, 
	iif(p.codcategoria=351,'NVO','AMPL') as 'tipo_pre', 
	p.flagrefinanciado, 
	pro.descripcion as 'Funcionario', 
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
	p.FechaVentaCartera, 
	tm4.descripcion as 'EstadoSocio'
-- pcu.FechaVencimiento as Fecha1raCuota, pcu.NumeroCuota, pcu.SaldoInicial,
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

where CONVERT(VARCHAR(10),p.fechadesembolso,112) 
BETWEEN '20110101' AND '{fecha_hoy}' and s.codigosocio>0  and p.codestado = 341 -- and (p.CODTIPOCREDITO=2 or p.CODTIPOCREDITO=9) and pcu.NumeroCuota=1 and tm2.descripcion is null -- 341 PENDIENTES  /  p.codestado <> 563  anulados
--where year(p.fechadesembolso) >= 2021 and month(p.fechadesembolso) >= 1 and s.codigosocio>0 and p.codestado <> 563 AND tc.CODTIPOCREDITO <>3 -- and pro.Descripcion like '%WILLIAMS TRAUCO%' --  and p.codcategoria=351
order by socio asc, p.fechadesembolso desc

'''

df_fincore = pd.read_sql_query(query, conn)
del conn
