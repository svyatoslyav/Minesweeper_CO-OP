import unittest
import server  # Імпортуємо наш файл server.py як модуль


class TestMinesweeperLogic(unittest.TestCase):

    def setUp(self):
        """Цей метод запускається перед кожним тестом.
        Ми скидаємо налаштування до тестових значень."""
        server.GRID_WIDTH = 10
        server.GRID_HEIGHT = 10
        server.MINES_COUNT = 10
        # Скидаємо глобальні змінні
        server.game_grid = []
        server.visible_grid = []
        server.game_state = server.STATE_MENU

    def test_grid_generation_counts(self):
        """Тест 1: Перевіряємо, чи правильно генерується поле"""
        print("Запуск тесту генерації поля...")

        # Запускаємо генерацію
        server.generate_grid()

        # 1. Перевіряємо розмір масиву
        self.assertEqual(len(server.game_grid), 10, "Висота поля неправильна")
        self.assertEqual(len(server.game_grid[0]), 10, "Ширина поля неправильна")

        # 2. Рахуємо кількість мін на полі
        real_mines_count = 0
        for y in range(server.GRID_HEIGHT):
            for x in range(server.GRID_WIDTH):
                if server.game_grid[y][x] == -1:
                    real_mines_count += 1

        # Перевіряємо, чи кількість мін збігається із заданою
        self.assertEqual(real_mines_count, server.MINES_COUNT, "Кількість мін не відповідає налаштуванням")

    def test_flood_fill_logic(self):
        """Тест 2: Перевіряємо алгоритм заливки (Flood Fill)"""
        print("Запуск тесту алгоритму заливки...")

        # Створюємо вручну маленьке поле 5x1 для тестування
        # Схема: [0, 0, 1, -1, 0]
        # Якщо відкрити першу 0, має відкритися друга 0 і цифра 1. Міна і остання 0 - ні.

        server.GRID_WIDTH = 5
        server.GRID_HEIGHT = 1

        # Ініціалізуємо масиви
        server.visible_grid = [[False for _ in range(5)]]
        server.game_grid = [[0, 0, 1, -1, 0]]

        # ДІЯ: Відкриваємо першу клітинку (координати 0,0)
        server.reveal_cell(0, 0)

        # ПЕРЕВІРКА:
        # 1. Перша клітинка (0) має бути відкрита
        self.assertTrue(server.visible_grid[0][0], "Клітинка (0,0) має бути відкрита")

        # 2. Друга клітинка (0) має бути відкрита автоматично (сусід пустий)
        self.assertTrue(server.visible_grid[0][1], "Клітинка (1,0) має бути відкрита рекурсивно")

        # 3. Третя клітинка (1) має бути відкрита (бо це межа пустої зони)
        self.assertTrue(server.visible_grid[0][2], "Клітинка (2,0) з цифрою 1 має бути відкрита")

        # 4. Четверта клітинка (Міна) має залишитися закритою
        self.assertFalse(server.visible_grid[0][3], "Міна (3,0) має залишитися закритою")


if __name__ == '__main__':
    unittest.main()