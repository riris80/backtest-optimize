# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 15:11:28 2019

@author: HP
"""
#atom test
#import os
#import datetime
#from datetime import date
#import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
#import pandas_datareader as pdr
#import pprint
#import datetime as dtt
#import csv
#import myfilemanagerscript as fms

from backtest import Strategy, Portfolio



class BackToAverageStrategy(Strategy):
    """
    Requires:
    symbol - A stock symbol on which to form a strategy on.
    bars - A DataFrame of bars for the above symbol.
    short_window - Lookback period for short moving average.
    long_window - Lookback period for long moving average."""
    def __init__(self, trade_direction, symbol, bars, profit_tradelimit, loss_tradelimit, short_window=100, long_window=400):
        self.trade_direction = trade_direction
        self.symbol = symbol
        self.bars = bars
        self.short_window = short_window
        self.long_window = long_window
        self.profit_tradelimit = profit_tradelimit
        self.loss_tradelimit = loss_tradelimit

        #self.product_data = product_data
        '''3. self.strategy_identifier - '''

    #return dataframe of signals
    def generate_signals(self):
        self.signals = pd.DataFrame(index=self.bars.index)
        self.signals['sB'] = 0.0
        self.signals['sS'] = 0.0
        self.signals['belowMA'] = 0.0
        self.signals['aboveMA'] = 0.0
        self.signals['diversion'] = 0.0
        self.signals['booltrade'] = 0.0

        self.signals['Close'] = self.bars['CLOSE']
        self.signals['short_mavg'] = self.bars['CLOSE'].rolling(self.short_window,min_periods=1,center=False).mean()


        if self.trade_direction == 'BUY':
            print('IN BUY strategy2')
            ''' Signals to BUY when price below MA and has a certain degree of diversion from the average. When price moves above MA to position is implicitly closed'''

            #1 below MA
            self.signals['belowMA'][self.short_window:] = np.where(self.signals['Close'][self.short_window:] <
            self.signals['short_mavg'][self.short_window:], 1.0, 0.0)
            print('after 1st below')

            #2 Diversion by x
            temptest = self.signals['short_mavg'][self.short_window:]-100
            #2 Diversion by x
            self.signals['diversion'][self.short_window:] = np.where(self.signals['Close'][self.short_window:] <
            self.signals['short_mavg'][self.short_window:]-50, 1.0, 0.0)

            #3 sB
            self.signals['sB'] = ((self.signals['belowMA'] == 1) & (self.signals['diversion'] == 1)).astype(int)
            # ilocs
            self.signals.reset_index(inplace=True)
            countdf = self.signals.index.size
            for row in range(0, countdf):
                if row > 0:
                    if ((self.signals.iloc[row]['sB'] == 0) & (self.signals.iloc[row - 1]['sB'] == 1) & (self.signals.iloc[row]['belowMA'] == 1)):
                        self.signals.loc[row, 'sB'] = 1
                        #pass


            self.signals.set_index('Date', inplace=True)

            #4 Difference it
            self.signals['positionsB'] = self.signals['sB'].diff()

            #5 TradeID
            self.signals['TradeID'] = abs(self.signals['positionsB']).cumsum()
            self.signals['TradeID'] =  self.signals['TradeID']*abs(self.signals['positionsB'])


        else:
            print('IN SELL strategy2')
            '''Signals to SELL when price above MA and has a certain degree of diversion from the average. When price moves above MA to position is implicitly closed'''
            #1 below MA
            self.signals['aboveMA'][self.short_window:] = np.where(self.signals['Close'][self.short_window:] >
            self.signals['short_mavg'][self.short_window:], -1.0, 0.0)
            print('after 1st below')


            #2 Diversion by x
            self.signals['diversion'][self.short_window:] = np.where(self.signals['Close'][self.short_window:] >
            (self.signals['short_mavg'][self.short_window:]+50), -1.0, 0.0)

            #3 sS
            self.signals['sS'] = ((self.signals['aboveMA'] == -1) & (self.signals['diversion'] == -1)).astype(int)
            # ilocs
            self.signals.reset_index(inplace=True)
            countdf = self.signals.index.size
            for row in range(0, countdf):
                if row > 0:
                    if ((self.signals.iloc[row]['sS'] == 0) & (self.signals.iloc[row - 1]['sS'] == 1) & (self.signals.iloc[row]['aboveMA'] == -1)):
                        self.signals.loc[row, 'sS'] = 1



            self.signals.set_index('Date', inplace=True)


            #4 Difference it
            self.signals['positionsS'] = self.signals['sS'].diff()

            #5 TradeID
            self.signals['TradeID'] = abs(self.signals['positionsS']).cumsum()
            self.signals['TradeID'] =  self.signals['TradeID']*abs(self.signals['positionsS'])




        if self.trade_direction == 'BUY':
             ################################################
            '''Following code enables us to see points gained/lossed on each data point (row/date) compared to prior data point'''
            #inTrade (first bracket in following code) is True when enter a position and stays true until and including exit of trade is trigerred
            self.signals['signalsinTradePrice'] = ((self.signals['sB'].abs() + self.signals['positionsB'].abs())!=0)*self.signals['Close']
            self.signals['signalsperCloseP/L'] = (np.subtract(self.signals['signalsinTradePrice'],self.signals['signalsinTradePrice'].shift(1)).where((self.signals['signalsinTradePrice']!=0) & (self.signals['signalsinTradePrice'].shift(1)!=0)).fillna(0))

            '''following code gives us the cumsum of data points while in the trade '''
            '''Also good example of resetting cumsum to zero when zero encountered..'''
            self.signals['signalscumUncrystallized'] = self.signals['signalsperCloseP/L'].cumsum() - self.signals['signalsperCloseP/L'].cumsum().where(self.signals['signalsperCloseP/L'] == 0).ffill().fillna(0)

            '''following code identifies when the strategy is closed and shows crystallizes points gained/lossed'''
            self.signals['signalsboolCrystallization'] = self.signals['positionsB'] < 0
            self.signals['signalscumCrystallized'] = self.signals['signalsboolCrystallization']*self.signals['signalscumUncrystallized']

        else:
            ################################################
            '''Following code enables us to see points gained/lossed on each data point (row/date) compared to prior data point'''
            #inTrade (first bracket in following code) is True when enter a position and stays true until and including exit of trade is trigerred
            self.signals['signalsinTradePrice'] = ((self.signals['sS'].abs() + self.signals['positionsS'].abs())!=0)*self.signals['Close']
            #edo kano allagi theseon
            self.signals['signalsperCloseP/L'] = (np.subtract(self.signals['signalsinTradePrice'].shift(1),self.signals['signalsinTradePrice']).where((self.signals['signalsinTradePrice']!=0) & (self.signals['signalsinTradePrice'].shift(1)!=0)).fillna(0))

            '''following code gives us the cumsum of data points while in the trade '''
            '''Also good example of resetting cumsum to zero when zero encountered..'''
            self.signals['signalscumUncrystallized'] = self.signals['signalsperCloseP/L'].cumsum() - self.signals['signalsperCloseP/L'].cumsum().where(self.signals['signalsperCloseP/L'] == 0).ffill().fillna(0)

            '''following code identifies when the strategy is closed and shows crystallizes points gained/lossed'''
            #self.signals['signalsboolCrystallization'] = self.signals['positionsB'] > 0
            self.signals['signalsboolCrystallization'] = self.signals['positionsS'] > 0
            self.signals['signalscumCrystallized'] = self.signals['signalsboolCrystallization']*self.signals['signalscumUncrystallized']




        return self.signals




class AveragePriceCrossStrategy(Strategy):
    """
    Requires:
    symbol - A stock symbol on which to form a strategy on.
    bars - A DataFrame of bars for the above symbol.
    short_window - Lookback period for short moving average.
    long_window - Lookback period for long moving average."""
    def __init__(self, trade_direction, symbol, bars, profit_tradelimit, loss_tradelimit, short_window=100, long_window=400):
        self.trade_direction = trade_direction
        self.symbol = symbol
        self.bars = bars
        self.short_window = short_window
        self.long_window = long_window
        self.profit_tradelimit = profit_tradelimit
        self.loss_tradelimit = loss_tradelimit

        #self.product_data = product_data
        '''3. self.strategy_identifier - '''

    #return dataframe of signals
    def generate_signals(self):
        self.signals = pd.DataFrame(index=self.bars.index)
        self.signals['sB'] = 0.0
        self.signals['sS'] = 0.0


        self.signals['Close'] = self.bars['CLOSE']
        self.signals['short_mavg'] = self.bars['CLOSE'].rolling(self.short_window,min_periods=1,center=False).mean()


        if self.trade_direction == 'BUY':

            ''' So signal to BUY at Close of current bar when price > shortMA
            signal shows close position at Close of current bar when price < shortMA'''
            self.signals['sB'][self.short_window:] = np.where(self.signals['short_mavg'][self.short_window:] <
            self.signals['Close'][self.short_window:], 1.0, 0.0)

            self.signals['sS'][self.short_window:] = np.where(self.signals['short_mavg'][self.short_window:] >
            self.signals['Close'][self.short_window:], -1.0, 0.0)

            self.signals['positionsB'] = self.signals['sB'].diff()
            self.signals['positionsS'] = self.signals['sS'].diff()

            self.signals['TradeID'] = abs(self.signals['positionsB']).cumsum()
            self.signals['TradeID'] =  self.signals['TradeID']*abs(self.signals['positionsB'])
            #self.signals['ActualTradePrice'] = np.where(self.signals['positionsB']>0, self.signals['positionsB']*self.signals['Close'],0)

        else:
            ''' So signal to SELL at Close of current bar when price > shortMA
            signal shows close position at Close of current bar when price < shortMA'''
            self.signals['sS'][self.short_window:] = np.where(self.signals['short_mavg'][self.short_window:] <
            self.signals['Close'][self.short_window:], -1.0, 0.0)

            self.signals['sB'][self.short_window:] = np.where(self.signals['short_mavg'][self.short_window:] >
            self.signals['Close'][self.short_window:], 1.0, 0.0)



            self.signals['positionsB'] = self.signals['sB'].diff()
            self.signals['positionsS'] = self.signals['sS'].diff()

            self.signals['TradeID'] = abs(self.signals['positionsS']).cumsum()
            self.signals['TradeID'] =  self.signals['TradeID']*abs(self.signals['positionsS'])
            #self.signals['ActualTradePrice'] = np.where(self.signals['positionsB']>0, self.signals['positionsB']*self.signals['Close'],0)


        if self.trade_direction == 'BUY':
             ################################################
            '''Following code enables us to see points gained/lossed on each data point (row/date) compared to prior data point'''
            #inTrade (first bracket in following code) is True when enter a position and stays true until and including exit of trade is trigerred
            self.signals['signalsinTradePrice'] = ((self.signals['sB'].abs() + self.signals['positionsB'].abs())!=0)*self.signals['Close']
            self.signals['signalsperCloseP/L'] = (np.subtract(self.signals['signalsinTradePrice'],self.signals['signalsinTradePrice'].shift(1)).where((self.signals['signalsinTradePrice']!=0) & (self.signals['signalsinTradePrice'].shift(1)!=0)).fillna(0))

            '''following code gives us the cumsum of data points while in the trade '''
            '''Also good example of resetting cumsum to zero when zero encountered..'''
            self.signals['signalscumUncrystallized'] = self.signals['signalsperCloseP/L'].cumsum() - self.signals['signalsperCloseP/L'].cumsum().where(self.signals['signalsperCloseP/L'] == 0).ffill().fillna(0)

            '''following code identifies when the strategy is closed and shows crystallizes points gained/lossed'''
            self.signals['signalsboolCrystallization'] = self.signals['positionsB'] < 0
            self.signals['signalscumCrystallized'] = self.signals['signalsboolCrystallization']*self.signals['signalscumUncrystallized']

        else:
            ################################################
            '''Following code enables us to see points gained/lossed on each data point (row/date) compared to prior data point'''
            #inTrade (first bracket in following code) is True when enter a position and stays true until and including exit of trade is trigerred
            self.signals['signalsinTradePrice'] = ((self.signals['sS'].abs() + self.signals['positionsS'].abs())!=0)*self.signals['Close']
            #edo kano allagi theseon
            self.signals['signalsperCloseP/L'] = (np.subtract(self.signals['signalsinTradePrice'].shift(1),self.signals['signalsinTradePrice']).where((self.signals['signalsinTradePrice']!=0) & (self.signals['signalsinTradePrice'].shift(1)!=0)).fillna(0))

            '''following code gives us the cumsum of data points while in the trade '''
            '''Also good example of resetting cumsum to zero when zero encountered..'''
            self.signals['signalscumUncrystallized'] = self.signals['signalsperCloseP/L'].cumsum() - self.signals['signalsperCloseP/L'].cumsum().where(self.signals['signalsperCloseP/L'] == 0).ffill().fillna(0)

            '''following code identifies when the strategy is closed and shows crystallizes points gained/lossed'''
            self.signals['signalsboolCrystallization'] = self.signals['positionsB'] > 0
            self.signals['signalscumCrystallized'] = self.signals['signalsboolCrystallization']*self.signals['signalscumUncrystallized']




        return self.signals


      #def generate_trades(self):




    """
    def set_signal_attributes(self):
        ################################################
        '''Following code enables us to see points gained/lossed on each data point (row/date) compared to prior data point'''
        #inTrade (first bracket in following code) is True when enter a position and stays true until and including exit of trade is trigerred
        signals['signalsinTradePrice'] = ((signals['sB'].abs() + signals['positionsB'].abs())!=0)*signals['Close']
        signals['signalsperCloseP/L'] = (np.subtract(signals['signalsinTradePrice'],signals['signalsinTradePrice'].shift(1)).where((signals['signalsinTradePrice']!=0) & (signals['signalsinTradePrice'].shift(1)!=0)).fillna(0))

        '''following code gives us the cumsum of data points while in the trade '''
        '''Also good example of resetting cumsum to zero when zero encountered..'''
        signals['signalscumUncrystallized'] = signals['signalsperCloseP/L'].cumsum() - signals['signalsperCloseP/L'].cumsum().where(signals['signalsperCloseP/L'] == 0).ffill().fillna(0)

        '''following code identifies when the strategy is closed and shows crystallizes points gained/lossed'''
        signals['signalsboolCrystallization'] = signals['positionsB'] < 0
        signals['signalscumCrystallized'] = signals['signalsboolCrystallization']*signals['signalscumUncrystallized']

        return signals
    """

    def con_trade(self):

        """Function that takes a Dataframe object representing the signals
        of the no limit strategy modifies the signals to represent a constraint
        strategy with stop loss and target limits stores result in dataframe
        and returns the dataframe to caller"""
        if self.trade_direction == 'BUY':
             character = 'B'
        else:
             character = 'S'


        #'sB', 'sS', 'Close', 'short_mavg', 'positionsB', 'positionsS', 'TradeID'
        if self.trade_direction == 'BUY':
            self.signals.reset_index(inplace=True)
            self.signals['TradeID2'] = abs(self.signals['positionsB']).cumsum()
            #z = (f'positions{character}')
            #print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')

            #dftemp['ST'] = np.where((dftemp['Close']==1401.25) | (dftemp['Close']==1412.50), -1.0, 0.0)
            self.signals['ST'] = np.where((self.signals['signalscumUncrystallized']>=self.profit_tradelimit) | (self.signals['signalscumUncrystallized']<=self.loss_tradelimit), -1.0, 0.0)

            self.signals['modSignals'] = self.signals['sB']
            groupobj = self.signals.groupby('TradeID2')
            grouplist = list(groupobj)

            listsize = len(grouplist)

            '''function to keep only one -1 entry in ST column for each group '''
            for i in range(0,listsize):
                #loc
                #dftemp['ST'] = np.where((dftemp['cumUncrystallized']<tradelimits[i][0]*product_data.multiplier) | (dftemp['cumUncrystallized']>tradelimits[i][1]*product_data.multiplier), -1.0, 0.0)
                loc_result = grouplist[i][1].loc[grouplist[i][1].ST == -1]
                countSTs = loc_result.sB.count()

                if countSTs == 0:
                #print('pass')
                    first_loc_result = grouplist[i][1].index[0]

                    location_last = grouplist[i][1][-1:]

                    location_last_list = list(location_last.index)

                    location_result = location_last_list[0]+1
                    location_result

                    #pass
                else:
                    #print('else')
                    #print(f'loc result: {countSTs}')
                    loc_result_list = list(loc_result.index)
                    first_loc_result = loc_result_list[0]
                    first_loc_result
                    location_last = grouplist[i][1][-1:]
                    location_last_list = list(location_last.index)
                    location_result = location_last_list[0]+1
                    location_result
                    self.signals['modSignals'][first_loc_result:location_result]=0
                    #dftemp.iloc[dftemp.modSignals][first_loc_result:location_result]=0
                    #if I want I can create new column for each time a ST -1 is found
                    #dftemp[f'signalsB'{i}]
            self.signals.set_index('Date',inplace=True)
            self.signals['positionsB'] = self.signals['modSignals'].diff()
            #dftemp['modTradeID'] = abs(dftemp['modSignals'].diff()).cumsum()
            self.signals['modTradeID'] = abs(self.signals['positionsB']).cumsum()
            self.signals['modTradeID'] =  self.signals['modTradeID']*abs(self.signals['positionsB'])
            self.signals['sB'] = self.signals['modSignals']

            self.signals['TradeID'] = self.signals['modTradeID']
            self.signals.drop(['TradeID2', 'ST','modSignals','modTradeID'], axis=1,inplace=True)

            '''Following code enables us to see points gained/lossed on each data point (row/date) compared to prior data point'''
            #inTrade (first bracket in following code) is True when enter a position and stays true until and including exit of trade is trigerred
            self.signals['signalsinTradePrice'] = ((self.signals['sB'].abs() + self.signals['positionsB'].abs())!=0)*self.signals['Close']
            self.signals['signalsperCloseP/L'] = (np.subtract(self.signals['signalsinTradePrice'],self.signals['signalsinTradePrice'].shift(1)).where((self.signals['signalsinTradePrice']!=0) & (self.signals['signalsinTradePrice'].shift(1)!=0)).fillna(0))

            '''following code gives us the cumsum of data points while in the trade '''
            '''Also good example of resetting cumsum to zero when zero encountered..'''
            self.signals['signalscumUncrystallized'] = self.signals['signalsperCloseP/L'].cumsum() - self.signals['signalsperCloseP/L'].cumsum().where(self.signals['signalsperCloseP/L'] == 0).ffill().fillna(0)

            '''following code identifies when the strategy is closed and shows crystallizes points gained/lossed'''
            self.signals['signalsboolCrystallization'] = self.signals['positionsB'] < 0
            self.signals['signalscumCrystallized'] = self.signals['signalsboolCrystallization']*self.signals['signalscumUncrystallized']
        else:
            self.signals.reset_index(inplace=True)
            self.signals['TradeID2'] = abs(self.signals['positionsS']).cumsum()
            #z = (f'positions{character}')
            #print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')

            #dftemp['ST'] = np.where((dftemp['Close']==1401.25) | (dftemp['Close']==1412.50), -1.0, 0.0)
            self.signals['ST'] = np.where((self.signals['signalscumUncrystallized']>=self.profit_tradelimit) | (self.signals['signalscumUncrystallized']<=self.loss_tradelimit), 1.0, 0.0)

            self.signals['modSignals'] = self.signals['sS']
            groupobj = self.signals.groupby('TradeID2')
            grouplist = list(groupobj)

            listsize = len(grouplist)

            '''function to keep only one -1 entry in ST column for each group '''
            for i in range(0,listsize):
                #loc
                #dftemp['ST'] = np.where((dftemp['cumUncrystallized']<tradelimits[i][0]*product_data.multiplier) | (dftemp['cumUncrystallized']>tradelimits[i][1]*product_data.multiplier), -1.0, 0.0)
                loc_result = grouplist[i][1].loc[grouplist[i][1].ST == 1]
                countSTs = loc_result.sS.count()

                if countSTs == 0:
                #print('pass')
                    first_loc_result = grouplist[i][1].index[0]

                    location_last = grouplist[i][1][-1:]

                    location_last_list = list(location_last.index)

                    location_result = location_last_list[0]+1
                    location_result

                    #pass
                else:
                    #print('else')
                    #print(f'loc result: {countSTs}')
                    loc_result_list = list(loc_result.index)
                    first_loc_result = loc_result_list[0]
                    first_loc_result
                    location_last = grouplist[i][1][-1:]
                    location_last_list = list(location_last.index)
                    location_result = location_last_list[0]+1
                    location_result
                    self.signals['modSignals'][first_loc_result:location_result]=0
                    #dftemp.iloc[dftemp.modSignals][first_loc_result:location_result]=0
                    #if I want I can create new column for each time a ST -1 is found
                    #dftemp[f'signalsB'{i}]
            self.signals.set_index('Date',inplace=True)
            self.signals['positionsS'] = self.signals['modSignals'].diff()
            #dftemp['modTradeID'] = abs(dftemp['modSignals'].diff()).cumsum()
            self.signals['modTradeID'] = abs(self.signals['positionsS']).cumsum()
            self.signals['modTradeID'] =  self.signals['modTradeID']*abs(self.signals['positionsS'])
            self.signals['sS'] = self.signals['modSignals']

            self.signals['TradeID'] = self.signals['modTradeID']
            self.signals.drop(['TradeID2', 'ST','modSignals','modTradeID'], axis=1,inplace=True)

            '''Following code enables us to see points gained/lossed on each data point (row/date) compared to prior data point'''
            #inTrade (first bracket in following code) is True when enter a position and stays true until and including exit of trade is trigerred
            self.signals['signalsinTradePrice'] = ((self.signals['sS'].abs() + self.signals['positionsS'].abs())!=0)*self.signals['Close']

            ########################################edo
            self.signals['signalsperCloseP/L'] = (np.subtract(self.signals['signalsinTradePrice'],self.signals['signalsinTradePrice'].shift(1)).where((self.signals['signalsinTradePrice']!=0) & (self.signals['signalsinTradePrice'].shift(1)!=0)).fillna(0))

            '''following code gives us the cumsum of data points while in the trade '''
            '''Also good example of resetting cumsum to zero when zero encountered..'''
            self.signals['signalscumUncrystallized'] = self.signals['signalsperCloseP/L'].cumsum() - self.signals['signalsperCloseP/L'].cumsum().where(self.signals['signalsperCloseP/L'] == 0).ffill().fillna(0)

            '''following code identifies when the strategy is closed and shows crystallizes points gained/lossed'''
            self.signals['signalsboolCrystallization'] = self.signals['positionsS'] > 0
            self.signals['signalscumCrystallized'] = self.signals['signalsboolCrystallization']*self.signals['signalscumUncrystallized']



        return self.signals


class FadeAverage(Strategy):
    pass

#For market portfolio, methods to get the series within the dataframe


class MarketPortfolio(Portfolio):
    """Encapsulates the notion of a portfolio of positions based
    on a set of signals as provided by a Strategy.

    Requires:
    symbol - A stock symbol which forms the basis of the portfolio.
    bars - A DataFrame of bars for a symbol set.
    signals - A pandas DataFrame of signals (1, 0, -1) for each symbol.
    initial_capital - The amount in cash at the start of the portfolio."""

    def __init__(self, trade_direction, symbol, bars, strategyname, strategylimits, signals, initial_capital=100000.0, product_data=[]):

        self. strategyname = strategyname
        self.strategylimits = strategylimits
        self.symbol = symbol
        self.bars = bars
        self.signals = signals
        self.initial_capital = float(initial_capital)
        self.product_data = product_data
        self.positions = self.generate_positions()
        self.value_to_reset = 0
        self.trade_direction = trade_direction

    def generate_positions(self):
        self.positions = pd.DataFrame(index=self.signals.index).fillna(0.0)
        #positions[self.symbol] = 1*dftemp['signal']   # This strategy buys 100 shares




        #old
        self.positions['positionsB'] = 1*self.signals['sB']
        self.positions['positionsS'] = 1*self.signals['sS']
        #print(self.positions['positionsB'][20:60])
        #pprint.pprint(product_data)

        return self.positions


    ########
    #def getstrategyname(self):


    def backtest_portfolio(self):

        self.portfolio = pd.DataFrame(index=self.positions.index).fillna(0.0)



        if self.trade_direction == 'BUY':
            self.portfolio['signalsB'] = self.signals['sB']
            self.portfolio['holdingsB'] = self.positions['positionsB']*self.bars['CLOSE']
            #pos_diff to chech whether there has been a change in a position
            pos_diffB = self.positions['positionsB'].diff()
            ''' positionsB correctly timed with signalsB and shows BUY and close positions'''
            self.portfolio['positionsB'] = pos_diffB
            self.portfolio.positionsB.fillna(0, inplace = True)
        else:
            self.portfolio['signalsS'] = self.signals['sS']
            self.portfolio['holdingsS'] = self.positions['positionsS']*self.bars['CLOSE']
            pos_diffS = self.positions['positionsS'].diff()
            self.portfolio['positionsS'] = pos_diffS
            self.portfolio.positionsS.fillna(0, inplace = True)

        ######################################
        self.portfolio['short_mavg']=self.signals['short_mavg']
        self.portfolio['price'] = self.signals['Close']
        self.portfolio['TradedPrice'] = (self.signals.TradeID > 0)* self.portfolio['price']



        if self.trade_direction == 'BUY':
            self.portfolio['cash'] = self.initial_capital - (pos_diffB*self.bars['CLOSE']).cumsum()
            #self.portfolio['cash_net'] = self.portfolio['cash'] - abs(self.portfolio['positionsB'])*(product_data.Exchange_fee[0]+product_data.Broker_commission[0])
            #self.portfolio['cash_net'] = self.portfolio['cash'] - (abs(self.portfolio['signalsB']))*(product_data.Exchange_fee[0]+product_data.Broker_commission[0])
            self.portfolio['cash_net'] = self.portfolio['cash'] - ((abs(self.portfolio['positionsB']))*(self.product_data.Exchange_fee[0]+self.product_data.Broker_commission[0])).cumsum()


            #self.portfolio['cash'] = self.initial_capital - (pos_diffS['SPY']*self.bars['CLOSE']).cumsum()

            self.portfolio['total'] = self.portfolio['cash'] + self.portfolio['holdingsB']
            self.portfolio['total_net'] = self.portfolio['cash_net'] + self.portfolio['holdingsB']
            #self.portfolio['total'] = self.portfolio['cash'] + self.portfolio['holdingsS']
        else:



            self.portfolio['cash'] = self.initial_capital - (pos_diffS*self.bars['CLOSE']).cumsum()
            #self.portfolio['cash_net'] = self.portfolio['cash'] - abs(self.portfolio['positionsB'])*(product_data.Exchange_fee[0]+product_data.Broker_commission[0])
            #self.portfolio['cash_net'] = self.portfolio['cash'] - (abs(self.portfolio['signalsB']))*(product_data.Exchange_fee[0]+product_data.Broker_commission[0])
            self.portfolio['cash_net'] = self.portfolio['cash'] - ((abs(self.portfolio['positionsS']))*(self.product_data.Exchange_fee[0]+self.product_data.Broker_commission[0])).cumsum()


            #self.portfolio['cash'] = self.initial_capital - (pos_diffS['SPY']*self.bars['CLOSE']).cumsum()

            self.portfolio['total'] = self.portfolio['cash'] + self.portfolio['holdingsS']
            self.portfolio['total_net'] = self.portfolio['cash_net'] + self.portfolio['holdingsS']
            #self.portfolio['total'] = self.portfolio['cash'] + self.portfolio['holdingsS']


        '''
        TRADING
        '''
        if self.trade_direction == 'BUY':
            '''Following code enables us to see points gained/lossed on each data point (row/date) compared to prior data point'''
            #inTrade - True when enter a position and stays true until and including exit of trade is trigerred
            self.portfolio['inTrade'] = (self.portfolio['signalsB'].abs() + self.portfolio['positionsB'].abs())!=0
            self.portfolio['inTradePrice'] = self.portfolio['inTrade']*self.portfolio['price']
            #self.portfolio['perCloseP/L'] = (np.subtract(self.portfolio['inTradePrice'],self.portfolio['inTradePrice'].shift(1)).where((self.portfolio['inTradePrice']!=0) & (self.portfolio['inTradePrice'].shift(1)!=0)).fillna(0))
            self.portfolio['perCloseP/L'] = ((np.subtract(self.portfolio['inTradePrice'],self.portfolio['inTradePrice'].shift(1)).where((self.portfolio['inTradePrice']!=0) & (self.portfolio['inTradePrice'].shift(1)!=0)).fillna(0))/self.product_data.iloc[0].mintick)*self.product_data.iloc[0].multiplier


            #uncrystallized P/L that is P/L on a live position that is currently being held and reset cum count to zero in order to get cumsum per trade
            #self.portfolio['cumUncrystallized'] = self.portfolio['perCloseP/L'].cumsum() - self.portfolio['perCloseP/L'].cumsum().where(self.portfolio['perCloseP/L'] == 0).ffill().fillna(0)
            self.portfolio['cumUncrystallized'] = self.portfolio['perCloseP/L'].cumsum() - self.portfolio['perCloseP/L'].cumsum().where(self.portfolio['perCloseP/L'] == 0).ffill().fillna(0)


            #self.portfolio['boolCrystallization'] = (self.portfolio['cumUncrystallized']!=0) & (self.portfolio['cumUncrystallized'].shift(-1)==0)
            self.portfolio['boolCrystallization'] = self.portfolio['positionsB'] < 0
            self.portfolio['cumCrystallized'] = self.portfolio['boolCrystallization']*self.portfolio['cumUncrystallized']

            #pprint.pprint(product_data.MMargin_DTR)

            marginDeposit = self.product_data.iloc[0].IMargin_DTR
            marginMaintanance = self.product_data.iloc[0].MMargin_DTR
            '''continue from here'''


            ###############
            self.portfolio['MarginAccount'] = marginDeposit*self.portfolio['signalsB']+self.portfolio['signalsB']*self.portfolio['cumUncrystallized']
            self.portfolio['MarginMaintanance'] = marginMaintanance*self.portfolio['signalsB']
            self.portfolio['Margin_call_bool'] = (self.portfolio['signalsB']!=0) & (self.portfolio['MarginAccount'] < self.portfolio['MarginMaintanance'])
            self.portfolio['Variation_Margin'] = self.portfolio['signalsB']*((marginDeposit - self.portfolio['MarginAccount'])*self.portfolio['Margin_call_bool'])
            self.portfolio['Variation_Margin2'] = self.portfolio['signalsB'].shift(+1)*((marginDeposit - self.portfolio['MarginAccount'].shift(+1))*self.portfolio['Margin_call_bool'].shift(+1))

            ''' PROBLEM IN UPDATING MarginAccount with variation margin amount'''


            self.portfolio['cash_Trading'] = self.initial_capital - (pos_diffB*marginDeposit).cumsum() + self.portfolio['cumCrystallized'].cumsum()

            #self.portfolio['ExchangeCosts'] = ((abs(self.portfolio['positionsB']))*(product_data.Exchange_fee[0]+product_data.Broker_commission[0])).cumsum()
            #self.portfolio['cash_net'] = self.portfolio['cash'] - abs(self.portfolio['positionsB'])*(product_data.Exchange_fee[0]+product_data.Broker_commission[0])
            self.portfolio['cash_net_Trading'] = self.portfolio['cash_Trading'] - ((abs(self.portfolio['positionsB']))*(self.product_data.Exchange_fee[0]+self.product_data.Broker_commission[0])).cumsum()


            self.portfolio['strategy'] = self.strategyname
            self.portfolio['Con-strategylimits'] = self.strategylimits

        else:
            '''Following code enables us to see points gained/lossed on each data point (row/date) compared to prior data point'''
            #inTrade - True when enter a position and stays true until and including exit of trade is trigerred
            self.portfolio['inTrade'] = (self.portfolio['signalsS'].abs() + self.portfolio['positionsS'].abs())!=0
            self.portfolio['inTradePrice'] = self.portfolio['inTrade']*self.portfolio['price']
            #self.portfolio['perCloseP/L'] = (np.subtract(self.portfolio['inTradePrice'],self.portfolio['inTradePrice'].shift(1)).where((self.portfolio['inTradePrice']!=0) & (self.portfolio['inTradePrice'].shift(1)!=0)).fillna(0))
            self.portfolio['perCloseP/L'] = ((np.subtract(self.portfolio['inTradePrice'].shift(1),self.portfolio['inTradePrice']).where((self.portfolio['inTradePrice']!=0) & (self.portfolio['inTradePrice'].shift(1)!=0)).fillna(0))/self.product_data.iloc[0].mintick)*self.product_data.iloc[0].multiplier


            #uncrystallized P/L that is P/L on a live position that is currently being held and reset cum count to zero in order to get cumsum per trade
            #self.portfolio['cumUncrystallized'] = self.portfolio['perCloseP/L'].cumsum() - self.portfolio['perCloseP/L'].cumsum().where(self.portfolio['perCloseP/L'] == 0).ffill().fillna(0)
            self.portfolio['cumUncrystallized'] = self.portfolio['perCloseP/L'].cumsum() - self.portfolio['perCloseP/L'].cumsum().where(self.portfolio['perCloseP/L'] == 0).ffill().fillna(0)

            ###########################################################################################
            #self.portfolio['boolCrystallization'] = (self.portfolio['cumUncrystallized']!=0) & (self.portfolio['cumUncrystallized'].shift(-1)==0)
            self.portfolio['boolCrystallization'] = self.portfolio['positionsS'] < 0
            self.portfolio['cumCrystallized'] = self.portfolio['boolCrystallization']*self.portfolio['cumUncrystallized']

            #pprint.pprint(product_data.MMargin_DTR)

            marginDeposit = self.product_data.iloc[0].IMargin_DTR
            marginMaintanance = self.product_data.iloc[0].MMargin_DTR
            '''continue from here'''


            ###############
            '''
            self.portfolio['MarginAccount'] = marginDeposit*self.portfolio['signalsB']+self.portfolio['signalsB']*self.portfolio['cumUncrystallized']
            self.portfolio['MarginMaintanance'] = marginMaintanance*self.portfolio['signalsB']
            self.portfolio['Margin_call_bool'] = (self.portfolio['signalsB']!=0) & (self.portfolio['MarginAccount'] < self.portfolio['MarginMaintanance'])
            self.portfolio['Variation_Margin'] = self.portfolio['signalsB']*((marginDeposit - self.portfolio['MarginAccount'])*self.portfolio['Margin_call_bool'])
            self.portfolio['Variation_Margin2'] = self.portfolio['signalsB'].shift(+1)*((marginDeposit - self.portfolio['MarginAccount'].shift(+1))*self.portfolio['Margin_call_bool'].shift(+1))
            '''
            ''' PROBLEM IN UPDATING MarginAccount with variation margin amount'''



            self.portfolio['cash_Trading'] = self.initial_capital - (pos_diffS*marginDeposit).cumsum() + self.portfolio['cumCrystallized'].cumsum()

            #self.portfolio['ExchangeCosts'] = ((abs(self.portfolio['positionsB']))*(product_data.Exchange_fee[0]+product_data.Broker_commission[0])).cumsum()
            #self.portfolio['cash_net'] = self.portfolio['cash'] - abs(self.portfolio['positionsB'])*(product_data.Exchange_fee[0]+product_data.Broker_commission[0])
            self.portfolio['cash_net_Trading'] = self.portfolio['cash_Trading'] - ((abs(self.portfolio['positionsS']))*(self.product_data.Exchange_fee[0]+self.product_data.Broker_commission[0])).cumsum()


            self.portfolio['strategy'] = self.strategyname
            self.portfolio['Con-strategylimits'] = self.strategylimits

        return self.portfolio
