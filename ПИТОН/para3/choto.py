from flask import Flask
app = Flask(__name__)

from flask import request

@app.route('/')
def home():
    return '''
        <a>main_page</a><br><br>
        <a href="/login">Вход</a><br>
        <a>Регистрация</a><br>
        '''

@app.route('/login', methods = ['GET','POST'] )
def login():
    if request.method == 'POST':
        username = request.form['username']
        return f'добро пожаловать {username}'
    else:
        return '''
        <h2>Вход</h2>
        <form method = "POST">
            Имя: <input type="Text" name="username"><br><br>
            <button type="submit">Войти</button>
            </form>
        '''
        
if __name__ == '__main__':
    app.run(debug=True)