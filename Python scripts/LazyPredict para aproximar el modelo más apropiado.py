# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 12:56:55 2023

@author: Joseph Montoya
"""

###############################################################################
#    LAZYPREDICT para saber qué modelos podrían ser los más convenientes      #
###############################################################################

#!pip install lazypredict

from lazypredict.Supervised import LazyClassifier
from sklearn.model_selection import train_test_split

import pandas as pd
import pyodbc
import numpy as np

#%%

conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')

base = pd.read_sql_query('''
SELECT
FechaCorte1,
(YEAR(FechadeDesembolso21)-YEAR(FechadeNacimiento3)) AS 'EDAD',
CASE
	WHEN Situacion_Credito LIKE 'VIGENTE' THEN 1
	ELSE 0
	END AS 'MOROSO?',
CASE
	WHEN Departamento LIKE 'lima' then 1
	else 0
	end as 'LIMEÑO?',
CASE 
	WHEN Genero4 LIKE 'F' THEN 0
	ELSE 1
	END AS 'SEXOOO',
CASE	
	WHEN EstadoCivil5 LIKE 'S' THEN 0
	ELSE 1
	END AS 'ESTADO CIVIL',
TipodeDocumento9,
CASE	
	WHEN TipodeDocumento9 LIKE 1 THEN 1
	ELSE 0
	END AS 'DOCUMENTO 1?',
TIPODEPERSONA11,
CASE 
	WHEN TipodePersona11 LIKE '1' THEN 1
	ELSE 0
	END AS 'PERSONA 1?',
TipodeCredito19,
MontodeDesembolso22,
TasadeInteresAnual23,
TipodeProducto43,
CASE
	WHEN TipodeProducto43 IN (34,35,36,37,38,39) THEN 1
	ELSE 0
	END AS 'PRODUCTO DXP?',
CASE
	WHEN TipodeProducto43 IN (15,16,17,18,19) THEN 1
	ELSE 0
	END AS 'PRODUCTO PEQUEÑA?',
CASE
	WHEN TipodeProducto43 IN (21,22,23,24,25,29) THEN 1
	ELSE 0
	END AS 'PRODUCTO MICRO?',
TIPO_afil,
CASE
	WHEN TIPO_afil LIKE 'NUEVO' THEN 1
	ELSE 0
	END AS 'AFILIACIÓN NUEVO?',
REGIMEN_LABORAL,
CASE
	WHEN REGIMEN_LABORAL LIKE 'CAS' THEN 1
	ELSE 0
	END AS 'REGIMEN CAS?',
Departamento

FROM anexos_riesgos2..Anx06_preliminar
WHERE FechaCorte1 IS NOT NULL
AND FechadeNacimiento3 IS  NOT NULL
AND FechadeDesembolso21 IS NOT NULL
and MontodeDesembolso22 > 0
and FechadeNacimiento3 < FechadeDesembolso21
and FechaCorte1 = '20230930'
''', conn)

del conn
base['log desembolsado'] = np.log(base['MontodeDesembolso22'])
base['log edad'] = np.log(base['EDAD'])

#%% establecimiento del Xy
X = base[['log edad', 'LIMEÑO?', 'SEXOOO', 'ESTADO CIVIL', 'DOCUMENTO 1?', 'PERSONA 1?',
          'log desembolsado', 'TasadeInteresAnual23', 'PRODUCTO DXP?',
          'PRODUCTO PEQUEÑA?', 'PRODUCTO MICRO?',
          'AFILIACIÓN NUEVO?', 'REGIMEN CAS?']]

y = base['MOROSO?']

#%% MODELO QUE HACE MÁS MODELOS
X_train, X_test, y_train, y_test = train_test_split(X, y,
                                                    test_size    = .2,
                                                    random_state = 123,)
clf = LazyClassifier(verbose         = 0,
                     ignore_warnings = True, 
                     custom_metric   = None)

models,predictions = clf.fit(X_train, X_test, y_train, y_test)
print(models)

