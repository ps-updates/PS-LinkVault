import asyncio
from shortzy import Shortzy

async def get_shortlink(api, site, long_url):
    shortzy = Shortzy(api, site)
    try:
        link = await shortzy.convert(long_url)
    except Exception:
        link = await shortzy.get_quick_link(long_url)
    return link

def get_readable_time(seconds: int, long: bool = False) -> str:
    periods = [
        ('Days', 86400),
        ('Hours', 3600),
        ('Minutes', 60),
        ('Seconds', 1)
    ]

    result = []
    for name, count in periods:
        if seconds >= count:
            value, seconds = divmod(seconds, count)
            result.append(f"{int(value)} {name}")
            if not long:
                break

    return ': '.join(result) if long else result[0] if result else '0 Seconds'
