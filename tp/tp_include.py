
SS = "1-StrongSell"
SELL = "2-Sell"
HOLD = "3-Hold"
BB = "4-Buy"
SB = "5-StrongBuy"
BS = "BS"
S = "S"
B = "B"
ShortTermBuy = "STBuy"
STBuyLimit = "STBuyL"
ShortTermSell = "STSell"
STSellLimit = "STSellL"
ShortTermHold = "STHold"
ShortTermDays = 45 # No of Days to consider for Short Term
IdleSecurityDays = ShortTermDays
ShortTermGnLPercentageBuy = 5 # 5% Gain or Loss
ShortTermGnLPercentageSell = 5 # 5% Gain or Loss
STLPerc = 2.5 # 2.5% Loss/gain
OrderExistSign = "+"


# Define Col Names
Symbol = 'Symbol'
Date = 'Date'
Quantity = 'Quantity'
Price = 'Price'
Amount = 'Amount'
Account = 'Account'
Description = 'Description'
last_trade_date = 'last_date'



# % Changes today - to recommend buy/sell
TodaysChange = 0
StrongBuy = 5
StrongSell = StrongBuy
Buy = StrongBuy-2
Sell = Buy
Hold = Buy -1

SellTh = 0.05 # 5 %
BuyTh = SellTh +  0.02 # 7%

SmallMrkCapValue = 200