import typer
import asyncio
import aiohttp
import ujson

async def binance_conn():
    websocket = await _conn('wss://stream.binance.com:443/ws/!miniTicker@arr')
    return websocket
    
async def _conn(uri):
    session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(100))
    websocket = await session.ws_connect(uri, proxy=PROXY, ssl=False)
    return websocket
    
async def get_k_line(kline_q):
    print('binance web Socket Connecting ...')
    websocket = await ws.binance_conn()
    ts = time.time()
    print('binance web Socket Connect Success!')

    while 1:
        try:
            msg = await websocket.receive(timeout=10)
        except asyncio.exceptions.TimeoutError as e:
            print('TimeoutError: Reconnecting')
            websocket = await ws.binance_conn()
            await asyncio.sleep(1)
        else:
            match msg.type:
                case aiohttp.WSMsgType.TEXT:
                    data = ujson.loads(msg.data)
                    for ticker in data:
                        # TODO Real-time data logic processing
                        
                case aiohttp.WSMsgType.CLOSED:
                    print('Binance web Socket Connect Failed!')
                    websocket = await ws.binance_conn()
                    await asyncio.sleep(1)


===== starting program =====

app = typer.Typer()
async def run():
    kline_q = asyncio.queues.Queue(maxsize=10000)
    await asyncio.gather(
        get_k_line(kline_q)
    )

@app.command()
def start():
    asyncio.run(run())

@app.command()
def goodbye(name: str, formal: bool = False):
    if formal:
        typer.echo(f"Goodbye Ms. {name}. Have a good day.")
    else:
        typer.echo(f"Bye {name}!")

if __name__ == "__main__":
    app()       