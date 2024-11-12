# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 10:07:35 2024

@author: sanmiguel38
"""
# =============================================================================
# creador del csv de COSECHA
# =============================================================================

import pandas as pd
import os
import pyodbc

#%%
corte = 'Octubre 2024'
# Define el directorio
directorio = 'C:\\Users\\sanmiguel38\\Desktop\\CSV COSECHA\\2024\\OCTUBRE'

#%%
# Crea el directorio si no existe, incluyendo subdirectorios
os.makedirs(directorio, exist_ok=True)

# Cambia al directorio especificado
os.chdir(directorio)

#%%
conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')

query = '''
----- QUERY PARA NUEVO REPORTE AUTOMATIZADO DE COSECHA ---------
----- ES EL MISMO CÓDIGO QUE EL NUEVO DE GRÁFICOS DE COSECHA ---
--172.16.1.162

select                 --  top 1000
Refinanciado,
CASE
	WHEN Refinanciado = 'REFINANCIADO' THEN 'REFINANCIADO' ELSE 'NO REFINANCIADO' END AS 'REFINANCIADOS FILTRO',

CASE 
	WHEN Refinanciado = 'REFINANCIADO' THEN Saldodecolocacionescreditosdirectos24 ELSE 0 END AS 'SALDO REFINANCIADOS'
,
 Reprogramados52,
CASE
	WHEN Reprogramados52 > 0 THEN 'REPROGRAMADO'  ELSE 'NO REPROGRAMADO' END AS REPROGRAMADOS

,a.FechaCorte1 as  Mes_Corte_Grafico, 
a.FechaCorte1 as Mes_Corte, 

------------------------------------------------------------------------------------------------------

CASE
	WHEN DATEDIFF(MONTH, EOMONTH(a.FechadeDesembolso21), A.FECHACORTE1 ) = 3 THEN '3 MESES'
	WHEN DATEDIFF(MONTH, EOMONTH(a.FechadeDesembolso21), A.FECHACORTE1 ) = 6 THEN '6 MESES'
	WHEN DATEDIFF(MONTH, EOMONTH(a.FechadeDesembolso21), A.FECHACORTE1 ) = 9 THEN '9 MESES'
	WHEN DATEDIFF(MONTH, EOMONTH(a.FechadeDesembolso21), A.FECHACORTE1 ) = 12 THEN '12 MESES'
	ELSE 'OTROS'
		END AS 'DIFERENCIA DE MESES',
	
------------------------------------------------------------------------------------------------------

a.FechadeDesembolso21 as  Mes_Desembolso,
concat(DATENAME(MONTH, a.FechadeDesembolso21),'/', year(a.FechadeDesembolso21)) AS Mes_desembolso_txt,
concat(DATENAME(MONTH, a.FechaCorte1),'/', year(a.FechaCorte1)) AS Mes_corte_txt
,a.NumerodeDocumento10, 
a.TipodeDocumento9, 
a.CodigoSocio7, 
a.ApellidosyNombresRazonSocial2, 
ALINEAMIENTO.[ALINEAMIENTO EXTERNO],
ALINEAMIENTO.[MAX CALIFICACION] AS 'MÁXIMA CALIFICACIÓN ENTRE AL. EXTERNO E INTERNO',
a.NumerodeCredito18,
a.nro_fincore,
A.MDesembolsadoxM,
a.Monedadelcredito17,
a.MontodeDesembolso22, 
a.Saldodecolocacionescreditosdirectos24, 
a.CapitalVencido29, 
a.nuevo_capitalvencido, 
a.CapitalenCobranzaJudicial30,
a.CarteraAtrasada, 
--a.NUEVO_PROMOTOR AS ORIGINADOR_antiguo,
--a.originador AS 'Originador_actualizado',
--A.PROMOTOR,
--A.NUEVO_PROMOTOR, 
a.administrador, 
a.TipodeProducto43, 
a.FechadeNacimiento3, 
a.SaldodeGarantiasAutoliquidables35,
a.SaldosdeCreditosCastigados38,
a.mcastigadoxm,
A.MtotalCastigadoxM,
iif(a.SaldosdeCreditosCastigados38>0,'CASTIGADO','VIGENTE')as 'ESTADO',
--b.NUEVA_PLANILLA_creada AS Planilla2, 
a.PLANILLA_CONSOLIDADA AS Planilla2, 
a.NUEVA_PLANILLA,

CASE WHEN ADMINISTRADOR LIKE '%PROSEVA%' OR  ADMINISTRADOR LIKE '%CAÑETE%' THEN 'PROVINCIA'
	ELSE 'LIMA' END AS 'FILTRO_PROVINCIA',

CASE 
	WHEN a.ADMINISTRADOR LIKE '%SEVA PIURA%' THEN 'PIURA' 
	WHEN a.ADMINISTRADOR LIKE '%CHINCHA%' THEN 'CHINCHA'
	WHEN a.ADMINISTRADOR LIKE '%TACNA%' THEN 'TACNA'
	WHEN a.ADMINISTRADOR LIKE '%CHICLAYO%' THEN 'CHICLAYO'
	WHEN a.ADMINISTRADOR LIKE '%AREQUIPA%' THEN 'AREQUIPA'
	WHEN (a.ADMINISTRADOR LIKE '%SEVA ICA%' and a.ADMINISTRADOR not like '%ricardo%') THEN 'ICA'
	WHEN a.ADMINISTRADOR LIKE '%HUACHO%' THEN 'HUACHO'
	WHEN a.ADMINISTRADOR LIKE '%JAEN%' THEN 'JAEN'
	WHEN a.ADMINISTRADOR LIKE '%TRUJILLO%' THEN 'TRUJILLO'
	WHEN a.ADMINISTRADOR LIKE '%TUMBES%' THEN 'TUMBES'
	WHEN a.ADMINISTRADOR LIKE '%CAÑETE%' THEN 'CAÑETE'
	WHEN a.ADMINISTRADOR LIKE '%CAJAMARCA%' THEN 'CAJAMARCA'
	when a.ADMINISTRADOR like '%TARAPOTO%' THEN 'TARAPOTO'
	when (a.ADMINISTRADOR like '%CUSCO%' OR a.ADMINISTRADOR like '%CUZCO%') THEN 'CUSCO'

ELSE 'LIMA' END as 'ZONAS(prosevas)',

--CASE 
--	WHEN a.TipodeProducto43 in (21,22,23,24,25,26,27,28,29) THEN 'MICRO EMPRESA'
--	WHEN a.TipodeProducto43 in (30,33, 31, 32)              THEN 'LIBRE DISPONIBILIDAD'
--	WHEN a.TipodeProducto43 IN (16,15,17,18,19)             THEN 'PEQUEÑA EMPRESA' -- AND a.FechaCorte1>='20210930'
--	WHEN a.TipodeProducto43 IN (41,45)						THEN 'HIPOTECARIO'
--	WHEN a.TipodeProducto43 IN (34,35,36,37,38,39)			THEN 'DXP'
--	WHEN a.TipodeProducto43 IN (95,96,97,98,99)				THEN 'MEDIANA EMPRESA'
--		ELSE 'OTROS' end Producto,
MASTER.DBO.tipo_producto(a.TipodeProducto43) AS 'Producto',

case 
	when ADMINISTRADOR like '%ALICIA OVIEDO%' or ADMINISTRADOR like '%ANDREA BILBAO%' 
	or ADMINISTRADOR like '%GIOVANNA HERRERA%'  or  ADMINISTRADOR like '%MARGIORY ELIAS%' 
	or ADMINISTRADOR like '%grecia%'
	then 'ILLIANOVICH PAREJA'

	WHEN ADMINISTRADOR like '%AZUCENA%' or ADMINISTRADOR like '%CHUQUIZUTA%' 
	or ADMINISTRADOR like '%CHUQUISUTA%'or ADMINISTRADOR like '%LUDHIANA CASTAÑEDA%' 
	or ADMINISTRADOR like '%maldonado%' or ADMINISTRADOR like '%roxana%' or ADMINISTRADOR like '%laureano%' 
	then 'KARL AZAHUANCHE'

	WHEN ADMINISTRADOR like '%JULY GARCIA%' or  ADMINISTRADOR LIKE '%JULY OLGA%' 
	or ADMINISTRADOR like '%gustavo%' 
	or ADMINISTRADOR like '%DAVID BORJA%' OR ADMINISTRADOR LIKE '%ROSARIO BORJA%'
	or ADMINISTRADOR like '%LUZ CABALLERO%' OR ADMINISTRADOR LIKE '%KATHERIN RAMOS%' 
	then 'MIGUEL CUYUBAMBA'

	WHEN a.ADMINISTRADOR like '%PROSEVA%' OR  a.ADMINISTRADOR like '%OFICINA%' 
	then 'EDUARDO SALAS'

	WHEN ADMINISTRADOR like '%CRISTIAN ZAMORA%' or  ADMINISTRADOR LIKE '%LUIS JUSTO%' ----OJO A ESTE ÚLTIMO 
	or ADMINISTRADOR like '%GREYCY BENITES%' 
	or ADMINISTRADOR like '%JAQUELINE LIÑAN%' OR ADMINISTRADOR LIKE '%JERSON ALVA%'
	----antiguos de ahora en adelante
	or administrador like '%MARGARITA CHINGA%'
	or administrador like '%LUIS CASTAÑEDA%'
	or administrador like '%EVELYN LOJA%'
	or administrador like '%HAXELL TINOCO%'

	then 'ANABEL PEREZ'

	WHEN ADMINISTRADOR like '%JHONNY SALDAÑA%'
	or ADMINISTRADOR like '%JHONY SALDAÑA%'
	or ADMINISTRADOR LIKE '%DAYANA CHIR%'
	or ADMINISTRADOR like '%MARIBEL PUCHO%' 
	or ADMINISTRADOR like '%ESTHER RAMIREZ%' 
	OR ADMINISTRADOR LIKE '%LUIS BUSTAMANTE%'
	OR ADMINISTRADOR LIKE '%FIGARI VEGA%'
	OR ADMINISTRADOR LIKE '%ELBER ALVARADO%'
	OR ADMINISTRADOR LIKE '%KELLY HUAMANI%'
	OR ADMINISTRADOR LIKE '%ANTHONNY OSORIO%'
	OR ADMINISTRADOR LIKE '%ANTONNY OSORIO%'
	OR ADMINISTRADOR LIKE '%ANTHONY OSORIO%'
	OR ADMINISTRADOR LIKE '%ANTONY OSORIO%'
	OR ADMINISTRADOR LIKE '%MARTIN VILCA%'
	OR ADMINISTRADOR LIKE '%GINO PALOMINO%'
	OR ADMINISTRADOR LIKE '%YULAISE MOREANO%'
	OR ADMINISTRADOR LIKE '%NADINE SELMIRA%'
	OR ADMINISTRADOR LIKE '%JESSICA PISCOYA%'
	OR ADMINISTRADOR LIKE '%JOSE SANCHEZ%'
	OR ADMINISTRADOR LIKE '%ROY NARVAEZ%'
	OR ADMINISTRADOR LIKE '%PAULO SARE%'
	--------antiguos de ahora en adelante
	or administrador like '%YESENIA POTENCIANO%'
	or administrador like '%WILLIAMS TRAUCO%'
	or administrador like '%MILTON JUAREZ%'
	or administrador like '%JIMN MENDOZA%'
	or administrador like '%JONATHAN ESTRADA%'
	or administrador like '%CESAR MEDINA%'
	or administrador like '%VICTOR FARFAN%'
	or administrador like '%JESSICA SOLORZANO%'
	or administrador like '%JEAN BRAVO%'
	then 'JHONNY SALDAÑA'

ELSE 'OTROS'END 'SUPERVISORES',

a.Departamento,
a.Provincia,
a.Distrito,
D.FDN_DRIVE,
CASE 
	WHEN D.FDN_DRIVE IS NULL THEN A.originador ELSE D.FDN_DRIVE END AS 'ORIGINADOR',

CASE
	WHEN a.desembolso_para_filtros <=   1000 THEN 'A.[<1000]'
	WHEN a.desembolso_para_filtros between 1001 and 2000 THEN 'B.[<=2000]'
	WHEN a.desembolso_para_filtros between 2001 and 3000 THEN 'C.[<=3000]'
	WHEN a.desembolso_para_filtros between 3001 and 4000 THEN 'D.[<=4000]'
	WHEN a.desembolso_para_filtros between 4001 and 5000 THEN 'E.[<=5000]'
	WHEN a.desembolso_para_filtros between 5001 and 6000 THEN 'F.[<=6000]'
	WHEN a.desembolso_para_filtros between 6001 and 7000 THEN 'G.[<=7000]'
	WHEN a.desembolso_para_filtros between 7001 and 8000 THEN 'H.[<=8000]'
	WHEN a.desembolso_para_filtros between 8001 and 9000 THEN 'I.[<=9000]'
	WHEN a.desembolso_para_filtros between 9001 and 10000 THEN 'J.[<=10000]'
	WHEN a.desembolso_para_filtros between 10001 and  11000 THEN 'K.[<=11000]'
	WHEN a.desembolso_para_filtros between 11001 and  12000 THEN 'L.[<=12000]'
	WHEN a.desembolso_para_filtros between 12001 and  13000 THEN 'M.[<=13000]'
	WHEN a.desembolso_para_filtros between 13001 and  14000 THEN 'N.[<=14000]'
	WHEN a.desembolso_para_filtros between 14001 and  15000 THEN 'Ñ.[<=15000]'
	WHEN a.desembolso_para_filtros between 15001 and  16000 THEN 'O.[<=16000]'
	WHEN a.desembolso_para_filtros between 16001 and  17000 THEN 'P.[<=17000]'
	WHEN a.desembolso_para_filtros between 17001 and  18000 THEN 'Q.[<=18000]'
	WHEN a.desembolso_para_filtros between 18001 and  19000 THEN 'R.[<=19000]'
	WHEN a.desembolso_para_filtros between 19001 and  20000 THEN 'S.[<=20000]'
	ELSE 'T.[>20000]'
	END AS 'SEGMENTACIÓN MONTO DESEMBOLSADO',

a.[Dpto Negocio],
a.[Provincia Negocio],
a.[Distrito Negocio],

	--CASE
		
	--WHEN A.Nro_Fincore = '00102322' THEN 'AREQUIPA'
		
	--	WHEN 
	--	(SEDE.SEDE IS NULL)
	--	THEN 'NO ES MYPE'
	--	WHEN (SEDE.SEDE IS NOT NULL) AND
	--	A.TipodeProducto43 IN (15,16,17,18,19,
	--						   20,21,22,23,24,25,26,27,28,29)
	--	THEN SEDE.SEDE

	--	ELSE 'NO ES MYPE'
	--	END AS 'SEDE MYPE',

		MASTER.DBO.[ZONA_MYPE](A.originador, A.TipodeProducto43) AS 'ZONA MYPE(originador)',
		MASTER.DBO.[ZONA_MYPE](A.ADMINISTRADOR, A.TipodeProducto43) AS 'ZONA MYPE(administrador)',

		apro.[USUARIO APROBADOR]


from cosecha..cosecha_NUEVO AS A

	--left join Anexos_Riesgos..planilla2 b
	--on(a.NUEVA_PLANILLA=b.NUEVA_PLANILLA)

LEFT JOIN anexos_riesgos3.[ALINEAMIENTO EXTERNO].[AL_EXTERNO] AS ALINEAMIENTO
ON (A.Nro_Fincore = ALINEAMIENTO.[Nro Prestamo _Fincore] 
AND A.FechaCorte1 = ALINEAMIENTO.FECHA_CORTE)
	
	LEFT JOIN anexos_riesgos2..ORIGINADOR_ENERO_2023 AS D
	ON (A.Nro_Fincore = D.NRO_FINCORE)

	--LEFT JOIN anexos_riesgos3.[mype].[colaboradores_20240229] AS SEDE
	--ON (
 --   CASE 
 --       WHEN D.FDN_DRIVE IS NULL THEN A.originador
 --       ELSE D.FDN_DRIVE
 --   END) = SEDE.[LISTA DE TRABAJADORES]

------------------------
	LEFT JOIN [anexos_riesgos3]..[APROBADOR] AS APRO
	ON A.Nro_Fincore  = APRO.pagare_fincore



'''
base = pd.read_sql_query(query, conn)

del conn

#%%
# crear csv
base.to_csv('Cosecha corte ' + corte + '.csv', 
            index    = False,
            encoding = 'utf-8-sig')

