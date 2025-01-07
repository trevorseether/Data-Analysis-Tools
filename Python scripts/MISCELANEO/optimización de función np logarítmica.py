# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 09:48:15 2024

@author: sanmiguel38
"""

import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# Datos de los puntos
x_data = np.array([0, 2, 11])
y_data = np.array([0, 10, 20])

# Definir la función logarítmica a ajustar
def log_func(x, a, b):
    return a * np.log(b * x + 1)

# Ajustar los parámetros (a, b) utilizando curve_fit
params, _ = curve_fit(log_func, x_data, y_data)

# Extraer los parámetros optimizados
a_opt, b_opt = params
print(f"Parámetros óptimos: a = {a_opt}, b = {b_opt}")

# Graficar los puntos y la curva ajustada
x_fit = np.linspace(0, 12, 100)
y_fit = log_func(x_fit, a_opt, b_opt)

plt.scatter(x_data, y_data, label='Datos', color='red')
plt.plot(x_fit, y_fit, label=f'Ajuste: a={a_opt:.2f}, b={b_opt:.2f}', color='blue')
plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.title('Ajuste de Función Logarítmica')
plt.grid(True)
plt.show()


#%%

import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# Datos de los puntos
x_data = np.array([0, 2, 8])
y_data = np.array([0, 10, 20])

# Definir la función logarítmica a ajustar
def log_func(x, a, b):
    return a * np.log(b * x + 1)

# Ajustar los parámetros (a, b) utilizando curve_fit
params, _ = curve_fit(log_func, x_data, y_data)

# Extraer los parámetros optimizados
a_opt, b_opt = params
print(f"Parámetros óptimos: a = {a_opt}, b = {b_opt}")

# Graficar los puntos y la curva ajustada
x_fit = np.linspace(0, 10, 100)
y_fit = log_func(x_fit, a_opt, b_opt)

plt.scatter(x_data, y_data, label='Datos', color='red')
plt.plot(x_fit, y_fit, label=f'Ajuste: a={a_opt:.2f}, b={b_opt:.2f}', color='blue')
plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.title('Ajuste de Función Logarítmica')
plt.grid(True)
plt.show()


