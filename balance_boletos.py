import requests
import json
import time
import pandas as pd


def getBoleto(fila):
    return { 
        'Especie': fila[0],
        'Num Boleto': fila[1],
        'Ticker': fila[2],
        'Tipo': fila[3],
        'Concertacion': fila[4],
        'Liquidacion': fila[5],
        'Cantidad': int(fila[6]),
        'Precio': fila[7],
        'Bruto': fila[8],
        'Costos Mercado': fila[9],
        'Arancel': fila[10],
        'Neto': fila[11],
        'Moneda': fila[12]
    }

def map_to_object(df):
    boletos = list()
    for index, row in df.iterrows():
        boleto_no_usd = getBoleto(row) 
        boleto_con_usd = add_mep_value(boleto_no_usd)
        boletos.append(boleto_con_usd)
    return boletos

CEDEAR_INSTRUMENT = 'Cedears'
BOLETO = 'Boleto' 
COMPRA = 'COMPRA' 
VENTA = 'VENTA' 
TICKER = 'Ticker'
GD30 = 'GD30' 
EPOCH_DAY = 86400
# AMBITO_MEP_HIST_EJ = 'https://mercados.ambito.com//dolarrava/mep/historico-general/2023-06-22/2023-06-23'
AMBITO_MEP_HIST = 'https://mercados.ambito.com//dolarrava/mep/historico-general/{anio}-{mes}-{dia}/{anio}-{mes}-{dia_sgte}'
# https://www.reddit.com/r/merval/comments/npi3j8/api_con_informaci%C3%B3n_hist%C3%B3rica_de_cedears/
MERVAL_HIST = 'https://analisistecnico.com.ar/services/datafeed/history?symbol={cedear}%3ACEDEAR&resolution=D&from={from_date}&to={to_date}' # dates in epoch
HEADERS = {'Accept': 'application/json'}
payload = {}

def get_dolar_mep(anio, mes, dia):
    cotizacion = get_dolar_mep_request(anio, mes, dia) 
    return cotizacion[-1]
    

def get_dolar_mep_request(anio, mes, dia): # no distingue si recibe '07' ó '7' 
    cotizacion_list = list()
    URL_MEP  = AMBITO_MEP_HIST.format(anio = anio, mes = mes, dia = dia, dia_sgte = int(dia) + 1)
    response = requests.get(URL_MEP, headers=HEADERS,  data=payload)
    print(response.text)
    if response.status_code == 200:
      cotizacion_list = response.text

    return json.loads(cotizacion_list)[-1]
    
def es_cedear(ticker):
    return ticker['Ticker'] != GD30     #TODO: discriminar ONs
        # 'CEDEAR' not in ticker['Especie'] 
         
def add_mep_value(ticker):
    date_list = ticker['Liquidacion'].split("-")
    mep_day = get_dolar_mep(date_list[0], date_list[1], date_list[2])    
    if(ticker['Moneda'] == 'Dólares'):
        ticker['mep_value'] = ticker['Neto'] #TODO: agregar como seria en pesos y ventas 
    # elif(ticker['Moneda'] = 'Pesos'):
        # if(ticker['Tipo'] == COMPRA):
        #     ticker['mep_value'] = 
        # elif(ticker['Tipo'] == VENTA):
        #     ticker['mep_value'] = 
    return ticker

def getEpochToday():
    return time.time()

def getStringToday():
    named_tuple = time.localtime() # get struct_time
    return time.strftime("%Y-%m-%d", named_tuple)

def get_dolar_mep_now():
    today_list = getStringToday().split("-")
    string_mep = get_dolar_mep(today_list[0], today_list[1], int(today_list[2]) - 1) # TODO: fix se rompe cuando va a pedir valor dolar mep un dia [sab, dom y feriados] Tambien a la madrugada
    return convert_to_float(string_mep)

def get_pesos_cedear_value(cedear): # en pesos
    epoch_today= getEpochToday() 
    MERVAL_URL = MERVAL_HIST.format(cedear = cedear, from_date = epoch_today - 4 * EPOCH_DAY, to_date = epoch_today)
    response = requests.get(MERVAL_URL, headers=HEADERS,  data=payload)
   # print("cedear ", cedear, " response: ", response.text)
    if response.status_code == 200:
        cotizacion_list = response.text
        cotizacion_json = json.loads(cotizacion_list)
        cedear_value = float(cotizacion_json['o'][-1])
        print("cedear ", cedear, " value: $", cedear_value)
        return cedear_value # devolvemos el ultimo valor entre hoy y 4 dias anteriores de 'o' open
    else:
        print("Error with cedear: ", cedear, " with reponse: ", response)
        return -1.0
#given a sting with comma decimal format ej: 1,5 -> float
def convert_to_float(string_number):
    correct_format_string_number = string_number.replace(",", ".")
    return float(correct_format_string_number)

def cedear_usd_value_now(cedear, cantidad, dolar_mep_now):
    one_cedear_in_pesos = get_pesos_cedear_value(cedear)
    one_cedear_in_mep = one_cedear_in_pesos / dolar_mep_now 
    return one_cedear_in_mep * cantidad

# ----------------------------------------------------------------------------------------------------- #
# TODO: Hacer que el programa reciba x parametro 

archivo = '/home/leanutn/Documentos/balanz manager/boletos.xlsx'

df = pd.read_excel(archivo) #dataframe

print (df.describe)
cedears_df = df[es_cedear] # filtro solo me quedo con cedears

cedears_list = map_to_object(cedears_df)

#cedears_list = list(filter(es_cedear, boletos_list))


# def gruping_by_tickers(notes):
cedears_dict = {}

for cedear in cedears_list:
    new_boleto_sublist = {}
    if (cedears_dict.get(cedear['Ticker'])  == None):
        #verify if exists "JNJ"? [TICKER
        cedears_dict[cedear['Ticker']] = cedear
        #my_dictionary["tree"] = 3
    else:
        #add to list of existing value
        cedear_update = cedears_dict[cedear['Ticker']]
        
        cedear_update['Cantidad'] += cedear['Cantidad']
        cedear_update['Arancel'] += cedear['Arancel']
        cedear_update['Costos Mercado'] += cedear['Costos Mercado']
        cedear_update['Bruto'] += cedear['Bruto']
        cedear_update['Neto'] += cedear['Neto']
   
        cedears_dict[cedear['Ticker']] = cedear_update


print("Cedears dict: ", cedears_dict)
print(get_dolar_mep_now())
# mapeear cada objeto. Agregarle un campo de valor en dolares
# con ese campo en dolares + si COMPRA, - si VENTA 
dolar_mep = get_dolar_mep_now()

for cedear, values in cedears_dict.items():
    print(f"{cedear}: {values['Neto']} vs {cedear_usd_value_now(values['Ticker'], values['Cantidad'], dolar_mep)}")
# tickers = processTickers(notes)
# print(tickers)
# print('')

# mapeo de tickers a lo que de verdad me interesa
# def es_boleto_venta(ticker):
#     return (BOLETO in ticker['descripcion']) & (COMPRA in ticker['descripcion'])

# def es_cedear(ticker):
#     return (ticker['Ticker'] != GD30

# cedears = list(filter(es_cedear, tickers))

# def pritn_cedears(cedears):
#     for cedear in cedears:
#         print (cedear)   


# pritn_cedears(cedears)
# agrupar por TICKER, dolarizar su cant * importe. Y por ult, sacar comparativa con precio actual 

# la forma de agregar un elemento a una lista sin saber que es una [lista]
# list_no_explicita  + [cedear]
