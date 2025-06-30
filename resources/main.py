import pandas as pd
import re
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

def str_to_date(nse_date: str) -> str:
    """Convert '25JAN24' to '2024-01-25'."""
    return datetime.strptime(nse_date, "%d%b%y").strftime("%Y-%m-%d")

def date_to_str(date_str: str) -> str:
    """Convert '01-04-2020' or '2020-01-21' to '01APR20' format."""
    for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%d%b%y").upper()
        except ValueError:
            continue
    raise ValueError(f"Date format not recognized: {date_str}")

from datetime import datetime

def format_to_dd_mm_yyyy(date_string):

    
    # List of common date formats to try
    date_formats = [
        "%Y-%m-%d",      # 2020-04-07
        "%d-%m-%Y",      # 07-04-2020
        "%m-%d-%Y",      # 04-07-2020
        "%Y/%m/%d",      # 2020/04/07
        "%d/%m/%Y",      # 07/04/2020
        "%m/%d/%Y",      # 04/07/2020
        "%d.%m.%Y",      # 07.04.2020
        "%Y.%m.%d",      # 2020.04.07
        "%d %b %Y",      # 07 Apr 2020
        "%b %d, %Y",     # Apr 07, 2020
        "%B %d, %Y",     # April 07, 2020
        "%d %B %Y",      # 07 April 2020
        "%Y-%m-%d %H:%M:%S",  # 2020-04-07 10:30:00
        "%d-%m-%Y %H:%M:%S",  # 07-04-2020 10:30:00
    ]
    
    # Try each format
    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_string, fmt)
            return parsed_date.strftime("%d-%m-%Y")
        except ValueError:
            continue
    
    # If no format worked, raise an error
    raise ValueError(f"Unable to parse date string: '{date_string}'. Please use a recognized date format.")

def read_tradeFile(file_path):
    #df = pd.read_csv(file_path)
    df = pd.read_excel(file_path, sheet_name='Sheet1', header=0)
    df['Type'] = df['Type'].astype('string')
    df['Date/Time'] = df['Date/Time'].astype('string')
    df['Date/Time'] = df['Date/Time'].apply(format_to_dd_mm_yyyy)
    df['time'] = df['time'].astype('string')
    df['StringDate'] = df['Date/Time'].apply(date_to_str)
    df['StringDate'] = df['StringDate'].astype('string')
    df['Price INR'] = df['Price INR'].str.replace(',', '').astype(float)
    df['Rounded Price'] = df['Price INR'].apply(lambda x: round(x, -2)).astype(int)
    df[['Action', 'Trade_Type']] = df['Type'].str.split(expand=True)
    print(df.dtypes)
    return df
    print(df.dtypes)
    print(df.head(10))


def read_database(file_path):
    df = pd.read_csv(file_path)
    df['Ticker'] = df['Ticker'].astype('string')
    df['Date'] = df['Date'].astype('string')
    df['Date'] = df['Date'].apply(format_to_dd_mm_yyyy)
    df['Time'] = df['Time'].astype('string')
    df = split_column(df, 'Ticker')
    #print(df.dtypes)
    #print(df.head(10))
    return df
    #print(df.dtypes)
    

def split_option_symbol(symbol_str):
    # Define the regex pattern
    pattern = r'^([A-Z]+)(\d{2}[A-Z]{3}\d{2})(\d+(?:\.\d+)?)(CE|PE)\.NFO$'
    
    match = re.match(pattern, symbol_str)
    if match:
        return match.groups()  # Returns a tuple (Symbol, Expiry, Strike, OptionType)
    else:
        return (None, None, None, None)

# Example usage with a DataFrame
def split_column(df, column_name):
    df[['Symbol', 'Expiry', 'Strike', 'OptionType']] = df[column_name].apply(lambda x: pd.Series(split_option_symbol(x)))
    return df

def get_filtered_sorted_dates(df, symbol, strike, option_type, date_column='Expiry'):

    
    # Apply filters based on the three input parameters
    filtered_df = df[
        (df['Symbol'] == symbol) & 
        (df['Strike'] == strike) & 
        (df['OptionType'] == option_type)
    ]
    filtered_df.to_csv('filtered_data.csv', index=False)  # Save filtered data for debugging
    
    # If no data matches the filters, return empty list
    if filtered_df.empty:
        return []
    
    # Convert date strings to datetime for proper sorting
    # Format: %d%b%y (e.g., 02JAN25 = 02-Jan-2025)
    date_series = pd.to_datetime(filtered_df[date_column], format='%d%b%y')
    
    # Get unique dates, sort them, and convert back to original string format
    unique_sorted_dates = date_series.drop_duplicates().sort_values()
    
    # Convert back to original string format
    date_strings = unique_sorted_dates.dt.strftime('%d%b%y').str.upper()
    
    return date_strings.tolist()

def get_closest_dates(date_list, reference_date, top_n=3):

    
    # Return empty list if input is empty
    if not date_list:
        return []
    
    # Convert reference date to datetime
    try:
        ref_datetime = pd.to_datetime(reference_date, format='%d%b%y')
    except ValueError:
        raise ValueError(f"Invalid reference date format: {reference_date}. Expected format like '02JAN25'")
    
    # Convert all dates in the list to datetime
    try:
        date_objects = pd.to_datetime(date_list, format='%d%b%y')
    except ValueError:
        raise ValueError("Invalid date format in date_list. Expected format like '02JAN25'")
    
    # Filter dates that are equal to or after the reference date
    valid_dates = date_objects[date_objects >= ref_datetime]
    
    # If no valid dates found, return empty list
    if valid_dates.empty:
        return []
    
    # Calculate time differences (in days) from reference date
    time_diffs = (valid_dates - ref_datetime).days
    
    # Convert valid dates back to string format
    date_strings = valid_dates.strftime('%d%b%y').str.upper()
    
    # Create a DataFrame to pair dates with their differences
    date_diff_df = pd.DataFrame({
        'date': valid_dates,
        'diff_days': time_diffs,
        'date_str': date_strings
    })
    
    # Sort by difference (closest first) and get top N
    closest_dates = date_diff_df.sort_values('diff_days').head(top_n)
    
    return closest_dates['date_str'].tolist()

def validate_single_trade(df, trade_number, trade_col='Trade #'):

    
    # Filter for the specific trade
    trade_data = df[df[trade_col] == trade_number]
    
    if len(trade_data) == 0:
        return {'valid': False, 'message': f'Trade {trade_number} not found'}
    
    # Count entries and exits
    entry_count = (trade_data['Action'] == 'Entry').sum()
    exit_count = (trade_data['Action'] == 'Exit').sum()
    
    # Check counts
    if entry_count != 1 or exit_count != 1:
        return {
            'valid': False, 
            'message': f'Trade {trade_number}: Found {entry_count} entries and {exit_count} exits (expected 1 each)'
        }
    
    # Check if trade types match
    trade_types = trade_data['Trade_Type'].unique()
    if len(trade_types) != 1:
        return {
            'valid': False,
            'message': f'Trade {trade_number}: Mismatched trade types: {list(trade_types)}'
        }
    
    return {
        'valid': True,
        'message': f'Trade {trade_number}: Valid ({trade_types[0]})'
    }

def main():
    trade_db_df = read_tradeFile(r'E:\trades 1.xlsx')
    base_path = r'E:\Database'
    print(trade_db_df.head(10))

    number_of_trades = trade_db_df['Trade #'].max()
    #number_of_trades + 1
    for i in range(1, number_of_trades + 1):
        try:
            trade_check = validate_single_trade(trade_db_df, i)

            if trade_check['valid']:
                # GET THE ROW NUMBER ON WHICH THE TRADE IS ENTERED
                row_number = trade_db_df[(trade_db_df['Trade #'] == i) & (trade_db_df['Action'] == 'Entry')].index[0]

                # COMPLETING THE ENTRY TRADE DETAILS
                # CREATING THE FILE NAME BASED ON THE TRADE DATE
                trade_type = trade_db_df.loc[row_number, 'Trade_Type']
                trade_date = trade_db_df.loc[row_number, 'Date/Time']
                trade_time = (datetime.strptime(trade_db_df.loc[row_number, 'time'], "%H:%M:%S") - timedelta(seconds=1)).strftime("%H:%M:%S")
                option_type = 'CE' if trade_type == 'short' else 'PE'
                strike_price = trade_db_df.loc[row_number, 'Rounded Price']
                parsed_date = datetime.strptime(trade_date, "%d-%m-%Y")
                file_name = f'{parsed_date.strftime("%Y")}/{parsed_date.strftime("%b_%Y").upper()}/GFDLNFO_OPTIONS_{parsed_date.strftime("%d%m%Y")}.csv'            
                path = os.path.join(base_path, *file_name.split('/'))
                #print(f"{path}")
                database_df = read_database(path)

                #dates = get_filtered_sorted_dates(database_df, 'NIFTY', str(strike_price), option_type)
                dates = database_df['Expiry'].unique().tolist()
                date_series = pd.to_datetime(dates, format='%d%b%y')
                sorted_dates = date_series.sort_values()
                sorted_date_list = sorted_dates.strftime('%d%b%y').tolist()

                trade_db_df.loc[row_number, 'ExpiryDates'] = ', '.join(sorted_date_list)
                print(sorted_date_list)
                expiry_dates = get_closest_dates(dates, trade_db_df.loc[row_number, 'StringDate'], top_n=4)
                trade_db_df.loc[row_number, 'ExpiryDates1'] = ', '.join(expiry_dates)
                print(expiry_dates)

                for j in range(1, 5):
                    for k in range(-1500, 1600, 100):
                        colname = f"Expiry{j} - ATM {k}"
                        result = database_df[
                        (database_df['Ticker'] == f"NIFTY{expiry_dates[j-1]}{strike_price+k}{option_type}.NFO") & 
                        (database_df['Date'] == trade_date) & 
                        (database_df['Time'] == trade_time)]['Low']
                        if len(result) > 0 & len(result) < 2:
                            trade_db_df.loc[row_number, colname] = result.iloc[0]
                        else:
                            #trade_db_df.loc[row_number, colname] = f"NIFTY{expiry_dates[j-1]}{strike_price+i}{option_type}.NFO  {trade_date}-{trade_time}"
                            trade_db_df.loc[row_number, colname] = None

                row_number = trade_db_df[(trade_db_df['Trade #'] == i) & (trade_db_df['Action'] == 'Exit')].index[0]
                trade_date = trade_db_df.loc[row_number, 'Date/Time']
                trade_time = (datetime.strptime(trade_db_df.loc[row_number, 'time'], "%H:%M:%S") - timedelta(seconds=1)).strftime("%H:%M:%S")
                parsed_date = datetime.strptime(trade_date, "%d-%m-%Y")
                file_name = f'{parsed_date.strftime("%Y")}/{parsed_date.strftime("%b_%Y").upper()}/GFDLNFO_OPTIONS_{parsed_date.strftime("%d%m%Y")}.csv'
                path = os.path.join(base_path, *file_name.split('/'))
                print(f"{path}")
                database_df = read_database(path)

                trade_db_df.loc[row_number, 'ExpiryDates'] = ', '.join(sorted_date_list)
                print(sorted_date_list)
                trade_db_df.loc[row_number, 'ExpiryDates1'] = ', '.join(expiry_dates)
                print(expiry_dates)

                for j in range(1, 5):
                    for k in range(-1500, 1600, 100):
                        colname = f"Expiry{j} - ATM {k}"
                        result = database_df[
                        (database_df['Ticker'] == f"NIFTY{expiry_dates[j-1]}{strike_price+k}{option_type}.NFO") & 
                        (database_df['Date'] == trade_date) & 
                        (database_df['Time'] == trade_time)]['High']
                        if len(result) > 0 & len(result) < 2:
                            trade_db_df.loc[row_number, colname] = result.iloc[0]
                        else:
                            #trade_db_df.loc[row_number, colname] = f"NIFTY{expiry_dates[j-1]}{strike_price+i}{option_type}.NFO  {trade_date}-{trade_time}"
                            trade_db_df.loc[row_number, colname] = None
        except Exception as e:
            print(f"Error processing trade {i}: {e}")
            continue

    #print(trade_db_df.head(10))
    trade_db_df.to_csv(r'E:\Freelance work\15 - Harish backtest python script\trades 1_updated.csv', index=False)

    

if __name__ == "__main__":
    main()
    #read_tradeFile(r'E:\Freelance work\15 - Harish backtest python script\trades 1.xlsx')