
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import timedelta
import random
import secrets
import string
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.permanent_session_lifetime = timedelta(days=1)
app.url_map.strict_slashes = False

# Store game sessions
games = {}

@app.route('/')
def index():
    if 'player_id' in session:
        game_code = session.get('game_code')
        if game_code in games:
            return render_template('player.html', 
                                role=games[game_code]['players'].get(session['player_id']),
                                show_role=games[game_code]['roles_revealed'])
    return render_template('join.html')

@app.route('/join', methods=['POST'])
def join():
    code = request.form.get('code')
    if code in games:
        session.permanent = True
        player_id = secrets.token_hex(8)
        player_name = request.form.get('player_name')
        session['player_id'] = player_id
        session['game_code'] = code
        games[code]['players'][player_id] = {'name': player_name, 'role': None}
        return redirect(url_for('index'))
    return "Invalid game code", 400

@app.route('/admin')
def admin():
    if session.get('is_admin'):
        return render_template('admin.html', games=games)
    return redirect(url_for('admin_login'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == os.getenv('ADMIN_PASSWORD', '123456'):
            session.permanent = True
            session['is_admin'] = True
            return redirect(url_for('admin'))
        return render_template('admin_login.html', error="Invalid password")
    return render_template('admin_login.html', error=None)

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

@app.route('/create_game', methods=['POST'])
def create_game():
    roles = []
    
    # Add standard roles based on count
    villagers = int(request.form.get('villagers', 0))
    werewolves = int(request.form.get('werewolves', 0))
    seer = int(request.form.get('seer', 0))
    doctor = int(request.form.get('doctor', 0))
    
    roles.extend(['Villager'] * villagers)
    roles.extend(['Werewolf'] * werewolves)
    roles.extend(['Seer'] * seer)
    roles.extend(['Doctor'] * doctor)
    
    # Add custom roles
    custom_roles = request.form.getlist('custom_roles[]')
    custom_counts = request.form.getlist('custom_counts[]')
    for role, count in zip(custom_roles, custom_counts):
        if role.strip() and int(count) > 0:
            roles.extend([role.strip()] * int(count))

    if not roles:
        return "Please select at least one role", 400

    game_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    games[game_code] = {
        'roles': roles,
        'players': {},
        'roles_revealed': False
    }
    return redirect(url_for('admin'))

@app.route('/remove_game/<code>')
def remove_game(code):
    if code in games:
        del games[code]
    return redirect(url_for('admin'))

@app.route('/assign_roles/<code>')
def assign_roles(code):
    if code in games:
        game = games[code]
        players = list(game['players'].keys())
        available_roles = game['roles'].copy()

        if len(players) != len(available_roles):
            return "Number of players must match number of roles", 400

        random.shuffle(available_roles)
        for player, role in zip(players, available_roles):
            game['players'][player]['role'] = role
        game['roles_revealed'] = True

    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
