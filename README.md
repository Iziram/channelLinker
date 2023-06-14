# Channel Linker

## Description du projet

ChannelLinker est un bot Discord qui permet de lier des channels de différents serveurs. Les messages envoyés dans un channel lié sont automatiquement transférés aux autres channels liés.
Permissions nécessaires :

Pour utiliser les commandes de ChannelLinker, un utilisateur doit avoir le rôle LinkerManager. Les administrateurs du serveur devront créer ce rôle et l'attribuer aux utilisateurs autorisés.
Commandes :

- `/linker register <label> [mention | tag]`: Enregistre le serveur et le channel où la commande est exécutée dans la base de données avec un label unique. (Choix du type de mention [@user | user#1234])
- `/linker unregister` : Supprime l'enregistrement du serveur et du channel actuel de la base de données.
- `/linker mention [mention | tag]` : Modifie le choix de mention dans le channel actuel
- `/linker view`: Affiche le label du channel enregistré, s'il existe, sinon affiche un message d'information.
- `/linker link <target_label>` : Lie le serveur actuel au serveur cible identifié par le label donné.
- `/linker unlink <target_label>` : Supprime le lien entre le serveur actuel et le serveur cible identifié par le label donné.
- `/linker links` : Affiche les channels liés au channel courant, s'il existe, sinon affiche un message d'information.

## Exemple d'utilisation

Enregistrez le channel actuel avec le label "ServeurA_Channel1" :

`/linker register ServeurA_Channel1 mention`

Liez le channel actuel à un autre channel enregistré avec le label "ServeurB_Channel1" :

`/linker link ServeurB_Channel1`

Les messages envoyés dans le channel actuel seront désormais automatiquement transférés au channel lié "ServeurB_Channel1" et vice versa.

## Tutoriel de mise en place

1. Invitez le bot ChannelLinker sur votre serveur en utilisant le  lien d'invitation .
2. Créez un rôle "LinkerManager" sur votre serveur et attribuez-le aux utilisateurs qui doivent être autorisés à utiliser les commandes du bot.
3. Utilisez la commande `/linker register <label>` mention dans le channel que vous souhaitez enregistrer. Le label doit être unique parmi tous les serveurs qui utilisent le bot ChannelLinker.
Répétez l'étape 3 sur un autre serveur et un autre channel que vous souhaitez lier.
4. Utilisez la commande /linker link `<target_label>` pour lier les channels. Remplacez `<target_label>` par le label du serveur cible.
5. Les channels sont maintenant liés, et les messages seront automatiquement transférés entre eux. Vous pouvez utiliser la commande `/linker unlink <target_label>` pour supprimer le lien entre les channels si nécessaire.
6. Pour supprimer l'enregistrement d'un serveur et d'un channel, utilisez la commande `/linker unregister` .

## Installation (Développement / Production)

Pour installer le bot sur un serveur / en local, il faut suivre les étapes suivantes :

1. Cloner ce répo dans le dossier de votre choix
2. à l'interieur du dossier "ChannelLinker", ajouter un fichier `.env`:

   ```console
    DISCORD_TOKEN= #le token de votre bot discord
    DB_URL="" #l'url absolu vers le fichier de base de donnée (sera créé si le fichier n'existe pas)
   ```

3. Créer un environement virtuel avec python :
   1. `python3 -m pip install python-venv`
   2. `python3 -m venv venv`
4. Installer l'environement du bot
   1. `source venv/bin/activate`
   2. `pip install -r requirements.txt`
5. Lancer le bot
   1. `python channelLinker.py`
