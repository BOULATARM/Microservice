# LAB 3 — API CONTRACTS
## Contribution individuelle : Authentication (User) et Shipping

**Base étudiée :** dépôt public [BOULATARM/Microservice](https://github.com/BOULATARM/Microservice), branche `main`, consulté le 18 novembre 2026, et énoncé *LAB 3: DESIGNING AN API CONTRACT* (Prof. Zouheir BANOU).

> **Périmètre :** ce document répond à Q2 et Q3 pour les deux microservices développés, et à Q4 et Q5 pour le cas **Catalog** spécifié dans l'énoncé. Il ne constitue pas une preuve d'exécution des tests. Les données d'exemple sont illustratives, sauf indication contraire.

## Question 2 — REST endpoints nécessaires aux opérations métier

### 2.1 Architecture des deux services

| Propriété | Authentication / User | Shipping |
|---|---|---|
| Framework | Django REST Framework | Django REST Framework |
| Stockage | SQLite, table `users` | SQLite, table `shipments` |
| URL locale | `http://localhost:8001` | `http://localhost:8086` |
| Responsabilité | Comptes, authentification, profil | Création et suivi des expéditions |
| Identifiant | `id` (UUID stocké comme texte) | `id` (UUID stocké comme texte) |

Chaque service dispose de sa propre base SQLite. `Shipping.orderId` est un identifiant externe de commande, pas une relation SQL vers la base Orders.

### 2.2 Authentication — description des opérations

| Méthode | Route | Objectif | Entrée | Succès | Erreurs |
|---|---|---|---|---|---|
| `POST` | `/api/auth/register` | Inscription d'un utilisateur | JSON `name`, `email`, `password` | `201` : `{message, user}` | `400` : validation, email déjà utilisé |
| `POST` | `/api/auth/login` | Connexion et génération d'un JWT | JSON `email`, `password` | `200` : `{message, token, access_token, token_type, expires_in, user}` | `400` : données invalides ; `401` : identifiants incorrects |
| `GET` | `/api/auth/me` | Consulter le compte connecté | `Authorization: Bearer <JWT>` | `200` : objet `User` | `401` : JWT manquant/invalide/expiré |
| `POST` | `/api/auth/logout` | Confirmer la déconnexion | `Authorization: Bearer <JWT>` | `200` : `{success:true,message}` | `401` : JWT manquant/invalide/expiré |

Pour les méthodes POST, l'en-tête `Content-Type: application/json` accompagne les corps JSON. Le JSON de connexion contient un JWT de durée de vie **3600 secondes**, signé en **HS256** à l'aide de la clé Django. La déconnexion ne révoque pas ce JWT côté serveur : le client doit supprimer sa session localement.

**Corps d'inscription (exemple) :**

```json
{
  "name": "Demo User",
  "email": "demo.user@example.com",
  "password": "ExampleSecurePassword2026!"
}
```

**Réponse de connexion (structure, données fictives) :**

```json
{
  "message": "Connexion réussie",
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

Le modèle `User` contient `id`, `name`, `email`, `password_hash`, `role`, `created_at`. Le mot de passe est validé, haché et **jamais renvoyé dans `UserSerializer`**.

### 2.3 Shipping — description des opérations

| Méthode | Route | Objectif | Entrée | Succès | Erreurs |
|---|---|---|---|---|---|
| `GET` | `/api/shipments` | Lister les expéditions | Aucune | `200` : tableau d'objets `Shipment` | — |
| `POST` | `/api/shipments` | Créer une expédition | JSON `orderId`, `address` | `201` : objet `Shipment`, statut `PREPARING` | `400` : données invalides ; `409` : `orderId` déjà utilisé / conflit |
| `GET` | `/api/shipments/order/{orderId}` | Chercher une expédition pour une commande | Paramètre URL `orderId` (texte) | `200` : objet `Shipment` | `404` : expédition introuvable |
| `PATCH` | `/api/shipments/{id}/status` | Mettre à jour un statut | Paramètre URL `id` (UUID texte), JSON `status` | `200` : objet `Shipment` modifié | `400` : statut inconnu ; `404` : expédition introuvable ; `409` : transition interdite |

**Corps de création (exemple) :**

```json
{
  "orderId": "order-123",
  "address": {
    "name": "Demo Customer",
    "address": "123 Main Street",
    "city": "Casablanca"
  }
}
```

**Réponse d'expédition (structure, exemple fictif) :**

```json
{
  "id": "<UUID>",
  "orderId": "order-123",
  "address": {
    "name": "Demo Customer",
    "address": "123 Main Street",
    "city": "Casablanca"
  },
  "trackingNumber": "MSOA-AB5ED67C54B6",
  "status": "PREPARING",
  "createdAt": "2026-11-18T12:00:00+00:00",
  "updatedAt": "2026-11-18T12:00:00+00:00"
}
```

**Corps de modification :** `{ "status": "SHIPPED" }`.

**États autorisés :** `PREPARING`, `SHIPPED`, `IN_TRANSIT`, `DELIVERED`, `CANCELLED`.

**Transitions autorisées :**

- `PREPARING` → `SHIPPED` ou `CANCELLED` ;
- `SHIPPED` → `IN_TRANSIT` ;
- `IN_TRANSIT` → `DELIVERED` ;
- `DELIVERED` et `CANCELLED` : états terminaux.

**Limite actuelle :** les vues Shipping n'appliquent pas d'authentification ni d'autorisation explicite. Ne pas déclarer le service protégé par JWT.

### 2.4 Interaction avec les autres services

- **Frontend → Auth** : inscription, connexion, JWT, profil, déconnexion.
- **Frontend / futur Orders → Shipping** : création, consultation et suivi des expéditions à partir d'`orderId`.
- **Shipping → Orders** : aucune lecture directe de la base Orders ; l'intégration réelle doit encore être validée.
- **Catalog, Inventory, Orders, Payments** : non implémentés dans ce dépôt ; leurs contrats restent à obtenir auprès des autres membres du groupe.

## Question 3 — API contract design and implementation

Deux fichiers OpenAPI 3.0.3 sont déjà publiés :

- [`contracts/auth.openapi.yaml`](https://github.com/BOULATARM/Microservice/blob/main/contracts/auth.openapi.yaml)
- [`contracts/shipping.openapi.yaml`](https://github.com/BOULATARM/Microservice/blob/main/contracts/shipping.openapi.yaml)

Ces fichiers décrivent les routes, opérations, chemins, paramètres, exemples de `requestBody`, schémas des entrées et sorties, ainsi que les principaux codes d'erreur. Le contrat Auth déclare `securitySchemes.bearerAuth` et l'applique à `/me` et `/logout`. Le contrat Shipping décrit les changements d'état et la structure de `Shipment`.

### Vérification des dix éléments exigés (a–j)

| Élément demandé | Auth | Shipping | Commentaire |
|---|---|---|---|
| a. Opérations | Oui | Oui | 4 opérations par service |
| b. Méthode + endpoint | Oui | Oui | Alignés sur `urls.py` et `views.py` |
| c. Objet de chaque endpoint | Oui | Oui | `summary` dans YAML |
| d. Paramètres d'URL | Sans objet pour les 4 routes | Oui | `orderId` et `id` |
| e. Paramètres et formats | Oui | Oui | Schémas OpenAPI |
| f. HTTP headers | Partiellement explicites | Partiellement explicites | `Content-Type` via `application/json`, Bearer sous `securitySchemes`; compléter explications |
| g. Schémas des requêtes | Oui | Oui | Champs obligatoires présents |
| h. Codes HTTP de succès | Oui | Oui | 200/201 |
| i. Schémas des réponses | Oui | Oui | `User`, `Shipment` |
| j. Schémas des erreurs | Partiel | Partiel | Voir correctifs ci-dessous |

### Corrections nécessaires pour Q3

1. **Auth** : ajouter un schéma concret de réponse `401` pour `/api/auth/me` et `/api/auth/logout` (actuellement seule la description est fournie). Pour les erreurs de JWT de Django REST Framework, les réponses prennent généralement la forme `{ "detail": "..." }`; vérifier sur le serveur avant de figer ce schéma.
2. **Shipping** : compléter `content.application/json.schema` pour les deux réponses `400` (création et modification de statut). Le DRF retourne typiquement des erreurs par champ (`{"status":["..."]}` ou `{"address":{...}}`) ; utiliser les sorties réelles Postman comme référence.
3. **Validation documentaire** : ouvrir les deux fichiers dans Swagger Editor et vérifier les avertissements OpenAPI.
4. **Tests de contrat** : conserver des captures réelles (requête + réponse + code HTTP). Le dépôt publie actuellement des `tests.py` avec uniquement le squelette initial, donc aucun test automatisé n'y est démontré.
5. **Intégration** : le README indique que Auth et Shipping sont en `rest`, mais Orders, Catalog, Inventory et Payments restent en mode `mock` côté frontend ; ne pas déclarer l'intégration collective achevée.

### Scénarios Postman à démontrer

| Test | HTTP attendu | Preuve à produire |
|---|---|---|
| Inscription valide | 201 | Capture du JSON `{message,user}` |
| Inscription invalide / doublon | 400 | Capture des erreurs de validation |
| Connexion valide | 200 | Masquer le JWT sur capture ; vérifier `token`, `expires_in`, `user` |
| Mauvais identifiants | 401 | Capture `{message}` |
| Profil sans JWT | 401 | Capture du JSON d'erreur |
| Profil avec JWT | 200 | Capture de `User` |
| Déconnexion avec JWT | 200 | Capture `{success,message}` |
| Création d'expédition | 201 | Capture de `Shipment` et `PREPARING` |
| Liste d'expéditions | 200 | Capture de la liste |
| Recherche par `orderId` existant | 200 | Capture de `Shipment` |
| Recherche par `orderId` absent | 404 | Capture `{message}` |
| Création `orderId` dupliqué | 409 | Capture `{message}` |
| Transition `PREPARING` → `SHIPPED` | 200 | Capture nouveau statut |
| Transition interdite | 409 | Capture `{message}` |
| Statut inconnu | 400 | Capture d'erreur de validation |

Ne pas joindre de JWT actif, clé secrète ou données personnelles réelles dans les captures.

## Question 4 — Pourquoi le changement `price` rompt-il la compatibilité ?

Le cas donné dans le TP concerne **Catalog**, même si ma contribution technique porte sur Auth et Shipping.

**Ancien contrat (V1) :**

```json
{ "id": 1, "name": "Lenovo ThinkPad E14", "price": 8499 }
```

**Nouveau contrat non compatible :**

```json
{
  "id": 1,
  "name": "Lenovo ThinkPad E14",
  "price": { "amount": 8499, "currency": "MAD" }
}
```

Le JSON reste syntaxiquement correct, mais le type de `price` passe de **nombre** à **objet**, ce qui viole les hypothèses du contrat existant. Un frontend effectuant un formatage ou une opération numérique sur `price` peut afficher un résultat incorrect ou produire une erreur. Orders peut échouer pendant le calcul du total, la validation de commande ou la transmission du montant à Payments. Inventory et Shipping ne consomment pas nécessairement le prix directement, mais peuvent être touchés indirectement si Orders échoue en amont. Auth, qui gère identité et JWT, n'est pas directement concerné par le changement de structure du prix.

**Conclusion Q4 :** une API peut retourner un JSON valide tout en rompant la compatibilité sémantique et structurelle prévue par les consommateurs. Les types et propriétés des champs font partie du contrat.

## Question 5 — Quelle stratégie d'évolution choisir ?

| Approche | Principe | Avantages | Inconvénients |
|---|---|---|---|
| Remplacement immédiat | Modifier `price` de `number` à `object` dans l'API existante | Mise en œuvre rapide | Rupture des consommateurs existants ; à éviter |
| Extension additive | Garder `price: 8499`, ajouter `priceDetails: { amount: 8499, currency: "MAD" }` | Compatibilité descendante forte, migration simple | Duplication temporaire de l'information |
| Versionnement explicite | Conserver V1 (`price` nombre), publier V2 (`price` objet) | Contrats explicites, migration indépendante, bon exercice pédagogique | Deux versions à maintenir temporairement |

**Stratégie proposée pour le TP : versionnement d'API**, à valider en groupe. Conserver une route V1 avec la structure `price` numérique et introduire une route V2 avec `price.amount` et `price.currency`. Mettre à jour le contrat OpenAPI de Catalog avec les deux versions et tester les consommateurs existants sur V1, puis le nouveau consommateur sur V2. Déprécier V1 uniquement après migration vérifiée.

*Remarque :* si le besoin n'impose pas de changer le type du champ `price`, l'extension additive est l'option la plus simple en pratique ; le versionnement est proposé ici car l'énoncé met l'accent sur la gestion explicite d'un changement incompatible.

**Exemple de stratégie (routes à adapter au projet Catalog réel) :**

- `GET /api/products` — V1 : `{ "id":1, "price":8499 }`;
- `GET /api/v2/products` — V2 : `{ "id":1, "price": { "amount":8499, "currency":"MAD" } }`.

Ces routes V2 **ne sont pas présentes dans le dépôt Auth/Shipping** ; elles constituent une proposition pour la question 6 et nécessitent une mise en œuvre par le membre responsable de Catalog.

## Sources examinées

- Énoncé du professeur : *LAB 3: DESIGNING AN API CONTRACT*, pages 1–2 (fichier fourni dans la conversation).
- [README.md](https://github.com/BOULATARM/Microservice/blob/main/README.md)
- [Contrat Auth](https://github.com/BOULATARM/Microservice/blob/main/contracts/auth.openapi.yaml)
- [Contrat Shipping](https://github.com/BOULATARM/Microservice/blob/main/contracts/shipping.openapi.yaml)
- [Auth views](https://github.com/BOULATARM/Microservice/blob/main/user-service/users/views.py), [serializers](https://github.com/BOULATARM/Microservice/blob/main/user-service/users/serializers.py), [authentication](https://github.com/BOULATARM/Microservice/blob/main/user-service/users/authentication.py), [models](https://github.com/BOULATARM/Microservice/blob/main/user-service/users/models.py)
- [Shipping views](https://github.com/BOULATARM/Microservice/blob/main/shipping-service/shipments/views.py), [serializers](https://github.com/BOULATARM/Microservice/blob/main/shipping-service/shipments/serializers.py), [models](https://github.com/BOULATARM/Microservice/blob/main/shipping-service/shipments/models.py)
- [Shipping settings](https://github.com/BOULATARM/Microservice/blob/main/shipping-service/config/settings.py)
- [Tests Auth](https://github.com/BOULATARM/Microservice/blob/main/user-service/users/tests.py), [Tests Shipping](https://github.com/BOULATARM/Microservice/blob/main/shipping-service/shipments/tests.py)
