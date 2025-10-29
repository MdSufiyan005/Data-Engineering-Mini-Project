from datetime import datetime, timedelta
import requests
from typing import Dict, List, Optional

from utils.config import Config

# Client for interacting with the Fixer.io API
class FixerClient:
    

    def __init__(self, api_key: str):
        """Initialize with API key"""
        self.api_key = Config.API_KEY
        self.base_url = "http://data.fixer.io/api"

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        try:
            url = f"{self.base_url}/{endpoint}"
            params = params or {}
            params["access_key"] = self.api_key

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            if not data.get("success"):
                error_info = data.get('error', {})
                error_code = error_info.get('code')
                error_msg = error_info.get('info')
                raise Exception(f"API Error {error_code}: {error_msg}")

            return data
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")

    def fetch_fx_rates(self, target_currencies: List[str] = None, date: str = None) -> Dict:

        # Use timeseries endpoint for historical data
        if date:
            endpoint = date
        else:
            endpoint = "latest"

        params = {
            "access_key": self.api_key,
        }
        
        if target_currencies:
            params["symbols"] = ",".join(target_currencies)

        try:
            data = self._make_request(endpoint, params)
            
            if not data.get("success"):
                raise Exception(f"API Error: {data.get('error', {}).get('info')}")

            return {
                "base_currency": data["base"],
                "timestamp": datetime.fromtimestamp(data["timestamp"]).isoformat(),
                "date": data["date"],
                "rates": data["rates"],
            }
        except Exception as e:
            print(f"Error fetching rates: {str(e)}")
            return None

    def get_available_currencies(self) -> List[str]:
        data = self.fetch_fx_rates()
        return sorted(list(data["rates"].keys()))

    def get_rate_for_currency(
        self, target_currency: str, date: str = None
    ) -> Optional[float]:
        """Get specific exchange rate for a currency pair"""
        data = self.fetch_fx_rates([target_currency.upper()], date)
        return data["rates"].get(target_currency.upper())

    def get_historical_rates(
        self, date: str, target_currencies: List[str] = None
    ) -> Dict:
        
        if not date:
            raise ValueError("Date parameter is required for historical rates")
        return self.fetch_fx_rates(target_currencies, date)

    def get_historical_timeseries(self, start_date: str, end_date: str, target_currencies: List[str]) -> Dict:

        endpoint = "timeseries"
        params = {
            "access_key": self.api_key,
            "start_date": start_date,
            "end_date": end_date,
            "symbols": ",".join(target_currencies)
        }

        try:
            data = self._make_request(endpoint, params)
            if not data.get("success"):
                raise Exception(f"API Error: {data.get('error', {}).get('info')}")
            return data
        except Exception as e:
            print(f"Error fetching historical timeseries: {str(e)}")
            return None

    def get_historical_data(self, start_date: datetime, end_date: datetime, 
                          target_currencies: List[str]) -> List[Dict]:
        historical_data = []
        current_date = start_date

        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            params = {"symbols": ",".join(target_currencies)}
            
            data = self._make_request(date_str, params)
            
            if data and data.get("success"):
                for currency, rate in data["rates"].items():
                    historical_data.append({
                        "currency": currency,
                        "rate": rate,
                        "timestamp": current_date.isoformat()
                    })
            
            current_date += timedelta(days=1)

        return historical_data