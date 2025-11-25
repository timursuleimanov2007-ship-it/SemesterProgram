def integerSafeInput():
    while True:
        try:
            anyInteger = int(input("Введите переменную (int) >> "))
            return anyInteger

        except Exception as e:
            print(f"Ошибка! Подробнее: {e}")





def scytale_encrypt(text, diameter):
    if not text or diameter <= 0:
        return text
        
    rows = math.ceil(len(text) / diameter)
    matrix = [[' ' for _ in range(diameter)] for _ in range(rows)]

    index = 0
    for i in range(rows):
        for j in range(diameter):
            if index < len(text):
                matrix[i][j] = text[index]
                index += 1

    result = []
    for j in range(diameter):
        for i in range(rows):
            result.append(matrix[i][j])
    
    return ''.join(result).rstrip()





def scytale_decrypt(encrypted_text, diameter):
    if not encrypted_text or diameter <= 0:
        return encrypted_text
        
    rows = math.ceil(len(encrypted_text) / diameter)
    matrix = [[' ' for _ in range(diameter)] for _ in range(rows)]
    
    index = 0
    for j in range(diameter):
        for i in range(rows):
            if index < len(encrypted_text):
                matrix[i][j] = encrypted_text[index]
                index += 1
    
    result = []
    for i in range(rows):
        for j in range(diameter):
            result.append(matrix[i][j])
    
    return ''.join(result).rstrip()