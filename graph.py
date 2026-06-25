import networkx as nx
import matplotlib.pyplot as plt #biblioteca de plotare
import random

#1. Create graph
def create_graph():
    G = nx.Graph() #creearea grafului
    us_airports = set() #set pentru a retine aeroporturile din US; folosim pentru routes

    with open("airports.dat.txt", "r", encoding="utf-8") as f:

        for line in f:
            splited_line = line.strip().split(",")
            airport_code = splited_line[4].strip().replace('"','') #de ex "GKA" devine GKA (fara ghilimele)
            airport_name = splited_line[1].strip().replace('"','') 
            airport_country = splited_line[3].strip().replace('"', '')
            if airport_country == "United States" and airport_code!="\\N": 
                G.add_node(airport_code, name=airport_name, country=airport_country)
                us_airports.add(airport_code) #adaugam aeroportul in set 

    with open("routes.dat.txt","r", encoding="utf-8") as f:
        for line in f:
            splited_line = line.strip().split(",")
            origin = splited_line[2].strip().replace('"', '')
            destination = splited_line[4].strip().replace('"', '')

            if len(splited_line)>=4 and origin in us_airports and destination in us_airports: #ne asiguram ca route e in US
                G.add_edge(origin,destination)
    
    return G

#2. Central betweeness-hubs

def find_hubs(G):
    centrality = nx.betweenness_centrality(G) #se returneaza un dictionar, cheile sunt nodurile, valorile sunt betweenness centrality
    hubs = sorted(centrality.items(), key = lambda x: x[1], reverse=True)[:10] #sortam descrescator dupa valoare si pastram doar primele 10 elemente (primele 10 hub-uri)
    return hubs

#3.Attack+Load redistribution

def attack(G, node, alpha):

    load = nx.betweenness_centrality(G, normalized=True)
    capacity = {n: alpha * load[n] for n in G.nodes()}  

    G_temp = G.copy()
    G_temp.remove_node(node)

    print("Removed hub:", node)

    nodes_over_time = []  #pt grafic
    iteration = 0

    while True:  #ce magie se face cu load-ul?
        iteration += 1
        load = nx.betweenness_centrality(G_temp, normalized=True) #!ce e normalized????  #daca stergem un nod, se face redistribuirea si load e recalculat

        failed = []  #nodurile care au load>capacitatea
        for n in G_temp.nodes():
            if load[n] > capacity[n]:
                failed.append(n)

        nodes_over_time.append(G_temp.number_of_nodes()) #pt grafic, retine cate noduri mai sunt la fiecare iteratie

        if not failed:  #daca nu mai cade niciun nod, iesim din while
            break

        G_temp.remove_nodes_from(failed)

    nodes_over_time.append(G_temp.number_of_nodes())
    
    return G_temp, nodes_over_time

def analyze_cascade(G, G_temp):
    initial_nodes = G.number_of_nodes()

    print("Final nodes:",initial_nodes)

    print("Failed airports:",initial_nodes - G_temp.number_of_nodes())

    largest_component = max(nx.connected_components(G_temp),key=len)  #????

    S = len(largest_component)
    print("Largest component size:", S)
    print("Normalized S:",S / initial_nodes)

    E_before = nx.global_efficiency(G)  #????
    E_after = nx.global_efficiency(G_temp)

    print("Efficiency before:",E_before)
    print("Efficiency after:",E_after)

def plot_cascade(nodes_over_time, node):
    plt.plot(nodes_over_time, marker='o')  #marker pune cerculet in fiecare punct

    plt.xlabel("Iteration")
    plt.ylabel("Remaining nodes")
    plt.title(f"Cascade failure after removing {node}")
    plt.grid(True)

    plt.show()

def random_attack(G, alpha):
    random.seed(42)  # Set a seed for reproducibilityU, whatever that means girl 
    random_node = random.choice(list(G.nodes()))
    return attack(G, random_node, alpha)

def main():
    G =create_graph()

    G_temp, nodes_over_time = attack(G, "DEN", 1.5)
    analyze_cascade(G, G_temp)
    plot_cascade(nodes_over_time, "DEN")

    # G_temp, nodes_over_time = random_attack(G, 1.5)
    # analyze_cascade(G, G_temp)
    # plot_cascade(nodes_over_time, "Random Node")

main()