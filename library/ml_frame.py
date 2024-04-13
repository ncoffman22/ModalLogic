import random
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import itertools
from ml_parser import ModalLogicParser as mlp

class World:
    def __init__(self, name):
        self.name = name
        self.frames = []

    def pointed_evaluate(self, formula, frame):
        if not isinstance(frame, Frame):
            raise ValueError('Frame must be an instance of Frame')
        if len(formula) == 2:
            operator = formula[0]
            operand = formula[1]
            if operator == '~':
                return not self.pointed_evaluate(operand, frame)
            elif operator == '[]':
                return all(frame.pointed_evaluate(operand, neighbor) for neighbor in frame.connections[self.name])
            elif operator == '<>':
                return any(frame.pointed_evaluate(operand, neighbor) for neighbor in frame.connections[self.name])
        elif len(formula) == 3:
            operator = formula[1]
            operand1 = self.pointed_evaluate(formula[0], frame)
            operand2 = self.pointed_evaluate(formula[2], frame)
            if operator == '&':
                return self.pointed_evaluate(operand1, frame) and self.pointed_evaluate(operand2, frame)
            elif operator == '|':
                return self.pointed_evaluate(operand1, frame) or self.pointed_evaluate(operand2, frame)
            elif operator == '->':
                return not self.pointed_evaluate(operand1, frame) or self.pointed_evaluate(operand2, frame)
        elif len(formula) == 1:
            return frame.valuations[self.name].get(formula[0], False)
        return False

class Frame:
    def __init__(self, name, worlds, propositions={'p', 'q', 'r', 's', 't'}, valuations = None):
        self.name = name
        self.worlds = {world.name: world for world in worlds}
        self.connections = {world.name: [] for world in worlds}
        self.valuations = {world.name: {} for world in worlds}
        self._assign_top_and_bottom_valuations()
        self.propositions = propositions

        if valuations is None:
            self.assign_random_valuations(propositions)
        else:
            if self.propositions != set(valuations[worldname].keys() for worldname in self.worlds.keys()):
                raise ValueError('Valuations do not match the set of propositions')
            self.valuations = valuations

    def _assign_top_and_bottom_valuations(self):
        for world in self.worlds.keys():
            self.valuations[world]['T'] = True
            self.valuations[world]['B'] = False
        
    def assign_random_valuations(self, propositions):
        for worldname in self.worlds.keys():
            for prop in propositions:
                self.valuations[worldname][prop] = random.choice([True, False])
                
    def add_world(self, world):
        if isinstance(world, World):
            self.worlds[world.name] = world
            self.connections[world] = []
    
    def remove_world(self, name):
        if name in self.worlds.keys():
            self.worlds.pop(name)
            self.connections.pop(name)

    def valued_evaluate(self, formula):
        return all(world.pointed_evaluate(formula, self) for world in self.worlds.values())
    
    def assign_random_connections(self, p=0.5):
        for world in self.worlds.keys():
            for world2 in self.worlds.keys():
                if random.random() < p:
                    world.add_connection(world2)
    
    def pointed_evaluate(self, formula, world):
        if isinstance(self.worlds[world], World):
            return self.worlds[world].pointed_evaluate(formula, self)
    
    def add_connection(self, world1, world2):
        if world1 in self.worlds.keys() and world2 in self.worlds.keys():
            self.connections[world1].append(world2)
        else:
            raise ValueError('Worlds not in the frame')
    
    def remove_connections(self, world1, world2):
        if world1 in self.worlds.keys() and world2 in self.worlds.keys():
            if world2 in self.connections[world1]:
                self.connections[world1].remove(world2)
            else:
                raise ValueError('World not connected')
        else:
            raise ValueError('Worlds not in the frame')
    
    def change_valuation(self, world, prop, value):
        if world in self.worlds.keys():
            if prop in self.propositions:
                if value is bool:
                    self.valuations[world][prop] = value
                else:
                    raise ValueError('Value must be a boolean')
            else:
                raise ValueError('Proposition not in the set of propositions')
        else:
            raise ValueError('World not in the frame')
    
    def assign_random_connections(self, p=0.5):
        for world1 in self.worlds.keys():
            for world2 in self.worlds.keys():
                if random.random() < p:
                    self.add_connection(world1, world2)

    def world_graph(self):
        G = nx.DiGraph()
        for world in self.worlds.keys():
            G.add_node(world)
        
        for world in self.worlds.keys():
            for neighbor in self.connections[world]:
                G.add_edge(world, neighbor)
        
        plt.figure(1)
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True)
        plt.title('World Graph')

    def valuation_table(self):
        valuations_data = {'World': [], 'Valuations': []}
        for world, valuations in self.valuations.items():
            valuations_data['World'].append(world)
            valuations_data['Valuations'].append(valuations)
        df = pd.DataFrame(valuations_data)
        plt.figure(2)
        plt.axis('off')
        plt.axis('tight')
        table = plt.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center', edges='open')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        plt.title('Valuations Table')
    
    def plots(self, world_graph=True, valuation_table=True):
        if world_graph:
            self.world_graph()
        if valuation_table:
            self.valuation_table()
        plt.show()
    
    def check_connection(self, world1, world2):
        return world2 in self.connections[world1]
