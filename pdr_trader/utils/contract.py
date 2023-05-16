
import json
import os
from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3 import Web3, HTTPProvider, WebsocketProvider
from web3.middleware import construct_sign_and_send_raw_middleware
from os.path import expanduser

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

home = expanduser("~")

private_key = os.environ.get("PRIVATE_KEY")
assert private_key is not None, "You must set PRIVATE_KEY environment variable"
assert private_key.startswith("0x"), "Private key must start with 0x hex prefix"

# instantiate Web3 instance
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
private_key = os.environ.get("PRIVATE_KEY")
account: LocalAccount = Account.from_key(private_key)
owner = account.address
w3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))


""" Temporary solution until we have ocean-contracts published in pypi"""
f = open(home+'/.ocean/ocean-contracts/artifacts/contracts/templates/ERC20Template3.sol/ERC20Template3.json')
data=json.load(f)
abi = data['abi']
f = open(home+'/.ocean/ocean-contracts/artifacts/contracts/pools/fixedRate/FixedRateExchange.sol/FixedRateExchange.json ')
data=json.load(f)
fre_abi = data['abi']


class Token:
    def __init__(self, address):
        self.contract_address = w3.to_checksum_address(address)
        self.contract_instance = w3.eth.contract(address=w3.to_checksum_address(address), abi=abi)

    def allowance(self,account,spender):
        return self.contract_instance.functions.allowance(account,spender).call()

    def balanceOf(self,account):
        return self.contract_instance.functions.balanceOf(account).call()
    
    def approve(self,spender,amount):
        gasPrice = w3.eth.gas_price
        #print(f"Approving {amount} for {spender} on contract {self.contract_address}")
        try:
            tx = self.contract_instance.functions.approve(spender,amount).transact({"from":owner,"gasPrice":gasPrice})
            receipt = w3.eth.wait_for_transaction_receipt(tx)
            return receipt
        except:
            return None

class FixedRate:
    def __init__(self, address):
        self.contract_address = w3.to_checksum_address(address)
        self.contract_instance = w3.eth.contract(address=w3.to_checksum_address(address), abi=abi)

    def get_dt_price(self,exchangeId):
        return self.contract_instance.functions.calcBaseInGivenOutDT(exchangeId,w3.to_wei('1','ether'),0).call()


class PredictorContract:
    def __init__(self, address):
        self.contract_address = w3.to_checksum_address(address)
        self.contract_instance = w3.eth.contract(address=w3.to_checksum_address(address), abi=abi)

    def is_valid_subscription(self):
        return self.contract_instance.isValidSubscription(owner).call()
    
    def buy_and_start_subscription(self):
        """ Buys 1 datatoken and starts a subscription"""
        fixed_rates=self.get_exchanges()
        (fixed_rate_address,exchange_id) = fixed_rates[0]
        # get datatoken price
        exchange = FixedRate(fixed_rate_address)
        (baseTokenAmount, oceanFeeAmount, publishMarketFeeAmount,consumeMarketFeeAmount) = FixedRate.get_dt_price(exchange_id)
        token = Token(self.get_stake_token(self))
        gasPrice = w3.eth.gas_price
        try:
            tx = self.contract_instance.functions.buyFromFreAndOrder(
                (
                    owner,
                    0,
                    (
                        ZERO_ADDRESS,
                        ZERO_ADDRESS,
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                    ),
                    (   
                        ZERO_ADDRESS,
                        ZERO_ADDRESS,
                        0
                    ),
                ),
                (
                    w3.to_checksum_address(fixed_rate_address),
                    exchange_id,
                    baseTokenAmount,
                    0,
                    ZERO_ADDRESS,
                ),
                {"from":owner,"gasPrice":gasPrice},
            )
            receipt = w3.eth.wait_for_transaction_receipt(tx)
            return receipt
        except:
            return None

    def get_exchanges(self):
        return self.contract_instance.functions.getFixedRates().call()
    
    def get_stake_token(self):
        return self.contract_instance.functions.stakeToken().call()
    
    def get_current_epoch(self):
        return self.contract_instance.functions.curEpoch().call()
    
    def get_agg_predval(self, block):
        """ check subscription"""
        if not self.is_valid_subscription():
            print("Buying a new subscription")
            self.buy_and_start_subscription()
        (nom, denom) = self.contract_instance.functions.getAggPredval(block).call({"from":owner})
        return nom/denom    



