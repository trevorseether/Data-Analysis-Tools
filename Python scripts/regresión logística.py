# -*- coding: utf-8 -*-
"""
Created on Wed May  3 09:29:52 2023

@author: sanmiguel38
"""
import pandas as pd
import pyodbc

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import statsmodels.api as sm
import numpy as np

import matplotlib.pyplot as plt
from matplotlib import style
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Configuración matplotlib
# ==============================================================================
plt.rcParams['image.cmap'] = "bwr"
#plt.rcParams['figure.dpi'] = "100"
plt.rcParams['savefig.bbox'] = "tight"
style.use('ggplot') or plt.style.use('ggplot')

#%%
#CONECCIÓN A SQL
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

''', conn)

base['log desembolsado'] = np.log(base['MontodeDesembolso22'])
base['log edad'] = np.log(base['EDAD'])

#%% ESTABLECEMOS X y
X = base[['log edad', 'LIMEÑO?', 'SEXOOO', 'ESTADO CIVIL', 'DOCUMENTO 1?', 'PERSONA 1?',
          'log desembolsado', 'TasadeInteresAnual23', 'PRODUCTO DXP?',
          'PRODUCTO PEQUEÑA?', 'PRODUCTO MICRO?',
          'AFILIACIÓN NUEVO?', 'REGIMEN CAS?']]

X = sm.add_constant(X)
#X['EDAD'] = X['EDAD'].astype(int)

y = base['MOROSO?']


df_filtrado = X[X.isna().any(axis=1)]

# Dividir los datos en conjuntos de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.05, random_state=5)

# Crear y ajustar el modelo de regresión logística
logreg = LogisticRegression()
logreg.fit(X_train, y_train)

# Hacer predicciones en el conjunto de prueba
y_pred = logreg.predict(X_test)

# Evaluar la precisión del modelo en el conjunto de prueba
print(classification_report(y_test, y_pred))

#%%
train_accuracy = logreg.score(X_train, y_train)
print("Train accuracy:", train_accuracy)

# obtener el accuracy del modelo sobre los datos de prueba
test_accuracy = logreg.score(X_test, y_test)
print("Test accuracy:", test_accuracy)

# obtener las predicciones del modelo sobre los datos de prueba
y_pred = logreg.predict(X_test)

coeficients = logreg.coef_
print("Coeficients:", coeficients)

# obtener el intercepto de la regresión logística
intercept = logreg.intercept_
print("Intercept:", intercept)

#%%

logit_model=sm.Logit(y,X)
result=logit_model.fit()

# Imprimir los resultados de la regresión
print(result.summary())

#%%
#correlación
def tidy_corr_matrix(corr_mat):
    '''
    Función para convertir una matriz de correlación de pandas en formato tidy
    '''
    corr_mat = corr_mat.stack().reset_index()
    corr_mat.columns = ['variable_1','variable_2','r']
    corr_mat = corr_mat.loc[corr_mat['variable_1'] != corr_mat['variable_2'], :]
    corr_mat['abs_r'] = np.abs(corr_mat['r'])
    corr_mat = corr_mat.sort_values('abs_r', ascending=False)
    
    return(corr_mat)

corr_matrix = X.select_dtypes(include=['float64', 'int']).corr(method='pearson')
tidy_corr_matrix(corr_matrix).head(50)

# Heatmap matriz de correlaciones
# ==============================================================================
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(20, 20))

sns.heatmap(
    corr_matrix,
    annot     = True,
    cbar      = False,
    annot_kws = {"size": 12},
    vmin      = -1,
    vmax      = 1,
    center    = 0,
    cmap      = sns.diverging_palette(20, 220, n=200),
    square    = True,
    ax        = ax
)

ax.set_xticklabels(
    ax.get_xticklabels(),
    rotation = 90,
    horizontalalignment = 'right',
)

ax.tick_params(labelsize = 15)

#%%
#graficando una función logística
def f(x):
    return 1/(1 +(np.e**(-x)))

x = np.linspace(-10, 10, 50)
y = f(x)
plt.plot(x, y, label='sin(x)', color='blue')
plt.title('Gráfica de la función logística')
plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.show()

#%%

#redes neuronales

!pip install --upgrade tensorflow
!pip install --upgrade google-auth
!pip install --upgrade numpy

pip install tensorflow
import tensorflow as tf
from tensorflow import keras
from sklearn.model_selection import train_test_split

# Dividir los datos en conjunto de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Crear un modelo de red neuronal secuencial
model = keras.Sequential([
    keras.layers.Dense(64, activation='relu', input_shape=[len(X.columns)]),
    keras.layers.Dense(64, activation='relu'),
    keras.layers.Dense(1, activation='sigmoid')
])

# Compilar el modelo
model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy'])

# Entrenar el modelo
history = model.fit(X_train, y_train, epochs=50, validation_data=(X_test, y_test))

# Evaluar el modelo en el conjunto de prueba
test_loss, test_acc = model.evaluate(X_test, y_test)
print('Precisión en el conjunto de prueba:', test_acc)

import numpy as np


print(np.e)
