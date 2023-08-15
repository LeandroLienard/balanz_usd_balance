import requests
import json
import time
import matplotlib.pyplot as plt
import pandas as pd
import ambito_service as ambito  
import yahoo_finance as yf  


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
MTCGO = 'MTCGO' 
ON = 'ON' 

EPOCH_DAY = 86400 # seconds in a day
DAYS_AGO = 4
# https://www.reddit.com/r/merval/comments/npi3j8/api_con_informaci%C3%B3n_hist%C3%B3rica_de_cedears/
MERVAL_HIST = 'https://analisistecnico.com.ar/services/datafeed/history?symbol={cedear}%3ACEDEAR&resolution=D&from={from_date}&to={to_date}' # dates in epoch
HEADERS = {'Accept': 'application/json'}
payload = {}
    
def es_cedear(ticker):
    return (ticker['Ticker'] != GD30)  & ticker['Especie'].map(is_not_ON, na_action='ignore')  #(ticker['Ticker'] != MTCGO)
         
def is_not_ON(a_string):
    return a_string.split(" ")[0] != ON 

def add_mep_value(ticker):
    date_list = ticker['Liquidacion'].split("-")
    mep_at_day = ambito.get_dolar_mep_at(date_list[0], date_list[1], date_list[2])    
    if(ticker['Moneda'] == 'Dólares'):
        if(ticker['Tipo'] == COMPRA):
            ticker['mep_value'] = ticker['Neto'] #TODO: agregar como seria en pesos y ventas 
        # elif(ticker['Tipo'] == VENTA):
        #     ticker['mep_value'] = -ticker['Neto']
        #     ticker['Cantidad'] = -ticker['Cantidad']
        #     ticker['Neto'] = -ticker['Neto']
    elif(ticker['Moneda'] == 'Pesos'):
        if(ticker['Tipo'] == COMPRA):
            ticker['mep_value'] =  ticker['Neto'] / mep_at_day
        
        # elif(ticker['Tipo'] == VENTA):
        #     ticker['mep_value'] = 
    return ticker

def getEpochToday():
    return time.time()

def getStringToday():
    named_tuple = time.localtime() # get struct_time
    return time.strftime("%Y-%m-%d", named_tuple)

def get_pesos_cedear_value(cedear): # en pesos
    epoch_today= getEpochToday() 
    MERVAL_URL = MERVAL_HIST.format(cedear = cedear, from_date = epoch_today - DAYS_AGO * EPOCH_DAY, to_date = epoch_today)
    response = requests.get(MERVAL_URL, headers=HEADERS,  data=payload)
   # print("cedear ", cedear, " response: ", response.text)
    if response.status_code == 200:
        cotizacion_list = response.text
        cotizacion_json = json.loads(cotizacion_list)
        cedear_value = float(cotizacion_json['o'][-1])
        print("cedear ", cedear, " value: $", cedear_value)
        return cedear_value # devolvemos el ultimo valor entre hoy y 4 dias anteriores de 'c' open
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

archivo = 'boletos.xlsx'

df = pd.read_excel(archivo) #dataframe

print(df.describe)
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
        cedear_update['mep_value'] += cedear['mep_value']
           
        cedears_dict[cedear['Ticker']] = cedear_update


print("Cedears dict: ", cedears_dict)
print(ambito.get_dolar_mep_now())
# mapeear cada objeto. Agregarle un campo de valor en dolares
# con ese campo en dolares + si COMPRA, - si VENTA 
dolar_mep = ambito.get_dolar_mep_now()
print("Ultimo dolar mep: ", dolar_mep)
investment_list = list()
actual_values = 0

for cedear, values in cedears_dict.items():
    investment_list.append( values['mep_value'])
    actual_usd_cedear_value = cedear_usd_value_now(values['Ticker'], values['Cantidad'], dolar_mep)
    actual_values +=  actual_usd_cedear_value
    print(f"{cedear}: {round(values['mep_value'], 2)} vs {round(actual_usd_cedear_value, 2)}")
   
total_invested = sum(investment_list)
print(f"SUMMARY: invested {round(total_invested, 2)} vs actual {round(actual_values,2)}")
print(f"with profit of {round(actual_values-total_invested, 2)} ({round((actual_values*100/total_invested)- 100, 2)}%)")


# list1 = cedears_dict.values()
# list1.map(lambda cedear: cedear['Especie'] )
plt.pie(investment_list, labels = cedears_dict.keys(), autopct="%0.1f %%")
plt.axis("equal")
plt.show()

 
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
