from baraholka import *



class User(UserMixin):
    id = None
    email = None
    password = None
    firstname = None
    lastname = None
    phone = None
    isModerator = None

    def get_id(self = None):
        return User.id


    @property
    def is_active(self):
        return self.is_active

    @property
    def is_authenticated(self):
        return self.is_authenticated

    @property
    def is_anonymous(self):
        return self.is_anonymous


    @staticmethod
    @login_manager.user_loader
    def loadById(id):
        n = 10
        for i in range(n):
            try:
                dbCur.execute(f"SELECT * FROM appuser WHERE id = '{id}'")
                result = dbCur.fetchone()
                break
            except:pass

        print(f'user_loader n = {i}')

        if result is None:
            User.id = None
            User.email = None
            User.password = None
            User.firstname = None
            User.lastname = None
            User.phone = None
            User.isModerator = None

            return None

        else:
            User.id = result[0]
            User.email = result[1]
            User.password = result[2]
            User.firstname = result[3]
            User.lastname = result[4]
            User.phone = result[5]
            User.isModerator = result[6]

            return User



class Advert():
    def __init__(self, id, name, price, state, imagePath = ''):
        self.name = name
        self.price = price
        self.link = '/advert/' + id + '/'
        self.image = AdvImage(imagePath, 270, 180)
        self.state = state


class AdvertBig():
    def __init__(self, name, description, price, category, address, datetime:datetime.datetime, userFirstname, userPhone, state, buttonsType, imagesPaths):
        self.name = name
        self.description = description
        self.price = formatPrice(price)
        self.category = category
        self.address = address
        self.datetime = f'{str(datetime.day).rjust(2, "0")}.{str(datetime.month).rjust(2, "0")}.{datetime.year} в {str(datetime.hour).rjust(2, "0")}:{str(datetime.minute).rjust(2, "0")}'
        self.user_phone = userFirstname + '⠀✆' + userPhone
        self.state = state
        self.buttonsType = buttonsType

        self.images = []
        self.indicators = []
        for i in range(len(imagesPaths)):
            self.images.append(AdvImage(imagesPaths[i], 720, 400))

        if len(self.images) == 0:
            self.images.append(AdvImage('static/index/assets/img/nophoto.png', 720, 400))

        self.images[0].active = ' active'


        if len(imagesPaths) > 1:
            for i in range(len(imagesPaths)):
                self.indicators.append(CarouselIndicator(str(i)))

            self.indicators[0].active = 'active'




class EditAdvert():
    def __init__(self, name, description, price, address):
        self.name = name
        self.description = description
        self.price = price
        self.address = address


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



class Category():
    def __init__(self, name, isSelected = False):
        self.name = name

        if isSelected:
            self.selected = 'selected=""'
        else:
            self.selected = ''



class SortOption():
    def __init__(self, name, orderBy, direction, isSelected = False):
        self.name = name
        self.orderBy = orderBy
        self.direction = direction

        if isSelected:
            self.selected = 'selected=""'
        else:
            self.selected = ''



class ChatPreview():
    def __init__(self, advertName, otherUserName, lastMessagePreview, link, imagePath = ''):
        self.image = AdvImage(imagePath, 128, 87)
        self.advertName = advertName
        self.otherUserName = otherUserName
        self.link = link
        self.lastMessagePreview = lastMessagePreview





class AdvertState():
    waitingAppoval = 0
    approved = 1
    rejected = 2
    archived = 3


class AdvertButtonsType():
    noButtons = 0
    owner = 1
    moderator = 2
    registeredUser = 3


class MessageStyle():
    byThisUser = 0
    byOtherUser = 1


def formatPrice(price):
    if price is None or price == '':
        return 'Бесплатно'
    else:
        priceSplit = price.split(',')[0]
        if priceSplit == '0':
            priceSplit = 'Бесплатно'
        else:
            priceSplit += ' ₽'

        return priceSplit



#в result должны быть id, name, price, state
def getAdvertsGrid(result, desiredAdvertsPerPage):
    advertsGrid = []

    if result is None:
        return advertsGrid

    for i in range(0, desiredAdvertsPerPage, 3):
        if i >= len(result):
            break
        row = []

        for j in range(3):
            if i + j >= len(result) or i + j > desiredAdvertsPerPage - 1 :
                break

            dbCur.execute(f"SELECT file_path FROM advert_picture WHERE advert_id = '{result[i + j][0]}' AND main = 'TRUE' LIMIT 1")
            result2 = dbCur.fetchone()
            imagePath = ''
            if result2 is not None:
                imagePath = result2[0]

            row.append(Advert(result[i + j][0], result[i + j][1], formatPrice(result[i + j][2]), result[i + j][3], imagePath))

        if len(row) > 0:
            advertsGrid.append(row)

    return advertsGrid






def getPageButtons(page, lenResult, desiredAdvertsPerPage, desiredNumberOfPages, pageName, requestArgs = {}):
    if lenResult == 0:
        return [PageButton('disabled', '', '<'), PageButton('active', '#', str(page)), PageButton('disabled', '', '>')]

    foundAdvertsNumber = lenResult #сколько найдено объявлений (на этой странице и далее)

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
        prevButton = PageButton('', url_for(pageName, page = page - 1, **requestArgs), '<')

    #кнопка вправо
    if pagesAfterThis == 0:
        nextButton = PageButton('disabled', '', '>')
    else:
        nextButton = PageButton('', url_for(pageName, page = page + 1, **requestArgs), '>')



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
            pageButtons.append(PageButton('', url_for(pageName, page = pageNum, **requestArgs), str(pageNum)))
    pageButtons.append(nextButton)

    return pageButtons







def getCategories(currentCategory = None):
    dbCur.execute(f"SELECT name FROM category ORDER BY name")
    result = dbCur.fetchall()

    categories = []
    for r in result:
        categories.append(Category(r[0], (currentCategory is not None and r[0] == currentCategory)))

    return categories



def getSearchCategories(currentCategory = None):
    categories = getCategories(currentCategory)
    categories.insert(0, Category('Все категории', (currentCategory is None) ))
    return categories



def getSortOptions(currentOption = None):
    sortOptions = [
        SortOption('По дате (сначала новые)', 'datetime', 'DESC'),
        SortOption('По дате (сначала старые)', 'datetime', 'ASC'),
        SortOption('По цене (сначала дешевые)', 'price', 'ASC'),
        SortOption('По цене (сначала дорогие)', 'price', 'DESC')
    ]

    for opt in sortOptions:
        if opt.name == currentOption:
            opt.selected = 'selected=""'

    return sortOptions











def advertsListPage(page, pageName, request, fromCurrentUserOnly, allowedStates = [AdvertState.approved]):
    if page is not None:
        if page == 1:
            return redirect(url_for(pageName, **request.args))
    else:
        page = 1



    searchEntry = request.args.get('search')
    searchCategory = request.args.get('category')
    searchSort = request.args.get('sortby')

    if searchEntry == '':
        searchEntry = None
    if searchCategory == '' or searchCategory == 'Все категории':
        searchCategory = None
    if searchSort == '':
        searchSort = None



    sortOptions = getSortOptions(searchSort)

    if searchSort == None:
        searchSort = sortOptions[0].name

    sortSettings = None
    for opt in sortOptions:
        if opt.name == searchSort:
            sortSettings = opt
            break



    #формируем секцию WHERE
    where = ' WHERE'

    if len(allowedStates) > 0:
        where += f" ("

        for state in allowedStates:
            if state != allowedStates[0]:
                where += ' OR'
            where += f" state = '{state}'"

        where += f" )"


    if fromCurrentUserOnly:
        if where != ' WHERE':
            where += ' AND'
        where += f" user_id = '{current_user.id}'"

    if searchCategory is not None:
        if where != ' WHERE':
            where += ' AND'

        where += f" category = '{searchCategory}'"

    if searchEntry is not None:
        if where != ' WHERE':
            where += ' AND'

        where += f" LOWER(name) LIKE LOWER('%{searchEntry}%')"

        if where == ' WHERE':
            where =''


    desiredNumberOfPages = 5 #сколько хотим кнопок навигации по страницам
    desiredAdvertsPerPage = 9 #сколько хотим объявлений на одной странице


    dbCur.execute(f"SELECT id, name, price, state FROM advert{where} ORDER BY {sortSettings.orderBy} {sortSettings.direction} OFFSET {(page - 1) * desiredAdvertsPerPage} LIMIT {desiredAdvertsPerPage * desiredNumberOfPages}")
    result = dbCur.fetchall()

    return render_template('index.html', advertsGrid = getAdvertsGrid(result, desiredAdvertsPerPage), pageButtons = getPageButtons(page, len(result), desiredAdvertsPerPage, desiredNumberOfPages, pageName, request.args), searchCategories = getSearchCategories(searchCategory), sortOptions = sortOptions)