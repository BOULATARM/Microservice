# Microservices E-Commerce — Django REST Framework

Projet réalisé dans le cadre du **TP2 — Microservices-Oriented Architectures** (application e-commerce **MSOA Shop**).

Ce dépôt rassemble deux microservices backend indépendants, développés en **Python / Django REST Framework** avec une base **SQLite propre à chaque service**. Le frontend React de référence est fourni séparément dans le dépôt du TP.

## Architecture

```text
Microservice/
├── user-service/
│   ├── config/
│   ├── users/
│   ├── manage.py
│   └── requirements.txt
├── shipping-service/
│   ├── config/
│   ├── shipments/
│   ├── manage.py
│   └── requirements.txt
├── .gitignore
└── README.md
```

| Microservice | Rôle | Technologie | Port local | Base de données |
| --- | --- | --- | --- | --- |
| **User / Auth** | Inscription, connexion JWT, profil et déconnexion | Django REST Framework + PyJWT | `8001` | `user-service/db.sqlite3` |
| **Shipping** | Création, consultation et suivi des expéditions | Django REST Framework | `8086` | `shipping-service/db.sqlite3` |

**Important :** les fichiers `db.sqlite3`, `.venv/` et `.env` sont exclus de Git. Les migrations Django sont conservées pour reconstruire les tables.

## 1. Installation locale (Windows / PowerShell)

Pré-requis : Python, Git et PowerShell.

### User Service

```powershell
cd user-service
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Configurer `user-service/.env` avec une clé secrète Django propre à l'installation :

```dotenv
DJANGO_SECRET_KEY=replace-with-a-strong-random-secret
```

Le fichier `config/settings.py` doit lire cette variable depuis `.env` (voir **Configuration des secrets** plus bas).

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver 8001
```

### Shipping Service

Dans **un deuxième terminal** :

```powershell
cd shipping-service
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Configurer `shipping-service/.env` avec une **autre** clé secrète Django :

```dotenv
DJANGO_SECRET_KEY=replace-with-another-strong-random-secret
```

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver 8086
```

> Les répertoires de travail et les bases de données des deux microservices sont distincts. Chaque commande `manage.py` doit être lancée dans le dossier du service correspondant.

## 2. API User / Auth

Base URL : `http://localhost:8001`

| Méthode | Endpoint | Description | Authentification |
| --- | --- | --- | --- |
| `POST` | `/api/auth/register` | Inscrire un utilisateur | Non |
| `POST` | `/api/auth/login` | Se connecter et obtenir un JWT | Non |
| `GET` | `/api/auth/me` | Lire son profil | Bearer JWT |
| `POST` | `/api/auth/logout` | Déconnexion côté client | Bearer JWT |

Les anciennes routes `/api/users/register/`, `/api/users/login/`, `/api/users/me/` et `/api/users/logout/` peuvent également être disponibles pour les tests Postman.

**Exemple — Inscription :**

```json
{
  "name": "Demo User",
  "email": "demo.user@example.com",
  "password": "ExampleSecurePassword2026!"
}
```

**Exemple — Connexion :**

```json
{
  "email": "demo.user@example.com",
  "password": "ExampleSecurePassword2026!"
}
```

Réponse Login (structure) :

```json
{
  "token": "<JWT>",
  "access_token": "<JWT>",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "id": "<UUID>",
    "name": "Demo User",
    "email": "demo.user@example.com",
    "role": "CUSTOMER",
    "created_at": "<ISO_DATETIME>"
  }
}
```

Le profil et la déconnexion utilisent l'en-tête : `Authorization: Bearer <JWT>`.

**Limite actuelle :** la déconnexion supprime la session côté frontend, mais ne révoque pas immédiatement le JWT côté serveur ; il reste valide jusqu'à expiration.

## 3. API Shipping

Base URL : `http://localhost:8086`

| Méthode | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/shipments` | Créer une expédition |
| `GET` | `/api/shipments` | Lister les expéditions |
| `GET` | `/api/shipments/order/{orderId}` | Obtenir une expédition par commande |
| `PATCH` | `/api/shipments/{id}/status` | Changer le statut d'une expédition |

**Exemple — Création :**

```json
{
  "orderId": "order-demo-001",
  "address": {
    "name": "Demo User",
    "address": "123 Boulevard Hassan II",
    "city": "Casablanca"
  }
}
```

**Exemple — Mise à jour :**

```json
{
  "status": "SHIPPED"
}
```

Statuts : `PREPARING`, `SHIPPED`, `IN_TRANSIT`, `DELIVERED`, `CANCELLED`.

Transitions principales :

```text
PREPARING --> SHIPPED --> IN_TRANSIT --> DELIVERED
     |
     +------> CANCELLED
```

Les doublons de `orderId` sont refusés par un code HTTP `409 Conflict`. Le champ `orderId` est un identifiant externe : Shipping ne lit pas directement la base de données du service Orders.

## 4. Connexion au frontend React du TP

Frontend de référence : [ZOUHEIRBN/MSOA-E-com-Demo](https://github.com/ZOUHEIRBN/MSOA-E-com-Demo).

Dans `src/config/backend.js` du frontend :

```javascript
const BACKEND_MODE = {
  AUTH: "rest",
  CATALOG: "mock",
  INVENTORY: "mock",
  ORDERS: "mock",
  PAYMENTS: "mock",
  SHIPPING: "rest",
};

const API_URLS = {
  AUTH: "http://localhost:8001",
  CATALOG: "http://localhost:8082",
  INVENTORY: "http://localhost:8083",
  ORDERS: "http://localhost:8084",
  PAYMENTS: "http://localhost:8085",
  SHIPPING: "http://localhost:8086",
};

export { BACKEND_MODE, API_URLS };
```

Dans les deux backends, autoriser l'origine React avec `django-cors-headers` :

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
```

La communication interservices avec Orders et les autres composants doit encore être validée lors de l'intégration de l'équipe. Une commande simulée dans le frontend n'est pas une commande persistée par un service Orders réel.

## 5. Configuration des secrets

**Ne jamais publier une clé Django `SECRET_KEY` réelle, un JWT, ni une base SQLite contenant des utilisateurs.**

Dans chaque service, installer `python-dotenv` (inclus dans `requirements.txt` après mise à jour), puis dans `config/settings.py` :

```python
import os
from dotenv import load_dotenv

# Après la définition de BASE_DIR :
load_dotenv(BASE_DIR / ".env")
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
```

Générer une nouvelle clé secrète localement :

```powershell
.\.venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copier la valeur générée dans `.env` (non suivi par Git). Utiliser une clé distincte pour chacun des deux services. Si des clés ont déjà été publiées, les remplacer.

## 6. Vérifications

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py migrate
```

Les opérations principales ont été testées localement avec Postman ; des parcours d'authentification et de suivi ont également été visualisés dans React. La validation complète en équipe et les tests de sécurité restent à compléter.

## 7. Avertissement

Projet pédagogique pour exécution locale. Le serveur Django de développement, SQLite sous charge élevée, l'authentification JWT et les endpoints Shipping ne constituent pas une configuration prête pour la production. Les opérations d'expédition doivent être protégées par une authentification et des autorisations appropriées avant toute exposition publique.
