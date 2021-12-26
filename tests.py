import requests # не встроено
import tkinter as Tk # ТОЛЬКО ДЛЯ САМОГО ОКНА
import tkinter.ttk as ttk # всё остальноe
from ttkthemes import ThemedTk  # для красоты. не встроено
from functools import partial # костыль
from PIL import Image, ImageTk # картинки
from random import sample  # перемешать варианты
from io import BytesIO # перевод байтов в картинку и наоборот
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# график matplotlib в окне tkinter
import matplotlib.pyplot as plt # график
# from creator_tool import create_window

w = ThemedTk(theme='arc')
w.title('Тестограф')
w.geometry('500x500')
w.configure(bg='white')
w.resizable(width=False, height=False) # мне лень
# w.iconphoto(True, Tk.PhotoImage(file='icon.png')) 
# True -- иконка используется для всех окон
# Tk.PhotoImage() -- Tkinter поддерживает только какие-то древние
# форматы файлов. Приходится оборачивать
# logged_in = False

# def send_login(name, password, login_window, error_widget):
#     recieved = requests.get('https://pastebin.com/raw/mCrU24mG').text.replace('\r', '').split('\n')
#     for account in recieved:
#         account = account.split(', ')
#     print(recieved)
#     for acc in recieved:
#         if name.get() in acc and password.get() in acc:
#             logged_in = True
#             login_window.destroy()
#             login_btn.configure(state='disabled', text=f'Доброго времени суток, {name.get()}!')
#         else:
#             error_widget.configure(text='Или логин, или пароль неправильны.\nУверены, что ввели данные без ошибок?')

# def remember_me():
#     open('config.txt', 'a').close()
#     with open('config.txt', 'r+') as file:
#         boolean = file.read()
#         file.truncate(0)
#         if 'True' in boolean:
#             file.write('False')
#         else:
#             file.write('True')

# def login():
#     answer = None
#     login = Tk.Toplevel()
#     login.title('Тестограф')
#     login.geometry('500x500')
#     login.configure(bg='white')
#     w.resizable(width=False, height=False)
#     name = Tk.StringVar()
#     password = Tk.StringVar()

#     ttk.Label(login, text='Вход', font=('bold', 28)).pack(side='top')
#     ttk.Label(login, text='Фамилия и имя', font=16).pack(side='top')
#     ttk.Entry(login, textvariable=name).pack(side='top')
#     ttk.Label(login, text='Назначенный пароль', font=16).pack(side='top')
#     ttk.Entry(login, textvariable=password, show='*').pack(side='top')
#     error_widget = ttk.Label(login, text='', font='bold')
#     error_widget.pack(side='bottom')
#     # remember_btn = ttk.Checkbutton(login, text='Запомнить меня', variable=answer, command=partial(remember_me))
#     # remember_btn.pack(side='top')
#     ttk.Button(login, text='Войти', command=partial(send_login, name, password, login, error_widget)).pack(side='top')


# login_btn = ttk.Button(w, text="Войти (регистрация по приглашениям)", command=login)
# login_btn.pack(side='top')
# ttk.Button(w, text='Создать тест', command=create_window).pack(anchor='ne')

canvas1 = Tk.Canvas(w, height=3, width=500) # холст для разделителя
canvas1.pack(side='top')

canvas1.create_line(0, 3, 500, 3)


canvas = Tk.Canvas(w, height=465, width=500, background='#e6e6e6')
frame = Tk.Frame(canvas, background='#e6e6e6')
scroll = Tk.Scrollbar(w, orient='vertical', command=canvas.yview)
canvas.configure(yscrollcommand=scroll.set)
# этот код создаёт холст tkinter с кнопками, по которому можно двигать колёсиком

scroll.pack(side='right', fill='y')
canvas.pack(side='top')
canvas.create_window((0,0), window=frame)
frame.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
# я не точно понимаю, что это делает. первые три строчки -- перемещение холста,
# последняя -- не знаю что. но аргумент event обязателен

all_tests = requests.get('https://pastebin.com/raw/jgUTbHhU').text.replace('\r', '').split('\n')
tests_dict = {}
for item in all_tests:
    if item.startswith('----'): # если это название теста
        name_of_test = item[4:]
        tests_dict[name_of_test] = {}
        tests_dict[name_of_test]['properties'] = []
    elif item.startswith('=='): # если это картинка теста
        tests_dict[name_of_test]['picture'] = item[2:]
    else: # если это внутренности теста
        item = item.split(' : ')
        properties = []
        properties.append(item[0]) # это тип вопроса
        properties.append(item[1]) # это сам вопрос
        properties.append(item[2]) # это ссыль на картинку
        if item[0] == 'RADIO' or item[0] == 'ENTRY': # если радио
            properties.append(item[3].split(' || ')) # это варианты ответа
        elif item[0] == 'CHECK': # если вариантов ответа несколько
            list_for_check_properties = []
            for answer_bundle in item[3].split(' // ', 1):
                # сначала я разделяю ответы на правильные и неправильные с //
                list_for_check_properties.append(answer_bundle.split(' || '))
                # а здесь я уже дальше дроблю ответы на отдельные
            properties.append(list_for_check_properties)
        tests_dict[name_of_test]['properties'].append(properties)
        # то есть вместо одного ответа здесь теперь список со списками
        #[['правильный ответ 1', 'правильный ответ 2'], ['неправильный ответ 1', 'неправильный ответ 2']]
# результат:
# словарь со всеми тестами. в таких словарях ещё словарик с картинкой
# если есть и со всеми вопросами в виде списков. затем в каждом вопросе 
# есть тип, сам вопрос, картинка к вопросу и варианты ответа (картинка в виде ссылки)

def preview_show(arg):
    '''
    я очень не хотел превью.
    но для того, чтобы словарик с ответами заработал,
    нужно его создавать в отдельном окне. иначе бы
    он перезаписывался с каждым новым вопросом
    (словарик действует на каждый тест, не на каждое окно)
    '''
    global preview, answers
    answers = {}
    # почему словарь?
    # если бы это был список, то при переключении назад
    # вопрос бы записывался опять, а не обновлялся. это
    # можно было бы пофиксить простой проверкой, но мне
    # просто больше нравятся словари
    preview = ThemedTk(theme='arc')
    preview.title('Тестограф')
    preview.geometry('500x500')
    preview.configure(bg='white')
    preview.resizable(width=False, height=False)
    right = ttk.Button(preview, text='=>', command=partial(new_window, arg, 0, None))
    right.pack()
    # ВНИМАНИЕ: надо заняться превью, это очень важная часть теста
    # а как ещё узнать, на правильный тест ты нажал или нет?
    # максимум мне кажется в превью должно быть 3 картинки
def new_window(arg, pos, okno, action=None, field=None):
    '''
    arg это название теста
    pos номер текущего вопроса
    okno окно предыдущего вопроса
    '''
    prop = (tests_dict[arg])['properties']
    data = prop[pos] # мы берём внутренности вопроса
    if field != None:
        if action == '+':
            answers[prop[pos - 1]] = field.get()
        elif action == '-':
            answers[prop[pos + 1]] = field.get()
    if pos == 0:
        preview.destroy()
    else:
        okno.destroy() # может быть только одно окно с вопросом за раз

    test_new = Tk.Toplevel() # photoimage нельзя использовать когда два окна Tk
    test_new.title('Тестограф')
    test_new.geometry('500x500')
    test_new.configure(bg='white') # белый фон
    test_new.resizable(width=False, height=False)

    answer = None
    question = ttk.Label(test_new, text=data[1], font=16) # сам вопрос
    question.pack()
    if data[2] != 'None': # если есть картинка
        image = requests.get(data[2]).content
        image = Image.open(BytesIO(image))
        image.thumbnail((200, 500), Image.ANTIALIAS)
        image = ImageTk.PhotoImage(image)
        img = ttk.Label(test_new, image=image)
        img.pack()
        img.image = image
        # я ненавижу ткинтер
    if data[0] == 'RADIO':
        # заметка
        # здесь большое количество кода было перенесено за if, так что он сработает даже если
        # вопрос не радио. это важно для нового типа вопроса check
        shuffled = sample(data[3], len(data[3]))
        for variant in shuffled:
            # answer для красоты (без него сами кнопки не работают). всё делается через command
            radio = ttk.Radiobutton(test_new, text=variant, variable=answer, value=variant, command=partial(setans_radio, data, variant))
            radio.pack()
    elif data[0] == 'CHECK': # если это вопрос с несколькими вариантами ответа
        answers[data[1]] = [] # в словаре с ответами создаётся список
        flattened = data[3][0] + data[3][1] # sample не будет работать с списком со списками
        # он бы просто перемешал списки, которые есть, а не сами ответы в них
        shuffled = sample(flattened, len(flattened))
        for variant in shuffled:
            check = ttk.Checkbutton(test_new, text=variant, variable=answer, command=partial(setans_check, data, variant))
            check.pack()
            # главное изменение -- Checkbutton
    elif data[0] == 'ENTRY':
        global entry_answer
        entry_answer = Tk.StringVar()
        entry_field = ttk.Entry(test_new, textvariable=entry_answer, width=50)
        entry_field.pack()
    else:
        raise ValueError('Unsupported question type')
    if data != prop[-1]:
        if data[0] == 'ENTRY':
            right = ttk.Button(test_new, text = '=>' , command = partial(new_window, arg, (pos + 1), test_new, action='+', field=entry_answer))
        else:
            right = ttk.Button(test_new, text='=>', command=partial(new_window, arg, (pos + 1), test_new))
        right.pack(side = 'right')
    else:
        # кнопка последняя
        right = ttk.Button(test_new, text='Отправить результаты', command=partial(get_results, arg, test_new))
        right.pack(side='right')
    
    if data != prop[0]: # если это не первый вопрос
        if data[0] == 'ENTRY':
            left = ttk.Button(test_new, text = '<=' , command = partial(new_window, arg, (pos - 1), test_new, action='-', field=entry_answer))
        else:
            left = ttk.Button(test_new, text = '<=' , command = partial(new_window, arg, (pos - 1), test_new))
        left.pack(side = 'left')
    

def setans_radio(data, answ):
    answers[data[1]] = answ
# я хотел это сделать через lambda, но были проблемы с синтаксисом

def setans_check(data, answ):
    answers[data[1]].append(answ)
# так как там список, надо использовать append

def get_results(arg, okno):
    '''
    arg, можно догадаться, название теста
    okno окно последнего вопроса (это можно было бы сделать легче,
    был бы я хорош в поле видимости)
    я уже хорош потому что использую классы где не нужно поле видимости
    '''
    data = tests_dict[arg]['properties']
    if data[-1][0] == 'ENTRY':
        answers[data[-1][1]] = entry_answer.get()
    okno.destroy() # всегда будет предыдущее окно
    all_count = [0, 0, 0] # правильные, неправильные, пропущенные
    wrongs = {} # это словарь с неправильными вопросами и их позициями
    rights = [] # это список с правильными вопросами (он почти не нужен)
    for pos, each_a in enumerate(answers.values()):
        if data[pos][0] == 'ENTRY':
            if each_a in data[pos][3]:
                all_count[0] += 1
                rights.append(data[pos][1])
            elif each_a == '':
                all_count[2] += 1
            else:
                all_count[1] += 1
                wrongs[data[pos][1]] = pos
        else:
            if each_a == data[pos][3][0]:
                # tests_dict -- все тесты, arg -- название определённого теста,
                # pos -- номер определённого вопроса, 3 -- ответы в нём
                # хорошо, что я в самом начале решил, что первый ответ всегда правилен
                # (НЕ ПРИМЕНЯТЬ В РЕАЛЬНОЙ ЖИЗНИ)
                all_count[0] += 1
                rights.append(data[pos][1]) # правильный вопрос добавлен
            elif each_a == []: # это значит, что вопрос с несколькими вариантами ответов пропущен
                # если подумать, есть же вопросы с подвохом, в которых правильных ответов нет?
                # это для меня слишком злобно и я не хочу это добавлять
                all_count[2] += 1
            else:
                wrongs[data[pos][1]] = pos
                # в словарь добавляется ключ (неправильный вопрос) со значением (его позицией)
                all_count[1] += 1
    all_count[2] += len(data) - sum(all_count)
    all_questions = sum(all_count) # это вообще сколько вопросов во всём тесте
    # потом можно добавить "пропущенность" не через просто вычитание.
    # но с этим были непонятки так что ¯\_(ツ)_/¯
    # этот комментарий частично устарел, это было частично добавлено
    names = ['Правильно', 'Неправильно', 'Пропущено']
    colors = ['yellowgreen', 'red', '#999999']
    for each_num_num, each_num in enumerate(all_count):
        # что такое each_num_num?!
        # номер числа, как бы странно это ни звучало
        if each_num == 0:
            del all_count[each_num_num]
            del names[each_num_num]
            del colors[each_num_num]
            # нулевые значения на диаграмме плохо выглядят
    results = Tk.Toplevel() # photoimage нельзя использовать когда два окна Tk
    results.title('Тестограф')
    results.geometry('500x500')
    results.configure(bg='white')
    results.resizable(width=False, height=False)
    fig = plt.figure(figsize=(4,2)) # вот здесь уже сложненько
    # это фигура, в которую будет помещена наша круговая диаграмма
    p1 = fig.add_subplot(111) # это как бы для диаграммы, не меняй здесь числа нигде, пожалуйста
    # я слишком долго старался, чтобы сделать диаграмму хотя бы читаемой
    p1.pie(all_count, labels=names, colors=colors, autopct=lambda p: f'{p*sum(all_count)/100 :.0f}')
    # autopct делает количество каждого типа ответов. я не знаю, что такое :.0f, правда
    canvas_new = FigureCanvasTkAgg(fig, master=results)
    # это холст для диаграммы в окне
    canvas_new.get_tk_widget().pack(side='top') # здесь он перемещается
    lastnum = str(len(rights)) # это всё число правильных ответов в строковом формате, нужно для
    # склонения слова "балл"
    if lastnum.endswith('1') and not lastnum.endswith('11'):
        # если число заканчивается на один, но не на одиннадцать
        bll = 'балл'
    elif (lastnum[-1] in ['2', '3', '4']):
        # если число заканчивается на любое из чисел в списке
        try:
            if not lastnum[-2] == '1': # если это не 12, 13 или 14
                bll = 'балла'
        except IndexError:
            # если в числе меньше двух цифр (то есть 12, 13, 14 быть не может)
            bll = 'балла'
    else:
        # любые другие случаи
        bll = 'баллов'
    description = f'Вы прошли тест «{arg}» на {len(rights)} {bll} из {all_questions}'
    # пример: Вы прошли тест «Обыкновенные дроби» на 10 баллов из 10
    if (len(rights) / all_questions) >= 0.9: # если правильно 90% или более
        description += '! \nФеноменально!'
    elif (len(rights) / all_questions) >= 0.7: # если 70% или более
        description += '! \nТак держать!'
    else:
        description += '.' # не будем обижать бедного юзера-троечника )))
    if wrongs != {}: # если вообще есть неправильные ответы
        description += '\nВот в каких вопросах ошибки:'
        for wrong, position in wrongs.items():
            description += f'\n{position + 1}. {wrong}'
            # пример: 1. Какая первая буква в алфавите?
            # заметка: position начинается с 0, так что нужно прибавить 1
    ttk.Label(results, text=description, font=18).pack(side='top')


imglist = []
# все картинки нужно обязательно в список а то ткинтер не поймёт КУДА ЖЕ ДЕЛИСЬ КАРТИНКИ
for item in tests_dict.keys():
    if 'picture' in (tests_dict[item]).keys(): # если картинка есть
        pilpic = BytesIO(requests.get(tests_dict[item]['picture']).content)
        pilpic = Image.open(pilpic)
        pilpic.thumbnail((300, 300), Image.ANTIALIAS)
        pilpic = ImageTk.PhotoImage(pilpic)
        imglist.append(pilpic)
        btn = ttk.Button(frame, 
            image=pilpic, 
            text=item,
            command=partial(preview_show, item),
            compound='top',
            width=80
        )
    else: # мы принимаем (и хотим) кнопки без картинок
        btn = ttk.Button(frame, text=item, command=partial(preview_show, item), width=80)
    btn.pack()

w.mainloop()