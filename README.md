# balanz_usd_balance
This Script resolve that balanz app displays our growth in USD mep instead of pesos, currency which is impossible to hava as reference.

Step 1: Prerequisites

Make sure you have Python installed on your computer. If not, you can download and install it from the official Python website (https://www.python.org/downloads/).
Step 2: Download the Script

Download the Python script from the source where you found it or copy the entire code into a new Python file (e.g., cedear_analysis.py).
Step 3: Install Required Libraries

The script uses some external libraries that need to be installed before running it. Open your terminal or command prompt and use the following commands:
'''
pip install requests
'''

Step 4: Prepare Input Data

The script expects a CSV file named boletos.csv with the necessary data for processing. The file should have the following columns in the given order: 'Especie', 'Num Boleto', 'Ticker', 'Tipo', 'Concertacion', 'Liquidacion', 'Cantidad', 'Precio', 'Bruto', 'Costos Mercado', 'Arancel', 'Neto', 'Moneda'.

Make sure that boletos.csv is present in the same directory as the Python script and contains the required data.

Step 5: Run the Script

Open your terminal or command prompt, navigate to the directory containing the Python script and the boletos.csv file, and run the following command:
'''
python cedear_analysis.py
'''

Step 6: Review the Results

The script will process the data from the CSV file and provide the results on the terminal. It will display the calculated mep_value for each entry in the CSV file and group the data by 'Ticker', combining the values for the same ticker. The script will also calculate the current USD value for each cedear based on the mep value and display a comparison.
Note: Make sure to review the script and CSV file to ensure that the data format and content match the expected format by the script.

That's it! You've successfully used the Python script to analyze cedears data from the CSV file. If you encounter any issues, please check the input data and ensure you have installed the required libraries correctly.
