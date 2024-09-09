# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 16:01:34 2024

@author: sanmiguel38
"""
import pandas as pd
import os 

#%%
os.chdir('R:\\REPORTES DE GESTIÓN\\DESARROLLO\\Implementacion NetBank\\Datos para Migracion\\Crediticio\\04092024\\Procesamiento 06-09-2024')
excel        = '002_Prestamos.xlsx'

sheet_nombre = 'prppg'
filas_skip   = 9
crear_csv   = False
crear_excel = True
#########################################
verificar_duplicados = False
columna_unica = 'NumerodePrestamo'
#########################################

#%%
###############################################################################
df1 = pd.read_excel(io         = excel,
                    skiprows   = filas_skip,
                    sheet_name = sheet_nombre,
                    dtype      = str)
print(df1.shape[1])

# df1['CodigoSocio'] = df1['CodigoSocio'].str.strip()
# df1 = df1.replace('Ü', 'U', regex = True )
# df1 = df1.replace('Á', 'A', regex = True )
# df1 = df1.replace('É', 'E', regex = True )
# df1 = df1.replace('Í', 'I', regex = True )
# df1 = df1.replace('Ó', 'O', regex = True )
# df1 = df1.replace('Ú', 'U', regex = True )

df1 = df1.replace(';', '', regex = True)
df1 = df1.fillna('')

#%% VALIDACION DE INDEX prppg

df1['index_unico']  = df1['NroPrestamo'] + '-'+ df1['numerocuota']
df1['es_duplicado'] = df1['index_unico'].duplicated(keep=False)

df1['es_duplicado_debajo'] = df1['index_unico'].duplicated(keep='first')
df1['es_duplicado_arriba'] = df1['index_unico'].duplicated(keep='last')

df1['capital_float']    = df1['capital'].astype(float)

def mantener(df1):
    if df1['es_duplicado'] == False:
        return 'mantener'

    if (df1['numerocuota'] == '0') and (df1['numerocuota'] == '0'):
        return 'mantener'

    if (df1['numerocuota'] == '0') and (df1['capital_float'] > '0'):
        return 'mantener-amortización'
    
    if (df1['numerocuota'] != '0') and (df1['es_duplicado'] == True) and (df1['es_duplicado_arriba'] == False):
        return 'mantener'
    else:
        return ''
    
df1['mantener'] = df1.apply(mantener, axis = 1)

dup = df1[df1['es_duplicado'] == True]

#%% identificación de monocuotas

df1['numero_cuota_int'] = df1['numerocuota'].astype(int)
monocuota = df1.pivot_table(values   = 'numero_cuota_int',
                             index   = 'NroPrestamo',
                             aggfunc = 'sum').reset_index()
monocuota = monocuota.rename(columns = {'numero_cuota_int' : 'suma_cuotas'})

conteo_cuotas = df1.pivot_table(values  = 'numero_cuota_int',
                                
                                index   = 'NroPrestamo',
                                aggfunc = 'count').reset_index()
conteo_cuotas = conteo_cuotas.rename(columns = {'numero_cuota_int' : 'numero_cuotas'})

identificacion_monocuotas = monocuota.merge(conteo_cuotas,
                                            on = 'NroPrestamo',
                                            how = 'left')
def mono(df):
    if df['suma_cuotas'] == df['numero_cuotas']:
        return 'monocuota'

identificacion_monocuotas['mono'] = identificacion_monocuotas.apply(mono, axis = 1)

monos = identificacion_monocuotas[identificacion_monocuotas['mono'] == 'monocuota']
monos = monos[monos['numero_cuotas'] > 1]

################# ## etiqueta monocuota para la base total (hay que rectificar)
lista_monocuotas = list(monos['NroPrestamo'])
def etiqueta_mono(df1):
    if df1['NroPrestamo'] in lista_monocuotas:
        return 'monocuota'
df1['monocuota flag'] = df1.apply(etiqueta_mono, axis = 1)

#%%
if verificar_duplicados == True:
    duplicados = df1[df1.duplicated(columna_unica, keep=False)]
    if duplicados.shape[0] > 0:
        print('alerta de duplicidad')

#%% limpieza de correos
limpiar_correos = False

if limpiar_correos == True:
    df1['gbemamail'] = df1['gbemamail'].replace(' ', '', regex = True )
    df1['gbemamail'] = df1['gbemamail'].replace('|', '', regex = True )
    
    def eliminar_coma_inicial(texto):
        # Usar str.lstrip() para eliminar la coma al principio de la cadena
        return texto.lstrip(',')
    # Aplicar la función a la columna 'gbemamail'
    df1['gbemamail'] = df1['gbemamail'].apply(eliminar_coma_inicial)
    
    df1['gbemamail'] = df1['gbemamail'].replace(',', '.', regex = True )
    df1['gbemamail'] = df1['gbemamail'].replace('..COM', '.COM', regex = True )
    df1['gbemamail'] = df1['gbemamail'].replace('@GM,AIL.COM', '@GMAIL.COM', regex = True )
    
    
    # Función para limpiar el texto después de '.com'
    import re
    def limpiar_email(texto):
        # Usar una expresión regular para mantener solo el texto hasta el primer '.com'
        return re.sub(r'\.COM.*', '.COM', texto)
    df1['gbemamail'] = df1['gbemamail'].apply(limpiar_email)
    
    def limpiar_email2(texto):
        # Usar una expresión regular para mantener solo el texto hasta el primer '@GMAIL.COM'
        return re.sub(r'(@GMAIL\.COM).*', r'\1', texto, flags=re.IGNORECASE)
    df1['gbemamail'] = df1['gbemamail'].apply(limpiar_email2)
    
    ###############################################################################
    
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.COM.PE'  , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.COM.COM' , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAILCON'      , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAI.COM'      , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GGMIAL.COM'    , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GNMAIL.COM'    , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.COMN'    , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMNAIL.COM'    , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GIMAIL.COM'    , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.CONM'    , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMA.IL.COM'    , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL..COM'    , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL'         , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@HMAIL.COM'     , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMIL.COM'      , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMEIL.COM'     , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@OUTOOK.ES'     , '@OUTLOOK.ES')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@HOTMAIL.C'     , '@HOTMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@HOTMAILCOM'    , '@HOTMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@HOTMAI.COM'    , '@HOTMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.COM.CO'  , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@HOTMAIL.COMOM' , '@HOTMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@HOTMAIL.COMOM.PE' , '@HOTMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.COMJM'   , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.COMOM'   , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.COMM'    , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIOL.COM'    , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAOL.COM'     , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GAIL.COM'      , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.COMC.OM' , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.COMPM'   , '@GMAIL.COM')
    
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAL.COM'      , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@HOTMAIIL.COM'  , '@HOTMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@HOTMAL.COM'    , '@HOTMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.COMPM'   , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMIAL.COM'     , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAILCOM'      , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAI.COM'      , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAILL.COM'    , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAL.COM'      , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.CCOM'    , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL .COM'    , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAILO.COM'    , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAILCOM'      , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.CM'      , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMNAIL.COM'    , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.COPM'    , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GAMAIL.COM'    , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.COMN'    , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GAMIL.COM'     , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GIMAIL.COM'    , '@GMAIL.COM')    
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.COMCALLE CESAR VALEJO 420 INT' , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.CM'      , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAILC.OM'     , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMIAL.COM'     , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GAMIL.COM'     , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.CONM'    , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIOL.COM'    , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GNAIL.COM'     , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GAMAIL.COM'    , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.COJM'    , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAOL.COM'     , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.CONM'    , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.COM.'    , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.COM.CM'  , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.CONM'    , '@GMAIL.COM')
    
    df1['gbemamail'] = df1['gbemamail'].str.replace('@OUTLOOCK.COM' , '@OUTLOOK.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@HOTMAIOL.COM' , '@HOTMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@OUTLOC.COM'   , '@OUTLOOK.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.COMCM'  , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.COMPE'  , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.COM*9'  , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.COMPE'  , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.COM614' , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@HTOMAIL.COM'  , '@HOTMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@HPTMAIL.COM'  , '@HOTMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.CONM'   , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.CONM'   , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.CONM'   , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.CONM'   , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.CONM'   , '@GMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GHOTMAIL.COM' , '@HOTMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@HOTMAIL.COMO' , '@HOTMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@HTMAIL.COM'   , '@HOTMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@HOTAMIL.COM'  , '@HOTMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@HOTMIAL.COM'  , '@HOTMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@HTMAIL.COM'   , '@HOTMAIL.COM')
    df1['gbemamail'] = df1['gbemamail'].str.replace('@HOSMAIL.COM'  , '@HOTMAIL.COM')
    
    # usando regular expresions
    df1['gbemamail'] = df1['gbemamail'].str.replace(r'@GMAIL$', '@GMAIL.COM', 
                                                  regex = True)
    df1['gbemamail'] = df1['gbemamail'].str.replace(r'@HOTMAIL$', '@HOTMAIL.COM', 
                                                  regex = True)
    
    df1.loc[df1['gbemamail'] == '@GMAIL.COM'    , 'gbemamail'] = 'REGULARIZARCORREO@GMAIL.COM'
    df1.loc[df1['gbemamail'] == '.@GMAIL.COM'   , 'gbemamail'] = 'REGULARIZARCORREO@GMAIL.COM'
    df1.loc[df1['gbemamail'] == '@NOTIENE.COM'  , 'gbemamail'] = 'REGULARIZARCORREO@GMAIL.COM'
    df1.loc[df1['gbemamail'] == '@NOTIEN.COM'   , 'gbemamail'] = 'REGULARIZARCORREO@GMAIL.COM'
    df1.loc[df1['gbemamail'] == '.COM'          , 'gbemamail'] = 'REGULARIZARCORREO@GMAIL.COM'
    df1.loc[df1['gbemamail'] == '@HOTMAIL.COM'  , 'gbemamail'] = 'REGULARIZARCORREO@HOTMAIL.COM'
    
    
    df1.loc[df1['gbemamail'] == 'CARLOSCASTILLOFUENTES12@'  , 'gbemamail'] = 'CARLOSCASTILLOFUENTES12@GMAIL.COM'
    df1.loc[df1['gbemamail'] == 'DENIS_POBLETE@GHOTMAIL.COM', 'gbemamail'] = 'DENIS_POBLETE@HOTMAIL.COM'
    df1.loc[df1['gbemamail'] == 'RAQUELALINA@GNAIL.COM'     , 'gbemamail'] = 'RAQUELALINA@GMAIL.COM'
    df1.loc[df1['gbemamail'] == 'RRENGIFOCORAL@HOTMAIL..COM', 'gbemamail'] = 'RRENGIFOCORAL@HOTMAIL.COM'
    df1.loc[df1['gbemamail'] == 'TATO.12.TLV@GMAOL.COM'     , 'gbemamail'] = 'TATO.12.TLV@GMAIL.COM'
    df1['gbemamail'] = df1['gbemamail'].str.replace('@GMAIL.COM\n.COM', '@GMAIL.COM')    
    
    df1.loc[df1['gbemamail'] == 'BRAULIO.18@@HOTMAIL.COM'          , 'gbemamail'] = 'BRAULIO.18@HOTMAIL.COM'
    df1.loc[df1['gbemamail'] == 'GISELAISABELLEONATOCHE@GMAIL.'    , 'gbemamail'] = 'GISELAISABELLEONATOCHE@GMAIL.COM'
    df1.loc[df1['gbemamail'] == 'RAQUELALINA@GNAIL.COMALDAIRPOLOPASTOR@GMAIL.COM9614' , 'gbemamail'] = 'ALDAIRPOLOPASTOR@GMAIL.COM'
    df1.loc[df1['gbemamail'] == 'HERRERA2019ROMULO@OUTLOOK.COM-'   , 'gbemamail'] = 'HERRERA2019ROMULO@OUTLOOK.COM'
    df1.loc[df1['gbemamail'] == 'CESARSOLISBARRETO@GM,AIL.COM'     , 'gbemamail'] = 'CESARSOLISBARRETO@GMAIL.COM'
    df1.loc[df1['gbemamail'] == 'LISSET_SS@HOTM,AIL.COM', 'gbemamail'] = 'LISSET_SS@HOTMAIL.COM'
    df1['gbemamail'] = df1['gbemamail'].str.replace('@KONECTA_GROUP.COM'    , '@KONECTA-GROUP.COM')    
    
    df1.loc[df1['gbemamail'] == 'MARJORIE.LIBRAVITVIL1994@GMAIL', 'gbemamail'] = 'MARJORIE.LIBRAVITVIL1994@GMAIL.COM'
    df1.loc[df1['gbemamail'] == 'CIBER_APOL@HOTMAIL'            , 'gbemamail'] = 'CIBER_APOL@HOTMAIL.COM'
    df1.loc[df1['gbemamail'] == 'JSU8095@GMAIL.COM*9'           , 'gbemamail'] = 'JSU8095@GMAIL.COM'
    
    ###########################################################################
    df1.loc[df1['gbemamail'] == 'RQUIROZQ@SUNAT.GOB.PEDR.RICARDOQUIROZ@HOTMAIL.COM', 'gbemamail'] = 'DR.RICARDOQUIROZ@HOTMAIL.COM'
    df1.loc[df1['gbemamail'] == 'MCESPEDES412@YAHOO.ESDCESPEDES@PJ.GOB.PE',          'gbemamail'] = 'MCESPEDES412@YAHOO.ES'
    df1.loc[df1['gbemamail'] == 'WALTERARIAS012@GMAIL.COMONIASERQUEF@HOTMAIL.COM',   'gbemamail'] = 'WALTERARIAS012@GMAIL.COM'
    df1.loc[df1['gbemamail'] == 'GANDRADE@SUNAT.GOB.PEGUILLERMO7020@HOTMAIL.COM',    'gbemamail'] = 'MARJORIE.LIBRAVITVIL1994@GMAIL.COM'
    df1.loc[df1['gbemamail'] == 'JESSYANCH@YAHOO.ESRANCHANTE@PJ.GOB.PE',             'gbemamail'] = 'JESSYANCH@YAHOO.ES'
    df1.loc[df1['gbemamail'] == 'ELEON@APCI.GOB.PEELEON.F@GMAIL.COM',                'gbemamail'] = 'ELEON@APCI.GOB.PE'
    df1.loc[df1['gbemamail'] == 'ZLLAYAC@USMP.PEZOILAELENALC@YAHOO.ES',              'gbemamail'] = 'ZLLAYAC@USMP.PE'
    df1.loc[df1['gbemamail'] == 'MAPOLO@MININTER@GOB.PE',                            'gbemamail'] = 'MAPOLO@MININTER.GOB.PE'
    df1.loc[df1['gbemamail'] == 'ALICIASOTO28@HERNANDEZ@GMAIL.COM',                  'gbemamail'] = 'ALICIASOTO28_HERNANDEZ@GMAIL.COM'
    df1.loc[df1['gbemamail'] == 'JULIOC87@PC@HOTMAIL.COM',                           'gbemamail'] = 'JULIOC87_PC@HOTMAIL.COM'
    df1.loc[df1['gbemamail'] == 'JHINOSTROZA@OSINFOR.GOB.PE.JAVIERHUH@HOTMAIL.COM',  'gbemamail'] = 'JHINOSTROZA@OSINFOR.GOB.PE'
    df1.loc[df1['gbemamail'] == 'AORTEGA@CONTRALORIA.GOB.PE.ALEJANDROALMEIDA526@GMAIL.COM', 'gbemamail'] = 'AORTEGA@CONTRALORIA.GOB.PE'
    df1.loc[df1['gbemamail'] == 'NRIVERA@APCI.GOB.PENEL_R27@HOTMAIL.COM',            'gbemamail'] = 'NRIVERA@APCI.GOB.PE'
    df1.loc[df1['gbemamail'] == 'MARY_ZAVALAC@GMAIL.COMC@MAI.COM',                   'gbemamail'] = 'MARY_ZAVALAC@GMAIL.COM'
    df1.loc[df1['gbemamail'] == 'ANGELJODHUABRAVO@1703@GMAIL.COM',                   'gbemamail'] = 'ANGELJODHUABRAVO_1703@GMAIL.COM'
    
    
    ###########################################################################
    df_arrobas = df1[df1['gbemamail'].str.count('@') > 1]
else:
    pass

#%%
if crear_csv == True:
    df1.to_csv(sheet_nombre + '.csv', 
            index    =  False,
            encoding =  'utf-8-sig', #'utf-8',
            header   =  False,
            sep      =  ';')

else:
    print('ñ')

if crear_excel == True:
    df1.to_excel(sheet_nombre + '.xlsx', 
                 index    =  False
                 )