"""
Bloc 6 — Interface Graphique Tkinter
Analyseur de Trafic Réseau Simulé
Visualisation réseau avec NetworkX + Matplotlib
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
import matplotlib.patches as mpatches

from network.graph import Graph
from network.packet import Packet
from simulation.queue_manager import QueueManager

# ─── Palette ──────────────────────────────────────────────────────────────────
BG_DARK   = "#0d1117"
BG_CARD   = "#161b22"
BG_INPUT  = "#21262d"
ACCENT    = "#00d2ff"
ACCENT2   = "#3a7bd5"
GREEN     = "#3fb950"
RED       = "#f85149"
YELLOW    = "#d29922"
TEXT_MAIN = "#e6edf3"
TEXT_DIM  = "#8b949e"
BORDER    = "#30363d"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Analyseur de Trafic Réseau — Bloc 6")
        self.geometry("1280x750")
        self.minsize(1000, 650)
        self.configure(bg=BG_DARK)

        # Modèle
        self.graph              = Graph()
        self.nx_graph           = nx.Graph()
        self.queue              = QueueManager(capacity=5)
        self.packet_counter     = 1
        self.simulation_running = False
        self._counter_nodes     = 0
        self._counter_links     = 0
        self._counter_sent      = 0
        self._active_packet     = None

        self._build_ui()


    # Construction UI
    
    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg=BG_CARD, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="◈  ANALYSEUR DE TRAFIC RÉSEAU",
                 font=("Courier", 13, "bold"), fg=ACCENT, bg=BG_CARD
                 ).pack(side="left", padx=20, pady=12)
        self.status_lbl = tk.Label(header, text="● EN ATTENTE",
                                   font=("Courier", 10), fg=YELLOW, bg=BG_CARD)
        self.status_lbl.pack(side="right", padx=20)

        # Corps 3 colonnes
        body = tk.Frame(self, bg=BG_DARK)
        body.pack(fill="both", expand=True, padx=10, pady=8)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.columnconfigure(2, weight=3)
        body.rowconfigure(0, weight=1)

        left = tk.Frame(body, bg=BG_DARK)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self._build_network_panel(left)

        mid = tk.Frame(body, bg=BG_DARK)
        mid.grid(row=0, column=1, sticky="nsew", padx=5)
        self._build_packet_panel(mid)

        right = tk.Frame(body, bg=BG_DARK)
        right.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
        self._build_right_panel(right)

        self._build_stats_bar()

    # ── Panneau gauche ────────────────────────────────────────────────────────
    def _build_network_panel(self, parent):
        self._card_title(parent, "RÉSEAU — NŒUDS")
        frm = self._card(parent)
        tk.Label(frm, text="Nom du nœud", font=("Courier", 9),
                 fg=TEXT_DIM, bg=BG_CARD).pack(anchor="w", padx=10, pady=(8, 0))
        self.node_entry = self._entry(frm)
        self.node_entry.pack(fill="x", padx=10, pady=4)
        self._btn(frm, "＋  Ajouter nœud", self._add_node, ACCENT
                  ).pack(fill="x", padx=10, pady=(0, 10))

        self._card_title(parent, "CONNEXION")
        frm2 = self._card(parent)
        for lbl, attr in [("Nœud A", "conn_a"), ("Nœud B", "conn_b")]:
            tk.Label(frm2, text=lbl, font=("Courier", 9),
                     fg=TEXT_DIM, bg=BG_CARD).pack(anchor="w", padx=10, pady=(6, 0))
            e = self._entry(frm2)
            e.pack(fill="x", padx=10, pady=2)
            setattr(self, attr, e)
        self._btn(frm2, "⟷  Connecter", self._add_connection, ACCENT2
                  ).pack(fill="x", padx=10, pady=(6, 10))

        self._card_title(parent, "TOPOLOGIE")
        frm3 = self._card(parent, expand=True)
        self.topo_text = scrolledtext.ScrolledText(
            frm3, font=("Courier", 9), bg=BG_INPUT, fg=TEXT_MAIN,
            insertbackground=ACCENT, relief="flat", bd=0, wrap="word")
        self.topo_text.pack(fill="both", expand=True, padx=8, pady=8)
        self.topo_text.config(state="disabled")

    # ── Panneau centre ────────────────────────────────────────────────────────
    def _build_packet_panel(self, parent):
        self._card_title(parent, "CRÉATION DE PAQUETS")
        frm = self._card(parent)
        for lbl, attr, default in [
            ("Source",      "pkt_src",  ""),
            ("Destination", "pkt_dst",  ""),
            ("Taille (KB)", "pkt_size", "10"),
        ]:
            tk.Label(frm, text=lbl, font=("Courier", 9),
                     fg=TEXT_DIM, bg=BG_CARD).pack(anchor="w", padx=10, pady=(6, 0))
            e = self._entry(frm, default)
            e.pack(fill="x", padx=10, pady=2)
            setattr(self, attr, e)
        self._btn(frm, "📦  Envoyer paquet", self._add_packet, GREEN
                  ).pack(fill="x", padx=10, pady=(8, 10))

        self._card_title(parent, "FILE D'ATTENTE")
        frm2 = self._card(parent)
        cap_frm = tk.Frame(frm2, bg=BG_CARD)
        cap_frm.pack(fill="x", padx=10, pady=(8, 4))
        tk.Label(cap_frm, text="Capacité :", font=("Courier", 9),
                 fg=TEXT_DIM, bg=BG_CARD).pack(side="left")
        self.cap_var = tk.IntVar(value=5)
        tk.Spinbox(cap_frm, from_=1, to=20, textvariable=self.cap_var,
                   width=4, font=("Courier", 9), bg=BG_INPUT, fg=ACCENT,
                   relief="flat", bd=0, command=self._update_capacity
                   ).pack(side="left", padx=6)
        self.queue_bar_frame = tk.Frame(frm2, bg=BG_CARD)
        self.queue_bar_frame.pack(fill="x", padx=10, pady=(2, 10))
        self._update_queue_bar()

        self._card_title(parent, "SIMULATION")
        frm3 = self._card(parent)
        self._btn(frm3, "▶  Lancer simulation", self._run_simulation, GREEN
                  ).pack(fill="x", padx=10, pady=(10, 4))
        self._btn(frm3, "⟳  Réinitialiser", self._reset, RED
                  ).pack(fill="x", padx=10, pady=(0, 10))

        self._card_title(parent, "ANALYSE RÉSEAU")
        frm4 = self._card(parent)
        self._btn(frm4, "🔍  Goulots d'étranglement", self._show_bottlenecks, YELLOW
                  ).pack(fill="x", padx=10, pady=(8, 4))
        self._btn(frm4, "📈  Plus court chemin", self._show_shortest_path, ACCENT2
                  ).pack(fill="x", padx=10, pady=(0, 10))

    # ── Panneau droit : graphe + log ──────────────────────────────────────────
    def _build_right_panel(self, parent):
        parent.rowconfigure(0, weight=3)
        parent.rowconfigure(1, weight=2)
        parent.columnconfigure(0, weight=1)

        # Zone graphe
        gf = tk.Frame(parent, bg=BG_DARK)
        gf.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        self._card_title(gf, "VISUALISATION DU RÉSEAU")
        card = self._card(gf, expand=True)
        self.fig, self.ax = plt.subplots(figsize=(6, 3.5))
        self.fig.patch.set_facecolor("#161b22")
        self.ax.set_facecolor("#0d1117")
        self.ax.axis("off")
        self.canvas = FigureCanvasTkAgg(self.fig, master=card)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
        self._draw_graph()

        # Zone log
        lf = tk.Frame(parent, bg=BG_DARK)
        lf.grid(row=1, column=0, sticky="nsew")
        self._card_title(lf, "JOURNAL D'ÉVÉNEMENTS")
        lc = self._card(lf, expand=True)
        self.log_area = scrolledtext.ScrolledText(
            lc, font=("Courier", 9), bg=BG_INPUT, fg=TEXT_MAIN,
            insertbackground=ACCENT, relief="flat", bd=0, wrap="word", height=8)
        self.log_area.pack(fill="both", expand=True, padx=8, pady=(8, 4))
        self.log_area.config(state="disabled")
        self.log_area.tag_config("INFO",  foreground=ACCENT)
        self.log_area.tag_config("OK",    foreground=GREEN)
        self.log_area.tag_config("WARN",  foreground=YELLOW)
        self.log_area.tag_config("ERROR", foreground=RED)
        self._btn(lc, "🗑  Effacer log", self._clear_log, TEXT_DIM
                  ).pack(fill="x", padx=8, pady=(0, 6))

        self._log("Système initialisé.", "INFO")
        self._log("Ajoutez des nœuds, connectez-les puis envoyez des paquets.", "INFO")

    # ── Stats bar ─────────────────────────────────────────────────────────────
    def _build_stats_bar(self):
        bar = tk.Frame(self, bg=BG_CARD, height=36)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)
        self.stat_nodes = self._stat_lbl(bar, "Nœuds : 0")
        self.stat_links = self._stat_lbl(bar, "Liens : 0")
        self.stat_sent  = self._stat_lbl(bar, "Envoyés : 0")
        self.stat_lost  = self._stat_lbl(bar, "Perdus : 0")
        self.stat_queue = self._stat_lbl(bar, "File : 0/5")

    def _stat_lbl(self, parent, text):
        l = tk.Label(parent, text=text, font=("Courier", 9),
                     fg=TEXT_DIM, bg=BG_CARD)
        l.pack(side="left", padx=16, pady=8)
        return l

    # ══════════════════════════════════════════════════════════════════════════
    # Actions
    # ══════════════════════════════════════════════════════════════════════════
    def _add_node(self):
        name = self.node_entry.get().strip().upper()
        if not name:
            messagebox.showwarning("Erreur", "Entrez un nom de nœud.")
            return
        if name in self.graph.nodes:
            self._log(f"Nœud '{name}' existe déjà.", "WARN")
            return
        self.graph.add_node(name)
        self.nx_graph.add_node(name)
        self._counter_nodes += 1
        self.node_entry.delete(0, "end")
        self._log(f"Nœud '{name}' ajouté au réseau.", "OK")
        self._refresh_topo()
        self._refresh_stats()
        self._draw_graph()

    def _add_connection(self):
        a = self.conn_a.get().strip().upper()
        b = self.conn_b.get().strip().upper()
        if not a or not b:
            messagebox.showwarning("Erreur", "Entrez les deux nœuds.")
            return
        if a not in self.graph.nodes or b not in self.graph.nodes:
            self._log(f"Nœud inexistant : '{a}' ou '{b}'.", "ERROR")
            return
        self.graph.add_connection(a, b)
        self.nx_graph.add_edge(a, b)
        self._counter_links += 1
        self.conn_a.delete(0, "end")
        self.conn_b.delete(0, "end")
        self._log(f"Lien {a} ⟷ {b} créé.", "OK")
        self._refresh_topo()
        self._refresh_stats()
        self._draw_graph()

    def _add_packet(self):
        src  = self.pkt_src.get().strip().upper()
        dst  = self.pkt_dst.get().strip().upper()
        try:
            size = int(self.pkt_size.get().strip())
        except ValueError:
            messagebox.showwarning("Erreur", "La taille doit être un entier.")
            return
        if not src or not dst:
            messagebox.showwarning("Erreur", "Entrez source et destination.")
            return
        p = Packet(self.packet_counter, src, dst, size)
        self.packet_counter += 1
        before = self.queue.dropped_packets
        self.queue.add_packet(p)
        if self.queue.dropped_packets > before:
            self._log(f"⚠ Paquet #{p.id_packet} rejeté — file pleine !", "ERROR")
        else:
            self._counter_sent += 1
            self._log(f"Paquet #{p.id_packet} : {src}→{dst} ({size} KB) en file.", "OK")
        self._refresh_stats()
        self._update_queue_bar()

    def _update_capacity(self):
        self.queue.capacity = self.cap_var.get()
        self._log(f"Capacité mise à jour : {self.queue.capacity}", "INFO")
        self._refresh_stats()
        self._update_queue_bar()

    def _run_simulation(self):
        if self.simulation_running:
            self._log("Simulation déjà en cours.", "WARN")
            return
        if self.queue.is_empty():
            self._log("File vide — ajoutez des paquets.", "WARN")
            return
        self.simulation_running = True
        self.status_lbl.config(text="● SIMULATION", fg=GREEN)
        self._log("─── Simulation démarrée ───", "INFO")
        threading.Thread(target=self._simulate_thread, daemon=True).start()

    def _simulate_thread(self):
        while not self.queue.is_empty():
            p = self.queue.process_packet()
            if p:
                self._active_packet = p
                self.after(0, lambda pkt=p: self._log(
                    f"✓ Traité : #{pkt.id_packet} {pkt.source}→{pkt.destination} ({pkt.size} KB)", "OK"))
                self.after(0, self._draw_graph)
            self.after(0, self._update_queue_bar)
            self.after(0, self._refresh_stats)
            time.sleep(0.9)

        self._active_packet = None
        stats = self.queue.stats()
        self.after(0, lambda: self._log(
            f"─── Terminé | Perdus : {stats['perdus']} ───", "INFO"))
        self.after(0, lambda: self.status_lbl.config(text="● TERMINÉ", fg=ACCENT))
        self.after(0, self._draw_graph)
        self.simulation_running = False

    def _show_bottlenecks(self):
        if len(self.nx_graph.nodes) == 0:
            self._log("Réseau vide.", "WARN")
            return
        centrality = nx.degree_centrality(self.nx_graph)
        sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        self._log("── Analyse goulots (centralité de degré) ──", "INFO")
        for node, score in sorted_nodes:
            tag = "ERROR" if score > 0.5 else "WARN" if score > 0.25 else "OK"
            self._log(f"  {node} : {score:.2f}  {'⚠ GOULOT' if score > 0.5 else ''}", tag)
        self._draw_graph(highlight_centrality=centrality)

    def _show_shortest_path(self):
        src = self.pkt_src.get().strip().upper()
        dst = self.pkt_dst.get().strip().upper()
        if not src or not dst:
            self._log("Entrez source et destination.", "WARN")
            return
        if src not in self.nx_graph or dst not in self.nx_graph:
            self._log(f"'{src}' ou '{dst}' absent du réseau.", "ERROR")
            return
        try:
            path = nx.shortest_path(self.nx_graph, source=src, target=dst)
            self._log(f"Chemin {src}→{dst} : {' → '.join(path)}", "OK")
            self._draw_graph(highlight_path=path)
        except nx.NetworkXNoPath:
            self._log(f"Aucun chemin entre {src} et {dst}.", "ERROR")

    def _reset(self):
        if messagebox.askyesno("Réinitialiser", "Remettre à zéro tout le réseau ?"):
            self.graph = Graph()
            self.nx_graph = nx.Graph()
            self.queue = QueueManager(capacity=self.cap_var.get())
            self.packet_counter = 1
            self._counter_nodes = self._counter_links = self._counter_sent = 0
            self.simulation_running = False
            self._active_packet = None
            self.status_lbl.config(text="● EN ATTENTE", fg=YELLOW)
            self._refresh_topo()
            self._refresh_stats()
            self._update_queue_bar()
            self._draw_graph()
            self._log("═══ Réseau réinitialisé. ═══", "WARN")

    # ══════════════════════════════════════════════════════════════════════════
    # Dessin NetworkX
    # ══════════════════════════════════════════════════════════════════════════
    def _draw_graph(self, highlight_path=None, highlight_centrality=None):
        self.ax.clear()
        self.ax.set_facecolor("#0d1117")
        self.ax.axis("off")

        if len(self.nx_graph.nodes) == 0:
            self.ax.text(0.5, 0.5,
                         "Ajoutez des nœuds pour visualiser le réseau",
                         ha="center", va="center", color=TEXT_DIM,
                         fontsize=10, fontfamily="monospace",
                         transform=self.ax.transAxes)
            self.canvas.draw()
            return

        pos = nx.spring_layout(self.nx_graph, seed=42)

        # Couleurs nœuds
        node_colors = []
        for n in self.nx_graph.nodes:
            if self._active_packet and n in (
                    self._active_packet.source, self._active_packet.destination):
                node_colors.append("#f85149")
            elif highlight_path and n in highlight_path:
                node_colors.append("#3a7bd5")
            elif highlight_centrality and highlight_centrality.get(n, 0) > 0.5:
                node_colors.append("#d29922")
            else:
                node_colors.append("#00d2ff")

        # Couleurs liens
        path_edges = set()
        if highlight_path:
            path_edges = set(zip(highlight_path, highlight_path[1:]))
        edge_colors = [
            "#3a7bd5" if (e in path_edges or (e[1], e[0]) in path_edges)
            else "#30363d"
            for e in self.nx_graph.edges
        ]

        nx.draw_networkx_edges(self.nx_graph, pos, ax=self.ax,
                               edge_color=edge_colors, width=2, alpha=0.8)
        nx.draw_networkx_nodes(self.nx_graph, pos, ax=self.ax,
                               node_color=node_colors, node_size=600, alpha=0.95)
        nx.draw_networkx_labels(self.nx_graph, pos, ax=self.ax,
                                font_color="#0d1117", font_size=9,
                                font_weight="bold", font_family="monospace")

        legend = [
            mpatches.Patch(color="#00d2ff", label="Nœud normal"),
            mpatches.Patch(color="#f85149", label="Transit actif"),
            mpatches.Patch(color="#3a7bd5", label="Chemin court"),
            mpatches.Patch(color="#d29922", label="Goulot"),
        ]
        self.ax.legend(handles=legend, loc="lower right",
                       facecolor="#161b22", edgecolor="#30363d",
                       labelcolor="#e6edf3", fontsize=7)
        self.fig.tight_layout()
        self.canvas.draw()

    # ══════════════════════════════════════════════════════════════════════════
    # Helpers UI
    # ══════════════════════════════════════════════════════════════════════════
    def _log(self, message, level="INFO"):
        self.log_area.config(state="normal")
        ts = time.strftime("%H:%M:%S")
        self.log_area.insert("end", f"[{ts}] ", "INFO")
        self.log_area.insert("end", f"{message}\n", level)
        self.log_area.see("end")
        self.log_area.config(state="disabled")

    def _clear_log(self):
        self.log_area.config(state="normal")
        self.log_area.delete("1.0", "end")
        self.log_area.config(state="disabled")

    def _refresh_topo(self):
        self.topo_text.config(state="normal")
        self.topo_text.delete("1.0", "end")
        if not self.graph.nodes:
            self.topo_text.insert("end", "  (aucun nœud)\n")
        for name, node in self.graph.nodes.items():
            conns = [n.name for n in node.connections]
            self.topo_text.insert(
                "end", f"  {name}  →  {', '.join(conns) if conns else '—'}\n")
        self.topo_text.config(state="disabled")

    def _refresh_stats(self):
        stats = self.queue.stats()
        cap   = self.queue.capacity
        self.stat_nodes.config(text=f"Nœuds : {self._counter_nodes}")
        self.stat_links.config(text=f"Liens : {self._counter_links}")
        self.stat_sent.config( text=f"Envoyés : {self._counter_sent}")
        self.stat_lost.config( text=f"Perdus : {stats['perdus']}",
                               fg=RED if stats['perdus'] > 0 else TEXT_DIM)
        self.stat_queue.config(text=f"File : {stats['restants']}/{cap}")

    def _update_queue_bar(self):
        for w in self.queue_bar_frame.winfo_children():
            w.destroy()
        cap   = self.queue.capacity
        used  = len(self.queue.queue)
        ratio = used / cap if cap > 0 else 0
        color = GREEN if ratio < 0.6 else YELLOW if ratio < 0.9 else RED
        tk.Label(self.queue_bar_frame, text=f"{used}/{cap} paquets",
                 font=("Courier", 9), fg=TEXT_DIM, bg=BG_CARD).pack(anchor="w")
        bg = tk.Frame(self.queue_bar_frame, bg=BG_INPUT, height=10)
        bg.pack(fill="x", pady=2)
        bg.update_idletasks()
        w = bg.winfo_width()
        if w > 1:
            tk.Frame(bg, bg=color, height=10,
                     width=int(w * ratio)).place(x=0, y=0)

    def _card_title(self, parent, text):
        tk.Label(parent, text=text, font=("Courier", 8, "bold"),
                 fg=ACCENT, bg=BG_DARK).pack(anchor="w", pady=(8, 2))

    def _card(self, parent, expand=False):
        f = tk.Frame(parent, bg=BG_CARD,
                     highlightbackground=BORDER, highlightthickness=1)
        f.pack(fill="both", expand=expand, pady=(0, 4))
        return f

    def _entry(self, parent, default=""):
        e = tk.Entry(parent, font=("Courier", 10), bg=BG_INPUT, fg=TEXT_MAIN,
                     insertbackground=ACCENT, relief="flat", bd=4)
        if default:
            e.insert(0, default)
        return e

    def _btn(self, parent, text, cmd, color=ACCENT):
        return tk.Button(parent, text=text, command=cmd,
                         font=("Courier", 9, "bold"),
                         fg=BG_DARK, bg=color,
                         activebackground=TEXT_MAIN, activeforeground=BG_DARK,
                         relief="flat", bd=0, cursor="hand2", pady=6)


if __name__ == "__main__":
    app = App()
    app.mainloop()
