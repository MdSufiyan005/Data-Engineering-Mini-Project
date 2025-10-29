def clean_fx_data(raw_data):
    """
    Cleans and preprocesses the raw foreign exchange rates data.

    Parameters:
    raw_data (dict): The raw data fetched from the Fixer.io API.

    Returns:
    dict: A cleaned dictionary containing the FX rates.
    """
    cleaned_data = {}
    
    # Example of cleaning process
    if 'rates' in raw_data:
        for currency, rate in raw_data['rates'].items():
            cleaned_data[currency] = round(rate, 4)  # Round rates to 4 decimal places

    return cleaned_data

def validate_fx_data(cleaned_data):
    """
    Validates the cleaned foreign exchange rates data.

    Parameters:
    cleaned_data (dict): The cleaned FX rates data.

    Returns:
    bool: True if data is valid, False otherwise.
    """
    return all(isinstance(rate, (int, float)) for rate in cleaned_data.values()) and len(cleaned_data) > 0