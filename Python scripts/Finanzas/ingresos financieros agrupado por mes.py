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
fecha_inicio = '20241001'   # recordar que tiene que ser el inicio del mes
fecha_final  = '20241231'

#columnas nuevas solicitadas

# DIRECTORIO DE TRABAJO:
directorio = 'C:\\Users\\sanmiguel38\\Desktop\\ingresos financierso\\setiembre a diciembre 2024'

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

Where CONVERT(VARCHAR(10),ccab.fecha,112) BETWEEN '{fecha_inicio}' AND '{fecha_final}' 
and cdet.CodEstado <> 376
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
    ultimo_dia_del_mes = datetime(fecha.year, 
                                  fecha.month, 
                                  ultimo_dia)
    return ultimo_dia_del_mes

# Aplicar la función a la columna 'fecha_cob' de tu DataFrame
df_cobranza['mes corte'] = df_cobranza['fecha_cob'].apply(ultimo_dia_del_mes)
df_cobranza['mes corte numérica'] = df_cobranza['mes corte'].dt.strftime('%Y%m%d')
df_cobranza['mes corte numérica'] = df_cobranza['mes corte numérica'].astype(int)

#%%

df_cobranza_sin_retenciones = df_cobranza[df_cobranza['tipoPago'] != 'RETENCIONES']

creditos_con_retenciones = df_cobranza[df_cobranza['tipoPago'] == 'RETENCIONES']

# creditos_con_retenciones = creditos_con_retenciones[creditos_con_retenciones['INT_CUOTA'] > 0]
# filtrando por fechas en específico
# creditos_con_retenciones = creditos_con_retenciones[(creditos_con_retenciones['mes corte numérica'] >= 20220101)  & \
#                                                     (creditos_con_retenciones['mes corte numérica'] <= 20220131)]

#%%
# agrupamos por meses

ing_fin_total = df_cobranza.pivot_table(values  = 'INT_CUOTA',
                                        index   = 'mes corte', #'PagareFincore',
                                        # columns = 'mes corte',
                                        aggfunc = 'sum')
ing_fin_total = ing_fin_total.reset_index()
ing_fin_total.rename(columns = {"INT_CUOTA" : "INT_CUOTA total"}, inplace = True)

ing_fin_sin_retenciones = df_cobranza_sin_retenciones.pivot_table(values  = 'INT_CUOTA',
                                                                  index   = 'PagareFincore',
                                                                  columns = 'mes corte numérica',
                                                                  aggfunc = 'sum')
ing_fin_sin_retenciones.fillna(0, inplace = True)

ing_fin_sin_retenciones = ing_fin_sin_retenciones.reset_index()
ing_fin_sin_retenciones.rename(columns = {"INT_CUOTA" : "INT_CUOTA sin retenciones"},
                               inplace = True)

#%%
# LEEMOS DEL SQL, INFO DE LOS CRÉDITOS DESEMBOLSADOS
conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'

conn = pyodbc.connect(conn_str)

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
	-------------------------------------------------------------------------
	/*
	p.NroPlazos, 
	p.CuotaFija, 
	*/
	--p.codestado,
	-------------------------------------------------------------------------
	tm.descripcion as 'Estado',
	p.fechaCancelacion, 
	iif(p.codcategoria=351,'NVO','AMPL') as 'tipo_pre', 
	p.flagrefinanciado, 
	pla.descripcion as 'Planilla',
	/* -----------------------------------------------------------------------
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
	*/
	tc.Descripcion as 'TipoCredito', 
	FI.CODIGO AS 'COD_FINALIDAD',
	FI.DESCRIPCION as 'FINALIDAD',
	/*
	s.FechaNacimiento, 
	s.fechaInscripcion, 
	u.IdUsuario as 'User_Desemb', 
	tm4.descripcion as 'EstadoSocio',
	*/
    '' AS 'NADA'
-- pcu.FechaVencimiento as Fecha1raCuota, pcu.NumeroCuota, pcu.SaldoInicial,
FROM prestamo as p

	INNER JOIN socio as s               ON s.codsocio = p.codsocio
	LEFT JOIN sociocontacto as sc       ON sc.codsocio = s.codsocio
	LEFT JOIN planilla as pla           ON p.codplanilla = pla.codplanilla
	INNER JOIN grupocab as pro          ON pro.codgrupocab = p.codgrupocab
	INNER JOIN distrito as d            ON d.coddistrito = sc.coddistrito
	INNER JOIN provincia as pv          ON pv.codprovincia = d.codprovincia
	INNER JOIN departamento as dp       ON dp.coddepartamento = pv.coddepartamento
	INNER JOIN tablaMaestraDet as tm    ON tm.codtabladet = p.CodEstado
	LEFT JOIN grupocab as gpo           ON gpo.codgrupocab = pla.codgrupocab
	LEFT JOIN tablaMaestraDet as tm2    ON tm2.codtabladet = s.codestadocivil
	LEFT JOIN tablaMaestraDet as tm3    ON tm3.codtabladet = p.CodSituacion
	--INNER JOIN tablaMaestraDet as tm3 ON tm3.codtabladet = s.codcategoria
	INNER JOIN pais                     ON pais.codpais = s.codpais
	LEFT JOIN FINALIDAD AS FI           ON FI.CODFINALIDAD = P.CODFINALIDAD
	LEFT JOIN TipoCredito as TC         ON tc.CodTipoCredito = p.CodTipoCredito
	INNER JOIN usuario as u             ON p.CodUsuario = u.CodUsuario
	INNER JOIN TablaMaestraDet as tm4   ON s.codestado = tm4.CodTablaDet
	--LEFT JOIN PrestamoCuota as pcu    ON p.CodPrestamo = pcu.CodPrestamo

WHERE    1 = 1

/*
AND pro.descripcion IN (
'BORJA HERENCIA',
'HERENCIA BORJA / G. HERRERA',
'MARGIORY ELIAS BENAVIDES',
'GIOVANNA HERRERA MATHEWS',
'JONATHAN ESTRADA ESTRADA',
'ADMINISTRADOR DXP MAGDALENA',
'ALICIA OVIEDO VELASQUEZ',
'GERENCIA GM',
'ANDREA BILBAO BRICEÑO',
'JAQUELINE CHUQUISUTA',
'YOBANA LAUREANO',
'ROSA MALDONADO FIGUREOA',
'LUDHIANA CASTAÑEDA',
'GUSTAVO PALLETE ALFERANO',
'ROXANA QUISPE CHAVEZ',
'CRISTIAN ZAMORA PERLECHE',
'PROSEVA CHICLAYO',
'MARGARITA CHINGA ESPINOZA',
'MARIA DEL ROSARIO BORJA HERENCIA',
'KELLY HUAMANI',
'LUIS CASTAÑEDA ALEJOS',
'HAXELL TINOCO ESQUEN',
'ADMINISTRADOR MYPE MAGDALENA',
'GREYCY BENITES',
'ANTHONNY OSORIO',
'CONSUELO MEDRANO',
'JERSON ALVA FARFAN',
'DAVID BORJA HERENCIA',
'JHONATAN SEGAMA SALAZAR',
'MIJAEL SERKOVICH PASCUAL',
'KATHERIN RAMOS CCAMA',
'MARTIN VILCA PRADO',
'FIGARI VEGA AYQUIPA',
'JULY GARCIA ALCANTARA',
'GRUPO SAN MIGUEL',
'EVELYN LOJA PINEDO',
'JEFERSON MALVACEDA SAMANAMUD',
'JAQUELINE LIÑAN MORE',
'ALEXANDRE SALDAÑA LOPEZ',
'PAMELA GARCIA',
'YESENIA POTENCIANO',
'GERSON SANCHEZ POSSO',
'LUIS JUSTO',
'JIMN MENDOZA CORNEJO',
'AZUCENA OCHOA TERRY',
'YULI ECHABAUTIS NAVARRO',
'YULAISE MOREANO CHACON',
'ELBER ALVARADO GARCIA',
'ZAIRA KATHERINE ASCUE MARTINEZ',
'ALEXANDER CASTAÑEDA',
'ADOLFO HUAMAN',
'JEAN KARLHO BRAVO MATIAS',
'LUZ CABALLERO CARBAJAL',
'VICTOR VARGAS AVALO',
'JOSE SANCHEZ FLORES (Cesado 27/12/23)',
'VICTOR FARFAN UGARTE',
'MILAGROS VEREAU DE LOS SANTOS',
'EDUARDO ROJAS DE LA CRUZ',
'WILLIAMS TRAUCO PAREDES',
'BEATRIZ PALOMINO',
'SUSAN ROJAS TORRES',
'EDUAR MIGUEL TITO',
'AMERICA YESENIA CAMA AURIS',
'ALEJANDRO HUAMAN FERNANDEZ',
'ROBERT ZELADA TORRES',
'GABRIELA CARBAJAL REYES',
'BORIS CAMARGO',
'DANTE FLORES BELTRAN',
'WIGBERTO FRANK SANCHEZ NUREÑA',
'OFICINA PRINCIPAL',
'MARCOS NEYRA SUAREZ',
'ESTEBAN EDUARDO YNGUNZA MUJICA',
'EDDIN SEMINARIO SANCHEZ',
'MIGUEL TELLO CESPEDES',
'JOISE DALY DIAZ LIBERATO',
'HUGO MARCHAND OSTOLAZA',
'ELI YOSIP VARAS RONCAL',
'CRISTINA CHAVEZ',
'WILLIAM FRANK FLORES SUAZO',
'ROXANA BENITES MENESES',
'LESLIER MARTINEZ DE LA CRUZ',
'JOSE YARLEQUE ESCATE'
    
)
*/

--AND   CONVERT(VARCHAR(10),p.fechadesembolso,112) >= '20231101' ---------------des/activar esto para multioficios
--AND s.codigosocio>0  and p.codestado = 342
--AND FI.CODIGO IN (26,32) --ESTE ES EL PROD 43 EN LA EMPRESA  -----------------des/activar esto para multioficios


--and (p.CODTIPOCREDITO=2 or p.CODTIPOCREDITO=9) and pcu.NumeroCuota=1 and tm2.descripcion is null -- 341 PENDIENTES  /  p.codestado <> 563  anulados
--where year(p.fechadesembolso) >= 2021 and month(p.fechadesembolso) >= 1 and s.codigosocio>0 and p.codestado <> 563 AND tc.CODTIPOCREDITO <>3 -- and pro.Descripcion like '%WILLIAMS TRAUCO%' --  and p.codcategoria=351
ORDER BY socio ASC, p.fechadesembolso DESC

'''

df_creditos = pd.read_sql_query(query, conn)
del conn

datos_creditos = df_creditos[['Socio',            
                              'Doc_Identidad',    
                              'pagare_fincore',   
                              'moneda',           
                              'Otorgado',         
                              'fechadesembolso',  
                              'Estado',           
                              'fechaCancelacion', 
                              'Planilla',         
                              'COD_FINALIDAD',    
                              'TipoCredito',      
                              'FINALIDAD']]

datos_creditos = datos_creditos.drop_duplicates(subset  = 'pagare_fincore')

#%% merge de datos
dat = ing_fin_sin_retenciones.merge(datos_creditos,
                                    left_on  = 'PagareFincore', 
                                    right_on = 'pagare_fincore',
                                    how      = 'left')

#%%
# CREACIÓN DE DATAFRAMES PARA CADA MES

columnas_numericas = dat.select_dtypes(include = 'number').columns
os.chdir(directorio)
# Crear un diccionario para almacenar los DataFrames
dataframes_dict = {}

# Iterar sobre las columnas numéricas
for columna in columnas_numericas:
    # Filtrar valores mayores que cero en la columna numérica actual
    df_filtrado = dat[['PagareFincore', 
                       columna,
                       'Socio',
                       'Planilla',
                       'COD_FINALIDAD',
                       'FINALIDAD',
                       'TipoCredito'
                       ]][dat[columna] > 0]

    # Si el DataFrame filtrado tiene filas, lo almacenamos en el diccionario con el nombre correspondiente
    if not df_filtrado.empty:
        # Obtener el nombre del DataFrame
        nombre_df = f"df_{columna}"  # Puedes modificar esto para el nombre deseado

        # Almacenar el DataFrame en el diccionario
        dataframes_dict[nombre_df] = df_filtrado

        # Exportar el DataFrame a un archivo Excel con el mismo nombre
        df_filtrado.to_excel(f"{nombre_df}.xlsx", 
                             index = False)

