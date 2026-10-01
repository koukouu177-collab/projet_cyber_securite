#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JEUXPRO
Jeu éducatif avancé des protocoles Internet.
Théorie + pratique + simulations visuelles.
Créé par les Hackers Tchadiens.
Tout en une seule page avec Pygame.
"""

import os
import sys
import json
import random
import math
import datetime
from pathlib import Path

# --- Imports ---
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Pygame non installe. Installez-le avec : pip install pygame")
    sys.exit(1)

# --- Configuration ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
TITLE = "JEUXPRO — Protocoles Internet"
SAVE_FILE = "jeuxpro_progress.json"

# Couleurs cyberpunk/hacker
BLACK = (10, 10, 15)
DARK_BG = (15, 20, 30)
PANEL_BG = (25, 35, 55)
GREEN = (0, 255, 65)
DARK_GREEN = (0, 180, 40)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 220, 0)
ORANGE = (255, 140, 0)
RED = (255, 50, 50)
WHITE = (240, 240, 240)
GRAY = (150, 150, 150)

# --- Données pédagogiques : protocoles ---
PROTOCOLS = {
    "HTTP": {
        "title": "HTTP / HTTPS",
        "description": "Protocole de transfert hypertexte. HTTPS ajoute le chiffrement TLS.",
        "ports": "80 (HTTP), 443 (HTTPS)",
        "key_points": [
            "Client envoie une requête (GET, POST, PUT, DELETE)",
            "Serveur répond avec un code de statut (200, 404, 500)",
            "HTTPS chiffre les données avec TLS/SSL",
            "Les headers transportent les métadonnées"
        ]
    },
    "TCP": {
        "title": "TCP",
        "description": "Transmission Control Protocol — connexion fiable et ordonnée.",
        "ports": "Dépend du service (ex: 80, 443, 22)",
        "key_points": [
            "Handshake en 3 étapes : SYN, SYN-ACK, ACK",
            "Garantit la livraison des paquets",
            "Contrôle de flux et de congestion",
            "Utilisé pour web, email, SSH, FTP"
        ]
    },
    "UDP": {
        "title": "UDP",
        "description": "User Datagram Protocol — rapide mais non fiable.",
        "ports": "Dépend du service (ex: 53 DNS, 3478 STUN)",
        "key_points": [
            "Pas de connexion établie",
            "Plus rapide que TCP",
            "Utilisé pour streaming, jeux en ligne, DNS",
            "Ne garantit pas l'ordre ni la livraison"
        ]
    },
    "IP": {
        "title": "IP",
        "description": "Internet Protocol — adressage et routage des paquets.",
        "ports": "Couche 3, pas de ports",
        "key_points": [
            "IPv4 : 32 bits (ex: 192.168.1.1)",
            "IPv6 : 128 bits (ex: fe80::1)",
            "Chaque paquet a une source et une destination",
            "Les routeurs acheminent les paquets"
        ]
    },
    "ICMP": {
        "title": "ICMP",
        "description": "Internet Control Message Protocol — messages de contrôle et d'erreur.",
        "ports": "Aucun (couche 3)",
        "key_points": [
            "Utilisé par la commande ping",
            "Signale les erreurs de routage",
            "Types : Echo Request (8), Echo Reply (0), Destination Unreachable (3)",
            "Traceroute utilise ICMP ou UDP"
        ]
    },
    "DNS": {
        "title": "DNS",
        "description": "Domain Name System — traduit les noms de domaine en adresses IP.",
        "ports": "53 (UDP et TCP)",
        "key_points": [
            "Résolution de www.exemple.com → 93.184.216.34",
            "Hiérarchie : racine, TLD, domaine, sous-domaine",
            "Types d'enregistrements : A, AAAA, CNAME, MX, TXT",
            "Cache DNS accélère les requêtes"
        ]
    },
    "DHCP": {
        "title": "DHCP",
        "description": "Dynamic Host Configuration Protocol — attribution automatique d'IP.",
        "ports": "67 (serveur), 68 (client)",
        "key_points": [
            "DORA : Discover, Offer, Request, Acknowledge",
            "Attribue IP, masque, passerelle, DNS",
            "Bail (lease time) limité dans le temps",
            "Évite les conflits d'adresses IP"
        ]
    },
    "FTP": {
        "title": "FTP / SFTP",
        "description": "File Transfer Protocol — transfert de fichiers.",
        "ports": "21 (FTP), 22 (SFTP/SSH)",
        "key_points": [
            "FTP envoie les données en clair",
            "SFTP sécurise via SSH",
            "Deux canaux : commandes (21) et données (20)",
            "Modes actif et passif"
        ]
    },
    "SSH": {
        "title": "SSH",
        "description": "Secure Shell — connexion sécurisée à distance.",
        "ports": "22",
        "key_points": [
            "Chiffrement asymétrique pour l'authentification",
            "Tunnel sécurisé pour les commandes",
            "Remplace Telnet non sécurisé",
            "Utilise des clés publiques/privées"
        ]
    },
    "TLS": {
        "title": "TLS / SSL",
        "description": "Transport Layer Security — chiffrement des communications.",
        "ports": "443 (HTTPS), 993 (IMAPS), etc.",
        "key_points": [
            "Handshake TLS établit une clé de session",
            "Certificats X.509 validés par une CA",
            "Chiffrement symétrique pour les données",
            "SSL est l'ancêtre obsolète de TLS 1.2/1.3"
        ]
    }
}

# --- Banque de questions ---
QUESTIONS = [
    {
        "protocol": "ICMP",
        "question": "Que signifie ICMP ?",
        "choices": [
            "Internet Control Message Protocol",
            "Internal Communication Management Protocol",
            "Internet Connection Message Process",
            "Intranet Control Monitoring Protocol"
        ],
        "answer": 0,
        "explanation": "ICMP = Internet Control Message Protocol. Il sert aux messages de contrôle comme ping et aux erreurs de routage."
    },
    {
        "protocol": "TCP",
        "question": "Quel est le handshake TCP correct ?",
        "choices": [
            "SYN, SYN-ACK, ACK",
            "ACK, SYN, FIN",
            "SYN, ACK, RST",
            "HELLO, REPLY, DATA"
        ],
        "answer": 0,
        "explanation": "Le handshake TCP en 3 étapes est SYN (synchronisation), SYN-ACK (synchronisation-acquittement), ACK (acquittement)."
    },
    {
        "protocol": "UDP",
        "question": "Pourquoi UDP est-il plus rapide que TCP ?",
        "choices": [
            "Il n'établit pas de connexion et ne garantit pas la livraison",
            "Il utilise un algorithme de compression",
            "Il fonctionne sur la couche 2",
            "Il divise toujours les paquets en deux"
        ],
        "answer": 0,
        "explanation": "UDP est sans connexion : pas de handshake, pas de retransmission, donc plus rapide mais moins fiable."
    },
    {
        "protocol": "IP",
        "question": "Quelle est la taille d'une adresse IPv4 ?",
        "choices": [
            "32 bits",
            "64 bits",
            "128 bits",
            "16 bits"
        ],
        "answer": 0,
        "explanation": "IPv4 utilise 32 bits (4 octets). IPv6 utilise 128 bits."
    },
    {
        "protocol": "DNS",
        "question": "Quel port utilise principalement DNS ?",
        "choices": [
            "53",
            "80",
            "443",
            "22"
        ],
        "answer": 0,
        "explanation": "DNS utilise le port 53 en UDP pour les requêtes et parfois TCP pour les transferts de zone."
    },
    {
        "protocol": "DHCP",
        "question": "Quelle séquence décrit le processus DHCP ?",
        "choices": [
            "Discover, Offer, Request, Acknowledge",
            "Ask, Give, Take, Confirm",
            "Ping, Reply, Lease, Renew",
            "Search, Find, Bind, Release"
        ],
        "answer": 0,
        "explanation": "DORA : Discover (client), Offer (serveur), Request (client), Acknowledge (serveur)."
    },
    {
        "protocol": "HTTP",
        "question": "Quel code HTTP signifie 'Non trouvé' ?",
        "choices": [
            "404",
            "200",
            "500",
            "301"
        ],
        "answer": 0,
        "explanation": "404 Not Found indique que la ressource demandée n'existe pas sur le serveur."
    },
    {
        "protocol": "SSH",
        "question": "Sur quel port SSH fonctionne-t-il par défaut ?",
        "choices": [
            "22",
            "23",
            "21",
            "80"
        ],
        "answer": 0,
        "explanation": "SSH utilise le port 22 par défaut pour les connexions sécurisées à distance."
    },
    {
        "protocol": "TLS",
        "question": "Que garantit TLS dans HTTPS ?",
        "choices": [
            "Confidentialité, intégrité et authentification",
            "Uniquement la vitesse de téléchargement",
            "La compression des images",
            "Le routage des paquets"
        ],
        "answer": 0,
        "explanation": "TLS chiffre les données (confidentialité), détecte les modifications (intégrité) et authentifie le serveur."
    },
    {
        "protocol": "FTP",
        "question": "Quelle est la différence principale entre FTP et SFTP ?",
        "choices": [
            "SFTP chiffre les transferts via SSH",
            "FTP est plus rapide que SFTP",
            "SFTP n'utilise pas de ports",
            "FTP fonctionne uniquement sur IPv6"
        ],
        "answer": 0,
        "explanation": "SFTP (SSH File Transfer Protocol) chiffre les commandes et données via SSH, contrairement à FTP en clair."
    },
    {
        "protocol": "ICMP",
        "question": "Quel type ICMP est envoyé par la commande ping ?",
        "choices": [
            "Echo Request (type 8)",
            "Echo Reply (type 0)",
            "Destination Unreachable (type 3)",
            "Time Exceeded (type 11)"
        ],
        "answer": 0,
        "explanation": "Ping envoie des Echo Request (type 8) et attend des Echo Reply (type 0)."
    },
    {
        "protocol": "IP",
        "question": "Quel protocole achemine les paquets entre réseaux ?",
        "choices": [
            "IP",
            "TCP",
            "HTTP",
            "DNS"
        ],
        "answer": 0,
        "explanation": "IP (Internet Protocol) gère l'adressage et le routage des paquets entre réseaux."
    },
    {
        "protocol": "TCP",
        "question": "Quel mécanisme TCP garantit que les paquets arrivent en ordre ?",
        "choices": [
            "Numéros de séquence et acquittements",
            "Broadcast",
            "Multicast",
            "TTL"
        ],
        "answer": 0,
        "explanation": "TCP utilise des numéros de séquence et des ACK pour ordonner et retransmettre les paquets perdus."
    },
    {
        "protocol": "DNS",
        "question": "Quel enregistrement DNS associe un nom à une adresse IPv4 ?",
        "choices": [
            "A",
            "AAAA",
            "CNAME",
            "MX"
        ],
        "answer": 0,
        "explanation": "L'enregistrement A associe un nom de domaine à une adresse IPv4. AAAA pour IPv6."
    },
    {
        "protocol": "HTTP",
        "question": "Quelle méthode HTTP est utilisée pour envoyer des données de formulaire ?",
        "choices": [
            "POST",
            "GET",
            "DELETE",
            "HEAD"
        ],
        "answer": 0,
        "explanation": "POST envoie des données au serveur, contrairement à GET qui les demande."
    }
]

# --- Initialisation Pygame ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# Polices
try:
    FONT_TITLE = pygame.font.Font(None, 64)
    FONT_LARGE = pygame.font.Font(None, 48)
    FONT_NORMAL = pygame.font.Font(None, 32)
    FONT_SMALL = pygame.font.Font(None, 24)
except Exception:
    FONT_TITLE = pygame.font.SysFont("arial", 64)
    FONT_LARGE = pygame.font.SysFont("arial", 48)
    FONT_NORMAL = pygame.font.SysFont("arial", 32)
    FONT_SMALL = pygame.font.SysFont("arial", 24)


# --- Utilitaires ---

def load_progress():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"score": 0, "level": 1, "unlocked": ["HTTP"], "completed": []}


def save_progress(progress):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)


def draw_text(surface, text, font, color, x, y, center=True, max_width=None):
    if max_width:
        words = text.split(" ")
        lines = []
        current = ""
        for word in words:
            test = current + word + " "
            if font.size(test)[0] <= max_width:
                current = test
            else:
                lines.append(current.strip())
                current = word + " "
        if current:
            lines.append(current.strip())
        for i, line in enumerate(lines):
            render = font.render(line, True, color)
            rect = render.get_rect()
            if center:
                rect.center = (x, y + i * (font.get_height() + 5))
            else:
                rect.topleft = (x, y + i * (font.get_height() + 5))
            surface.blit(render, rect)
    else:
        render = font.render(text, True, color)
        rect = render.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        surface.blit(render, rect)


def draw_button(surface, text, x, y, w, h, color, text_color=WHITE, hover=False):
    rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
    border = 3 if hover else 2
    pygame.draw.rect(surface, color, rect, border_radius=8)
    pygame.draw.rect(surface, CYAN if hover else GRAY, rect, border, border_radius=8)
    draw_text(surface, text, FONT_NORMAL, text_color, x, y)
    return rect


def draw_panel(surface, x, y, w, h, alpha=180):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((*PANEL_BG, alpha))
    surface.blit(s, (x, y))
    pygame.draw.rect(surface, CYAN, (x, y, w, h), 2, border_radius=10)


def matrix_rain_effect():
    """Génère un effet de pluie de code en arrière-plan."""
    chars = "01ABCDEF"
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for _ in range(80):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        char = random.choice(chars)
        color = (*DARK_GREEN, random.randint(30, 100))
        render = FONT_SMALL.render(char, True, color)
        surface.blit(render, (x, y))
    return surface


# --- Scènes du jeu ---

class Game:
    def __init__(self):
        self.progress = load_progress()
        self.score = self.progress.get("score", 0)
        self.current_scene = "menu"
        self.current_protocol = None
        self.current_question = None
        self.questions_queue = []
        self.feedback = ""
        self.feedback_color = WHITE
        self.simulation_mode = None
        self.simulation_objects = []
        self.simulation_time = 0
        self.running = True

    def save(self):
        self.progress["score"] = self.score
        save_progress(self.progress)

    def run(self):
        while self.running:
            dt = clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save()
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.current_scene in ("protocol", "quiz", "simulation", "learn"):
                        self.current_scene = "menu"
                    elif self.current_scene == "menu":
                        self.save()
                        self.running = False
                elif event.key == pygame.K_SPACE:
                    if self.current_scene == "protocol":
                        self.start_quiz()
                    elif self.current_scene == "simulation":
                        self.current_scene = "menu"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click(event.pos)

    def handle_click(self, pos):
        if self.current_scene == "menu":
            buttons = self.get_menu_buttons()
            for label, rect, action in buttons:
                if rect.collidepoint(pos):
                    action()
        elif self.current_scene == "protocol":
            buttons = self.get_protocol_buttons()
            for label, rect, action in buttons:
                if rect.collidepoint(pos):
                    action()
        elif self.current_scene == "quiz":
            buttons = self.get_quiz_buttons()
            for idx, rect in buttons:
                if rect.collidepoint(pos):
                    self.check_answer(idx)
        elif self.current_scene == "simulation":
            buttons = self.get_simulation_buttons()
            for label, rect, action in buttons:
                if rect.collidepoint(pos):
                    action()
        elif self.current_scene == "learn":
            buttons = self.get_learn_buttons()
            for label, rect, action in buttons:
                if rect.collidepoint(pos):
                    action()
        elif self.current_scene == "final":
            buttons = self.get_final_buttons()
            for label, rect, action in buttons:
                if rect.collidepoint(pos):
                    action()

    def update(self, dt):
        if self.current_scene == "simulation":
            self.simulation_time += dt
            self.update_simulation(dt)

    def draw(self):
        screen.fill(BLACK)
        screen.blit(matrix_rain_effect(), (0, 0))

        if self.current_scene == "menu":
            self.draw_menu()
        elif self.current_scene == "protocol":
            self.draw_protocol_select()
        elif self.current_scene == "learn":
            self.draw_learn()
        elif self.current_scene == "quiz":
            self.draw_quiz()
        elif self.current_scene == "simulation":
            self.draw_simulation()
        elif self.current_scene == "final":
            self.draw_final()

        # HUD score
        draw_text(screen, f"Score: {self.score}", FONT_NORMAL, GREEN, SCREEN_WIDTH - 100, 30)
        pygame.display.flip()

    # --- Menu principal ---

    def draw_menu(self):
        draw_text(screen, "JEUXPRO", FONT_TITLE, GREEN, SCREEN_WIDTH // 2, 120)
        draw_text(screen, "Apprends les protocoles Internet en jouant", FONT_NORMAL, CYAN, SCREEN_WIDTH // 2, 190)
        draw_text(screen, "Créé par les Hackers Tchadiens", FONT_SMALL, MAGENTA, SCREEN_WIDTH // 2, 230)

        buttons = self.get_menu_buttons()
        mx, my = pygame.mouse.get_pos()
        for label, rect, action in buttons:
            hover = rect.collidepoint(mx, my)
            draw_button(screen, label, rect.centerx, rect.centery, rect.width, rect.height, PANEL_BG, WHITE, hover)

        draw_text(screen, "ESPACE = valider · ÉCHAP = quitter", FONT_SMALL, GRAY, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40)

    def get_menu_buttons(self):
        y_start = 320
        spacing = 80
        buttons = [
            ("Niveaux / Protocoles", None, self.show_protocol_select),
            ("Mode Apprentissage", None, self.show_learn),
            ("Examen Final", None, self.start_final_exam),
            ("Quitter", None, self.quit_game)
        ]
        result = []
        for i, (label, _, action) in enumerate(buttons):
            rect = pygame.Rect(0, 0, 400, 60)
            rect.center = (SCREEN_WIDTH // 2, y_start + i * spacing)
            result.append((label, rect, action))
        return result

    def show_protocol_select(self):
        self.current_scene = "protocol"

    def show_learn(self):
        self.current_scene = "learn"
        self.current_protocol = list(PROTOCOLS.keys())[0]

    def start_final_exam(self):
        self.questions_queue = random.sample(QUESTIONS, min(10, len(QUESTIONS)))
        self.current_scene = "quiz"
        self.feedback = ""
        self.load_next_question()

    def quit_game(self):
        self.save()
        self.running = False

    # --- Sélection des protocoles ---

    def draw_protocol_select(self):
        draw_text(screen, "CHOISIS UN PROTOCOLE", FONT_LARGE, CYAN, SCREEN_WIDTH // 2, 80)
        mx, my = pygame.mouse.get_pos()
        buttons = self.get_protocol_buttons()
        for label, rect, action in buttons:
            hover = rect.collidepoint(mx, my)
            color = GREEN if label in self.progress.get("unlocked", []) else GRAY
            draw_button(screen, label, rect.centerx, rect.centery, rect.width, rect.height, PANEL_BG, color, hover)
        draw_text(screen, "Clique sur un protocole débloqué pour jouer", FONT_SMALL, GRAY, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40)

    def get_protocol_buttons(self):
        keys = list(PROTOCOLS.keys())
        buttons = []
        cols = 2
        w, h = 280, 60
        start_x = SCREEN_WIDTH // 2 - (cols * w + 40) // 2 + w // 2
        start_y = 180
        for i, key in enumerate(keys):
            x = start_x + (i % cols) * (w + 40)
            y = start_y + (i // cols) * (h + 30)
            rect = pygame.Rect(0, 0, w, h)
            rect.center = (x, y)
            action = lambda k=key: self.select_protocol(k)
            buttons.append((key, rect, action))
        return buttons

    def select_protocol(self, protocol):
        if protocol not in self.progress.get("unlocked", []):
            self.feedback = "Protocole verrouillé !"
            self.feedback_color = RED
            return
        self.current_protocol = protocol
        protocol_questions = [q for q in QUESTIONS if q["protocol"] == protocol]
        if not protocol_questions:
            protocol_questions = QUESTIONS
        self.questions_queue = random.sample(protocol_questions, min(3, len(protocol_questions)))
        self.current_scene = "quiz"
        self.feedback = ""
        self.load_next_question()

    # --- Mode apprentissage ---

    def draw_learn(self):
        draw_text(screen, "MODE APPRENTISSAGE", FONT_LARGE, CYAN, SCREEN_WIDTH // 2, 60)
        if self.current_protocol:
            data = PROTOCOLS[self.current_protocol]
            draw_panel(screen, 50, 100, SCREEN_WIDTH - 100, 500)
            draw_text(screen, data["title"], FONT_LARGE, GREEN, SCREEN_WIDTH // 2, 140)
            draw_text(screen, data["description"], FONT_NORMAL, WHITE, SCREEN_WIDTH // 2, 200, max_width=SCREEN_WIDTH - 200)
            draw_text(screen, f"Ports : {data['ports']}", FONT_NORMAL, YELLOW, SCREEN_WIDTH // 2, 270)
            y = 330
            for point in data["key_points"]:
                draw_text(screen, f"• {point}", FONT_NORMAL, WHITE, 100, y, center=False, max_width=SCREEN_WIDTH - 200)
                y += 45

        mx, my = pygame.mouse.get_pos()
        buttons = self.get_learn_buttons()
        for label, rect, action in buttons:
            hover = rect.collidepoint(mx, my)
            draw_button(screen, label, rect.centerx, rect.centery, rect.width, rect.height, PANEL_BG, WHITE, hover)

    def get_learn_buttons(self):
        keys = list(PROTOCOLS.keys())
        buttons = []
        y = 630
        x_start = SCREEN_WIDTH // 2 - ((len(keys) * 100) // 2) + 50
        for i, key in enumerate(keys):
            rect = pygame.Rect(0, 0, 90, 50)
            rect.center = (x_start + i * 105, y)
            action = lambda k=key: self.set_learn_protocol(k)
            buttons.append((key, rect, action))
        # Bouton simulation
        sim_rect = pygame.Rect(0, 0, 200, 50)
        sim_rect.center = (SCREEN_WIDTH // 2, y + 70)
        buttons.append(("Simulation", sim_rect, self.start_simulation))
        return buttons

    def set_learn_protocol(self, protocol):
        self.current_protocol = protocol

    # --- Quiz ---

    def load_next_question(self):
        if not self.questions_queue:
            self.feedback = "Niveau terminé !"
            self.feedback_color = GREEN
            if self.current_protocol:
                self.unlock_next_protocol()
            self.current_scene = "protocol" if self.current_protocol else "final"
            return
        self.current_question = self.questions_queue.pop(0)
        self.feedback = ""

    def draw_quiz(self):
        if not self.current_question:
            return
        q = self.current_question
        draw_text(screen, f"Protocole : {q['protocol']}", FONT_NORMAL, CYAN, SCREEN_WIDTH // 2, 60)
        draw_panel(screen, 50, 100, SCREEN_WIDTH - 100, 180)
        draw_text(screen, q["question"], FONT_LARGE, WHITE, SCREEN_WIDTH // 2, 160, max_width=SCREEN_WIDTH - 200)

        mx, my = pygame.mouse.get_pos()
        buttons = self.get_quiz_buttons()
        for idx, rect in buttons:
            hover = rect.collidepoint(mx, my)
            label = q["choices"][idx]
            draw_button(screen, label, rect.centerx, rect.centery, rect.width, rect.height, PANEL_BG, WHITE, hover)

        if self.feedback:
            draw_text(screen, self.feedback, FONT_NORMAL, self.feedback_color, SCREEN_WIDTH // 2, 650, max_width=SCREEN_WIDTH - 200)
            if "Explication" in self.feedback:
                draw_text(screen, "Clique pour continuer...", FONT_SMALL, GRAY, SCREEN_WIDTH // 2, 720)

    def get_quiz_buttons(self):
        if not self.current_question:
            return []
        choices = self.current_question["choices"]
        buttons = []
        w, h = 500, 70
        start_y = 330
        for i in range(len(choices)):
            rect = pygame.Rect(0, 0, w, h)
            rect.center = (SCREEN_WIDTH // 2, start_y + i * 90)
            buttons.append((i, rect))
        return buttons

    def check_answer(self, idx):
        if not self.current_question:
            return
        correct = self.current_question["answer"]
        if idx == correct:
            self.score += 10
            self.feedback = f"✓ Correct ! {self.current_question['explanation']}"
            self.feedback_color = GREEN
        else:
            correct_text = self.current_question["choices"][correct]
            self.feedback = f"✗ Faux. La bonne réponse était : {correct_text}. {self.current_question['explanation']}"
            self.feedback_color = RED
        self.save()
        # Passage automatique après un court délai si clic sur feedback
        if self.feedback_color == GREEN:
            pygame.time.delay(1200)
            self.load_next_question()

    def unlock_next_protocol(self):
        keys = list(PROTOCOLS.keys())
        if self.current_protocol in keys:
            idx = keys.index(self.current_protocol)
            if idx + 1 < len(keys):
                next_protocol = keys[idx + 1]
                if next_protocol not in self.progress["unlocked"]:
                    self.progress["unlocked"].append(next_protocol)
                    self.feedback = f"Débloqué : {next_protocol} !"
                    self.feedback_color = GREEN
        if self.current_protocol not in self.progress["completed"]:
            self.progress["completed"].append(self.current_protocol)
        self.save()

    # --- Simulations visuelles ---

    def start_simulation(self):
        self.simulation_mode = self.current_protocol or "TCP"
        self.simulation_objects = []
        self.simulation_time = 0
        self.current_scene = "simulation"

    def update_simulation(self, dt):
        self.simulation_objects = []
        t = self.simulation_time
        mode = self.simulation_mode

        if mode == "TCP":
            # SYN, SYN-ACK, ACK se déplacent
            phases = ["SYN", "SYN-ACK", "ACK"]
            for i, phase in enumerate(phases):
                progress = ((t * 0.5) - i * 1.2) % 3.0
                x = 150 + progress * 300
                y = 250 + (i % 2) * 100
                self.simulation_objects.append(("packet", phase, x, y, GREEN))
        elif mode == "ICMP":
            # Ping aller-retour
            progress = (t * 0.8) % 2.0
            direction = 1 if progress < 1.0 else -1
            x = 150 + (progress if progress < 1.0 else 2.0 - progress) * 700
            self.simulation_objects.append(("packet", "ICMP Echo", x, 250, CYAN))
        elif mode == "DNS":
            # Requête vers serveur DNS
            progress = (t * 0.6) % 2.0
            x = 150 + (progress if progress < 1.0 else 2.0 - progress) * 700
            label = "Requête" if progress < 1.0 else "Réponse IP"
            self.simulation_objects.append(("packet", label, x, 250, MAGENTA))
        elif mode == "DHCP":
            steps = ["DISCOVER", "OFFER", "REQUEST", "ACK"]
            idx = int((t * 0.5) % 4)
            self.simulation_objects.append(("text", steps[idx], SCREEN_WIDTH // 2, 300, YELLOW))
        else:
            # Simulation générique : paquets
            for i in range(5):
                x = (150 + i * 180 + t * 50) % (SCREEN_WIDTH - 200)
                y = 250 + math.sin(t + i) * 50
                self.simulation_objects.append(("packet", "DATA", x, y, ORANGE))

    def draw_simulation(self):
        draw_text(screen, f"SIMULATION : {self.simulation_mode}", FONT_LARGE, CYAN, SCREEN_WIDTH // 2, 60)

        # Dessine client et serveur
        client_rect = pygame.Rect(50, 200, 120, 120)
        server_rect = pygame.Rect(SCREEN_WIDTH - 170, 200, 120, 120)
        pygame.draw.rect(screen, GREEN, client_rect, border_radius=10)
        pygame.draw.rect(screen, GREEN, server_rect, border_radius=10)
        draw_text(screen, "CLIENT", FONT_NORMAL, BLACK, client_rect.centerx, client_rect.centery)
        draw_text(screen, "SERVEUR", FONT_NORMAL, BLACK, server_rect.centerx, server_rect.centery)
        pygame.draw.line(screen, GRAY, (170, 260), (SCREEN_WIDTH - 170, 260), 2)

        for obj in self.simulation_objects:
            kind, label, x, y, color = obj
            if kind == "packet":
                pygame.draw.circle(screen, color, (int(x), int(y)), 20)
                draw_text(screen, label, FONT_SMALL, BLACK, int(x), int(y))
            elif kind == "text":
                draw_text(screen, label, FONT_LARGE, color, int(x), int(y))

        mx, my = pygame.mouse.get_pos()
        buttons = self.get_simulation_buttons()
        for label, rect, action in buttons:
            hover = rect.collidepoint(mx, my)
            draw_button(screen, label, rect.centerx, rect.centery, rect.width, rect.height, PANEL_BG, WHITE, hover)

        draw_text(screen, "Regarde l'échange de paquets en temps réel", FONT_SMALL, GRAY, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)

    def get_simulation_buttons(self):
        buttons = []
        keys = list(PROTOCOLS.keys())
        x_start = SCREEN_WIDTH // 2 - ((len(keys) * 100) // 2) + 50
        for i, key in enumerate(keys):
            rect = pygame.Rect(0, 0, 90, 40)
            rect.center = (x_start + i * 105, 500)
            action = lambda k=key: self.set_simulation(k)
            buttons.append((key, rect, action))
        back_rect = pygame.Rect(0, 0, 200, 50)
        back_rect.center = (SCREEN_WIDTH // 2, 580)
        buttons.append(("Retour", back_rect, lambda: setattr(self, "current_scene", "menu")))
        return buttons

    def set_simulation(self, protocol):
        self.simulation_mode = protocol
        self.simulation_time = 0
        self.simulation_objects = []

    # --- Examen final ---

    def draw_final(self):
        draw_text(screen, "EXAMEN FINAL TERMINÉ", FONT_LARGE, GREEN, SCREEN_WIDTH // 2, 200)
        draw_text(screen, f"Score final : {self.score}", FONT_LARGE, CYAN, SCREEN_WIDTH // 2, 300)
        level = self.get_level_title()
        draw_text(screen, f"Niveau atteint : {level}", FONT_NORMAL, YELLOW, SCREEN_WIDTH // 2, 380)

        mx, my = pygame.mouse.get_pos()
        buttons = self.get_final_buttons()
        for label, rect, action in buttons:
            hover = rect.collidepoint(mx, my)
            draw_button(screen, label, rect.centerx, rect.centery, rect.width, rect.height, PANEL_BG, WHITE, hover)

    def get_level_title(self):
        if self.score >= 120:
            return "Expert Réseau"
        elif self.score >= 80:
            return "Administrateur Réseau"
        elif self.score >= 40:
            return "Technicien Réseau"
        else:
            return "Débutant"

    def get_final_buttons(self):
        buttons = []
        restart_rect = pygame.Rect(0, 0, 250, 60)
        restart_rect.center = (SCREEN_WIDTH // 2, 500)
        menu_rect = pygame.Rect(0, 0, 250, 60)
        menu_rect.center = (SCREEN_WIDTH // 2, 600)
        return [
            ("Recommencer", restart_rect, self.start_final_exam),
            ("Menu principal", menu_rect, self.show_protocol_select)
        ]


# --- Point d'entrée ---

def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
