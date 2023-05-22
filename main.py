import time
import asyncio
import os

from pdr_trader.utils.process import process_block
from pdr_trader.utils.contract import w3


# TODO - check for all envs
assert os.environ.get("RPC_URL",None), "You must set RPC_URL environment variable"
assert os.environ.get("SUBGRAPH_URL",None), "You must set SUBGRAPH_URL environment variable"

async def log_loop(event_filter, poll_interval):
    last_processed_block_no = 0
    while True:
        block = None
        events = event_filter.get_new_entries()
        #print(f" Got {len(events)} events..")
        for event in events:
            block_hash = event.hex()
            block = w3.eth.get_block(block_hash, full_transactions=False)
        """ Always handle latest block"""
        if block and block["number"]>last_processed_block_no:
            last_processed_block_no = block["number"]
            process_block(block)
        await asyncio.sleep(poll_interval)

def main():
    print("Starting main loop...")
    while True:
        try:
            block_filter = w3.eth.filter('latest')
            loop = asyncio.get_event_loop()
            try:
                loop.run_until_complete(
                    asyncio.gather(
                        log_loop(block_filter, 1))
                )
            except Exception as e:
                print(e)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    main()