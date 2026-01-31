import prompt


def help():
    print()
    print(50*"=")
    print("Справка")
    print(50*"=")

    print("exit - выйти из программы")
    print("help - справочная информация")  

    print(50*"=")

def welcome():
    
    print("Первая попытка запустить проект!")
    help()

    while True:
        try:
            command = prompt.string("\nВведите команду: ").strip().lower()
            
            if command == "exit":
                print("\nВыход из программы...")
                break
            elif command == "help":
                help()
            else:
                # Пустая строка
                continue
                
        except KeyboardInterrupt:
            print("\nВыход из программы...")
            break
        except EOFError:
            print("\nВыход из программы...")
            break