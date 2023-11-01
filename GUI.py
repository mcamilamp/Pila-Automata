import sys 
sys.path.insert(0, 'C:\\Users\\leidi\\AppData\\Roaming\\Python\\Python38\\site-packages')
from PySide6.QtCore import *
from PySide6.QtGui import QPixmap, QAction, QActionGroup
from PySide6.QtWidgets import *
from gtts import gTTS
import pygame
import matplotlib as matp
import matplotlib.pyplot as plt
import matplotlib.backends.backend_qt5agg
import networkx as nx
import os
import gettext
from main import create_automata

matp.use('Qt5Agg')

directorio_actual = os.getcwd()
localedir = os.path.join(directorio_actual, 'locale')

gettext.bindtextdomain('myapp', localedir)
gettext.textdomain('myapp')

class Interface(QMainWindow):
    def __init__(self, automata):
        super().__init__()

        self.automata = automata
        self.graph = nx.DiGraph()
        self.graph.add_nodes_from(self.automata.estados)  # Assuming 'estados' contains your states
        self.graph.add_weighted_edges_from(self.generate_edges())

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)

        # Create a central widget to hold the QGraphicsView
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.setWindowTitle("Automata Graph")
        self.setGeometry(100, 100, 800, 600)

        self.update_nodes(self.automata.estado_inicial)
        # INICIALIZAR LAS OPCIONES DE LOS MENÚ
        self.languages_menu = None
        self.ingles_action = None
        self.portugues_action = None
        self.espanol_action = None
        self.frances_action = None
        self.german_action = None

        # PARA GENERAR LOS MENÚ DE LOS IDIOMAS
        self.languages_group = QActionGroup(self)
        self.languages_group.setExclusive(True)

        self.create_interface()


    def create_interface(self, idioma = 'es'):

        translations = gettext.translation('mensajes', localedir, languages=[idioma])
        translations.install()
        _ = translations.gettext
        
        
        # WIDGET PRNCIPAL
        widget = QWidget()
        self.setCentralWidget(widget)
        
        # LAYOUT PRINCIPAL
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # CREAR UN WIDGET TIPO LIENZO PARA MOSTRAR LA IMAGEN
        self.scene = QGraphicsScene()
        self.canvas = QGraphicsView(self.scene)
        layout.addWidget(self.canvas)

        # NOMBRE Y TAMAÑO DE LA VENTANA
        self.setWindowTitle(_("Autómata"))
        self.setGeometry(100, 100, 600,600)
        self.setStyleSheet("background-color: lavender; color: black")

        
        # ACTUALIZAR EL MENU DE IDIOMAS
        if self.languages_menu:
            self.language_text_update()

        # BARRA DE MENU PARA CAMBIAR IDIOMA
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet("color: red; font-weight:bold")


        if not self.languages_menu:

            self.languages_menu = menu_bar.addMenu(_("Idiomas"))

        if not self.ingles_action:

            self.ingles_action = QAction(_("Inglés"), self)
            self.languages_menu.addAction(self.ingles_action)
            self.ingles_action.setCheckable(True)
            self.languages_group.addAction(self.ingles_action)

        self.ingles_action.triggered.connect(lambda: self.change_language('en'))
        
        if not self.frances_action:

            self.espanol_action = QAction(_("Francés"), self)
            self.languages_menu.addAction(self.espanol_action)
            self.espanol_action.setCheckable(True)
            self.languages_group.addAction(self.espanol_action)
            self.espanol_action.setChecked(True)

        self.espanol_action.triggered.connect(lambda: self.change_language('fr'))
        
        if not self.german_action:

            self.espanol_action = QAction(_("Alemán"), self)
            self.languages_menu.addAction(self.espanol_action)
            self.espanol_action.setCheckable(True)
            self.languages_group.addAction(self.espanol_action)
            self.espanol_action.setChecked(True)

        self.espanol_action.triggered.connect(lambda: self.change_language('gr'))

        if not self.portugues_action:

            self.portugues_action = QAction(_("Portugués"), self)
            self.languages_menu.addAction(self.portugues_action)
            self.portugues_action.setCheckable(True)
            self.languages_group.addAction(self.portugues_action)

        self.portugues_action.triggered.connect(lambda: self.change_language('pt'))

        if not self.espanol_action:

            self.espanol_action = QAction(_("Español"), self)
            self.languages_menu.addAction(self.espanol_action)
            self.espanol_action.setCheckable(True)
            self.languages_group.addAction(self.espanol_action)
            self.espanol_action.setChecked(True)

        self.espanol_action.triggered.connect(lambda: self.change_language('es'))

        

        # QLABEL PARA MOSTRAR MENSAJE
        string_label = QLabel(_("Verificar palabra"))
        layout.addWidget(string_label )
        string_label.setStyleSheet("font-size:15px; font-weight: bold; color: red")

        # QLINEEDIT PARA INGRESAR LA CADENA
        self.string_linee = QLineEdit()
        layout.addWidget(self.string_linee)
        self.string_linee.setStyleSheet("background:white; color: black")
        

        speed_label = QLabel(_("Velocidad"))
        layout.addWidget(speed_label)
        speed_label.setStyleSheet("font-size:15px; font-weight: bold; color: red")

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(5)
        self.slider.setValue(1)
        layout.addWidget(self.slider)
        

        # BOTÓN PARA PROCESAR
        process_button = QPushButton(_("Verificar"))
        process_button.clicked.connect(self.process)
        layout.addWidget(process_button)
        process_button.setStyleSheet("background-color: #884DFF; color: white; font-weight: bold; font-size:15px")

        

        # QLABEL PARA MOSTRAR LA IMAGEN
        self.picture_label = QLabel()
        layout.addWidget(self.picture_label)
        
        
        
        #QLABEL PARA MOSTRAR LA PILA
        self.pila_label = []

    def process_word(self, word):
        current_status = tuple(self.automata.get_initial_status())  # Convertir a tupla
        self.update_nodes(current_status)
        for symbol in word:
            if (current_status, symbol) in self.automata.get_transitions():
                self.update_edges(current_status, self.automata.get_transitions()[(current_status, symbol)])
                current_status = self.automata.get_transitions()[(current_status, symbol)]
                current_status = tuple(current_status)  # Convertir a tupla
                self.update_nodes(current_status)
            else:
                return False
        return current_status in self.automata.get_final_status()

    def process(self):
        if self.process_word(self.string_linee.text()):
            self.process_voice(self.traduction("La palabra es aceptada"))
            QMessageBox.information(self, self.traduction("Resultado"), self.traduction("La palabra es aceptada"))
        else:
            self.process_voice(self.traduction("La palabra no es aceptada"))
            QMessageBox.warning(self, self.traduction("Resultado"), self.traduction("La palabra no es aceptada"))


    def generate_edges(self):
        edges = set()
        for key, value in self.automata.transiciones.items():
            edges.add((key[0], value[0], key[1]))
        return edges


    def update_nodes(self, status):
        if status in self.automata.posicion:
            positions = self.automata.posicion
            node_colors = ['green' if node == status else 'red' for node in self.graph.nodes()]
            nx.draw(self.graph, positions, with_labels=True, node_color=node_colors)
            self.draw_labels()
            plt.savefig('output.png', dpi=300, format='png', bbox_inches='tight')
            self.update_picture()
            plt.pause(1 / 1.0)  # You can adjust the pause time as needed
        else:
            print(f"El estado {status} no se encuentra en la posición del autómata.")

        
    def update_edges(self, initial_status, final_status):
        nx.draw(self.graph, self.automata.get_position(), with_labels = True, node_color = "red")
        nx.draw_networkx_edges(self.graph, self.automata.get_position(), edgelist = {(initial_status, final_status)}, edge_color = "blue")
        
        # OBTIENE EL PESO DE CADA ARISTA
        weight = nx.get_edge_attributes(self.graph, 'weight')
        # DIBUJA EL GRAFO CON LOS PESOS DE CADA ARISTA
        nx.draw_networkx_edge_labels(self.graph, self.automata.get_position(), edge_labels = weight)
        nx.draw_networkx_edge_labels(self.graph, self.automata.get_position(), edge_labels = {(initial_status, final_status): weight[(initial_status, final_status)]}, font_color = "green")

        plt.savefig('output.png', dpi = 300, format = 'png', bbox_inches ='tight')
        self.update_picture()

        plt.pause(1 / self.slider.value())

    def draw_labels(self):
        weight = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw_networkx_edge_labels(self.graph, self.automata.posicion, edge_labels=weight)

    def update_picture(self):
        pixmap = QPixmap("output.png")
        item = self.scene.addPixmap(pixmap)
        item.setPos(0, 0)
        self.view.fitInView(item, Qt.KeepAspectRatio)
        self.view.setScene(self.scene)

    def process_voice(self, texto):
        objeto = gTTS(text = texto, lang = self.get_language(), slow = False)
        objeto.save('mensaje.mp3')
        pygame.mixer.init()
        pygame.mixer.music.load("mensaje.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    def change_language(self, language):
        if language == 'en':
            self.ingles_action.setChecked(True)
            locale = 'en'
        elif language == 'pt':
            self.portugues_action.setChecked(True)
            locale = 'pt'
        elif language == 'fr':
            self.portugues_action.setChecked(True)
            locale = 'fr'
        elif language == 'gr':
            self.portugues_action.setChecked(True)
            locale = 'gr'
        else:
            self.espanol_action.setChecked(True)
            locale = 'es'
        gettext.install('mensajes', localedir, names=("ngettext",))
        gettext.translation('mensajes', localedir, languages=[locale]).install()
        self.create_interface(locale)

    def get_language(self):
        if self.ingles_action.isChecked():
            return 'en'
        elif self.portugues_action.isChecked():
            return 'pt'
        elif self.espanol_action.isChecked():
            return 'es'
        elif self.espanol_action.isChecked():
            return 'fr'
        elif self.espanol_action.isChecked():
            return 'gr'

    def traduction(self, mensaje):
        language = self.get_language()
        translations = gettext.translation('mensajes', localedir, languages=[language])
        translations.install()
        _ = translations.gettext
        return _(mensaje)

    def language_text_update(self):
        self.ingles_action.setText(self.traduction("Inglés"))
        self.espanol_action.setText(self.traduction("Español"))
        self.portugues_action.setText(self.traduction("Portugués"))
        self.frances_action.setText(self.traduction("Francés"))
        self.german_action.setText(self.traduction("Alemán"))
        self.languages_menu.setTitle(self.traduction("Idiomas"))
        

    
if __name__ == '__main__':
    app = QApplication([])
    automata = create_automata()  # You should define create_automata() function
    window = Interface(automata)
    window.show()
    app.exec()
