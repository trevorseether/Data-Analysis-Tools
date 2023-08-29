# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 17:56:41 2023

@author: Joseph Montoya
"""

############################################################
#   KASHIO: REPORTE MENSUAL PARA COBRANZAS
############################################################

#%%
import pandas as pd
import pyodbc
import os

MES          = 'SEPTIEMBRE 2023'
fecha_inicio = '2023-09-01'
fecha_final  = '2023-09-30'

#%% UBICACIÓN DE LOS ARCHIVOS
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\KASHIO\\2023 AGOSTO\\28 agosto 2023')

#%%
'NOMBRE DEL ARCHIVO DE HOY' ##########################################
ARCHIVO_HOY = 'insumo cobranzas 20230828.xlsx'
#####################################################################

#%%
kashio = pd.read_excel(ARCHIVO_HOY,
                       dtype={'ID CLIENTE'          : str,
                              'TELEFONO'            : str,
                              'ID ORDEN DE PAGO'    : str,
                              'REFERENCIA'          : str,
                              'MONTO'               : float,
                              'VENCIMIENTO'         : str})

kashio['ID CLIENTE']       = kashio['ID CLIENTE'].str.strip()
kashio['TELEFONO']         = kashio['TELEFONO'].str.strip()
kashio['ID ORDEN DE PAGO'] = kashio['ID ORDEN DE PAGO'].str.upper()

# nos quedamos solo con los números de DNI
kashio['DNI'] = kashio['NUMERO DOCUMENTO'].str.extract('(\d+)')

#%%
kashio_ordenado = kashio[['DNI', 'NOMBRE', 'ID ORDEN DE PAGO', 'MONEDA','MONTO',
                          'ID CLIENTE', 'REFERENCIA', 'VENCIMIENTO']]

# parseo de fechas
formatos = ['%d/%m/%Y']  # Lista de formatos a analizar

def parse_dates(date_str):
    for formato in formatos:
        try:
            return pd.to_datetime(date_str, format=formato)
        except ValueError:
            pass
    return pd.NaT

kashio_ordenado['VENCIMIENTO'] = kashio_ordenado['VENCIMIENTO'].apply(parse_dates)

#%% FILTRADO DE FECHAS

kashio_filtrado = kashio_ordenado[(kashio_ordenado['VENCIMIENTO'] >= pd.Timestamp(fecha_inicio)) &
                                  (kashio_ordenado['VENCIMIENTO'] <= pd.Timestamp(fecha_final))]

kashio_filtrado = kashio_filtrado.rename(columns={'NOMBRE'      : "Nombre Cliente",
                                                  'ID ORDEN DE PAGO'    : 'CODIGO DE PAGO',
                                                  'MONTO'       : 'VALOR PAGO',
                                                  'ID CLIENTE'  : 'codsoc',
                                                  'REFERENCIA'  : 'num pagare',
                                                  'VENCIMIENTO' : 'Fecha Cuota'})

#%% IMPORTAMOS DATOS DEL SQL PARA HACER UN MERGE
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
fecha_corte = '20230930'
query = f'''
SELECT
    RIGHT(CONCAT('0000000',p.numero),8) as 'pagare_fincore', 
	s.codigosocio, 
	iif(s.CodTipoPersona =1, s.nroDocIdentidad, s.nroruc) AS 'Doc_Identidad',
	pro.descripcion as 'Funcionario',
	d.nombre as 'distrito',
	pv.nombre as 'provincia',
	dp.nombre as 'departamento',
	sc.celular1,
	sc.Email,
	tc.Descripcion as 'TipoCredito',
	FI.CODIGO AS 'COD_FINALIDAD'
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
<= '{fecha_corte}' and s.codigosocio>0  and p.codestado = 341
'''

df_fincore = pd.read_sql_query(query, conn)
del conn

#%% columnas necesarias para merge
df_fincore = df_fincore[['pagare_fincore','Doc_Identidad', 
                         'celular1', 'Email', 'Funcionario', 
                         'distrito', 'provincia', 'departamento',
                         'COD_FINALIDAD', 'TipoCredito']]

#%% merge

kashio_union = kashio_filtrado.merge(df_fincore, 
                             left_on=['num pagare'], 
                             right_on=['pagare_fincore']
                             ,how='inner') #'left'  si le ponemos left, vemos las cancelaciones
                             #inner porque los casos que no hagan match es porque ya fueron cancelados

owo = kashio_union[kashio_union['DNI'] != kashio_union['Doc_Identidad']]
print(owo)

#%%
kashio_final = kashio_union[['DNI', 'Nombre Cliente', 'CODIGO DE PAGO',
                             'MONEDA', 'VALOR PAGO', 'codsoc', 'num pagare',
                             'Fecha Cuota', 'celular1', 'Email', 'Funcionario',
                             'departamento', 'provincia', 'distrito', 'COD_FINALIDAD',
                             'TipoCredito']]

kashio_final = kashio_final.rename(columns={'codsoc'    : 'CODSOC',
                                            'num pagare': 'NUM PAGARE',
                                            'celular1'  : 'CELULAR',
                                            'Email'     : 'CORREO',
                                            'Funcionario'   : 'FUNCIONARIO',
                                            'departamento'  : 'DEPARATAMENTO',
                                            'provincia' : 'PROVINCIA',
                                            'distrito'  : 'DISTRITO',
                                            'TipoCredito'   : 'PRODUCTO'})

#%% arreglito para libre disponibilidad
def libre_disponibildiad(kashio_final):
    if kashio_final['COD_FINALIDAD'] in [30,31,32,33,'30','31', '32', '33']:
        return 'LIBRE DISPONIBILIDAD'
    else:
        return kashio_final['PRODUCTO']
    
kashio_final['PRODUCTO'] = kashio_final.apply(libre_disponibildiad, axis=1)

#%% EXPORTACIÓN A EXCEL
nombre = "KASHIO COBRANZAS - CUOTAS " + MES + '.xlsx'
try:
    ruta = nombre
    os.remove(ruta)
except FileNotFoundError:
    pass

kashio_final.to_excel(nombre, index=False)

#%%
'SE ENVÍA A COBRANZAS'