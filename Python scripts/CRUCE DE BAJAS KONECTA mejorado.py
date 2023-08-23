# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 10:46:51 2023

@author: Joseph Montoya Muñoz
"""

###############################################################################
##          CRUCE DE BAJAS DE KONECTA
###############################################################################

import pandas as pd
import os
import numpy as np
import pyodbc

#%%

'AQUI SE PONE LA FECHA QUE UNO QUIERE QUE APAREZCA EN EL NOMBRE DEL ARCHIVO'
############################################################################
FECHATXT = '22-08-2023'
############################################################################

'ubicación de trabajo'
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\BAJAS KONECTA\\2023 AGOSTO\\22 agosto 2023 p2')

#%%
################################
#  DATA ENVIADA POR COBRANZA
################################

bajas = pd.read_excel('VF ADICIONAL 6TO INFORME DE BAJAS GRUPO - AGOSTO 2023.xlsx',
                    dtype=({'Documento': object}))

bajas['Documento'] = bajas['Documento'].astype(str)
bajas['Documento'] = bajas['Documento'].str.strip()

uwu = bajas[pd.isna(bajas['Documento'])]
print('Documentos que se hayan convertido en Null:')
print(uwu.shape[0])
bajas['Documento original'] =   bajas['Documento']
bajas['Documento'] = bajas['Documento'].str.zfill(14)
print('Documentos que se hayan convertido en Null:')

if uwu.shape[0] > 0:
    print(uwu)
    print('investigar qué ha pasado ( ´･･)ﾉ(._.`)')
else:
    print(uwu.shape[0])
    del uwu
    print('''todo bien (●'◡'●)''')

#%% LECTURA DE LAS CREDENCIALES
datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')

#%% CREACIÓN DE LA CONECCIÓN A SQL

server      = datos['DATOS'][0]
username    = datos['DATOS'][2]
password    = datos['DATOS'][3]

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'

conn = pyodbc.connect(conn_str)

#%%
########################################################
###                CAMBIAR LA FECHA               ######
########################################################

###############################################################################
fecha_hoy = '20230822' ######### NO OLVIDAAR (AQUÍ VA LA FECHA DE HOY) ########
###############################################################################
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
vigentes = pd.read_sql_query(query, conn, dtype={'Doc_Identidad': object,
       'codigosocio': object,
       'pagare_fincore': object,
       'fechadesembolso': object
       })
del conn
#%%
#parsenado las fechas
formatos = ['%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y',
            '%Y%m%d', '%Y-%m-%d', 
            '%Y-%m-%d %H:%M:%S', 
            '%Y/%m/%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S PM',
            '%Y-%m-%d %H:%M:%S AM']  # Lista de formatos a analizar
def parse_dates(date_str):
    for formato in formatos:
        try:
            return pd.to_datetime(date_str, format=formato)
        except ValueError:
            pass
    return pd.NaT

vigentes['fechadesembolso'] = vigentes['fechadesembolso'].apply(parse_dates)

#%%
'por si acaso, nos quedamos solo con los que tienen estado = pendiente'

vigentes["Estado"] = vigentes["Estado"].str.strip() #quitamos espacios
vigentes["Estado"] = vigentes["Estado"].str.upper() #mayúsculas

vigentes = vigentes[vigentes["Estado"] == 'PENDIENTE']

#%%
'agregamos 14 ceros al reporte EXTRAIDO CON SQL'
vigentes["Doc_Identidad"] = vigentes["Doc_Identidad"].astype(str)
vigentes["DOC_IDENTIDAD_ceros"] = vigentes["Doc_Identidad"].str.zfill(14)

#%%
'nos quedamos solo con las columnas necesarias'

vigentes2 = vigentes[["DOC_IDENTIDAD_ceros", "Socio", "fechadesembolso", "pagare_fincore", "CuotaFija", "Planilla"]]
vigentes2 = vigentes2.rename(columns={"Doc_Identidad"   : "DOC_IDENTIDAD",
                                      "Socio"           : "SOCIO",
                                      "fechadesembolso" : "FECHA_DESEMBOLSO",
                                      "pagare_fincore"  : "PAGARE_FINCORE",
                                      "CuotaFija"       : "CUOTA MENSUAL",
                                      "Planilla"        : "EMPRESA/PLANILLA"})

bajas2 = bajas[['Documento', 'Documento original']]
#%%
'inner join usando '
df_resultado = vigentes2.merge(bajas2, 
                               left_on=["DOC_IDENTIDAD_ceros"], 
                               right_on=['Documento']
                               ,how='inner')

#%%
'''creamos el archivo final'''

df_resultado['SALDO A DESCONTAR'] = np.nan
df_resultado['# CUOTAS'] = np.nan

final = df_resultado[['Documento original',
                      'SOCIO', 
                      'FECHA_DESEMBOLSO', 
                      'SALDO A DESCONTAR', 
                      '# CUOTAS',"CUOTA MENSUAL",
                      'PAGARE_FINCORE', 
                      "EMPRESA/PLANILLA"]]

final = final.rename(columns={'Documento original': 'Documento'})

#%% NOS QUEDAMOS SOLO CON LAS COLUMNAS NECESARIAS (ya lo que hacíamos a mano no hace falta)

final = final[['Documento', 
               'SOCIO', 
               'FECHA_DESEMBOLSO',
               'CUOTA MENSUAL', 
               'PAGARE_FINCORE', 
               'EMPRESA/PLANILLA']]

# POR SI ACASO, ELIMINAMOS DUPLICADOS
final.drop_duplicates(subset = 'PAGARE_FINCORE', inplace=True)

#%%

NOMBRE = 'BAJAS '+ FECHATXT +'.xlsx'
try:

    os.remove(NOMBRE)
except FileNotFoundError:
    pass

final.to_excel(NOMBRE, index=False,
               sheet_name=FECHATXT)


