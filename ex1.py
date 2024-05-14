import random
import numpy as np # type: ignore

random.seed(103541)


K = 32                  # setup cost Normal order   
IC = 3                  # Incremental cost per item
HC = 1                  # Holding cost per item per month
PC = 5                  # Backlog cost per item per month
N_MONTHS = 120          # 120 months
MIN_LAG = 0.5         
MAX_LAG = 1

shelf_life_min = 1.5
shelf_life_max = 2.5

probs_demand = [1/6, 1/3, 1/3, 1/6]

# Inventory policies
policies = [(20, 40), (20, 60), (20, 80), (20, 100), (40, 60), 
            (40, 80), (40, 100), (60, 80), (60, 100)]

init_inv_level = 60

time_next_event = [0, 0, 0, 0, 0]
next_event_type = 0 

dict_events = {
    1: "Order arrival",
    2: "Demand",
    3: "End of simulation",
    4: "Inventory evaluation"
}

num_events = 4
final_results = []
time_theres_backlog = 0
n_express_orders = 0
n_spoiled_items = 0
all_items = 0
demanded_items = 0


def timing():
    global next_event_type, num_events, time_next_event, sim_time, time_last_event
    next_event_type = 0
    min_time_next_event = 1e29

    for i in range(1, num_events + 1):
        if time_next_event[i] < min_time_next_event:    
            min_time_next_event = time_next_event[i]
            next_event_type = i # 1 - Order arrival, 2 - Demand, 3 - End of simulation, 
                                            # 4 - Inventory evaluation


    sim_time = min_time_next_event

def order_arrival():
    global INV_LEVEL, amount, inventory, time_next_event, sim_time, all_items
    
    # increment the inventory level by the amount of the order
    INV_LEVEL += amount
    # print(f"Order arrived, Got {amount} items, New inventory level: {INV_LEVEL}")
    all_items += amount
    # Append new shelf lives to the inventory list
    for _ in range(amount):
        shelf_life = sim_time + random.uniform(shelf_life_min, shelf_life_max)
        inventory = np.append(inventory, shelf_life)
        
    # eliminate order-arrival event from consideration
    time_next_event[1] = 1e30
    

def demand():
    global INV_LEVEL, inventory, sim_time, time_next_event, n_spoiled_items, demanded_items

    # Generate the size of this demand
    val = random.random()   # random number between 0 and 1
    lx = 4
    if val <= 1/6:
        lx = 1
    elif val <= 1/2:
        lx = 2
    elif val <= 5/6:
        lx = 3

    # Check for spoilage -> items that are expired  
    items_spoiled = 0
    inventory_cp = inventory
    for i, item in enumerate(inventory):
        if item < 0:
            # print("\n\nItem expired!")
            items_spoiled += 1
            # remove the item from the inventory
            inventory = inventory[i:]


    # update the inventory level
    INV_LEVEL -= items_spoiled
    n_spoiled_items += items_spoiled
    # Adjust the inventory level based on the number of items actually demanded
    INV_LEVEL -= lx
    demanded_items += lx
    # print(f"Demanded {lx} items, New inventory level: {INV_LEVEL}")
    time_next_event[2] = sim_time + random.expovariate(1/0.1)


def evaluate():

    global INV_LEVEL, amount, total_ordering_cost, inventory, n_express_orders

    """ EXPRESS ORDER """
    if INV_LEVEL < 0:
        # print("Express order!")
        amount = S - INV_LEVEL
        total_ordering_cost += 48 + 4 * amount
        time_next_event[1] = sim_time + random.uniform(0.20, 0.5)
        n_express_orders += 1

    elif INV_LEVEL < s:    # h
        amount = S - INV_LEVEL
        total_ordering_cost += 32 + 3 * amount      # K = 32, IC = 3
        time_next_event[1] = sim_time + random.uniform(0.5, 1)


    time_next_event[4] = sim_time + 1.0

    # update shelf life of the items in the inventory
    for i in range(len(inventory)):
        inventory[i] -= 1.0



def update_time_avg_stats():

    global time_last_event, area_holding, area_shortage, INV_LEVEL, time_theres_backlog
    
   
    time_since_last_event = sim_time - time_last_event
    time_last_event = sim_time

    if INV_LEVEL < 0:
        area_shortage -= INV_LEVEL * time_since_last_event
        time_theres_backlog += time_since_last_event
    elif INV_LEVEL > 0:
        area_holding += INV_LEVEL * time_since_last_event
    

def report():
    avg_ordering_cost = total_ordering_cost / N_MONTHS
    avg_holding_cost = HC * area_holding / N_MONTHS
    avg_shortage_cost = PC * area_shortage / N_MONTHS
    # print(f"({s}, {S}) {avg_ordering_cost + avg_holding_cost + avg_shortage_cost} {avg_ordering_cost} {avg_holding_cost} {avg_shortage_cost}")
    final_results.append((s, S, avg_ordering_cost + avg_holding_cost + avg_shortage_cost, avg_ordering_cost, avg_holding_cost, 
                          avg_shortage_cost, n_express_orders, n_spoiled_items, demanded_items, all_items, time_theres_backlog))



for s, S in policies:
    # simulation clock
    sim_time = 0

    # state variables
    INV_LEVEL = init_inv_level
    time_last_event = 0

    # statistical counters
    total_ordering_cost = 0
    area_holding = 0
    area_shortage = 0
    time_theres_backlog = 0
    
    # time of next events 
    time_next_event = [0, 0, 0, 0, 0]   
    time_next_event[1] = 1e30           # order arrival
    time_next_event[2] = sim_time + random.expovariate(1/0.1) # demand
    time_next_event[3] = N_MONTHS       # end of simulation                    
    time_next_event[4] = 0.0            # inventory evaluation (1st event - at the start of each month) 

    inventory = np.zeros(INV_LEVEL)    # init_inv_level items and their shelf life

    n_spoiled_items = 0
    all_items = 60
    demanded_items = 0
    n_express_orders = 0


    # generate the shelf life of the items in the inventory
    for i in range(INV_LEVEL):
        shelf_life = random.uniform(shelf_life_min, shelf_life_max)
        inventory[i] = shelf_life


    while True:
        
        # determine the next event
        timing()
        # update time-average statistical variables
        update_time_avg_stats()        

        if next_event_type == 1:
            order_arrival()
        elif next_event_type == 2:
            demand()
        elif next_event_type == 4:
            evaluate()
        elif next_event_type == 3:
            report()
            break


print("Final results:")
header = "{:<5}{:<5}{:<20}{:<20}{:<20}{:<20}{:<20}{:<20}"
data_format = "{:<5}{:<5}{:<20.4f}{:<20.4f}{:<20.4f}{:<20.4f}{:<20}({:<4},{:0})"

print(header.format('s', 'S', 'Avg Total', 'Avg Order', 'Avg Hold', 'Avg Shortage', 'Express', '(Spoiled,DemandedIt)'))
tt = 0
for res in final_results:
    print(data_format.format(res[0], res[1], res[2], res[3], res[4], res[5], res[6], res[7], res[8]))
    print("Time with backlog: ", res[10])
    tt += res[2]

print("Total: ", tt)




spoiled = [196, 171, 226, 230, 223, 199, 259, 175, 258]
demanded = [3023, 2832, 3112, 2938, 3162, 3059, 2987, 3111, 3054]
all_items = [3231, 3005, 3338, 3254, 3424, 3301, 3328, 3340, 3389]

policies = [(20, 40), (20, 60), (20, 80), (20, 100), (40, 60),
            (40, 80), (40, 100), (60, 80), (60, 100)]

print("\n\n\nProportion of items taken out of the inventory that are discarded due to being spoiled.")
for i in range(len(spoiled)):
    items_taken_out = demanded[i] + spoiled[i]
    proportion = spoiled[i] / items_taken_out
    print(f"Policy: {policies[i]} -> {proportion:.4f} ({proportion * 100:.2f}%)")
