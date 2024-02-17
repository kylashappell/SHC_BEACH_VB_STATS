# don't delete or edit this section
from flask import Flask, g,  render_template, redirect, session, url_for, request
import sqlite3

app = Flask(__name__)

app.config['SECRET_KEY'] = 'icdattCwsmP413'

#----------------------------------
# this section is for setting up and connecting my SQLite database

# Get the directory of the current script file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the database file path
DATABASE = os.path.join(current_dir, 'SHC_Beach_VB_Stats.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


#----------------------------------
# This section is for adding/editing tables in the database based on user input/clicks


# Define a function to retrieve the game name based on the game_id
def get_game_name(game_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT OPPONENT FROM GAME WHERE GAME_ID = ?", (game_id,))
    game_name = cursor.fetchone()[0]
    db.close()
    return game_name


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/what-do-you-want-to-do')
def what_do_you_want_to_do():
    return render_template('what-do-you-want-to-do.html')


# Define route for stats-taking page
@app.route('/stats-taking/<game_id>/<pair_number>/<game_id_actual>/<set_number>/<set_number_id>/<player_name>/<player_id>', methods=['GET', 'POST'])
def stats_taking(game_id, pair_number, game_id_actual, set_number, set_number_id, player_name, player_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
                   SELECT COUNT(*) AS POINTS
                        , SCORING_TEAM
                   FROM POINT
                   WHERE GAME_ID = {}
                     AND SET_NUMBER = {}
                     AND PAIR_NUMBER = {}
                     AND PLAYER_ID = {}
                   GROUP BY SCORING_TEAM
                   """.format(game_id_actual, set_number, pair_number, player_id))
    rows = cursor.fetchall()
    shc_points = 0
    opp_points = 0
    for row in rows:
        # Check the scoring team and update the corresponding variable
        if row[1] == 'SHC':  # Assuming SCORING_TEAM is the second column in the query result
            shc_points = row[0]  # Assuming POINTS is the first column in the query result
        else:
            opp_points = row[0]  # Assuming POINTS is the first column in the query result
    if set_number != '3':
        print(set_number)
        if (shc_points + opp_points) % 7 == 0 and (shc_points + opp_points) != 0:
            cursor.execute("INSERT INTO BREAK (GAME_ID, SET_NUMBER, PAIR_NUMBER, BREAK_TYPE, SHC_SCORE, OPPONENT_SCORE, WIND, CALLED_BY) VALUES (?, ?, ?, ?, ?, ?, ?, NULL)",
                           (game_id_actual, set_number, pair_number, 'SIDE SWITCH', shc_points, opp_points, 'ph'))
    if set_number == '3':
        print(set_number)
        if (shc_points + opp_points) % 5 == 0 and (shc_points + opp_points) != 0:
            cursor.execute("INSERT INTO BREAK (GAME_ID, SET_NUMBER, PAIR_NUMBER, BREAK_TYPE, SHC_SCORE, OPPONENT_SCORE, WIND, CALLED_BY) VALUES (?, ?, ?, ?, ?, ?, ?, NULL)",
                           (game_id_actual, set_number, pair_number, 'SIDE SWITCH', shc_points, opp_points, 'ph'))
    if request.method == 'POST':
        # Check if the SERVE button was clicked
        if 'SERVE' in request.form:
            # Insert new row into SERVE table in the database
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO SERVE (GAME_ID, SET_NUMBER, PLAYER_ID, SERVE_TYPE, RESULT, LOCATION, ERROR_TYPE) VALUES (?, ?, ?, ?, ?, NULL, NULL)",
                           (game_id_actual, set_number, player_id, 'ph', 'ph'))
            db.commit()
            # Retrieve the last inserted row's SERVE_ID
            cursor.execute("SELECT last_insert_rowid()")
            serve_id = cursor.fetchone()[0]
            return redirect(url_for('serve_type', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, serve_id=serve_id))  # Redirect to webpage.html
            # Check if the RECEIVE button was clicked
        elif 'RECEIVE' in request.form:
            # Insert new row into RECEIVE table in the database
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO RECEIVE (GAME_ID, SET_NUMBER, PLAYER_ID, RECEIVE_TYPE, RESULT) VALUES (?, ?, ?, ?, ?)",
                           (game_id_actual, set_number, player_id, 'ph', 'ph'))
            db.commit()
            # Retrieve the last inserted row's RECEIVE_ID
            cursor.execute("SELECT last_insert_rowid()")
            receive_id = cursor.fetchone()[0]
            return redirect(url_for('receive_side', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, receive_id=receive_id))  # Redirect to webpage.html
        elif 'DIG' in request.form:
            # Insert new row into DIG table in the database
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO DIG (GAME_ID, SET_NUMBER, PLAYER_ID, DIG_TYPE, RESULT) VALUES (?, ?, ?, ?, ?)",
                           (game_id_actual, set_number, player_id, 'ph', 'ph'))
            db.commit()
            # Retrieve the last inserted row's DIG_ID
            cursor.execute("SELECT last_insert_rowid()")
            dig_id = cursor.fetchone()[0]
            return redirect(url_for('dig_type', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, dig_id=dig_id))  # Redirect to webpage.html
        elif 'SET' in request.form:
            # Insert new row into SET table in the database
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO SETTING (GAME_ID, SET_NUMBER, PLAYER_ID, SETTING_TYPE, RESULT, ERROR_TYPE) VALUES (?, ?, ?, ?, ?, NULL)",
                           (game_id_actual, set_number, player_id, 'ph', 'ph'))
            db.commit()
            # Retrieve the last inserted row's SETTING_ID
            cursor.execute("SELECT last_insert_rowid()")
            setting_id = cursor.fetchone()[0]
            return redirect(url_for('set_type', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, setting_id=setting_id))  # Redirect to webpage.html
        elif 'ATTACK' in request.form:
            # Insert new row into ATTACK table in the database
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO ATTACK (GAME_ID, SET_NUMBER, PLAYER_ID, ATTACK_TYPE, RESULT, ERROR_TYPE) VALUES (?, ?, ?, ?, ?, NULL)",
                           (game_id_actual, set_number, player_id, 'ph', 'ph'))
            db.commit()
            # Retrieve the last inserted row's ATTACK_ID
            cursor.execute("SELECT last_insert_rowid()")
            attack_id = cursor.fetchone()[0]
            return redirect(url_for('attack_type', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, attack_id=attack_id))  # Redirect to webpage.html
        elif 'BLOCK' in request.form:
            # Insert new row into BLOCK table in the database
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO BLOCK (GAME_ID, SET_NUMBER, PLAYER_ID, BLOCK_TYPE, RESULT) VALUES (?, ?, ?, ?, ?)",
                           (game_id_actual, set_number, player_id, 'ph', 'ph'))
            db.commit()
            # Retrieve the last inserted row's BLOCK_ID
            cursor.execute("SELECT last_insert_rowid()")
            block_id = cursor.fetchone()[0]
            return redirect(url_for('block_type', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, block_id=block_id))  # Redirect to webpage.html
        elif 'TIME-OUT' in request.form:
            # Insert new row into BLOCK table in the database
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO BREAK (GAME_ID, SET_NUMBER, PAIR_NUMBER, BREAK_TYPE, SHC_SCORE, OPPONENT_SCORE, WIND, CALLED_BY) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                           (game_id_actual, set_number, pair_number, 'timeout', 'ph', 'ph', 'ph', 'ph'))
            db.commit()
            # Retrieve the last inserted row's BREAK_ID
            cursor.execute("SELECT last_insert_rowid()")
            break_id = cursor.fetchone()[0]
            return redirect(url_for('who_called_time_out', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, break_id=break_id))  # Redirect to webpage.html
        elif 'SET FINISHED' in request.form:
            return redirect(url_for('end_info', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id))  # Redirect to webpage.html
    return render_template('stats-taking.html', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, shc_points=shc_points, opp_points=opp_points)


# Define route for end-info page
@app.route('/end-info/<game_id>/<pair_number>/<game_id_actual>/<set_number>/<set_number_id>/<player_name>/<player_id>', methods=['GET', 'POST'])
def end_info(game_id, pair_number, game_id_actual, set_number, set_number_id, player_name, player_id):
    if request.method == 'POST':
        # Retrieve values from the form submitted by the user
        shc_score = request.form['shc_score']  # Assuming 'date' is the name of the input box for serve type
        opponent_score = request.form['opponent_score']
        set_winner = request.form['set_winner']
        match_winner = request.form['match_winner']
        end_time = request.form['end_time']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE SET_INFO SET SHC_SCORE=?, OPPONENT_SCORE=?, SET_WINNER=?, MATCH_WINNER=?, END_TIME=? WHERE SET_INFO_ID=?",
                       (shc_score, opponent_score, set_winner, match_winner, end_time, set_number_id))
        db.commit()
        return redirect(url_for('what_do_you_want_to_do'))  # Redirect to webpage.html
    return render_template('end-info.html', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id)


# Define route for serve-type page
@app.route('/serve-type/<game_id>/<pair_number>/<game_id_actual>/<set_number>/<set_number_id>/<player_name>/<player_id>/<serve_id>', methods=['GET', 'POST'])
def serve_type(game_id, pair_number, game_id_actual, set_number, set_number_id, player_name, player_id, serve_id):
    if request.method == 'POST':
        serve_kind = request.form.get('serve_type')
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE SERVE SET SERVE_TYPE=?, ERROR_TYPE=NULL WHERE SERVE_ID=?",
                       (serve_kind, serve_id))
        db.commit()
        return redirect(url_for('serve_result', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, serve_id=serve_id))  # Redirect to webpage.html
    return render_template('serve-type.html', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, serve_id=serve_id)


# Define route for serve-result page
@app.route('/serve-result/<game_id>/<pair_number>/<game_id_actual>/<set_number>/<set_number_id>/<player_name>/<player_id>/<serve_id>', methods=['GET', 'POST'])
def serve_result(game_id, pair_number, game_id_actual, set_number, set_number_id, player_name, player_id, serve_id):
    if request.method == 'POST':
        serve_result_ = request.form.get('serve_result')
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE SERVE SET RESULT=?, ERROR_TYPE=NULL WHERE SERVE_ID=?",
                       (serve_result_, serve_id))
        db.commit()
        if serve_result_ == 'ACE':
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO POINT (GAME_ID, SET_NUMBER, PAIR_NUMBER, PLAYER_ID, SCORING_TEAM) VALUES (?, ?, ?, ?, ?)",
                           (game_id_actual, set_number, pair_number, player_id, 'SHC'))
            db.commit()
            return redirect(url_for('serve_location', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, serve_id=serve_id))  # Redirect to webpage.html
        elif serve_result_ == 'ERROR':
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO POINT (GAME_ID, SET_NUMBER, PAIR_NUMBER, PLAYER_ID, SCORING_TEAM) VALUES (?, ?, ?, ?, ?)",
                           (game_id_actual, set_number, pair_number, player_id, 'OPPONENT'))
            db.commit()
            return redirect(url_for('serve_error_type', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, serve_id=serve_id))  # Redirect to webpage.html
        else:
            return redirect(url_for('serve_location', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, serve_id=serve_id))  # Redirect to webpage.html
    return render_template('serve-result.html', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, serve_id=serve_id)


# Define route for serve-location page
@app.route('/serve-location/<game_id>/<pair_number>/<game_id_actual>/<set_number>/<set_number_id>/<player_name>/<player_id>/<serve_id>', methods=['GET', 'POST'])
def serve_location(game_id, pair_number, game_id_actual, set_number, set_number_id, player_name, player_id, serve_id):
    if request.method == 'POST':
        serve_location_ = request.form.get('serve_location')
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE SERVE SET LOCATION=?, ERROR_TYPE=NULL WHERE SERVE_ID=?",
                       (serve_location_, serve_id))
        db.commit()
        return redirect(url_for('stats_taking', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id))  # Redirect to webpage.html
    return render_template('serve-location.html', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, serve_id=serve_id)


# Define route for serve-error-type page
@app.route('/serve-error-type/<game_id>/<pair_number>/<game_id_actual>/<set_number>/<set_number_id>/<player_name>/<player_id>/<serve_id>', methods=['GET', 'POST'])
def serve_error_type(game_id, pair_number, game_id_actual, set_number, set_number_id, player_name, player_id, serve_id):
    if request.method == 'POST':
        serve_error_ = request.form.get('serve_error')
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE SERVE SET LOCATION=NULL, ERROR_TYPE=? WHERE SERVE_ID=?",
                       (serve_error_, serve_id))
        db.commit()
        return redirect(url_for('stats_taking', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id))  # Redirect to webpage.html
    return render_template('serve-error-type.html', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, serve_id=serve_id)


# Define route for receive-side page
@app.route('/receive-side/<game_id>/<pair_number>/<game_id_actual>/<set_number>/<set_number_id>/<player_name>/<player_id>/<receive_id>', methods=['GET', 'POST'])
def receive_side(game_id, pair_number, game_id_actual, set_number, set_number_id, player_name, player_id, receive_id):
    if request.method == 'POST':
        receive_side_ = request.form.get('receive_side')
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE RECEIVE SET RECEIVE_TYPE=? WHERE RECEIVE_ID=?",
                       (receive_side_, receive_id))
        db.commit()
        return redirect(url_for('receive_result', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, receive_id=receive_id))  # Redirect to webpage.html
    return render_template('receive-side.html', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, receive_id=receive_id)


# Define route for receive-result page
@app.route('/receive-result/<game_id>/<pair_number>/<game_id_actual>/<set_number>/<set_number_id>/<player_name>/<player_id>/<receive_id>', methods=['GET', 'POST'])
def receive_result(game_id, pair_number, game_id_actual, set_number, set_number_id, player_name, player_id, receive_id):
    if request.method == 'POST':
        receive_result_ = request.form.get('receive_result')
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE RECEIVE SET RESULT=? WHERE RECEIVE_ID=?",
                       (receive_result_, receive_id))
        db.commit()
        if receive_result_ == 'ERROR':
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO POINT (GAME_ID, SET_NUMBER, PAIR_NUMBER, PLAYER_ID, SCORING_TEAM) VALUES (?, ?, ?, ?, ?)",
                           (game_id_actual, set_number, pair_number, player_id, 'OPPONENT'))
            db.commit()
            return redirect(url_for('stats_taking', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id))  # Redirect to webpage.html
        else:
            return redirect(url_for('stats_taking', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id))  # Redirect to webpage.html
    return render_template('receive-result.html', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, receive_id=receive_id)


# Define route for dig-type page
@app.route('/dig-type/<game_id>/<pair_number>/<game_id_actual>/<set_number>/<set_number_id>/<player_name>/<player_id>/<dig_id>', methods=['GET', 'POST'])
def dig_type(game_id, pair_number, game_id_actual, set_number, set_number_id, player_name, player_id, dig_id):
    if request.method == 'POST':
        dig_type_ = request.form.get('dig_type')
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE DIG SET DIG_TYPE=? WHERE DIG_ID=?",
                       (dig_type_, dig_id))
        db.commit()
        return redirect(url_for('dig_result', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, dig_id=dig_id))  # Redirect to webpage.html
    return render_template('dig-type.html', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, dig_id=dig_id)


# Define route for dig-result page
@app.route('/dig-result/<game_id>/<pair_number>/<game_id_actual>/<set_number>/<set_number_id>/<player_name>/<player_id>/<dig_id>', methods=['GET', 'POST'])
def dig_result(game_id, pair_number, game_id_actual, set_number, set_number_id, player_name, player_id, dig_id):
    if request.method == 'POST':
        dig_result_ = request.form.get('dig_result')
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE DIG SET RESULT=? WHERE DIG_ID=?",
                       (dig_result_, dig_id))
        db.commit()
        if dig_result_ == 'ERROR':
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO POINT (GAME_ID, SET_NUMBER, PAIR_NUMBER, PLAYER_ID, SCORING_TEAM) VALUES (?, ?, ?, ?, ?)",
                           (game_id_actual, set_number, pair_number, player_id, 'OPPONENT'))
            db.commit()
            return redirect(url_for('stats_taking', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id))  # Redirect to webpage.html
        else:
            return redirect(url_for('stats_taking', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id))
    return render_template('dig-result.html', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, dig_id=dig_id)


# Define route for set-type page
@app.route('/set-type/<game_id>/<pair_number>/<game_id_actual>/<set_number>/<set_number_id>/<player_name>/<player_id>/<setting_id>', methods=['GET', 'POST'])
def set_type(game_id, pair_number, game_id_actual, set_number, set_number_id, player_name, player_id, setting_id):
    if request.method == 'POST':
        setting_type = request.form.get('setting_type')
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE SETTING SET SETTING_TYPE=?, ERROR_TYPE=NULL WHERE SET_ID=?",
                       (setting_type, setting_id))
        db.commit()
        return redirect(url_for('set_result', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, setting_id=setting_id))  # Redirect to webpage.html
    return render_template('set-type.html', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, setting_id=setting_id)


# Define route for set-result page
@app.route('/set-result/<game_id>/<pair_number>/<game_id_actual>/<set_number>/<set_number_id>/<player_name>/<player_id>/<setting_id>', methods=['GET', 'POST'])
def set_result(game_id, pair_number, game_id_actual, set_number, set_number_id, player_name, player_id, setting_id):
    if request.method == 'POST':
        setting_result_ = request.form.get('set_result')
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE SETTING SET RESULT=?, ERROR_TYPE=NULL WHERE SET_ID=?",
                       (setting_result_, setting_id))
        db.commit()
        if setting_result_ == 'ASSIST':
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO POINT (GAME_ID, SET_NUMBER, PAIR_NUMBER, PLAYER_ID, SCORING_TEAM) VALUES (?, ?, ?, ?, ?)",
                           (game_id_actual, set_number, pair_number, player_id, 'SHC'))
            db.commit()
            return redirect(url_for('stats_taking', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id))  # Redirect to webpage.html
        elif setting_result_ == 'ERROR':
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO POINT (GAME_ID, SET_NUMBER, PAIR_NUMBER, PLAYER_ID, SCORING_TEAM) VALUES (?, ?, ?, ?, ?)",
                           (game_id_actual, set_number, pair_number, player_id, 'OPPONENT'))
            db.commit()
            return redirect(url_for('set_error_type', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, setting_id=setting_id))  # Redirect to webpage.html
        else:
            return redirect(url_for('stats_taking', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id))
    return render_template('set-result.html', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, setting_id=setting_id)


# Define route for set-error-type page
@app.route('/set-error-type/<game_id>/<pair_number>/<game_id_actual>/<set_number>/<set_number_id>/<player_name>/<player_id>/<setting_id>', methods=['GET', 'POST'])
def set_error_type(game_id, pair_number, game_id_actual, set_number, set_number_id, player_name, player_id, setting_id):
    if request.method == 'POST':
        set_error_ = request.form.get('set_error')
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE SETTING SET ERROR_TYPE=? WHERE SET_ID=?",
                       (set_error_, setting_id))
        db.commit()
        return redirect(url_for('stats_taking', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id))  # Redirect to webpage.html
    return render_template('set-error-type.html', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, setting_id=setting_id)


# Define route for attack-type page
@app.route('/attack-type/<game_id>/<pair_number>/<game_id_actual>/<set_number>/<set_number_id>/<player_name>/<player_id>/<attack_id>', methods=['GET', 'POST'])
def attack_type(game_id, pair_number, game_id_actual, set_number, set_number_id, player_name, player_id, attack_id):
    if request.method == 'POST':
        attack_type_ = request.form.get('attack_type')
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE ATTACK SET ATTACK_TYPE=?, ERROR_TYPE=NULL WHERE ATTACK_ID=?",
                       (attack_type_, attack_id))
        db.commit()
        return redirect(url_for('attack_result', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, attack_id=attack_id))  # Redirect to webpage.html
    return render_template('attack-type.html', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, attack_id=attack_id)


# Define route for attack-result page
@app.route('/attack-result/<game_id>/<pair_number>/<game_id_actual>/<set_number>/<set_number_id>/<player_name>/<player_id>/<attack_id>', methods=['GET', 'POST'])
def attack_result(game_id, pair_number, game_id_actual, set_number, set_number_id, player_name, player_id, attack_id):
    if request.method == 'POST':
        attack_result_ = request.form.get('attack_result')
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE ATTACK SET RESULT=?, ERROR_TYPE=NULL WHERE ATTACK_ID=?",
                       (attack_result_, attack_id))
        db.commit()
        if attack_result_ == 'KILL':
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO POINT (GAME_ID, SET_NUMBER, PAIR_NUMBER, PLAYER_ID, SCORING_TEAM) VALUES (?, ?, ?, ?, ?)",
                           (game_id_actual, set_number, pair_number, player_id, 'SHC'))
            db.commit()
            return redirect(url_for('stats_taking', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id))  # Redirect to webpage.html
        elif attack_result_ == 'ERROR':
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO POINT (GAME_ID, SET_NUMBER, PAIR_NUMBER, PLAYER_ID, SCORING_TEAM) VALUES (?, ?, ?, ?, ?)",
                           (game_id_actual, set_number, pair_number, player_id, 'OPPONENT'))
            db.commit()
            return redirect(url_for('attack_error_type', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, attack_id=attack_id))  # Redirect to webpage.html
        else:
            return redirect(url_for('stats_taking', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id))  # Redirect to webpage.html
    return render_template('attack-result.html', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, attack_id=attack_id)


# Define route for attack-error-type page
@app.route('/attack-error-type/<game_id>/<pair_number>/<game_id_actual>/<set_number>/<set_number_id>/<player_name>/<player_id>/<attack_id>', methods=['GET', 'POST'])
def attack_error_type(game_id, pair_number, game_id_actual, set_number, set_number_id, player_name, player_id, attack_id):
    if request.method == 'POST':
        attack_error_ = request.form.get('attack_error')
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE ATTACK SET ERROR_TYPE=? WHERE ATTACK_ID=?",
                       (attack_error_, attack_id))
        db.commit()
        return redirect(url_for('stats_taking', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id))  # Redirect to webpage.html
    return render_template('attack-error-type.html', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, attack_id=attack_id)


# Define route for block-type page
@app.route('/block-type/<game_id>/<pair_number>/<game_id_actual>/<set_number>/<set_number_id>/<player_name>/<player_id>/<block_id>', methods=['GET', 'POST'])
def block_type(game_id, pair_number, game_id_actual, set_number, set_number_id, player_name, player_id, block_id):
    if request.method == 'POST':
        block_type_ = request.form.get('block_type')
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE BLOCK SET BLOCK_TYPE=? WHERE BLOCK_ID=?",
                       (block_type_, block_id))
        db.commit()
        return redirect(url_for('block_result', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, block_id=block_id))  # Redirect to webpage.html
    return render_template('block-type.html', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, block_id=block_id)


# Define route for block-result page
@app.route('/block-result/<game_id>/<pair_number>/<game_id_actual>/<set_number>/<set_number_id>/<player_name>/<player_id>/<block_id>', methods=['GET', 'POST'])
def block_result(game_id, pair_number, game_id_actual, set_number, set_number_id, player_name, player_id, block_id):
    if request.method == 'POST':
        block_result_ = request.form.get('block_result')
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE BLOCK SET RESULT=? WHERE block_ID=?",
                       (block_result_, block_id))
        db.commit()
        if block_result_ == 'POINT-ENDING':
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO POINT (GAME_ID, SET_NUMBER, PAIR_NUMBER, PLAYER_ID, SCORING_TEAM) VALUES (?, ?, ?, ?, ?)",
                           (game_id_actual, set_number, pair_number, player_id, 'SHC'))
            db.commit()
            return redirect(url_for('stats_taking', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id))  # Redirect to webpage.html
        elif block_result_ == 'ERROR':
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO POINT (GAME_ID, SET_NUMBER, PAIR_NUMBER, PLAYER_ID, SCORING_TEAM) VALUES (?, ?, ?, ?, ?)",
                           (game_id_actual, set_number, pair_number, player_id, 'OPPONENT'))
            db.commit()
            return redirect(url_for('stats_taking', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id))  # Redirect to webpage.html
        else:
            return redirect(url_for('stats_taking', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id))  # Redirect to webpage.html
    return render_template('block-result.html', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, block_id=block_id)


# Define route for who-called-time-out page
@app.route('/who-called-time-out/<game_id>/<pair_number>/<game_id_actual>/<set_number>/<set_number_id>/<player_name>/<player_id>/<break_id>', methods=['GET', 'POST'])
def who_called_time_out(game_id, pair_number, game_id_actual, set_number, set_number_id, player_name, player_id, break_id):
    if request.method == 'POST':
        # Retrieve values from the form submitted by the user
        who_called_to = request.form['who_called_time_out']
        shc_score = request.form['shc_score']
        opponent_score = request.form['opponent_score']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE BREAK SET SHC_SCORE=?, OPPONENT_SCORE=?, WIND=?, CALLED_BY=? WHERE BREAK_ID=?",
                       (shc_score, opponent_score, 'ph', who_called_to, break_id))
        db.commit()
        return redirect(url_for('stats_taking', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id))  # Redirect to webpage.html
    return render_template('who-called-time-out.html', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, break_id=break_id)


# Define route for game-info page
@app.route('/game-info', methods=['GET', 'POST'])
def game_info():
    if request.method == 'POST':
        # Retrieve values from the form submitted by the user
        date_input = request.form['date_input']  # Assuming 'date' is the name of the input box for serve type
        tournament = request.form['tournament']
        city = request.form['city']
        state = request.form['state']
        opponent = request.form['opponent']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO GAME (DATE, TOURNAMENT, CITY, STATE, OPPONENT) VALUES (?, ?, ?, ?, ?)",
                       (date_input, tournament, city, state, opponent))
        db.commit()
        # Retrieve the last inserted row's GAME_ID
        cursor.execute("SELECT last_insert_rowid()")
        game_id_actual = cursor.fetchone()[0]
        return redirect(url_for('lineup', game_id=game_id_actual))  # Redirect to webpage.html
    return render_template('game-info.html')


# Define route for player-info page
@app.route('/player-info', methods=['GET', 'POST'])
def player_info():
    if request.method == 'POST':
        # Retrieve values from the form submitted by the user
        player_name = request.form['player_name']  # Assuming 'date' is the name of the input box for serve type
        player_id = request.form['player_id']
        year = request.form['year']
        city = request.form['city']
        state = request.form['state']
        height = request.form['height']
        position = request.form['position']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO PLAYER VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (player_id, player_name, year, city, state, height, position))
        db.commit()
        return redirect(url_for('home'))  # Redirect to webpage.html
    return render_template('player-info.html')


# Define route for lineup page
@app.route('/lineup/<game_id>', methods=['GET', 'POST'])
def lineup(game_id):
    if request.method == 'POST':
        # Retrieve values from the form submitted by the user
        pair1player1 = request.form['pair1player1'].split('/')[1]
        pair1player2 = request.form['pair1player2'].split('/')[1]
        pair2player1 = request.form['pair2player1'].split('/')[1]
        pair2player2 = request.form['pair2player2'].split('/')[1]
        pair3player1 = request.form['pair3player1'].split('/')[1]
        pair3player2 = request.form['pair3player2'].split('/')[1]
        pair4player1 = request.form['pair4player1'].split('/')[1]
        pair4player2 = request.form['pair4player2'].split('/')[1]
        pair5player1 = request.form['pair5player1'].split('/')[1]
        pair5player2 = request.form['pair5player2'].split('/')[1]
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO LINEUP (GAME_ID, PAIR_NUMBER, PLAYER_1_ID, PLAYER_2_ID) VALUES (?, ?, ?, ?)",
                       (game_id, 1, pair1player1, pair1player2))
        cursor.execute("INSERT INTO LINEUP (GAME_ID, PAIR_NUMBER, PLAYER_1_ID, PLAYER_2_ID) VALUES (?, ?, ?, ?)",
                       (game_id, 2, pair2player1, pair2player2))
        cursor.execute("INSERT INTO LINEUP (GAME_ID, PAIR_NUMBER, PLAYER_1_ID, PLAYER_2_ID) VALUES (?, ?, ?, ?)",
                       (game_id, 3, pair3player1, pair3player2))
        cursor.execute("INSERT INTO LINEUP (GAME_ID, PAIR_NUMBER, PLAYER_1_ID, PLAYER_2_ID) VALUES (?, ?, ?, ?)",
                       (game_id, 4, pair4player1, pair4player2))
        cursor.execute("INSERT INTO LINEUP (GAME_ID, PAIR_NUMBER, PLAYER_1_ID, PLAYER_2_ID) VALUES (?, ?, ?, ?)",
                       (game_id, 5, pair5player1, pair5player2))
        db.commit()
        db.close()
        return redirect(url_for('home'))  # Redirect to webpage.html
        # Fetch the necessary data to populate the dropdown dynamically
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT DISTINCT NAME, PLAYER_ID FROM PLAYER")
    player_info = cursor.fetchall()
    db.close()
    return render_template('lineup.html', game_id=game_id, player_options=player_info)  # player_options is all the player options for the dropdown. Coming from the entry from the player-info page


@app.route('/delete-last-game-entry/<game_id>', methods=['POST'])
def delete_last_game_entry(game_id):
    db = get_db()
    cursor = db.cursor()
    # Delete the last inserted row from the GAME table for the given game_id
    cursor.execute("DELETE FROM GAME WHERE GAME_ID = ?", game_id)
    db.commit()
    db.close()
    return redirect(url_for('game_info'))


# Define route for take-stats page
@app.route('/take-stats', methods=['GET', 'POST'])
def take_stats():
    if request.method == 'POST':
        # Retrieve the selected game ID and pair number from the form data
        selected_game_id = request.form.get('game_id').split('/')[0]
        selected_pair_number = request.form.get('pair_number')
        selected_game_id_actual = request.form.get('game_id').split('/')[-1]
        selected_set_number = request.form.get('set_number')
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO SET_INFO (GAME_ID, SET_NUMBER, PAIR_NUMBER, TEMPERATURE, WEATHER, WIND, SERVE_RECEIVE, START_TIME, SHC_SCORE, OPPONENT_SCORE, SET_WINNER, MATCH_WINNER, END_TIME) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (selected_game_id_actual, selected_set_number, selected_pair_number, '9', 'ph', 'ph', 'ph', 'ph', 'ph', 'ph', 'ph',
             'ph', 'ph'))
        db.commit()
        # Retrieve the last inserted row's GAME_ID
        cursor.execute("SELECT last_insert_rowid()")
        set_info_id = cursor.fetchone()[0]
        return redirect(url_for('has_start_info_been_entered', game_id=selected_game_id, pair_number=selected_pair_number, game_id_actual=selected_game_id_actual, set_number=selected_set_number, set_number_id=set_info_id))
    # Fetch the necessary data to populate the dropdown dynamically
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT DISTINCT OPPONENT, DATE, GAME_ID FROM GAME")
    game_info = cursor.fetchall()
    db.close()
    return render_template('take-stats.html', game_options=game_info)  # game_options is all the game options for the dropdown. Coming from the entry from the game-info page


# Define route for has-start-info-been-entered page
@app.route('/has-start-info-been-entered/<game_id>/<pair_number>/<game_id_actual>/<set_number>/<set_number_id>', methods=['GET', 'POST'])
def has_start_info_been_entered(game_id, pair_number, game_id_actual, set_number, set_number_id):
    game_name = get_game_name(game_id_actual)
    return render_template('has-start-info-been-entered.html', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, game_name=game_name)


# Define route for which-player page
@app.route('/has-start-info-been-entered/<game_id>/<pair_number>/<game_id_actual>/<set_number>/<set_number_id>/which-player', methods=['GET', 'POST'])
def which_player(game_id, pair_number, game_id_actual, set_number, set_number_id):
    if request.method == 'POST':
        selected_player = request.form.get('player_choice').split('/')[0]
        selected_player_id = request.form.get('player_choice').split('/')[1]
        return redirect(url_for('stats_taking', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=selected_player, player_id=selected_player_id))
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT DISTINCT NAME, PLAYER_ID FROM (
            SELECT NAME, PLAYER_ID FROM LINEUP 
            LEFT JOIN PLAYER ON LINEUP.PLAYER_1_ID = PLAYER.PLAYER_ID 
            WHERE GAME_ID=? AND PAIR_NUMBER=?
            UNION
            SELECT NAME, PLAYER_ID FROM LINEUP 
            LEFT JOIN PLAYER ON LINEUP.PLAYER_2_ID = PLAYER.PLAYER_ID 
            WHERE GAME_ID=? AND PAIR_NUMBER=?
        ) AS player_names
    """, (game_id_actual, pair_number, game_id_actual, pair_number))
    player_names = cursor.fetchall()  # Extracting names from the fetched tuples
    game_name = get_game_name(game_id_actual)
    db.close()
    return render_template('which-player.html', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_names=player_names, game_name=game_name)


# Define route for start-info page
@app.route('/has-start-info-been-entered/<game_id>/<pair_number>/<game_id_actual>/<set_number>/<set_number_id>/start-info', methods=['GET', 'POST'])
def start_info(game_id, pair_number, game_id_actual, set_number, set_number_id):
    if request.method == 'POST':
        # Retrieve values from the form submitted by the user
        temperature = request.form['temp']
        weather = request.form['weather']
        wind = request.form['wind']
        serve_receive = request.form['serve_receive']
        start_time = request.form['start_time']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE SET_INFO SET TEMPERATURE=?, WEATHER=?, WIND=?, SERVE_RECEIVE=?, START_TIME=? WHERE SET_INFO_ID=?",
                       (temperature, weather, wind, serve_receive, start_time, set_number_id))
        db.commit()
        return redirect(url_for('which_player', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id))  # Redirect to webpage.html
    return render_template('start-info.html', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id)


# Define route for stats page
@app.route('/stats', methods=['GET', 'POST'])
def stats():
    if request.method == 'POST':
        # Retrieve values from the form submitted by the user
        player = request.form['player'].split('/')[-1]  # Gives player_id
        player_name = request.form['player'].split('/')[0]  # Gives player_name
        match = request.form['match'].split('/')[-1] # Gives game_id
        game = request.form['match'].split('/')[0]  # Gives game_name(opponent?)
        category = request.form['category']

        # TYPE QUERY
        query = """
        SELECT DISTINCT
               TOTAL_ATTEMPTS.{}_TYPE
             , TOTAL_ATTEMPTS.TOTAL_TYPE
             , TOTAL_ATTEMPTS.TOTAL_ATTEMPTS
             , ROUND(100.0 * TOTAL_TYPE / TOTAL_ATTEMPTS, 1) || '%' AS PERCENTAGE
        FROM(
             SELECT DISTINCT
                    TOTAL_TYPES.*
                  , SUM(TOTAL_TYPES.TOTAL_TYPE) OVER() AS TOTAL_ATTEMPTS
             FROM(
                  SELECT DISTINCT
                         CATEGORY.{}_TYPE
                       , COUNT(CATEGORY.RESULT) AS TOTAL_TYPE
                  FROM {} AS CATEGORY
                  LEFT JOIN PLAYER
                    ON CATEGORY.PLAYER_ID = PLAYER.PLAYER_ID
                  WHERE {}_TYPE != 'ph'        
        """.format(category, category, category, category)
        # Conditionally include WHERE clauses based on user selections
        if player_name != "ALL PLAYERS":
            query += " AND CATEGORY.PLAYER_ID = {}".format(player)
        if game != "ALL GAMES":
            query += " AND GAME_ID = {}".format(match)
        query += """
                 GROUP BY CATEGORY.{}_TYPE
                ) AS TOTAL_TYPES
            ) AS TOTAL_ATTEMPTS
            ORDER BY TOTAL_ATTEMPTS.TOTAL_TYPE DESC 
            """.format(category)
        # Execute the SQL query
        db = get_db()
        cursor = db.cursor()
        cursor.execute(query)
        # Get column names
        columns = [column[0] for column in cursor.description]
        # Fetch all rows and convert to list of dictionaries
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        # Store the results in the session
        session['results'] = results

        # RESULTS QUERY
        query2 = """
                SELECT DISTINCT
                       TOTAL_ATTEMPTS.RESULT
                     , TOTAL_ATTEMPTS.TOTAL_RESULT
                     , TOTAL_ATTEMPTS.TOTAL_ATTEMPTS
                     , ROUND(100.0 * TOTAL_RESULT / TOTAL_ATTEMPTS, 1) || '%' AS PERCENTAGE
                FROM(
                     SELECT DISTINCT
                            TOTAL_RESULTS.*
                          , SUM(TOTAL_RESULTS.TOTAL_RESULT) OVER() AS TOTAL_ATTEMPTS
                     FROM(
                          SELECT DISTINCT
                                 CATEGORY.RESULT
                               , COUNT(CATEGORY.RESULT) AS TOTAL_RESULT
                          FROM {} AS CATEGORY
                          LEFT JOIN PLAYER
                            ON CATEGORY.PLAYER_ID = PLAYER.PLAYER_ID
                          WHERE RESULT != 'ph'        
                """.format(category, category, category, category)
        # Conditionally include WHERE clauses based on user selections
        if player_name != "ALL PLAYERS":
            query2 += " AND CATEGORY.PLAYER_ID = {}".format(player)
        if game != "ALL GAMES":
            query2 += " AND GAME_ID = {}".format(match)
        query2 += """
                  GROUP BY CATEGORY.RESULT
                        ) AS TOTAL_RESULTS
                    ) AS TOTAL_ATTEMPTS
                    ORDER BY TOTAL_ATTEMPTS.TOTAL_RESULT DESC 
                    """.format(category)
        # Execute the SQL query
        db = get_db()
        cursor = db.cursor()
        cursor.execute(query2)
        # Get column names
        columns2 = [column[0] for column in cursor.description]
        # Fetch all rows and convert to list of dictionaries
        results2 = [dict(zip(columns2, row)) for row in cursor.fetchall()]
        # Store the results in the session
        session['results2'] = results2

        # ERROR TYPE QUERY
        if category != 'DIG' and category != 'RECEIVE' and category != 'BLOCK':
            query3 = """
                    SELECT DISTINCT
                           TOTAL_ERRORS.ERROR_TYPE
                         , TOTAL_ERRORS.ERR
                         , TOTAL_ERRORS.TOTAL_ERRORS
                         , ROUND(100.0 * ERR / TOTAL_ERRORS, 1) || '%' AS PERCENTAGE
                    FROM(
                         SELECT DISTINCT
                                TOTAL_RESULTS.*
                              , SUM(TOTAL_RESULTS.ERR) OVER() AS TOTAL_ERRORS
                         FROM(
                              SELECT DISTINCT
                                     CATEGORY.ERROR_TYPE
                                   , COUNT(CATEGORY.ERROR_TYPE) AS ERR
                              FROM {} AS CATEGORY
                              LEFT JOIN PLAYER
                                ON CATEGORY.PLAYER_ID = PLAYER.PLAYER_ID
                              WHERE ERROR_TYPE != 'ph' 
                                AND ERROR_TYPE IS NOT NULL       
                    """.format(category, category, category, category)
            # Conditionally include WHERE clauses based on user selections
            if player_name != "ALL PLAYERS":
                query3 += " AND CATEGORY.PLAYER_ID = {}".format(player)
            if game != "ALL GAMES":
                query3 += " AND GAME_ID = {}".format(match)
            query3 += """
                      GROUP BY CATEGORY.ERROR_TYPE
                            ) AS TOTAL_RESULTS
                        ) AS TOTAL_ERRORS
                        ORDER BY TOTAL_ERRORS.ERR DESC 
                        """.format(category)
            # Execute the SQL query
            db = get_db()
            cursor = db.cursor()
            cursor.execute(query3)
            # Get column names
            columns3 = [column[0] for column in cursor.description]
            # Fetch all rows and convert to list of dictionaries
            results3 = [dict(zip(columns3, row)) for row in cursor.fetchall()]
            # Store the results in the session
            session['results3'] = results3

        return redirect(url_for('stats_data', player=player_name, player_id=player, game=game, category=category))  # Redirect to webpage.html
    # Fetch the necessary data to populate the dropdown dynamically
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT DISTINCT OPPONENT, DATE, GAME_ID FROM GAME")
    game_options = cursor.fetchall()
    cursor.execute("SELECT DISTINCT NAME, PLAYER_ID FROM PLAYER")
    player_options = cursor.fetchall()
    db.close()
    return render_template('stats.html', game_options=game_options, player_options=player_options)


@app.route('/stats-data/<player>/<player_id>/<game>/<category>')
def stats_data(player, player_id, game, category):
    # Retrieve the results from the session
    results = session.get('results')
    results2 = session.get('results2')
    results3 = session.get('results3')
    total_attempts = None
    # Check if results exist in the session
    if results:
        # Extract the TOTAL_ATTEMPTS value from the first row
        total_attempts = results[0]['TOTAL_ATTEMPTS']
        return render_template('stats-data.html', player=player, player_id=player_id, game=game, category=category, results=results, results2=results2, results3=results3, total_attempts=total_attempts)
    else:
        return render_template('stats-data.html', player=player, player_id=player_id, game=game, category=category)


@app.route('/roster')
def roster():
    # TYPE QUERY
    query = """
            SELECT DISTINCT
                   *
            FROM PLAYER       
            """
    # Execute the SQL query
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query)
    # Get column names
    columns = [column[0] for column in cursor.description]
    # Fetch all rows and convert to list of dictionaries
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return render_template('roster.html', results=results)


@app.route('/add-shc-point/<game_id>/<pair_number>/<game_id_actual>/<set_number>/<set_number_id>/<player_name>/<player_id>/<shc_points>/<opp_points>', methods=['POST'])
def add_shc_point(game_id, pair_number, game_id_actual, set_number, set_number_id, player_name, player_id, shc_points, opp_points):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO POINT (GAME_ID, SET_NUMBER, PAIR_NUMBER, PLAYER_ID, SCORING_TEAM) VALUES (?, ?, ?, ?, ?)",
                   (game_id_actual, set_number, pair_number, player_id, 'SHC'))
    db.commit()
    db.close()
    return redirect(url_for('stats_taking', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, shc_points=int(shc_points)+1, opp_points=opp_points))


@app.route('/add-opp-point/<game_id>/<pair_number>/<game_id_actual>/<set_number>/<set_number_id>/<player_name>/<player_id>/<shc_points>/<opp_points>', methods=['POST'])
def add_opp_point(game_id, pair_number, game_id_actual, set_number, set_number_id, player_name, player_id, shc_points, opp_points):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO POINT (GAME_ID, SET_NUMBER, PAIR_NUMBER, PLAYER_ID, SCORING_TEAM) VALUES (?, ?, ?, ?, ?)",
                   (game_id_actual, set_number, pair_number, player_id, 'OPPONENT'))
    db.commit()
    db.close()
    return redirect(url_for('stats_taking', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, shc_points=shc_points, opp_points=int(opp_points)+1))


@app.route('/minus-shc-point/<game_id>/<pair_number>/<game_id_actual>/<set_number>/<set_number_id>/<player_name>/<player_id>/<shc_points>/<opp_points>', methods=['POST'])
def minus_shc_point(game_id, pair_number, game_id_actual, set_number, set_number_id, player_name, player_id, shc_points, opp_points):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
                        DELETE FROM POINT 
                        WHERE GAME_ID=? AND SET_NUMBER=? AND PAIR_NUMBER=? AND PLAYER_ID=? AND SCORING_TEAM='SHC' 
                        AND ROWID=(SELECT ROWID 
                                          FROM POINT 
                                          WHERE GAME_ID=?
                                                AND SET_NUMBER=? 
                                                AND PAIR_NUMBER=? 
                                                AND PLAYER_ID=? 
                                                AND SCORING_TEAM='SHC'
                                   ORDER BY POINT_ID DESC 
                                   LIMIT 1)
                          """,
                   (game_id_actual, set_number, pair_number, player_id, game_id_actual, set_number, pair_number, player_id))
    db.commit()
    db.close()
    return redirect(url_for('stats_taking', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, shc_points=int(shc_points)-1, opp_points=opp_points))


@app.route('/minus-opp-point/<game_id>/<pair_number>/<game_id_actual>/<set_number>/<set_number_id>/<player_name>/<player_id>/<shc_points>/<opp_points>', methods=['POST'])
def minus_opp_point(game_id, pair_number, game_id_actual, set_number, set_number_id, player_name, player_id, shc_points, opp_points):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
                        DELETE FROM POINT 
                        WHERE GAME_ID=? AND SET_NUMBER=? AND PAIR_NUMBER=? AND PLAYER_ID=? AND SCORING_TEAM='OPPONENT' 
                        AND ROWID=(SELECT ROWID 
                                          FROM POINT 
                                          WHERE GAME_ID=?
                                                AND SET_NUMBER=? 
                                                AND PAIR_NUMBER=? 
                                                AND PLAYER_ID=? 
                                                AND SCORING_TEAM='OPPONENT'
                                   ORDER BY POINT_ID DESC 
                                   LIMIT 1)
                          """,
                   (game_id_actual, set_number, pair_number, player_id, game_id_actual, set_number, pair_number, player_id))
    db.commit()
    db.close()
    return redirect(url_for('stats_taking', game_id=game_id, pair_number=pair_number, game_id_actual=game_id_actual, set_number=set_number, set_number_id=set_number_id, player_name=player_name, player_id=player_id, shc_points=
    shc_points, opp_points=int(opp_points)-1))


#----------------------------------
# don't delete or edit this section
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False)
