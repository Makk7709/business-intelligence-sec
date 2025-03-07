# Intégration de l'API OpenAI pour l'Assistant IA

Ce document décrit les modifications apportées pour intégrer l'API OpenAI à l'assistant IA du dashboard financier.

## Modifications apportées

### 1. Fichier `app/run_direct.py`

Le fichier `app/run_direct.py` a été modifié pour utiliser l'API OpenAI au lieu des réponses prédéfinies. Les modifications incluent :

- Ajout des imports nécessaires pour utiliser l'API OpenAI et charger les variables d'environnement :
  ```python
  from dotenv import load_dotenv
  import openai
  ```

- Chargement des variables d'environnement :
  ```python
  load_dotenv()
  ```

- Configuration de l'API OpenAI avec la clé API présente dans le fichier `.env` :
  ```python
  openai_api_key = os.getenv("OPENAI_API_KEY")
  if not openai_api_key:
      logger.warning("Clé API OpenAI non trouvée. L'assistant IA utilisera des réponses prédéfinies.")
  else:
      openai.api_key = openai_api_key
      logger.info("API OpenAI configurée avec succès.")
  ```

- Modification de la fonction `ai_query()` pour utiliser l'API OpenAI au lieu des réponses prédéfinies :
  ```python
  # Utiliser l'API OpenAI si disponible
  if openai_api_key:
      try:
          logger.info(f"Envoi de la requête à OpenAI: {query}")
          
          # Contexte financier pour l'assistant
          financial_context = """
          Données financières d'Apple:
          - Revenus: 390,036 millions de dollars en 2024, 375,970 millions en 2023, 368,234 millions en 2022
          - Marge brute: 43.8% en 2024, 43.2% en 2023, 46.4% en 2022
          - Bénéfice net: 97,150 millions de dollars en 2024, 94,320 millions en 2023, 99,803 millions en 2022
          
          Données financières de Microsoft:
          - Revenus: 225,340 millions de dollars en 2024, 205,357 millions en 2023, 188,852 millions en 2022
          - Marge brute: 70.0% en 2024, 69.0% en 2023, 66.8% en 2022
          - Bénéfice net: 72,361 millions de dollars en 2024, 72,361 millions en 2023, 67,430 millions en 2022
          
          Prédictions pour Apple:
          - Revenus: environ 405,637 millions de dollars en 2025, 421,863 millions en 2026
          - Marge brute: environ 44.1% en 2025, 44.3% en 2026
          
          Prédictions pour Microsoft:
          - Revenus: environ 245,621 millions de dollars en 2025, 267,726 millions en 2026
          - Marge brute: environ 70.5% en 2025, 71.0% en 2026
          """
          
          # Appel à l'API OpenAI
          response = openai.chat.completions.create(
              model="gpt-3.5-turbo",
              messages=[
                  {"role": "system", "content": f"Tu es un assistant financier spécialisé dans l'analyse des données d'Apple et Microsoft. Réponds de manière concise et précise aux questions sur les données financières. Voici les données dont tu disposes: {financial_context}"},
                  {"role": "user", "content": query}
              ],
              max_tokens=150,
              temperature=0.7
          )
          
          # Extraire la réponse
          ai_response = response.choices[0].message.content
          logger.info(f"Réponse d'OpenAI reçue: {ai_response[:50]}...")
          
          return jsonify({
              'response': ai_response,
              'query': query
          })
          
      except Exception as e:
          logger.error(f"Erreur lors de l'appel à l'API OpenAI: {str(e)}")
          logger.info("Utilisation des réponses prédéfinies comme fallback.")
  ```

- Ajout d'un mécanisme de fallback pour utiliser les réponses prédéfinies en cas d'erreur ou si l'API OpenAI n'est pas disponible.

## Configuration requise

Pour que l'intégration de l'API OpenAI fonctionne correctement, vous devez avoir un fichier `.env` à la racine du projet avec la clé API OpenAI :

```
OPENAI_API_KEY=votre_clé_api_ici
```

## Dépendances

Les dépendances suivantes ont été ajoutées au projet :

- `python-dotenv` : Pour charger les variables d'environnement
- `openai` : Pour utiliser l'API OpenAI

Vous pouvez les installer avec la commande suivante :

```bash
pip install python-dotenv openai
```

## Vérification du fonctionnement

Pour vérifier que l'assistant IA est bien connecté à l'API OpenAI, vous pouvez lancer l'application et envoyer une requête à l'API de l'assistant IA :

```bash
python app/run_direct.py
```

Puis, dans un autre terminal :

```bash
curl -s -X POST -H "Content-Type: application/json" -d '{"query":"Quels sont les revenus d Apple ?"}' http://127.0.0.1:5115/api/ai-query
```

Vous devriez recevoir une réponse générée par l'API OpenAI, comme en témoigne le format et le contenu de la réponse qui est plus détaillé et personnalisé que les réponses prédéfinies.

## Logs

Les logs de l'application montrent que l'API OpenAI est bien utilisée :

```
2025-03-07 09:47:41 - INFO - API OpenAI configurée avec succès.
2025-03-07 09:47:41 - INFO - Envoi de la requête à OpenAI: Quels sont les revenus d Apple ?
2025-03-07 09:47:44 - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
2025-03-07 09:47:44 - INFO - Réponse d'OpenAI reçue: Les revenus d'Apple sont les suivants :
- 390,036 ...
```

## Sauvegarde

Une sauvegarde du fichier modifié a été créée dans le répertoire `backups/app/`. 