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
  - you can also export SOURCE_FILTER, TIMEFRAME_FILTER, PAIR_FILTER *(comma-separated lists) to limit predictions based on NFT data. E.g. export PAIR_FILTER=eth-usdt,eth-btc
  - STAKE_TOKEN = combined with above, narrow scope only to template3 contracts that are using a specific list of STAKE_TOKENS (ie: Ocean). If not present or empty, will predict and stake everywhere :)

Install requirements if needed
```bash
pip install -r requirements.txt
```

Start the trader:
```bash
python3 main.py
```

## Fork and customize
  The actual trade code is in trade.py.

  We call trade function with 3 args:
   - topic:  this is ERC20.name
   - contract_address
   - direction:  this is the agg pred val


  You need to change the function code and actually do some trades

## TO DO
  - [ ]  - implement logic for STAK_TOKENS
  - [ ]  - check for balances
  - [ ]  - improve approve/allowence flow
