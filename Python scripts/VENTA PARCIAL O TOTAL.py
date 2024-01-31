# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 16:14:45 2024

@author: Joseph Montoya
"""
# =============================================================================
# VALIDACIÓN DE SI EL CRÉDITO ES VENTA TOTAL O PARCIAL
# =============================================================================

import pandas as pd
import pyodbc
import os
import warnings
warnings.filterwarnings('ignore')

#%%
fecha_corte = '20231231'

directorio = 'C:\\Users\\sanmiguel38\\Desktop\\VENTA DE CARTERA TOTAL O PARCIAL'

anx06      = 'Rpt_DeudoresSBS Anexo06 - Diciembre 2023 - campos ampliados version final v5.xlsx'
ubi_anx06  = 'C:\\Users\\sanmiguel38\\Desktop\\TRANSICION  ANEXO 6\\2023 DICIEMBRE\\V FINAL'

fecha_hoy_sql = '20240131'

#%%
os.chdir(directorio)

#%% ANEXO 06
df_anx_06 = pd.read_excel(io       = ubi_anx06 + '\\' + anx06, 
                          skiprows = 2,
                          dtype = {'Nro Prestamo \nFincore'  : str,
                                   'Código Socio 7/'         : str,
                                   'Número de Documento 10/' : str})
#eliminando las filas con NaN en las siguiente columnas al mismo tiempo:
df_anx_06.dropna(subset = ['Apellidos y Nombres / Razón Social 2/', 
                           'Fecha de Nacimiento 3/',
                           'Número de Documento 10/',
                           'Domicilio 12/',
                           'Numero de Crédito 18/'], 
                 inplace = True, 
                 how     = 'all')

df_anx_06.rename(columns = {'Nro Prestamo \nFincore' : 'pagare_fincore'}, inplace = True)
df_anx_06['pagare_fincore'] = df_anx_06['pagare_fincore'].str.strip()

#%% créditos desembolsados
fecha_inicio = fecha_hoy_sql[:-2] + '01'

datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')
server      = datos['DATOS'][0]
username    = datos['DATOS'][2]
password    = datos['DATOS'][3]

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'
conn = pyodbc.connect(conn_str)

query = f'''
-- p.codcategoria = 351 -> nuevo
-- p.codcategoria = 352 -> ampliacion
-- p.codestado = 563 -> anulado
-- p.codestado = 341 -> pendiente
-- p.codestado = 342 -> cancelado
-- tc.CODTIPOCREDITO -> ( 3=Cons.Ordinario / 1=Med.Empresa / 2=MicroEmp. / 9=Peq.Empresa)

SELECT
	s.codigosocio as 'Código Socio 7/', 
	iif(s.CodTipoPersona =1, CONCAT(S.ApellidoPaterno,' ',S.ApellidoMaterno, ' ', S.Nombres),s.razonsocial) AS 'Socio',
	iif(s.CodTipoPersona =1, s.nroDocIdentidad, s.nroruc) AS 'Número de Documento 10/', 
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

where 
CONVERT(VARCHAR(10),p.fechadesembolso,112) BETWEEN '{fecha_inicio}' AND '{fecha_hoy_sql}' 
and s.codigosocio>0  and p.codestado = 341
order by socio asc, p.fechadesembolso desc
'''

df_desembolsados = pd.read_sql_query(query, conn)

#%%
# venta_cartera = pd.read_excel('nombre.xlsx')

#%%
columnas = ['pagare_fincore',
            'Código Socio 7/',
            'Número de Documento 10/']

anx06 = df_anx_06[columnas]

anx06['Origen'] = 'Anexo 06'

desem = df_desembolsados[columnas]

desem['Origen'] = 'Desembolsado posterior'

#%% concatenación

df_concatenado = pd.concat([anx06, desem], ignore_index = True)

#%%
# query = '''
# SELECT

# 	RIGHT(CONCAT('0000000',p.numero),8) as 'pagare_fincore',
# 	p.fechaCancelacion

# FROM prestamo as p

# inner join socio as s on s.codsocio = p.codsocio
# where CONVERT(VARCHAR(10),p.fechadesembolso,112) > '20100101' 
# and s.codigosocio>0  
# and p.codestado = 342
# order by p.fechadesembolso desc

# '''

# df_cancelados = pd.read_sql_query(query, conn)

#%% no se deben quitar los créditos cancelados, porque si el socio cancela, después del corte y se vende el otro crédito
# este debe seguir considerándose como venta parcial
#%% contamos el número de créditos por socio
num_cred = df_concatenado.groupby('Código Socio 7/')['pagare_fincore'].count().reset_index()
num_cred.rename(columns = {'pagare_fincore' : 'número de créditos'}, inplace = True)


df_concatenado = df_concatenado.merge(num_cred,
                                      on = 'Código Socio 7/',
                                      how = 'left')

#%% por si acaso, eliminamos duplicados en nro fincore
filas1 = df_concatenado.shape[0]

df_concatenado.drop_duplicates(subset = 'pagare_fincore', inplace=True)
filas2 = df_concatenado.shape[0]
if filas1 > filas2:
    print('algo ha pasado, hay duplicados, investigar')
else:
    print('todo ok o((>ω< ))o')

#%%
# df_concatenado['número de créditos'].unique()

#%%  eliminar todo esto una vez que tengamos el formato de castigo
lista_venta_cartera_provisonal = ['00000681','00025314','00051147','00019565','00059920','00025678','00055472','00001346','00009592',
                                  '00050796','00021245','00014203','00019911','00052890','00020153','00000633','00021016','00000942',
                                  '00023215','00020154','00054955','00016572','00001147','00001287','00055472','00061987','00010827',
                                  '00021016','00023215','00014819','00058140','00057592','00060249','00016572','00021994','00087481',
                                  '00093507','00098725','00094791','00103282','00088637','00080108','00096417','00068978','00097332',
                                  '00098973','00098454','00082582','00101711','00091367','00099619','00084311','00091354','00085994',
                                  '00098112','00100112','00078588','00096775','00102941','00085287','00073062','00086998','00085544',
                                  '00088082','00091858','00090487','00097094','00102185','00088217','00096808','00099864','00088644',
                                  '00083469','00102177','00085358','00094227','00102322','00084146','00090588','00099821','00089733',
                                  '00088497','00101038','00100125','00101012','00084875','00102430','00092802','00097977','00086775',
                                  '00091004','00091310','00092930','00097354','00101033','00085161','00092292','00091373','00092595',
                                  '00099885','00082054','00101699','00086604','00081400','00092060','00095283','00099348','00098095',
                                  '00095355','00072746','00084530','00093694','00100895','00095425','00097641','00067015','00092751',
                                  '00091010','00085926','00090392','00102370','00095112','00083885','00088722','00081477','00103274',
                                  '00103362','00099863','00082785','00093411','00074648','00089889','00094732','00081776','00101647',
                                  '00093146','00089808','00100907','00088965','00090835','00096505','00078869','00095031','00099342',
                                  '00090816','00099221','00097237','00101581','00084039','00094083','00072567','00087753','00085628',
                                  '00087968','00097960','00072999','00099858','00086685','00075441','00098849','00100986','00101057',
                                  '00093332','00100957','00101875','00090798','00076590','00090764','00078831','00088290','00102535',
                                  '00081777','00098957','00084306','00099407','00089822','00090170','00102369','00092291','00092446',
                                  '00085151','00083856','00081296','00098963','00088014','00074571','00101726','00085672','00088666',
                                  '00083585','00099717']

data = {
        'fincore' : lista_venta_cartera_provisonal,
        'num'     : range(0,191)
        }

venta_cartera = pd.DataFrame(data)
#%%
# primero que nada, alerta de créditos que están en la lista de castigos, y no están en la base
no_aparecen = venta_cartera[~venta_cartera['fincore'].isin(list(df_concatenado['pagare_fincore']))]

print(no_aparecen)

#activar cuando ya sea el reporte finalizado
# pd.to_excel('no_aparecen.xlsx',
            # index = False)

#%%
def vendido(df):
    if df['pagare_fincore'] in list(venta_cartera['fincore']):
        return 'cred vendido'
    else:
        return ''

df_concatenado['vendido'] = df_concatenado.apply(vendido, axis = 1)

socios_vendidos = df_concatenado[df_concatenado['vendido'] == 'cred vendido']

socios_mas_de_uno = socios_vendidos[socios_vendidos['número de créditos'] > 1]

#socios que tienen más de un crédito, y al menos uno de los créditos ha sido vendido
socios_mas_de_uno = socios_mas_de_uno[['Código Socio 7/', 'Número de Documento 10/']].drop_duplicates(subset = 'Código Socio 7/')

#%%
def mas_de_uno_y_vendido(df):
    if df['Código Socio 7/'] in list(socios_mas_de_uno['Código Socio 7/']):
        return 'vendido y más de uno'
    else:
        return ''

df_concatenado['auxiliar 1'] = df_concatenado.apply(mas_de_uno_y_vendido, axis = 1)

ventas_parciales = df_concatenado[(df_concatenado['auxiliar 1'] =='vendido y más de uno') &
                                  (df_concatenado['vendido'] == '')]

#%%
def venta_parcial(df):
    if df['Código Socio 7/'] in list(ventas_parciales['Código Socio 7/']):
        return 'Venta Parcial'
    else:
        return ''
        
df_concatenado['auxiliar 2'] = df_concatenado.apply(venta_parcial, axis = 1)

def venta_total(df):
    if (df['vendido'] == 'cred vendido') and (df['auxiliar 2'] == ''):
        return 'Venta Total'
    else:
        return df['auxiliar 2']

df_concatenado['auxiliar 2'] = df_concatenado.apply(venta_total, axis = 1)

#%%

df_concatenado['Tipo Venta'] = df_concatenado['auxiliar 2']

df_final = df_concatenado[['pagare_fincore', 
                           'Código Socio 7/', 
                           'Número de Documento 10/',
                           'Origen', 
                           'número de créditos',
                           'Tipo Venta']]

vendidos = df_final[df_final['Tipo Venta'] != '']

#%% a excel

vendidos.to_excel('tipo de venta.xlsx',
                  index = False)

