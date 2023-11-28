# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 17:33:39 2023

@author: sanmiguel38
"""

import pyodbc
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

#%%
datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')

fecha_desembolso_fincore = '20200101'

#%% 
# =============================================================================
# leyendo creditos cancelados cuyo desembolso haya sido posterior al 2022
# =============================================================================
server    =  datos['DATOS'][0]
username  =  datos['DATOS'][2]
password  =  datos['DATOS'][3]

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'

conn = pyodbc.connect(conn_str)

#####################################################
###                CAMBIAR LA FECHA               ###
#####################################################

#extraemos una tabla con el NumerodeCredito18 y ponemos fecha de hace 2 meses (para que jale datos de 2 periodos)
query = '''

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
CONVERT(VARCHAR(10),p.fechadesembolso,112) >= '{fecha_desembolso_fincore}'
and s.codigosocio>0  and p.codestado = 342
--AND FI.CODIGO IN (15,16,17,18,19,20,21,22,23,24,25,29)
-- and (p.CODTIPOCREDITO=2 or p.CODTIPOCREDITO=9) and pcu.NumeroCuota=1 and tm2.descripcion is null -- 341 PENDIENTES  /  p.codestado <> 563  anulados
--where year(p.fechadesembolso) >= 2021 and month(p.fechadesembolso) >= 1 and s.codigosocio>0 and p.codestado <> 563 AND tc.CODTIPOCREDITO <>3 -- and pro.Descripcion like '%WILLIAMS TRAUCO%' --  and p.codcategoria=351
order by socio asc, p.fechadesembolso desc

'''

df_fincore = pd.read_sql_query(query, conn)
del conn

#%% df fincore con retenciones

df_fincore_amp = df_fincore[df_fincore['tipo_pre'] == 'AMPL']
socios_con_ampl = list(set(list(df_fincore_amp['Doc_Identidad'])))

#%% lectura de la cobranza
conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'

conn = pyodbc.connect(conn_str)

########################################################
###                CAMBIAR LA FECHA               ######
########################################################

#extraemos una tabla con el NumerodeCredito18 y ponemos fecha de hace 2 meses (para que jale datos de 2 periodos)
query = '''

SELECT 
	soc.codsocio, 
	soc.codigosocio, 
	iif(soc.CodTipoPersona =1,concat(soc.apellidopaterno,' ',soc.apellidomaterno,' ',soc.nombres),soc.razonsocial) as Socio, 
	iif(soc.CodTipoPersona =1,soc.nrodocIdentidad,soc.nroRuc) as doc_ident, right(concat('0000000',pre.numero),8) as PagareFincore,
	pre.FechaDesembolso,
	precuo.numerocuota, 
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
	fin.Descripcion as finalidad,  
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
                            left join CobranzaDocumento cdoc ON ccab.CodCobranzaDocumento =cdoc.CodCobranzaDocumento
                            left join Cuenta  CU ON CU.CodCuenta  =cdoc.CodCuentaDestino
                            left join NotaCredito  NC ON ccab.CodNotaCredito =NC.CodNotaCredito
                            left join CobranzaDocumento CDDNC ON NC.CodCobranzaDocumento =CDDNC.CodCobranzaDocumento
                            left join Cuenta  CUNC ON CDDNC.CodCuentaDestino=CUNC.CodCuenta

                            --------
  
-- WHERE        (ccab.Fecha >= '01-01-2020' and ccab.Fecha <= '31-12-2020') and cdet.flagponderosa is null
-- where year(ccab.fecha)=2021 and cdet.CodEstado <> 376 -- and fin.codigo<30 and gr.descripcion like '%PROSEVA%'  
-- 376 Anulado and cdet.flagponderosa is null

Where CONVERT(VARCHAR(10),ccab.fecha,112) BETWEEN '20220101' AND '20231031' and cdet.CodEstado <> 376   
ORDER BY socio, ccab.fecha

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
    ultimo_dia_del_mes = datetime(fecha.year, fecha.month, ultimo_dia)

    return ultimo_dia_del_mes

# Aplicar la función a la columna 'fecha_cob' de tu DataFrame
df_cobranza['mes corte'] = df_cobranza['fecha_cob'].apply(ultimo_dia_del_mes)
df_cobranza['mes corte numérica'] = df_cobranza['mes corte'].dt.strftime('%Y%m%d')

#%%
# =============================================================================
# Agrupando INT_CUOTA (ingreso financiero) que no sean RETENCIONES y que sean DXP
# =============================================================================

cobranza_sin_retenciones = df_cobranza[df_cobranza['tipoPago'] != 'RETENCIONES']
cobranza_sin_retenciones = cobranza_sin_retenciones[cobranza_sin_retenciones['codigo'].isin([ 34,  35,  36,  37,  38,  39,
                                                                                             '34','35','36','37','38','39'])]

cobranza_de_retenciones = df_cobranza[df_cobranza['tipoPago'] == 'RETENCIONES']
cobranza_de_retenciones = cobranza_de_retenciones[cobranza_de_retenciones['doc_ident'].isin(socios_con_ampl)]
cobranza_de_retenciones = cobranza_de_retenciones[cobranza_de_retenciones['codigo'].isin([ 34,  35,  36,  37,  38,  39,
                                                                                          '34','35','36','37','38','39'])]

# =============================================================================
# Agrupando el INT_CUOTA por nro fincore
# =============================================================================
int_cuota_sin_retenciones = cobranza_sin_retenciones.pivot_table(values  = 'INT_CUOTA',
                                                                 index   = 'mes corte', #'PagareFincore',
                                                                 # columns = 'mes corte',
                                                                 aggfunc = 'sum')

int_cuota_con_retenciones = cobranza_de_retenciones.pivot_table(values  = 'INT_CUOTA',
                                                                index   = 'mes corte', #'PagareFincore',
                                                                # columns = 'mes corte',
                                                                aggfunc = 'sum')

#%% cuota en la que hicieron la retención
df = cobranza_de_retenciones.sort_values(by = 'numerocuota')

sum_int_reten = df.pivot_table(values  = 'INT_CUOTA',
                               index   = 'PagareFincore',
                               aggfunc = 'sum')
sum_int_reten = sum_int_reten.reset_index()
sum_int_reten = sum_int_reten.rename(columns = {"INT_CUOTA" : "INT_CUOTA AGREGADO"})
df = df.merge(sum_int_reten,
              left_on  = 'PagareFincore',
              right_on = 'PagareFincore',
              how      = 'left')
cuota_de_retención = df.drop_duplicates(subset = 'PagareFincore', 
                                        keep   = 'first')
# cuota_de_retención = cobranza_de_retenciones.pivot_table(values  = 'numerocuota',
#                                                          index   = 'PagareFincore',
#                                                          aggfunc = 'min')

prom_cuota_retencion = cuota_de_retención.pivot_table(values  = 'numerocuota',
                                                      index   = 'mes corte',
                                                      aggfunc = 'mean')
# ======================================
import seaborn as sns
import matplotlib.pyplot as plt

sns.set(style="whitegrid")  # Estilo de fondo del gráfico
plt.figure(figsize=(10, 6))  # Tamaño del gráfico

# Crear el gráfico de líneas
sns.lineplot(data = prom_cuota_retencion, 
             x    = prom_cuota_retencion.index, 
             y    = 'numerocuota', 
             marker = 'o', 
             color  = 'b')

# Configuraciones adicionales
plt.title('Promedio de cuota de retención')  # Título del gráfico
plt.xlabel('Fechas')  # Etiqueta del eje x
plt.ylabel('cuota promedio')  # Etiqueta del eje y
plt.xticks(rotation=45)  # Rotar etiquetas del eje x para mejor visualización

# Mostrar el gráfico
plt.tight_layout()
plt.show()
# ======================================

#% por si acaso, lo vamos a calcular con las fechas, a ver qué diferencia hay
# from datetime import datetime
cobranza_de_retenciones_2 = cobranza_de_retenciones.drop_duplicates(subset  = 'PagareFincore')

cobranza_de_retenciones_2['fecha_cob'] = cobranza_de_retenciones_2['fecha_cob'].astype(str)
cobranza_de_retenciones_2['FechaDesembolso'] = cobranza_de_retenciones_2['FechaDesembolso'].astype(str)

def diff_month(df):
    d1 = datetime.strptime(df['fecha_cob'], '%Y-%m-%d')
    d2 = datetime.strptime(df['FechaDesembolso'], '%Y-%m-%d %H:%M:%S')
    return (d1.year - d2.year) * 12 + d1.month - d2.month

cobranza_de_retenciones_2['diferencia meses'] = cobranza_de_retenciones_2.apply(diff_month, 
                                                                                axis = 1)
cuota_de_retención = cuota_de_retención.reset_index()
comparacion = cuota_de_retención.merge(cobranza_de_retenciones_2[['PagareFincore', 'diferencia meses']], 
                                        left_on  = 'PagareFincore', 
                                        right_on = 'PagareFincore',
                                        how      = 'left')

print(cuota_de_retención['numerocuota'].mean())
print(comparacion['diferencia meses'].mean())

# =============================================================================
# 8.2086599477417 antes de filtrar dxp
# 7.4204553938037
# 
# 8.2515048618613 después de filtrar dxp
# 7.4445130421361
# =============================================================================

#%%
import seaborn as sns
import matplotlib.pyplot as plt
# import numpy as np

# Crear datos de ejemplo para tres distribuciones en diferentes momentos
datos_t0 = cuota_de_retención['numerocuota']  # Datos en el tiempo 0
datos_t1 = comparacion['diferencia meses']  # Datos en el tiempo 1

# Combinar los datos en un DataFrame de Pandas (opcional)
import pandas as pd
df = pd.DataFrame({'nro cuota': datos_t0, 
                   'dif meses': datos_t1})

# Utilizar Seaborn para crear el gráfico de histogramas superpuestos
sns.histplot(df,
             kde         = True,
             element     = 'step',
             common_norm = False)

# Configurar etiquetas y leyenda
plt.xlabel('Valores')
plt.ylabel('nro de socios')
plt.title('Distribuciones')
# plt.legend(title='Tiempo')

# Mostrar el gráfico
plt.show()

#%%
import matplotlib.pyplot as plt
# import numpy as np

# Supongamos que tienes una lista de datos para diferentes momentos
datos_t0 = comparacion['numerocuota']  # Datos en el tiempo 0
datos_t1 = comparacion['diferencia meses']  # Datos en el tiempo 1

# Crear un histograma para cada conjunto de datos y superponerlos
plt.hist(datos_t0, bins = 120, alpha = 0.60, label = 'nro cuota')
plt.hist(datos_t1, bins = 120, alpha = 0.45, label = 'dif meses')

# Configurar etiquetas y leyenda
plt.xlabel('Valores')
plt.ylabel('nro de socios')
plt.legend(loc='upper right')

# Mostrar el gráfico
plt.title('Distribuciones')
plt.show()

#%%
# =============================================================================
# INGRESO FINANCIERO PACTADO
# =============================================================================

df_fincore['INTERÉS PACTADO'] = (df_fincore['NroPlazos'] * df_fincore['CuotaFija']) - df_fincore['Otorgado']

df_fincore['INTERÉS PACTADO'] = df_fincore['INTERÉS PACTADO'].round(2)

# ingreso financiero pactado, agrupado por fecha de desembolso:
df_fincore['mes desembolso'] = df_fincore['fechadesembolso'].apply(ultimo_dia_del_mes)

i_fin_pactado_pivot = df_fincore.pivot_table(values = 'INTERÉS PACTADO',
                                             index  = 'mes desembolso')

# =============================================================================
# Lo cobrado real
# =============================================================================

cobrado_real = int_cuota_sin_retenciones.copy()

