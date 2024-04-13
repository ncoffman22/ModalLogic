from ml_frame import Frame, World
import itertools
from collections import deque

def dfs(graph, start, visited, path):
    visited[start] = True
    path.append(start)
    longest_path = path.copy()

    for neighbor in graph[start]:
        if not visited[neighbor]:
            new_path = dfs(graph, neighbor, visited, path)
            if len(new_path) > len(longest_path):
                longest_path = new_path

    path.pop()
    visited[start] = False
    return longest_path

def longest_path(graph):
    visited = {node: False for node in graph}
    longest = []
    for node in graph:
        path = dfs(graph, node, visited, [])
        if len(path) > len(longest):
            longest = path
    
    long = len(longest)
    for item in longest:
        if item in graph[item]:
            long += 1
    return long-1

def graph_formulas(frame):
    if not isinstance(frame, Frame):
        raise ValueError('Frame must be an instance of Frame')

    formulas = set()

    unary_operators = ['[]', '<>']

    unaries = []
    for item in itertools.product(unary_operators, repeat=longest_path(frame.connections)):
        unaries.append(list(item))
    
    propositions = list(frame.propositions)
    propositions.append('T')
    propositions.append('B')
    for valuation in itertools.product(unary_operators, propositions):
        print(valuation)
        formulas.add(valuation)

    print(formulas)
worlds = [World('w1'), World('w2'), World('w3')]
frame = Frame('f1', worlds)
frame.assign_random_connections()
print(longest_path(frame.connections))
print(frame.connections)
graph_formulas(frame)