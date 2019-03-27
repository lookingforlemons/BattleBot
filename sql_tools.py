import os
import sqlite3

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')


def db_connect(db_path=DEFAULT_PATH):
    con = sqlite3.connect(db_path)
    return con


def create_contestant(con, discord, name, score, speed):
    sql = """
        INSERT INTO contestants (discord_id, discord_name, player_score, player_speed)
        VALUES (?, ?, ?, ?)"""
    cur = con.cursor()
    cur.execute(sql, (discord, name, score, speed))
    return cur.lastrowid


def get_current_score(con, name):
    sql = """
        SELECT player_score FROM contestants WHERE discord_name LIKE "%s"
        """ % name
    cur = con.cursor()
    cur.execute(sql)
    result = cur.fetchone()
    if result is None:
        return 0
    else:
        return result[0]


def update_score(con, name, score):
    sql = "UPDATE contestants SET player_score = %d WHERE discord_name LIKE '%s'" % (score, name)
    cur = con.cursor()
    cur.execute(sql)
    return cur.lastrowid


def get_all_scores(con):
    sql = "SELECT discord_name, player_score FROM contestants ORDER BY player_score DESC"
    cur = con.cursor()
    cur.execute(sql)
    return cur


def get_discord_id(con, name):
    sql = "SELECT discord_id FROM contestants WHERE discord_name LIKE '%s'" % name
    cur = con.cursor()
    cur.execute(sql)
    result = cur.fetchone()
    if result is None:
        return 0
    else:
        return result



