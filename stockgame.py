import random
import sys
from IPython.display import display, HTML

import pandas as pd
import numpy as np
## plotply
from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go
from plotly import tools
init_notebook_mode(connected=True)


colors = [
'rgb(214, 39, 40)',
'rgb(44, 160, 44)',
'rgb(31, 119, 180)',
'rgb(255, 127, 14)',
'rgb(148, 103, 189)'
]

# parameters
start_money = 0
start_stock = 0

order_base_cost = 4
order_cost = 0
holding_cost = 1
sell_money = 2

max_stock = 20
max_order = 10

filename = 'table.csv'
teams = ['Red','Green','Blue','Orange','Robot']

################%%

def forecast2demands(forecast):
	if forecast == 0:
		return [0]
	elif forecast == 1:
		return [1,2,3]
	elif forecast == 2:
		return [1,2,3,4,5,6]
	print('sth is wrong with forecast')

def step(money,stock,order,demand):
	new_stock = stock + order
	if not np.isnan(demand):
		sold_stock = min(new_stock,demand)
	else:
		sold_stock = 0
	new_stock = new_stock-sold_stock
	new_money = money
	if order > 0:
		new_money -= order_base_cost
	new_money -= order*order_cost
	new_money += sold_stock*sell_money
	new_money -= new_stock*holding_cost
	return new_money, new_stock

def new_demand(randomly=True):
	################%%
	df = pd.read_csv(filename).set_index('Round')
	df['Demand'] = df['Forecast'].apply(forecast2demands).apply(random.choice)
	df.to_csv(filename)
	################%%

def clean(randomly=True):
	################%%
	df = pd.read_csv(filename).set_index('Round')
	df['Demand'] = None
	for team in teams:
		df['%s-Order'%team] = None
		df['%s-Factor'%team] = 1
	df.to_csv(filename)
	################%%

def fill():
	################%%
	df = pd.read_csv(filename).set_index('Round')
	Order, Money = compute_strategy(df)
	for team in teams:
		for i,row in df.iterrows():
			demand = df.loc[i]['Demand']*df.loc[i]['%s-Factor'%team]
			df.at[i,'%s-Demand'%team] = demand
			if i == df.index.min():
				stock = start_stock
				money = start_money
			else:
				money = df.loc[i-1]['%s-Money'%team]
				stock = df.loc[i-1]['%s-Stock'%team]
			if team == 'Robot' and not np.isnan(demand):
				order = Order[i,stock]
				df.at[i,'%s-Order'%team] = order
			else:
				order = df.loc[i]['%s-Order'%team]
			new_money, new_stock = step(money,stock,order,demand)
			df.at[i,'%s-Money'%team] = new_money
			df.at[i,'%s-Stock'%team] = new_stock
	#display(HTML(df.to_html()))
	print(df)
	plot_table(df)
	plot_stats(df)
	################%%

def plot_table(df):
	################%%
	colors_ = [ color.replace('rgb','rgba')[:-1]+',0.4)' for color in colors ]
	traces = []
	traces_stock = []
	traces_money = []
	traces2 = []
	traces += [ go.Bar(x=df.index,y=df['Demand'],marker=dict(color='lightgrey'),name='Demand') ]

	weather_colors = ['lightgrey','lightblue','yellow']
	traces += [ go.Scatter(x=df.index,y=[df.max().max()+2]*len(df),mode='markers',marker=dict(size=30,color=df['Forecast'].astype(int).apply(weather_colors.__getitem__)),name='Weather',showlegend=True) ]

	for j,team in enumerate(teams):
		stocks = df['%s-Stock'%team].dropna()
		last_stock = 0
		if len(stocks) > 0:
			last_stock = stocks.tail(1).values[0]
		moneys = df['%s-Money'%team].dropna().tail(1)
		last_money = 0
		if len(moneys) > 0:
			last_money = moneys.tail(1).values[0]
		#traces2 += [ go.Bar(x=[0]+list(df.index),y=df['%s-Order'%team],name='%s-Order'%team,marker=dict(color=colors_[j])) ]
		traces_stock += [ go.Scatter(x=[0]+list(df.index),y=[start_stock]+list(df['%s-Stock'%team]),name='%i %s-Stock'%(last_stock,team),mode='lines',line=dict(color=colors[j],width=10),marker=dict(color=colors_[j],size=20))]
		traces_money += [ go.Scatter(x=[0]+list(df.index),y=[start_money]+list(df['%s-Money'%team]),name='%i %s-Money'%(last_money,team),mode='lines',line=dict(color=colors_[j],width=10,dash='dot'),marker=dict(color=colors_[j],size=30,symbol=18))]

	layout = go.Layout(
	height=1000,
	width=2000,
	showlegend=True,
	font=dict(size=25),
	xaxis=dict(title='day',dtick=1,range=(-0.5,15.5)),
	yaxis=dict(title='amount'),
	)
	fig = go.Figure(data=traces+traces_money+traces_stock,layout=layout)
	#iplot(fig,show_link=False)
	plot(fig, filename = 'table.html', auto_open=False,show_link=False)
	################%%


def plot_stats(df):
	################%%
	traces = []
	df_stats = df.copy(deep=True)
	cols = ['Demand']
	for i,team in enumerate(teams):
	    df_stats['%s-NumOrders'%team] = df_stats['%s-Order'%team] > 0
	    cols = [ '%s-Demand'%team, '%s-Order'%team, '%s-NumOrders'%team ]
	    s = df_stats.sum()[cols]
	    color = colors[i]
	    traces.append( go.Bar(x=['Demand','Orders','NumOrders'],y=s,name=team,marker=dict(color=color)) )

	layout = go.Layout(
	height=1000,
	width=2000,
	showlegend=True,
	font=dict(size=40),
	)
	fig = go.Figure(data=traces,layout=layout)
	#iplot(fig,show_link=False)
	plot(fig, filename = 'stats.html', auto_open=False,show_link=False)
	################%%


def compute_strategy(df):
	################%%
	rounds = df.index
	forecasts = df['Forecast']
	Money = dict()
	Order = dict()
	for i in rounds[::-1]:
		forecast = forecasts[i]
		for stock in range(0,max_stock):
			if i == max(rounds):
				Money[i,stock] = 0
				Order[i,stock] = 0
			else:
				order2money = dict()
				for order in range(0,max_order):
					demand_range = forecast2demands(forecast)
					moneys = []
					money = 0
					for demand in demand_range:
						new_money, new_stock = step(money,stock,order,demand)
						diff_money = new_money - money
						if (i+1,new_stock) in Money:
							moneys += [diff_money+Money[i+1,new_stock]]
					if moneys:
						order2money[order] = np.mean(moneys)
				if order2money:
					order2money = pd.Series(order2money)
					Money[i,stock] = order2money.max()
					Order[i,stock] = order2money.idxmax()
	print('max order:',max(Order.values()))
	print('max money:',max(Money.values()))
	################%%
	return Order, Money




if __name__ == "__main__":
	if 'new_demand' in sys.argv:
		new_demand()
	if 'clean' in sys.argv:
		clean()
	fill()
