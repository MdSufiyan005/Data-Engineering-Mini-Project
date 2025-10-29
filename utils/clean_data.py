def clean_fx_data(raw_data):
    cleaned_data = {}
    
    # Example of cleaning process
    if 'rates' in raw_data:
        for currency, rate in raw_data['rates'].items():
            cleaned_data[currency] = round(rate, 4)  # Round rates to 4 decimal places

    return cleaned_data

def validate_fx_data(cleaned_data):

    return all(isinstance(rate, (int, float)) for rate in cleaned_data.values()) and len(cleaned_data) > 0