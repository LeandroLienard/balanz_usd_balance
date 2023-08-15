import requests
import json
import time
import datetime
import matplotlib.pyplot as plt
import pandas as pd

COMPRA = 'COMPRA' 
VENTA = 'VENTA' 
EPOCH_DAY = 86400 # seconds in a day
DAYS_AGO = 4
# AMBITO_MEP_HIST_EJ = 'https://mercados.ambito.com//dolarrava/mep/historico-general/2023-06-22/2023-06-23'
AMBITO_MEP_HIST = 'https://mercados.ambito.com//dolarrava/mep/historico-general/{from_date}/{to_date}'
# https://www.reddit.com/r/merval/comments/npi3j8/api_con_informaci%C3%B3n_hist%C3%B3rica_de_cedears/
HEADERS = {'Accept': 'application/json'}
payload = {}

def get_dolar_mep(anio, mes, dia):
    cotizacion = get_dolar_mep_request(anio, mes, dia) 
    return convert_to_float(cotizacion[-1])
        

def get_dolar_mep_request(anio, mes, dia): # no discrimina si recibe '07' ó '7' 
    to_date = datetime.datetime(int(anio), int(mes), int(dia) + 1) # TODO: poner un mas 2 y cambiar la api de los cedears
    # pedimos cotizacion de hoy a 4 dias atras porque el mep opera de lun-viernes no feriados
    from_date = getNDaysAgoDate(to_date, DAYS_AGO)    
    URL_MEP  = AMBITO_MEP_HIST.format(from_date = from_date, to_date = to_date.date()) 
    response = requests.get(URL_MEP, headers=HEADERS,  data=payload)
    
    print(response.text)
    if response.status_code == 200:
      cotizacion_list = response.text
    return json.loads(cotizacion_list)[1] #quedamos el 1 porque [["Fecha","Referencia"],["26\/07\/2023","503,90"],["25\/07\/2023","507,12"]
    

def add_mep_value(ticker):
    date_list = ticker['Liquidacion'].split("-")
    mep_at_day = get_dolar_mep(date_list[0], date_list[1], date_list[2])    
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



def getStringToday():
    named_tuple = time.localtime() # get struct_time
    return time.strftime("%Y-%m-%d", named_tuple)

def get_tomorrow(a_date): # datetime should be a datetime
    next_days = datetime.timedelta(days = 1)
    return (a_date - next_days).date()

def getNDaysAgoDate(a_date, n): # datetime should be a datetime
    daysAgo = datetime.timedelta(days = n)
    return (a_date - daysAgo).date()

def get_dolar_mep_now():
    today_list = getStringToday().split("-")
    return get_dolar_mep(today_list[0], today_list[1], int(today_list[2]))

#given a sting with comma decimal format ej: 1,5 -> float
def convert_to_float(string_number):
    correct_format_string_number = string_number.replace(",", ".")
    return float(correct_format_string_number)

# ----------------------------------------------------------------------------------------------------- #
