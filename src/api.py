from flask import *
import json

app = Flask(__name__)
    
@app.route('/orders', methods=['GET'])
def order():
    round = []
    orders_from_market = []
    orders_from_retailer = []
    orders_from_wholesaler = []
    orders_from_distributor = []
    orders_from_manufacturer = []
    
    order_data = open('data/order.txt', 'r').read()
    order_data_array = order_data.split('\n')
    
    for order_line in order_data_array:
        if len(order_line)>1:
            # split by comma
            i, md, ro, wo, do, mo = order_line.split(',')
            round.append(int(i)+1)
            orders_from_market.append(float(md))
            orders_from_retailer.append(float(ro))
            orders_from_wholesaler.append(float(wo))
            orders_from_distributor.append(float(do))
            orders_from_manufacturer.append(float(mo))
            
    # convert the string arrays into int arrays
    round = [int(i) for i in round]
    orders_from_market = [float(i) for i in orders_from_market]
    orders_from_retailer = [float(i) for i in orders_from_retailer]
    orders_from_wholesaler = [float(i) for i in orders_from_wholesaler]
    orders_from_distributor = [float(i) for i in orders_from_distributor]
    orders_from_manufacturer = [float(i) for i in orders_from_manufacturer]
    
    # remove the last element of each array
    round.pop()
    orders_from_market.pop()
    orders_from_retailer.pop()
    orders_from_wholesaler.pop()
    orders_from_distributor.pop()
    orders_from_manufacturer.pop()
            
    data_set = {'Round': round,
                'Manufacturer Orders': orders_from_manufacturer,
                'Distributor Orders': orders_from_distributor,
                'Wholesaler Orders': orders_from_wholesaler,
                'Manufacturer Orders': orders_from_manufacturer}
    
    json_dump = json.dumps(data_set)
        
    return json_dump

@app.route('/inventories', methods=['GET'])
def inventory():
    round = []
    inventory_at_market = []
    inventory_at_retailer = []
    inventory_at_wholesaler = []
    inventory_at_distributor = []
    inventory_at_manufacturer = []
    
    inventory_data = open('data/inventory.txt', 'r').read()
    inventory_data_array = inventory_data.split('\n')
    
    for inventory_line in inventory_data_array:
        if len(inventory_line)>1:
            # split by comma
            i, md, ro, wo, do, mo = inventory_line.split(',')
            round.append(int(i)+1)
            inventory_at_market.append(float(md))
            inventory_at_retailer.append(float(ro))
            inventory_at_wholesaler.append(float(wo))
            inventory_at_distributor.append(float(do))
            inventory_at_manufacturer.append(float(mo))
            
    # convert the string arrays into int arrays
    round = [int(i) for i in round]
    inventory_at_market = [float(i) for i in inventory_at_market]
    inventory_at_retailer = [float(i) for i in inventory_at_retailer]
    inventory_at_wholesaler = [float(i) for i in inventory_at_wholesaler]
    inventory_at_distributor = [float(i) for i in inventory_at_distributor]
    inventory_at_manufacturer = [float(i) for i in inventory_at_manufacturer]
    
    # remove the last element of each array
    round.pop()
    inventory_at_market.pop()
    inventory_at_retailer.pop()
    inventory_at_wholesaler.pop()
    inventory_at_distributor.pop()
    inventory_at_manufacturer.pop()
            
    data_set = {'Round': round,
                'Manufacturer Inventory': inventory_at_manufacturer,
                'Distributor Inventory': inventory_at_distributor,
                'Wholesaler Inventory': inventory_at_wholesaler,
                'Manufacturer Inventory': inventory_at_manufacturer}
    
    json_dump = json.dumps(data_set)
        
    return json_dump

@app.route('/backorders', methods=['GET'])
def backorder():
    round = []
    backorder_at_market = []
    backorder_at_retailer = []
    backorder_at_wholesaler = []
    backorder_at_distributor = []
    backorder_at_manufacturer = []
    
    backorder_data = open('data/backorder.txt', 'r').read()
    backorder_data_array = backorder_data.split('\n')
    
    for backorder_line in backorder_data_array:
        if len(backorder_line)>1:
            # split by comma
            i, md, ro, wo, do, mo = backorder_line.split(',')
            round.append(int(i)+1)
            backorder_at_market.append(float(md))
            backorder_at_retailer.append(float(ro))
            backorder_at_wholesaler.append(float(wo))
            backorder_at_distributor.append(float(do))
            backorder_at_manufacturer.append(float(mo))
            
    # convert the string arrays into int arrays
    round = [int(i) for i in round]
    backorder_at_market = [float(i) for i in backorder_at_market]
    backorder_at_retailer = [float(i) for i in backorder_at_retailer]
    backorder_at_wholesaler = [float(i) for i in backorder_at_wholesaler]
    backorder_at_distributor = [float(i) for i in backorder_at_distributor]
    backorder_at_manufacturer = [float(i) for i in backorder_at_manufacturer]
    
    # remove the last element of each array
    round.pop()
    backorder_at_market.pop()
    backorder_at_retailer.pop()
    backorder_at_wholesaler.pop()
    backorder_at_distributor.pop()
    backorder_at_manufacturer.pop()

    data_set = {'Round': round,
                'Manufacturer Backorder': backorder_at_manufacturer,
                'Distributor Backorder': backorder_at_distributor,
                'Wholesaler Backorder': backorder_at_wholesaler,
                'Manufacturer Backorder': backorder_at_manufacturer}
    
    json_dump = json.dumps(data_set)

    return json_dump

@app.route('/balances', methods=['GET'])
def balance():  
    round = []
    balance_at_market = []
    balance_at_retailer = []
    balance_at_wholesaler = []
    balance_at_distributor = []
    balance_at_manufacturer = []
    
    balance_data = open('data/balance.txt', 'r').read()
    balance_data_array = balance_data.split('\n')
    
    for balance_line in balance_data_array:
        if len(balance_line)>1:
            # split by comma
            i, ro, wo, do, mo = balance_line.split(',')
            round.append(int(i)+1)
            balance_at_retailer.append(float(ro))
            balance_at_wholesaler.append(float(wo))
            balance_at_distributor.append(float(do))
            balance_at_manufacturer.append(float(mo))
            
    # convert the string arrays into int arrays
    round = [int(i) for i in round]
    balance_at_market = [float(i) for i in balance_at_market]
    balance_at_retailer = [float(i) for i in balance_at_retailer]
    balance_at_wholesaler = [float(i) for i in balance_at_wholesaler]
    balance_at_distributor = [float(i) for i in balance_at_distributor]
    balance_at_manufacturer = [float(i) for i in balance_at_manufacturer]
    
    # remove the last element of each array
    round.pop()
    balance_at_retailer.pop()
    balance_at_wholesaler.pop()
    balance_at_distributor.pop()
    balance_at_manufacturer.pop()
            
    data_set = {'Round': round,
                'Manufacturer Balance': balance_at_manufacturer,
                'Distributor Balance': balance_at_distributor,
                'Wholesaler Balance': balance_at_wholesaler,
                'Manufacturer Balance': balance_at_manufacturer}
    
    json_dump = json.dumps(data_set)
        
    return json_dump
                                
if __name__ == '__main__':
    app.run(port=7777)