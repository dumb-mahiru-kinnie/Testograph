import tkinter as tk
import tkinter.ttk as ttk
from requests import get
from ttkthemes import ThemedTk
from functools import partial
from io import BytesIO
from PIL import Image, ImageTk
from random import sample
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
class Testograph():
    def __init__(self):
        self.main = self.new_window()
        # self.main.iconphoto(True, tk.PhotoImage(file='icon.png'))

        canvas1 = tk.Canvas(self.main, height=3, width=500)
        canvas1.pack(side='top')
        canvas1.create_line(0, 3, 500, 3)

        canvas = tk.Canvas(self.main, height=465, width=500, background='#e6e6e6')
        frame = tk.Frame(canvas, background='#e6e6e6')
        scroll = tk.Scrollbar(self.main, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        canvas.pack(side='top')
        canvas.create_window((0,0), window=frame)
        frame.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))


        all_tests = get('https://pastebin.com/raw/jgUTbHhU').text.replace('\r', '').split('\n')
        self.tests_dict = {}
        for item in all_tests:
            if item.startswith('----'): # если это название теста
                name_of_test = item[4:]
                self.tests_dict[name_of_test] = {}
                self.tests_dict[name_of_test]['properties'] = []
            elif item.startswith('=='): # если это картинка теста
                self.tests_dict[name_of_test]['picture'] = item[2:]
            elif item.startswith('!'):
                self.tests_dict[name_of_test]['preview_txt'] = item[1:]
            elif item.startswith('?'):
                self.tests_dict[name_of_test]['preview_pic'] = item[1:]
            else: # если это внутренности теста
                item = item.split(' : ')
                self.properties = []
                self.properties.append(item[0]) # это тип вопроса
                self.properties.append(item[1]) # это сам вопрос
                self.properties.append(item[2]) # это ссыль на картинку
                if item[0] == 'RADIO' or item[0] == 'ENTRY': # если радио
                    self.properties.append(item[3].split(' || ')) # это варианты ответа
                elif item[0] == 'CHECK': # если вариантов ответа несколько
                    list_for_check_properties = []
                    for answer_bundle in item[3].split(' // ', 1):
                        # сначала я разделяю ответы на правильные и неправильные с //
                        list_for_check_properties.append(answer_bundle.split(' || '))
                        # а здесь я уже дальше дроблю ответы на отдельные
                    self.properties.append(list_for_check_properties)
                self.tests_dict[name_of_test]['properties'].append(self.properties)
                # то есть вместо одного ответа здесь теперь список со списками
                #[['правильный ответ 1', 'правильный ответ 2'], ['неправильный ответ 1', 'неправильный ответ 2']]
        # результат:
        # словарь со всеми тестами. в таких словарях ещё словарик с картинкой
        # если есть и со всеми вопросами в виде списков. затем в каждом вопросе 
        # есть тип, сам вопрос, картинка к вопросу и варианты ответа (картинка в виде ссылки)
        self.imglist = []
        # все картинки нужно обязательно в список а то ткинтер не поймёт КУДА ЖЕ ДЕЛИСЬ КАРТИНКИ
        for item in self.tests_dict.keys():
            if 'picture' in (self.tests_dict[item]).keys(): # если картинка есть
                pilpic = BytesIO(get(self.tests_dict[item]['picture']).content)
                pilpic = Image.open(pilpic)
                pilpic.thumbnail((300, 300), Image.ANTIALIAS)
                pilpic = ImageTk.PhotoImage(pilpic)
                self.imglist.append(pilpic)
                btn = ttk.Button(frame, 
                    image=pilpic, 
                    text=item,
                    command=partial(self.preview_show, item),
                    compound='top',
                    width=80
                )
            else: # мы принимаем (и хотим) кнопки без картинок
                btn = ttk.Button(frame, text=item, command=partial(self.preview_show, item), width=80)
            btn.pack()
        ttk.Button(self.main, text="Создать новый тест", command=partial(self.new_test)).pack()
    def new_window(self, toplevel=False):
        if toplevel:
            w = tk.Toplevel()
        else:
            w = ThemedTk(theme='arc')
        w.title('Тестограф')
        w.geometry('500x500')
        w.configure(bg='white')
        w.resizable(width=False, height=False)
        return w
    def preview_show(self, item):
        '''
        я очень не хотел превью.
        но для того, чтобы словарик с ответами заработал,
        нужно его создавать в отдельном окне. иначе бы
        он перезаписывался с каждым новым вопросом
        (словарик действует на каждый тест, не на каждое окно)
        '''
        self.current = item
        self.answers = {}
        self.entry = None
        # почему словарь?
        # если бы это был список, то при переключении назад
        # вопрос бы записывался опять, а не обновлялся. это
        # можно было бы пофиксить простой проверкой, но мне
        # просто больше нравятся словари
        self.preview = self.new_window()
        ttk.Button(self.preview, text='=>', command=partial(self.progress, 0)).pack()
        # ВНИМАНИЕ: надо заняться превью, это очень важная часть теста
        # а как ещё узнать, на правильный тест ты нажал или нет?
        # максимум мне кажется в превью должно быть 3 картинки
    def progress(self, pos, action=None, field=None):
        self.prop = (self.tests_dict[self.current])['properties']
        data = self.prop[pos] # мы берём внутренности вопроса
        if field != None:
            if action == '+':
                self.answers[self.prop[pos - 1]] = (field.get()).strip()
            elif action == '-':
                self.answers[self.prop[pos + 1]] = (field.get()).strip()
        if pos == 0:
            self.preview.destroy()
        else:
            self.cw.destroy() # может быть только одно окно с вопросом за раз

        self.cw = self.new_window(toplevel=True)

        answer = None
        ttk.Label(self.cw, text=data[1], font=16).pack()
        if data[2] != 'None': # если есть картинка
            image = get(data[2]).content
            image = Image.open(BytesIO(image))
            image.thumbnail((200, 500), Image.ANTIALIAS)
            image = ImageTk.PhotoImage(image)
            img = ttk.Label(self.cw, image=image)
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
                ttk.Radiobutton(self.cw, text=variant, variable=answer, value=variant, command=partial(self.radio_func, data, variant)).pack()
        elif data[0] == 'CHECK': # если это вопрос с несколькими вариантами ответа
            self.answers[data[1]] = [] # в словаре с ответами создаётся список
            flattened = data[3][0] + data[3][1] # sample не будет работать с списком со списками
            # он бы просто перемешал списки, которые есть, а не сами ответы в них
            shuffled = sample(flattened, len(flattened))
            for variant in shuffled:
                ttk.Checkbutton(self.cw, text=variant, variable=answer, 
                    command=partial(lambda: (self.answers[data[1]]).append(variant))
                ).pack()
                # главное изменение -- Checkbutton
        elif data[0] == 'ENTRY':
            self.entry_answer = tk.StringVar()
            ttk.Entry(self.cw, textvariable=self.entry_answer, width=50).pack()
        else:
            raise ValueError('Unsupported question type')
        if data != self.prop[-1]:
            if data[0] == 'ENTRY':
                right = ttk.Button(self.cw, text='=>', command=partial(self.progress, (pos + 1), action='+', field=self.entry_answer))
            else:
                right = ttk.Button(self.cw, text='=>', command=partial(self.progress, (pos + 1)))
            right.pack(side = 'right')
        else:
            # кнопка последняя
            ttk.Button(self.cw, text='Отправить результаты', command=partial(self.get_results)).pack(side='right')
        
        if data != self.prop[0]: # если это не первый вопрос
            if data[0] == 'ENTRY':
                left = ttk.Button(self.cw, text='<=', command=partial(self.progress, (pos - 1), action='-', field=self.entry_answer))
            else:
                left = ttk.Button(self.cw, text = '<=' , command = partial(self.progress, (pos - 1)))
            left.pack(side = 'left')
    def radio_func(self, data, variant):
        self.answers[data[1]] = variant
    def get_results(self):
        data = self.tests_dict[self.current]['properties']
        if data[-1][0] == 'ENTRY':
            self.answers[data[-1][1]] = self.entry_answer.get()
        self.cw.destroy() # всегда будет предыдущее окно
        all_count = [0, 0, 0] # правильные, неправильные, пропущенные
        wrongs = {} # это словарь с неправильными вопросами и их позициями
        rights = [] # это список с правильными вопросами (он почти не нужен)
        for pos, each_a in enumerate(self.answers.values()):
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
        results = self.new_window(toplevel=True)
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
        description = f'Вы прошли тест «{self.current}» на {len(rights)} {bll} из {all_questions}'
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
    def new_test(self):
        self.title = self.new_window(toplevel=True)
        ttk.Label(self.title, text="Назовите свой тест", font=18).pack()
        self.title_a = tk.StringVar()
        ttk.Entry(self.title, textvariable=self.title_a, width=50).pack()
        ttk.Label(self.title, text="Текст превью", font=18).pack()
        self.preview_text = tk.StringVar()
        ttk.Entry(self.title, textvariable=self.preview_text, width=50).pack()
        ttk.Label(self.title, text="Ссылка на картинку в главном меню", font=18).pack()
        self.main_img_link = tk.StringVar()
        ttk.Entry(self.title, textvariable=self.main_img_link, font=18, width=50).pack()
        ttk.Label(self.title, text="Ссылка на картинку в превью", font=18).pack()
        self.preview_img_link = tk.StringVar()
        ttk.Entry(self.title, textvariable=self.preview_img_link, width=50).pack()
        ttk.Button(self.title, text="Далее", command=partial(self.create_progress, 0)).pack()
    def create_progress(self, pos):
        if pos == 0:
            self.created_test = {self.title_a.get().strip(): {
                'picture': self.main_img_link.get().strip(),
                'properties': [],
                'preview_txt': self.preview_text.get().strip(),
                'preview_pic': self.preview_img_link.get().strip()
            }}
            self.title.destroy()
        else:
            self.question.destroy()
        self.question = self.new_window(toplevel=True)

        ttk.Label(self.question, text="Выберите тип вопроса", font=18).pack()
        question_type = tk.StringVar()
        for each_type in ["RADIO", "CHECK", "ENTRY"]:
            ttk.Radiobutton(self.question, text=each_type, variable=question_type, value=each_type, command=partial(self.reset, each_type)).pack()

        question_txt = tk.StringVar()
        ttk.Label(self.question, text="Текст вопроса", font=18).pack()
        ttk.Entry(self.question, textvariable=question_txt, width=50).pack()
        
        canvas = tk.Canvas(self.question, height=300, width=500, background='#e6e6e6')
        self.frame = tk.Frame(canvas, background='#e6e6e6')
        scroll = tk.Scrollbar(self.question, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill='y')
        canvas.pack()
        canvas.create_window((0,0), window=self.frame)
        self.frame.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
    def reset(self, type):
        for child in self.frame.winfo_children():
            child.destroy()
        ttk.Button(self.frame, text="Добавить вариант ответа", command=partial(self.add_variant, type)).pack()
    def add_variant(self, type):
        if type == "RADIO":
            variant = tk.StringVar()
            right_answer = tk.StringVar()
            ttk.Radiobutton(self.frame, 
                text=ttk.Entry(self.frame, textvariable=variant, width=20).pack(), 
                textvariable=right_answer, value=variant.get(), command=(lambda: print(right_answer.get()))
            ).pack()
            # ЧТО ЭТО -- это поле внутри радиокнопки, также называемое смертью.
            # TODO: пофиксить выбирание всех кнопок за раз
            # это, наверно, легко сделать, но мои мозги слишком прожаренные для этого. спокойной ночи.
    def start(self):
        self.main.mainloop()
Testograph().start()
