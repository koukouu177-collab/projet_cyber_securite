#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADMIN_REMOTE - Outil d'Administration à Distance Légitime
Développé par les hacker_tchadien

Usage éducatif : contrôle de vos propres machines uniquement.
"""

import socket
import threading
import json
import base64
import os
import sys
import platform
import subprocess
import time
import datetime
from pathlib import Path

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class DummyFore:
        def __getattr__(self, name): return ""
    class DummyStyle:
        def __getattr__(self, name): return ""
    Fore = DummyFore()
    Style = DummyStyle()

# ============ CONFIGURATION ============
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 4444
BUFFER_SIZE = 4096
ENCODING = "utf-8"

# ============ ASCII ART LOGO ============
LOGO = f"""
{Fore.CYAN}    █████╗ ██████╗ ███╗   ███╗██╗███╗   ██╗    ██████╗ ███████╗███╗   ███╗ ██████╗ ████████╗███████╗
   ██╔══██╗██╔══██╗████╗ ████║██║████╗  ██║    ██╔══██╗██╔════╝████╗ ████║██╔═══██╗╚══██╔══╝██╔════╝
   ███████║██║  ██║██╔████╔██║██║██╔██╗ ██║    ██████╔╝█████╗  ██╔████╔██║██║   ██║   ██║   █████╗  
   ██╔══██║██║  ██║██║╚██╔╝██║██║██║╚██╗██║    ██╔══██╗██╔══╝  ██║╚██╔╝██║██║   ██║   ██║   ██╔══╝  
   ██║  ██║██████╔╝██║ ╚═╝ ██║██║██║ ╚████║    ██║  ██║███████╗██║ ╚═╝ ██║╚██████╔╝   ██║   ███████╗
   ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝    ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝    ╚═╝   ╚══════╝{Style.RESET_ALL}
{Fore.YELLOW}                                    [ Outil d'Administration à Distance - Usage Personnel ]
                                          [ Développé par les hacker_tchadien ]{Style.RESET_ALL}
"""

# ============ SERVEUR ============
class AdminServer:
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self.host = host
        self.port = port
        self.server = None
        self.clients = {}
        self.lock = threading.Lock()
        self.running = False

    def start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        self.running = True
        print(f"{Fore.GREEN}[+] Serveur démarré sur {self.host}:{self.port}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[!] Attente de connexion de vos machines...{Style.RESET_ALL}\n")
        threading.Thread(target=self.accept_connections, daemon=True).start()

    def accept_connections(self):
        while self.running:
            try:
                self.server.settimeout(1)
                client, addr = self.server.accept()
                client_id = f"{addr[0]}:{addr[1]}"
                with self.lock:
                    self.clients[client_id] = {"socket": client, "addr": addr, "connected": time.time()}
                print(f"{Fore.GREEN}[+] Machine connectée : {client_id}{Style.RESET_ALL}")
                threading.Thread(target=self.handle_client, args=(client, client_id), daemon=True).start()
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"{Fore.RED}[-] Erreur : {e}{Style.RESET_ALL}")

    def handle_client(self, client, client_id):
        while self.running:
            try:
                data = client.recv(BUFFER_SIZE).decode(ENCODING)
                if not data:
                    break
                msg = json.loads(data)
                if msg.get("type") == "heartbeat":
                    continue
                print(f"{Fore.CYAN}[{client_id}] {msg.get('data', '')}{Style.RESET_ALL}")
            except Exception:
                break
        with self.lock:
            if client_id in self.clients:
                del self.clients[client_id]
        print(f"{Fore.YELLOW}[-] Machine déconnectée : {client_id}{Style.RESET_ALL}")

    def send_command(self, client_id, command):
        with self.lock:
            if client_id in self.clients:
                try:
                    self.clients[client_id]["socket"].send(json.dumps({"cmd": command}).encode(ENCODING))
                    return True
                except Exception as e:
                    print(f"{Fore.RED}[-] Erreur d'envoi : {e}{Style.RESET_ALL}")
        return False

    def list_clients(self):
        with self.lock:
            return list(self.clients.keys())

    def stop(self):
        self.running = False
        for c in list(self.clients.values()):
            try:
                c["socket"].close()
            except:
                pass
        if self.server:
            self.server.close()

# ============ CLIENT ============
class AdminClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.running = False

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.server_host, self.server_port))
            self.running = True
            print(f"{Fore.GREEN}[+] Connecté au serveur {self.server_host}:{self.server_port}{Style.RESET_ALL}")
            threading.Thread(target=self.receive_commands, daemon=True).start()
            self.heartbeat()
        except Exception as e:
            print(f"{Fore.RED}[-] Connexion échouée : {e}{Style.RESET_ALL}")

    def heartbeat(self):
        while self.running:
            try:
                self.socket.send(json.dumps({"type": "heartbeat"}).encode(ENCODING))
                time.sleep(30)
            except:
                break

    def receive_commands(self):
        while self.running:
            try:
                data = self.socket.recv(BUFFER_SIZE).decode(ENCODING)
                if not data:
                    break
                msg = json.loads(data)
                cmd = msg.get("cmd", "")
                result = self.execute_command(cmd)
                self.socket.send(json.dumps({"type": "result", "data": result}).encode(ENCODING))
            except Exception as e:
                print(f"{Fore.RED}[-] Erreur : {e}{Style.RESET_ALL}")
                break
        self.running = False

    def execute_command(self, cmd):
        try:
            if cmd == "info":
                return self.get_system_info()
            elif cmd == "screenshot":
                return self.take_screenshot()
            elif cmd == "list_files":
                return self.list_files()
            elif cmd.startswith("exec "):
                return self.run_command(cmd[5:])
            elif cmd == "shutdown":
                return self.shutdown_system()
            else:
                return f"Commande inconnue : {cmd}"
        except Exception as e:
            return f"Erreur : {str(e)}"

    def get_system_info(self):
        info = {
            "os": platform.system(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "hostname": socket.gethostname(),
            "ip": socket.gethostbyname(socket.gethostname()),
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return json.dumps(info, indent=2)

    def take_screenshot(self):
        try:
            import pyautogui
            screenshot = pyautogui.screenshot()
            filename = f"screenshot_{int(time.time())}.png"
            screenshot.save(filename)
            return f"Capture d'écran sauvegardée : {filename}"
        except ImportError:
            return "pyautogui non installé. Installez-le avec : pip install pyautogui"
        except Exception as e:
            return f"Erreur capture : {str(e)}"

    def list_files(self):
        try:
            files = os.listdir(".")
            return "\n".join(files[:50])
        except Exception as e:
            return f"Erreur : {str(e)}"

    def run_command(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
            output = result.stdout + result.stderr
            return output[:2000] if output else "Commande exécutée (pas de sortie)"
        except subprocess.TimeoutExpired:
            return "Commande trop longue (timeout)"
        except Exception as e:
            return f"Erreur : {str(e)}"

    def shutdown_system(self):
        try:
            os.system("shutdown /s /t 60" if platform.system() == "Windows" else "shutdown -h +1")
            return "Arrêt programmé dans 60 secondes. Annulez avec : shutdown /a (Windows) ou shutdown -c (Linux)"
        except Exception as e:
            return f"Erreur : {str(e)}"

# ============ MENU PRINCIPAL ============
def print_menu():
    print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║                      MENU PRINCIPAL                          ║
╠══════════════════════════════════════════════════════════════╣
║  {Fore.GREEN}[1]{Fore.CYAN} Démarrer le serveur (attendre connexion)              ║
║  {Fore.GREEN}[2]{Fore.CYAN} Se connecter à un serveur (mode client)               ║
║  {Fore.GREEN}[3]{Fore.CYAN} Envoyer une commande à une machine connectée          ║
║  {Fore.GREEN}[4]{Fore.CYAN} Lister les machines connectées                        ║
║  {Fore.GREEN}[5]{Fore.CYAN} Voir les commandes disponibles                        ║
║  {Fore.RED}[6]{Fore.CYAN} Quitter                                               ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
""")


def print_commands():
    print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║                    COMMANDES DISPONIBLES                     ║
╠══════════════════════════════════════════════════════════════╣
║  {Fore.YELLOW}info{Fore.CYAN}         - Informations système de la machine          ║
║  {Fore.YELLOW}screenshot{Fore.CYAN}   - Prendre une capture d'écran                 ║
║  {Fore.YELLOW}list_files{Fore.CYAN}   - Lister les fichiers du répertoire           ║
║  {Fore.YELLOW}exec <cmd>{Fore.CYAN}   - Exécuter une commande shell                 ║
║  {Fore.YELLOW}shutdown{Fore.CYAN}     - Arrêter la machine (avec confirmation)      ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
""")


def main():
    print(LOGO)
    server = None
    client = None

    while True:
        print_menu()
        choice = input(f"{Fore.GREEN}[?] Votre choix : {Style.RESET_ALL}").strip()

        if choice == "1":
            host = input(f"{Fore.YELLOW}[?] Hôte (défaut: {DEFAULT_HOST}) : {Style.RESET_ALL}").strip() or DEFAULT_HOST
            port = input(f"{Fore.YELLOW}[?] Port (défaut: {DEFAULT_PORT}) : {Style.RESET_ALL}").strip() or str(DEFAULT_PORT)
            server = AdminServer(host, int(port))
            server.start()
            print(f"{Fore.GREEN}[+] Serveur actif. Appuyez sur Entrée pour retourner au menu...{Style.RESET_ALL}")
            input()

        elif choice == "2":
            host = input(f"{Fore.YELLOW}[?] IP du serveur : {Style.RESET_ALL}").strip()
            port = input(f"{Fore.YELLOW}[?] Port (défaut: {DEFAULT_PORT}) : {Style.RESET_ALL}").strip() or str(DEFAULT_PORT)
            if host:
                client = AdminClient(host, int(port))
                client.connect()
                print(f"{Fore.GREEN}[+] Client connecté. Appuyez sur Entrée pour retourner au menu...{Style.RESET_ALL}")
                input()

        elif choice == "3":
            if not server or not server.list_clients():
                print(f"{Fore.RED}[-] Aucune machine connectée.{Style.RESET_ALL}")
                continue
            print(f"{Fore.CYAN}[*] Machines connectées :{Style.RESET_ALL}")
            for i, cid in enumerate(server.list_clients(), 1):
                print(f"  {Fore.GREEN}[{i}]{Style.RESET_ALL} {cid}")
            idx = input(f"{Fore.YELLOW}[?] Numéro de la machine : {Style.RESET_ALL}").strip()
            try:
                client_id = server.list_clients()[int(idx) - 1]
                cmd = input(f"{Fore.YELLOW}[?] Commande à envoyer : {Style.RESET_ALL}").strip()
                if server.send_command(client_id, cmd):
                    print(f"{Fore.GREEN}[+] Commande envoyée avec succès.{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}[-] Échec de l'envoi.{Style.RESET_ALL}")
            except (IndexError, ValueError):
                print(f"{Fore.RED}[-] Sélection invalide.{Style.RESET_ALL}")

        elif choice == "4":
            if server and server.list_clients():
                print(f"{Fore.CYAN}[*] Machines connectées :{Style.RESET_ALL}")
                for cid in server.list_clients():
                    print(f"  {Fore.GREEN}[+]{Style.RESET_ALL} {cid}")
            else:
                print(f"{Fore.YELLOW}[!] Aucune machine connectée.{Style.RESET_ALL}")

        elif choice == "5":
            print_commands()

        elif choice == "6":
            print(f"{Fore.YELLOW}[!] Fermeture...{Style.RESET_ALL}")
            if server:
                server.stop()
            break

        else:
            print(f"{Fore.RED}[-] Choix invalide.{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
