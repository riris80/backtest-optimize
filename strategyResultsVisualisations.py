# -*- coding: utf-8 -*-
"""
Created on Sat May 30 12:18:28 2020

@author: HP
"""

# -*- coding: utf-8 -*-
"""
Created on Sat May 23 14:06:34 2020

@author: HP
"""

import os
import matplotlib.pyplot as plt
#import numpy as np
import pandas as pd
#import seaborn as sns

from bokeh.plotting import figure
# Import output_file and show from bokeh.io
from bokeh.io import show #, output_file
#from bokeh.models import HoverTool
#from bokeh.plotting import ColumnDataSource
from math import pi
#from bokeh.layouts import row
#from bokeh.layouts import column
#from bokeh.models.widgets import DataTable, DateFormatter, TableColumn
#from bokeh.layouts import gridplot
#


#%matplotlib inline

#not relevant but helpful functions:
#print(os.getcwd())
#print(dir(os.getcwd))
#print(LogisticRegression())
#print(dir(LogisticRegression()))

'''
Display range of optimised trading strategies performance of cash on a line plot 
'''
def visualiseStrategyResults():

    portfolios = list()

    #def#####################
    
    tempcount = 0
    for item in os.scandir():
        stritem = str(item)
        #print(stritem)
        #print(type(stritem))
        #if stritem == '<DirEntry \'backtest.py\'>':
        #print('ffffffffffffffffffffff')
        if 'Portfolio' in stritem:
            tempcount = tempcount + 1
            #print(stritem)
    #print(tempcount)


    for i in range(0,tempcount):
        portfolio = pd.read_csv(f'Portfolio{i}.csv')
        portfolios.append(portfolio)

    #print(../../../)

    '''TEST VISUALIZATION'''
        ######################################################################  

    #inc = bars.CLOSE > bars.OPEN
    #dec = bars.OPEN > bars.CLOSE
    '''
    w = 12*60*60*1000 # half day in ms
    TOOLS = "pan,crosshair,wheel_zoom,box_zoom,reset,save"
    p3 = figure(x_axis_type="datetime", tools=TOOLS, plot_width=850, plot_height=600, title = "S&P500 Daily MA strategy")
    p3.xaxis.major_label_orientation = pi/2  
    p3.grid.grid_line_alpha=0.3
    #print(df2.index)
    #p3.line(df2.index, portfolios[0].total_net,color='red')
    #show(p3)
    '''

    #convert panda series to datetime obj
    datetime_series = pd.to_datetime(portfolios[0].Date)
    # create datetime index passing the datetime series
    datetime_index = pd.DatetimeIndex(datetime_series.values)
    df2=portfolios[0].set_index(datetime_index)
    # we don't need the column anymore
    df2.drop('Date',axis=1,inplace=True)

    ################map colors

    colors = {0: 'red', 1: 'blue', 2: 'green', 3: 'orange', 4: 'brown',5:'purple',6:'pink',7:'black',
             8: 'red', 9: 'blue', 10: 'green', 11: 'orange', 12: 'brown',13:'purple',14:'pink',15:'black',
             16: 'red', 17: 'blue', 18: 'green', 19: 'orange'}
    plt.figure(figsize=(10,10))
    plt.xlabel('Date')
    plt.ylabel('Total Account')
    plt.title('Optimization Output')
    for i in range(0,len(portfolios)):
        txt1 = portfolios[i].strategy[0]
        txt2 = portfolios[i]['Con-strategylimits'][0]
        plt.plot(df2.index, portfolios[i].cash_net_Trading, color=colors[i],label=f'str: {txt1} con: {txt2}')
    plt.legend(loc=(1.02,0))

    
    
    
def strategyEntryVisualisation(bars, df2, ma):
     
    inc = bars.CLOSE > bars.OPEN
    dec = bars.OPEN > bars.CLOSE
    w = 12*60*60*1000 # half day in ms

    TOOLS = "pan,crosshair,wheel_zoom,box_zoom,reset,save"

    p = figure(x_axis_type="datetime", tools=TOOLS, plot_width=850, plot_height=600, title = "S&P500 Daily MA strategy")
    p.xaxis.major_label_orientation = pi/2  
    p.grid.grid_line_alpha=0.3
    '''    
    p2 = figure(x_axis_type="datetime", plot_width=400, plot_height=300)
    p2.vbar(x=returns.index, width=0.5, bottom=0,
       top=returns.cumCrystallized, color="firebrick")
    '''
    
    'First add then thin black line high to low - Xo, Yo, X1, Y1'
    p.segment(bars.Date, bars.HIGH, bars.Date, bars.LOW, color="black")

    'v.bar(x of vertical bar, width of bar, y bottom of vertical bar, y top of vertical bar)'
    p.vbar(bars.Date[inc], w, bars.OPEN[inc], bars.CLOSE[inc], fill_color="#D5E1DD", line_color="black")
    p.vbar(bars.Date[dec], w, bars.OPEN[dec], bars.CLOSE[dec], fill_color="#F2583E", line_color="black")

    #p.line(signals.index, self.signals['short_mavg'],color='blue')
    p.line(bars.index, bars.CLOSE.rolling(ma,min_periods=1,center=False).mean(),color='blue')
    
    
    #if trade == 'BUY' then: 
    
    #p.triangle(df2.loc[df2.positionsB == 1.0].index, df2.TradedPrice[df2.positionsB == 1.0],8,fill_color="blue")
    #p.triangle(df2.loc[df2.positionsB == -1.0].index, df2.TradedPrice[df2.positionsB == -1.0],8,fill_color="red",angle=45)   

    #else:

    p.triangle(df2.loc[df2.positionsS == 1.0].index, df2.TradedPrice[df2.positionsS == 1.0],8,fill_color="red",angle=45)
    p.triangle(df2.loc[df2.positionsS == -1.0].index, df2.TradedPrice[df2.positionsS == -1.0],8,fill_color="blue")      
    
    
    '''           
    p3 = figure(x_axis_type="datetime", tools=TOOLS, plot_width=850, plot_height=600, title = "S&P500 Daily MA strategy")
    p3.xaxis.major_label_orientation = pi/2  
    p3.grid.grid_line_alpha=0.3
    
    #p3.line(returns.index, returns.cash,color='red')
    p3.line(returns.index, returns.cash_Trading,color='blue')
    p3.line(returns.index, returns.cash_net_Trading,color='red')
    '''   
    
    #output_file("S&P500DMAstrat.html", title="S&P500DailyMAstrat")
    
    #to show with chart with position taking
    #show(row(p, column(p2, stats)))
    
    #show(p3)
    show(p)    


def getVisualization(**kwargs):
#if __name__ == "__main__":
   
    ma = kwargs.get('ma')
    print(f' average passed to GETVISUALIZATION {ma}')
    print('in getVisualization')
    df = pd.read_csv('EPDailyData_temp2.csv')
    bars = df
    bars["Date"] = pd.to_datetime(bars["Date"])
    bars.index = bars.Date
    
    portfolios = list()
    
    #signals = pd.read_csv('EPDailyData_temp2.csv')
    
    #def#####################
    tempcount = 0
    for item in os.scandir():
        stritem = str(item)
        #print(stritem)
        #print(type(stritem))
        #if stritem == '<DirEntry \'backtest.py\'>':
        #print('ffffffffffffffffffffff')
        if 'Portfolio' in stritem:
            tempcount = tempcount + 1
            #print(stritem)
    #print(tempcount)


    for i in range(0,tempcount):
        portfolio = pd.read_csv(f'Portfolio{i}.csv')
        portfolios.append(portfolio)
    
    #convert panda series to datetime obj
    datetime_series = pd.to_datetime(portfolios[0].Date)
    # create datetime index passing the datetime series
    datetime_index = pd.DatetimeIndex(datetime_series.values)
    df2=portfolios[0].set_index(datetime_index)
    # we don't need the column anymore
    df2.drop('Date',axis=1,inplace=True)
    
    
    
    #visualiseStrategyResults()
    strategyEntryVisualisation(bars, df2,ma)