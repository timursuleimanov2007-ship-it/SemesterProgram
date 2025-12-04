import math


"""

Line    —   строка с текстом, сообщение пользователя;
stick   —   ключ-диаметр скиталы, число столбцов;
band    —   лента, список символов, из которых состоит строка с текстом;
far     —   число строк;
pear    —   номер символа в ленте, которая была получена из строки с текстом пользователя;
forest  —   строка для записи результата шифрования;
berry   —   символ из двумерного массива.

"""


def make(Line: str, stick: int):
    band = list(Line)
    far = math.ceil(len(Line) / stick)
    scytale = []
    pear = 0
    for i in range(far):
        honey = []
        for j in range(stick):
            if pear < len(band):
                honey.append(band[pear])
                pear += 1
            else:
                honey.append('')
        scytale.append(honey)
    forest = ""
    for a in range(stick):
        for b in range(far):
            berry = scytale[b][a]
            if berry:
                forest += berry
    return forest


def blue(Line: str, stick: int):
    far = math.ceil(len(Line) / stick)
    return far