"""
Точка входа в интернет-магазин одежды.
Запускает интерфейс командной строки (CLI).
"""

import sys
import os

# Добавляем текущую директорию в путь для импорта (если необходимо)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli import main


if __name__ == "__main__":
    """
    Запуск приложения.
    При возникновении ошибок выводит сообщение и завершает работу.
    """
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Программа прервана пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n  [КРИТИЧЕСКАЯ ОШИБКА] {e}")
        print("  Пожалуйста, обратитесь к разработчику")
        sys.exit(1)