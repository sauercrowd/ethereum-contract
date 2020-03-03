import os
import json
from requests.auth import HTTPBasicAuth

import web3
from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware

from solc import compile_standard

PROJECT_ID=os.environ['PROJECT_ID']
PROJECT_SECRET=os.environ['PROJECT_SECRET']
ENDPOINT=os.environ['ENDPOINT']

WALLET_KEY=os.environ['WALLET_KEY']
WALLET_ADDR=os.environ['WALLET_ADDR']

w3 = Web3(Web3.HTTPProvider(ENDPOINT, request_kwargs={'auth': HTTPBasicAuth(PROJECT_ID, PROJECT_SECRET)}))
w3.middleware_onion.add(construct_sign_and_send_raw_middleware(WALLET_KEY))

acct = w3.eth.account.privateKeyToAccount(WALLET_KEY)
w3.eth.defaultAccount = WALLET_ADDR

compiled_sol = compile_standard({
    "language": "Solidity",
    "sources": {"election.sol": {"urls": ["./coin.sol"]}},
    "settings":{
             "outputSelection": {
                 "*": {
                     "*": [
                         "metadata", "evm.bytecode"
                         , "evm.bytecode.sourceMap"
                     ]
                 }
             }
         }
    } , allow_paths=".")


bytecode = compiled_sol['contracts']['election.sol']['Election']['evm']['bytecode']['object']
abi = json.loads(compiled_sol['contracts']['election.sol']['Election']['metadata'])['output']['abi']

# Create contract
Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
# transact it
tx_hash = Contract.constructor().transact()
# and wait for the deployment
tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

print("Contract Deployed At:", tx_receipt['contractAddress'])

# update contract
election = Contract(address=tx_receipt.contractAddress)

# mint coins
tx_hash = election.functions.mint(w3.eth.defaultAccount, 1).transact()
# print coins (too early)
print("Coins:", election.functions.balances(w3.eth.defaultAccount).call())
# now wait for transaction to go through
tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
# and try again
print("Coins:", election.functions.balances(w3.eth.defaultAccount).call())
