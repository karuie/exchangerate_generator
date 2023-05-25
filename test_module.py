import unittest
from unittest.mock import patch
import pandas as pd
from exchangerate_generator.rategenerator import ExchangeRateGenerator
import json

class TestExchangeRateGenerator(unittest.TestCase):
    @patch('requests.get')
    def test_generate_dataframe(self, mock_get):
        # Mock the response from the API
        mock_response = '{"quotes": {"2022-01-01": {"EURGBP": 0.84037, "EURUSD": 1.13715}, "2022-01-02": {"EURGBP": 0.84038, "EURUSD": 1.13716}}}'

        # Set up the mock response
        mock_get.return_value.text = mock_response
        data = json.loads(mock_get.return_value.text)

        # Create an instance of ExchangeRateGenerator
        generator = ExchangeRateGenerator(api_url="https://mock.api.apilayer.com/currency_data/timeframe?start_date=2022-01-01&end_date=2022-01-02&source=EUR", source_currency="EUR")

        # Set up the test data
        date_string_lst = ["2022-01-01", "2022-01-02"]

        # Call the generate_dataframe method
        df = generator.generate_dataframe(data, date_string_lst=date_string_lst, source_currency="EUR")

        # Define the expected DataFrame
        expected_data = {
            "Date": ["2022-01-01", "2022-01-01", "2022-01-02", "2022-01-02"],
            "Source_currency": ["EUR", "EUR", "EUR", "EUR"],
            "Target_currency": ["GBP", "USD", "GBP", "USD"],
            "Exchange_rate": [0.84037, 1.13715, 0.84038, 1.13716]
        }
        expected_df = pd.DataFrame(expected_data)

        # Compare the generated DataFrame with the expected DataFrame
        self.assertTrue(df.equals(expected_df))

if __name__ == '__main__':
    unittest.main()
