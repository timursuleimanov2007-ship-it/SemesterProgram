class EmptyLineError(Exception):
    """Ошибка пустой строки."""
    pass

class NotEnoughSymbolsError(Exception):
    """Ошибка недостаточного количества символов."""
    pass

class NullValueError(Exception):
    """Ошибка нулевого значения."""
    pass



def safe(Out: str):
    Line = ""
    while True:
        try:
            Line = input(Out)
            if (not Line):
                raise EmptyLineError
            return Line
        except EmptyLineError as elementary:
            print(f"\nОшибка! Подробнее: {elementary}")
        except Exception as execution:
            print(f"\nОшибка! Подробнее: {execution}")




def number(Out: str):
    Number = 0
    while True:
        try:
            Line = input(Out)
            if (not Line):
                raise EmptyLineError
            Number = int(Line)
            if (Number == 0):
                raise NullValueError
            return Number
        except ValueError as amphora:
            print(f"\nОшибка! Подробнее: {amphora}")
        except EmptyLineError as elementary:
            print(f"\nОшибка! Подробнее: {elementary}")
        except NullValueError as willow:
            print(f"\nОшибка! Подробнее: {willow}")
        except Exception as execution:
            print(f"\nОшибка! Подробнее: {execution}")




def password(Out: str):
    Line = ""
    while True:
        try:
            Line = input(Out)
            if (not Line):
                raise EmptyLineError
            elif (len(Line) < 10):
                raise NotEnoughSymbolsError
            return Line
        except EmptyLineError as elementary:
            print(f"\nОшибка! Подробнее: {elementary}")
        except NotEnoughSymbolsError as nest:
            print(f"\nОшибка! Подробнее: {nest}")
        except Exception as execution:
            print(f"\nОшибка! Подробнее: {execution}")