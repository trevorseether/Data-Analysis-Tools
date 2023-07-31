# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 10:28:00 2023

@author: Joseph Montoya
"""

import pandas as pd
import pyodbc
import numpy as np

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

#%% DATOS
conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')

# QUERY
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
AND Situacion_Credito is NOT NULL
and MontodeDesembolso22 > 0
and FechadeNacimiento3 < FechadeDesembolso21
and FechaCorte1 = '20230630'
''', conn)

# AGREGANDO LOGARITMOS
base['log desembolsado'] = np.log(base['MontodeDesembolso22'])
base['log edad'] = np.log(base['EDAD'])

#%% REDUCCIÓN ALEATORIA DE FILAS EN EL DATAFRAME
num_filas_aleatorias = 70000

# Obtiene una muestra aleatoria de filas del DataFrame original
filas_aleatorias = base.sample(n=num_filas_aleatorias,
                               random_state=456)

# Crea el nuevo DataFrame a partir de las filas aleatorias seleccionadas
df_aleatorio = pd.DataFrame(filas_aleatorias)

df_aleatorio == filas_aleatorias
# Restablece los índices del nuevo DataFrame para que sean consecutivos
df_aleatorio.reset_index(drop=True, inplace=True)

#%% DATAFRAME PARA TRABAJAR

DATA = base.copy() #aquí se pone el dataframe que vamos a usar

#%%
# establecemos X y
X = DATA[['LIMEÑO?', 'SEXOOO', 'ESTADO CIVIL',
          'DOCUMENTO 1?', 'PERSONA 1?',
          'PRODUCTO DXP?', 'PRODUCTO PEQUEÑA?',
          'PRODUCTO MICRO?', 'AFILIACIÓN NUEVO?',
          'REGIMEN CAS?']]

# Obtener la columna de la variable objetivo
y = DATA['MOROSO?'].values

#%%

# Crear el modelo de redes neuronales
model = Sequential()

# Agregar capas al modelo
model.add(Dense(40, input_dim=10, activation='relu'))
model.add(Dense(1, activation='sigmoid'))

# Compilar el modelo
model.compile(loss='binary_crossentropy', 
              optimizer='adam', 
              metrics=['accuracy'])

# Entrenar el modelo
model.fit(X, y, epochs=100, batch_size=1)

# Hacer predicciones
predictions = model.predict(X)

#%% convertimos las predicciones a binario

predictions_binary = (predictions > 0.68).astype(int)
#print(predictions_binary)

#%%
# Convierte las predicciones binarias a un DataFrame
df_predictions = pd.DataFrame({'Predicciones': list(predictions_binary)})

# Imprime la tabla de conteo
print('')
print('predicción')
print(df_predictions['Predicciones'].value_counts())
print('')
print('datos originales')
print(base['MOROSO?'].value_counts())

#%% creación de dataframe 

base_dataframe = pd.DataFrame({'MOROSO?': base['MOROSO?']})
predictions_dataframe = pd.DataFrame({'Predicciones': df_predictions['Predicciones']})

# Concatenar los DataFrames horizontalmente
df_comparacion = pd.concat([base_dataframe, predictions_dataframe], axis=1)

df_comparacion['Predicciones'] = df_comparacion['Predicciones'].astype(str)
df_comparacion['Predicciones'] = df_comparacion['Predicciones'].str.strip()

df_comparacion['Predicciones'] = df_comparacion['Predicciones'].str.replace('[', '', regex=True)
df_comparacion['Predicciones'] = df_comparacion['Predicciones'].str.replace(']', '', regex=True)
df_comparacion = df_comparacion.astype(int)

# Imprimir el DataFrame resultante
'''
print(df_comparacion[df_comparacion['MOROSO?'] != df_comparacion['Predicciones']]) #mal predecido

print(df_comparacion[(df_comparacion['MOROSO?'] == 0) &
                     (df_comparacion['MOROSO?'] == df_comparacion['Predicciones'])]) #morosos bien predecidos
'''
#%% MATRIZ DE CONFUSIÓN

clase_real = df_comparacion['MOROSO?'].values
prediccion_modelo = df_comparacion['Predicciones'].values

# Calcular la matriz de confusión
confusion_matrix = pd.crosstab(clase_real, prediccion_modelo, 
                               rownames=['Clase Real'], 
                               colnames=['Prediccion Modelo'])

# Imprimir la matriz de confusión
print(confusion_matrix)
