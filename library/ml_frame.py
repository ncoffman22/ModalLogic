import random
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import itertools

class World:
    def __init__(self, propostions=('p', 'q', 'r', 's', 't'), valuations = None):
        if valuations is None:
            self.valuations = {prop: random.choice([True, False]) for prop in propostions}
        else:
            self.valuations = valuations
        self.connections = []

    def add_connection(self, world):
        self.connections.append(world)

    def remove_connection(self, world):
        self.connections.remove(world)

    def change_valuation(self, prop, value):
        self.valuations[prop] = value

    def evaluate(self, formula):
        if len(formula) == 2:
            operator = formula[0]
            operand = formula[1]
            if operator == '~':
                return not self.evaluate(operand)
            elif operator == '[]':
                return all(neighbor.evaluate(operand) for neighbor in self.connections)
            elif operator == '<>':
                return any(neighbor.evaluate(operand) for neighbor in self.connections)
        elif len(formula) == 3:
            operator = formula[1]
            operand1 = self.evaluate(formula[0])
            operand2 = self.evaluate(formula[2])
            if operator == '&':
                return operand1 and operand2
            elif operator == '|':
                return operand1 or operand2
            elif operator == '->':
                return not operand1 or operand2
        elif len(formula) == 1:
            return self.valuations.get(formula[0], False)
        return False

class Frame:
    def __init__(self, worlds):
        self.worlds = {i: world for i, world in enumerate(worlds)}

    def add_world(self, world):
        self.worlds[len(self.worlds)] = world

    def remove_world(self, index):
        self.worlds.pop(index)

    def evaluate(self, formula):
        return all(world.evaluate(formula) for _, world in self.worlds.items())

    def assign_random_connections(self, p=0.5):
        for _, world in self.worlds.items():
            for index, world2 in self.worlds.items():
                if random.random() < p:
                    world.add_connection(world2)

    def get_connections(self):
        return {index: [list(self.worlds.keys())[list(self.worlds.values()).index(neighbor)] for neighbor in world.connections] for index, world in self.worlds.items()}

    def plots(self, world_graph=True, valuation_table=True):
        if world_graph:
            self.world_graph()
        if valuation_table:
            self.valuation_table()
        plt.show()

    def world_graph(self):
        G = nx.DiGraph()
        for index, world in self.worlds.items():
            G.add_node(index, label=str(index))

        for index, world in self.worlds.items():
            for neighbor in world.connections:
                neighbor_index = list(self.worlds.keys())[list(self.worlds.values()).index(neighbor)]
                G.add_edge(index, neighbor_index)

        plt.figure(1)
        pos = nx.spring_layout(G)
        node_labels = {i: G.nodes[i]['label'] for i in G.nodes}
        nx.draw(G, pos, with_labels=False)
        nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8)
        plt.title('World Graph')

    def valuation_table(self):
       # Create a valuations table
        valuations_data = {'World': [], 'Valuations': []}
        for index, world in self.worlds.items():
            valuations_data['World'].append(index)
            valuations_data['Valuations'].append(world.valuations)
        df = pd.DataFrame(valuations_data)
        plt.figure(2)
        plt.axis('off')  # Turn off axis
        plt.axis('tight')
        table = plt.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center',edges='open')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        plt.title('Valuations Table')

    def check_connection(self, index1, index2):
        # Check if world at index1 is connected to world at index2
        return self.worlds[index2] in self.worlds[index1].connections

    def T(self):
        for index, world in self.worlds.items():
            if not self.check_connection(index, index):
                world.add_connection(world)

    def B(self):
        for index1, world in self.worlds.items():
            for index2, world2 in self.worlds.items():
                if world2 in world.connections and not self.check_connection(index2, index1):
                    world2.add_connection(world)
    def Four(self):
        for i in range(len(self.worlds)):
            for j in range(len(self.worlds)):
                if i != j:
                    for k in range(len(self.worlds)):
                        if i != k and j != k:
                            if self.check_connection(i, j) and self.check_connection(j, k) and not self.check_connection(i, k):
                                self.add_connection(i, k)

def generate_formulas(propositional_letters=['p', 'q', 'r', 's', 't']):
    formulas = set()
    formulas.update(tuple(i) for i in propositional_letters)
    binary_operators = ['&', '|', '->']
    unary_operators = ['~', '[]', '<>']

    # unaries valued formulas
    for i in itertools.product(unary_operators, propositional_letters):
        formulas.add(i)

    for _ in range(len(propositional_letters) -1):
        formulas.update(itertools.product(formulas, binary_operators, formulas))

    return formulas

def are_dicts_equal(dict1, dict2):
    if set(dict1.keys()) != set(dict2.keys()):
        return False

    # Check if the values are the same for each key
    for key in dict1.keys():
        if dict1[key] != dict2[key]:
            return False
    return True

def equivalence_classes(frame):
    classes = []

    # Create equivalence class for each world with itself
    for world in frame.worlds.values():
        classes.append([world])

    # Iterate over worlds and form equivalence classes
    for index, world1 in frame.worlds.items():
        for index2, world2 in frame.worlds.items():
            # Skip if comparing the same world
            if index == index2:
                continue
            # Check if the valuations are equal and not already in the same class
            if are_dicts_equal(world1.valuations, world2.valuations):
                # Find the class containing world1
                world1_class = next((c for c in classes if world1 in c), None)
                # Find the class containing world2
                world2_class = next((c for c in classes if world2 in c), None)
                # If both worlds are not in any class, create a new class
                if not world1_class and not world2_class:
                    classes.append([world1, world2])
                # If world1 is not in any class, add it to world2's class
                elif not world1_class:
                    world2_class.append(world1)
                # If world2 is not in any class, add it to world1's class
                elif not world2_class:
                    world1_class.append(world2)
                # If both worlds are in different classes, merge the classes
                elif world1_class != world2_class:
                    world1_class.extend(world2_class)
                    classes.remove(world2_class)

    return classes


def get_key_from_value(dictionary, value):
    for key, val in dictionary.items():
        if val == value:
            return key
    # If the value is not found, return None or raise an exception
    return None  # or raise ValueError("Value not found")

def left_filtration(frame):
    # Dict structure
        # {original index: new_index}
    eq_classes = equivalence_classes(frame)
    og_new_index = {}
    i = 0
    for item in eq_classes:
        for world in item:
            og_new_index[get_key_from_value(frame.worlds, world)] = i
        i += 1

    new_worlds = [c[0].valuations for c in eq_classes]
    left_frame = Frame(new_worlds)

    connections = frame.get_connections()
    for world, neighbors in connections.items():
        world1_index = og_new_index[world]
        for neighbor in neighbors:
            world2_index = og_new_index[neighbor]
            world = left_frame.worlds[world1_index]
            world.add_connection(world2_index)

    return left_frame


worlds = [World(['p', 'q']) for _ in range(5)]
frame = Frame(worlds)

frame.assign_random_connections()
frame.T()
frame.B()
frame.Four()
print(frame.get_connections())
left_filtration = left_filtration(frame)
frame.plots()
left_filtration.plots()


