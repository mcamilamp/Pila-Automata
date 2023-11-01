import tkinter as tk
import networkx as nx
from PIL import Image, ImageTk
from pila import Stack
import time
import matplotlib.pyplot as plt

class Automaton:
    def __init__(self):
        self.stack = Stack()
        self.states = {
            'q0': {'a': ('q1', 'pop_push'), 'b': ('q2', 'pop_push'), '': ('q2', 'pop')},
            'q1': {'a': ('q1', 'pop_push'), 'b': ('q2', 'pop'), '': ('q2', 'pop')},
            'q2': {'a': ('q2', 'pop'), 'b': ('q2', 'pop'), '': ('q2', 'pop')},
        }
        self.current_state = 'q0'

    def reset(self):
        self.stack = Stack()
        self.current_state = 'q0'

    def process_input(self, input_str):
        self.reset()
        for symbol in input_str:
            if symbol in self.states[self.current_state]:
                next_state, action = self.states[self.current_state][symbol]
                if action == 'pop_push':
                    self.stack.pop()
                    self.stack.push(symbol)
                elif action == 'pop':
                    self.stack.pop()
                self.current_state = next_state
                yield (self.current_state, symbol)

    def is_valid(self):
        return self.current_state == 'q2' and self.stack.is_empty()

class PalindromeRecognizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Palindrome Recognizer')
        self.root.geometry("700x600")

        self.label = tk.Label(root, text='Enter a string (abbbba format):')
        self.label.pack()

        self.entry = tk.Entry(root)
        self.entry.pack()

        self.check_button = tk.Button(root, text='Check', command=self.check_palindrome)
        self.check_button.pack()

        self.result_label = tk.Label(root, text='Result: ')
        self.result_label.pack()

        self.state_label = tk.Label(root, text='Current State: q0')
        self.state_label.pack()

        self.speed_label = tk.Label(root, text='Speed:', font=("Helvetica", 14, "bold"))
        self.speed_label.pack()

        self.speed_scale = tk.Scale(root, from_=0.1, to=2.0, resolution=0.1, orient="horizontal", length=300)
        self.speed_scale.set(1.0)
        self.speed_scale.pack()

        label_style = ("Helvetica", 14, "bold")
        self.label.config(fg="Purple", font=label_style)
        self.result_label.config(fg="Purple", font=label_style)
        self.state_label.config(fg="Purple", font=label_style)
        self.speed_label.config(fg="Purple", font=label_style)

        self.graph = nx.DiGraph()
        self.graph.add_nodes_from(['q0', 'q1', 'q2'])
        self.graph.add_edges_from([
            ('q0', 'q1', {'label': 'a'}),
            ('q0', 'q2', {'label': 'b'}),
            ('q1', 'q1', {'label': 'a'}),
            ('q1', 'q2', {'label': 'b'}),
            ('q2', 'q2', {'label': 'a'}),
            ('q2', 'q2', {'label': 'b'})
        ])

        self.node_positions = {
            'q0': (100, 100),
            'q1': (300, 100),
            'q2': (200, 300),
        }

        self.node_colors = ['lightblue' for _ in range(len(self.graph.nodes))]

        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack()

        self.update_graph()

    def check_palindrome(self):
        input_str = self.entry.get()
        automaton = Automaton()
        self.node_colors = ['lightblue' for _ in range(len(self.graph.nodes))]

        speed = self.speed_scale.get()

        prev = None
        for i, (state, _) in enumerate(automaton.process_input(input_str)):
            self.node_colors[list(self.graph.nodes).index(state)] = 'lightcoral'
            self.state_label.config(text=f'Current State: {state} -> Next Symbol: {input_str[i]}')
            self.root.update()
            self.node_colors[list(self.graph.nodes).index(state)] = 'red'
            time.sleep(0.5 / speed)
            if prev is not None:
                self.node_colors[prev] = 'lightcoral'
            self.update_graph()
            prev = list(self.graph.nodes).index(state)

        if automaton.is_valid():
            self.result_label.config(text='Result: Valid Palindrome')
        else:
            self.result_label.config(text='Result: Not a valid palindrome')

    def update_graph(self):
        edge_labels = {(u, v): d['label'] for u, v, d in self.graph.edges(data=True)}

        fig = plt.figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        ax.axis('off')
        pos = self.node_positions

        nx.draw(self.graph, pos, with_labels=True, node_color=self.node_colors, node_size=300, font_size=10)
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)
        plt.savefig('automaton.png', bbox_inches='tight', transparent=True)

        self.graph_image = ImageTk.PhotoImage(Image.open('automaton.png'))
        self.canvas.delete("all")
        self.graph_label = self.canvas.create_image(5, 5, anchor=tk.NW, image=self.graph_image)
        self.canvas.update()

if __name__ == '__main__':
    root = tk.Tk()
    app = PalindromeRecognizerApp(root)
    root.mainloop()
