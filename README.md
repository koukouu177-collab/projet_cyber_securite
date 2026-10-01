# ADMIN_REMOTE - Administration à Distance Légale

> **Créé par les hacker_tchadien** - Outil d'administration de vos propres machines

## Description

ADMIN_REMOTE est un outil légal pour **administrer vos propres ordinateurs** sur le même réseau local. Il permet de surveiller et contrôler vos machines avec une interface claire indiquant que la connexion est active.

## Fonctionnalités

- **Surveillance système** — CPU, RAM, disque, processus
- **Capture d'écran** — Visualiser l'écran de la machine distante
- **Liste des fichiers** — Explorer les répertoires
- **Exécution de commandes** — Lancer des commandes à distance
- **Notifications** — Alertes Telegram/Discord configurables
- **Interface sécurisée** — Mot de passe requis, affichage du statut de connexion

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

### 1. Sur la machine à contrôler (serveur)
```bash
python admin_remote.py
# Choisissez [1] Mode Serveur
```

### 2. Sur votre machine (client)
```bash
python admin_remote.py
# Choisissez [2] Mode Client
# Entrez l'IP du serveur
```

## Avertissement

**Cet outil doit être utilisé uniquement sur vos propres machines.** Une notification visible s'affiche sur le serveur indiquant que la connexion est active.

## Auteur

**les hacker_tchadien**
