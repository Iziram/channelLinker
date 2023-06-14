import sqlite3
import os

def create_connection():
    conn = sqlite3.connect(os.getenv("DB_URL"))
    return conn


def create_tables(conn):
    c = conn.cursor()
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS servers (
        label TEXT PRIMARY KEY,
        guild_id INTEGER NOT NULL,
        channel_id INTEGER UNIQUE NOT NULL
    )
    """
    )
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS link (
        id_servA TEXT,
        id_servB TEXT,
        FOREIGN KEY (id_servA) REFERENCES servers (label) ON DELETE CASCADE,
        FOREIGN KEY (id_servB) REFERENCES servers (label) ON DELETE CASCADE,
        PRIMARY KEY (id_servA,id_servB)
    )
    """
    )

    c.execute(
        """
    CREATE TABLE IF NOT EXISTS banned (
        discord_id TEXT PRIMARY KEY
    )
    """
    )
    conn.commit()


def register_server(conn, guild_id, label, channel_id, mention="mention"):
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO servers (label, guild_id, channel_id, mention) VALUES (?, ?, ?, ?)",
            (label, guild_id, channel_id, mention),
        )
        conn.commit()
        return 0
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint" in str(e):
            if "guild_id" in str(e):
                return 1
            elif "label" in str(e):
                return 2
        return 3


def unregister_server(conn, label):
    c = conn.cursor()
    c.execute("DELETE FROM servers WHERE label=?", (label,))
    c.execute("DELETE FROM link where id_servA=? or id_servB=?", (label, label))
    conn.commit()


def get_server_label(conn, channel_id):
    c = conn.cursor()
    c.execute("SELECT label FROM servers WHERE channel_id=?", (channel_id,))
    row = c.fetchone()
    if row:
        return row[0]
    return None


def get_servers_labels(conn):
    c = conn.cursor()
    c.execute("SELECT label from servers order by label;")
    row = c.fetchall()
    if row:
        return (s[0] for s in row)
    return ()


def link_servers(conn, label_A, label_B):
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO link (id_servA, id_servB) VALUES (?, ?)", (label_A, label_B)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def unlink_servers(conn, label_A, label_B):
    c = conn.cursor()
    c.execute(
        "DELETE FROM link WHERE (id_servA=? AND id_servB=?) OR (id_servA=? AND id_servB=?)",
        (label_A, label_B, label_B, label_A),
    )
    conn.commit()


def get_linked_labels(conn, label):
    c = conn.cursor()
    c.execute(
        "SELECT id_servA, id_servB FROM link WHERE id_servA=? OR id_servB=?",
        (label, label),
    )
    rows = c.fetchall()
    linked_labels = []
    for row in rows:
        linked_labels.append(row[0] if row[1] == label else row[1])
    return linked_labels


def get_channel_from_label(conn, label):
    c = conn.cursor()
    c.execute("SELECT guild_id, channel_id FROM servers WHERE label=?", (label,))
    row = c.fetchone()
    if row:
        return row[0], row[1]
    return None


def get_mention(conn, label):
    c = conn.cursor()
    c.execute("select mention from servers where label=?;", (label,))
    row = c.fetchone()
    if row:
        return row[0]
    return None


def set_mention(conn, label, mention):
    c = conn.cursor()
    c.execute(
        "UPDATE servers set mention=? where label=?;",
        (
            mention,
            label,
        ),
    )
    conn.commit()

def is_banned(conn, discord_id):
    c = conn.cursor()
    c.execute("select discord_id from banned where discord_id=?;", (discord_id,))
    row = c.fetchone()
    if row:
        return True
    return False

def ban(conn, discord_id):
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO banned (discord_id) VALUES (?)", (discord_id,)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def unban(conn, discord_id):
    c = conn.cursor()
    c.execute(
        "DELETE FROM banned WHERE discord_id=?",
        (discord_id,),
    )
    conn.commit()