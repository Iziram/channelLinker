import os
import discord
from discord.ext import commands
from discord import app_commands
from discord.enums import Enum
from dotenv import load_dotenv
from database import *

# Charger le token depuis le fichier .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Créer la base de données SQLite
conn = create_connection()
create_tables(conn)


class Linker(app_commands.Group):
    ...


linker = Linker(name="linker")


@bot.event
async def on_message(message: discord.Message):
    # Ignore les messages du bot lui-même
    if message.author == bot.user or is_banned(conn, message.author.id):
        return

    channel_id = message.channel.id
    current_label = get_server_label(conn, channel_id)

    if current_label:
        linked_labels = get_linked_labels(conn, current_label)

        for label in linked_labels:
            guild_id, linked_channel_id = get_channel_from_label(conn, label)
            if guild_id and linked_channel_id:
                target_guild = bot.get_guild(guild_id)
                if target_guild:
                    target_channel = target_guild.get_channel(linked_channel_id)
                    if target_channel:
                        mention = get_mention(conn, label)
                        content = f"{message.author.mention}: {message.content}" if mention == "mention" else f"**{str(message.author)}** : {message.content}"
                        
                        # Créer une liste des fichiers joints
                        attachments = [await attachment.to_file() for attachment in message.attachments]
                        
                        # Envoyer le message et les fichiers joints
                        await target_channel.send(content=content, files=attachments)


@bot.event
async def on_ready():
    print(f"{bot.user} est connecté !")
    try:
        bot.tree.add_command(linker)
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)


async def check_linker_manager_role(interaction: discord.Interaction):
    if not any(role.name == "LinkerManager" for role in interaction.user.roles):
        await interaction.response.send_message(
            "Vous n'avez pas la permission d'exécuter cette commande.", ephemeral=True
        )
        return False
    return True


@linker.command(
    name="register",
    description="Enregistre le channel où la commande est exécutée dans la base de données avec un label unique.",
)
@app_commands.describe(label="Nom qui sera utilisé pour lier les channels")
@app_commands.choices(
    choices=[
        app_commands.Choice(name="Mention", value="mention"),
        app_commands.Choice(name="Tag", value="tag"),
    ]
)
async def register(
    interaction: discord.Interaction, label: str, choices: app_commands.Choice[str]
):
    if not await check_linker_manager_role(interaction):
        return

    error_code = register_server(
        conn, interaction.guild.id, label, interaction.channel.id, choices.value
    )
    if error_code == 0:
        await interaction.response.send_message(
            f"Serveur enregistré avec succès. Label: {label}", ephemeral=True
        )
    elif error_code == 1:
        await interaction.response.send_message(
            "Le channel_id est déjà utilisé.", ephemeral=True
        )
    elif error_code == 2:
        await interaction.response.send_message(
            "Le label est déjà utilisé.", ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "Une erreur est survenue lors de l'enregistrement du serveur.",
            ephemeral=True,
        )


@linker.command(
    name="unregister",
    description="Supprime l'enregistrement du serveur et du channel actuel de la base de données.",
)
async def unregister(interaction: discord.Interaction):
    if not await check_linker_manager_role(interaction):
        return

    label = get_server_label(conn, interaction.channel.id)
    if label:
        unregister_server(conn, label)
        await interaction.response.send_message(
            f"Serveur avec le label {label} retiré.", ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "Ce channel n'est pas enregistré.", ephemeral=True
        )


@linker.command(
    name="view",
    description="Affiche le label du channel enregistré, s'il existe, sinon affiche un message d'information.",
)
async def view(interaction: discord.Interaction):
    if not await check_linker_manager_role(interaction):
        return

    label = get_server_label(conn, interaction.channel.id)
    if label:
        await interaction.response.send_message(
            f"Le label de ce channel est : {label}", ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "Ce channel n'est pas enregistré.", ephemeral=True
        )


@linker.command(
    name="links",
    description="Affiche les channels liés au channel courant, s'il existe, sinon affiche un message d'information.",
)
async def links(interaction: discord.Interaction):
    if not await check_linker_manager_role(interaction):
        return

    label = get_server_label(conn, interaction.channel.id)
    if label:
        linked = get_linked_labels(conn, label)
        linked = "\n - ".join(linked)
        await interaction.response.send_message(
            f"Ce channel est lié à : {linked}", ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "Ce channel n'est pas enregistré.", ephemeral=True
        )


@linker.command(
    name="link",
    description="Lie le serveur actuel au serveur cible identifié par le label donné.",
)
@app_commands.describe(target_label="Nom du channel à lier")
async def link(interaction: discord.Interaction, target_label: str):
    if not await check_linker_manager_role(interaction):
        return

    current_label = get_server_label(conn, interaction.channel.id)
    if current_label:
        if target_label == current_label:
            await interaction.response.send_message(
                f"Vous ne pouvez pas lier votre channel à votre propre channel",
                ephemeral=True,
            )
        elif target_label in get_servers_labels(conn):
            success = link_servers(conn, current_label, target_label)
            if success:
                await interaction.response.send_message(
                    f"Channels liés avec succès: {current_label} et {target_label}",
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    "Une erreur est survenue lors de la liaison des channels.",
                    ephemeral=True,
                )
        else:
            await interaction.response.send_message(
                f"Le channel {target_label} n'existe pas.", ephemeral=True
            )
    else:
        await interaction.response.send_message(
            "Le serveur courant n'est pas enregistré.", ephemeral=True
        )


@linker.command(
    name="unlink",
    description="Supprime le lien entre le serveur actuel et le serveur cible identifié par le label donné.",
)
@app_commands.describe(target_label="Nom du channel à délier")
async def unlink(interaction: discord.Interaction, target_label: str):
    if not await check_linker_manager_role(interaction):
        return

    current_label = get_server_label(conn, interaction.channel.id)
    if current_label:
        if target_label in get_servers_labels(conn):
            unlink_servers(conn, current_label, target_label)
            await interaction.response.send_message(
                f"Channels déliés: {current_label} et {target_label}", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"Le label {target_label} n'existe pas.", ephemeral=True
            )
    else:
        await interaction.response.send_message(
            "Le channel courant n'est pas enregistré.", ephemeral=True
        )


@linker.command(
    name="mention",
    description="Défini le type d'affichage des messages dans le channel commun",
)
@app_commands.choices(
    choices=[
        app_commands.Choice(name="Mention", value="mention"),
        app_commands.Choice(name="Tag", value="tag"),
    ]
)
async def register(interaction: discord.Interaction, choices: app_commands.Choice[str]):
    if not await check_linker_manager_role(interaction):
        return

    current_label = get_server_label(conn, interaction.channel.id)
    if current_label:
        mention = choices.value
        set_mention(conn, current_label, mention)
        await interaction.response.send_message(
            f"L'affichage est désormais en {choices.name}", ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "Le channel courant n'est pas enregistré.", ephemeral=True
        )


bot.run(TOKEN)
