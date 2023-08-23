# balanz_usd_balance
This Script resolve that balanz app displays our growth in USD mep instead of pesos, currency which is impossible to hava as reference.

## How to Use
execute as an example this from the folder where you download this repo
> /bin/python3 /balance_boletos.py

pass your "boletos.xlsx" as parameter to get your personal cedears balanz usd summary
> /bin/python3 /balance_boletos.py my_boletos.xlsx


Tabla tiene que tener el siguiente formato  

| Especie | Num Boleto | Ticker | Tipo | Concertacion | Liquidacion | Cantidad |Precio|Bruto|Costos Mercado|Arancel|Neto|Moneda| 
|---------|-----------|---------|------|--------------|-------------| ---------| -----|-----| -------------|-------|---|:-----:|

De los cuales es obligatorio completar

 - 1. ESPECIE (ej CEDEAR COCA COLA COMPANY ESCRIT.)
 - 3. TICKER (ej: KO, TSLA, etc )
 - 4. TIPO (COMPRA, VENTA)
 - 6. LIQUIDACIÓN (formato yyyy-mm-aa, ej:  '2023-07-10)
 - 7. CANTIDAD (nro entero)
 - 12. NETO (ej 62973,92) (seria cantidad x precio_accion + comisiones)
 - 13. MONEDA ('Dólares' o 'Pesos')