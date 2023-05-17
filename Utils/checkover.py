import asyncio
import time

async def checkOver(deadline):
    if int(time.time()) >= deadline:
        return False

    while True:
        try:
            await asyncio.sleep(1.0)
        except asyncio.CancelledError:
            # The task was cancelled, so return False
            return False

        if int(time.time()) >= deadline:
            break

    return True