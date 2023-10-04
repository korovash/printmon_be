import asyncio
import aiodns
import re

loop = asyncio.get_event_loop()
resolver = aiodns.DNSResolver(loop=loop)

async def query(name, query_type):
    try:
        return await resolver.query(name, query_type)
    except:
        pass

def resolve_host(host):
    if not(re.match(r'^\S+\.[dD][vV][fF][uU]\.[rR][uU]$', host)):
        host = host + '.dvfu.ru'
    coro = query(host, 'A')
    result = loop.run_until_complete(coro)
    if result is not None:
        return result[0].host
