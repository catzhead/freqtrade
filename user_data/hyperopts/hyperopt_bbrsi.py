# pragma pylint: disable=missing-docstring, invalid-name
# pragma pylint: disable=pointless-string-statement

# --- Do not remove these libs ---
from functools import reduce
from typing import Any, Callable, Dict, List

import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
from skopt.space import Categorical, Dimension, Integer, Real  # noqa

from freqtrade.optimize.hyperopt_interface import IHyperOpt

# --------------------------------
# Add your lib to import here
import talib.abstract as ta  # noqa


class HyperOptBBRSI(IHyperOpt):
    @staticmethod
    def buy_strategy_generator(params: Dict[str, Any]) -> Callable:
        """
        Define the buy strategy parameters to be used by Hyperopt.
        """
        def populate_buy_trend(dataframe: DataFrame, metadata: dict)\
                -> DataFrame:
            """
            Buy strategy Hyperopt will build and use.
            """
            conditions = []

            # GUARDS AND TRENDS
            if 'rsi-enabled' in params and params['rsi-enabled']:
                conditions.append(dataframe['rsi'] < params['rsi-value'])
            if 'mfi-enabled' in params and params['mfi-enabled']:
                conditions.append(dataframe['mfi'] < params['mfi-value'])

            # TRIGGERS
            if 'trigger' in params:
                if params['trigger'] == 'bb_lower1':
                    conditions.append(dataframe['close'] <
                                      dataframe['bb_lowerband1'])
                if params['trigger'] == 'bb_lower2':
                    conditions.append(dataframe['close'] <
                                      dataframe['bb_lowerband2'])
                if params['trigger'] == 'bb_lower3':
                    conditions.append(dataframe['close'] <
                                      dataframe['bb_lowerband3'])

            if conditions:
                dataframe.loc[
                    reduce(lambda x, y: x & y, conditions),
                    'buy'] = 1

            return dataframe

        return populate_buy_trend

    @staticmethod
    def indicator_space() -> List[Dimension]:
        """
        Define your Hyperopt space for searching buy strategy parameters.
        """
        return [
            Integer(20, 50, name='rsi-value'),
            Integer(20, 50, name='mfi-value'),
            Categorical([True, False], name='rsi-enabled'),
            Categorical([True, False], name='mfi-enabled'),
            Categorical(['bb_lower1', 'bb_lower2', 'bb_lower3'],
                        name='trigger')
        ]

    @staticmethod
    def sell_strategy_generator(params: Dict[str, Any]) -> Callable:
        """
        Define the sell strategy parameters to be used by Hyperopt.
        """
        def populate_sell_trend(dataframe: DataFrame, metadata: dict)\
                -> DataFrame:
            """
            Sell strategy Hyperopt will build and use.
            """
            conditions = []

            # GUARDS AND TRENDS
            if 'sell-rsi-enabled' in params and params['sell-rsi-enabled']:
                conditions.append(dataframe['rsi'] > params['sell-rsi-value'])
            if 'sell-mfi-enabled' in params and params['sell-mfi-enabled']:
                conditions.append(dataframe['mfi'] > params['sell-mfi-value'])

            # TRIGGERS
            if 'sell-trigger' in params:
                if params['sell-trigger'] == 'sell-bb_middle':
                    conditions.append(dataframe['close'] >
                                      dataframe['bb_middleband'])
                if params['sell-trigger'] == 'sell-bb_high1':
                    conditions.append(dataframe['close'] >
                                      dataframe['bb_upperband1'])
                if params['sell-trigger'] == 'sell-bb_high2':
                    conditions.append(dataframe['close'] >
                                      dataframe['bb_upperband2'])
                if params['sell-trigger'] == 'sell-bb_high3':
                    conditions.append(dataframe['close'] >
                                      dataframe['bb_upperband3'])

            if conditions:
                dataframe.loc[
                    reduce(lambda x, y: x & y, conditions),
                    'sell'] = 1

            return dataframe

        return populate_sell_trend

    @staticmethod
    def sell_indicator_space() -> List[Dimension]:
        """
        Define your Hyperopt space for searching sell strategy parameters.
        """
        return [
            Integer(50, 100, name='sell-rsi-value'),
            Integer(50, 100, name='sell-mfi-value'),
            Categorical([True, False], name='sell-rsi-enabled'),
            Categorical([True, False], name='sell-mfi-enabled'),
            Categorical(['sell-bb_middle',
                         'sell-bb_high1',
                         'sell-bb_high2',
                         'sell-bb_high3'
                         ],
                        name='sell-trigger')
        ]

    def populate_buy_trend(self,
                           dataframe: DataFrame,
                           metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the buy signal for the given
        dataframe
        :param dataframe: DataFrame populated with indicators
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with buy column
        """
        dataframe.loc[
            (
                (dataframe['close'] < dataframe['bb_lowerband']) &
                (dataframe['rsi'] <= 31)
            ),
            'buy'] = 1

        return dataframe

    def populate_sell_trend(self,
                            dataframe: DataFrame,
                            metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the sell signal for the
        given dataframe
        :param dataframe: DataFrame populated with indicators
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with buy column
        """
        dataframe.loc[
            (
                (dataframe['close'] > dataframe['bb_middleband']) &
                (dataframe['rsi'] >= 56)
            ),
            'sell'] = 1
        return dataframe
