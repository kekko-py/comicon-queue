import sqlite3
import mysql.connector
from datetime import datetime

# Configurazione database
SQLITE_DB_PATH = 'stand_db.db'
ARUBA_DB_CONFIG = {
    'host': 'localhost',  # Qui dobbiamo inserire le credenziali di aruba MySQL per salvarlo li sopra
    'user': 'root',
    'password': '',
    'database': 'stand_db'
}


def sync_table(table_name):
    try:
        # Connessione a SQLite
        sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
        sqlite_cursor = sqlite_conn.cursor()

        # Connessione a MySQL (Aruba)
        aruba_conn = mysql.connector.connect(**ARUBA_DB_CONFIG)
        aruba_cursor = aruba_conn.cursor()

        # Leggi dati da SQLite
        sqlite_cursor.execute(f"SELECT player_type, player_id, player_name, arrival_time FROM {table_name}")
        rows = sqlite_cursor.fetchall()

        aruba_cursor.execute("DELETE FROM queues")

        # Sincronizza con Aruba
        for player_type, player_id, player_name, arrival_time in rows:
            aruba_cursor.execute(
                f"INSERT INTO {table_name} (player_type, player_id, player_name, arrival_time) "
                "VALUES (%s ,%s, %s, %s) ON DUPLICATE KEY UPDATE "
                "player_name = VALUES(player_name), arrival_time = VALUES(arrival_time)",
                (player_type, player_id, player_name, arrival_time)
            )

        aruba_conn.commit()
        aruba_conn.close()
        sqlite_conn.close()
    except Exception as e:
        print(f"Errore durante la sincronizzazione di {table_name}: {e}")


def sync_scoring_table():
    try:
        # Connessione a SQLite
        sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
        sqlite_cursor = sqlite_conn.cursor()

        # Connessione a MySQL (Aruba)
        aruba_conn = mysql.connector.connect(**ARUBA_DB_CONFIG)
        aruba_cursor = aruba_conn.cursor()

        # Leggi dati da SQLite
        sqlite_cursor.execute("SELECT player_type, player_id, player_name, score FROM scoring")
        rows = sqlite_cursor.fetchall()

        # Sincronizza con Aruba
        aruba_cursor.execute("DELETE FROM scoring")

        for player_type, player_id, player_name, score in rows:
            aruba_cursor.execute(
                "INSERT INTO scoring (player_type, player_id, player_name, score) "
                "VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE "
                "player_name = VALUES(player_name), score = VALUES(score)",
                (player_type, player_id, player_name, score)
            )

        aruba_conn.commit()
        aruba_conn.close()
        sqlite_conn.close()
    except Exception as e:
        print(f"Errore durante la sincronizzazione della tabella scoring: {e}")

def sync_skipped_table():
    try:
        # Connessione a SQLite
        sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
        sqlite_cursor = sqlite_conn.cursor()

        # Connessione a MySQL (Aruba)
        aruba_conn = mysql.connector.connect(**ARUBA_DB_CONFIG)
        aruba_cursor = aruba_conn.cursor()

        # Leggi dati da SQLite
        sqlite_cursor.execute("SELECT player_type, player_id, player_name, skipped_at FROM skipped_players")
        rows = sqlite_cursor.fetchall()

        # Sincronizza con Aruba
        aruba_cursor.execute("DELETE FROM skipped_players")
        
        for player_type, player_id, player_name, skipped_at in rows:
            aruba_cursor.execute(
                "INSERT INTO skipped_players (player_type, player_id, player_name, skipped_at) "
                "VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE "
                "player_name = VALUES(player_name), skipped_at = VALUES(skipped_at)",
                (player_type, player_id, player_name, skipped_at)
            )

        aruba_conn.commit()
        aruba_conn.close()
        sqlite_conn.close()
    except Exception as e:
        print(f"Errore durante la sincronizzazione della tabella skipped_players: {e}")


if __name__ == '__main__':
    sync_table('queues')
    sync_scoring_table()
    sync_skipped_table()