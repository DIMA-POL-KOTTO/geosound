from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import re
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from init_db import FDataBase

class UserLogin(UserMixin):
    def fromDB(self, user_id):
        dbase = FDataBase()
        user_data = dbase.get_user_by_id(user_id)
        dbase.close()
        if not user_data:
            return False
        self.__user = {
            'id': user_data[0],
            'username': user_data[1],
            'email': user_data[2],
            'password_hash': user_data[3],
            'is_premium': user_data[4],
            'created_at': user_data[5]
        }
        return self
    def create(self, user):
        self.__user = user
        return self
    def get_id(self):
        return str(self.__user['id'])
    def get_username(self):
        return str(self.__user['username'])

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'bjlasdl32b2ln54kl31e2' #для session
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Авторизуйтесь сначала, пожалуйста'
login_manager.login_message_category = 'success'

@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id)

@app.route('/')
def index():
    dbase = FDataBase()
    tracks = dbase.get_tracks_with_audio() #[(1, 'LET ME BE', ... , None), (...), ..., (...)]
    user_playlists = []
    if current_user.is_authenticated:
        user_playlists = dbase.get_playlists_by_owner(current_user.get_id())
    dbase.close()
    return render_template('index.html', tracks=tracks, user_playlists=user_playlists)

@app.route('/map')
def map():
    return render_template('map.html')

@app.route('/support')
def support():
    return "<h1>Поддержка</h1>"

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', username=current_user.get_username())

@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        dbase = FDataBase()
        user_data = dbase.get_user_by_username(username)
        dbase.close()
        if user_data and check_password_hash(user_data[3], password):
            user = {
                'id': user_data[0],
                'username': user_data[1],
                'email': user_data[2],
                'password_hash': user_data[3],
                'is_premium': user_data[4],
                'created_at': user_data[5]
            }
            userlogin = UserLogin().create(user)
            login_user(userlogin)
            session['username'] = user['username']
            return redirect(request.args.get("next") or url_for("index"))
        flash('Неверный логин или пароль', 'error')
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password2 = request.form['password2']
        if len(username) >= 4 and re.match(r'^[a-zA-Z0-9_\-$]+$', username):
            if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                if len(password) >= 8:
                    if password == password2:
                        password_hash = generate_password_hash(password)
                        dbase = FDataBase()
                        user_exist = dbase.get_id_by_username_or_email(username, email)
                        if user_exist:
                            row = dbase.get_username_and_email_by_username_or_email(username, email)
                            if row[0] == username:
                                flash("Пользователь с таким именем уже существует", 'error')
                            else:
                                flash('Пользователь с таким email уже существует', 'error')
                            dbase.close()
                        else:
                            dbase.add_user(username, email, password_hash)
                            dbase.close()
                            flash('Вы зарегистрировались!', 'success')
                            return redirect(url_for('login'))
                    else:
                        flash('Пароли не совпадают', 'error')
                else:
                    flash('Пароль должен быть больше 8 символов', 'error')
            else:
                flash('Неверный email', 'error')
        else:
            flash('Длина имени должна быть больше 4 и может содержать только буквы латинского алфавита, цифры, _, -, $', 'error')

    return render_template('register.html')

@app.route("/create_playlist", methods=['POST'])
@login_required
def create_playlist():
    if request.method == 'POST':
        name = request.form['name']
        if name:
            dbase = FDataBase()
            dbase.add_playlist(name, current_user.get_id())
            flash('Плейлист создан!','success')
            return redirect(url_for('playlists'))
        else:
            flash('Название плейлиста не может быть пустым!','error')
            return redirect(url_for('playlists'))

@app.route ('/playlists')
@login_required
def playlists():
    dbase = FDataBase()
    playlists = dbase.get_playlists_by_owner(current_user.get_id())
    dbase.close()
    return render_template('playlists.html', playlists=playlists)

@app.route('/add_track_to_playlist', methods=['POST'])
@login_required
def add_track_to_playlist():
    if request.method == 'POST':
        playlist_id = request.form['playlist_id']
        track_id = request.form['track_id']
        dbase = FDataBase()
        dbase.add_track_to_playlist(playlist_id, track_id)
        dbase.close()
        return redirect(url_for('index'))

@app.route('/playlists/<int:playlist_id>')
@login_required
def playlist_detail(playlist_id):
    dbase = FDataBase()
    playlist = dbase.get_playlist_by_id(playlist_id)
    if not playlist:
        flash('Плейлист не найден!')
        return redirect(url_for('profile'))
    tracks = dbase.get_tracks_by_playlist(playlist_id)
    dbase.close()
    return render_template('playlist_detail.html', playlist_name = playlist[1], tracks=tracks)

#получить данные из бд -> парсинг: POLYGON((31.43 43.23, 31.54 34.54...)) -> 31.43 43.23, 31.54 34.54... -> менять местами
#широту и долготу -> формирование данных в виде json
@app.route('/get_zones')
@login_required
def get_zones():
    dbase = FDataBase()
    zones_data = dbase.get_zones_by_owner(current_user.get_id())  # массив кортежей
    dbase.close()
    zones = []
    for z in zones_data:
        match = re.search(r'\(\((.*?)\)\)', z[4])
        coords_str = match.group(1)
        points = []
        for point in coords_str.split(','):
            lng, lat = point.split()
            points.append([float(lat), float(lng)])
        zones.append({
            'id': z[0],
            'name': z[3],
            'coords': points,
            'color': z[7]
        })
    return jsonify(zones)




# with app.app_context():
#     dbase = FDataBase()
#     zones_data = dbase.get_zones_by_owner(5)  # массив кортежей
#     dbase.close()
#     zones = []
#     for z in zones_data:
#         match = re.search(r'\(\((.*?)\)\)', z[4])
#         coords_str = match.group(1)
#         points = []
#         for point in coords_str.split(','):
#             lng, lat = point.split()
#             points.append([float(lat), float(lng)])
#         zones.append({
#             'id': z[0],
#             'name': z[3],
#             'coords': points
#         })
#     print(zones)




if __name__ == '__main__':
    app.run(debug=True)

