# 🎙️ Anti-Scam AI – Rapport Technique et Fonctionnel

## 1. 🎯 Introduction Générale

Ce projet a été réalisé dans le cadre d’un exercice pédagogique visant à construire une intelligence artificielle capable de dialoguer avec des arnaqueurs téléphoniques dans le but de leur faire perdre du temps. Il exploite des technologies modernes comme la reconnaissance vocale, les modèles de langage (LLM) et la synthèse vocale.

L’objectif est de simuler un faux interlocuteur crédible, afin de prolonger les échanges avec l’escroc sans éveiller de soupçons.

---

## 2. 📋 Spécifications Fonctionnelles

L’IA doit :

- Être capable d’écouter un arnaqueur (via micro ou fichier audio)
- Transcrire ce qu’il dit (Speech-to-Text)
- Générer une réponse crédible (via LLM)
- Lire cette réponse à voix haute (Text-to-Speech)
- Ajouter des caractéristiques réalistes : hésitations, lapsus, erreurs
- Simuler un comportement humain convaincant

Elle **ne doit pas** :

- Révéler qu’elle est une IA
- Donner des réponses robotiques
- Couper la parole

---

## 3. 🏗️ Architecture Générale

Le système repose sur 4 modules principaux :

- **Interface Web (index.html)** : Permet à l’utilisateur de chatter ou d’envoyer un message vocal. Communique avec Flask via WebSocket (Socket.IO).
- **Serveur Flask (webrtc.py)** : Gère les routes, relaie les messages texte ou audio, émet les réponses.
- **Moteur IA (anti\_scam.py)** : Enregistre, transcrit, envoie à un LLM, puis lit la réponse avec synthèse vocale.
- **LLM & APIs** : Utilisation de Nebius (Qwen2.5-32B) pour la génération de texte, et Google Cloud pour la voix.

---

## 4. 🧠 Prompt Système : Conception et Justification

```text
Contexte : Tu es une fausse victime d’arnaque. Tu parles à un escroc qui propose une fausse offre d’emploi.
Objectif : Lui faire perdre du temps.
Personnalité : MARTIN MARTIN, 28 ans, vivant à Lyon, enthousiaste et naïf.
Instructions : Pose des questions, montre de l’intérêt, reste polie.
Négatif : Ne jamais dire que tu es une IA. Si on te le demande, sois offensée.
Réaliste : Ajoute des hésitations, des erreurs, des lapsus, des pauses…
```

Ce prompt est intégré dès le lancement du script dans une variable système, puis enrichi dynamiquement avec les messages de l’escroc (retranscrits).

---

## 5. 🖥️ Interface Utilisateur

L’interface web simple mais fonctionnelle permet :

- D’envoyer un message texte
- D’enregistrer un message vocal (en wav)
- De voir les réponses de l’IA
- D’afficher l’émotion détectée (simulée pour l’instant)

> La communication se fait via Socket.IO. Le serveur Flask gère les événements `chat_message` et `audio_stream`.

---

## 6. ⚙️ Fonctionnalités IA

- **🎧 Enregistrement audio** via microphone (SoundDevice)
- **🧠 Transcription vocale** via Google Speech-to-Text
- **📝 Génération de texte** avec Nebius / Qwen2.5-32B-Instruct
- **📢 Synthèse vocale** via Google Text-to-Speech (voix féminine)
- **🔁 Streaming** : la réponse est générée et lue progressivement
- **💬 Simulation humaine** :
  - Hésitations : [euh], [hum]...
  - Pauses longues
  - Reformulations spontanées
  - Lapsus volontairement injectés

---

## 7. 🧪 Exemple de Scénario (démo simplifiée)

1. L’escroc envoie : “Bonjour, vous avez été sélectionné pour un poste très bien payé.”
2. L’IA transcrit l’audio → texte
3. Elle génère : “Oh super ! Et euh… [pause] vous pouvez me dire où est basé le poste exactement ?”
4. Elle lit cette réponse avec une voix naturelle féminine

> Chaque échange prend plusieurs secondes et donne l’illusion d’une vraie conversation humaine.

---

## 8. 🧰 Technologies Utilisées

| Module                | Technologie           |
| --------------------- | --------------------- |
| Serveur Web           | Flask + Socket.IO     |
| Interface utilisateur | HTML + JS             |
| STT (speech to text)  | Google Speech-to-Text |
| LLM                   | Nebius + HuggingFace  |
| TTS (voice)           | Google Cloud TTS      |
| Audio & playback      | SoundDevice, Pydub    |

---

## 9. 🚧 Limites Actuelles

- L’émotion détectée est statique (“neutre”) → à améliorer
- Le TTS est bon mais manque encore de prosodie réaliste
- L’IA n’adapte pas encore son comportement au ton de l’escroc
- Aucun historique ou contexte sauvegardé sur le long terme

---

## 10. 🔮 Axes d’Amélioration

- Ajouter un vrai modèle de détection émotionnelle
- Génération TTS avec SSML (plus expressif)
- Adapter la durée et le ton des réponses à l’intonation de l’escroc
- Simulation 100 % vocale en WebRTC (streaming direct)
- Gestion d’un scénario évolutif / profil adaptatif

---

## 11. 👥 Membres du Projet

- Eckson GLITHO

---

## 12. 📎 Annexes

- `anti_scam.py` : logique IA, prompt, génération et audio
- `webrtc.py` : serveur Flask + gestion WebSocket
- `index.html` : interface utilisateur
- `private/` : à créer manuellement pour stocker vos clés API
- `cache/` : généré automatiquement pour stocker l’audio temporaire

---

## 13. 🛡️ Avertissement Éthique

Ce projet est purement pédagogique. Il a pour but de :

- Sensibiliser aux méthodes des arnaques
- Explorer les capacités d’une IA dans un contexte social

Il **ne doit en aucun cas être utilisé à des fins malveillantes**.