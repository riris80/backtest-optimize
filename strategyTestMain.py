# -*- coding: utf-8 -*-
"""
Created on Thu Dec 10 11:20:47 2020

@author: HP
"""

import myfilemanagerscript as fms
import pandas as pd
import price_cross_10122020_CV as tstrat
import strategyResultsVisualisations as srv
from strategyStats import StrategyPerformance
from tkinter import *
import math
# ---------------------------- CONSTANTS ------------------------------- #
PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
FONT_NAME = "Courier"
WORK_MIN = 0.2
SHORT_BREAK_MIN = 0.1
LONG_BREAK_MIN = 0.2
reps = 0
timer = None



if __name__ == "__main__":

    #Initialize environment
    #If csv excel portfolios already saved in folder then just delete to create new portfolio csv files
    csvfilename = 'Portfolio'
    entriesfound = fms.countFileEntries(csvfilename)
    print(f'in main found xxxxxxxxxxxxxx {entriesfound} portfolios!!!')
    fms.deleteFileEntries(entriesfound, csvfilename)
    
    #Will be client input and possible GUI
    #Select strategy
    #Get csv data
    symbol = 'SPY'
    df = pd.read_csv('EPDailyData_temp2.csv')
    bars = df
    bars["Date"] = pd.to_datetime(bars["Date"])
    bars.index = bars.Date
    '''Get product data for margins, fees etc'''
    product_data = pd.read_csv('Trading Products.csv')
    #will select strategy from a choice of strategies
    
    
    
    #Initial strategy input
    initial_capital = 10000
    short_window = 25
    long_window=100
    margin=0.1
    optimization = False
    trade_direction = 'SELL'
    #strategy_selection = 'AveragePriceCrossStrategy'
    
    
     
    #User selecrs a simple test ie no optimization
    if optimization == False:
        print('STANDALONE')
        apc = tstrat.BackToAverageStrategy(trade_direction, symbol, bars, 0, 0, short_window, long_window)
        #apc = tstrat.AveragePriceCrossStrategy(trade_direction, symbol, bars, 0, 0, short_window, long_window)
        signals = apc.generate_signals()
        portfolio = tstrat.MarketPortfolio(trade_direction, symbol, bars, 'standalone', 'standalone', signals, initial_capital, product_data) 
        returns = portfolio.generate_positions()
        returns = portfolio.backtest_portfolio()
        returns.to_csv('Portfolio0.csv')
        signals.to_csv('SelltestNew.csv')
        #returns.to_csv('ReturnsNew.csv')
        
        srv.getVisualization(ma=short_window)
    
        ###################Portfolio Stats!#####################################################
        '''Gather the list of '''
        portfoliolist = list()
        #initial_capital = 10000
        portfolioentries = fms.countFileEntries('Portfolio')
        #trade_direction = 'BUY'
        for i in range(0,portfolioentries):
            portfolio = pd.read_csv(f'Portfolio{i}.csv')
            portfoliolist.append(portfolio)
        
        #trying to make code better
        attribution = StrategyPerformance(portfoliolist,0.02, initial_capital,trade_direction)
        stats=attribution.generate_stats()
        for item in range(len(stats)):
            print('\n')  
            for key, value in stats[item].items():  
                print(key, ' : ', value)
        
        #########################################################################################
    
    
    #User selects to Optimize strategy 
    else:
        print('OPTIMIZE')
        start_shortMA = short_window
        start_longMA = long_window
        increment = 25
        mindifference = 50
        end_longMA=100    
        
        if end_longMA < start_longMA:
            end_longMA = start_longMA+increment
        
        tradelimits = [[2.0,-4.0],[15.0,-20.0]]
        
        #portfolio list initialisations
        unc_portfoliolist = list()
        con_portfoliolist = list()
        comp_portfoliolist = list()
        signals_list = list()
        portfolio_list = list()
        
        #################Check how many strategies we expect from the above inputs
        exp_constrategies = 0
        exp_unconstrategies = 0
        if (end_longMA - start_longMA) == 0:
            exp_constrategies = len(tradelimits)*((start_longMA-mindifference)/increment)     
            exp_unconstrategies = (start_longMA-mindifference)/increment
        else:    
            for i in range(0, int((end_longMA-start_longMA)/increment)+1):
                exp_constrategies = exp_constrategies + ((i*increment+start_longMA-mindifference)/increment)*len(tradelimits)
                exp_unconstrategies = exp_unconstrategies + ((i*increment+start_longMA-mindifference)/increment)
        
        
        exp_totstrategies = exp_constrategies + exp_unconstrategies
        
        print(f'....exp_unc: {exp_unconstrategies}')
        print(f'....exp_con: {exp_constrategies}')
        print(f'....exp_tot: {exp_totstrategies}')
        
        
        ##################################Run optimization
        countunconstraint = 0
        '''While loop is not entered when x > end_longMA'''
        while long_window <= end_longMA:
            '''if statement required to keep the amount difference between short and long MAs'''
            if long_window-short_window >= mindifference:
                '''1. Need an  array of signals to send to marketportfolio object'''
                profit_tradelimit = 0
                loss_tradelimit = 0
                
                if countunconstraint < exp_unconstrategies:
                    countunconstraint = countunconstraint + 1
                    '''create strategy name column in returns dataframe'''
                    strategyname = 'strat {},{}'.format(short_window, long_window)
                    strategylimits = 'strat {},{}'.format(0, 0)
                    
                    '''Generate signals containing crystallized and uncrystallized points etc...'''
                    apc = tstrat.AveragePriceCrossStrategy(trade_direction, symbol, bars, profit_tradelimit, loss_tradelimit, short_window, long_window)
                    signals = apc.generate_signals()
                    signals_list.append(signals)
                    
                    #print(f'id signals main {id(signals)}')
                    
                    '''Generate portfolio containing cash, crystallized and uncrystallized values etc...'''
                    
                    portfolio = tstrat.MarketPortfolio(trade_direction, symbol, bars, strategyname, strategylimits, signals, initial_capital, product_data) 
                    returns = portfolio.generate_positions()
                    returns = portfolio.backtest_portfolio()
                    
                    #print(f'....returns: {id(returns)}')
                    
                    '''append unconstraint return to a list of dataframes of unconstraint returns'''
                    unc_portfoliolist.append(returns)
                    comp_portfoliolist.append(returns)        
                    #unc_portfoliolist[0].to_csv('P1.csv')
                    #returns.to_csv('R.csv')
                else:
                    pass
                
                for i in range(0, len(tradelimits)):
                    #print(f'top short window: {short_window}')
                    #print(f'top long window: {long_window}')
                    profit_tradelimit = tradelimits[i][0]
                    loss_tradelimit = tradelimits[i][1]
                    strategyname = 'strat {},{}'.format(short_window, long_window)
                    strategylimits = 'strat {},{}'.format(tradelimits[i][0], tradelimits[i][1])
                    
                    apcx = tstrat.AveragePriceCrossStrategy(trade_direction, symbol, bars, tradelimits[i][0], tradelimits[i][1], short_window, long_window)
                    signalsx = apcx.generate_signals()
                    signalsx = apcx.con_trade()
                    signals_list.append(signalsx)
                    #print(f'id of signalsx.........{id(signalsx)}')
                    #print(f'signalsx iloc {signalsx.short_mavg.iloc[25]}')
                    
                    #print(f'before obj short window: {short_window}')
                    #print(f'before obj long window: {long_window}')
                    portfoliox = tstrat.MarketPortfolio(trade_direction, symbol, bars, strategyname, strategylimits, signalsx, initial_capital, product_data) 
                    #portfoliox = MarketPortfolio(symbol, bars, strategyname, strategylimits, signalsx, initial_capital, product_data) 
                    #returnsx = portfoliox.generate_positions()
                    returnsx = portfoliox.backtest_portfolio()
                    #print(f'....{i+1}st iteration portfolio_list: {id(returnsx)}')
                    #print(f'after obj short window: {short_window}')
                    #print(f'after obj long window: {long_window}')
                    portfolio_list.append(returnsx)
                    
                    con_portfoliolist.append(returnsx)
                    comp_portfoliolist.append(returnsx) 
                    
                    #returnsx.to_csv(f'R{i+1}.csv')
                
                #portfoliolist = con_portfoliolist
                portfoliolist = comp_portfoliolist
                
                #for i in portfoliolist:
                    #portfoliolist[i].to_csv(f'PP{i}.csv')
                
                #portfoliolist[0].to_csv('Test2.csv')
                #attribution = StrategyPerformance(symbol, bars,portfoliolist,0.02, initial_capital)
                #attribution = StrategyPerformance(symbol, bars,returns,0.02, initial_capital)
                #stats=attribution.generate_stats()
                #print(f'stats: {stats}')
                #con_portfoliolist[0].to_csv('Test3.csv')
                short_window = short_window + increment
        
            else:
                short_window = start_shortMA
                long_window = long_window + increment
        #######################################################################
                
        
        """
        ########################write complete portfolio list to csv
        
        """
        for i in range(len(comp_portfoliolist)):
            comp_portfoliolist[i].to_csv(f'Portfolio{i}.csv')
        
        print(f'number of strategies = {len(portfoliolist)}')
        print(f'....number of con_strategies = {len(con_portfoliolist)}')
        print(f'....number of uncon_strategies = {len(unc_portfoliolist)}')
        
        #OPTIMIZATION sanity CHECK
        #Ensuring that strategies in actual portfolio lists are 
        #equal to how many strategies should actually be
        if len(portfoliolist) != exp_totstrategies:
            raise TypeError(f'unequal number of total strategies. Expected {exp_totstrategies} vs actual in portfoliolist {len(portfoliolist)}')
        if len(con_portfoliolist) != exp_constrategies:
            raise TypeError(f'unequal number of constricted strategies. Expected {exp_constrategies} vs actual in con_portfoliolist {len(con_portfoliolist)}')
        if len(unc_portfoliolist) != exp_unconstrategies:
            raise TypeError(f'unequal number of unconstricted strategies. Expected {exp_unconstrategies} vs actual in unc_portfoliolist {len(unc_portfoliolist)}')    
    
        #################Optimization Complete!#################################################
        
        
        
        
        
        
        
        #################User can select to visualize strategies... #############################
        #currently only entries and performance line charts are available
        srv.getVisualization()
        ##########################################################################################
        
        
        
        
        
        

        ###################Portfolio Stats!#####################################################
        '''Gather the list of '''
        portfoliolist = list()
        #initial_capital = 10000
        portfolioentries = fms.countFileEntries('Portfolio')
        #trade_direction = 'BUY'
        for i in range(0,portfolioentries):
            portfolio = pd.read_csv(f'Portfolio{i}.csv')
            portfoliolist.append(portfolio)
        
        #trying to make code better
        attribution = StrategyPerformance(portfoliolist,0.02, initial_capital,trade_direction)
        stats=attribution.generate_stats()
        for item in range(len(stats)):
            print('\n')  
            for key, value in stats[item].items():  
                print(key, ' : ', value)
        
        #########################################################################################
        
        
        '''
        Check signals and portfolio data in CSV
        
        for i in range(len(portfolio_list)):
            portfolio_list[i].to_csv(f'PP{i}.csv')
            
        for i in range(len(signals_list)):
            signals_list[i].to_csv(f'SS{i}.csv')
        '''
   
    
   
