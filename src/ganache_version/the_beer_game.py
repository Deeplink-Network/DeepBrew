'''
run this script to watch four base-stock agents play the beer game with one another
plots summarising the game will be displayed after the rounds are completed
'''
# libraries
from web3 import Web3
from ethtoken.abi import EIP20_ABI
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from gbm import GBM

# connect to ganache
ganache_url = 'HTTP://127.0.0.1:8545'
web3 = Web3(Web3.HTTPProvider(ganache_url))

# accounts dictionary
# mnemonic: myth like bonus scare over problem client lizard pioneer submit female collect
accounts = {
    'manufacturer': {
        'address': '0xFE41FE950d4835bD539AC24fBaaDED16b2E32922',
        'private_key': '0x4d8631d58af474e97e8646472077626207ed5c32a0a956b256811401e756f1a3'
                    },
    'distributor':  {
        'address': '0x45928E9F64590F28c964E1d73a01Ad0311896b4B',
        'private_key': '0x4836c020dedd3e96f1ebfdb55986e1d7aeac5bf26bf154550da87a1e5e34049d'
                    },
    'wholesaler': {
        'address': '0x7c66F5C9e97aC36B181BFE17CFB6303EE32C270e',
        'private_key': '0xd189172812b452424cc60aa57f6c6321c3f552ac45dedb0a6baa20419963326e'
    },
    'retailer': {
        'address': '0xc1ba023e51396C0e9891026736BcaB4ecfB587E3',
        'private_key': '0x103cafa8c177c0eb9eeee852fc3e3b24a0869a59a91df78527abeef9f719eba7'        
    },
    'market': {
        'address': '0x6CDf8da55Ba3b54D52d1F21392cc2409b1153E88',
        'private_key': '0xce4b3f8a6364c266b2a155acc16b379451e50c5e54eccfb119474943447a9f30'
    }
}
# BEER functions
# ERC20 contract address (DeepBrew, BEER)
# need to find a way to grab the contract address with code rather than manually
deepbrew_contract = Web3.toChecksumAddress('0x6dF43d5EFD4ddE3cC72EDf36F012A5c390b628aC')

# ERC20 contract object
deepbrew = web3.eth.contract(address=deepbrew_contract, abi=EIP20_ABI)

# returns the BEER balance of a given account
# INPUTS: account NAME, as a string, e.g. 'manufacturer'
def get_inventory(account):
    return float(deepbrew.functions.balanceOf(accounts[account]['address']).call())

'''
used to send BEER from one wallet to another
INPUTS
from_account: string, name of the account sending
to_account: string, name of the account receiving
amount: integer, amount to be sent in BEER
'''
def send_beer(from_account, to_account, amount):
    ret = max(0, amount - get_inventory(from_account))
    if amount == 0:
        return
    nonce = web3.eth.getTransactionCount(accounts[from_account]['address'])

    deepbrew_txn = deepbrew.functions.transfer(
        accounts[to_account]['address'],
        # send as much as possible in account, no more
        round(min(get_inventory(from_account), amount)), # round because ERC20 can't be divided, thus can only be traded in integer quantities
    ).buildTransaction({
        'gas': 70000,
        'gasPrice': web3.toWei('50', 'gwei'),
        'nonce': nonce,
    })

    signed_txn = web3.eth.account.signTransaction(deepbrew_txn, accounts[from_account]['private_key'])
    signed_txn.hash
    signed_txn.rawTransaction
    signed_txn.r
    signed_txn.s
    signed_txn.v
    web3.eth.sendRawTransaction(signed_txn.rawTransaction) 
    web3.toHex(web3.sha3(signed_txn.rawTransaction))
    
    # if amount to send is greater than inventory of sender, return the difference, else return 0
    return ret

'''
function called at the start of each round to return agent inventory to initial conditions
INPUTS
balance: the desired starting inventory for each agent in BEER
'''
def reset_inventories(inventory):
    # send all current inventory to the market
    for account in accounts:
        if account != 'market' and deepbrew.functions.balanceOf(accounts[account]['address']).call() != 0:
            send_beer(account, 'market', deepbrew.functions.balanceOf(accounts[account]['address']).call())
    for account in accounts:
        if account != 'market':
            send_beer('market', account, inventory)

# ETH functions

# returns the ETH balance of a given account
# INPUTS: account NAME, as a string, e.g. 'manufacturer'
def get_balance(account):
    return float(web3.fromWei(web3.eth.getBalance(accounts[account]['address']), 'ether'))

'''
used to send eth from one wallet to another
INPUTS
from_account: string, name of the account sending
to_account: string, name of the account receiving
amount: integer, amount to be sent in ETH
'''
def send_eth(from_account, to_account, amount):
    if amount == 0:
        return
    # calculate nonce from sender account
    nonce = web3.eth.getTransactionCount(accounts[from_account]['address'])
    #build tx
    tx = {
        'nonce': nonce,
        'to': accounts[to_account]['address'],
        'value': web3.toWei(amount, 'ether'),
        'gas': 200000,
        'gasPrice': web3.toWei('50', 'gwei')
    }
    # sign the transaction
    singed_tx = web3.eth.account.signTransaction(tx, accounts[from_account]['private_key'])
    # send transaction
    tx_hash = web3.eth.sendRawTransaction(singed_tx.rawTransaction)
    # get transaction hash
    # print("Transaction hash: ", web3.toHex(tx_hash))
    # print latest block number
    # print("Block numbers: ", web3.eth.block_number)

'''
function called at the start of each round to return agent balances to initial conditions
INPUTS
balance: the desired starting balance for each agent in ETH
'''
def reset_balances(balance):
    # send all current balances to the market
    for account in accounts:
        if account != 'market':
            # if the agent has more than 1 ETH, send all but 1 ETH to market to cover gas
            if web3.fromWei(web3.eth.getBalance(accounts[account]['address']), 'ether') >= 1: 
                send_eth(account, 'market', (web3.fromWei(web3.eth.getBalance(accounts[account]['address']), 'ether')-1))
            # if the agent has less than 1 ETH, the market sends them the amount such that they now have 1 ETH
            else:
                send_eth('market', account, 1-(web3.fromWei(web3.eth.getBalance(accounts[account]['address']), 'ether')))
                
    # redistribute desired ETH to each agent
    for account in accounts:
        if account != 'market' and balance != 1: # need to leave behind 1 ETH to cover gas fees, in the event that desired balance is 1, send nothing back
            send_eth('market', account, balance-1) # send back the desired amount -1 

# game functions
def the_beer_game(starting_balance, starting_inventory, starting_beer_price, starting_demand, rounds):
    # reset balances and inventories
    reset_balances(starting_balance)
    reset_inventories(starting_inventory)
    # VARIABLES
    # demand
    demand = []
    # base stock
    base_stock = []
    # inventories
    manufacturer_inventory = []
    distributor_inventory = []
    wholesaler_inventory = []
    retailer_inventory = []
    market_inventory = []
    # balances
    manufacturer_balance = []
    distributor_balance = []
    wholesaler_balance = []
    retailer_balance = []
    market_balance = []
    # deliveries 
    deliveries_to_manufacturer = []
    deliveries_to_distributor = []
    deliveries_to_wholesaler = []
    deliveries_to_retailer = []
    deliveries_to_market = []
    # orders 
    orders_from_market = []
    orders_from_retailer = []
    orders_from_wholesaler = []
    orders_from_distributor = []
    orders_from_manufacturer = []
    # inventory positions
    retailer_position = []
    wholesaler_position = []
    distributor_position = []
    manufacturer_position = []
    # backorder
    retailer_backorder = []
    wholesaler_backorder = []
    distributor_backorder = []
    manufacturer_backorder = []
    # expenses
    retailer_expenses = []
    wholesaler_expenses = []
    distributor_expenses = []
    manufacturer_expenses = []
    
    # geometric brownian motion for demand and BEER price
    demand = GBM(starting_demand, 0.9, 0.9, 1/rounds, 1).prices
    beer_price = GBM(starting_beer_price, 0.8, 0.5, 1/rounds, 1).prices
    
    for i in range(rounds):
        
        print('Round', i+1, 'of', rounds)
    
        # store inventories for this i (after deliveries)
        manufacturer_inventory.append(get_inventory('manufacturer'))
        distributor_inventory.append(get_inventory('distributor'))
        wholesaler_inventory.append(get_inventory('wholesaler'))
        retailer_inventory.append(get_inventory('retailer'))
        market_inventory.append(get_inventory('market'))

        # store balances for this i
        manufacturer_balance.append(get_balance('manufacturer'))
        distributor_balance.append(get_balance('distributor'))
        wholesaler_balance.append(get_balance('wholesaler'))
        retailer_balance.append(get_balance('retailer'))
        market_balance.append(get_balance('market'))

        # calculate and store backorders
        retailer_backorder.append(round(sum(orders_from_market) - sum(deliveries_to_market)))
        wholesaler_backorder.append(round(sum(orders_from_retailer) - sum(deliveries_to_retailer)))
        distributor_backorder.append(round(sum(orders_from_wholesaler) - sum(deliveries_to_wholesaler)))
        manufacturer_backorder.append(round(sum(orders_from_distributor) - sum(deliveries_to_distributor)))

        # calculate base-stock: average demand from last 4 rounds + safety stock (the forecasted next market demand: last demand * average increase of last 4 rounds)
        safety_stock = 1.5*starting_demand
        if i < 3: 
            base_stock.append(4*np.average(demand)+safety_stock)
        else:
            base_stock.append(4*np.average(demand[-4:])+safety_stock)
        # calculate inventory position
        if i == 0:
            retailer_position.append(retailer_inventory[0])
            wholesaler_position.append(wholesaler_inventory[0])
            distributor_position.append(distributor_inventory[0])
            manufacturer_position.append(manufacturer_inventory[0])
        else:
            '''
            # my equation
            retailer_position.append(round(retailer_inventory[i] + orders_from_retailer[i-1] + wholesaler_backorder[i] - orders_from_market[i-1] - retailer_backorder[i]))
            wholesaler_position.append(round(wholesaler_inventory[i] + orders_from_wholesaler[i-1] + distributor_backorder[i-1] - orders_from_retailer[i-1] - wholesaler_backorder[i]))
            distributor_position.append(round(distributor_inventory[i] + orders_from_distributor[i-1] + manufacturer_backorder[i] - orders_from_wholesaler[i-1] - distributor_backorder[i]))
            manufacturer_position.append(round(manufacturer_inventory[i] + orders_from_manufacturer[i-1] - orders_from_distributor[i-1] - manufacturer_backorder[i])) # manufacturer's supplier (market) has no backorder
            '''
            # flowlity's equation 
            retailer_position.append(round(sum(orders_from_retailer[-3:]) + sum(wholesaler_backorder[-4:]) - retailer_backorder[i]))
            wholesaler_position.append(round(sum(orders_from_wholesaler[-3:]) + sum(distributor_backorder[-4:]) - wholesaler_backorder[i]))
            distributor_position.append(round(sum(orders_from_distributor[-3:]) + sum(manufacturer_backorder[-4:]) - distributor_backorder[i]))
            manufacturer_position.append(round(sum(orders_from_manufacturer[-3:]) + sum(orders_from_distributor[-4:]) - manufacturer_backorder[i]))
            

        # calculate replenishment orders (base-stock policy), order zero if inventory position is higher than the base-stock
        orders_from_market.append(demand[i]) # market demand order from retailer
        orders_from_retailer.append(max(0,round(base_stock[i] - retailer_position[i])))
        orders_from_wholesaler.append(max(0,round(base_stock[i] - wholesaler_position[i])))
        orders_from_distributor.append(max(0, round(base_stock[i] - distributor_position[i])))
        orders_from_manufacturer.append(max(0,round(base_stock[i] - manufacturer_position[i])))

        # send ETH corresponding to orders placed, a 50% markup is applied for each touchpoint in the supply chain
        send_eth('market', 'retailer', orders_from_market[i]*beer_price[i]*3) # consumers purchase from retailer
        send_eth('retailer', 'wholesaler', orders_from_retailer[i]*beer_price[i]*2.5)
        send_eth('wholesaler', 'distributor', orders_from_wholesaler[i]*beer_price[i]*2)        
        send_eth('distributor', 'manufacturer', orders_from_distributor[i]*beer_price[i]*1.5)
        send_eth('manufacturer', 'market', orders_from_manufacturer[i]*beer_price[i]) # cost to manufacture beer

        # calculate and append expenses
        retailer_expenses.append(get_balance('retailer')-retailer_balance[i])
        wholesaler_expenses.append(get_balance('wholesaler')-wholesaler_balance[i])
        distributor_expenses.append(get_balance('distributor')-distributor_balance[i])
        manufacturer_expenses.append(get_balance('manufacturer')-manufacturer_balance[i])

        # calculate and append deliveries for next round
        deliveries_to_manufacturer.append(round(min(get_inventory('market'), orders_from_manufacturer[i])))
        deliveries_to_distributor.append(round(min(get_inventory('manufacturer'), orders_from_distributor[i] + manufacturer_backorder[i])))
        deliveries_to_wholesaler.append(round(min(get_inventory('distributor'), orders_from_wholesaler[i] + distributor_backorder[i])))
        deliveries_to_retailer.append(round(min(get_inventory('wholesaler'), orders_from_retailer[i] + wholesaler_backorder[i])))
        deliveries_to_market.append(round(min(get_inventory('retailer'), orders_from_market[i] + retailer_backorder[i])))

        # send deliveries 
        send_beer('market', 'manufacturer', deliveries_to_manufacturer[i])
        send_beer('manufacturer', 'distributor', deliveries_to_distributor[i])
        send_beer('distributor', 'wholesaler', deliveries_to_wholesaler[i])
        send_beer('wholesaler', 'retailer', deliveries_to_retailer[i])
        send_beer('retailer', 'market', deliveries_to_market[i])
        
        for account in accounts:
            print(account, get_balance(account), 'ETH')
            print(account, get_inventory(account), 'BEER')

        print('--------------------------------')

        if i == rounds-1:
            print('Game complete.')

    # create a dataframe to track game variables
    df = pd.DataFrame({
        'beer_price': beer_price[:rounds],
        'demand': demand[:rounds],

        # inventory and balance
        'manufacturer_inventory': manufacturer_inventory[:rounds],
        'manufacturer_balance': manufacturer_balance[:rounds],
        'distributor_inventory': distributor_inventory[:rounds],
        'distributor_balance': distributor_balance[:rounds],
        'wholesaler_inventory': wholesaler_inventory[:rounds],
        'wholesaler_balance': wholesaler_balance[:rounds],
        'retailer_inventory': retailer_inventory[:rounds],
        'retailer_balance': retailer_balance[:rounds],
        'market_inventory': market_inventory[:rounds],
        'market_balance': market_balance[:rounds],

        # deliveries (drop last index)
        'deliveries_to_manufacturer': deliveries_to_manufacturer[:rounds],
        'deliveries_to_distributor': deliveries_to_distributor[:rounds],
        'deliveries_to_wholesaler': deliveries_to_wholesaler[:rounds],
        'deliveries_to_wholesaler': deliveries_to_wholesaler[:rounds],
        'deliveries_to_market': deliveries_to_market[:rounds],

        # variables for calculating orders
        # base stock
        'base_stock': base_stock[:rounds],

        # backorders
        'manufacturer_backorder': manufacturer_backorder[:rounds],
        'distributor_backorder': distributor_backorder[:rounds],
        'wholesaler_backorder': wholesaler_backorder[:rounds],
        'retailer_backorder': retailer_backorder[:rounds],

        # inventory positions
        'manufacturer_position': manufacturer_position[:rounds],
        'distributor_position': distributor_position[:rounds],
        'wholesaler_position': wholesaler_position[:rounds],
        'retailer_position': retailer_position[:rounds],

        # orders
        'market_demand': orders_from_market[:rounds],
        'orders_from_retailer': orders_from_retailer[:rounds],
        'orders_from_wholesaler': orders_from_wholesaler[:rounds],
        'orders_from_distributor': orders_from_distributor[:rounds],
        'orders_from_manufacturer': orders_from_manufacturer[:rounds],

        #expenses
        'retailer_expenses': retailer_expenses[:rounds],
        'wholesaler_expenses': wholesaler_expenses[:rounds],
        'distributor_expenses': distributor_expenses[:rounds],
        'manufacturer_expenses': manufacturer_expenses[:rounds]
        })
    # save match log to excel and return
    # df.to_excel('match.xlsx')
    return df

if __name__ == '__main__':
    # check ganache connection
    if web3.isConnected():
        print('Successfully connected to Ganache test-net.')
        print('--------------------------------')
    else:
        sys.exit('Connection to Ganache unsuccessful.')
    
    # the_beer_game(starting_balance, starting_inventory, beer_price, starting_demand, rounds)
    df = the_beer_game(250000, 10, 0.005, 10, 5)
    df.plot(y=['orders_from_manufacturer','orders_from_distributor','orders_from_wholesaler','orders_from_retailer','market_demand']) 
    plt.xlabel('Round')
    plt.ylabel('Orders')
    df.plot(y=['manufacturer_backorder','distributor_backorder','wholesaler_backorder','retailer_backorder']) 
    plt.xlabel('Round')
    plt.ylabel('Backorder (BEER)')
    df.plot(y=['manufacturer_inventory','distributor_inventory','wholesaler_inventory','retailer_inventory']) 
    plt.xlabel('Round')
    plt.ylabel('Inventory (BEER)')
    df.plot(y=['manufacturer_balance','distributor_balance','wholesaler_balance','retailer_balance'])
    plt.xlabel('Round')
    plt.ylabel('ETH Balance')
    df.plot(y=['manufacturer_expenses','distributor_expenses','wholesaler_expenses','retailer_expenses'])
    plt.xlabel('Round')
    plt.ylabel('Profit and Loss (ETH)')
    plt.show()