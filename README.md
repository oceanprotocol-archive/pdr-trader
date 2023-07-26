First cut: it may work, with errors

## Flow
- reads from subgraph list of template3 contracts, this gets list of all template3 deployed contracts
- for every contract, monitors when epoch is changing
- checks for valid subscription, if there is none, will buy one
- calls trade function from trade.py with the agg predval


## How to run

For full flow see [README](https://github.com/oceanprotocol/pdr-trueval/blob/main/README_local_full_flow.md)

```bash
export RPC_URL=http://127.0.0.1:8545
export SUBGRAPH_URL="http://172.15.0.15:8000/subgraphs/name/oceanprotocol/ocean-subgraph"
export PRIVATE_KEY="xxx"
export STAKE_TOKENS="[]"
```
where:
  - STAKE_TOKEN = combined with above, narrow scope only to template3 contracts that are using a specific list of STAKE_TOKENS (ie: Ocean). If not present or empty, will predict and stake everywhere :)

Install requirements if needed
```bash
pip install -r requirements.txt
```

Start the trader:
```bash
python3 main.py
```

## Additional ENV variables used to filter:

 - PAIR_FILTER = if we do want to act upon only same pair, like  "BTC/USDT,ETH/USDT"
 - TIMEFRAME_FILTER = if we do want to act upon only same timeframes, like  "5m,15m"
 - SOURCE_FILTER = if we do want to act upon only same sources, like  "binance,kraken"
 - OWNER_ADDRS = if we do want to act upon only same publishers, like  "0x123,0x124"

## Fork and customize
  The actual trade code is in trade.py.

  We call trade function with 3 args:
   - topic:  this is pair object
   - direction:  this is the agg pred val  ( 0 -> fully confident that goes down , 1 -> fully confident that goes up)


  You need to change the function code and actually do some trades

## TO DO
  - [ ]  - check for balances
  - [ ]  - improve approve/allowence flow
