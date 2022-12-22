from baraholka import *


class Advert():
    def __init__(self, id, name, price, imagePath = ''):
        self.name = name
        self.price = price
        self.link = '/advert/' + id
        self.image = AdvImage(imagePath, 270, 185)


class AdvertBig():
    def __init__(self, name, description, price, category, address, datetime:datetime.datetime, userFirstname, userPhone, imagesPaths):
        self.name = name
        self.description = description
        self.price = formatPrice(price)
        self.category = category
        self.address = address
        self.datetime = f'{datetime.day}.{datetime.month}.{datetime.year} в {datetime.hour}:{datetime.minute}'
        self.user_phone = userFirstname + '⠀✆' + userPhone

        self.images = []
        self.indicators = []
        for i in range(len(imagesPaths)):
            self.images.append(AdvImage(imagesPaths[i], 720, 400))
            self.indicators.append(CarouselIndicator('#carousel-1', i))

        if len(self.images) == 0:
            self.images.append(AdvImage('static/index/assets/img/nophoto.png', 720, 400))
            self.indicators.append(CarouselIndicator(0))

        self.images[0].active = 'active'
        self.indicators[0].active = 'active'


class AdvImage():
    def __init__(self, path, maxW, maxH, active = ''):
        if path == '':
            self.path = '/static/index/assets/img/nophoto.png'
        else:
            self.path = '/' + path

        try:
            img = Image.open('baraholka' + self.path)
            scaledMaxW = img.width
            sclaedMaxH = maxH * scaledMaxW / maxW

            if img.height <= sclaedMaxH:
                self.w = maxW
                self.h = img.height * maxW / img.width
            else:
                self.h = maxH
                self.w = img.width * maxH / img.height
        except:
            self.w = maxW
            self.h = maxH
            self.path = ''

        self.active = active




class CarouselIndicator():
    def __init__(self, slideTo, active = ''):
        self.slideTo = slideTo
        self.active = active



class PageButton():
    def __init__(self, state, link, symbol):
        self.state = state
        self.symbol = symbol

        if link == '':
            self.href = ''
        else:
            self.href = f'href={link}'






def formatPrice(price):
    if price is None:
        return 'Бесплатно'
    else:
        return price.split(',')[0] + ' ₽'



#в result должны быть id, name, price
def getAdvertsGrid(result, desiredAdvertsPerPage):
    advertsGrid = []

    if result is None:
        return advertsGrid

    for i in range(0, desiredAdvertsPerPage, 3):
        if i >= len(result):
            break
        row = []

        for j in range(3):
            if i + j >= len(result):
                break

            dbCur.execute(f"SELECT file_path FROM advert_picture WHERE advert_id = '{result[i + j][0]}' LIMIT 1")
            result2 = dbCur.fetchone()
            imagePath = ''
            if result2 is not None:
                imagePath = result2[0]

            row.append(Advert(result[i + j][0], result[i + j][1], formatPrice(result[i + j][2]), imagePath))

        if len(row) > 0:
            advertsGrid.append(row)

    return advertsGrid






def getPageButtons(page, result, desiredAdvertsPerPage, desiredNumberOfPages):
    if result is None:
        return [PageButton('disabled', '', '<'), PageButton('active', '#', str(page)), PageButton('disabled', '', '>')]

    foundAdvertsNumber = len(result) #сколько найдено объявлений (на этой странице и далее)

    if foundAdvertsNumber < desiredAdvertsPerPage:
        advertsAfterThisPage = 0
    else:
        advertsAfterThisPage = foundAdvertsNumber - desiredAdvertsPerPage

    pagesAfterThis = int(math.ceil(advertsAfterThisPage / desiredAdvertsPerPage)) #сколько можно сформировать страниц после этой
    pagesBeforeThis = page - 1 #сколько страниц до этой
    totalNumberOfPages = page + pagesAfterThis #общее количество страниц

    #кнопка влево
    if page == 1:
        prevButton = PageButton('disabled', '', '<')
    else:
        prevButton = PageButton('', str(page - 1), '<')

    #кнопка вправо
    if pagesAfterThis == 0:
        nextButton = PageButton('disabled', '', '>')
    else:
        nextButton = PageButton('', str(page + 1), '>')



    #количество кнопок навигации
    if totalNumberOfPages < desiredNumberOfPages:
        numberOfPageButtons = desiredNumberOfPages
    else:
        numberOfPageButtons = desiredNumberOfPages


    #кнопка текушей страницы посередине (если четное количество кнопок, то "слева от середины")
    thisPageButtonIndex = int(math.ceil(numberOfPageButtons / 2)) - 1
    if pagesBeforeThis < thisPageButtonIndex:
        thisPageButtonIndex = pagesBeforeThis


    numberOfPageButtonsBeforeThis = thisPageButtonIndex #сколько кнопок страниц слева от текущей
    numberOfPageButtonsAfterThis = (numberOfPageButtons - 1) - thisPageButtonIndex #сколько кнопок страниц справа от текущей

    #если до текушей страницы меньше страниц, чем мы хотим кнопок, то убираем кнопки ДО и если можно, добавляем ПОСЛЕ
    if pagesBeforeThis < numberOfPageButtonsBeforeThis:
        diff = numberOfPageButtonsBeforeThis - pagesBeforeThis
        numberOfPageButtonsBeforeThis -= diff

        if numberOfPageButtonsAfterThis + diff < pagesAfterThis:
            numberOfPageButtonsAfterThis += diff
        else:
            numberOfPageButtonsAfterThis = pagesAfterThis

    #зеркально
    if pagesAfterThis < numberOfPageButtonsAfterThis:
        diff = numberOfPageButtonsAfterThis - pagesAfterThis
        numberOfPageButtonsAfterThis -= diff

        if numberOfPageButtonsBeforeThis + diff < pagesBeforeThis:
            numberOfPageButtonsBeforeThis += diff
        else:
            numberOfPageButtonsBeforeThis = pagesBeforeThis


    #формируем массив кнопок
    pageButtons = [prevButton]
    for pageNum in range(page - numberOfPageButtonsBeforeThis, page + numberOfPageButtonsAfterThis + 1):
        if pageNum == page:
            pageButtons.append(PageButton('active', '#', str(pageNum)))
        else:
            pageButtons.append(PageButton('', str(pageNum), str(pageNum)))
    pageButtons.append(nextButton)

    return pageButtons



@app.route('/')
@app.route('/<int:page>')
def mainPage(page = None):
    if page is not None:
        if page == 1:
            return redirect('/')
    else:
        page = 1

    searchEntry = request.args.get('search')
    if searchEntry is not None:
        pass


    desiredNumberOfPages = 5 #сколько хотим кнопок навигации по страницам
    desiredAdvertsPerPage = 18 #сколько хотим объявлений на одной странице

    dbCur.execute(f"SELECT id, name, price FROM advert ORDER BY datetime desc OFFSET {(page - 1) * desiredAdvertsPerPage} LIMIT {desiredAdvertsPerPage * desiredNumberOfPages}")
    result = dbCur.fetchall()

    return render_template('index.html', advertsGrid = getAdvertsGrid(result, desiredAdvertsPerPage), pageButtons = getPageButtons(page, result, desiredAdvertsPerPage, desiredNumberOfPages))




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

    return redirect('/')



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






@app.route('/newadvert/')
def newAdvertPage():
    if not current_user.is_authenticated:
        return redirect('/login/')

    searchEntry = request.args.get('search')
    if searchEntry is not None:
        pass


    dbCur.execute(f"SELECT name FROM category ORDER BY name")
    result = dbCur.fetchall()
    #TODO если none?

    categories = []
    for r in result:
        categories.append(r[0])

    return render_template('advcreate.html', categories = categories)


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


    if price != '':
        try:
            priceFloat = float(price.replace(',', '.'))
        except: #если цена как-то неправильно написана
            return render_template('blank.html', text = 'Ошибка')

    #если цена не указана, или указана нулевая, записываем NULL
    if price == '' or priceFloat == 0:
        price = 'NULL'

    else:
        price = price.replace('.', ',')
        price = "'" + price + "'"

    dbCur.execute(f"INSERT INTO advert (name, user_id, description, price, category, address, status) VALUES ('{name}', '{current_user.get_id()}', '{description}', {price}, '{category}', '{address}', 'ok') RETURNING id")
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

    if page is not None:
        if page == 1:
            return redirect('/myadverts/')
    else:
        page = 1


    searchEntry = request.args.get('search')
    if searchEntry is not None:
        pass


    desiredNumberOfPages = 5 #сколько хотим кнопок навигации по страницам
    desiredAdvertsPerPage = 18 #сколько хотим объявлений на одной странице

    dbCur.execute(f"SELECT id, name, price FROM advert WHERE user_id = '{current_user.id}' ORDER BY datetime desc OFFSET {(page - 1) * desiredAdvertsPerPage} LIMIT {desiredAdvertsPerPage * desiredNumberOfPages}")
    result = dbCur.fetchall()

    return render_template('index.html', advertsGrid = getAdvertsGrid(result, desiredAdvertsPerPage), pageButtons = getPageButtons(page, result, desiredAdvertsPerPage, desiredNumberOfPages))









@app.route('/advert/')
@app.route('/advert/<uuid:advertdId>')
def advertPage(advertdId = None):
    if advertdId == None:
        return redirect('/')

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


    return render_template('adv.html', advert = advert, showControlButtons = showControlButtons)