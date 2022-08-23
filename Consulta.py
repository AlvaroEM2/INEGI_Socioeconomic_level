import webbrowser as web
import pyautogui as pt
import pandas as pd
import time
import pyperclip
import re
import os
import math
import json

def AddressToLocation(address):
    # web.open("https://www.google.com.mx/maps")
    web.open("https://www.google.com")
    coord = []
    p1 = 536, 52  # click to Google search engine
    p2 = 291, 175  # click on maps icon
    p3 = 489, 60  # click to url
    pobs3 = 170, 356  # click to optional directions (in case took us to other country)

    # Start search
    pt.click(p1)
    time.sleep(2)

    pt.typewrite(address)
    pt.hotkey("ENTER")
    time.sleep(5)
    # pt.hotkey("Ctrl", "f")
    # time.sleep(2)
    # pt.typewrite("maps")
    # time.sleep(2)
    # pt.hotkey("Ctrl", "Enter")
    pt.click(p2)
    time.sleep(10)
    pt.click(p3)
    time.sleep(3)
    pt.hotkey("Ctrl", "c")
    a = re.findall("@\d+.\d+,-\d+.\d+", pyperclip.paste())
    try:
        a = re.sub("@", "", a[0])
        coord.append(a)
    except:
        print("1 falla")
        pt.click(pobs3)
        time.sleep(9)
        pt.click(p3)
        time.sleep(3)
        pt.hotkey("Ctrl", "c")
        a = re.findall("@\d+.\d+,-\d+.\d+", pyperclip.paste())
        a = re.sub("@", "", a[0])
        coord.append(a)
    coordinates = coord[0].replace(',', ', ')
    return coordinates

def CodeINEGI(coordinates):
    web.open("http://gaia.inegi.org.mx/mdm-client/?v=bGF0OjIzLjMyMDA4LGxvbjotMTAxLjUwMDAwLHo6MSxsOmMxMTFzZXJ2aWNpb3M=")
    geo_code = []
    p1 = 130, 211  # click to Digital Map search engine
    p2 = 226, 437  # geostatistics code
    pobs3 = 660, 445  # click to optional directions (in case took us to other country)

    # Start search
    time.sleep(5)
    pt.click(p1)
    time.sleep(2)

    pt.typewrite(coordinates)
    pt.hotkey("ENTER")
    time.sleep(5)
    pt.hotkey("ENTER")
    time.sleep(5)
    pt.click(p2)
    # time.sleep(0.5)
    pt.click(p2)
    time.sleep(2)
    pt.hotkey("Ctrl", "c")
    a = pyperclip.paste()
    try:
        geo = int(a)
        geo_code.append(a)
    except:
        print("1 falla")
        pt.click(pobs3)
        time.sleep(9)
        pt.click(p2)
        time.sleep(2)
        pt.click(p2)
        time.sleep(2)
        pt.hotkey("Ctrl", "c")
        a = pyperclip.paste()
        geo = int(a)
        geo_code.append(a)
    return geo_code[0]

def SocioEconmicLevel(geo_code):
    # Clean AGEB code
    AGEB = ''
    if 'A' not in geo_code[9:13]:
        for char in geo_code[9:13]:
            if char != '0':
                break
            else:
                AGEB = AGEB + char
    AGEB = geo_code[9:13].strip(AGEB)

    entidad = geo_code[0:2]
    path = 'INEGI_data_manzanas/conjunto_de_datos_ageb_urbana_' + entidad + '_cpv2020.csv'
    cpv = pd.read_csv(path)
    search = cpv[(cpv['MUN'] == int(geo_code[2:5])) & (cpv['LOC'] == int(geo_code[5:9]))]
    search = search[(search['AGEB'] == AGEB) & (search['MZA'] == int(geo_code[13:16]))]
    # Data cleaning
    search = search.replace('*', 0)
    # Scholar level calculation
    '''
    pob_analfabeta = search['P15YM_AN']
    pob_preescolar = search['P15YM_SE']
    pob_primaria_incompleta = search['P15PRI_IN']
    pob_primaria_completa = search['P15PRI_CO']
    pob_secundaria_incompleta = search['P15SEC_IN']
    pob_secundaria_completa = search['P15SEC_CO']
    pob_posbasica = search['P18YM_PB']
    pob_18mas = search['P_18YMAS']
    pob_15mas = search['P_15YMAS']
    '''
    escolaridad = float(search['GRAPROES'])
    # pob_escolar = int(pob_analfabeta)+int(pob_preescolar)+int(pob_primaria_incompleta)+int(pob_primaria_completa)+int(pob_secundaria_incompleta)+int(pob_secundaria_completa)
    if escolaridad == 0:
        nivel_educativo = 0
    else:
        nivel_educativo = -0.112257 + (2.99372 * escolaridad) - (0.352511 * (escolaridad ** 2)) + (
                    0.025092 * (escolaridad ** 3))

    # Variables for calculations
    viviendas = search['TVIVPARHAB']
    viviendas_bano = search['VPH_EXCSA']  # or search['VPH_DSADMA']
    viviendas_automovil = search['VPH_AUTOM']
    viviendas_internet = search['VPH_INTER']
    viviendas_1dormitorio = search['VPH_1DOR']
    viviendas_2omasdormitorios = search['VPH_2YMASD']
    personas_trabajadoras = search['PEA']

    # Restrooms
    nivel_banos = (int(viviendas_bano) * 47) / int(viviendas)
    # Automobile
    nivel_auto = (int(viviendas_automovil) * 43) / int(viviendas)
    # Internet
    nivel_internet = (int(viviendas_internet) * 32) / int(viviendas)
    # Workers
    empleados = int(personas_trabajadoras) / int(viviendas)
    if empleados == 0:
        nivel_empleados = 0
    elif empleados > 4:
        nivel_empleados = 61
    else:
        nivel_empleados = -0.04286 + (14.86905 * empleados) + (0.42857 * (empleados ** 2)) - (
                    0.08333 * (empleados ** 3))
    # Bedrooms
    nivel_dormitorios = (16 * int(viviendas_1dormitorio) + (32 * int(viviendas_2omasdormitorios))) / int(viviendas)
    if nivel_dormitorios > 32:
        nivel_dormitorios = 32

    # Score
    puntos = nivel_educativo + nivel_banos + nivel_auto + nivel_empleados + nivel_internet + nivel_dormitorios
    if puntos > 201:
        nivel_socioeconomico = 7
    elif puntos > 167:
        nivel_socioeconomico = 6
    elif puntos > 140:
        nivel_socioeconomico = 5
    elif puntos > 115:
        nivel_socioeconomico = 4
    elif puntos > 94:
        nivel_socioeconomico = 3
    elif puntos > 47:
        nivel_socioeconomico = 2
    else:
        nivel_socioeconomico = 1

    return nivel_socioeconomico

# with open('alv.json', encoding='UTF-8') as file:
#     Buro = json.load(file)
# file.close()
#
# city = Buro['consulta']['Personas']['Persona']['Domicilios']['Domicilio'][0]['Ciudad']
# street = Buro['consulta']['Personas']['Persona']['Domicilios']['Domicilio'][0]['Direccion1']
# neighborhood = Buro['consulta']['Personas']['Persona']['Domicilios']['Domicilio'][0]['ColoniaPoblacion']
# country = Buro['consulta']['Personas']['Persona']['Domicilios']['Domicilio'][0]['CodPais']
# CP = Buro['consulta']['Personas']['Persona']['Domicilios']['Domicilio'][0]['CP']
# state = Buro['consulta']['Personas']['Persona']['Domicilios']['Domicilio'][0]['Estado']
# address = street+', '+neighborhood+', '+city+', '+state+', '+country+' '+CP
# print(address)

address = input("Ingrese su dirección: ")

# Start RPA for google maps
coordinates = AddressToLocation(address)
print(coordinates)

# Start RPA for INEGI geostatistics code
geo_code = CodeINEGI(coordinates)
print(geo_code)

# Generate SocioEconmicLevel
nivel_socioeconomico = SocioEconmicLevel(geo_code)
print(nivel_socioeconomico)