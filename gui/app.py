"""
Bloc 6 — Interface Graphique Tkinter
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
import time
import threading

import networkx as nx
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from network.graph import Graph
from network.packet import Packet
from simulation.queue_manager import QueueManager


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Analyseur de Trafic Réseau")
        self.geometry("1100x650")
        self.configure(bg="#1e1e1e")

        # Modèle
        self.graph          = Graph()
        self.nx_graph       = nx.Graph()
        self.queue          = QueueManager(capacity=5)
        self.packet_counter = 1
        self.running        = False
        self._active        = None

        self._build_ui()

    # ── Construction UI ───────────────────────────────────────────────────────
    def _build_ui(self):
        # Titre
        tk.Label(self, text="ANALYSEUR DE TRAFIC RÉSEAU",
                 font=("Courier", 14, "bold"),
                 fg="#00d2ff", bg="#1e1e1e").pack(pady=8)

        # Corps principal
        corps = tk.Frame(self, bg="#1e1e1e")
        corps.pack(fill="both", expand=True, padx=10, pady=5)

        # Colonne gauche
        gauche = tk.Frame(corps, bg="#1e1e1e")
        gauche.pack(side="left", fill="y", padx=(0, 10))
        self._panel_reseau(gauche)
        self._panel_paquets(gauche)

        # Colonne droite
        droite = tk.Frame(corps, bg="#1e1e1e")
        droite.pack(side="left", fill="both", expand=True)
        self._panel_graphe(droite)
        self._panel_log(droite)

    # ── Panneau Réseau ────────────────────────────────────────────────────────
    def _panel_reseau(self, parent):
        frm = self._cadre(parent, "RÉSEAU")

        tk.Label(frm, text="Nœud :", bg="#2d2d2d", fg="white",
                 font=("Courier", 9)).grid(row=0, column=0, padx=5, pady=4)
        self.e_node = tk.Entry(frm, width=8, bg="#3d3d3d", fg="white",
                               insertbackground="white", relief="flat")
        self.e_node.grid(row=0, column=1, padx=5, pady=4)
        tk.Button(frm, text="Ajouter", command=self._add_node,
                  bg="#00d2ff", fg="black", relief="flat",
                  font=("Courier", 9, "bold")).grid(row=0, column=2, padx=5)

        tk.Label(frm, text="A :", bg="#2d2d2d", fg="white",
                 font=("Courier", 9)).grid(row=1, column=0, padx=5, pady=4)
        self.e_a = tk.Entry(frm, width=8, bg="#3d3d3d", fg="white",
                            insertbackground="white", relief="flat")
        self.e_a.grid(row=1, column=1, padx=5)

        tk.Label(frm, text="B :", bg="#2d2d2d", fg="white",
                 font=("Courier", 9)).grid(row=2, column=0, padx=5, pady=4)
        self.e_b = tk.Entry(frm, width=8, bg="#3d3d3d", fg="white",
                            insertbackground="white", relief="flat")
        self.e_b.grid(row=2, column=1, padx=5)
        tk.Button(frm, text="Connecter", command=self._add_connection,
                  bg="#3a7bd5", fg="white", relief="flat",
                  font=("Courier", 9, "bold")).grid(row=2, column=2, padx=5)

    # ── Panneau Paquets ───────────────────────────────────────────────────────
    def _panel_paquets(self, parent):
        frm = self._cadre(parent, "PAQUETS & SIMULATION")

        for i, (lbl, attr, val) in enumerate([
            ("Source :",      "e_src",  ""),
            ("Destination :", "e_dst",  ""),
            ("Taille (KB) :", "e_size", "10"),
        ]):
            tk.Label(frm, text=lbl, bg="#2d2d2d", fg="white",
                     font=("Courier", 9)).grid(row=i, column=0, padx=5, pady=3)
            e = tk.Entry(frm, width=10, bg="#3d3d3d", fg="white",
                         insertbackground="white", relief="flat")
            e.insert(0, val)
            e.grid(row=i, column=1, padx=5, pady=3)
            setattr(self, attr, e)

        tk.Label(frm, text="Capacité :", bg="#2d2d2d", fg="white",
                 font=("Courier", 9)).grid(row=3, column=0, padx=5, pady=3)
        self.e_cap = tk.Entry(frm, width=10, bg="#3d3d3d", fg="white",
                              insertbackground="white", relief="flat")
        self.e_cap.insert(0, "5")
        self.e_cap.grid(row=3, column=1, padx=5, pady=3)

        # Boutons
        btns = [
            ("Envoyer paquet",        self._add_packet,         "#3fb950"),
            ("▶ Lancer simulation",   self._run_simulation,     "#a855f7"),
            ("Goulots",               self._show_bottlenecks,   "#d29922"),
            ("Plus court chemin",     self._show_shortest_path, "#3a7bd5"),
            ("Réinitialiser",         self._reset,              "#f85149"),
        ]
        for i, (txt, cmd, col) in enumerate(btns):
            tk.Button(frm, text=txt, command=cmd, bg=col,
                      fg="black" if col == "#3fb950" else "white",
                      relief="flat", font=("Courier", 9, "bold"),
                      width=20).grid(row=4+i, column=0, columnspan=2,
                                     padx=5, pady=3, sticky="ew")

    # ── Panneau Graphe ────────────────────────────────────────────────────────
    def _panel_graphe(self, parent):
        tk.Label(parent, text="VISUALISATION", font=("Courier", 9, "bold"),
                 fg="#00d2ff", bg="#1e1e1e").pack(anchor="w")
        card = tk.Frame(parent, bg="#2d2d2d")
        card.pack(fill="both", expand=True, pady=(0, 5))

        self.fig, self.ax = plt.subplots(figsize=(6, 3))
        self.fig.patch.set_facecolor("#2d2d2d")
        self.ax.set_facecolor("#1e1e1e")
        self.ax.axis("off")

        self.canvas = FigureCanvasTkAgg(self.fig, master=card)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self._draw_graph()

    # ── Panneau Log ───────────────────────────────────────────────────────────
    def _panel_log(self, parent):
        tk.Label(parent, text="JOURNAL", font=("Courier", 9, "bold"),
                 fg="#00d2ff", bg="#1e1e1e").pack(anchor="w")
        self.log = scrolledtext.ScrolledText(
            parent, height=6, font=("Courier", 9),
            bg="#2d2d2d", fg="white", relief="flat")
        self.log.pack(fill="x")
        self.log.tag_config("OK",    foreground="#3fb950")
        self.log.tag_config("ERR",   foreground="#f85149")
        self.log.tag_config("WARN",  foreground="#d29922")
        self.log.tag_config("INFO",  foreground="#00d2ff")
        self._log("Système prêt.", "INFO")

    # ── Actions ───────────────────────────────────────────────────────────────
    def _add_node(self):
        name = self.e_node.get().strip().upper()
        if not name:
            return
        if name in self.graph.nodes:
            self._log(f"'{name}' existe déjà.", "WARN")
            return
        self.graph.add_node(name)
        self.nx_graph.add_node(name)
        self.e_node.delete(0, "end")
        self._log(f"Nœud '{name}' ajouté.", "OK")
        self._draw_graph()

    def _add_connection(self):
        a = self.e_a.get().strip().upper()
        b = self.e_b.get().strip().upper()
        if a not in self.graph.nodes or b not in self.graph.nodes:
            self._log(f"Nœud inexistant.", "ERR")
            return
        self.graph.add_connection(a, b)
        self.nx_graph.add_edge(a, b)
        self.e_a.delete(0, "end")
        self.e_b.delete(0, "end")
        self._log(f"Lien {a} ↔ {b} créé.", "OK")
        self._draw_graph()

    def _add_packet(self):
        src  = self.e_src.get().strip().upper()
        dst  = self.e_dst.get().strip().upper()
        try:
            size = int(self.e_size.get().strip())
            cap  = int(self.e_cap.get().strip())
        except ValueError:
            self._log("Taille/capacité invalide.", "ERR")
            return
        if not src or not dst:
            return
        self.queue.capacity = cap
        p = Packet(self.packet_counter, src, dst, size)
        self.packet_counter += 1
        before = self.queue.dropped_packets
        self.queue.add_packet(p)
        if self.queue.dropped_packets > before:
            self._log(f"⚠ Paquet #{p.id_packet} rejeté — file pleine !", "ERR")
        else:
            self._log(f"Paquet #{p.id_packet} : {src}→{dst} ({size}KB) en file.", "OK")

    def _run_simulation(self):
        if self.running:
            self._log("Simulation en cours...", "WARN")
            return
        if self.queue.is_empty():
            self._log("File vide.", "WARN")
            return
        self.running = True
        self._log("─── Simulation démarrée ───", "INFO")
        threading.Thread(target=self._simulate_thread, daemon=True).start()

    def _simulate_thread(self):
        while not self.queue.is_empty():
            p = self.queue.process_packet()
            if p:
                self._active = p
                self.after(0, lambda pk=p: self._log(
                    f"✓ Traité : #{pk.id_packet} {pk.source}→{pk.destination}", "OK"))
                self.after(0, self._draw_graph)
            time.sleep(0.9)
        self._active = None
        stats = self.queue.stats()
        self.after(0, lambda: self._log(
            f"─── Terminé | Perdus : {stats['perdus']} ───", "INFO"))
        self.after(0, self._draw_graph)
        self.running = False

    def _show_bottlenecks(self):
        if not self.nx_graph.nodes:
            self._log("Réseau vide.", "WARN")
            return
        centrality = nx.degree_centrality(self.nx_graph)
        for node, score in sorted(centrality.items(), key=lambda x: x[1], reverse=True):
            tag = "ERR" if score > 0.5 else "WARN" if score > 0.25 else "OK"
            self._log(f"{node} : {score:.2f} {'⚠ GOULOT' if score > 0.5 else ''}", tag)
        self._draw_graph(centrality=centrality)

    def _show_shortest_path(self):
        src = self.e_src.get().strip().upper()
        dst = self.e_dst.get().strip().upper()
        if src not in self.nx_graph or dst not in self.nx_graph:
            self._log("Nœud absent.", "ERR")
            return
        try:
            path = nx.shortest_path(self.nx_graph, source=src, target=dst)
            self._log(f"Chemin : {' → '.join(path)}", "OK")
            self._draw_graph(path=path)
        except nx.NetworkXNoPath:
            self._log("Aucun chemin.", "ERR")

    def _reset(self):
        if messagebox.askyesno("Reset", "Réinitialiser ?"):
            self.graph          = Graph()
            self.nx_graph       = nx.Graph()
            self.queue          = QueueManager(capacity=5)
            self.packet_counter = 1
            self.running        = False
            self._active        = None
            self._draw_graph()
            self._log("Réseau réinitialisé.", "WARN")

    # ── Dessin graphe ─────────────────────────────────────────────────────────
    def _draw_graph(self, path=None, centrality=None):
        self.ax.clear()
        self.ax.set_facecolor("#1e1e1e")
        self.ax.axis("off")

        if not self.nx_graph.nodes:
            self.ax.text(0.5, 0.5, "Ajoutez des nœuds...",
                         ha="center", va="center", color="gray",
                         transform=self.ax.transAxes)
            self.canvas.draw()
            return

        pos = ({list(self.nx_graph.nodes)[0]: (0.5, 0.5)}
               if len(self.nx_graph.nodes) == 1
               else nx.spring_layout(self.nx_graph, seed=42))

        # Couleurs nœuds
        colors = []
        for n in self.nx_graph.nodes:
            if self._active and n in (self._active.source, self._active.destination):
                colors.append("#f85149")
            elif path and n in path:
                colors.append("#3a7bd5")
            elif centrality and centrality.get(n, 0) > 0.5:
                colors.append("#d29922")
            else:
                colors.append("#00d2ff")

        # Couleurs liens
        path_edges = set(zip(path, path[1:])) if path else set()
        edge_colors = [
            "#3a7bd5" if (e in path_edges or (e[1], e[0]) in path_edges)
            else "#555555"
            for e in self.nx_graph.edges
        ]

        nx.draw_networkx_edges(self.nx_graph, pos, ax=self.ax,
                               edge_color=edge_colors, width=2)
        nx.draw_networkx_nodes(self.nx_graph, pos, ax=self.ax,
                               node_color=colors, node_size=500)
        nx.draw_networkx_labels(self.nx_graph, pos, ax=self.ax,
                                font_color="black", font_size=9,
                                font_weight="bold")
        self.fig.tight_layout()
        self.canvas.draw()

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _log(self, msg, tag="INFO"):
        self.log.config(state="normal")
        self.log.insert("end", f"[{time.strftime('%H:%M:%S')}] {msg}\n", tag)
        self.log.see("end")
        self.log.config(state="disabled")

    def _cadre(self, parent, titre):
        tk.Label(parent, text=titre, font=("Courier", 9, "bold"),
                 fg="#00d2ff", bg="#1e1e1e").pack(anchor="w", pady=(8, 2))
        frm = tk.Frame(parent, bg="#2d2d2d", padx=8, pady=8)
        frm.pack(fill="x", pady=(0, 6))
        return frm


if __name__ == "__main__":
    app = App()
    app.mainloop()