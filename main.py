import time
import os

from pdr_trader.utils.process import process_block
from pdr_trader.utils.contract import w3


# TODO - check for all envs
assert os.environ.get("RPC_URL",None), "You must set RPC_URL environment variable"
assert os.environ.get("SUBGRAPH_URL",None), "You must set SUBGRAPH_URL environment variable"

def main():
    print("Starting main loop...")
    lastblock =0
    while True:
        block = w3.eth.block_number
        if block>lastblock:
            lastblock = block
            process_block(w3.eth.get_block(block, full_transactions=False))
        else:
            time.sleep(1)

if __name__ == '__main__':
    main()