from baraholka.service import *



@app.route('/')
@app.route('/<int:page>')
def mainPage(page = None):
    if current_user.is_authenticated and current_user.isModerator: #модератор видит только ожидающие одобрения
        allowedStates = [AdvertState.waitingAppoval]
    else:
        allowedStates = [AdvertState.approved]

    return advertsListPage(page, 'mainPage', request, fromCurrentUserOnly = False, allowedStates = allowedStates)




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

    passwordHash =  hashlib.sha256((appSettings['userPasswordSalt1'] + password + appSettings['userPasswordSalt2']).encode()).hexdigest()

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

    passwordHash =  hashlib.sha256((appSettings['userPasswordSalt1'] + password + appSettings['userPasswordSalt2']).encode()).hexdigest()

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

    if current_user.isModerator:
        return redirect('/')

    searchEntry = request.args.get('search')
    searchCategory = request.args.get('category')
    if searchEntry is not None or searchCategory is not None:
        return redirect(url_for('mainPage', **request.args))


    return render_template('advcreate.html', searchCategories = getSearchCategories(searchCategory), categories = getCategories())


@app.route('/newadvert/', methods = ['post'])
def newAdvertPost():
    if not current_user.is_authenticated:
        return redirect('/login/')

    if current_user.isModerator:
        return redirect('/')

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

    dbCur.execute(f"INSERT INTO advert (name, user_id, description, price, category, address, state) VALUES ('{name}', '{current_user.get_id()}', '{description}', '{price}', '{category}', '{address}', '{AdvertState.waitingAppoval}') RETURNING id")
    dbCon.commit()
    result = dbCur.fetchone()
    advertId = result[0]

    for file in uploadedFiles:
        print(f'file "{file}"')
        if file.filename != '':
            fileType = file.filename.rsplit('.', 1)[1].lower()
            if fileType in appSettings['allowedFileTypes']:
                fileName = str(uuid.uuid4()) + '.' + fileType #сохраняем под уникальным именем
                file.save('baraholka/static/userFiles/' + fileName)

                dbCur.execute(f"INSERT INTO advert_picture (advert_id, file_path) VALUES ('{advertId}', 'static/userFiles/{fileName}')")

    if len(uploadedFiles) > 0:
        dbCon.commit()


    return redirect(f'/advert/{advertId}/')






@app.route('/myadverts/')
@app.route('/myadverts/<int:page>')
def myAdvertsPage(page = None):
    if not current_user.is_authenticated:
        return redirect('/login/')

    if current_user.isModerator:
        return redirect('/')

    allowedStates = [AdvertState.waitingAppoval, AdvertState.approved, AdvertState.rejected, AdvertState.archived]

    return advertsListPage(page, 'myAdvertsPage', request, fromCurrentUserOnly = True, allowedStates = allowedStates)









@app.route('/advert/')
@app.route('/advert/<uuid:advertId>/')
def advertPage(advertId = None):
    if advertId == None:
        return redirect('/')

    searchEntry = request.args.get('search')
    searchCategory = request.args.get('category')
    if searchEntry is not None or searchCategory is not None:
        return redirect(url_for('mainPage', **request.args))


    dbCur.execute(f"SELECT name, description, price, category, address, datetime, user_id, state FROM advert WHERE id = '{advertId}'")
    result = dbCur.fetchone()

    if result == None:
        return redirect('/')

    #неодобренные или ожидающие объявления могут просматривать только их авторы и модераторы
    if  result[7] not in [AdvertState.approved, AdvertState.archived] and (not current_user.is_authenticated or (current_user.get_id() != result[6] and not current_user.isModerator)):
        return redirect('/')

    dbCur.execute(f"SELECT firstname, phone FROM appuser WHERE id = '{result[6]}'")
    result2 = dbCur.fetchone()

    dbCur.execute(f"SELECT file_path FROM advert_picture WHERE advert_id = '{advertId}'")
    result3 = dbCur.fetchall()

    imagesPaths = []
    for r in result3:
        imagesPaths.append(r[0])



    buttonsType = AdvertButtonsType.noButtons
    if current_user.is_authenticated and current_user.isModerator and result[7] == AdvertState.waitingAppoval:
        buttonsType = AdvertButtonsType.moderator
    elif current_user.get_id() == result[6] and result[7] != AdvertState.archived:
        buttonsType = AdvertButtonsType.owner

    advert = AdvertBig(result[0], result[1].replace('\n', '<br>'), result[2], result[3], result[4], result[5], result2[0], result2[1], result[7], buttonsType, imagesPaths)

    return render_template('adv.html', advert = advert, searchCategories = getSearchCategories(searchCategory))




@app.route('/advert/<uuid:advertId>/', methods = ['post'])
def advertPost(advertId = None):
    if not current_user.is_authenticated:
        return redirect('/login/')

    dbCur.execute(f"SELECT state, user_id FROM advert WHERE id = '{advertId}'")
    result = dbCur.fetchone()

    if result is None:
        return redirect('/')

    currentState = result[0]
    ownerId = result[1]


    if 'stopSelling' in request.form:
        if current_user.get_id() == ownerId and currentState != AdvertState.archived:
            dbCur.execute(f"UPDATE advert SET state = '{AdvertState.archived}' WHERE id = '{advertId}'")
            dbCon.commit()
        else:
            return redirect('/')


    elif 'approve' in request.form:
        if current_user.isModerator and currentState != AdvertState.approved:
            dbCur.execute(f"UPDATE advert SET state = '{AdvertState.approved}' WHERE id = '{advertId}'")
            dbCon.commit()
        else:
            return redirect('/')


    elif 'reject' in request.form:
        if current_user.isModerator and currentState != AdvertState.rejected:
            dbCur.execute(f"UPDATE advert SET state = '{AdvertState.rejected}' WHERE id = '{advertId}'")
            dbCon.commit()
        else:
            return redirect('/')

    return redirect(f'/advert/{advertId}/')






@app.route('/advert/edit/')
@app.route('/advert/<uuid:advertId>/edit/')
def advertEdit(advertId = None):
    if not current_user.is_authenticated:
        return redirect('/login/')

    if advertId == None:
        return redirect('/')


    dbCur.execute(f"SELECT state, user_id, name, description, address, category, price FROM advert WHERE id = '{advertId}'")
    result = dbCur.fetchone()

    if result is None:
        return redirect('/')

    currentState = result[0]
    ownerId = result[1]

    if current_user.get_id() != ownerId:
        return redirect('/')

    if currentState == AdvertState.archived:
        return redirect('/')

    searchEntry = request.args.get('search')
    searchCategory = request.args.get('category')
    if searchEntry is not None or searchCategory is not None:
        return redirect(url_for('mainPage', **request.args))

    price = result[6].split(',')[0].replace(' ', '')

    editAdvert = EditAdvert(result[2], result[3], price, result[4])

    return render_template('advcreate.html', searchCategories = getSearchCategories(searchCategory), categories = getCategories(result[5]), editAdvert = editAdvert)





@app.route('/advert/<uuid:advertId>/edit/', methods = ['post'])
def advertEditpost(advertId = None):
    if not current_user.is_authenticated:
        return redirect('/login/')

    if advertId == None:
        return redirect('/')


    dbCur.execute(f"SELECT state, user_id, name, description, address, category, price FROM advert WHERE id = '{advertId}'")
    result = dbCur.fetchone()

    if result is None:
        return redirect('/')

    currentState = result[0]
    ownerId = result[1]

    if current_user.get_id() != ownerId:
        return redirect('/')

    if currentState == AdvertState.archived:
        return redirect('/')



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

    #dbCur.execute(f"INSERT INTO advert (name, user_id, description, price, category, address, state) VALUES ('{name}', '{current_user.get_id()}', '{description}', '{price}', '{category}', '{address}', '{AdvertState.waitingAppoval}') RETURNING id")
    dbCur.execute(f"UPDATE advert SET name = '{name}', description = '{description}', price = '{price}', category = '{category}', address = '{address}', state = '{AdvertState.waitingAppoval}' WHERE id = '{advertId}'")
    dbCon.commit()

    print(f'sdfsdfsdfsd = {uploadedFiles}')


    numberOfallowedFiles = 0
    for file in uploadedFiles:
        if file.filename != '':
            fileType = file.filename.rsplit('.', 1)[1].lower()
            if fileType in appSettings['allowedFileTypes']:
                numberOfallowedFiles += 1

    #если загружены новые фотографии, старые удаляются
    if numberOfallowedFiles > 0:
        dbCur.execute(f"DELETE from advert_picture WHERE advert_id = '{advertId}'")
        dbCon.commit()


        for file in uploadedFiles:
            if file.filename != '':
                fileType = file.filename.rsplit('.', 1)[1].lower()
                if fileType in appSettings['allowedFileTypes']:
                    fileName = str(uuid.uuid4()) + '.' + fileType #сохраняем под уникальным именем
                    file.save('baraholka/static/userFiles/' + fileName)

                    dbCur.execute(f"INSERT INTO advert_picture (advert_id, file_path) VALUES ('{advertId}', 'static/userFiles/{fileName}')")

            dbCon.commit()


    return redirect(f'/advert/{advertId}/')