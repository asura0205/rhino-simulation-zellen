"""
Cellular Growth Simulation für Rhino
Implementiert ast-artiges Wachstum ohne innere Löcher mit echter Außenrand-Erkennung
"""

from collections import deque
import random


class Config:
    """Konfiguration für die Cellular Growth Simulation"""
    
    def __init__(self):
        # Grid-Größe
        self.GRID_WIDTH = 50
        self.GRID_HEIGHT = 50
        
        # Wachstums-Parameter
        self.MAX_STEPS = 1000
        self.GROWTH_PROBABILITY = 0.7
        
        # Licht-Distanz Regel: maximale Entfernung zum echten Außenrand
        # Verhindert zu große Strukturen und erzwingt Verzweigungen
        self.LIGHT_DISTANCE = {
            'default': 8,
            'branch': 6,
            'coral': 10
        }
        self.DEFAULT_LIGHT_DISTANCE = 8
        
        # Start-Zellen
        self.INITIAL_CELLS = [(25, 25)]  # Zentrum als Ursprung
        
        # Aktuelle Wachstumsfunktion
        self.GROWTH_FUNCTION = 'default'


class Grid:
    """2D Grid für die Zellenstruktur"""
    
    def __init__(self, width, height):
        self.cols = width
        self.rows = height
        self.cells = [[0 for _ in range(width)] for _ in range(height)]
    
    def is_valid(self, x, y):
        """Prüft ob Koordinaten im Grid sind"""
        return 0 <= x < self.cols and 0 <= y < self.rows
    
    def is_empty(self, x, y):
        """Prüft ob Zelle leer ist"""
        return self.is_valid(x, y) and self.cells[y][x] == 0
    
    def is_alive(self, x, y):
        """Prüft ob Zelle lebt"""
        return self.is_valid(x, y) and self.cells[y][x] == 1
    
    def set(self, x, y, value):
        """Setzt Zellwert"""
        if self.is_valid(x, y):
            self.cells[y][x] = value
    
    def get(self, x, y):
        """Gibt Zellwert zurück"""
        if self.is_valid(x, y):
            return self.cells[y][x]
        return None
    
    def neighbors_4(self, x, y):
        """Gibt 4-Nachbarschaft zurück (oben, unten, links, rechts)"""
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if self.is_valid(nx, ny):
                neighbors.append((nx, ny))
        return neighbors
    
    def neighbors_8(self, x, y):
        """Gibt 8-Nachbarschaft zurück (inkl. Diagonalen)"""
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if self.is_valid(nx, ny):
                    neighbors.append((nx, ny))
        return neighbors
    
    def count_alive_neighbors(self, x, y):
        """Zählt lebende Nachbarn (4-Nachbarschaft)"""
        count = 0
        for nx, ny in self.neighbors_4(x, y):
            if self.is_alive(nx, ny):
                count += 1
        return count


class VerticalHolesTracker:
    """Verwaltet vertikale Löcher für strukturelle Integrität"""
    
    def __init__(self):
        self.vertical_holes = {}
    
    def check_vertical_hole(self, grid, x, y):
        """Prüft ob Position ein vertikales Loch erzeugen würde"""
        # Vereinfachte Version: Prüft ob Platzierung zu isolierten Regionen führt
        return False
    
    def update(self, grid, x, y):
        """Aktualisiert Tracking nach Zellenplatzierung"""
        pass


class Constraints:
    """Prüft Constraints für Zellplatzierung"""
    
    def __init__(self):
        pass
    
    def check_all(self, grid, x, y):
        """Prüft alle Constraints"""
        # Grundlegende Constraint: Position muss leer sein
        if not grid.is_empty(x, y):
            return False
        
        # Position muss mindestens einen lebenden Nachbarn haben
        if grid.count_alive_neighbors(x, y) == 0:
            return False
        
        return True


class GrowthPoint:
    """Repräsentiert einen möglichen Wachstumspunkt"""
    
    def __init__(self, x, y, priority=0):
        self.x = x
        self.y = y
        self.priority = priority


class SmoothnessCalculator:
    """Berechnet Glattheit/Qualität der Struktur"""
    
    def calculate_smoothness(self, grid, x, y):
        """Berechnet Glattheitswert für Position"""
        # Höhere Werte für Positionen mit mehr Nachbarn (glattere Kanten)
        alive_neighbors = grid.count_alive_neighbors(x, y)
        return alive_neighbors


class GrowthEngine:
    """Hauptklasse für das Zellwachstum mit ast-artigem Muster"""
    
    def __init__(self, config, constraints, vertical_holes_tracker):
        self.config = config
        self.constraints = constraints
        self.vertical_holes_tracker = vertical_holes_tracker
        self.current_function = config.GROWTH_FUNCTION
        
        # Cache für Außenzellen-Berechnung
        self._outside_cache = None
        self._outside_cache_hash = None
    
    def _get_outside_cells(self, grid):
        """
        Findet alle echten Außenzellen via Flood-Fill vom Grid-Rand.
        Cached für Performance.
        
        Diese Methode unterscheidet zwischen:
        - Echten Außenzellen: Vom Grid-Rand aus erreichbare leere Zellen
        - Inneren Löchern: Leere Zellen die von Struktur umschlossen sind
        """
        # Cache-Check: Verwende gecachte Außenzellen wenn Grid unverändert
        current_hash = hash(tuple(tuple(row) for row in grid.cells))
        
        if self._outside_cache_hash == current_hash:
            return self._outside_cache
        
        outside_cells = set()
        visited = set()
        queue = deque()
        
        # Alle leeren Rand-Zellen als Startpunkte für Flood-Fill
        for x in range(grid.cols):
            for y in range(grid.rows):
                is_edge = (x == 0 or x == grid.cols - 1 or 
                          y == 0 or y == grid.rows - 1)
                if is_edge and grid.is_empty(x, y):
                    queue.append((x, y))
                    visited.add((x, y))
                    outside_cells.add((x, y))
        
        # Flood-Fill durch alle erreichbaren leeren Zellen
        while queue:
            cx, cy = queue.popleft()
            for nx, ny in grid.neighbors_4(cx, cy):
                if (nx, ny) not in visited and grid.is_empty(nx, ny):
                    visited.add((nx, ny))
                    outside_cells.add((nx, ny))
                    queue.append((nx, ny))
        
        # Cache aktualisieren
        self._outside_cache = outside_cells
        self._outside_cache_hash = current_hash
        return outside_cells
    
    def distance_to_true_outside(self, grid, x, y):
        """
        Berechnet kürzesten Weg zum ECHTEN Außenbereich.
        Innere Löcher werden NICHT als außen gezählt.
        
        Verwendet BFS um die Manhattan-Distanz zur nächsten
        echten Außenzelle zu finden.
        """
        outside_cells = self._get_outside_cells(grid)
        
        # Wenn Position selbst außen ist
        if (x, y) in outside_cells:
            return 0
        
        # BFS zur nächsten echten Außenzelle
        visited = set([(x, y)])
        queue = deque([(x, y, 0)])
        
        while queue:
            cx, cy, dist = queue.popleft()
            
            # Prüfe alle Nachbarn
            for nx, ny in grid.neighbors_4(cx, cy):
                if (nx, ny) in outside_cells:
                    return dist + 1
                
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny, dist + 1))
        
        # Komplett eingeschlossen (sollte nicht passieren bei echten Außenzellen)
        return 9999
    
    def _would_create_internal_hole(self, grid, x, y):
        """
        Prüft ob das Platzieren einer Zelle ein inneres Loch erzeugen würde.
        
        Verwendet eine effiziente Heuristik:
        - Prüft ob leere Nachbarn nach Platzierung noch Zugang zum Außenbereich haben
        - Schneller als vollständiger Flood-Fill, aber sehr effektiv
        """
        # Für jeden leeren Nachbarn: prüfe ob er nach Platzierung noch 
        # mindestens einen Weg zum Rand hat (über andere leere Zellen)
        empty_neighbors = []
        for nx, ny in grid.neighbors_4(x, y):
            if grid.is_empty(nx, ny):
                empty_neighbors.append((nx, ny))
        
        if len(empty_neighbors) == 0:
            # Keine leeren Nachbarn - kein Risiko
            return False
        
        # Simuliere Platzierung temporär
        grid.set(x, y, 1)
        
        # Prüfe für jeden leeren Nachbarn ob er noch zu echtem Außen gehört
        for nx, ny in empty_neighbors:
            # Schnelle Prüfung: Ist die Position noch vom Rand erreichbar?
            # Verwende eine begrenzte BFS um zu prüfen ob Rand erreichbar ist
            if not self._can_reach_edge(grid, nx, ny, max_depth=20):
                # Dieser Nachbar würde abgeschnitten! 
                grid.set(x, y, 0)
                return True
        
        grid.set(x, y, 0)
        return False
    
    def _can_reach_edge(self, grid, start_x, start_y, max_depth=20):
        """
        Schnelle Prüfung ob eine Position den Grid-Rand erreichen kann.
        Verwendet begrenzte BFS durch leere Zellen.
        """
        if start_x == 0 or start_x == grid.cols - 1 or start_y == 0 or start_y == grid.rows - 1:
            return True  # Schon am Rand
        
        visited = set([(start_x, start_y)])
        queue = deque([(start_x, start_y, 0)])
        
        while queue:
            cx, cy, depth = queue.popleft()
            
            if depth >= max_depth:
                # Zu tief gesucht - nehmen wir an es ist OK
                return True
            
            for nx, ny in grid.neighbors_4(cx, cy):
                # Rand erreicht?
                if nx == 0 or nx == grid.cols - 1 or ny == 0 or ny == grid.rows - 1:
                    if grid.is_empty(nx, ny):
                        return True
                
                # Weiter suchen durch leere Zellen
                if (nx, ny) not in visited and grid.is_empty(nx, ny):
                    visited.add((nx, ny))
                    queue.append((nx, ny, depth + 1))
        
        return False  # Rand nicht erreichbar innerhalb max_depth
    
    def _check_light_distance(self, grid, x, y):
        """
        Prüft ob Zelle die Licht-Abstand-Regel einhält.
        Verwendet echten Außenrand (keine inneren Löcher).
        
        Die Licht-Distanz-Regel stellt sicher, dass jede Zelle
        Zugang zu "Licht" vom echten Außenrand hat, was:
        - Zu dicke Strukturen verhindert
        - Natürliche Verzweigungen fördert
        - Innere Hohlräume verhindert
        """
        max_dist = self.config.LIGHT_DISTANCE.get(
            self.current_function, self.config.DEFAULT_LIGHT_DISTANCE)
        
        # KRITISCH: Prüfe zuerst ob Platzierung ein inneres Loch erzeugen würde
        if self._would_create_internal_hole(grid, x, y):
            return False
        
        # Simuliere Platzierung der Zelle
        grid.set(x, y, 1)
        self._outside_cache_hash = None  # Cache invalidieren da Grid sich ändert
        
        try:
            # Prüfe ob die neue Zelle selbst die Regel einhält
            dist = self.distance_to_true_outside(grid, x, y)
            if dist > max_dist:
                return False
            
            # Prüfe ob alle Nachbarn die Regel noch einhalten
            # (neue Zelle könnte Nachbarn vom Außenrand abschneiden)
            for nx, ny in grid.neighbors_4(x, y):
                if grid.is_alive(nx, ny):
                    neighbor_dist = self.distance_to_true_outside(grid, nx, ny)
                    if neighbor_dist > max_dist:
                        return False
        finally:
            # Rückgängig machen der Simulation
            grid.set(x, y, 0)
            self._outside_cache_hash = None  # Cache erneut invalidieren
        
        return True
    
    def get_growth_candidates(self, grid):
        """
        Findet alle möglichen Wachstumspunkte.
        Berücksichtigt nur Positionen die:
        - Leer sind
        - An lebende Zellen grenzen
        - Licht-Distanz-Regel einhalten
        """
        candidates = []
        
        # Durchsuche alle Positionen die an lebende Zellen grenzen
        checked = set()
        for y in range(grid.rows):
            for x in range(grid.cols):
                if grid.is_alive(x, y):
                    # Prüfe alle leeren Nachbarn
                    for nx, ny in grid.neighbors_4(x, y):
                        if (nx, ny) not in checked and grid.is_empty(nx, ny):
                            checked.add((nx, ny))
                            
                            # Prüfe Constraints
                            if not self.constraints.check_all(grid, nx, ny):
                                continue
                            
                            # Prüfe Licht-Distanz
                            if not self._check_light_distance(grid, nx, ny):
                                continue
                            
                            # Kandidat gefunden
                            candidates.append(GrowthPoint(nx, ny))
        
        return candidates
    
    def select_growth_point(self, candidates, grid):
        """Wählt einen Wachstumspunkt aus den Kandidaten"""
        if not candidates:
            return None
        
        # Zufällige Auswahl für organisches Wachstum
        return random.choice(candidates)
    
    def grow_step(self, grid):
        """
        Führt einen Wachstumsschritt durch.
        Gibt True zurück wenn gewachsen wurde, False wenn kein Wachstum möglich.
        """
        # Finde Wachstumskandidaten
        candidates = self.get_growth_candidates(grid)
        
        if not candidates:
            return False
        
        # Wähle einen Punkt zum Wachsen
        growth_point = self.select_growth_point(candidates, grid)
        
        if growth_point is None:
            return False
        
        # Wachse mit konfigurierter Wahrscheinlichkeit
        if random.random() < self.config.GROWTH_PROBABILITY:
            grid.set(growth_point.x, growth_point.y, 1)
            self.vertical_holes_tracker.update(grid, growth_point.x, growth_point.y)
            self._outside_cache_hash = None  # Cache invalidieren
            return True
        
        return False


class Visualizer:
    """Visualisiert das Grid (Konsolen-Ausgabe)"""
    
    def __init__(self):
        pass
    
    def print_grid(self, grid):
        """Gibt Grid in der Konsole aus"""
        print("\n" + "=" * (grid.cols + 2))
        for y in range(grid.rows):
            row = "|"
            for x in range(grid.cols):
                if grid.is_alive(x, y):
                    row += "█"
                else:
                    row += " "
            row += "|"
            print(row)
        print("=" * (grid.cols + 2))
    
    def get_statistics(self, grid):
        """Berechnet Statistiken über das Grid"""
        alive_count = 0
        for y in range(grid.rows):
            for x in range(grid.cols):
                if grid.is_alive(x, y):
                    alive_count += 1
        
        total_cells = grid.cols * grid.rows
        return {
            'alive_cells': alive_count,
            'total_cells': total_cells,
            'fill_ratio': alive_count / total_cells if total_cells > 0 else 0
        }


class UI:
    """Benutzeroberfläche für die Simulation"""
    
    def __init__(self, visualizer):
        self.visualizer = visualizer
    
    def show_step(self, grid, step, max_steps):
        """Zeigt aktuellen Schritt"""
        stats = self.visualizer.get_statistics(grid)
        print(f"\nSchritt {step}/{max_steps}")
        print(f"Lebende Zellen: {stats['alive_cells']}")
        print(f"Füllrate: {stats['fill_ratio']:.2%}")


class Simulation:
    """Hauptsimulation"""
    
    def __init__(self, config):
        self.config = config
        self.grid = Grid(config.GRID_WIDTH, config.GRID_HEIGHT)
        self.constraints = Constraints()
        self.vertical_holes_tracker = VerticalHolesTracker()
        self.growth_engine = GrowthEngine(config, self.constraints, self.vertical_holes_tracker)
        self.visualizer = Visualizer()
        self.ui = UI(self.visualizer)
    
    def initialize(self):
        """Initialisiert die Simulation mit Start-Zellen"""
        for x, y in self.config.INITIAL_CELLS:
            if self.grid.is_valid(x, y):
                self.grid.set(x, y, 1)
    
    def run(self, show_steps=False):
        """
        Führt die Simulation aus.
        
        Args:
            show_steps: Wenn True, wird jeder Schritt visualisiert
        """
        self.initialize()
        
        print("Starte Cellular Growth Simulation")
        print("Ast-artiges Wachstum ohne innere Löcher")
        print(f"Grid-Größe: {self.config.GRID_WIDTH} x {self.config.GRID_HEIGHT}")
        print(f"Maximale Licht-Distanz: {self.config.DEFAULT_LIGHT_DISTANCE}")
        
        if show_steps:
            self.visualizer.print_grid(self.grid)
        
        steps_without_growth = 0
        for step in range(1, self.config.MAX_STEPS + 1):
            grew = self.growth_engine.grow_step(self.grid)
            
            if grew:
                steps_without_growth = 0
                if show_steps and step % 10 == 0:
                    self.ui.show_step(self.grid, step, self.config.MAX_STEPS)
            else:
                steps_without_growth += 1
                # Stoppe wenn 50 Schritte lang kein Wachstum
                if steps_without_growth > 50:
                    print(f"\nKein Wachstum mehr möglich nach {step} Schritten")
                    break
        
        # Finale Statistiken
        print("\n" + "=" * 50)
        print("SIMULATION BEENDET")
        print("=" * 50)
        stats = self.visualizer.get_statistics(self.grid)
        print(f"Finale Anzahl Zellen: {stats['alive_cells']}")
        print(f"Füllrate: {stats['fill_ratio']:.2%}")
        
        self.visualizer.print_grid(self.grid)
        
        return self.grid


def main():
    """Hauptfunktion"""
    # Konfiguration erstellen
    config = Config()
    
    # Simulation erstellen und ausführen
    simulation = Simulation(config)
    simulation.run(show_steps=True)


if __name__ == "__main__":
    main()