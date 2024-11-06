def check_solution_feasibility(routes, distance_matrix, vehicle_capacity):
    capacity_violations = 0
    time_window_violations = 0

    for route in routes:
        total_demand = sum(customer.demand for customer in route)
        
        # Controllo dei vincoli di capacità
        if total_demand > vehicle_capacity:
            capacity_violations += 1  # Aggiunge una violazione se la capacità è superata

        # Controllo dei vincoli di finestre temporali
        time = 0  # Inizializza il tempo per la rotta
        for i in range(len(route)):
            current_customer = route[i]

            # Se non è il primo cliente, calcola il tempo di viaggio dal cliente precedente
            if i > 0:
                previous_customer = route[i - 1]
                time += distance_matrix[previous_customer.cust_no - 1][current_customer.cust_no - 1]

            # Controllo delle finestre temporali
            if time < current_customer.ready_time:
                time = current_customer.ready_time  # Aspetta fino all'apertura della finestra
            elif time > (current_customer.due_date - current_customer.service_time):
                time_window_violations += 1  # Aggiunge una violazione temporale

            # Aggiungi il tempo di servizio
            time += current_customer.service_time

    return capacity_violations, time_window_violations

def is_feasible_move(customer, destination_route, distance_matrix, vehicle_capacity):
    # Controlla che destination_route sia una lista di clienti e non sia vuota
    if not isinstance(destination_route, list) or len(destination_route) == 0:
        return False  # La destinazione non è valida

    # Verifica che customer sia un oggetto valido
    if not hasattr(customer, 'demand'):
        return False  # La customer non ha l'attributo 'demand'

    # Verifica la capacità del veicolo
    total_demand = sum(c.demand for c in destination_route) + customer.demand
    if int(total_demand) > vehicle_capacity:
        return False

    # Verifica le finestre temporali
    new_route = destination_route + [customer]
    time = 0
    for i in range(1, len(new_route)):
        previous_customer = new_route[i - 1]
        current_customer = new_route[i]
        time += distance_matrix[previous_customer.cust_no - 1][current_customer.cust_no - 1]
        
        if time < current_customer.ready_time:
            time = current_customer.ready_time  # Aspetta fino all'apertura della finestra
        elif time > (current_customer.due_date - current_customer.service_time):
            return False  # Violazione della finestra temporale

        time += current_customer.service_time

    return True  # La mossa è fattibile


def time_window_violation(route, distance_matrix):
    current_time = 0
    for i in range(1, len(route)):
        customer = route[i]
        prev_customer = route[i-1]
        
        # Calcola il tempo di arrivo al cliente successivo
        current_time += distance_matrix[prev_customer.cust_no-1][customer.cust_no-1]
        current_time = max(current_time, customer.ready_time)  # Aspetta se arriva in anticipo
        
        # Verifica se il cliente è servito in tempo
        if current_time > customer.due_date:
            return True
        
        # Aggiungi il tempo di servizio
        current_time += customer.service_time
    
    return False

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

def rimuovi_cliente_e_lista_vuota(lista_liste, indice_lista, indice_elemento):
    """Rimuove un cliente da una lista interna e, se la lista diventa vuota, la rimuove anche dalla lista esterna.

    Args:
    lista_liste: La lista di liste di clienti.
    indice_lista: L'indice della lista interna da modificare.
    indice_elemento: L'indice dell'elemento (cliente) da rimuovere dalla lista interna.
    """

    lista_interna = lista_liste[indice_lista]
    elem=lista_interna.pop(indice_elemento)

    # Se la lista interna è vuota, rimuovila dalla lista esterna
    if not lista_interna:
        lista_liste.pop(indice_lista)

    return elem