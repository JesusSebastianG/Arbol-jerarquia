import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox

class Nodo:
    def __init__(self, valor, izq=None, der=None):
        self.valor = valor
        self.izq = izq
        self.der = der

# ========================
# PARSER SEMÁNTICO CON PRECEDENCIA DESCENDENTE
# ========================

class Parser:
    def __init__(self, expresion):
        self.expresion = expresion.replace(' ', '')
        self.pos = 0
        self.token_actual = None
        self.avanzar()
    
    def avanzar(self):
        if self.pos < len(self.expresion):
            self.token_actual = self.expresion[self.pos]
            self.pos += 1
        else:
            self.token_actual = None
    
    def siguiente(self):
        """Devuelve el siguiente caracter sin avanzar el puntero"""
        if self.pos < len(self.expresion):
            return self.expresion[self.pos]
        return None

    def parse(self):
        """Parsea la expresión completa"""
        resultado = self.parse_expresion_logica()
        if self.token_actual is not None:
            raise ValueError(f"Token inesperado: {self.token_actual}")
        return resultado
    
    def parse_expresion_logica(self):
        """Parsea OR lógico (|, ∨)"""
        nodo = self.parse_expresion_and()
        while self.token_actual in ('|', '∨'):
            op = self.token_actual
            self.avanzar()
            derecho = self.parse_expresion_and()
            nodo = Nodo(op, nodo, derecho)
        return nodo
    
    def parse_expresion_and(self):
        """Parsea AND lógico (&, ∧)"""
        nodo = self.parse_expresion_comparacion()
        while self.token_actual in ('&', '∧'):
            op = self.token_actual
            self.avanzar()
            derecho = self.parse_expresion_comparacion()
            nodo = Nodo(op, nodo, derecho)
        return nodo
    
    def parse_expresion_comparacion(self):
        """
        Parsea comparaciones (<, >, <=, >=, =, !=, ≠, ≤, ≥)
        Maneja operadores de dos caracteres y un caracter.
        """
        nodo = self.parse_expresion_suma()
        while True:
            op = None
            # Verifica dos caracteres si quedan suficientes
            if self.token_actual and self.siguiente():
                dos_car = self.token_actual + self.siguiente()
                if dos_car in ('<=', '>=', '!='):
                    op = dos_car
                    self.avanzar()
                    self.avanzar()
            # Verifica operadores de un solo caracter válido
            if not op and self.token_actual in ('<', '>', '=', '≠', '≤', '≥'):
                op = self.token_actual
                self.avanzar()
            if not op:
                break
            derecho = self.parse_expresion_suma()
            nodo = Nodo(op, nodo, derecho)
        return nodo
    
    def parse_expresion_suma(self):
        """Parsea suma y resta (+, -)"""
        nodo = self.parse_expresion_multiplicacion()
        while self.token_actual in ('+', '-'):
            op = self.token_actual
            self.avanzar()
            derecho = self.parse_expresion_multiplicacion()
            nodo = Nodo(op, nodo, derecho)
        return nodo
    
    def parse_expresion_multiplicacion(self):
        """Parsea multiplicación y división (*, /)"""
        nodo = self.parse_expresion_potencia()
        while self.token_actual in ('*', '/'):
            op = self.token_actual
            self.avanzar()
            derecho = self.parse_expresion_potencia()
            nodo = Nodo(op, nodo, derecho)
        return nodo
    
    def parse_expresion_potencia(self):
        """Parsea potencia (^) - asociativo a la derecha"""
        nodo = self.parse_factor()
        if self.token_actual == '^':
            op = self.token_actual
            self.avanzar()
            derecho = self.parse_expresion_potencia()  # Asociatividad derecha
            nodo = Nodo(op, nodo, derecho)
        return nodo
    
    def parse_factor(self):
        """Parsea factor: número, variable, negación, paréntesis"""
        if self.token_actual is None:
            raise ValueError("Esperaba un factor")
        
        if self.token_actual in ('¬', '~'):
            op = self.token_actual
            self.avanzar()
            operando = self.parse_factor()
            return Nodo(op, operando, None)
        
        elif self.token_actual == '(':
            self.avanzar()
            # -------- CORRECCIÓN: analizar subexpresión lógica, NO toda la expresión ------
            nodo = self.parse_expresion_logica()
            if self.token_actual != ')':
                raise ValueError("Falta paréntesis de cierre")
            self.avanzar()
            return nodo
        
        else:
            # Leer token (variable o número)
            token = ''
            while self.token_actual and (self.token_actual.isalnum() or self.token_actual == '_'):
                token += self.token_actual
                self.avanzar()
            
            if not token:
                raise ValueError(f"Token inválido: {self.token_actual}")
            
            return Nodo(token)

def construir_arbol(expresion):
    """Construye el árbol usando el parser semántico"""
    try:
        parser = Parser(expresion)
        arbol = parser.parse()
        return arbol
    except Exception as e:
        raise ValueError(f"Error al parsear la expresión: {str(e)}")

# ========================
# ALGORITMO DE POSICIONAMIENTO ÓPTIMO
# ========================

def _calcular_ancho_subarbol(nodo):
    """Calcula el ancho del subárbol para posicionamiento"""
    if nodo is None:
        return 0
    
    if nodo.izq is None and nodo.der is None:
        return 1
    
    ancho_izq = _calcular_ancho_subarbol(nodo.izq)
    ancho_der = _calcular_ancho_subarbol(nodo.der)
    
    return max(ancho_izq, ancho_der) + 2

def _posicionar_nodos_optimo(nodo, pos, nivel=0, x_offset=0, sep=30):
    """Posiciona nodos con distribución jerárquica óptima y separación configurable"""
    if nodo is None:
        return 0

    if nodo.izq is None and nodo.der is None:
        pos[nodo] = (x_offset, -nivel)
        return 1

    if nodo.izq and nodo.der:
        ancho_izq = _calcular_ancho_subarbol(nodo.izq)
        ancho_der = _calcular_ancho_subarbol(nodo.der)

        # Espacio proporcional al tamaño de los subárboles
        espacio = max(sep, ancho_izq + ancho_der)
        x_izq = x_offset
        x_der = x_offset + ancho_izq + espacio

        _posicionar_nodos_optimo(nodo.izq, pos, nivel + 1, x_izq, sep)
        _posicionar_nodos_optimo(nodo.der, pos, nivel + 1, x_der, sep)

        x_centro = (x_izq + x_der) / 2
        pos[nodo] = (x_centro, -nivel)
        return ancho_izq + espacio + ancho_der

    elif nodo.izq:
        desplazamiento = _posicionar_nodos_optimo(nodo.izq, pos, nivel + 1, x_offset, sep)
        pos[nodo] = (x_offset + desplazamiento / 2, -nivel)
        return desplazamiento

    elif nodo.der:
        desplazamiento = _posicionar_nodos_optimo(nodo.der, pos, nivel + 1, x_offset + sep, sep)
        pos[nodo] = (x_offset + sep + desplazamiento / 2, -nivel)
        return sep + desplazamiento

    return 1

def dibujar_arbol_mejorado(raiz, ax):
    if raiz is None:
        ax.text(0.5, 0.5, "Árbol vacío", ha='center', va='center', transform=ax.transAxes, fontsize=16)
        return
    
    pos = {}
    _posicionar_nodos_optimo(raiz, pos, 0, 0, sep=30)  # Mayor separación entre nodos
    
    # Calcular límites
    xs = [x for x, y in pos.values()]
    ys = [y for x, y in pos.values()]
    
    if not xs or not ys:
        ax.text(0.5, 0.5, "Árbol vacío", ha='center', va='center', transform=ax.transAxes, fontsize=16)
        return
    
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    
    # Añadir márgenes generosos
    margin_x = max((max_x - min_x) * 0.4, 8)
    margin_y = max((max_y - min_y) * 0.4, 3)
    
    # Configurar título
    ax.set_title("Árbol de Expresión", fontsize=18, fontweight='bold', pad=20)
    
    # Dibujar nodos y conexiones
    for nodo, (x, y) in pos.items():
        # Determinar color según tipo de nodo
        if es_operador(nodo.valor):
            color_nodo = 'lightcoral'
        elif nodo.valor.replace('.', '').replace('-', '').isdigit():
            color_nodo = 'lightgreen'
        else:
            color_nodo = 'lightblue'
        
        # Dibujar nodo con borde grueso y texto centrado
        ax.scatter(x, y, s=1200, facecolor=color_nodo, edgecolors='black', linewidths=3.5)
        ax.text(x, y, str(nodo.valor), ha='center', va='center', 
                fontsize=16, weight='bold', fontfamily='monospace',
                bbox=dict(facecolor='white', alpha=0.95, edgecolor='black', boxstyle='round,pad=0.4'))
        
        # Dibujar conexiones
        if nodo.izq:
            x2, y2 = pos[nodo.izq]
            ax.plot([x, x2], [y, y2], 'k-', linewidth=3.5, alpha=0.85, zorder=0)
        if nodo.der:
            x2, y2 = pos[nodo.der]
            ax.plot([x, x2], [y, y2], 'k-', linewidth=3.5, alpha=0.85, zorder=0)
    
    ax.set_xlim(min_x - margin_x, max_x + margin_x)
    ax.set_ylim(min_y - margin_y, max_y + margin_y)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.15, linestyle='--', linewidth=0.5)
    ax.set_facecolor('white')

def es_operador(c):
    return c in "+-*/^=<>¬~&|∧∨≠≤≥" or c in ('<=', '>=', '!=')

def recorrer_prefijo(nodo):
    if nodo is None:
        return ''
    resultado = nodo.valor
    if nodo.izq:
        resultado += ' ' + recorrer_prefijo(nodo.izq)
    if nodo.der:
        resultado += ' ' + recorrer_prefijo(nodo.der)
    return resultado.strip()

def recorrer_infijo(nodo):
    if nodo is None:
        return ''
    resultado = ''
    if nodo.izq:
        resultado += '(' + recorrer_infijo(nodo.izq) + ')'
    resultado += str(nodo.valor)
    if nodo.der:
        resultado += '(' + recorrer_infijo(nodo.der) + ')'
    return resultado

def recorrer_postfijo(nodo):
    if nodo is None:
        return ''
    resultado = ''
    if nodo.izq:
        resultado += recorrer_postfijo(nodo.izq) + ' '
    if nodo.der:
        resultado += recorrer_postfijo(nodo.der) + ' '
    resultado += str(nodo.valor)
    return resultado.strip()

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Árbol de Expresión - Operadores Lógicos y Aritméticos")
        self.root.geometry("1800x1200")
        
        # Frame principal
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame para entrada
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="Expresión:").pack(side=tk.LEFT)
        self.entry_expresion = ttk.Entry(input_frame, width=100)
        self.entry_expresion.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        self.entry_expresion.insert(0, "A+(2-X)*Y-9/4<=45^6*(9/4)>H")  # Ejemplo con <= y >
        
        ttk.Button(input_frame, text="Generar Árbol", command=self.generar_arbol).pack(side=tk.LEFT)
        
        # Frame para información
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.lbl_prefijo = ttk.Label(info_frame, text="Prefijo: ")
        self.lbl_prefijo.pack(anchor=tk.W)
        
        self.lbl_postfijo = ttk.Label(info_frame, text="Postfijo: ")
        self.lbl_postfijo.pack(anchor=tk.W)
        
        self.lbl_infijo = ttk.Label(info_frame, text="Infijo: ")
        self.lbl_infijo.pack(anchor=tk.W)
        
        # Frame para el gráfico
        plot_frame = ttk.Frame(main_frame)
        plot_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear figura de matplotlib
        self.fig, self.ax = plt.subplots(figsize=(18, 10))
        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Mostrar ayuda
        help_frame = ttk.Frame(main_frame)
        help_frame.pack(fill=tk.X, pady=(10, 0))
        
        help_text = """
Operadores soportados: +, -, *, /, ^ (potencia), =, <, >, <=, >=, !=, ¬ (negación), ~ (negación), & (AND), | (OR)
Ejemplos: A+B, A+(B*C), ¬A, A&B|C, A+(2-X)*Y-9/4<=45^6*(9/4)>H
        """
        ttk.Label(help_frame, text=help_text, foreground='gray').pack(anchor=tk.W)
        
        # Ejemplo inicial
        self.generar_arbol()
    
    def generar_arbol(self):
        try:
            expresion = self.entry_expresion.get().strip()
            if not expresion:
                messagebox.showwarning("Advertencia", "Por favor ingrese una expresión")
                return
            
            # Limpiar el eje
            self.ax.clear()
            self.ax.set_axis_off()
            
            # Construir el árbol con el parser semántico
            arbol = construir_arbol(expresion)
            
            # Mostrar recorridos
            if arbol:
                prefijo = recorrer_prefijo(arbol)
                postfijo = recorrer_postfijo(arbol)
                infijo = recorrer_infijo(arbol)
                
                self.lbl_prefijo.config(text=f"Prefijo: {prefijo}")
                self.lbl_postfijo.config(text=f"Postfijo: {postfijo}")
                self.lbl_infijo.config(text=f"Infijo: {infijo}")
            else:
                self.lbl_prefijo.config(text="Prefijo: ")
                self.lbl_postfijo.config(text="Postfijo: ")
                self.lbl_infijo.config(text="Infijo: ")
            
            # Dibujar el árbol
            dibujar_arbol_mejorado(arbol, self.ax)
            
            # Actualizar el canvas
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar la expresión: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()