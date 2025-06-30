import pandas as pd
import re
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class DateUtils:
    """Utility class for date conversions and formatting."""
    DATE_FORMATS = [
        "%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y", "%Y/%m/%d", "%d/%m/%Y",
        "%m/%d/%Y", "%d.%m.%Y", "%Y.%m.%d", "%d %b %Y", "%b %d, %Y",
        "%B %d, %Y", "%d %B %Y", "%Y-%m-%d %H:%M:%S", "%d-%m-%Y %H:%M:%S"
    ]

    @staticmethod
    def str_to_date(nse_date: str) -> str:
        """Convert '25JAN24' to '2024-01-25'."""
        return datetime.strptime(nse_date, "%d%b%y").strftime("%Y-%m-%d")

    @staticmethod
    def date_to_str(date_str: str) -> str:
        """Convert '01-04-2020' or '2020-01-21' to '01APR20' format."""
        for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%d%b%y").upper()
            except ValueError:
                continue
        raise ValueError(f"Date format not recognized: {date_str}")

    @classmethod
    def format_to_dd_mm_yyyy(cls, date_string):
        for fmt in cls.DATE_FORMATS:
            try:
                parsed_date = datetime.strptime(date_string, fmt)
                return parsed_date.strftime("%d-%m-%Y")
            except ValueError:
                continue
        raise ValueError(f"Unable to parse date string: '{date_string}'. Please use a recognized date format.")

class OptionSymbolParser:
    """Utility class for parsing option symbols."""
    PATTERN = r'^([A-Z]+)(\d{2}[A-Z]{3}\d{2})(\d+(?:\.\d+)?)(CE|PE)\.NFO$'

    @staticmethod
    def split_option_symbol(symbol_str):
        match = re.match(OptionSymbolParser.PATTERN, symbol_str)
        if match:
            return match.groups()
        return (None, None, None, None)

    @staticmethod
    def split_column(df, column_name):
        return df.join(df[column_name].apply(lambda x: pd.Series(OptionSymbolParser.split_option_symbol(x)),
                                             ).rename({0: 'Symbol', 1: 'Expiry', 2: 'Strike', 3: 'OptionType'}, axis=1))

class TradeFileReader:
    """Class for reading and cleaning trade files."""
    @staticmethod
    def read_trade_file(file_path):
        df = pd.read_excel(file_path, sheet_name='Sheet1', header=0)
        df['Type'] = df['Type'].astype('string')
        df['Date/Time'] = df['Date/Time'].astype('string').map(DateUtils.format_to_dd_mm_yyyy)
        df['time'] = df['time'].astype('string')
        df['StringDate'] = df['Date/Time'].map(DateUtils.date_to_str).astype('string')
        df['Price INR'] = df['Price INR'].str.replace(',', '', regex=False).astype(float)
        df['Rounded Price'] = df['Price INR'].round(-2).astype(int)
        df[['Action', 'Trade_Type']] = df['Type'].str.split(expand=True)
        return df

    @staticmethod
    def read_market_file(file_path):
        df = pd.read_csv(file_path)
        df['Ticker'] = df['Ticker'].astype('string')
        df['Date'] = df['Date'].astype('string').map(DateUtils.format_to_dd_mm_yyyy)
        df['Time'] = df['Time'].astype('string')
        df = OptionSymbolParser.split_column(df, 'Ticker')
        return df

class TradeUtils:
    """Utility class for trade filtering, sorting, and validation."""
    @staticmethod
    def get_filtered_sorted_dates(df, symbol, strike, option_type, date_column='Expiry'):
        filtered_df = df[(df['Symbol'] == symbol) & (df['Strike'] == strike) & (df['OptionType'] == option_type)]
        if filtered_df.empty:
            return []
        date_series = pd.to_datetime(filtered_df[date_column], format='%d%b%y', errors='coerce')
        unique_sorted_dates = date_series.dropna().drop_duplicates().sort_values()
        return unique_sorted_dates.dt.strftime('%d%b%y').str.upper().tolist()

    @staticmethod
    def get_closest_dates(date_list, reference_date, top_n=3):
        if not date_list:
            return []
        try:
            ref_datetime = pd.to_datetime(reference_date, format='%d%b%y')
            date_objects = pd.to_datetime(date_list, format='%d%b%y', errors='coerce')
        except ValueError:
            raise ValueError("Invalid date format. Expected format like '02JAN25'")
        valid_dates = date_objects[date_objects >= ref_datetime]
        if valid_dates.empty:
            return []
        time_diffs = (valid_dates - ref_datetime).days
        date_strings = valid_dates.strftime('%d%b%y').str.upper()
        date_diff_df = pd.DataFrame({'date': valid_dates, 'diff_days': time_diffs, 'date_str': date_strings})
        closest_dates = date_diff_df.sort_values('diff_days').head(top_n)
        return closest_dates['date_str'].tolist()

    @staticmethod
    def validate_single_trade(df, trade_number, trade_col='Trade #'):
        trade_data = df[df[trade_col] == trade_number]
        if len(trade_data) == 0:
            return {'valid': False, 'message': f'Trade {trade_number} not found'}
        entry_count = (trade_data['Action'] == 'Entry').sum()
        exit_count = (trade_data['Action'] == 'Exit').sum()
        if entry_count != 1 or exit_count != 1:
            return {
                'valid': False,
                'message': f'Trade {trade_number}: Found {entry_count} entries and {exit_count} exits (expected 1 each)'
            }
        trade_types = trade_data['Trade_Type'].unique()
        if len(trade_types) != 1:
            return {
                'valid': False,
                'message': f'Trade {trade_number}: Mismatched trade types: {list(trade_types)}'
            }
        return {'valid': True, 'message': f'Trade {trade_number} is valid'} 