# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 17:26:00 2024

@author: sanmiguel38
"""

import pandas as pd
from   datetime import datetime #, timedelta
from   datetime import date
import pyodbc
import os

import warnings
warnings.filterwarnings('ignore')

#%% usuario SQL fincore
datos = pd.read_excel('C:\\Users\\sanmiguel38\\Desktop\\Joseph\\USUARIO SQL FINCORE.xlsx')

#%%

server      = datos['DATOS'][0]
username    = datos['DATOS'][2]
password    = datos['DATOS'][3]

conn_str = f'DRIVER=SQL Server;SERVER={server};UID={username};PWD={password};'

conn = pyodbc.connect(conn_str)

query = f'''
SELECT
    RIGHT(CONCAT('0000000', pre.numero), 8) AS id,
    precuo.numerocuota,
    MAX(ccab.fecha) AS cobra_reciente
FROM
    prestamoCuota AS precuo
    INNER JOIN Prestamo AS pre ON pre.codPrestamo = precuo.CodPrestamo 
    INNER JOIN CobranzaDet AS cdet ON precuo.CodprestamoCuota = cdet.CodprestamoCuota
    INNER JOIN CobranzaCab AS ccab ON ccab.CodCobranzaCab = cdet.CodCobranzaCab
WHERE
    precuo.CodEstado = 22
    AND ccab.fecha <= '20240930'
    AND ccab.fecha = (
        -- Subquery para obtener la fecha más reciente por nro_credito
        SELECT MAX(ccab2.fecha)
        FROM CobranzaCab ccab2
        INNER JOIN CobranzaDet cdet2 ON ccab2.CodCobranzaCab = cdet2.CodCobranzaCab
        WHERE cdet2.CodprestamoCuota = precuo.CodprestamoCuota
    )
	and ccab.fecha >= precuo.FechaVencimiento

GROUP BY
    RIGHT(CONCAT('0000000', pre.numero), 8),
    precuo.numerocuota
	
order by RIGHT(CONCAT('0000000', pre.numero), 8);
'''

df_pagos_completos_recientes = pd.read_sql_query(query, conn)

df_pagos_completos_recientes['cobra_reciente']
df = df_pagos_completos_recientes.sort_values(by=['id', 
                                                  'cobra_reciente'], ascending=[True, False])

# Eliminar duplicados, quedándose con la primera ocurrencia (que será la de la fecha más reciente)
df_unique = df.drop_duplicates(subset='id', keep='first')
df_unique['idd'] = df_unique['id'] + '         ' + df_unique['numerocuota'].astype(str)


#%%
query = f'''

SELECT -- soc.codsocio, 
precuo.CodEstado as 'estado cancelado = 22',
Concat(right(concat('0000000',pre.numero),8) , ' ' ,  str(precuo.numerocuota)) as 'id',
soc.codigosocio, iif(soc.CodTipoPersona =1,concat(soc.apellidopaterno,' ',soc.apellidomaterno,' ',soc.nombres),soc.razonsocial) as Socio, 
iif(soc.CodTipoPersona =1,soc.nrodocIdentidad,soc.nroRuc) as doc_ident, right(concat('0000000',pre.numero),8) as PagareFincore, pre.FechaDesembolso, precuo.FechaVencimiento,
precuo.numerocuota,
pre.CuotaFija, iif(cdet.CodMoneda='95','DÓLAR','SOLES') AS moneda, 

ccab.fecha as fecha_cob,
 
cdet.Capital, cdet.aporte as Aporte,
cdet.interes AS INT_CUOTA, cdet.InteresCompensatorio as IntCompVencido, cdet.Mora AS INTCOMP_MORA, cdet.GastoCobranza, cdet.FondoContigencia+cdet.MoraAnterior+cdet.GastoTeleOperador+cdet.GastoJudicial+cdet.GastoLegal+cdet.GastoOtros AS GTO_OTROS,
cdoc.numeroOperacion, --tmdet.descripcion as TipoDocmto, 
gr.descripcion as Funcionario, pla.descripcion as planilla, tc.Descripcion as TipoCredito, fin.codigo, fin.Descripcion as finalidad,  
pre.FechaVentaCartera, pre.FechaCastigo, 
cdoc.codestado, cDOC.NumeroOperacionDestino, CCAB.CODMEDIOPAGO, tmdet.descripcion as tipoPago, Nc.Correlativo as Nro_NCred, Nc.FechaOperacion as FecOpe_NCred, CDDNC.NumeroOperacionDestino as DocOperacion  --, CDOC.CODCOBRANZADOCUMENTO
, tmdet5.Descripcion as SituacCred, pre.FechaAsignacionAbogado, empl.NombreCompleto as Abogado, 

--IIF(CDDNC.NumeroOperacionDestino IS NULL,cdoc.NumeroOperacionDestino,CDDNC.NumeroOperacionDestino) AS NumeroOperacionDestino,
IIF(CDDNC.NumeroOperacionDestino IS NULL,CU.NumeroCuenta,CUNC.NumeroCuenta) AS NumeroCuenta,
--IIF(CDDNC.NumeroOperacionDestino IS NULL,NULL,CONCAT('NC-',RIGHT(CONCAT('000000',NC.Correlativo),6))) AS NroNotaCredito,
iif(cdet.FlagPonderosa=1,'POND','SM') as origen
, ccab.FechaRegistro, ccab.CodUsuarioCreacion, ccab.CodCobranzaCab, ccab.CodCobranzaDocumento

FROM   CobranzaDet AS cdet INNER JOIN prestamoCuota AS precuo ON precuo.CodprestamoCuota = cdet.CodprestamoCuota
                           INNER JOIN CobranzaCab as ccab ON ccab.CodCobranzaCab = cdet.CodCobranzaCab
                           Inner Join Prestamo as pre ON pre.codPrestamo = precuo.CodPrestamo 
                           Left Join Planilla AS pla ON pre.CodPlanilla = pla.CodPlanilla
                           Inner Join Socio as soc ON soc.CodSocio = pre.CodSocio
                           inner join finalidad as fin on pre.CodFinalidad = fin.CodFinalidad
                           inner join TipoCredito as tc on pre.CodTipoCredito = tc.CodTipoCredito
                           left join grupoCab as gr on gr.codGrupoCab = pre.codGrupoCab
                        --**   LEFT JOIN CobranzaDocumento as cdoc on ccab.CodCobranzaDocumento = cdoc.CodCobranzaDocumento
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
-- where year(ccab.fecha)=2021 and cdet.CodEstado <> 376 -- and fin.codigo<30 and gr.descripcion like '%PROSEVA%'  -- 376 Anulado and cdet.flagponderosa is null

Where 1=1
and precuo.CodEstado = 22

/*fecha cobranza*/
and  CONVERT(VARCHAR(10),ccab.fecha,112) BETWEEN '20220101' AND '20240930' 

and cdet.CodEstado <> 376 -- and soc.CodigoSocio = 11184 -- and fin.codigo in (34,35,36,37,38,39) -- and ccab.CodMedioPago = 719 -- and cdet.capital>0 and pre.FechaCastigo is not null -- and (pre.numero in (101330, 111048, 111755, 105737, 106769)) 

--and ccab.fecha <= precuo.FechaVencimiento

/*fecha vencimiento*/
and precuo.FechaVencimiento BETWEEN '20240101' AND '20240930'
--and ccab.fecha >= precuo.FechaVencimiento

--and right(concat('0000000',pre.numero),8) = '00118443'
ORDER BY socio, ccab.fecha, NumeroCuota

'''

cobranza_por_filtrar = pd.read_sql_query(query, conn)

filtrado =cobranza_por_filtrar[cobranza_por_filtrar['id'].isin(df_unique['idd'])]

owo = filtrado.columns
owo = list(set(owo))
filtrado = filtrado[owo]

#%%
CARGA_SQL_SERVER = True
if CARGA_SQL_SERVER == True:
    # Esta es la tabla que estará en SQL SERVER
    tabla =  '[experimentos2].[dbo].[cobranza]'
    
    # Establecer la conexión con SQL Server
    cnxn = pyodbc.connect('DRIVER=SQL Server;SERVER=SM-DATOS;UID=SA;PWD=123;')
    cursor = cnxn.cursor()
    
    df = filtrado.copy()
    df = df.fillna(0)
    
    # AQUÍ SE DEBE APLICAR UN PROCESO DE LIMPIEZA DE LA TABLA PORQUE NO ACEPTA CELDAS CON VALORES NULOS
    # EJEMPLO df = df.fillna(0)
    
    # Limpiar/eliminar la tabla antes de insertar nuevos datos
    cursor.execute(f"IF OBJECT_ID('{tabla}') IS NOT NULL DROP TABLE {tabla}")    

    # Generar la sentencia CREATE TABLE dinámicamente
    create_table_query = f"CREATE TABLE {tabla} ("
    for column_name, dtype in df.dtypes.items():
        sql_type = ''
        if dtype == 'int64':
            sql_type = 'INT'
        elif dtype == 'int32':
            sql_type = 'INT'
        elif dtype == 'float64':
            sql_type = 'FLOAT'
        elif dtype == 'object':
            sql_type = 'NVARCHAR(MAX)'  # Ajusta el tamaño según tus necesidades
        elif dtype == '<M8[ns]':
            sql_type = 'DATETIME'  # Ajusta el tamaño según tus necesidades

        create_table_query += f"[{column_name}] {sql_type}, "
        
    create_table_query = create_table_query.rstrip(', ') + ")"  # Elimina la última coma y espacio

    # Ejecutar la sentencia CREATE TABLE
    cursor.execute(create_table_query)
    
    # CREACIÓN DE LA QUERY DE INSERT INTO
    # Crear la lista de nombres de columnas con corchetes
    column_names = [f"[{col}]" for col in df.columns]
    # Crear la lista de placeholders para los valores
    value_placeholders = ', '.join(['?' for _ in df.columns])
    # Crear la consulta de inserción con los nombres de columna y placeholders de valores
    insert_query = f"INSERT INTO {tabla} ({', '.join(column_names)}) VALUES ({value_placeholders})"

    # Iterar sobre las filas del DataFrame e insertar en la base de datos
    for _, row in df.iterrows():
        cursor.execute(insert_query, tuple(row))

    # Confirmar los cambios y cerrar la conexión
    cnxn.commit()
    cursor.close()

    print(f'Se cargaron los datos a SQL SERVER {tabla}')

else:
    print('No se ha cargado a SQL SERVER')

