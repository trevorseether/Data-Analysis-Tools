# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 09:47:24 2023

@author: sanmiguel38
"""

import numpy as np
import pyodbc
import pandas as pd

conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')
df = pd.read_sql_query('''
Select 
	Saldodecolocacionescreditosdirectos24,
	MontodeDesembolso22,
	CASE
		WHEN TipodeProducto43 IN (15,16,17,18,19) THEN 'PEQUEÑA'
		WHEN TipodeProducto43 IN (21,22,23,24,25,29) THEN 'MICRO'
		WHEN TipodeProducto43 IN (34,35,36,37,38,39) THEN 'DXP'
		WHEN TipodeProducto43 IN (30,31,32,33) THEN 'LD'
		WHEN TipodeProducto43 IN (41,45) THEN 'HIPOTECARIA'
		WHEN TipodeProducto43 IN (95,96,97,98,99) THEN 'MEDIANA'
		ELSE 'OTROS'
		END AS 'PROD TXT'

from 
	anexos_riesgos2..Anx06_preliminar
where 
	FechaCorte1 = '20230430'
    and Saldodecolocacionescreditosdirectos24 > 0
    and MontodeDesembolso22 > 0    ''', conn)

#%%
import seaborn as sns
sns.set_theme(style='dark') #['white', 'dark', 'whitegrid', 'darkgrid', 'ticks']
sns.jointplot(x=df['Saldodecolocacionescreditosdirectos24'], 
              y=df['MontodeDesembolso22'], 
              kind="hist", #['scatter', 'hist', 'hex', 'kde', 'reg', 'resid']
              color="#4CB391", # https://htmlcolorcodes.com/es/
              xlim=(1,30000), #límites del eje x
              ylim=(1, 30000)) #límites del eje y

#%%
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt

sns.set_theme(style="ticks")

diamonds = sns.load_dataset("diamonds")

f, ax = plt.subplots(figsize=(7, 5))
sns.despine(f)

sns.histplot(
    df, #aquí se puede establecer del dataframe para no especificarlo más adelante, es opcional si especificamos la columna dataframe['columna']
    x=df['Saldodecolocacionescreditosdirectos24'], 
    hue=df['PROD TXT'],
    multiple="stack",
    palette="light:m_r",
    edgecolor=".3",
    linewidth=.5,
    log_scale=True
)
ax.xaxis.set_major_formatter(mpl.ticker.ScalarFormatter())
ax.set_xticks([500,15000])

ax.set_xlim(100, 20000)  # Cambiar límites del eje x
ax.set_ylim(0, 1000)  # Cambiar límites del eje y

#%%
df2 = df.head(300)
#%%
import seaborn as sns
sns.set_theme(style="ticks")

# Load the planets dataset and initialize the figure
g = sns.JointGrid(data=df2, 
                  x=df2['Saldodecolocacionescreditosdirectos24'], 
                  y=df2['MontodeDesembolso22'],
                  marginal_ticks=True)

# Set a log scaling on the y axis
g.ax_joint.set(yscale="linear") # ["log", "linear", "symlog", "symlog", "logit"]

# Create an inset legend for the histogram colorbar
cax = g.figure.add_axes([.15, .55, .02, .2])

# Add the joint and marginal histogram plots
g.plot_joint(
    sns.histplot, discrete=(True, False),
    cmap="light:#03012d", pmax=0.01, cbar=True, cbar_ax=cax
)
g.plot_marginals(sns.histplot, element="step", color="#03012d")



