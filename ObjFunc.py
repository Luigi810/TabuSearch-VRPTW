from UtilsTS import check_solution_feasibility
from math import ceil
from UtilsTS import max_overlapping_intervals


max_distance=0

# Funzione obiettivo f1: Somma delle distanze dei percorsi
def f1(routes, distance_matrix):
    total_distance = 0
    for route in routes:
        if len(route) > 0:  # Assicura che il percorso non sia vuoto
            route_distance = 0
            
            route_distance += distance_matrix[0][route[0].cust_no-1]
            
            # Calcola le distanze tra i clienti del percorso
            for i in range(0,len(route) - 1):
                if route[i] is not None and route[i + 1] is not None:
                    route_distance += distance_matrix[route[i].cust_no-1][route[i + 1].cust_no-1]
            
            route_distance += distance_matrix[route[-1].cust_no-1][0]
            
            total_distance += route_distance
    return total_distance

# Funzione per calcolare la funzione di costo f2 con penalità di capacità e finestre temporali
def f2(routes, distance_matrix, alpha, beta, vehicle_capacity):
    total_distance = f1(routes, distance_matrix)
    violazioni_capacita, violazioni_temporali=check_solution_feasibility(routes, distance_matrix, vehicle_capacity)
    total_demand = 0
    customers=[]
    for route in routes:
        for customer in route :
            customers.append(customer)
            total_demand+=customer.demand 
    #m = max(ceil(total_demand / vehicle_capacity), max_overlapping_intervals(customers))  # Minimo numero di veicoli necessari
    NV=0
    for route in routes:
        NV=NV+1
    max_distance=(max(max(row) for row in distance_matrix)/1) #dividendo per 2 si ottengono già performance
    if violazioni_capacita+violazioni_temporali==0:
        return total_distance+(alpha*max_distance*NV)
    elif alpha>=1:   #se ci sono violazioni temporali allora aggiungo un peso adattivo incredibilmente grande per tornare verso le soluzioni senza violazioni
        return total_distance+alpha*max_distance*(violazioni_capacita+violazioni_temporali)+(alpha*max_distance*NV) + alpha*max_distance*50 # è il costo per la perdita di reputazione
    else:
        return total_distance+alpha*max_distance*(violazioni_capacita+violazioni_temporali)+(alpha*max_distance*NV) + max_distance*50 # è il costo per la perdita di reputazione

