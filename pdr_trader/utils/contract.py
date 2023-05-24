
import json
import os
import glob
import time

from eth_account import Account
from eth_account.signers.local import LocalAccount
from pathlib import Path
from web3 import Web3, HTTPProvider, WebsocketProvider
from web3.middleware import construct_sign_and_send_raw_middleware
from os.path import expanduser

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

home = expanduser("~")

rpc_url = os.environ.get("RPC_URL")
assert rpc_url is not None, "You must set RPC_URL environment variable"
private_key = os.environ.get("PRIVATE_KEY")
assert private_key is not None, "You must set PRIVATE_KEY environment variable"
assert private_key.startswith("0x"), "Private key must start with 0x hex prefix"

# instantiate Web3 instance
w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={'timeout': 60}))

account: LocalAccount = Account.from_key(private_key)
owner = account.address
w3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))




class Token:
    def __init__(self, address):
        self.contract_address = w3.to_checksum_address(address)
        self.contract_instance = w3.eth.contract(address=w3.to_checksum_address(address), abi=get_contract_abi('ERC20Template3'))

    def allowance(self,account,spender):
        return self.contract_instance.functions.allowance(account,spender).call()

    def balanceOf(self,account):
        return self.contract_instance.functions.balanceOf(account).call()
    
    def approve(self,spender,amount):
        gasPrice = w3.eth.gas_price
        #print(f"Approving {amount} for {spender} on contract {self.contract_address}")
        tx = None
        try:
            tx = self.contract_instance.functions.approve(spender,amount).transact({"from":owner,"gasPrice":gasPrice})
            print(f"Approval tx: {tx.hex()}.")
            receipt = w3.eth.wait_for_transaction_receipt(tx)
            print(f"Got receipt")
            return receipt
        except Exception as e:
            print(e)
            return tx

class FixedRate:
    def __init__(self, address):
        self.contract_address = w3.to_checksum_address(address)
        self.contract_instance = w3.eth.contract(address=w3.to_checksum_address(address), abi=get_contract_abi('FixedRateExchange'))

    def get_dt_price(self, exchangeId):
        return self.contract_instance.functions.calcBaseInGivenOutDT(exchangeId,w3.to_wei('1','ether'),0).call()


class PredictorContract:
    def __init__(self, address):
        self.contract_address = w3.to_checksum_address(address)
        self.contract_instance = w3.eth.contract(address=w3.to_checksum_address(address), abi=get_contract_abi('ERC20Template3'))
        stake_token=self.get_stake_token()
        self.token = Token(stake_token)

    def is_valid_subscription(self):
        return self.contract_instance.functions.isValidSubscription(owner).call()
    
    def get_empty_provider_fee(self):
        return {
            "providerFeeAddress": ZERO_ADDRESS,
            "providerFeeToken": ZERO_ADDRESS,
            "providerFeeAmount": 0,
            "v": 0,
            "r": 0,
            "s": 0,
            "validUntil": 0,
            "providerData": 0,
        }
    def string_to_bytes32(self,data):
        if len(data) > 32:
            myBytes32 = data[:32]
        else:
            myBytes32 = data.ljust(32, '0')
        return bytes(myBytes32, 'utf-8')

    def buy_and_start_subscription(self):
        """ Buys 1 datatoken and starts a subscription"""
        fixed_rates=self.get_exchanges()
        if not fixed_rates:
            return
        (fixed_rate_address,exchange_id) = fixed_rates[0]
        # get datatoken price
        exchange = FixedRate(fixed_rate_address)
        (baseTokenAmount, oceanFeeAmount, publishMarketFeeAmount,consumeMarketFeeAmount) = exchange.get_dt_price(exchange_id)
        gasPrice = w3.eth.gas_price
        provider_fees = self.get_empty_provider_fee()
        print(f"Buying a subscription, cost is: {baseTokenAmount}")
        try:
            self.token.approve(self.contract_address,baseTokenAmount)
            print(f"Approved, going further")
            orderParams = (
                            owner,
                            0,
                            (
                                ZERO_ADDRESS,
                                ZERO_ADDRESS,
                                0,
                                0,
                                self.string_to_bytes32(''),
                                self.string_to_bytes32(''),
                                provider_fees["validUntil"],
                                w3.to_bytes(b'') ,
                            ),
                            (   
                                ZERO_ADDRESS,
                                ZERO_ADDRESS,
                                0
                            ),
                        )
            freParams=(
                            w3.to_checksum_address(fixed_rate_address),
                            w3.to_bytes(exchange_id),
                            baseTokenAmount,
                            0,
                            ZERO_ADDRESS,
                        )
            print("Calling buyFrom")
            tx = self.contract_instance.functions.buyFromFreAndOrder(orderParams,freParams).transact({"from":owner,"gasPrice":gasPrice})
            print(f"Subscription tx: {tx.hex()}")
            receipt = w3.eth.wait_for_transaction_receipt(tx)
            return receipt
        except Exception as e:
            print(e)
            return None

    def get_exchanges(self):
        return self.contract_instance.functions.getFixedRates().call()
    
    def get_stake_token(self):
        return self.contract_instance.functions.stakeToken().call()
    
    def get_current_epoch(self):
        return self.contract_instance.functions.curEpoch().call()
    
    def get_blocksPerEpoch(self):
        return self.contract_instance.functions.blocksPerEpoch().call()
    
    def get_agg_predval(self, block):
        """ check subscription"""
        if not self.is_valid_subscription():
            print("Buying a new subscription...")
            self.buy_and_start_subscription()
            time.sleep(1)
        try:
            print("Reading contract values...")
            (nom, denom) = self.contract_instance.functions.getAggPredval(block).call({"from":owner})
            print(f" Got {nom} and {denom}")
            if denom==0:
                return None
            return nom/denom
        except Exception as e:
            print("Failed to call getAggPredval")
            print(e)
            return None

def get_contract_abi(contract_name):
    """Returns the abi for a contract name."""
    path = get_contract_filename(contract_name)

    if not path.exists():
        raise TypeError("Contract name does not exist in artifacts.")

    with open(path) as f:
        data = json.load(f)
        return data['abi']

def get_contract_filename(contract_name):
    """Returns abi for a contract."""
    contract_basename = f"{contract_name}.json"

    # first, try to find locally
    address_filename = os.getenv("ADDRESS_FILE")
    path = None
    if address_filename:
        address_dir = os.path.dirname(address_filename)
        root_dir = os.path.join(address_dir, "..")
        os.chdir(root_dir)
        paths = glob.glob(f"**/{contract_basename}", recursive=True)
        if paths:
            assert len(paths) == 1, "had duplicates for {contract_basename}"
            path = paths[0]
            path = Path(path).expanduser().resolve()
            assert (
                path.exists()
            ), f"Found path = '{path}' via glob, yet path.exists() is False"
            return path
    # didn't find locally, so use use artifacts lib
    #path = os.path.join(os.path.dirname(artifacts.__file__), "", contract_basename)
    #path = Path(path).expanduser().resolve()
    #if not path.exists():
    #    raise TypeError(f"Contract '{contract_name}' not found in artifacts.")
    return path