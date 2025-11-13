import prompt

def welcome():
    """Функция приветствия"""
    print("Первая попытка запустить проект!")
    print("***")
    
    while True:
        user_input = prompt.string("Введите команду: ")
        command = user_input.strip().lower()
        
        if command == "exit":
            print("Выход из программы...")
            break
        elif command == "help":
            print("<command> exit - выйти из программы")
            print("<command> help - справочная информация")
        elif command == "":
            continue  # Игнорируем пустые команды
        else:
            print(f"Неизвестная команда: {command}")
            print("Доступные команды: exit, help")