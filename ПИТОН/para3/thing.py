from flask import Flask
app = Flask(__name__)

from flask import request

@app.route('/')
def home():
    return "main_page"

@app.route('/contact')
def contact():
    return "Contact us"

@app.route('/about')
def about():
    return "About us"

@app.route('/user/<username>')
def show_user(username):
    return f"Hello, {username}!"

@app.route('/post/<int:price>')
def show_user_post(price):
    return f"Post: {price}"

@app.route('/product/<name>/<int:price>')
def user_num(name, price):
    return f"Thing: {name}, Cost: {price}"

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