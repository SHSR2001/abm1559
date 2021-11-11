import secrets
import random

import pandas as pd
import numpy as np
from radcad import Model, Simulation, Experiment
from radcad.engine import Engine, Backend

#--------------------------------------- BASELINE MODEL --------------------------------------------#

## Constants

constants_eip1559 = {
    "BASEFEE_MAX_CHANGE_DENOMINATOR": 8,
    "TARGET_SIZE": 12500000,
    "MAX_BLOCK_SIZE": 25000000,
    "INITIAL_BASEFEE": 1 * (10 ** 9),
}

constants_legacy = {
    "MAX_BLOCK_SIZE": 12500000,
}

levers = {
    "mempool_length": 100
}

## Classes

class eip1559_transaction:
    def __init__(self,total_gas,fee_cap,premium):
        
        # Inherent txn propoerties 
        self.total_gas_used = total_gas
        self.transaction_hash = secrets.token_bytes(8)
        
        # User adjusted txn properties
        self.fee_cap = fee_cap
        self.premium = premium
        
class legacy_transaction:
    def __init__(self,total_gas,fee):
        
        # Inherent txn properties
        self.total_gas_used = total_gas
        self.transaction_hash = secrets.token_bytes(8)
        
        # User adjusted txn properties 
        self.fee = fee
        
class block:
    def __init__(self,size,transactions):
        self.size = size
        self.transactions = transactions 
        
        
## Functions 

def demand_functions_eip1559(params, substep, state_history, previous_state, policy_input):
    
    number_of_transactions_in_mempool = previous_state['mempool_length']
    demand_dict = {}
    
    a = random.randint(1,3)
    b = random.randint(3,7)
    
    for i in range(number_of_transactions_in_mempool):
        tx = Transaction(
            total_gas = random.randint(20000,30000),
            premium = a*(10**9),
            fee_cap = b *(10**9)
        )
        demand_dict[tx.tx_hash] = tx
    
    return ("demand", demand_dict)

def demand_functions_legacy(params, substep, state_history, previous_state, policy_input):
    
    number_of_transactions_in_mempool = levers['mempool_length']
    demand_dict = {}
    
    #a = random.randint(1,3)
    b = random.randint(3,7)
    
    for i in range(number_of_transactions_in_mempool):
        tx = Transaction(
            total_gas = random.randint(20000,30000),
            #premium = a*(10**9),
            fee = b * (10 ** 9)
        )
        demand_dict[tx.tx_hash] = tx
    
    return ("demand", demand_dict)


def transaction_selection_eip1559(params, substep, state_history, previous_state):
    
    demand = previous_state["demand"]
    basefee = previous_state["basefee"]
    
    size = constants_eip1559["MAX_BLOCK_SIZE"]
    final_fee_transactions = {}
    
    for i in demand:
        if basefee > demand_dict[i].fee_cap:
            continue
        else:
            final_fee_transactions[i] = min(demand_dict[i].premium - basefee, demand_dict[i].fee_cap)
            
    final_fee_transactions = sorted(final_fee_transactions.items(), key=lambda x: x[1], reverse=True)
    
    included_transactions = []
    total_size_used = 0
    
    for i in final_fee_transactions:
        
        if total_size_used < size:
            included_transactions += demand[i]
            
        total_size_used += demand[i].total_gas_used
        
    return { "block": Block(size = total_size_used, transactions = included_transactions) }
        
def transaction_selection_legacy(params, substep, state_history, previous_state):
    
    demand = previous_state["demand"]
    
    size = constants_legacy["MAX_BLOCK_SIZE"]
    final_fee_transactions = {}
    
    for i in demand:
            final_fee_transactions[i] =  demand_dict[i].fee     
            
    final_fee_transactions = sorted(final_fee_transactions.items(), key=lambda x: x[1], reverse=True)
    
    included_transactions = []
    total_size_used = 0
    
    for i in final_fee_transactions:
        
        if total_size_used < size:
            included_transactions += demand[i]
            
        total_size_used += demand[i].total_gas_used
        
    return { "block": Block(size = total_size_used, transactions = included_transactions) }
        
def update_basefee(params, substep, state_history, previous_state, policy_input):
    
    gas_used = sum([i.total_gas_used for i in policy_input["block"].txs])
    basefee = previous_state["basefee"]
    
    basefee = basefee + basefee * (gas_used - constants_eip1559["TARGET_SIZE"]) // constants_eip1559["TARGET_SIZE"] // constants_eip1559["BASEFEE_MAX_CHANGE_DENOMINATOR"]
    
    return ("basefee", basefee)


def record_latest_block(params, substep, state_history, previous_state, policy_input):
    
    block = policy_input["block"]
    
    return ("latest_block", block)

#--------------------------------------- INTERNAL SYSTEMS CHANGES  --------------------------------------------#


#--------------------------------------- EXTERNAL SYSTEMS CHANGES --------------------------------------------#