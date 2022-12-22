from baraholka.service import *



@app.route('/')
@app.route('/<int:page>')
def mainPage(page = None):
    return advertsListPage(page, 'mainPage', request, fromCurrentUserOnly = False)




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

    passwordHash = PASSWORD_SALT1 + hashlib.sha256(password.encode()).hexdigest() + PASSWORD_SALT2

    dbCur.execute(f"SELECT id FROM appuser WHERE email = '{email}' AND password = '{passwordHash}'")
    result = dbCur.fetchone()

    if result is None:
        return render_template('login.html', errorMsg = 'Неверный email или пароль', prefilledEmail = email)
    else:
        User.loadById(result[0])
        login_user(User)
        return redirect('/')





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
        return render_template('register.html', text = 'Пароли не совпадают', prefilledFirstname = firstname, prefilledLastname = lastname, prefilledEmail = email, prefilledPhone = phone)

    #в общем то можно забить, если сделать хорошие проверки в форме
    #TODO если неправильный формат имени
    #TODO если неправильный формат email
    #TODO если неправильный формат телефона

    dbCur.execute(f"SELECT * FROM appuser WHERE email = '{email}'")
    result = dbCur.fetchone()
    if result is not None:
        return render_template('register.html', errorMsg = 'Пользователь с таким email уже зарегистрирован', prefilledFirstname = firstname, prefilledLastname = lastname, prefilledEmail = email, prefilledPhone = phone)

    passwordHash = PASSWORD_SALT1 + hashlib.sha256(password.encode()).hexdigest() + PASSWORD_SALT2

    dbCur.execute(f"INSERT INTO appuser (email, password, firstname, lastname, phone) VALUES ('{email}', '{passwordHash}', '{firstname}', '{lastname}', '{phone}') returning id")
    dbCon.commit()
    result = dbCur.fetchone()

    if result is None:
        return render_template('blank.html', text = 'Ошибка')


    User.loadById(result[0])
    login_user(User)

    return redirect('/')





@app.route('/profile/')
def profilePage():
    if not current_user.is_authenticated:
        return redirect('/login/')

    searchEntry = request.args.get('search')
    searchCategory = request.args.get('category')
    if searchEntry is not None or searchCategory is not None:
        return redirect(url_for('mainPage', **request.args))

    return render_template('profile.html', user = current_user, searchCategories = getSearchCategories(searchCategory))


@app.route('/profile/', methods = ['post'])
def profilePost():
    if current_user.is_authenticated:
        if 'logout' in request.form:
            logout_user()

    return redirect('/')






@app.route('/newadvert/')
def newAdvertPage():
    if not current_user.is_authenticated:
        return redirect('/login/')

    searchEntry = request.args.get('search')
    searchCategory = request.args.get('category')
    if searchEntry is not None or searchCategory is not None:
        return redirect(url_for('mainPage', **request.args))


    return render_template('advcreate.html', searchCategories = getSearchCategories(), categories = getCategories(searchCategory))


@app.route('/newadvert/', methods = ['post'])
def newAdvertPost():
    if not current_user.is_authenticated:
        return redirect('/login/')

    name = request.form.get('name')
    description = request.form.get('description')
    address = request.form.get('address')
    category = request.form.get('category')
    price = request.form.get('price')

    uploadedFiles = request.files.getlist("file")

    if price == '':
        price = '0'
    else:
        try:
            float(price.replace(',', '.'))
        except: #если цена как-то неправильно написана
            return render_template('blank.html', text = 'Ошибка')

    price = price.replace('.', ',')

    dbCur.execute(f"INSERT INTO advert (name, user_id, description, price, category, address, status) VALUES ('{name}', '{current_user.get_id()}', '{description}', '{price}', '{category}', '{address}', 'ok') RETURNING id")
    dbCon.commit()
    result = dbCur.fetchone()
    advertId = result[0]

    for file in uploadedFiles:
        print(f'file "{file}"')
        if file.filename != '':
            fileType = file.filename.rsplit('.', 1)[1].lower()
            if fileType in ALLOWED_FILE_TYPES:
                fileName = str(uuid.uuid4()) + '.' + fileType #сохраняем под уникальным именем
                file.save('baraholka/static/userFiles/' + fileName)

            dbCur.execute(f"INSERT INTO advert_picture (advert_id, file_path) VALUES ('{advertId}', 'static/userFiles/{fileName}')")

    if len(uploadedFiles) > 0:
        dbCon.commit()


    return redirect('/')






@app.route('/myadverts/')
@app.route('/myadverts/<int:page>')
def myAdvertsPage(page = None):
    if not current_user.is_authenticated:
        return redirect('/login/')

    return advertsListPage(page, 'myAdvertsPage', request, fromCurrentUserOnly = True)









@app.route('/advert/')
@app.route('/advert/<uuid:advertdId>')
def advertPage(advertdId = None):
    if advertdId == None:
        return redirect('/')

    searchEntry = request.args.get('search')
    searchCategory = request.args.get('category')
    if searchEntry is not None or searchCategory is not None:
        return redirect(url_for('mainPage', **request.args))


    dbCur.execute(f"SELECT name, description, price, category, address, datetime, user_id FROM advert WHERE id = '{advertdId}'")
    result = dbCur.fetchone()

    if result == None:
        return redirect('/')

    dbCur.execute(f"SELECT firstname, phone FROM appuser WHERE id = '{result[6]}'")
    result2 = dbCur.fetchone()

    dbCur.execute(f"SELECT file_path FROM advert_picture WHERE advert_id = '{advertdId}'")
    result3 = dbCur.fetchall()

    imagesPaths = []
    for r in result3:
        imagesPaths.append(r[0])

    advert = AdvertBig(result[0], result[1], result[2], result[3], result[4], result[5], result2[0], result2[1], imagesPaths)



    if current_user.get_id() == result[6]:
        showControlButtons = True
    else:
        showControlButtons = False


    return render_template('adv.html', advert = advert, showControlButtons = showControlButtons, searchCategories = getSearchCategories(searchCategory))