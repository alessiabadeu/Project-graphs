import csv
import random
import copy

import networkx as nx
import matplotlib.pyplot as plt #biblioteca de plotare

#1. Creearea grafului

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


print("Number nodes:", G.number_of_nodes())
print("Number edges:", G.number_of_edges())

#2. Central betweeness-hubs

centrality = nx.betweenness_centrality(G) #se returneaza un dictionar, cheile sunt nodurile, valorile sunt betweenness centrality

hubs = sorted(centrality.items(), key = lambda x: x[1], reverse=True)[:5] #sortam descrescator dupa valoare si pastram doar primele 5 elemente (primele 5 hub-uri)

for hub in hubs:
    print(hub)

#nush daca e nevoie de graficul asta 

# values = list(centrality.values())

# plt.hist(values, bins=1000) #grupeaza valorile pe intervale; 50 de aeroporturi
# plt.xlabel("Betweenness Centrality") #pe axa x "Betweenness Centrality"
# plt.ylabel("Number Airports") #pe aza y
# plt.title("Betweennes Centrality Analysis")
# plt.show() #se afiseaza histograma; foarte multe aeroporturi-betweennes~0, putine-betweenness mare-> scale-free structure (cred)

#3.Attack+Load redistribution

load = nx.betweenness_centrality(G, normalized=True)

alpha = 1.2
capacity = {n: alpha * load[n] for n in G.nodes()}  

initial_nodes = G.number_of_nodes()
G_temp = G.copy()
G_temp.remove_node("DEN")

print("Removed hub:", "DEN")

nodes_over_time = []  #pt grafic
iteration = 0

while True:
    iteration += 1
    load = nx.betweenness_centrality(G_temp, normalized=True)  #daca stergem un nod, se face redistribuirea si load e recalculat

    failed = []  #nodurile care au load>capacitatea
    for n in G_temp.nodes():
        if load[n] > capacity[n]:
            failed.append(n)

    nodes_over_time.append(G_temp.number_of_nodes()) #pt grafic, retine cate noduri mai sunt la fiecare iteratie

    if not failed:  #daca nu mai cade niciun nod, iesim din while
        break

    G_temp.remove_nodes_from(failed)

nodes_over_time.append(G_temp.number_of_nodes())

print("Final nodes:",G_temp.number_of_nodes())

print("Failed airports:",initial_nodes - G_temp.number_of_nodes())

largest_component = max(   # Largest Connected Component (S)
    nx.connected_components(G_temp),
    key=len
)

S = len(largest_component)
print("Largest component size:", S)
print("Normalized S:",S / initial_nodes)

E_before = nx.global_efficiency(G)
E_after = nx.global_efficiency(G_temp)

print("Efficiency before:",E_before)
print("Efficiency after:",E_after)

plt.plot(nodes_over_time, marker='o')  #marker pune cerculet in fiecare punct

plt.xlabel("Iteration")
plt.ylabel("Remaining nodes")
plt.title(f"Cascade failure after removing DEN")
plt.grid(True)  #chestie de design

plt.show()