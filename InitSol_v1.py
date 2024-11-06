import math
import sys
from math import ceil
from UtilsTS import check_solution_feasibility


class Customer:
    def __init__(self, cust_no, x_coord, y_coord, demand, ready_time, due_date, service_time):
        self.cust_no = cust_no
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.demand = demand
        self.ready_time = ready_time
        self.due_date = due_date
        self.service_time = service_time

    def __repr__(self):
        return f"Customer {self.cust_no}"

def calculate_distance(cust1, cust2):
    return round(math.sqrt((cust2.x_coord - cust1.x_coord) ** 2 + (cust1.y_coord - cust2.y_coord) ** 2), 2)

def build_distance_matrix(customers):
    num_customers = len(customers)
    distance_matrix = [[0] * num_customers for _ in range(num_customers)]
    
    for i in range(num_customers):
        for j in range(num_customers):
            if i != j:
                distance_matrix[i][j] = calculate_distance(customers[i], customers[j])
    
    return distance_matrix

def max_overlapping_intervals(customers):
    intervals = []
    
    for customer in customers:
        start = customer.ready_time
        end = customer.due_date  # Non ridurre per il service time
        intervals.append((start, end))
    
    # Conta quanti intervalli si sovrappongono
    intervals.sort(key=lambda x: x[0])
    max_overlap = 0
    current_overlap = 0
    times = []
    
    for start, end in intervals:
        times.append((start, 'start'))
        times.append((end, 'end'))
    
    times.sort()
    
    for time, event in times:
        if event == 'start':
            current_overlap += 1
            max_overlap = max(max_overlap, current_overlap)
        elif event == 'end':
            current_overlap -= 1
    
    return max_overlap

def cw_modificato(customers, distance_matrix, vehicle_capacity): 
    # Inizializza i cluster (ogni cliente è inizialmente un singolo cluster)
    routes = [[customer] for customer in customers[1:]]  # Salta il deposito (customers[0])
    return routes


def _cw_modificato(customers, distance_matrix, vehicle_capacity): 
    num_customers = len(customers)
    
    # Calcola la somma delle domande
    total_demand = sum(customer.demand for customer in customers)
    
    # Calcola il numero minimo di veicoli necessari, utile a limitare le mosse di tipo merge se le routes sono m
    m = max(ceil(total_demand / vehicle_capacity), max_overlapping_intervals(customers))  # Minimo numero di veicoli necessari
    print(f"Numero di veicoli stimato: {m}")
    
    # Inizializza i cluster (ogni cliente è inizialmente un singolo cluster)
    routes = [[customer] for customer in customers[1:]]  # Salta il deposito (customers[0])
    
    # Calcola i risparmi
    savings = []
    for i in range(1, num_customers):
        for j in range(i + 1, num_customers):
            saving = (distance_matrix[0][i] + distance_matrix[0][j] - distance_matrix[i][j])
            savings.append((saving, i, j))
    
    # Ordina i risparmi in ordine decrescente
    savings.sort(reverse=True, key=lambda x: x[0])
    
    # Esegue i merge dei cluster basati sui risparmi
    for saving, i, j in savings:
        route_i = next((route for route in routes if customers[i] in route), None)
        route_j = next((route for route in routes if customers[j] in route), None)
        
        # Verifica che i clienti non siano già nella stessa rotta, che il merge rispetti la capacità,
        # e che non ci sia sovrapposizione temporale
        if route_i != route_j:
            total_demand = sum(customer.demand for customer in route_i + route_j)
            if total_demand <= vehicle_capacity and not has_time_window_overlap(route_i, route_j, distance_matrix):
                # Unisce i cluster
                routes.remove(route_i)
                routes.remove(route_j)
                routes.append(route_i + route_j)

    return routes


def has_time_window_overlap(route_i, route_j, distance_matrix):
    # Controlla se c'è sovrapposizione temporale tra i clienti di route_i e route_j
    time_i = 0
    for idx in range(1, len(route_i)):
        previous_customer = route_i[idx - 1]
        current_customer = route_i[idx]
        time_i += distance_matrix[previous_customer.cust_no-1][current_customer.cust_no-1]
        time_i = max(time_i, current_customer.ready_time)
        if time_i > (current_customer.due_date - current_customer.service_time):
            return True  # Sovrapposizione trovata
    
    time_j = time_i
    for idx in range(1, len(route_j)):
        previous_customer = route_j[idx - 1]
        current_customer = route_j[idx]
        time_j += distance_matrix[previous_customer.cust_no-1][current_customer.cust_no-1]
        time_j = max(time_j, current_customer.ready_time)
        if time_j > (current_customer.due_date - current_customer.service_time):
            return True  # Sovrapposizione trovata
    
    return False  # Nessuna sovrapposizione trovata

def read_vrptw_data(filename):
    customers = []
    
    with open(filename, 'r') as file:
        next(file)  # Salta la riga dell'intestazione
        for line in file:
            data = line.split()
            cust_no = int(data[0])
            x_coord = float(data[1])
            y_coord = float(data[2])
            demand = float(data[3])
            ready_time = float(data[4])
            due_date = float(data[5])
            service_time = float(data[6])
            
            customer = Customer(cust_no, x_coord, y_coord, demand, ready_time, due_date, service_time)
            customers.append(customer)
    
    return customers

def copia(routes):
    new_r=[]
    for i,r in enumerate(routes):
        new_r.append(r.copy())
    return new_r

if __name__ == "__main__":
    if len(sys.argv) < 3:
        input_file = "R3_25.txt"
        capacity = 200
        #print("Usage: python TabuSearch.py <input_file.txt> <vehicle_capacity>")
        #sys.exit(1)
    else:
        input_file = sys.argv[1]
        capacity = int(sys.argv[2])

    # Legge i dati dei clienti dal file
    customers = read_vrptw_data(input_file)

    # Costruisce la matrice delle distanze
    distance_matrix = build_distance_matrix(customers)

    # Esegue Clarke e Wright per costruire una soluzione iniziale
    routes = _cw_modificato(customers, distance_matrix, capacity)

    # Stampa le rotte finali
    print("\nRotte finali:")
    for route in routes:
        print(" -> ".join([str(customer.cust_no) for customer in route]))

    #current_f2=f2(routes,distance_matrix, 1, 1, capacity)
    #print(f"Funzione obiettivo f2 (distanza + penalita'): {round(current_f2,2)}")
    #print(f"Funzione obiettivo f1 (distanza): {round(f1(routes, distance_matrix),2)}")

    violazioni_capacita, violazioni_temporali=check_solution_feasibility(routes, distance_matrix, capacity)
    print(f"La soluzione presenta {violazioni_capacita} violazioni di capacita' e {violazioni_temporali} violazioni temporali")
