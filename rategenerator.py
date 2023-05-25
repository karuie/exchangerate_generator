import requests
import json
import pandas as pd
from environs import Env
from datetime import date, timedelta
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class ExchangeRateGenerator:
    def __init__(self, api_url,source_currency):
        self.api_url = api_url
        self.source_currency = source_currency
        self.data = None

    def fetch_exchange_rates(self):
        env = Env()
        env.read_env('credential.env')
        api_key = env("API_KEY")
        if api_key is None:
            print("API key not found.")
            return None

        headers = {"apikey": api_key}

        # Define retry strategy for rate limiting
        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[429])
        adapter = HTTPAdapter(max_retries=retries)
        session = requests.Session()
        session.mount("https://", adapter)

        response = requests.get(self.api_url, headers=headers)

        if response.status_code != 200:
            # Handle the API error here
            print("Error occurred while fetching exchange rates.")
            return None

        result = response.text
        data = json.loads(result)
        return data



    def generate_dataframe(self, data, date_string_lst, source_currency):
        if data is None or "quotes" not in data:
            # Handle the missing or invalid data
            return None

        quotes = data["quotes"]

        data_list = []

        for date in date_string_lst:
            quotes_each_day = quotes[date]

            if source_currency == "GBP":
                first_two_target_currencies = ["USD", "EUR"]
            elif source_currency == "USD":
                first_two_target_currencies = ["GBP", "EUR"]
            elif source_currency == "EUR":
                first_two_target_currencies = ["GBP", "USD"]
            # set default
            else:
                first_two_target_currencies = ["GBP", "USD"]

            combined_currency_arr = []

            for first_two_target_currency in first_two_target_currencies:
                combined_currency = f"{source_currency}{first_two_target_currency}"
                combined_currency_arr.append(combined_currency)


                try:
                    exchange_rate = quotes_each_day[combined_currency]
                except KeyError:
                    # Handle the KeyError here
                    exchange_rate = None

                data_list.append(
                    {
                        "Date": date,
                        "Source_currency": source_currency,
                        "Target_currency": first_two_target_currency,
                        "Exchange_rate": exchange_rate,
                    }
                )

            # Iterate over other target currencies
            for target_currency in quotes_each_day:
                if target_currency not in combined_currency_arr:
                    exchange_rate = quotes_each_day[target_currency]
                    target_currency = target_currency.replace(f"{source_currency}", "")
                    data_list.append(
                        {
                            "Date": date,
                            "Source_currency": source_currency,
                            "Target_currency": target_currency,
                            "Exchange_rate": exchange_rate,
                        }
                    )
                else:
                    pass

        df_initial = pd.DataFrame(data_list)
        return df_initial

    def run(self):
        data = self.fetch_exchange_rates()

        start_date = date(2022, 1, 1)
        end_date = date(2023, 1, 1)

        delta = timedelta(days=1)
        current_date = start_date

        date_string_lst = []

        while current_date <= end_date:
            date_string = current_date.strftime("%Y-%m-%d")
            date_string_lst.append(date_string)
            current_date += delta

        df = self.generate_dataframe(data, date_string_lst, self.source_currency)
        print(f"Exchange rates for {self.source_currency}:")
        print(df)
        return df

    def run(self):
        data = self.fetch_exchange_rates()

        start_date = date(2022, 1, 1)
        end_date = date(2023, 1, 1)

        delta = timedelta(days=1)
        current_date = start_date

        date_string_lst = []

        while current_date <= end_date:
            date_string = current_date.strftime("%Y-%m-%d")
            date_string_lst.append(date_string)
            current_date += delta

        df = self.generate_dataframe(data, date_string_lst, self.source_currency)
        print(f"Exchange rates for {self.source_currency}:")
        print(df)
        return df

def main():

    for source_currency in ["GBP", "USD", "EUR"]:
        api_url_template =  "https://api.apilayer.com/currency_data/timeframe?start_date=2022-01-01&end_date=2023-01-01&source={source_currency}"
        api_url = api_url_template.format(source_currency=source_currency)
        generator = ExchangeRateGenerator(api_url, source_currency=source_currency)
        df = generator.run()
        # Convert DataFrame to CSV
        df.to_csv(f'output_{source_currency}.csv', index=False)

if __name__ == "__main__":
    main()