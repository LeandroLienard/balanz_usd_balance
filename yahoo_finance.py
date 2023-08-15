import yfinance as yf
from datetime import datetime, timedelta

CLOSE = 'Close'
DAYS_BACK = 4

def format_to_ymd(a_datetime): #recieves a datetime
    return a_datetime.strftime('%Y-%m-%d')

def get_pesos_cedear_value(ticker, a_datetime): #recieves a string ticker and a datetime
    cedear = ticker + '.BA'
    fecha_inicio = a_datetime - timedelta(days= DAYS_BACK)
    fecha_fin = a_datetime + timedelta(days=1)
    fecha_inicio = format_to_ymd(fecha_inicio)
    fecha_fin = format_to_ymd(fecha_fin)
    cedear = yf.download(cedear, fecha_inicio, fecha_fin, progress=False)
    return cedear.tail(1).iloc[0][CLOSE]

def get_current_pesos_cedear_value(ticker):
    return get_pesos_cedear_value(ticker, datetime.now())