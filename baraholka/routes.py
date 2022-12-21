from baraholka import *


class Advert():
    def __init__(self, name, price, imagePath = None):
        self.name = name
        self.price = price
        self.imagePath = imagePath

class PageButton():
    def __init__(self, state, link, symbol):
        self.state = state
        if state == 'disabled':
            self.a = ''
        else:
            self.a = f'href={link}'
        self.symbol = symbol



@app.route('/')
@app.route('/<int:page>')
def mainPage(page = None):
    if page is not None:
        if page == 1:
            return redirect('/')
    else:
        page = 1

    numberOfPages = 2
    advertsPerPage = 18

    dbCur.execute(f"SELECT id, name, price FROM advert ORDER BY creation_time desc OFFSET {(page - 1) * advertsPerPage} LIMIT {advertsPerPage * numberOfPages}")
    result = dbCur.fetchall()
    advertsGrid = []

    for i in range(0, advertsPerPage, 3):
        if i >= len(result):
            break
        row = []

        for j in range(3):
            if i + j >= len(result):
                break

            dbCur.execute(f"SELECT file_path FROM advert_picture WHERE advert_id = '{result[i + j][0]}' LIMIT 1")
            result2 = dbCur.fetchone()
            imagePath = ''
            if result is not None:
                imagePath = result2

            price = result[i + j][2].split(',')[0]
            row.append(Advert(result[i + j][1], price, imagePath))

        if len(row) > 0:
            advertsGrid.append(row)





    if len(result) <= advertsPerPage:
        numberOfNextPages = 0
    else:
        numberOfNextPages = math.ceil((len(result) - advertsPerPage) / advertsPerPage)

    if page == 1:
        leftButton = PageButton('disabled', '', '«')
    else:
        leftButton = PageButton('', str(page-1), '«')


    if numberOfNextPages == 0:
        rightButton = PageButton('disabled', '', '»')
    else:
        rightButton = PageButton('', str(page+1), '»')

    middleButton = PageButton('active', '#', str(page))


    pageButtons = [leftButton, middleButton, rightButton]

    return render_template('index.html', advertsGrid = advertsGrid, pageButtons = pageButtons)




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



@app.route('/test/')
def uploadTest():
    return render_template('test.html')


@app.route('/test/', methods = ['post'])
def uploadPost():
    if 'file' in request.files:
        file = request.files['file']

        if file.filename != '':
            fileType = file.filename.rsplit('.', 1)[1].lower()
            if fileType in ALLOWED_FILE_TYPES:
                file.save(app.config['UPLOAD_FOLDER'] + str(uuid.uuid4()) + '.' + fileType) #сохраняем под уникальным именем


    return redirect(request.url)
