# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 10:26:19 2024

@author: sanmiguel38
"""

import pandas as pd
import win32com.client as win32
import os

#%%
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\envio de correos\\GARANTÍA CAPITAL')

ENVIAR_CORREOS = True

#%%
# Carga tu dataframe (asegúrate de que tiene las columnas 'correo', 'mensaje' y 'asunto')
df = pd.read_excel('Account m365 garantiacapital password.xlsx',
                   sheet_name = 'Hoja1',
                   skiprows   = 0,
                   dtype      = str)  # Reemplaza con tu archivo

df.dropna(subset = ['Correo electrónico', 
                    'Contraseña'], 
           inplace = True, 
           how     = 'all')

df.columns = ['NÚMERO', 'Nombres', 'Apellidos', 'nom', 'correo', 'contraseña']

df['nom']        = df['nom'].str.strip()
df['correo']     = df['correo'].str.strip()
df['contraseña'] = df['contraseña'].str.strip()

df['asunto'] = 'NUEVO ACCESO DE CORREO CORPORATIVO-MICROSOFT 365'

#%%
# Conexión a Outlook
outlook = win32.Dispatch('outlook.application')

contador = 1

if ENVIAR_CORREOS == True:

# Iterar sobre las filas del dataframe y enviar correos
    for index, row in df.iterrows():
        mail = outlook.CreateItem(0)
        mail.To = row['correo']
        mail.Subject = row['asunto']
        
        # Cuerpo del correo usando HTML y variables dinámicas
        mensaje_html = f'''
    <p style="text-align: left;color: rgb(44, 54, 58);background-color: rgb(255, 255, 255);font-size: 14px;font-family: Roboto, sans-serif;">Estimado/a {row['nom']},</p>
    <p style="text-align: left;color: rgb(44, 54, 58);background-color: rgb(255, 255, 255);font-size: 14px;font-family: Roboto, sans-serif;">Se detalla sus credenciales de acceso a la nueva plataforma de correo Microsoft, el cual se encontrará habilitado y pudiendo ingresar a partir de hoy, viernes 28/02/25, desde las 9PM &ldquo;<strong>SOLO PARA USO OUTLOOK ONLINE&rdquo;</strong>.</p>
    <table border="0" cellspacing="0" cellpadding="0" width="557" style="text-align: left; color: rgb(44, 54, 58); background-color: rgb(255, 255, 255); font-size: 14px; font-family: Roboto, sans-serif; border-collapse: collapse; width: 100%;">
        <tbody>
            <tr>
                <td valign="bottom" style="border: 1pt solid windowtext; width: 231px;">
                    <p align="center" style="text-align: center;"><span style="color: black;font-size: 12pt;">Correo electr&oacute;nico</span></p>
                </td>
                <td valign="bottom" style="border-left: none; border-right: 1pt solid windowtext; border-top: 1pt solid windowtext; border-bottom: 1pt solid windowtext; width: 132px;">
                    <p align="center" style="text-align: center;"><span style="color: black;font-size: 12pt;">Contrase&ntilde;a</span></p>
                </td>
                <td valign="bottom" style="border-left: none; border-right: 1pt solid windowtext; border-top: 1pt solid windowtext; border-bottom: 1pt solid windowtext; width: 195px;">
                    <p align="center" style="text-align: center;"><span style="color: black;font-size: 12pt;">Link Microsoft (todas las herramientas)</span></p>
                </td>
                <td valign="bottom" style="border-left: none; border-right: 1pt solid windowtext; border-top: 1pt solid windowtext; border-bottom: 1pt solid windowtext; width: 150px;">
                    <p align="center" style="text-align: center;"><span style="color: black;font-size: 12pt;">Link Outlook Online</span></p>
                </td>
            </tr>
            <tr>
                <td valign="bottom" style="border-left: 1pt solid windowtext; border-right: 1pt solid windowtext; border-top: none; border-bottom: 1pt solid windowtext; width: 132px;">
    
                    <p style="text-align: center;"><span style="color: black;">&nbsp;{row['correo']}</span></p>
                </td>
                <td valign="bottom" style="border-left: none; border-right: 1pt solid windowtext; border-top: none; border-bottom: 1pt solid windowtext; width: 132px;">
                    <p align="right" style="text-align: center;">{row['contraseña']}</p>
                </td>
                <td valign="bottom" style="border-left: none; border-right: 1pt solid windowtext; border-top: none; border-bottom: 1pt solid windowtext; width: 195px;">
                    <p style="text-align: center;"><a href="https://office.com/?auth=2" target="_blank" rel="noreferrer" style="color: rgb(5, 99, 193);"><span style="font-size: 12pt;">https://office.com/?auth=2</span></a></p>
                </td>
                <td valign="bottom" style="border-left: none; border-right: 1pt solid windowtext; border-top: none; border-bottom: 1pt solid windowtext; width: 195px;">
                    <p style="text-align: center;"><a href="https://office.com/?auth=2" target="_blank" rel="noreferrer" style="color: rgb(5, 99, 193);"><span style="font-size: 12pt;">https://outlook.office.com</span></a></p>
                </td>
    
            </tr>
        </tbody>
    </table>
    
    <p style="text-align: left;color: rgb(44, 54, 58);background-color: rgb(255, 255, 255);font-size: 14px;font-family: Roboto, sans-serif;"><strong>&nbsp;</strong></p>
    <p style="text-align: left;color: rgb(44, 54, 58);background-color: rgb(255, 255, 255);font-size: 14px;font-family: Roboto, sans-serif;"><strong>A partir de dicha hora (9pm), y en adelante, todo proceso de envio y recepcion de correos ser&aacute; mediante la nueva plataforma v&iacute;a Microsoft</strong> (la plataforma de correo actual dejará de operar, no recibiendo, ni poder enviar mensaje alguno).</p>
    <p style="text-align: left;color: rgb(44, 54, 58);background-color: rgb(255, 255, 255);font-size: 14px;font-family: Roboto, sans-serif;"><strong>&nbsp;</strong></p>
    <p style="text-align: left;color: rgb(44, 54, 58);background-color: rgb(255, 255, 255);font-size: 14px;font-family: Roboto, sans-serif;">IMPORTANTE:</p>
    <p style="text-align: left;color: rgb(44, 54, 58);background-color: rgb(255, 255, 255);font-size: 14px;font-family: Roboto, sans-serif;">1.No realizar cambio de clave al menos la primera semana (por el proceso de migraci&oacute;n).</p>
    <p style="text-align: left;color: rgb(44, 54, 58);background-color: rgb(255, 255, 255);font-size: 14px;font-family: Roboto, sans-serif;">2.Los correos existentes se podr&aacute;n visualizar al 100% entre el d&iacute;a lunes-martes (Seg&uacute;n cantidad de correos almacenados).</p>
    <p style="text-align: left;color: rgb(44, 54, 58);background-color: rgb(255, 255, 255);font-size: 14px;font-family: Roboto, sans-serif;">3.Desde el d&iacute;a martes 04, el &aacute;rea de TI estar&aacute; realizando la configuraci&oacute;n del Outlook v&iacute;a escritorio de manera progresiva.</p>
    <p style="text-align: left;color: rgb(44, 54, 58);background-color: rgb(255, 255, 255);font-size: 14px;font-family: Roboto, sans-serif;">4.En caso de requerimientos espec&iacute;ficos pueden comunicarse con el &aacute;rea de soporte mediante el WhatsApp T.I. 990 324 612.<br><br><br>Atentamente.&nbsp;<br>Subgerencia de T.I. Garantía Capital.</p>'''
    
    
        # Asignar el cuerpo del correo como HTML
        mail.HTMLBody = mensaje_html    
        
        
        # Puedes añadir un archivo adjunto si lo deseas
        # mail.Attachments.Add("ruta/al/archivo")
        
        mail.Send()
        print(f"Correo enviado a: {row['correo']}")
        print(contador)
        contador += 1
    
    


#%% versión sin cuerpo html y sin formato:

'''

import pandas as pd
import win32com.client as win32

# Carga tu dataframe (asegúrate de que tiene las columnas 'correo', 'mensaje' y 'asunto')
df = pd.read_excel('correos.xlsx')  # Reemplaza con tu archivo

# Conexión a Outlook
outlook = win32.Dispatch('outlook.application')

# Iterar sobre las filas del dataframe y enviar correos
for index, row in df.iterrows():
    mail = outlook.CreateItem(0)
    mail.To = row['correo']
    mail.Subject = row['asunto']
    mail.Body = row['mensaje']
    
    # Puedes añadir un archivo adjunto si lo deseas
    # mail.Attachments.Add("ruta/al/archivo")
    
    mail.Send()
    print(f"Correo enviado a: {row['correo']}")



'''