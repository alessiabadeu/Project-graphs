import csv
import random
import copy

import networkx as nx
import matplotlib.pyplot as plt


##################################################
# PASUL 1 - CITIM AEROPORTURILE
##################################################

airports = {}

with open("airports.dat.txt", encoding="utf-8") as f:

    reader = csv.reader(f)

    for row in reader:

        airport_id = row[0]
        iata = row[4]
        country = row[3]

        # pastram doar aeroporturile din SUA
        if country == "United States" and iata != "\\N":

            airports[airport_id] = iata


print("Numar aeroporturi US:", len(airports))


##################################################
# PASUL 2 - CONSTRUIM GRAFUL
##################################################

G = nx.Graph()

with open("routes.dat.txt", encoding="utf-8") as f:

    reader = csv.reader(f)

    for row in reader:

        if len(row) < 6:
            continue

        source_id = row[3]
        destination_id = row[5]

        if source_id in airports and destination_id in airports:

            source = airports[source_id]
            destination = airports[destination_id]

            G.add_edge(source, destination)


print("Numar noduri:", G.number_of_nodes())
print("Numar muchii:", G.number_of_edges())


##################################################
# PASUL 3 - GASIM HUB-URILE
##################################################

degrees = dict(G.degree())

top_hubs = sorted(
    degrees.items(),
    key=lambda x: x[1],
    reverse=True
)

print("\nTop 10 hub-uri:\n")

for airport, degree in top_hubs[:10]:

    print(airport, degree)


##################################################
# PASUL 4 - FUNCTIE PENTRU LCC
##################################################

def largest_component_ratio(graph):

    if graph.number_of_nodes() == 0:
        return 0

    largest_cc = max(
        nx.connected_components(graph),
        key=len
    )

    return len(largest_cc) / graph.number_of_nodes()


##################################################
# PASUL 5 - RANDOM FAILURES
##################################################

def random_attack(graph, percent):

    H = graph.copy()

    remove_count = int(
        percent * H.number_of_nodes()
    )

    nodes = list(H.nodes())

    removed = random.sample(
        nodes,
        remove_count
    )

    H.remove_nodes_from(removed)

    return largest_component_ratio(H)


##################################################
# PASUL 6 - TARGETED ATTACK
##################################################

def targeted_attack(graph, percent):

    H = graph.copy()

    remove_count = int(
        percent * H.number_of_nodes()
    )

    degrees = sorted(
        H.degree(),
        key=lambda x: x[1],
        reverse=True
    )

    hubs = [
        node
        for node, degree in degrees[:remove_count]
    ]

    H.remove_nodes_from(hubs)

    return largest_component_ratio(H)


##################################################
# PASUL 7 - EXPERIMENTE
##################################################

percentages = [
    0.01,
    0.05,
    0.10,
    0.15,
    0.20,
    0.25
]

random_results = []
targeted_results = []

for p in percentages:

    random_score = random_attack(
        G,
        p
    )

    targeted_score = targeted_attack(
        G,
        p
    )

    random_results.append(
        random_score
    )

    targeted_results.append(
        targeted_score
    )

    print(
        f"{int(p*100)}% removed"
    )

    print(
        f"Random: {random_score:.3f}"
    )

    print(
        f"Targeted: {targeted_score:.3f}"
    )

    print()


##################################################
# PASUL 8 - GRAFIC
##################################################

x = [
    p * 100
    for p in percentages
]

plt.figure(figsize=(8, 5))

plt.plot(
    x,
    random_results,
    marker="o",
    label="Random failures"
)

plt.plot(
    x,
    targeted_results,
    marker="s",
    label="Targeted attacks"
)

plt.xlabel(
    "Percentage of removed airports"
)

plt.ylabel(
    "Largest Connected Component"
)

plt.title(
    "Resilience of US Air Transportation Network"
)

plt.legend()

plt.grid(True)

plt.show()