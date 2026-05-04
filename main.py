"""
Точка входа в интернет-магазин одежды.
Запускает интерфейс командной строки (CLI).
"""

import sys

from cli import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Программа прервана пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n  [КРИТИЧЕСКАЯ ОШИБКА] {e}")
        print("  Пожалуйста, обратитесь к разработчику")
        sys.exit(1)