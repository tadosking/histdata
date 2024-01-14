"""
Name:
    loader.py
Description:
    load M1 ASCII free forex data downloaded from histdata.com and convert into specified timeframe.
Author:
    tadosking
Created on:
    2023-01-16
Updated on:
    2024-01-14
"""

import yaml, glob
from datetime import datetime,timedelta
import pandas as pd
import os


class HistdataLoader:
    """
    load M1 ASCII free forex data of histdata.com and convert into specified timeframe.
    raw data must be pre-downloaded from 'histdata.com' and stored into the directory specified in 'config.yaml'.
    """


    def __init__(self, config_path=None):
        """Init.

        :param config_path: to read external configuration file.
        """

        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')

        with open(config_path,'r') as yml :
            config = yaml.safe_load(yml)

        self._HISTDATA_DIR    = config['histdata_dir']
        self._TIMEFRAMES      = config['timeframes']
        self._pre_converted_df = {}


    @staticmethod
    def _is_weekend(d):

        # weekend is ...
        #  - starting from friday 17:00 (N.Y close)
        #  - ending at sunday 17:00 (Wellington open)
        if d.dayofweek == 4 and d.hour >= 17:
            return True
        elif d.dayofweek == 5:
            return True
        elif d.dayofweek == 6 and d.hour < 17:
            return True

        return False


    def _load(self, currency_pair:str) :

        filepaths = glob.glob( os.path.join(self._HISTDATA_DIR, f'DAT_ASCII_{currency_pair}_M1_*.csv') )
        print(filepaths)
        for fp in filepaths :
            print(fp)
        
        # convert csv into pandas.
        columns={'datetime':str, 'open':float, 'high':float, 'low':float, 'close':float, 'volume':float}
        df = (
            pd.concat([ pd.read_csv(fp, sep=';', names=columns.keys(), dtype=columns) for fp in filepaths ])
            .drop_duplicates()
            .assign( datetime = lambda d:d['datetime'].apply( lambda x: datetime.strptime(x, '%Y%m%d %H%M%S') ) )
            .set_index('datetime', drop=True)
            .tz_localize('US/Eastern') 
        )

        # remove weekend data. (middle east rate)
        df = df[~df.index.map( self._is_weekend ).values.astype(bool) ]

        # store for next call.
        self._pre_converted_df.update({ currency_pair: df })
        return df


    def _change_timeframe(self, df, timeframe, origin):

        if origin is None:
            origin = self._TIMEFRAMES[timeframe]['origin']
        origin = pd.Timestamp(origin).tz_localize('US/Eastern')
            
        timedelta_params = { self._TIMEFRAMES[timeframe]['unit']: self._TIMEFRAMES[timeframe]['amount'] }

        df = (
            df
            .resample(timedelta(**timedelta_params), origin=origin)
            .agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last'
            })
        )

        df = df.dropna()  # drop all rows with n/a

        return df

    def load(self,
            currency_pair: str,
            timeframe: str,
            start: str=None, 
            end: str=None,
            timezone: str='US/Eastern') -> pd.DataFrame:
        """Loads histdata 1min parquets and convert to pandas dataframe in selected timeframe.

        :param currency_pair: e.g. 'USDJPY'.
        :param timeframe: e.g. '4h'.
        :param start: will return dataframe starting from 'start'.
                        e.g. '2022-2-7', etc.
        :param end: will return dataframe ending at 'end'.
        :param timezone: returns dataframe in 'timezone', default 'US/Eastern'.
        :return: 'pandas.DataFrame' object.
        """

        if timeframe not in self._TIMEFRAMES.keys() :
            txt = ', '.join(self._TIMEFRAMES.keys())
            raise ValueError(f'please select timeframe from {txt}.')

        try :

            # load original 1min data
            if ( df0 := self._pre_converted_df.get(currency_pair) ) is None :
                df = self._load(currency_pair)
            else : 
                df = df0.copy()

            # change timeframe
            origin = self._TIMEFRAMES[timeframe]['origin']
            df = self._change_timeframe(df, timeframe, origin)

            # change timezone
            df = df.tz_convert(timezone)

            # clip 
            start = pd.to_datetime(start).tz_localize('US/Eastern').tz_convert('Asia/Tokyo')
            end   = pd.to_datetime(end).tz_localize('US/Eastern').tz_convert('Asia/Tokyo')
            df = df.loc[start:end]

        except Exception as e:
            raise e

        return df
    
   
