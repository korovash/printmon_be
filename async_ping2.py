import asyncio
import aioping

loop = asyncio.get_event_loop()

async def do_ping(host):
    try:
        await aioping.ping(host, timeout=1)
        return True
    except TimeoutError:
        return False

def ping_host(host):
    result = loop.run_until_complete(do_ping(host))
    return result