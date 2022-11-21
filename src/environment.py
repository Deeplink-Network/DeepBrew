'''
a custom reinforcement learning environment in accordance with openai's gym framework for the on-chain beer game
'''
# environment libraries
from gym import Env
from gym.spaces import Box
import numpy as np

# game libraries
from web3 import Web3
import numpy as np
from gbm import GBM
import json
import time
import dotenv

# GLOBAL VARIABLES
STARTING_DEMAND = 10
STARTING_BALANCE = 20_000
STARTING_INVENTORY = 10
STARTING_BEER_PRICE = 5
ROUNDS = 60
GAS_SCALE = 2

# KEYS
KEEPER_KEY = dotenv.dotenv_values(".env")['KEEPER_KEY']
INFURA_KEY = dotenv.dotenv_values(".env")['INFURA_KEY']

# INFURA AND WEB3
node_url = f'https://goerli.infura.io/v3/{INFURA_KEY}'
web3 = Web3(Web3.HTTPProvider(node_url))

# ABI
# SAVE AND LOAD THESE FROM A FILE INSTEAD
token_abi = json.loads('[{"inputs":[{"internalType":"string","name":"name_","type":"string"},{"internalType":"string","name":"symbol_","type":"string"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_account","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"burn","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_account","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"mint","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"minters","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_account","type":"address"},{"internalType":"bool","name":"_isMinter","type":"bool"}],"name":"setMinter","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"}]')
agent_abi = json.loads('[{"inputs":[{"internalType":"string","name":"name_","type":"string"},{"internalType":"contract IBeerToken","name":"beer_","type":"address"},{"internalType":"contract IERC20","name":"cash_","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"inputs":[],"name":"RATIO_DIVIDER","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"beer","outputs":[{"internalType":"contract IBeerToken","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"cash","outputs":[{"internalType":"contract IERC20","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"executors","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"ratio","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_account","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"sendBeer","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_account","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"sendCash","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_account","type":"address"},{"internalType":"bool","name":"_isExecutor","type":"bool"}],"name":"setExecutor","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]')

# ADDRESSES
# keeper
keeper_address = Web3.toChecksumAddress('0x6c51B510C83288831aDfdC4B76F461d41b45ad07')
# tokens
beer_address = Web3.toChecksumAddress('0x6d59DE07EaCeD3Ef50Ee99Ef4781fD0611B5e637')
cash_address = Web3.toChecksumAddress('0xCcC359e46479a91aCC71895Cf24c8C3291631B0d')
# agents
manufacturer_address = Web3.toChecksumAddress('0xD89a9D4098420eF2c6b3aeeb266a44f62084a15D') 
distributor_adress = Web3.toChecksumAddress('0x43BF386C6fCbF57Bf355a1AE956c694AF33Ec4A9') 
wholesaler_address = Web3.toChecksumAddress('0x87Dda551c41007C17B61a0DEC62b5f0b29671682') 
retailer_address = Web3.toChecksumAddress('0x79AF01Dc5B6bC91A49b60d42Adfd379Fef4C0e95')
# tools
escrow_address = Web3.toChecksumAddress('0xC07BA252866703433C0258DE7f35fdcDf8D5F92D') 
lp_address = Web3.toChecksumAddress('0xe61cE058d92993B12d257e8F73b80bD318065784')

# CONTRACT OBJECTS
# tokens
beer_contract = web3.eth.contract(address = beer_address , abi = token_abi)
cash_contract = web3.eth.contract(address = cash_address , abi = token_abi)
# agents
manufacturer_contract = web3.eth.contract(address = manufacturer_address , abi = agent_abi)
distributor_contract = web3.eth.contract(address = distributor_adress , abi = agent_abi)
wholesaler_contract = web3.eth.contract(address = wholesaler_address , abi = agent_abi)
retailer_contract = web3.eth.contract(address = retailer_address , abi = agent_abi)
# tools
escrow_contract = web3.eth.contract(address = escrow_address , abi = agent_abi)
lp_contract = web3.eth.contract(address = lp_address , abi = agent_abi)

# agent dictionary
accounts = {'manufacturer': {
                'contract': manufacturer_contract,
                'address': manufacturer_address
                },
            'distributor': {
                'contract': distributor_contract, 
                'address': distributor_adress
                },
            'wholesaler': {
                'contract': wholesaler_contract, 
                'address': wholesaler_address
                },
            'retailer': {
                'contract': retailer_contract, 
                'address': retailer_address
                },
            'market': {
                'contract': escrow_contract, 
                'address': escrow_address
                }
            }

# FUNCTIONS
# keeper functions
def get_keeper_eth_balance():
    return float(web3.eth.getBalance(keeper_address))/ 10**18

# cash functions
def mint_cash(to_account, amount, gas_scale=GAS_SCALE, nonce_offset=0):
    print('minting ', amount, 'CASH to', to_account)
    # checks
    try:
        assert to_account in accounts.keys(), 'Invalid account'
        assert amount >= 1, 'Invalid amount'
    except AssertionError as e:
        print(e)
        return
    try:
        # calculate nonce from keeper address
        nonce = web3.eth.getTransactionCount(keeper_address) + nonce_offset
        # build transaction
        tx = cash_contract.functions.mint(
            accounts[to_account]['address'],
            int(amount*10**18)).buildTransaction({
                'gas': int(web3.eth.get_block('latest').gasLimit/4),
                'gasPrice': int(web3.eth.gasPrice*gas_scale),
                'from': keeper_address,
                'nonce': nonce,
            })
        # sign transaction
        print('signing transaction...')
        signed_tx = web3.eth.account.signTransaction(tx, private_key=KEEPER_KEY)
        # send transaction
        print('sending transaction...')
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        print('tx hash:', web3.toHex(tx_hash))
        print('waiting for transaction receipt...')
        web3.eth.waitForTransactionReceipt(tx_hash, timeout = np.inf)
        print('transaction completed')
    
    # error handling
    except Exception as e:
        print(e)
        if(str(e) == "{'code': -32000, 'message': 'already known'}"):
            # wait 300 seconds for block to be mined
            print('waiting for block to be mined...')
            time.sleep(20)
            return
        elif (str(e) == "{'code': -32000, 'message': 'insufficient funds for gas * price + value'}"):
            print('waiting for next block and retrying...')
            time.sleep(20)
            return(mint_cash(to_account, amount, nonce_offset=0))
        elif (str(e) == "{'code': -32000, 'message': 'replacement transaction underpriced'}"):
            print('retrying with 10% higher gas price...')
            time.sleep(20)
            return(mint_cash(to_account, amount, gas_scale=1.21, nonce_offset=0))
        elif (str(e) == "{'code': -32000, 'message': 'nonce too low'}"):
            print('retrying with nonce offset...')
            time.sleep(20)
            return(mint_cash(to_account, amount, gas_scale=1.21, nonce_offset=0))
        return 

def burn_cash(from_account, amount, gas_scale=GAS_SCALE, nonce_offset=0):
    print('burning', amount, 'cash from', from_account)
    balance = get_balance(from_account)
    if amount > balance:
        amount = balance
    # checks
    try:
        assert from_account in accounts.keys(), 'Invalid account'
        # assert amount > 0, 'Invalid amount'
        # assert amount >= get_balance(from_account), 'Insufficient balance'
    except AssertionError as e:
        print(e)
        return

    try:
        nonce = web3.eth.getTransactionCount(keeper_address) + nonce_offset
        tx = cash_contract.functions.burn(
            accounts[from_account]['address'], 
            int(amount*10**18)).buildTransaction({
                'gas': int(web3.eth.get_block('latest').gasLimit/4),
                'gasPrice': int(web3.eth.gasPrice*gas_scale),
                'from': keeper_address,
                'nonce': nonce,
            })
        
        # sign transaction
        print('signing transaction...')
        signed_tx = web3.eth.account.signTransaction(tx, private_key=KEEPER_KEY)
        # send transaction
        print('sending transaction...')
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        print('tx hash:', web3.toHex(tx_hash))
        print('waiting for transaction receipt...')
        web3.eth.waitForTransactionReceipt(tx_hash, timeout = np.inf)
        print('transaction completed')
            
    # error handling
    except Exception as e:
        print(e)
        if(str(e) == "{'code': -32000, 'message': 'already known'}"):
            # wait 300 seconds for block to be mined
            print('waiting for block to be mined...')
            time.sleep(20)
            return
        elif (str(e) == "{'code': -32000, 'message': 'insufficient funds for gas * price + value'}"):
            print('waiting for next block and retrying...')
            time.sleep(20)
            return(burn_cash(from_account, amount, nonce_offset=0))
        elif (str(e) == "{'code': -32000, 'message': 'replacement transaction underpriced'}"):
            print('retrying with 10% higher gas price...')
            time.sleep(20)
            return(burn_cash(from_account, amount, gas_scale=1.21 ,nonce_offset=0))
        elif (str(e) == "{'code': -32000, 'message': 'nonce too low'}"):
            print('retrying with nonce offset...')
            time.sleep(20)
            return(burn_cash(from_account, amount, nonce_offset=0))
        return 
    
def send_cash(from_account, to_account, amount, gas_scale=GAS_SCALE, nonce_offset=0):
    balance = get_balance(from_account)
    if amount > balance:
        amount = balance
    print('sending', amount, 'cash from', from_account, 'to', to_account,)
    # checks
    try:
        assert from_account in accounts.keys(), 'Invalid account'
        assert to_account in accounts.keys(), 'Invalid account'
        assert amount >= 1, 'Invalid amount'
        # assert amount <= get_balance(from_account), 'Insufficient balance'
    except AssertionError as e:
        print(e)
        return
    # store account balance before sending
    balance_before = get_balance(from_account)
    try:
        # calculate nonce from keeper address
        nonce = web3.eth.getTransactionCount(keeper_address) + nonce_offset
        # build transaction
        tx = accounts[from_account]['contract'].functions.sendCash(
            accounts[to_account]['address'], 
            int(amount*10**18)).buildTransaction({
                'gas': int(web3.eth.get_block('latest').gasLimit/4),
                'gasPrice': int(web3.eth.gasPrice*gas_scale),
                'from': keeper_address,
                'nonce': nonce,
            })
        # sign transaction
        print('signing transaction...')
        signed_tx = web3.eth.account.signTransaction(tx, private_key=KEEPER_KEY)
        # send transaction
        print('sending transaction...')
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        print('tx hash:', web3.toHex(tx_hash))
        print('waiting for transaction receipt...')
        web3.eth.waitForTransactionReceipt(tx_hash, timeout = np.inf)
        print('transaction completed')

    # error handling
    except Exception as e:
        print(e)
        if(str(e) == "{'code': -32000, 'message': 'already known'}"):
            # wait 300 seconds for block to be mined
            print('waiting for block to be mined...')
            time.sleep(20)
            return
        elif (str(e) == "{'code': -32000, 'message': 'insufficient funds for gas * price + value'}"):
            print('waiting for next block and retrying...')
            time.sleep(20)
            return(send_cash(from_account, to_account, amount, nonce_offset=0))
        elif (str(e) == "{'code': -32000, 'message': 'replacement transaction underpriced'}"):
            print('retrying with 10% higher gas price...')
            time.sleep(20)
            return(send_cash(from_account, to_account, amount, gas_scale=1.21 ,nonce_offset=0))
        elif (str(e) == "{'code': -32000, 'message': 'nonce too low'}"):
            print('retrying with nonce offset...')
            time.sleep(20)
            return(send_cash(from_account, to_account, amount, gas_scale=1.21, nonce_offset=0))
        return 

def get_balance(account):
    #checks
    try:
        assert account in accounts.keys(), 'Invalid account'
    except AssertionError as e:
        print(e)
        return
    return float(cash_contract.functions.balanceOf(accounts[account]['address']).call())/ 10**18

# beer functions
def mint_beer(to_account, amount, gas_scale=GAS_SCALE, nonce_offset=0):
    print('minting', amount, 'BEER to', to_account)
    # checks
    try:
        assert to_account in accounts.keys(), 'Invalid account'
        assert amount >= 1, 'Invalid amount'
    except AssertionError as e:
        print(e)
        return

    try:
        # calculate nonce from keeper address
        nonce = web3.eth.getTransactionCount(keeper_address) + nonce_offset
        # build transaction
        tx = beer_contract.functions.mint(
            accounts[to_account]['address'], 
            int(amount*10**18)).buildTransaction({
                'gas': int(web3.eth.get_block('latest').gasLimit/4),
                'gasPrice': int(web3.eth.gasPrice*gas_scale),
                'from': keeper_address,
                'nonce': nonce,
            })
        # sign transaction
        print('signing transaction...')
        signed_tx = web3.eth.account.signTransaction(tx, private_key=KEEPER_KEY)
        # send transaction  
        print('sending transaction...')
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        print('tx hash:', web3.toHex(tx_hash))

        # sign transaction
        print('signing transaction...')
        signed_tx = web3.eth.account.signTransaction(tx, private_key=KEEPER_KEY)
        # send transaction
        print('sending transaction...')
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        print('tx hash:', web3.toHex(tx_hash))
        print('waiting for transaction receipt...')
        web3.eth.waitForTransactionReceipt(tx_hash, timeout = np.inf)
        print('transaction completed')

    # error handling
    except Exception as e:
        print(e)
        if(str(e) == "{'code': -32000, 'message': 'already known'}"):
            # wait 300 seconds for block to be mined
            print('waiting for block to be mined...')
            time.sleep(20)
            return
        elif (str(e) == "{'code': -32000, 'message': 'insufficient funds for gas * price + value'}"):
            print('waiting for next block and retrying...')
            time.sleep(20)
            return(mint_beer(to_account, amount, nonce_offset=0))
        elif (str(e) == "{'code': -32000, 'message': 'replacement transaction underpriced'}"):
            print('retrying with 10% higher gas price...')
            time.sleep(20)
            return(mint_beer(to_account, amount, gas_scale=1.21 ,nonce_offset=0))
        elif (str(e) == "{'code': -32000, 'message': 'nonce too low'}"):
            print('retrying with nonce offset...')
            time.sleep(20)
            return(mint_beer(to_account, amount, gas_scale=1.21, nonce_offset=0))
        return 

def burn_beer(from_account, amount, gas_scale=GAS_SCALE, nonce_offset=0):
    print('burning', amount, 'BEER from', from_account)
    if amount > get_inventory(from_account):
        amount = get_inventory(from_account)
    # checks
    try:
        assert from_account in accounts.keys(), 'Invalid account'
        # assert amount > 0, 'Invalid amount'
        # assert amount <= get_inventory(from_account), 'Insufficient inventory'
    except AssertionError as e:
        print(e)
        return

    try:
        # calculate nonce from keeper address
        nonce = web3.eth.getTransactionCount(keeper_address) + nonce_offset
        # build transaction
        tx = beer_contract.functions.burn(
            accounts[from_account]['address'], 
            int(int(amount*10**18))).buildTransaction({
                'gas': int(web3.eth.get_block('latest').gasLimit/4),
                'gasPrice': int(web3.eth.gasPrice*gas_scale),
                'from': keeper_address,
                'nonce': nonce,
            })
        # sign transaction
        print('signing transaction...')
        signed_tx = web3.eth.account.signTransaction(tx, private_key=KEEPER_KEY)
        # send transaction
        print('sending transaction...')
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        print('tx hash:', web3.toHex(tx_hash))
        print('waiting for transaction receipt...')
        web3.eth.waitForTransactionReceipt(tx_hash, timeout = np.inf)
        print('transaction completed')
        
    # error handling
    except Exception as e:
        print(e)
        if(str(e) == "{'code': -32000, 'message': 'already known'}"):
            # wait 300 seconds for block to be mined
            print('waiting for block to be mined...')
            time.sleep(20)
            return
        elif (str(e) == "{'code': -32000, 'message': 'insufficient funds for gas * price + value'}"):
            print('waiting for next block and retrying...')
            time.sleep(20)
            return(burn_beer(from_account, amount, nonce_offset=0))
        elif (str(e) == "{'code': -32000, 'message': 'replacement transaction underpriced'}"):
            print('retrying with 10% higher gas price...')
            time.sleep(20)
            return(burn_beer(from_account, amount, gas_scale=1.21 ,nonce_offset=0))
        elif (str(e) == "{'code': -32000, 'message': 'nonce too low'}"):
            print('retrying with nonce offset...')
            time.sleep(20)
            return(burn_beer(from_account, amount, nonce_offset=0))
        return 

def send_beer(from_account, to_account, amount, gas_scale=GAS_SCALE, nonce_offset=0):
    print('sending', amount, 'BEER from', from_account, 'to', to_account)
    inventory = get_inventory(from_account)
    if amount > inventory: 
        amount = inventory
    # checks
    try:
        assert from_account in accounts.keys(), 'Invalid account'
        assert to_account in accounts.keys(), 'Invalid account'
        assert amount >= 1, 'Invalid amount'
        # assert amount <= get_inventory(from_account), 'Insufficient inventory'
    except AssertionError as e:
        print(e)
        return
    
    try:
        # calculate nonce from keeper address
        nonce = web3.eth.getTransactionCount(keeper_address) + nonce_offset
        # build transaction
        tx = accounts[from_account]['contract'].functions.sendBeer(
            accounts[to_account]['address'], 
            int(amount*10**18)).buildTransaction({
                'gas': int(web3.eth.get_block('latest').gasLimit/4),
                'gasPrice': int(web3.eth.gasPrice*gas_scale),
                'from': keeper_address,
                'nonce': nonce,
            })
        # sign transaction
        print('signing transaction...')
        signed_tx = web3.eth.account.signTransaction(tx, private_key=KEEPER_KEY)
        # send transaction
        print('sending transaction...')
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        print('tx hash:', web3.toHex(tx_hash))
        print('waiting for transaction receipt...')
        web3.eth.waitForTransactionReceipt(tx_hash, timeout = np.inf)
        print('transaction completed')
            
    # error handling
    except Exception as e:
        print(e)
        if(str(e) == "{'code': -32000, 'message': 'already known'}"):
            # wait 300 seconds for block to be mined
            print('waiting for block to be mined...')
            time.sleep(20)
            return
        elif (str(e) == "{'code': -32000, 'message': 'insufficient funds for gas * price + value'}"):
            print('waiting for next block and retrying...')
            time.sleep(20)
            return(send_beer(from_account, to_account, amount, nonce_offset=0))
        elif (str(e) == "{'code': -32000, 'message': 'replacement transaction underpriced'}"):
            print('retrying with 10% higher gas price...')
            time.sleep(20)
            return(send_beer(from_account, to_account, amount, gas_scale=1.21 ,nonce_offset=0))
        elif (str(e) == "{'code': -32000, 'message': 'nonce too low'}"):
            print('retrying with nonce offset...')
            time.sleep(20)
            return(send_beer(from_account, to_account, amount, gas_scale=1.21, nonce_offset=0))
        return 

def get_inventory(account):
    # checks
    try:
        assert account in accounts.keys(), 'Invalid account'
    except AssertionError as e:
        print(e)
        return
    return float(beer_contract.functions.balanceOf(accounts[account]['address']).call())/ 10**18

# game functions
def reset_inventories(amount):
    print()
    print('reseting inventories to ', amount, 'BEER...')
    # checks
    try:
        assert amount > 0, 'Invalid amount'
    except AssertionError as e:
        print(e)
        return
    for account in accounts:
        if account != 'market':
            inventory = get_inventory(account)
            print(account, 'inventory: ', inventory)
            if amount < inventory:
                burn_beer(account, inventory-amount)
            elif amount > inventory:
                mint_beer(account, amount-inventory)
            else:
                print('inventory already at', amount)
                continue
        
def reset_balances(amount):
    print()
    print('reseting balances to ', amount, 'CASH...')
    # checks
    try:
        assert amount > 0, 'Invalid amount'
    except AssertionError as e:
        print(e)
        return
    for account in accounts:
        if account != 'market':
            balance = get_balance(account)
            print(account, 'balance: ', balance)
            if amount < balance:
                burn_cash(account, int(balance-amount))
            elif amount > balance:
                mint_cash(account, int(amount-balance))
            else:
                print('balance already at', amount)
                continue

# environment starts here
class BeerGameEnv(Env):
    def __init__(self):
        super(BeerGameEnv, self).__init__()
        # a game runs for 60 rounds
        # 1x continuous integer action space
        # the amount of BEER the agent orders each round 
        self.action_space = Box(low=0, high=200, shape=(1,), dtype=np.int64)
        # 8x continuous float32 observation space
        # own BEER balance
        # own CASH balance
        # own BEER backorder
        # supplier's BEER backorder
        # deliveries made to client
        # deliveries received from supplier
        # BEER requested by client
        # list of previous actions (BEER requested from supplier) (?)
        self.observation_space = Box(low=-np.inf, high=np.inf,
                                     shape=(1,8), dtype=np.float32) 
        
    def step(self, action):   
        # increase round by 1
        self.round += 1
        
        
        '''for account in accounts:
            print(account, get_balance(account), 'CASH')
            print(account, get_inventory(account), 'BEER')

        print('--------------------------------')'''
        
        # check if game is done
        if self.round >= ROUNDS-1:
            # dataframe functionality, may be used in future versions for archiving games
            '''# create a dataframe
            self.df = pd.DataFrame({
            'beer_price': self.beer_price[:ROUNDS-1],
            'demand': self.demand[:ROUNDS-1],

            # inventory and balance
            'manufacturer_inventory': self.manufacturer_inventory[:ROUNDS+1],
            'manufacturer_balance': self.manufacturer_balance[:ROUNDS+1],
            'distributor_inventory': self.distributor_inventory[:ROUNDS+1],
            'distributor_balance': self.distributor_balance[:ROUNDS+1],
            'wholesaler_inventory': self.wholesaler_inventory[:ROUNDS+1],
            'wholesaler_balance': self.wholesaler_balance[:ROUNDS+1],
            'retailer_inventory': self.retailer_inventory[:ROUNDS+1],
            'retailer_balance': self.retailer_balance[:ROUNDS+1],
            'market_inventory': self.market_inventory[:ROUNDS+1],
            'market_balance': self.market_balance[:ROUNDS+1],

            # deliveries (drop last index)
            'deliveries_to_manufacturer': self.deliveries_to_manufacturer[:ROUNDS+1],
            'deliveries_to_distributor': self.deliveries_to_distributor[:ROUNDS+1],
            'deliveries_to_wholesaler': self.deliveries_to_wholesaler[:ROUNDS+1],
            'deliveries_to_wholesaler': self.deliveries_to_wholesaler[:ROUNDS+1],
            'deliveries_to_market': self.deliveries_to_market[:ROUNDS+1],

            # variables for calculating orders
            # base stock
            'base_stock': self.base_stock[:ROUNDS+1],

            # backorders
            'manufacturer_backorder': self.manufacturer_backorder[:ROUNDS+1],
            'distributor_backorder': self.distributor_backorder[:ROUNDS+1],
            'wholesaler_backorder': self.wholesaler_backorder[:ROUNDS+1],
            'retailer_backorder': self.retailer_backorder[:ROUNDS+1],

            # inventory positions
            'manufacturer_position': self.manufacturer_position[:ROUNDS+1],
            'distributor_position': self.distributor_position[:ROUNDS+1],
            'wholesaler_position': self.wholesaler_position[:ROUNDS+1],
            'retailer_position': self.retailer_position[:ROUNDS+1],

            # orders
            'market_demand': self.orders_from_market[:ROUNDS+1],
            'orders_from_retailer': self.orders_from_retailer[:ROUNDS+1],
            'orders_from_wholesaler': self.orders_from_wholesaler[:ROUNDS+1],
            'orders_from_distributor': self.orders_from_distributor[:ROUNDS+1],
            'orders_from_manufacturer': self.orders_from_manufacturer[:ROUNDS+1],

            #expenses
            'retailer_expenses': self.retailer_expenses[:ROUNDS+1],
            'wholesaler_expenses': self.wholesaler_expenses[:ROUNDS+1],
            'distributor_expenses': self.distributor_expenses[:ROUNDS+1],
            'manufacturer_expenses': self.manufacturer_expenses[:ROUNDS+1]
            })'''
            
            self.done = True
            print('Game complete.')
            
        else:
            self.done = False
        
        print('Round', self.round+1, 'of', ROUNDS)
        print()
        for account in accounts:
            print(account)
            print(get_balance(account), 'CASH')
            print(get_inventory(account), 'BEER')
            print()
        
        # store inventories for this round (after deliveries)
        self.manufacturer_inventory.append(get_inventory('manufacturer'))
        self.distributor_inventory.append(get_inventory('distributor'))
        self.wholesaler_inventory.append(get_inventory('wholesaler'))
        self.retailer_inventory.append(get_inventory('retailer'))
        self.market_inventory.append(get_inventory('market'))

        # store balances for this round
        self.manufacturer_balance.append(get_balance('manufacturer'))
        self.distributor_balance.append(get_balance('distributor'))
        self.wholesaler_balance.append(get_balance('wholesaler'))
        self.retailer_balance.append(get_balance('retailer'))
        self.market_balance.append(get_balance('market'))

        # calculate and store backorders
        self.retailer_backorder.append(round(sum(self.orders_from_market) - sum(self.deliveries_to_market)))
        self.wholesaler_backorder.append(round(sum(self.orders_from_retailer) - sum(self.deliveries_to_retailer)))
        self.distributor_backorder.append(round(sum(self.orders_from_wholesaler) - sum(self.deliveries_to_wholesaler)))
        self.manufacturer_backorder.append(round(sum(self.orders_from_distributor) - sum(self.deliveries_to_distributor)))

        # calculate base-stock: average demand from last 4 rounds + safety stock (the forecasted next market demand: last demand * average increase of last 4 rounds)
        safety_stock = 1.5*STARTING_DEMAND
        if self.round < 3: 
            self.base_stock.append(4*np.average(self.demand)+safety_stock)
        else:
            self.base_stock.append(4*np.average(self.demand[-4:])+safety_stock)
        # calculate inventory position
        if self.round == 0:
            self.retailer_position.append(self.retailer_inventory[0])
            self.wholesaler_position.append(self.wholesaler_inventory[0])
            self.distributor_position.append(self.distributor_inventory[0])
            self.manufacturer_position.append(self.manufacturer_inventory[0])
        else:
            # flowlity's equation 
            self.retailer_position.append(round(sum(self.orders_from_retailer[-3:])
                                           + sum(self.wholesaler_backorder[-4:]) - self.retailer_backorder[self.round]))
            
            self.wholesaler_position.append(round(sum(self.orders_from_wholesaler[-3:])
                                             + sum(self.distributor_backorder[-4:]) - self.wholesaler_backorder[self.round]))
            
            self.distributor_position.append(round(sum(self.orders_from_distributor[-3:])
                                              + sum(self.manufacturer_backorder[-4:]) - self.distributor_backorder[self.round]))
            
            self.manufacturer_position.append(round(sum(self.orders_from_manufacturer[-3:])
                                               + sum(self.orders_from_market[-4:]) - self.manufacturer_backorder[self.round]))
        
        # calculate replenishment orders (base-stock policy), order zero if inventory position is greater than the base-stock
        if self.retailer_inventory[self.round] > sum(self.demand[:-4]):
            self.orders_from_market.append(round(self.demand[self.round])) # market demand order from retailer
            self.orders_from_retailer.append(max(0,round((self.base_stock[self.round] - self.retailer_position[self.round])/10)))
            self.orders_from_wholesaler.append(max(0,round((self.base_stock[self.round] - self.wholesaler_position[self.round])/10)))
            self.orders_from_distributor.append(action[0])
            self.orders_from_manufacturer.append(max(0,round((self.base_stock[self.round] - self.manufacturer_position[self.round])/10)))
        else:
            self.orders_from_market.append(round(self.demand[self.round])) # market demand order from retailer
            self.orders_from_retailer.append(max(0,round(self.base_stock[self.round] - self.retailer_position[self.round])))
            self.orders_from_wholesaler.append(max(0,round(self.base_stock[self.round] - self.wholesaler_position[self.round])))
            self.orders_from_distributor.append(action[0])
            self.orders_from_manufacturer.append(max(0,round(self.base_stock[self.round] - self.manufacturer_position[self.round])))
        print('orders:')
        print()
        # send CASH corresponding to orders placed, a 50% markup is applied for each touchpoint in the supply chain
        mint_cash('retailer', self.orders_from_market[self.round]*self.beer_price[self.round]*3) # consumers purchase from retailer
        send_cash('retailer', 'wholesaler', self.orders_from_retailer[self.round]*self.beer_price[self.round]*2.5)
        send_cash('wholesaler', 'distributor', self.orders_from_wholesaler[self.round]*self.beer_price[self.round]*2)        
        send_cash('distributor', 'manufacturer', self.orders_from_distributor[self.round]*self.beer_price[self.round]*1.5)
        burn_cash('manufacturer', self.orders_from_manufacturer[self.round]*self.beer_price[self.round]) # cost to manufacture beer

        # calculate and append expenses
        self.retailer_expenses.append(get_balance('retailer')-self.retailer_balance[self.round])
        self.wholesaler_expenses.append(get_balance('wholesaler')-self.wholesaler_balance[self.round])
        self.distributor_expenses.append(get_balance('distributor')-self.distributor_balance[self.round])
        self.manufacturer_expenses.append(get_balance('manufacturer')-self.manufacturer_balance[self.round])

        # calculate and append deliveries
        self.deliveries_to_manufacturer.append(round(min(get_inventory('market'), self.orders_from_manufacturer[self.round])))
        self.deliveries_to_distributor.append(round(min(get_inventory('manufacturer'), self.orders_from_distributor[self.round] + self.manufacturer_backorder[self.round])))
        self.deliveries_to_wholesaler.append(round(min(get_inventory('distributor'), self.orders_from_wholesaler[self.round] + self.distributor_backorder[self.round])))
        self.deliveries_to_retailer.append(round(min(get_inventory('wholesaler'), self.orders_from_retailer[self.round] + self.wholesaler_backorder[self.round])))
        self.deliveries_to_market.append(round(min(get_inventory('retailer'), self.orders_from_market[self.round] + self.retailer_backorder[self.round])))
        
        print()
        print('deliveries:')
        print()
        # send deliveries 
        mint_beer('manufacturer', self.deliveries_to_manufacturer[self.round])
        send_beer('manufacturer', 'distributor', self.deliveries_to_distributor[self.round])
        send_beer('distributor', 'wholesaler', self.deliveries_to_wholesaler[self.round])
        send_beer('wholesaler', 'retailer', self.deliveries_to_retailer[self.round])
        burn_beer('retailer', self.deliveries_to_market[self.round])

        # write to text logs (used for live graphs)
        with open('data/inventory.txt', 'a') as file:
            file.write(str(self.round)+', '+str(self.retailer_inventory[self.round])+', '+str(self.wholesaler_inventory[self.round])+
                       ', '+str(self.distributor_inventory[self.round])+', '+str(self.manufacturer_inventory[self.round])+'\n')
            
        with open('data/order.txt', 'a') as file:
            file.write(str(self.round)+', '+str(self.orders_from_market[self.round])+', '+str(self.orders_from_retailer[self.round])+', '+str(self.orders_from_wholesaler[self.round])+
                       ', '+str(self.orders_from_distributor[self.round])+', '+str(self.orders_from_manufacturer[self.round])+'\n')
            
        with open('data/backorder.txt', 'a') as file:
            file.write(str(self.round)+', '+str(self.retailer_backorder[self.round])+', '+str(self.wholesaler_backorder[self.round])+
                       ', '+str(self.distributor_backorder[self.round])+', '+str(self.manufacturer_backorder[self.round])+'\n')
            
        with open('data/balance.txt', 'a') as file:
            file.write(str(self.round)+', '+str(self.retailer_balance[self.round])+', '+str(self.wholesaler_balance[self.round])+
                       ', '+str(self.distributor_balance[self.round])+', '+str(self.manufacturer_balance[self.round])+'\n')

        # reward function
        self.reward = (self.deliveries_to_wholesaler[self.round]-self.orders_from_wholesaler[self.round]) - self.distributor_backorder[self.round]+ (self.distributor_balance[self.round]-self.distributor_balance[self.round-1])/self.beer_price[self.round]
        
        print()
        print('Observations:')
        print('Inventory:',self.observation[0])
        print('Balance:',self.observation[1])
        print('Client Order:',self.observation[2])
        print('Own Order:',self.observation[3])
        print('Own Backorder:',self.observation[4])
        print('Supplier Backorder:',self.observation[5])
        print('Deliveries Received:',self.observation[6])
        print('Deliveries Made:',self.observation[7])
        print('Distributor agent action: order ', action, ' BEER')
        print()
    
        # set placeholder info
        info = {}

        # normalize observations
        normalized_inventory = (self.distributor_inventory[self.round])/300
        normalized_balance = (self.distributor_balance[self.round])/20000
        normalized_client_order = (self.orders_from_wholesaler[self.round])/150                            
        normalized_action = (self.orders_from_distributor[self.round])/150 
        normalized_own_backorder = (self.distributor_backorder[self.round])/150
        normalized_supplier_backorder = (self.manufacturer_backorder[self.round])/150
        normalized_deliveries_received = (self.deliveries_to_distributor[self.round])/150
        normalized_deliveries_made = (self.deliveries_to_wholesaler[self.round])/150

        # set observation
        self.observation = [normalized_inventory, normalized_balance, normalized_client_order, normalized_action, normalized_own_backorder, normalized_supplier_backorder, normalized_deliveries_received, normalized_deliveries_made]
        
        self.observation = np.array(self.observation, dtype=object)
        
        # return step info
        return self.observation, self.reward, self.done, info
    
    def render(self):
        pass
    
    def reset(self):
        reset_balances(STARTING_BALANCE)
        reset_inventories(STARTING_INVENTORY)
        
        # clear text files (used for animated plots)
        open('data/inventory.txt', 'w').close()
        open('data/order.txt', 'w').close()
        open('data/backorder.txt', 'w').close()
        open('data/round.txt', 'w').close()
        open('data/balance.txt', 'w').close()
        
        # VARIABLES
        # used for indexing
        self.round_index = []
        # demand
        self.demand = []
        # base stock
        self.base_stock = []
        # inventories
        self.manufacturer_inventory = []
        self.distributor_inventory = []
        self.wholesaler_inventory = []
        self.retailer_inventory = []
        self.market_inventory = []
        # balances
        self.manufacturer_balance = []
        self.distributor_balance = []
        self.wholesaler_balance = []
        self.retailer_balance = []
        self.market_balance = []
        # deliveries 
        self.deliveries_to_manufacturer = []
        self.deliveries_to_distributor = []
        self.deliveries_to_wholesaler = []
        self.deliveries_to_retailer = []
        self.deliveries_to_market = []
        # orders 
        self.orders_from_market = []
        self.orders_from_retailer = []
        self.orders_from_wholesaler = []
        self.orders_from_distributor = []
        self.orders_from_manufacturer = []
        # inventory positions
        self.retailer_position = []
        self.wholesaler_position = []
        self.distributor_position = []
        self.manufacturer_position = []
        # backorder
        self.retailer_backorder = []
        self.wholesaler_backorder = []
        self.distributor_backorder = []
        self.manufacturer_backorder = []
        # expenses
        self.retailer_expenses = []
        self.wholesaler_expenses = []
        self.distributor_expenses = []
        self.manufacturer_expenses = []    
        
        # geometric brownian motion for demand and BEER price
        self.demand = GBM(STARTING_DEMAND, 0.4, 0.25, 1/ROUNDS, 1).prices
        self.beer_price = GBM(STARTING_BEER_PRICE, 0.24, 0.4, 1/ROUNDS, 1).prices
        
        # set round to -1 (so that it starts at 0)
        self.round = -1
        self.done = False
        
        # set observation
        self.observation = [0,0,0,0,0,0,0,0]
        self.observation = np.array(self.observation, dtype=object)
        
        return self.observation