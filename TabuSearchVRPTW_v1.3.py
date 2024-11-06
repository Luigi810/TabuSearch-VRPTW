from InitSol_v1 import read_vrptw_data
from InitSol_v1 import build_distance_matrix
from InitSol_v1 import cw_modificato
from ObjFunc import f1,f2
import sys
import math
from math import ceil
from UtilsTS import check_solution_feasibility
from UtilsTS import max_overlapping_intervals
from UtilsTS import rimuovi_cliente_e_lista_vuota

#formato mossa= move,i, j, cust_no del nodo i j , k, l, cust_no del nodo k l

num_customers=0 

def generate_neighbourhood(routes, distance_matrix, vehicle_capacity,alpha,current_f2):
    """Genera il vicinato ammissibile per una data soluzione VRPTW.
    Args: soluzione: La soluzione corrente del problema.
    Returns: list: Una lista di mosse ammissibili."""
    vicinato = []
    for i, percorsoi in enumerate(routes):
        for j in range(len(percorsoi)):
            if len(percorsoi)>j:
                cliente1=percorsoi[j]

                # Rimozione
                if len(percorsoi) > 1:  # Almeno un cliente deve rimanere nel percorso
                    mossa = ("rimozione", i, j,percorsoi[j].cust_no,0,0,0) # rimozione dell'elemento j dalla route i
                    valid,f2_val= mossa_ammissibile(mossa, routes,alpha,current_f2)
                    if valid:
                        vicinato.append((mossa,f2_val))
                # Scambio
                for k, percorsok in enumerate(routes):
                    if j!=k:
                        for l in range(len(percorsok)): 
                            cliente2=percorsok[l]
                            mossa=("scambio", i, j,percorsoi[j].cust_no, k, l,percorsok[l].cust_no) # scambio tra elemento j della route i con l'elemento l della route k
                            valid,f2_val= mossa_ammissibile(mossa, routes,alpha,current_f2)
                            if valid:
                                vicinato.append((mossa,f2_val))
                # Inserimento
                for k, percorsok in enumerate(routes):
                    if j!=k:
                        for l in range(len(percorsok)):
                            mossa = ("inserimento", i, j,percorsoi[j].cust_no, k, l,percorsok[l].cust_no) # inserisco il nodo j preso dalla route i nella route k dopo l'elemento l
                            valid,f2_val= mossa_ammissibile(mossa, routes,alpha,current_f2)
                            if valid:
                                vicinato.append((mossa,f2_val))

                # Inversione
                if j > 0:  # Necessari almeno due clienti per l'inversione (infatti nella route si parte dal primo cliente nodo 0, quindi j=1 vuol dire che ci sono 2 clienti)
                    mossa = ("inversione", i, j,percorsoi[j].cust_no,0,0,percorsoi[j-1].cust_no) # inversione dell'elemento j con l'elemento j-1 della route i
                    valid,f2_val= mossa_ammissibile(mossa, routes,alpha,current_f2)
                    if valid:
                        vicinato.append((mossa,f2_val))

    return vicinato

def copia(routes):
    new_r=[]
    for i,r in enumerate(routes):
        new_r.append(r.copy())
    return new_r

def applica_mossa(mossa, soluzione, alpha,current_f2):
    tipo_mossa, percorso1_index, cliente1_index, cliente1_id, percorso2_index, cliente2_index, cliente2_id = mossa
    soluzione_nuova = copia(soluzione) # Crea una copia della soluzione

    if tipo_mossa == "scambio":
        if soluzione[percorso1_index][cliente1_index].cust_no==cliente1_id and soluzione[percorso2_index][cliente2_index].cust_no==cliente2_id:
            #sys.exit(1)
            percorso1 = soluzione_nuova[percorso1_index]
            percorso2 = soluzione_nuova[percorso2_index]
            # Qui non devo cancellare le liste anche se vuote
            if percorso1_index!=percorso2_index:
                cliente1 = percorso1.pop(cliente1_index)
                cliente2 = percorso2.pop(cliente2_index)
                percorso1.insert(cliente1_index, cliente2)
                percorso2.insert(cliente2_index, cliente1)

    elif tipo_mossa == "inserimento":# inserisco il nodo j preso dalla route i nella route k dopo l'elemento l
        if soluzione[percorso1_index][cliente1_index].cust_no==cliente1_id and soluzione[percorso2_index][cliente2_index].cust_no==cliente2_id:
            #sys.exit(1)
            percorso1 = soluzione_nuova[percorso1_index]
            percorso2 = soluzione_nuova[percorso2_index]
            cliente1=rimuovi_cliente_e_lista_vuota(soluzione_nuova,percorso1_index,cliente1_index)
            percorso2.insert(cliente2_index+1, cliente1)
    
    elif tipo_mossa == "rimozione":
        if soluzione[percorso1_index][cliente1_index].cust_no==cliente1_id :
            #sys.exit(1)
            percorso1 = soluzione_nuova[percorso1_index]
            # Verifica che il percorso non sia vuoto
            cliente_rimosso=rimuovi_cliente_e_lista_vuota(soluzione_nuova,percorso1_index,cliente1_index)
            soluzione_nuova.append([cliente_rimosso])

    elif tipo_mossa == "inversione":# inversione dell'elemento j con l'elemento j-1 della route i
        if soluzione[percorso1_index][cliente1_index].cust_no==cliente1_id and soluzione[percorso1_index][cliente1_index-1].cust_no==cliente2_id:
            #sys.exit(1)
            percorso1 = soluzione_nuova[percorso1_index]
            cliente1 = percorso1.pop(cliente1_index)
            percorso1.insert(cliente1_index+1, cliente1)
    
    for i,lista_interna in enumerate(routes):
        if not lista_interna:
            routes.pop(i)

    # Aggiorna i tempi di arrivo
    f2_value=f2(soluzione_nuova, distance_matrix, alpha, beta, capacity)

    return soluzione_nuova, f2_value

def is_tabu(mossa,soluzione):
    tipo_mossa, percorso1_index, cliente1_index, cliente1_id, percorso2_index, cliente2_index, cliente2_id = mossa

    for mossa_tabu in tabu_list:
        if (cliente1_id==mossa_tabu[-1] or cliente1_id==mossa_tabu[3] or cliente2_id==mossa_tabu[3] and cliente2_id==mossa_tabu[-1]):
            return True

def mossa_ammissibile(mossa, soluzione,alpha,current_f2):
    soluzione_temporanea,new_f2 = applica_mossa(mossa, soluzione,alpha,current_f2)

    global num_customers
    num_clienti=0
    for route in soluzione_temporanea:
        num_clienti=num_clienti+len(route)
    if num_clienti<num_customers-1:      #global num_customers invece che 50
        return False, 0


    if new_f2<current_f2:  #criterio di aspirazione
        return True, new_f2
    
    # Verifica della lista tabù
    if is_tabu(mossa,soluzione):
        return False, 0

    # Verifica delle finestre temporali
    for i, percorso in enumerate(soluzione_temporanea):
        tempo_attuale = 0
        for j in range(len(percorso)-1) :#cliente in enumerate(percorso):
            if percorso[j]:
                cliente1 = percorso[j]
                cliente2 = percorso[j + 1]
                tempo_attuale += distance_matrix[cliente1.cust_no - 1][cliente2.cust_no - 1]
                if tempo_attuale < percorso[j].ready_time or tempo_attuale > percorso[j].due_date:
                    return False, 0

    # Verifica della capacità
    for percorso in soluzione_temporanea:
        if sum(cliente.demand for cliente in percorso) > capacity:
            return False, 0

    if any(len(p) == 0 for p in soluzione_temporanea):  # Verifica se ci sono percorsi vuoti
        return False, 0
    
    return True, new_f2


def tabu_search(initial_routes, distance_matrix, vehicle_capacity, tabu_list, tabu_dict, alpha,current_f2):
    # max_iterations, tabu_tenure, alpha, beta saranno definite localmente
    num_customers= len(customers)
    max_iterations = 50 * num_customers # Numero massimo di iterazioni per Tabu Search
    tabu_tenure = 10  # Dimensione della lista Tabu
    beta=1

    # Parametri iniziali
    best_routes = initial_routes[:]
    best_f2 = f2(best_routes, distance_matrix, alpha, beta, vehicle_capacity)
    current_routes = initial_routes[:]
    current_f2 = best_f2

    since_last_update=0 #contatore di iterazioni senza risultati
    num_consecutive_updates=0
    for iteration in range(max_iterations):
        neighbours = generate_neighbourhood(current_routes, distance_matrix, vehicle_capacity,alpha,current_f2)

        # è importante valutare current e best f2 con lo stesso alpha altrimenti è falsato
        best_f2=f2(best_routes,distance_matrix,alpha,beta,vehicle_capacity)

        if current_f2<best_f2:
            best_f2=current_f2
            best_routes=current_routes
            since_last_update=0
            num_consecutive_updates+=1
            if num_consecutive_updates%10==0:
                alpha=alpha*2
        else:
            num_consecutive_updates=0
            since_last_update+=1
            if since_last_update%10==0:
                alpha=alpha/2
            if since_last_update==50:
                break
        
        mossa_migliore=("",0,0,0,0,0,0)

        for i in range(len(neighbours)-1):
            move,f2_ipotetico=neighbours[i]
            if f2_ipotetico<best_f2:
                current_f2=f2_ipotetico
                mossa_migliore=move
        
        current_routes,current_f2=applica_mossa(mossa_migliore,current_routes,alpha,best_f2)

        # Aggiornare la tabu list e modificare la logica di is_tabu
        tabu_list.append(mossa_migliore)

        if len(tabu_list)>tabu_tenure:
            tabu_list.pop()

    return best_routes, best_f2


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python TabuSearch.py <input_file.txt> <vehicle_capacity>, using default benchmarck Solomon R101.25")
        input_file = "R1_25.txt"
        capacity = 200
        #sys.exit(1)
    else:
        input_file = sys.argv[1]
        capacity = int(sys.argv[2])

    tabu_list = []
    tabu_dict = {}

    # Legge i dati dei clienti dal file
    customers = read_vrptw_data(input_file)

    #global num_customers
    num_customers=len(customers)

    alpha=1
    beta=1

    
    # Costruisce la matrice delle distanze
    distance_matrix = build_distance_matrix(customers)

    # Esegue Clarke e Wright per costruire una soluzione iniziale
    routes = cw_modificato(customers, distance_matrix, capacity)
    
    NV=0
    #print("\nRotte iniziali:")
    for route in routes:
    #    print(" -> ".join([str(customer.cust_no) for customer in route]))
        NV=NV+1
    print(f"NV: {NV}")

    current_f2=f2(routes,distance_matrix, alpha, 1, capacity)
    # Stampa il valore della funzione f2

    print(f"Funzione obiettivo f2 (distanza + penalita'): {round(current_f2,2)}")
    print(f"Funzione obiettivo f1 (distanza): {round(f1(routes, distance_matrix),2)}")

    violazioni_capacita, violazioni_temporali=check_solution_feasibility(routes, distance_matrix, capacity)
    print(f"La soluzione presenta {violazioni_capacita} violazioni di capacita' e {violazioni_temporali} violazioni temporali")

    routes, curt_f2=tabu_search(routes,distance_matrix,capacity,tabu_list,tabu_dict,alpha,current_f2)

    NV=0
    # Stampa le rotte finali
    print("\nRotte finali:")
    for route in routes:
        print(" -> ".join([str(customer.cust_no) for customer in route]))
        NV=NV+1
    print(f"NV: {NV}")

    current_f2=f2(routes,distance_matrix, 1, 1, capacity)
    print(f"Funzione obiettivo f2 (distanza + penalita'): {round(current_f2,2)}")
    print(f"Funzione obiettivo f1 (distanza): {round(f1(routes, distance_matrix),2)}")

    violazioni_capacita, violazioni_temporali=check_solution_feasibility(routes, distance_matrix, capacity)
    print(f"La soluzione presenta {violazioni_capacita} violazioni di capacita' e {violazioni_temporali} violazioni temporali")
