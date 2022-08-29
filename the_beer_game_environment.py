'''
a custom reinforcement learning environment in accordance with openai's gym framework for the beer game
'''
# environment libraries
from gym import Env
from gym.spaces import Box
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# game libraries
from web3 import Web3
from ethtoken.abi import EIP20_ABI
import numpy as np
import matplotlib.pyplot as plt
from gbm import GBM

# global variables
STARTING_DEMAND = 10
STARTING_BALANCE = 10_000
STARTING_INVENTORY = 10
STARTING_BEER_PRICE = 0.005
ROUNDS = 62

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

            
'''
███████ ███    ██ ██    ██ ██ ██████   ██████  ███    ██ ███    ███ ███████ ███    ██ ████████ 
██      ████   ██ ██    ██ ██ ██   ██ ██    ██ ████   ██ ████  ████ ██      ████   ██    ██    
█████   ██ ██  ██ ██    ██ ██ ██████  ██    ██ ██ ██  ██ ██ ████ ██ █████   ██ ██  ██    ██    
██      ██  ██ ██  ██  ██  ██ ██   ██ ██    ██ ██  ██ ██ ██  ██  ██ ██      ██  ██ ██    ██    
███████ ██   ████   ████   ██ ██   ██  ██████  ██   ████ ██      ██ ███████ ██   ████    ██    
                                                                                               
'''

class BeerGameEnv(Env):
    def __init__(self):
        super(BeerGameEnv, self).__init__()
        # a game runs for 60 rounds
        # 1x continuous integer action space
        # the amount of BEER the agent orders each round 
        self.action_space = Box(low=0, high=100, shape=(1,), dtype=np.int64)
        # 8x continuous float32 observation space
        # own BEER balance
        # own ETH balance
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
            print(account, get_balance(account), 'ETH')
            print(account, get_inventory(account), 'BEER')

        print('--------------------------------')'''
        
        # check if game is done
        if self.round >= ROUNDS-1:

            # create a dataframe
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
            })
            
            self.done = True
            print('Game complete.')
            
        else:
            self.done = False
        
        print('Round', self.round+1, 'of', ROUNDS)
        
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

        # send ETH corresponding to orders placed, a 50% markup is applied for each touchpoint in the supply chain
        send_eth('market', 'retailer', self.orders_from_market[self.round]*self.beer_price[self.round]*3) # consumers purchase from retailer
        send_eth('retailer', 'wholesaler', self.orders_from_retailer[self.round]*self.beer_price[self.round]*2.5)
        send_eth('wholesaler', 'distributor', self.orders_from_wholesaler[self.round]*self.beer_price[self.round]*2)        
        send_eth('distributor', 'manufacturer', self.orders_from_distributor[self.round]*self.beer_price[self.round]*1.5)
        send_eth('manufacturer', 'market', self.orders_from_manufacturer[self.round]*self.beer_price[self.round]) # cost to manufacture beer

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
        
        # send deliveries 
        send_beer('market', 'manufacturer', self.deliveries_to_manufacturer[self.round])
        send_beer('manufacturer', 'distributor', self.deliveries_to_distributor[self.round])
        send_beer('distributor', 'wholesaler', self.deliveries_to_wholesaler[self.round])
        send_beer('wholesaler', 'retailer', self.deliveries_to_retailer[self.round])
        send_beer('retailer', 'market', self.deliveries_to_market[self.round])

        # write to text logs (used for live graphs)
        with open('inventory.txt', 'a') as file:
            file.write(str(self.round)+', '+str(self.retailer_inventory[self.round])+', '+str(self.wholesaler_inventory[self.round])+
                       ', '+str(self.distributor_inventory[self.round])+', '+str(self.manufacturer_inventory[self.round])+'\n')
            
        with open('order.txt', 'a') as file:
            file.write(str(self.round)+', '+str(self.orders_from_market[self.round])+', '+str(self.orders_from_retailer[self.round])+', '+str(self.orders_from_wholesaler[self.round])+
                       ', '+str(self.orders_from_distributor[self.round])+', '+str(self.orders_from_manufacturer[self.round])+'\n')
            
        with open('backorder.txt', 'a') as file:
            file.write(str(self.round)+', '+str(self.retailer_backorder[self.round])+', '+str(self.wholesaler_backorder[self.round])+
                       ', '+str(self.distributor_backorder[self.round])+', '+str(self.manufacturer_backorder[self.round])+'\n')
            
        # reward functions
        self.reward = -1*self.distributor_backorder[self.round] + (self.deliveries_to_wholesaler[self.round]-self.orders_from_wholesaler[self.round]) + 0.8*(self.distributor_balance[self.round]-self.distributor_balance[self.round-1])/self.beer_price[self.round] - 0.8*abs(sum(self.orders_from_wholesaler[-4:])-self.distributor_inventory[self.round])
        
        print(self.observation)
        '''print('Inventory:',self.observation[0])
        print('Balance:',self.observation[1])
        print('Client Order:',self.observation[2])
        print('Own Order:',self.observation[3])
        print('Own Backorder:',self.observation[4])
        print('Supplier Backorder:',self.observation[5])
        print('Deliveries Received:',self.observation[6])
        print('Deliveries Made:',self.observation[7])'''
        print(action)
        print('--------------------------')
        
        # print('market orders',self.orders_from_market)
        # print('retailer orders',self.orders_from_retailer)
        # print('wholesaler orders',self.orders_from_wholesaler)
        # print('distributor orders',self.orders_from_distributor)
        # print('manufacturer orders',self.orders_from_manufacturer)
    
        # set placeholder info
        info = {}

        # normalize observations
        normalized_inventory = (self.distributor_inventory[self.round])/300
        normalized_balance = (self.distributor_balance[self.round])/15000
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
        open('inventory.txt', 'w').close()
        open('order.txt', 'w').close()
        open('backorder.txt', 'w').close()
        
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
        self.beer_price = GBM(STARTING_BEER_PRICE, 0.8, 0.5, 1/ROUNDS, 1).prices
        
        # set round to zero
        self.round = -1
        
        self.done = False
        
        # set observation
        self.observation = [0,0,0,0,0,0,0,0]
        
        self.observation = np.array(self.observation, dtype=object)
        
        return self.observation