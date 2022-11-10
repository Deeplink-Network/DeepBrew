import matplotlib.pyplot as plt
import matplotlib.animation as animation

fig = plt.figure()
ax1 = fig.add_subplot(3,1,1)
ax2 = fig.add_subplot(3,1,2)
ax3 = fig.add_subplot(3,1,3)

open('inventory.txt', 'w').close()
open('order.txt', 'w').close()
open('backorder.txt', 'w').close()

def animate(i):
    # open inventory log and split by lines
    inventory_data = open('inventory.txt','r').read()
    inventory_data_array = inventory_data.split('\n')
    
    order_data = open('order.txt', 'r').read()
    order_data_array = order_data.split('\n')
    
    backorder_data = open('backorder.txt', 'r').read()
    backorder_data_array = backorder_data.split('\n')
    
    # arrays
    round_number = []
    
    retailer_inventory = []
    wholesaler_inventory = []
    distributor_inventory = []
    manufacturer_inventory = []
    
    orders_from_market = []
    orders_from_retailer = []
    orders_from_wholesaler = []
    orders_from_distributor = []
    orders_from_manufacturer = []
    
    retailer_backorder = []
    wholesaler_backorder = []
    distributor_backorder = []
    manufacturer_backorder = []

    for inventory_line in inventory_data_array:
        if len(inventory_line)>1:
            # split by comma
            i, ri, wi, di, mi = inventory_line.split(',')
            round_number.append(int(i))
            retailer_inventory.append(float(ri))
            wholesaler_inventory.append(float(wi))
            distributor_inventory.append(float(di))
            manufacturer_inventory.append(float(mi))
        
    for order_line in order_data_array:
        if len(order_line)>1:
            # split by comma
            i, md, ro, wo, do, mo = order_line.split(',')
            orders_from_market.append(float(md))
            orders_from_retailer.append(float(ro))
            orders_from_wholesaler.append(float(wo))
            orders_from_distributor.append(float(do))
            orders_from_manufacturer.append(float(mo))
            
    for backorder_line in backorder_data_array:
        if len(backorder_line)>1:
            # split by comma
            i, rbo, wbo, dbo, mbo = backorder_line.split(',')
            retailer_backorder.append(float(rbo))
            wholesaler_backorder.append(float(wbo))
            distributor_backorder.append(float(dbo))
            manufacturer_backorder.append(float(mbo))
        
    ax1.clear()
    ax2.clear()
    ax3.clear()
    
    ax1.plot(round_number, retailer_inventory, label='Retailer Inventory')
    ax1.plot(round_number, wholesaler_inventory, label='Wholesaler Inventory')
    ax1.plot(round_number, distributor_inventory, label='Distributor Inventory')
    ax1.plot(round_number, manufacturer_inventory, label='Manufacturer Inventory')
    ax1.legend(loc='upper left')

    ax2.plot(round_number, orders_from_retailer, label='Retailer Orders')
    ax2.plot(round_number, orders_from_wholesaler, label='Wholesaler Orders')
    ax2.plot(round_number, orders_from_distributor, label='Distributor Orders')
    ax2.plot(round_number, orders_from_manufacturer, label='Manufacturer Orders')
    ax2.plot(round_number, orders_from_market, label='Market Demand', lw=3)
    ax2.legend(loc='upper left')
    
    ax3.plot(round_number, retailer_backorder, label='Retailer Backorder')
    ax3.plot(round_number, wholesaler_backorder, label='Wholesaler Backorder')
    ax3.plot(round_number, distributor_backorder, label='Distributor Backorder')
    ax3.plot(round_number, manufacturer_backorder, label='Manufacturer Backorder')
    ax3.legend(loc='upper left')
    
    ax1.yaxis.set_major_locator(plt.MaxNLocator(7))
    ax2.yaxis.set_major_locator(plt.MaxNLocator(7))
    ax3.yaxis.set_major_locator(plt.MaxNLocator(7))
    
    ax1.xaxis.set_major_locator(plt.MaxNLocator(12))
    ax2.xaxis.set_major_locator(plt.MaxNLocator(12))
    ax3.xaxis.set_major_locator(plt.MaxNLocator(12))

if __name__ == '__main__':    
    ani = animation.FuncAnimation(fig, animate, interval=1)
    plt.show()