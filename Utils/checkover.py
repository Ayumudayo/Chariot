import asyncio
import time

# Async function that check the deadline is reached
async def checkOver(endTime):
        if(int(time.time()) >= endTime):
            return False

        while True:
            if(int(time.time()) >= endTime):
                break
            # Check evrey second.
            await asyncio.sleep(1.0)        

        return True