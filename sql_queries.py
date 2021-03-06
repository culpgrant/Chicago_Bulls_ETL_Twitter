"""
This is script that creates the functions to be used by the main file.
Provides Queries for the Daily Stats, Weekly, and Emoji's.
"""
import json
import psycopg2

# Postgresql Connection
with open(r"/Users/GrantCulp/Desktop/Python/credentials_python_info.txt") as f:
    data = json.loads(f.read())
    post_host = data['aws']['rds_post']['host']
    post_port = data['aws']['rds_post']['port']
    post_user = data['aws']['rds_post']['user']
    post_password = data['aws']['rds_post']['password']
    post_database = data['aws']['rds_post']['database']

connection = psycopg2.connect(
    host=post_host,
    port=post_port,
    user=post_user,
    password=post_password,
    database=post_database,
)
cursor = connection.cursor()


# Most Recent Game Played
def game_date_yest_query():
    """
    Date of most recent game played
    :return: Date
    """
    cursor.execute("""
    SELECT MAX(game_date) FROM bullsboxscore;""")
    last_game_date = cursor.fetchone()[0]
    return last_game_date


# Daily Record (Last Game)
def daily_record_query():
    """
    Win loss of the last game in the table
    :return: String and Emoji
    """
    cursor.callproc('public.func_record_daily')
    win_count = cursor.fetchone()[3]
    if win_count > 0:
        return "Win", "\U0001F525"
    return "Loss", "\U0001F44E"


# Daily Stat Query Function
def daily_stat_leader_query(sql_query, player_id_loc, player_name_loc, stat_loc):
    """
    Function that is used to get the information for the daily stats
    :param sql_query: STR -> Function to execute
    :param player_id_loc: INT -> Col location of player_id
    :param player_name_loc: INT -> Col location of player_name
    :param stat_loc: INT -> Col location of stat
    :return: player_id, player_name, player_stat
    """
    cursor.callproc(sql_query)
    sql_return_data = cursor.fetchone()
    player_id = sql_return_data[player_id_loc]
    player_last_name = sql_return_data[player_name_loc].split()[1]
    player_stat = sql_return_data[stat_loc]
    player_stat = round(player_stat, 1)
    return player_id, player_last_name, player_stat


# Weekly Stat Query Functions
def weekly_stat_leader_query(sql_query, player_id_loc, player_name_loc, stat_loc):
    """
    Function that is used to get the information for the weekly stats
    :param sql_query: STR -> Function to execute
    :param player_id_loc: INT -> Col location of player_id
    :param player_name_loc: INT -> Col location of player_name
    :param stat_loc: INT -> Col location of stat
    :return: player_id, player_name, player_stat
    """
    cursor.callproc(sql_query)
    sql_return_data = cursor.fetchone()
    player_id = sql_return_data[player_id_loc]
    player_last_name = sql_return_data[player_name_loc].split()[1]
    player_stat = sql_return_data[stat_loc]
    player_stat = round(player_stat, 1)
    return player_id, player_last_name, player_stat


# Dictionary Stats Query Functions: Season
def dict_stat_query(sql_query, sql_season, player_id_loc, stat_loc):
    """
    Function that returns a dict of player_id and their season average
    for the stat.
    :param sql_query: Query for the Function (postgres)
    :param sql_season: Parameter for SQL Function
    :param player_id_loc: Location in the result of Player Id
    :param stat_loc: Location of the stat in question
    :return: Dict of Player_ID, Stat
    """
    player_data_dict = {}
    cursor.callproc(sql_query, [sql_season])
    sql_data_list = cursor.fetchall()
    for player_data in sql_data_list:
        player_data_dict[player_data[player_id_loc]] = float(player_data[stat_loc])
    return player_data_dict


# Season Record Query Functions:
def season_record_query(sql_season):
    """
    Function to get the bulls record for any season
    :param sql_season: String
    :return: total games played, won, loss and an emoji (str)
    """
    cursor.callproc('public.func_record_season', [sql_season])
    total_record = cursor.fetchone()
    total_gp = total_record[0]
    total_wins = total_record[1]
    total_loss = total_record[2]
    if total_wins >= total_loss:
        # Good Emoji
        record_emoji = '\U0001F601'
    else:
        # Bad Emoji
        record_emoji = '\U0001F92E'
    return total_gp, total_wins, total_loss, record_emoji


# Emoji Query Regular
def emoji_standard_query(player_id, stat, stat_dict):
    """
    Function that compares the daily/weekly stat to the overall
        stat's to determine if it is better or worse.
    :return:
    """
    season_avg = stat_dict[player_id]
    if stat >= season_avg:
        # Trending Up
        emoji = "\U0001F4C8"
    else:
        # Trending Down
        emoji = "\U0001F4C9"
    return emoji


# Emoji Query Reversed
def emoji_reversed_query(player_id, stat, stat_dict):
    """
    Function that compares the daily/weekly stat to the overall
        stat's to determine if it is better or worse.
    :return:
    """
    season_avg = stat_dict[player_id]
    if stat >= season_avg:
        # Trending Down
        emoji = "\U0001F4C9"
    else:
        # Trending Up
        emoji = "\U0001F4C8"
    return emoji


# Weekly Tweet - Dates
def weekly_dates_tweet():
    """
    Function to get the date seven days ago and current date
    :return: Earlier Date (Seven Days Ago), Second Date (Current)
    """
    cursor.execute("SELECT date(current_date - INTERVAL '7 days')AS seven_days_ago,CURRENT_DATE;")
    dates = cursor.fetchall()
    first_date = dates[0][0]
    second_date = dates[0][1]
    return first_date, second_date


# Record For Last 7 Days
def weekly_record():
    """
    Function that returns the record for the last 7 days
    :return: Int, Text
    """
    cursor.callproc('func_record_weekly')
    record = cursor.fetchall()
    games_played = record[0][0]
    wins = record[0][1]
    loss = record[0][2]
    if wins >= loss:
        # Happy Face
        emoji = '\U0001F601'
    else:
        # Bad Emoji
        emoji = '\U0001F92E'
    return games_played, wins, loss, emoji


# Season Daily Dictionary
def season_daily_stats(sql_query, sql_season, player_id_loc, player_name_loc, stat_loc):
    """
    This is the function for the Daily Season Stats Tweets that calls a SQL query
    and returns a list of the data for easier processing
    :param sql_query: str
    :param sql_season: str
    :param player_id_loc: int
    :param player_name_loc: int
    :param stat_loc: int
    :return: List of the data
    """
    player_data_list = []
    cursor.callproc(sql_query, [sql_season])
    sql_data_list = cursor.fetchall()
    for player_data in sql_data_list:
        id = player_data[player_id_loc]
        name = player_data[player_name_loc]
        stat = round(float(player_data[stat_loc]), 1)
        dict_element = dict(player_id=id, player_name=name,
                            player_stat=stat)
        player_data_list.append(dict_element)
    return player_data_list
