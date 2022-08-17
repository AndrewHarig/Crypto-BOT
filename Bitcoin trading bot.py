import websocket, json, pprint, talib, numpy
import config
from binance.client import Client
from binance.enums import *

SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'BTCUSD'
TRADE_QUANTITY = 0.00085

closes = []
in_position = False

client = Client(config.API_KEY, config.API_KEY_SECRET, tld='us' )

def order(side, quantity, symbol,order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False
    return True

def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes

    print('recieved message')
    print(message)
    json_message = json.loads(message)
    pprint.pprint(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:
        print("candle clossed at {}".format(close))
        closes.append(float(closes))
        print("closes")
        print(closes)

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD) 
            print("all rsis calculated so far")
            print(rsi)
            last_rsi = rsi[-1]
            print("the current rsi is {}".format(last_rsi))

            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print("SELL!SELL!SELL!")
                    ORDER_SUCEEDED = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    if ORDER_SUCEEDED:
                        in_position = False
                else:
                    ("It is overbought but you already sold")
            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("It is already oversold, but you already own it")
                else:
                    print("BUY!BUY!BUY!")
                    ORDER_SUCEEDED = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    if ORDER_SUCEEDED:
                        in_position = True



ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()