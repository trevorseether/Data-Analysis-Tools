# -*- coding: utf-8 -*-
"""
Created on Tue May  9 13:02:49 2023

@author: Joseph Montoya
"""

import os

os.chdir('C:\\Users\\usuario\\Desktop') #cada carpeta se debe separar por doble \

import pandas as pd

datos = pd.read_excel('C:\\Users\\usuario\\Desktop\\archivo.xlsx')


x = '\\\\\\'

def operador_modulo(x):
    if x % 2 == 0 :
        return True
    return False

import numpy as np

def f(x):
    # Aquí se define la función
    return x**2

x = np.linspace(-1, 1, num=100)  # Puntos en los que se evalúa la función
y = f(x)  # Valores de la función en los puntos x
dydx = np.gradient(y, x)  # Estimación numérica de la derivada
print(dydx)


list(filter(lambda x: x % 2 == 0, [3, 7, 9, 22, 27]))


print(list(filter(lambda x: x % 2 == 0, [3, 7, 9, 22, 27])))

def eliminar_duplicados(lista):
    return list(set(map(tuple, lista)))

lista = [[12, 25], [40, 33], [30, 56, 25], [10, 12], [33], [40]]
lista_sin_duplicados = eliminar_duplicados(lista)
print(lista_sin_duplicados)



import numpy as np
import matplotlib.pyplot as plt
plt.hist([1,2,1],bins=[0,1,2,3,5])

plt.hist([1,2,1],bins=[0,1,2,3,5])
plt.show()

plt.hist([1,2,1],bins=[0,1,2,3,5])


def calcular_pendiente(f, x, h=0.0001):
    """
    Calcula la pendiente de la función `f` en el punto `x` utilizando la aproximación mediante diferencias finitas.
    
    :param f: Función a evaluar.
    :param x: Punto en el que se desea calcular la pendiente.
    :param h: Tamaño del paso para la aproximación de la derivada. Valor por defecto: 0.0001.
    :return: Pendiente de la función `f` en el punto `x`.
    """
    dy = f(x + h) - f(x)
    dx = h
    return dy/dx



import os 
import pandas as pd
os.chdir('C:\\Users\\sanmiguel38\\Desktop')

df = pd.read_excel('BD_prob_default.xlsx')

import statsmodels.api as sm
df.columns

X = df[['RETA', 'EBITTA', 'METL','STA']]
y = df['Default']

# Ajustar el modelo logit utilizando la función Logit de statsmodels
logit_model = sm.Logit(y, sm.add_constant(X))

# Obtener los resultados del modelo
resultados = logit_model.fit()

# Imprimir los coeficientes y sus p-valores
print(resultados.summary())

from sklearn.model_selection import train_test_split
# Dividir los datos en conjuntos de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Ajustar el modelo logit utilizando los datos de entrenamiento
logit_model = sm.Logit(y_train, sm.add_constant(X_train))
logit_results = logit_model.fit()

# Hacer predicciones en el conjunto de prueba
X_test_with_constant = sm.add_constant(X_test)
predicted_proba = logit_results.predict(X_test_with_constant)

# Imprimir las probabilidades de default para el conjunto de prueba
print(predicted_proba)

