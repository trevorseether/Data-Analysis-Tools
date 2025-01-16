# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 16:39:59 2025

@author: sanmiguel38
"""

# =============================================================================
# corrección de los días de gracia negativos
# =============================================================================

import os
import pandas as pd

#%%
# REQUISITOS PARA HACER ESTE PROCESAMIENTO
#     prmpr en excel con columnas ampliadas para cálculo de los días de gracia
#     excel completo de insumo donde están todas las pestañas

#%% prmpr
nombre_prmpr_ampliado = 'dias gracia ajustados.xlsx'
ubi_prmpr_ampliado    = 'C:\\Users\\sanmiguel38\\Desktop\\prueba\\nueva generación de datos\\02_Prestamos-16012025'

prmpr_ampliado = pd.read_excel(ubi_prmpr_ampliado + '\\' + nombre_prmpr_ampliado,
                               skiprows = 0,
                               dtype    = str)
del nombre_prmpr_ampliado
ubi_prmpr_ampliado

#%% prtsa (tasa de interés del crédito)
excel_completo = '02_Prestamos-16012025.xlsx'
ubi_excel_completo = 'C:\\Users\\sanmiguel38\\Desktop\\prueba\\nueva generación de datos'

pestana = 'prtsa'

tasas_interes = pd.read_excel(ubi_excel_completo + '\\' + excel_completo,
                              sheet_name = pestana,
                              skiprows   = 8,
                              dtype      = str)
del excel_completo
del ubi_excel_completo
del pestana

tasas_interes['tasa diaria'] = ((1+((tasas_interes['TEAPRTSA'].astype(float))/100))**(1/360))-1

#%% interés capitalizado
cuotas1    = 'prppg.csv'
cuotas2    = 'prppg (2).csv'
ubi_cuotas = 'C:\\Users\\sanmiguel38\\Desktop\\prueba\\nueva generación de datos\\02_Prestamos-16012025'

columnas = ['NroPrestamo','FechaVencimiento','numerocuota','capital','interes','CargosGenerales','CargosSeguro',
            'Aporte','TotalCargo','TotalPago','Ahorros','Pagado']

prppg1 = pd.read_csv(ubi_cuotas + '\\' + cuotas1,
                     dtype  = str ,
                     header = None,
                     names  = columnas,
                     sep=";")
prppg2 = pd.read_csv(ubi_cuotas + '\\' + cuotas2,
                     dtype  = str ,
                     header = None,
                     names  = columnas,
                     sep=";")

prppg = pd.concat([prppg1, prppg2], axis=0, ignore_index=True)

prppg['nro cuota generado'] = prppg.groupby('NroPrestamo').cumcount()

cuotas_cero = prppg[ (prppg['numerocuota'] == '0')  &  (prppg['nro cuota generado'] == 0)]
cuotas_cero = cuotas_cero[['NroPrestamo', 'interes']]

del columnas

#%% juntando prmpr ampliado con las tasas de interés y con el interés capitalizado
prmpr = prmpr_ampliado.merge(tasas_interes[['NumerodePrestamoPRTSA', 'tasa diaria']],
                             left_on  = 'NumerodePrestamo',
                             right_on = 'NumerodePrestamoPRTSA',
                             how = 'left')

nulos = prmpr[pd.isna(prmpr['tasa diaria'])]
if nulos.shape[0] > 0:
    print('match incompleto')
    
del prmpr['NumerodePrestamoPRTSA']
###############################################################################
prmpr = prmpr.merge(cuotas_cero,
                    left_on  = 'NumerodePrestamo',
                    right_on = 'NroPrestamo',
                    how = 'left'
                    )
nulos = prmpr[pd.isna(prmpr['interes'])]
if nulos.shape[0] > 0:
    print('match incompleto')
    
del prmpr['NroPrestamo']

#%% dias de gracia
prmpr["interes"] = prmpr["interes"].astype(float)
prmpr["MontoDesembolsadoAX"] = prmpr["MontoDesembolsadoAX"].astype(float)

import numpy as np
prmpr["dias"] = np.log((prmpr["interes"] / prmpr["MontoDesembolsadoAX"]) + 1) / np.log(1 + prmpr["tasa diaria"])
prmpr["dias redondeado"] = prmpr["dias"].round(0)

#%%
raraso = prmpr[prmpr["dias redondeado"] < 0]
if raraso.shape[0] > 0:
    print('dias de gracia negativos ahhhhhhhhhhhhhh')
    
#%%
prmpr['dias de gracia final'] = prmpr['(No column name).11'].astype(int)

def ajuste_dias_de_gracia(prmpr):
    if prmpr['dias de gracia final'] < 0:
        return prmpr["dias redondeado"]
    # if prmpr["dias redondeado"] == 0:
    #     return 0
    if prmpr['CodigoEstadoOperacion'] == '9': # para poner cero días de gracia a los cancelados
        return 0

    # añadir que todo crédito anterior a marzo/2022 debe tener cero de días de gracia
    else:
        return prmpr['dias de gracia final']

prmpr['dias de gracia final'] = prmpr.apply(ajuste_dias_de_gracia, axis = 1)

#%%
os.chdir(ubi_prmpr_ampliado)
# os.chdir('C:\\Users\\sanmiguel38\\Desktop\\prueba')

prmpr.to_excel('prmpr días de gracia arreglado (2).xlsx',
               index = False)

#%%
print('final')

