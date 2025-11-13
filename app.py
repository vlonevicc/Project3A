import requests
import pygal
from datetime import datetime
from flask import Flask, render_template, request, url_for, redirect, abort

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = '1234'

#Api setup
API_KEY = "6S6GQ8K8UNOSFDJS"
BASE_URL = "https://www.alphavantage.co/query"

@app.route('/', methods=['GET', 'POST'])
def index():
    chart_svg = None
    error = None

    if request.method == 'POST':
        stock_symbol = request.form.get('symbol')
        if not stock_symbol:
            error = "Please enter a stock symbol."
            return render_template('index.html', chart_svg=None, error=error)
        
        stock_symbol = stock_symbol.upper()
        chart_type = request.form.get('chart_type')
        function_choice = request.form.get('function_choice')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        if not start_date or not end_date:
            error = "Please select both start and end dates."
            return render_template('index.html', chart_svg=None, error=error)

        functions = {
                '1': ('TIME_SERIES_INTRADAY', '60min'),
                '2': ('TIME_SERIES_DAILY', None),
                '3': ('TIME_SERIES_WEEKLY', None),
                '4': ('TIME_SERIES_MONTHLY', None)
            }

        function, interval = functions.get(function_choice, ('TIME_SERIES_DAILY', None))

        params = {
            'function': function,
            'symbol': stock_symbol,
            'apikey': API_KEY
        }

        if interval:
            params['interval'] = interval

        print('\nFetching data...')
        try:
            response = requests.get(BASE_URL, params=params) 
            data = response.json() 
            print('Data fetched successfully.')
        except Exception as e:
            error = f"Error fetching data: {e}"
            return render_template('index.html', chart_svg=None, error=error)
        
        if 'Error Message' in data:
            error = "Invalid stock symbol. Please try again."
        else:
            time_series_key = next((key for key in data.keys() if 'Time Series' in key), None)
            if not time_series_key:
                error = "Unexpected data format received from API."
            else:
                time_series_data = data[time_series_key]
                filtered_data = []

                for date_str, values in time_series_data.items():
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').date() if ' ' in date_str else datetime.strptime(date_str, '%Y-%m-%d').date()
                    date_str_short = date_str[:10]  # Extract just the date part
                    if start_date <= date_str_short <= end_date:
                        filtered_data.append((date_obj, float(values['1. open']),
                                      float(values['2. high']), 
                                      float(values['3. low']), 
                                      float(values['4. close'])))
                
                if not filtered_data:
                    error = "No data available for the selected date range."
                else:
                    filtered_data.sort()
                    dates, opens, highs, lows, closes = zip(*filtered_data)

                    if chart_type == 'Line':
                        chart = pygal.Line(x_label_rotation=45)
                        chart.title = f"{stock_symbol} Stock Prices"
                        chart.x_labels = [d.strftime('%Y-%m-%d') for d in dates]
                        chart.add('Open', opens)
                        chart.add('High', highs)
                        chart.add('Low', lows)
                        chart.add('Close', closes)
                    else:
                        chart = pygal.Bar(x_label_rotation=45)
                        chart.title = f"{stock_symbol} Stock Prices"
                        chart.x_labels = [d.strftime('%Y-%m-%d') for d in dates]
                        chart.add('Open', opens)
                        chart.add('High', highs)
                        chart.add('Low', lows)
                        chart.add('Close', closes)

                    chart.x_title = 'Date'
                    chart.y_title = 'Price (USD)'
                    chart_svg = chart.render_data_uri()

    return render_template('index.html', chart_svg=chart_svg, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0')