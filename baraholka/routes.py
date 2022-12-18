from baraholka import *

@app.route('/')
def mainPage():
    return render_template('index.html')




@app.route('/login/')
def loginPage():
    if current_user.is_authenticated:
        return redirect('/profile/')

    return render_template('login.html')


@app.route('/login/', methods = ['post'])
def loginPost():
    email = request.form.get('email')
    password = request.form.get('password')

    if email is None or password is None:
        return render_template('blank.html', text = 'Ошибка')

    dbCur.execute(f"SELECT id FROM appuser WHERE email = '{email}' AND password = '{password}'")
    result = dbCur.fetchone()

    if result is None:
        return render_template('login.html', text = 'Неверный email или пароль', prefilledEmail = email)
    else:
        User.loadById(result[0])
        login_user(User)
        return redirect('/profile/')





@app.route('/register/')
def registerPage():
    if current_user.is_authenticated:
        return redirect('/profile/')

    return render_template('register.html')


@app.route('/register/', methods = ['post'])
def registerPost():
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    password2 = request.form.get('password2')

    if firstname is None or lastname is None or email is None or phone is None or password is None or password2 is None:
        return render_template('blank.html', text = 'Ошибка')

    if password != password2:
        return render_template('register.html', text = 'Пароли не совпадают')

    #в общем то можно забить, если сделать хорошие проверки в форме
    #TODO если неправильный формат имени
    #TODO если неправильный формат email
    #TODO если неправильный формат телефона

    dbCur.execute(f"SELECT * FROM appuser WHERE email = '{email}'")
    result = dbCur.fetchone()
    if result is not None:
        return render_template('register.html', text = 'Пользователь с таким email уже зарегистрирован. Воспользуйтесь <a href=/login/> формой входа </a>')

    dbCur.execute(f"INSERT INTO appuser (email, password, firstname, lastname, phone) VALUES ('{email}', '{password}', '{firstname}', '{lastname}', '{phone}') returning id")
    dbCon.commit()
    result = dbCur.fetchone()

    if result is None:
        return render_template('blank.html', text = 'Ошибка')


    User.loadById(result[0])
    login_user(User)

    return redirect('/profile/')



@app.route('/profile/')
def profilePage():
    if not current_user.is_authenticated:
        return redirect('/login/')

    return render_template('profile.html', user = current_user)


@app.route('/profile/', methods = ['post'])
def profilePost():
    if current_user.is_authenticated:
        if 'logout' in request.form:
            logout_user()

    return redirect('/')

