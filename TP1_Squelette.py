import tkinter as tk
from inspect import stack
from tkinter import ttk
import csv
import random
from queue import Queue
from queue import LifoQueue
from queue import PriorityQueue
import math
import time


search_algorithms = ('Parcours en largeur', 'Parcours en profondeur', 'Parcours en profondeur itératif', 'Recherche à coût Uniforme', 'Recherche gloutonne', 'A*')
costs = ('distance', 'temps')

town_color = 'lightcoral'
road_color = 'lightgreen'
path_color = 'red'


class Node:

        def __init__(self, town, parent=None, road_to_parent=None, cost=0, heuristic=0):
            self.town = town
            self.parent = parent
            self.road_to_parent = road_to_parent
            self.cost = cost
            self.heuristic = heuristic

        def __lt__(self, other):
            return self.all_costs() < other.all_costs()

        def all_costs(self):
            return self.cost + self.heuristic

class Town:

    def __init__(self, dept_id, name, latitude, longitude):
        self.dept_id = dept_id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.neighbours = dict()


class Road:

    def __init__(self, town1, town2, distance, time):
        self.town1 = town1
        self.town2 = town2
        self.distance = distance
        self.time = time

# Distance vol d'oiseau
def crowfliesdistance(town1, town2):
    return math.sqrt((town1.latitude - town2.latitude)**2 + (town1.longitude - town2.longitude)**2)

# A-Star
def a_star(start_town, end_town):
    tovisit = PriorityQueue()
    visited = set()
    current_node = Node(start_town, None, None, 0, crowfliesdistance(start_town, end_town))
    tovisit.put(current_node)
    while not tovisit.empty():
        current_node = tovisit.get()
        visited.add(current_node.town)
        if current_node.town == end_town:
            return current_node
        for neighbour in current_node.town.neighbours.keys():
            if neighbour not in visited:
                tovisit.put(Node(neighbour, current_node, current_node.town.neighbours[neighbour], current_node.cost + current_node.town.neighbours[neighbour].distance, crowfliesdistance(neighbour, end_town)))

# Recherche gloutonne
def greedy_search(start_town, end_town):
    current_node = Node(start_town)
    visited = set()
    old_stack = []
    while current_node.town != end_town:
        visited.add(current_node.town)
        old_stack.append(current_node)
        next_node = None
        for neighbour in current_node.town.neighbours.keys():
            if not neighbour in visited and (next_node is None or crowfliesdistance(neighbour, end_town) < crowfliesdistance(next_node, end_town)):
                next_node = neighbour
        if next_node is None:
            current_node = old_stack.pop()
        else:
            current_node = Node(next_node, current_node, current_node.town.neighbours[next_node], current_node.cost + current_node.town.neighbours[next_node].distance)
    return current_node

# Parcours à coût uniforme
def ucs(start_town, end_town):
    current_node = Node(start_town)
    visits = PriorityQueue()
    visited = set()
    visits.put(current_node)
    while not visits.empty():
        current_node = visits.get()
        visited.add(current_node.town)
        if current_node.town == end_town:
            return current_node
        for neighbour in current_node.town.neighbours.keys():
            if (neighbour not in visited) and (not any(node.town == neighbour for node in visits.queue)) :
                visits.put(Node(neighbour, current_node, current_node.town.neighbours[neighbour], current_node.cost + current_node.town.neighbours[neighbour].distance))

# Parcours en profondeur itératif
def dfs_iter(start_town, end_town):
    current_node = Node(start_town)
    visits = LifoQueue()
    visited = set()
    visits.put(current_node)
    while not visits.empty():
        current_node = visits.get()
        visited.add(current_node.town)
        if current_node.town == end_town:
            return current_node
        for neighbour in current_node.town.neighbours.keys():
            if (neighbour not in visited) and (not any(node.town == neighbour for node in visits.queue)) :
                visits.put(Node(neighbour, current_node, current_node.town.neighbours[neighbour], current_node.cost + current_node.town.neighbours[neighbour].distance))


# Parcours en profondeur (reccursif)
def dfs(start_town, end_town, max_depth=100, depth=0, visited=None, path=None):
    if visited is None:
        visited = LifoQueue()
    if start_town == end_town:
        if path is None:
            return Node(start_town)
    if depth >= max_depth:
        return None
    visited.put(start_town)
    for neighbour in start_town.neighbours.keys():
        if neighbour not in visited.queue:
            path = dfs(neighbour, end_town, max_depth, depth+1, visited, path)
            if path is not None:
                return Node(start_town, path, start_town.neighbours[neighbour], path.cost + start_town.neighbours[neighbour].distance)




# Parcours en largeur
def bfs(start_town, end_town):
    current_node = Node(start_town)
    visits = Queue()
    visited = set()
    visits.put(current_node)
    while not visits.empty():
        current_node = visits.get()
        visited.add(current_node.town)
        if current_node.town == end_town:
            return current_node
        for neighbour in current_node.town.neighbours.keys():
            if (neighbour not in visited) and (not any(node.town == neighbour for node in visits.queue)) :
                visits.put(Node(neighbour, current_node, current_node.town.neighbours[neighbour], current_node.cost + current_node.town.neighbours[neighbour].distance))


def display_path(path):
    current_node = path
    while current_node.parent is not None:
        canvas1.itemconfig(road_lines[current_node.road_to_parent], fill=path_color)
        print(current_node.road_to_parent.town1.name, current_node.road_to_parent.town2.name)
        current_node = current_node.parent


def run_search():
    button_run['state'] = tk.DISABLED
    # put all the roads in normal
    for road in roads:
        canvas1.itemconfig(road_lines[road], fill=road_color)
    start_city = towns[combobox_start.current() + 1]
    end_city = towns[combobox_end.current() + 1]
    search_method = combobox_algorithm.current()
    cost = combobox_cost.current()
    computing_time = time.time()
    if search_method == 0:  # Parcours en largeur
        path = bfs(start_city, end_city)
    elif search_method == 1:  # Parcours en profondeur
        path = dfs(start_city, end_city)
    elif search_method == 2:  # Parcours en profondeur itératif
        path = dfs_iter(start_city, end_city)
    elif search_method == 3:  # Parcours à coût uniforme
        path = ucs(start_city, end_city)
    elif search_method == 4:  # Recherche gloutonne
        path = greedy_search(start_city, end_city)
    elif search_method == 5:  # A*
        path = a_star(start_city, end_city)
    else:
        path = None
    computing_time = time.time() - computing_time
    if path is not None:
        label_path_title['text'] = "Itinéraire de "+start_city.name+" à "+end_city.name+" avec "+search_algorithms[search_method]
        label_distance['text'] = "Distance: "+str(path.cost)+"km"
        label_computing_time['text'] = "Temps de calcul: "+str(computing_time)+"s"
        display_path(path)
    button_run['state'] = tk.NORMAL


def longitude_to_pixel(longitude):
    return (longitude-map_W) * diff_W_E

def latitude_to_pixel(latitude):
    return (map_N - latitude) * diff_N_S


# Read towns and roads csv and create relative objects
towns = dict()
roads = list()
with open('data/towns.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';')
    for row in reader:
        towns[int(row['dept_id'])] = Town(dept_id=int(row['dept_id']), name=row['name'], latitude=float(row['latitude']), longitude=float(row['longitude']))
with open('data/roads.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';')
    for row in reader:
        road = Road(town1=towns[int(row['town1'])], town2=towns[int(row['town2'])], distance=int(row['distance']), time=int(row['time']))
        roads.append(road)
        road.town1.neighbours[road.town2] = road
        road.town2.neighbours[road.town1] = road


window = tk.Tk()
window.title("Itineria")

# Décommenter la carte pour choisir la bonne taille pour votre machine
#map_image = tk.PhotoImage(file="img/France_map_admin_1066_1024.png")
map_image = tk.PhotoImage(file="/Users/maximesanciaume/PycharmProjects/IA_tp1/img/France_map_admin_799_768.png")
#map_image = tk.PhotoImage(file="img/France_map_admin_499_480.png")



width = map_image.width()
height = map_image.height()
canvas1 = tk.Canvas(window, width=width, height=height)

background_map = canvas1.create_image(0, 0, anchor=tk.NW, image=map_image)

# Dessin des routes et villes
map_N = 51.5
map_S = 41
map_W = -5.8
map_E = 10
diff_W_E = width / (map_E - map_W)
diff_N_S = height / (map_N - map_S)
town_radius = 4
road_width = 3

road_lines = dict()
for road in roads:
    road_lines[road] = canvas1.create_line(longitude_to_pixel(road.town1.longitude), latitude_to_pixel(road.town1.latitude),
                        longitude_to_pixel(road.town2.longitude), latitude_to_pixel(road.town2.latitude), fill=road_color,
                        width=road_width)

for town in towns.values():
    canvas1.create_oval(longitude_to_pixel(town.longitude) - town_radius, latitude_to_pixel(town.latitude) - town_radius,
                        longitude_to_pixel(town.longitude) + town_radius, latitude_to_pixel(town.latitude) + town_radius,
                        fill=town_color)


canvas1.grid(row=0, column=0, columnspan=4)
label_start = tk.Label(window, text="Départ")
label_start.grid(row=1, column=0)
combobox_start = ttk.Combobox(window, state='readonly')
combobox_start.grid(row=1, column=1)

label_end = tk.Label(window, text="Arrivée")
label_end.grid(row=1, column=2)
combobox_end = ttk.Combobox(window, state='readonly')
combobox_end.grid(row=1, column=3)

town_list = []
for town in towns.values():
    town_list.append(str(town.dept_id)+" - "+town.name)
combobox_start['values'] = town_list
combobox_end['values'] = town_list
combobox_start.current(random.randint(0, len(town_list)-1))
combobox_end.current(random.randint(0, len(town_list)-1))

label_algorithm = tk.Label(window, text="Algorithme")
label_algorithm.grid(row=2, column=0)
combobox_algorithm = ttk.Combobox(window, state='readonly')
combobox_algorithm.grid(row=2, column=1)
combobox_algorithm['values'] = search_algorithms
combobox_algorithm.current(random.randint(0, len(combobox_algorithm['values'])-1))

label_cost = tk.Label(window, text="Coût")
label_cost.grid(row=2, column=2)
combobox_cost = ttk.Combobox(window, state='readonly')
combobox_cost.grid(row=2, column=3)
combobox_cost['values'] = costs
combobox_cost.current(random.randint(0, len(combobox_cost['values']) - 1))

label_path_title = tk.Label(window, text="")
label_path_title.grid(row=3, column=0, columnspan=4)

label_distance = tk.Label(window, text="")
label_distance.grid(row=4, column=0)

label_computing_time = tk.Label(window, text="")
label_computing_time.grid(row=4, column=3)

button_run = tk.Button(window, text='Calculer', command=run_search)
button_run.grid(row=5, column=0)

button_quit = tk.Button(window, text='Quitter', command=window.destroy)
button_quit.grid(row=5, column=3)
window.mainloop()
