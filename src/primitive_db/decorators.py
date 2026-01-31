# decorators.py
import time
from functools import wraps


def handle_db_errors(func):
    """
    Декоратор для обработки ошибок базы данных.
    Перехватывает KeyError, ValueError, FileNotFoundError и другие исключения.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            return False, (f"Ошибка: Файл данных не найден. "
                           f"Возможно, база данных не инициализирована. {e}")
        except KeyError as e:
            return False, f"Ошибка: Таблица или столбец '{e}' не найден."
        except ValueError as e:
            return False, f"Ошибка валидации: {e}"
        except Exception as e:
            return False, f"Произошла непредвиденная ошибка: {e}"
    return wrapper


def confirm_action(action_name):
    """
    Декоратор для запроса подтверждения опасных операций.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Ищем объект prompt в пространстве имен
            import sys
            if 'prompt' in sys.modules:
                prompt = sys.modules['prompt']
                confirmation = prompt.string(
                    f"Вы уверены, что хотите выполнить '{action_name}'? [y/n]: "
                ).strip().lower()
                
                if confirmation != 'y':
                    return True, "Операция отменена пользователем."
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def log_time(func):
    """
    Декоратор для замера времени выполнения функции.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        
        execution_time = end_time - start_time
        print(f"Функция '{func.__name__}' выполнялась {execution_time:.3f} секунд.")
        
        return result
    return wrapper


def create_cacher():
    """
    Функция с замыканием для кэширования результатов.
    Возвращает функцию cache_result для кэширования.
    """
    cache = {}
    
    def cache_result(key, value_func):
        """
        Внутренняя функция для кэширования.
        
        Args:
            key: Ключ для кэша
            value_func: Функция для получения данных, если их нет в кэше
        
        Returns:
            Результат из кэша или вычисленный результат
        """
        if key in cache:
            return cache[key]
        else:
            result = value_func()
            cache[key] = result
            return result
    
    return cache_result