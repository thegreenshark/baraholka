from baraholka.service import *



@app.route('/')
@app.route('/<int:page>/')
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
    chosenFile = request.form.get('photoSelectRadio')
    uploadedFiles = request.files.getlist("file")


    allowedFiles = []

    for file in uploadedFiles:
        if file.filename != '':
            fileType = file.filename.rsplit('.', 1)[1].lower()
            if fileType in appSettings['allowedFileTypes']:
                allowedFiles.append(file)


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




    for file in allowedFiles:
        if file.filename != '':
            fileType = file.filename.rsplit('.', 1)[1].lower()
            if fileType in appSettings['allowedFileTypes']:
                fileName = str(uuid.uuid4()) + '.' + fileType #сохраняем под уникальным именем
                file.save('baraholka/static/userFiles/' + fileName)

                main = 'FALSE'
                if len(allowedFiles) < 2:
                    main = 'TRUE'
                else:
                    if chosenFile is None:
                        if file == allowedFiles[0]:
                            main = 'TRUE'
                    else:
                        if chosenFile == file.filename:
                            main = 'TRUE'

                dbCur.execute(f"INSERT INTO advert_picture (advert_id, file_path, main) VALUES ('{advertId}', 'static/userFiles/{fileName}', '{main}')")

    if len(allowedFiles) > 0:
        dbCon.commit()


    return redirect(f'/advert/{advertId}/')






@app.route('/myadverts/')
@app.route('/myadverts/<int:page>/')
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


    linkToChat='/'

    buttonsType = AdvertButtonsType.noButtons
    if current_user.is_authenticated and current_user.isModerator and result[7] == AdvertState.waitingAppoval:
        buttonsType = AdvertButtonsType.moderator
    elif current_user.is_authenticated and not current_user.isModerator and current_user.get_id() == result[6] and result[7] != AdvertState.archived:
        buttonsType = AdvertButtonsType.owner
    elif current_user.is_authenticated and not current_user.isModerator and current_user.get_id() != result[6]:
        buttonsType = AdvertButtonsType.registeredUser
        linkToChat = f'/chat/{advertId}/{current_user.get_id()}/'

    advert = AdvertBig(result[0], result[1].replace('\n', '<br>'), result[2], result[3], result[4], result[5], result2[0], result2[1], result[7], buttonsType, imagesPaths)

    return render_template('adv.html', advert = advert, searchCategories = getSearchCategories(searchCategory), linkToChat = linkToChat)




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

    advertId = str(advertId)

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

    advertId = str(advertId)

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
    chosenFile = request.form.get('photoSelectRadio')
    uploadedFiles = request.files.getlist("file")

    allowedFiles = []

    for file in uploadedFiles:
        if file.filename != '':
            fileType = file.filename.rsplit('.', 1)[1].lower()
            if fileType in appSettings['allowedFileTypes']:
                allowedFiles.append(file)


    if price == '':
        price = '0'
    else:
        try:
            float(price.replace(',', '.'))
        except: #если цена как-то неправильно написана
            return render_template('blank.html', text = 'Ошибка')

    price = price.replace('.', ',')

    dbCur.execute(f"UPDATE advert SET name = '{name}', description = '{description}', price = '{price}', category = '{category}', address = '{address}', state = '{AdvertState.waitingAppoval}' WHERE id = '{advertId}'")
    dbCon.commit()

    #если загружены новые фотографии, старые удаляются
    if len(allowedFiles) > 0:
        dbCur.execute(f"DELETE from advert_picture WHERE advert_id = '{advertId}'")
        dbCon.commit()

        for file in uploadedFiles:
            if file.filename != '':
                fileType = file.filename.rsplit('.', 1)[1].lower()
                if fileType in appSettings['allowedFileTypes']:
                    fileName = str(uuid.uuid4()) + '.' + fileType #сохраняем под уникальным именем
                    file.save('baraholka/static/userFiles/' + fileName)

                    main = 'FALSE'
                    if len(allowedFiles) < 2:
                        main = 'TRUE'
                    else:
                        if chosenFile is None:
                            if file == allowedFiles[0]:
                                main = 'TRUE'
                        else:
                            if chosenFile == file.filename:
                                main = 'TRUE'

                    dbCur.execute(f"INSERT INTO advert_picture (advert_id, file_path, main) VALUES ('{advertId}', 'static/userFiles/{fileName}', '{main}')")


        dbCon.commit()


    return redirect(f'/advert/{advertId}/')



@app.route('/test/')
def testPage():
    return render_template("test.html")

@app.route('/test/requestUpdate', methods=['POST'])
def testPost():
    textInput = request.form.get('textInput')
    resultDict = {
        'success': True,
        'valuesArray':
        [textInput, textInput * 2, textInput * 3]
    }

    return json.dumps(resultDict)






@app.route('/chat/<uuid:advertId>/<uuid:buyerId>/')
def chatPage(advertId = None, buyerId = None):
    if not current_user.is_authenticated:
        return redirect('/login/')

    if current_user.isModerator:
        return redirect('/')

    if advertId is None or buyerId is None:
        return redirect('/chat/')

    buyerId = str(buyerId)
    advertId = str(advertId)

    searchEntry = request.args.get('search')
    searchCategory = request.args.get('category')
    if searchEntry is not None or searchCategory is not None:
        return redirect(url_for('mainPage', **request.args))

    dbCur.execute(f"SELECT name, state, user_id FROM advert WHERE id = '{advertId}'")
    result = dbCur.fetchone()
    if result is None or result[1] != AdvertState.approved:
        return redirect('/')

    if result[2] != current_user.get_id() and current_user.get_id() != buyerId:
        return redirect('/')

    advertName = result[0]
    advertLink = f'/advert/{advertId}/'

    return render_template("chat.html", searchCategories = getSearchCategories(searchCategory), advertName = advertName, advertLink = advertLink)



@app.route('/chat/<uuid:advertId>/<uuid:buyerId>/update', methods=['POST'])
def chatPost(advertId = None, buyerId = None):
    if not current_user.is_authenticated:
        return redirect('/login/')

    if current_user.isModerator:
        return redirect('/')

    if advertId is None or buyerId is None:
        return redirect('/')

    buyerId = str(buyerId)
    advertId = str(advertId)

    searchEntry = request.args.get('search')
    searchCategory = request.args.get('category')
    if searchEntry is not None or searchCategory is not None:
        return redirect(url_for('mainPage', **request.args))

    dbCur.execute(f"SELECT name, state, user_id FROM advert WHERE id = '{advertId}'")
    result = dbCur.fetchone()
    if result is None or result[1] != AdvertState.approved:
        return redirect('/')

    advertOwnerId = result[2]

    if result[2] != current_user.get_id() and current_user.get_id() != buyerId:
        return redirect('/')

    messagesUpdated = False #если появилось новое(ые) сообщение(ия) (либо то, которое этим запросом отправил текущий пользователь, либо от другого пользователя)

    messageInput = request.form.get('messageInput')
    lastMessageTimestamp = request.form.get('lastMessageTimestamp')

    if messageInput is not None and messageInput != '':
        if current_user.get_id() == advertOwnerId:
            receiver_id = buyerId
        else:
            receiver_id = advertOwnerId
        dbCur.execute(f"INSERT INTO message (sender_id, receiver_id, advert_id, text) VALUES ('{current_user.get_id()}', '{receiver_id}', '{advertId}', '{messageInput}')")
        dbCon.commit()
        messagesUpdated = True



    if lastMessageTimestamp is None:
        messagesUpdated = True
    else:
        dbCur.execute(f"SELECT datetime FROM message WHERE (sender_id = '{buyerId}' OR sender_id = '{advertOwnerId}') AND (receiver_id = '{buyerId}' OR receiver_id = '{advertOwnerId}') AND advert_id = '{advertId}' ORDER BY datetime DESC LIMIT 1")
        result5 = dbCur.fetchone()

        if result5 is not None and result5[0].timestamp() > float(lastMessageTimestamp):
            messagesUpdated = True



    resultDict = {'messagesUpdated': messagesUpdated}

    if messagesUpdated:
        resultDict['messages'] = []

        dbCur.execute(f"SELECT firstname FROM appuser WHERE id = '{buyerId}'")
        result2 = dbCur.fetchone()
        buyerFirstName = result2[0]

        dbCur.execute(f"SELECT firstname FROM appuser WHERE id = '{advertOwnerId}'")
        result4 = dbCur.fetchone()
        advertOwnerFirstName = result4[0]

        dbCur.execute(f"SELECT text, datetime, sender_id FROM message WHERE (sender_id = '{buyerId}' OR sender_id = '{advertOwnerId}') AND (receiver_id = '{buyerId}' OR receiver_id = '{advertOwnerId}') AND advert_id = '{advertId}' ORDER BY datetime ASC")
        result3 = dbCur.fetchall()

        if result3 is not None:
            for msg in result3:
                if msg[2] == buyerId:
                    senderFirstName = buyerFirstName
                else:
                    senderFirstName = advertOwnerFirstName

                if msg[2] == current_user.get_id():
                    style = MessageStyle.byThisUser
                else:
                    style = MessageStyle.byOtherUser


                datetime = f'{str(msg[1].day).rjust(2, "0")}.{str(msg[1].month).rjust(2, "0")}.{msg[1].year} в {str(msg[1].hour).rjust(2, "0")}:{str(msg[1].minute).rjust(2, "0")}'

                resultDict['messages'].append({
                    'text': msg[0],
                    'datetime': datetime,
                    'senderFirstname': senderFirstName,
                    'style': style
                })

        resultDict['lastMessageTimestamp'] = result3[-1][1].timestamp()

    return json.dumps(resultDict)







@app.route('/chat/')
@app.route('/chat/<int:page>/')
def chastListPage(page = None):
    if page is not None:
        if page == 1:
            return redirect('/chat/')
    else:
        page = 1


    if not current_user.is_authenticated:
        return redirect('/login/')

    if current_user.isModerator:
        return redirect('/')

    searchEntry = request.args.get('search')
    searchCategory = request.args.get('category')
    if searchEntry is not None or searchCategory is not None:
        return redirect(url_for('mainPage', **request.args))



    desiredNumberOfPages = 5 #сколько хотим кнопок навигации по страницам
    desiredChatsPerPage = 10 #сколько хотим чатов на одной странице

    dbCur.execute(f"SELECT * FROM (SELECT DISTINCT ON (advert_id) sender_id, receiver_id, advert_id, datetime, text FROM message WHERE sender_id = '{current_user.get_id()}' OR receiver_id = '{current_user.get_id()}' ORDER BY advert_id, datetime DESC) AS s ORDER BY datetime DESC OFFSET {(page - 1) * desiredChatsPerPage} LIMIT {desiredChatsPerPage * desiredNumberOfPages}")
    result = dbCur.fetchall()

    chatPreviews = []
    i = 0

    if result is not None:
        for chat in result:
            if i >= desiredChatsPerPage:
                break

            senderId = chat[0]
            receiverId = chat[1]
            advertId = chat[2]
            msgText = chat[4]

            dbCur.execute(f"SELECT name, state, user_id FROM advert WHERE id = '{advertId}'")
            result2 = dbCur.fetchone()
            advertName = result2[0]
            advertState = result2[1]
            advertOwnerId = result2[2]

            # if advertState != AdvertState.approved and advertState != AdvertState.archived:
            #     continue

            dbCur.execute(f"SELECT file_path FROM advert_picture WHERE advert_id = '{advertId}' AND main = 'TRUE' LIMIT 1")
            result3 = dbCur.fetchone()
            imagePath = result3[0]

            if current_user.get_id() == senderId:
                idToSearch = receiverId
            else:
                idToSearch = senderId
            dbCur.execute(f"SELECT firstname, id FROM appuser WHERE id = '{idToSearch}'")
            result4 = dbCur.fetchone()
            otherUserName = result4[0]
            otherUserId = result4[1]

            if senderId == current_user.get_id():
                lastMessagePreview = 'Вы: '
            else:
                lastMessagePreview = f'{otherUserName}: '
            lastMessagePreview += msgText

            if senderId == advertOwnerId:
                buyerId = receiverId
            else:
                buyerId = senderId
            link = f'/chat/{advertId}/{buyerId}/'

            chatPreviews.append(ChatPreview(advertName, otherUserName, lastMessagePreview, link, imagePath))
            i += 1


    return render_template("chatslist.html", searchCategories = getSearchCategories(searchCategory), chatPreviews = chatPreviews, pageButtons = getPageButtons(page, len(result), desiredChatsPerPage, desiredNumberOfPages, 'chastListPage') )