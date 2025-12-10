import cv2
import numpy as np

COLORS = {
    'team1': (0, 255, 0),
    'team2': (255, 0, 0),
    'text': (255, 255, 255)
}


class DartBoardDetector:
    def __init__(self):

        self.center = (320, 240)  # Центр мишени
        self.radius = 215  # Радиус мишени
        self.ring_width = 30  # Ширина каждого кольца

        # Расположение секторов на мишени (стандартный дартс)
        self.sectors = {
            20: 0, 1: 18, 18: 36, 4: 54, 13: 72, 6: 90,
            10: 108, 15: 126, 2: 144, 17: 162, 3: 180,
            19: 198, 7: 216, 16: 234, 8: 252, 11: 270,
            14: 288, 9: 306, 12: 324, 5: 342
        }

        # Баллы для каждой зоны
        self.zone_points = {
            0: 50,  # Центр (яблочко)
            1: 25,  # Кольцо вокруг центра
            2: 1,  # Внутренняя область
            3: 3,  # Утроение
            4: 1,  # Средняя область
            5: 2,  # Удвоение
            6: 0  # Вне мишени
        }

        # Счетчики
        self.team1_score = 0
        self.team2_score = 0
        self.current_team = 1

        self.darts = []

    def detect_board(self, frame):
        """Обнаружение мишени по кругу"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)

        # Поиск кругов (мишени)
        circles = cv2.HoughCircles(
            gray, cv2.HOUGH_GRADIENT, 1, 100,
            param1 = 100, param2 = 30, minRadius=100, maxRadius=250
        )

        if circles is not None:
            circles = np.uint16(np.around(circles))
            # Берем первый найденный круг
            circle = circles[0][0]
            self.center = (circle[0], circle[1])
            self.radius = circle[2]
            return True
        return False

    def get_sector(self, x, y):
        """Определение сектора по углу"""
        # Вычисляем угол от центра
        dx = x - self.center[0]
        dy = y - self.center[1]

        # Вычисляем угол в градусах
        angle = np.degrees(np.arctan2(dy, dx))
        angle = (angle + 360 + 9) % 360  # Сдвиг на половину сектора

        # Находим ближайший сектор
        for points, sector_angle in self.sectors.items():
            if abs(angle - sector_angle) <= 9:
                return points

        return 20  # По умолчанию сектор 20

    def get_zone(self, distance):
        """Определение зоны по расстоянию от центра"""
        if distance <= self.radius * 0.1:  # Центр (50 очков)
            return 0
        elif distance <= self.radius * 0.2:  # Кольцо вокруг центра (25 очков)
            return 1
        elif distance <= self.radius * 0.5:  # Внутренняя область (обычные очки)
            return 2
        elif distance <= self.radius * 0.6:  # Кольцо утроения
            return 3
        elif distance <= self.radius * 0.9:  # Средняя область (обычные очки)
            return 4
        elif distance <= self.radius:  # Кольцо удвоения
            return 5
        else:  # Вне мишени
            return 6

    def calculate_score(self, x, y):
        """Расчет баллов для точки попадания"""
        # Расстояние от центра
        dx = x - self.center[0]
        dy = y - self.center[1]
        distance = np.sqrt(dx * dx + dy * dy)

        # Определяем сектор и зону
        sector = self.get_sector(x, y)
        zone = self.get_zone(distance)

        # Расчет баллов
        base_points = sector
        zone_multiplier = self.zone_points[zone]

        if zone in [0, 1]:  # Яблочко или кольцо вокруг
            points = zone_multiplier
        elif zone == 3:  # Утроение
            points = base_points * 3
        elif zone == 5:  # Удвоение
            points = base_points * 2
        else:  # Обычные зоны
            points = base_points

        return points, sector, zone

    def detect_dart(self, frame, previous_frame):
        """Обнаружение нового дротика по разности кадров"""
        if previous_frame is None:
            return None

        # Преобразуем в оттенки серого
        gray1 = cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Вычисляем разность
        diff = cv2.absdiff(gray1, gray2)

        # Пороговая обработка
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

        # Находим контуры
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            # Фильтруем по размеру
            area = cv2.contourArea(contour)
            if 50 < area < 500:  # Размер дротика
                # Получаем центр контура
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])

                    # Проверяем, что дротик в мишени
                    dx = cx - self.center[0]
                    dy = cy - self.center[1]
                    distance = np.sqrt(dx * dx + dy * dy)

                    if distance <= self.radius:
                        return (cx, cy)

        return None

    def draw_board(self, frame):
        """Рисование мишени и разметки"""
        # Основной круг мишени
        cv2.circle(frame, self.center, self.radius, (255, 255, 255), 2)

        # Зоны мишени
        zones = [
            (0.1, (255, 0, 0)),  # Красный центр
            (0.2, (0, 255, 255)),  # Желтое кольцо
            (0.5, (0, 255, 0)),  # Зеленая область
            (0.6, (0, 0, 255)),  # Красное кольцо утроения
            (0.9, (0, 255, 0)),  # Зеленая область
            (1.0, (255, 0, 0))  # Красное кольцо удвоения
        ]

        for ratio, color in zones:
            cv2.circle(frame, self.center, int(self.radius * ratio), color, 1)

        # Секторы (линии)
        for i in range(20):
            angle = np.radians(i * 18)
            x1 = int(self.center[0] + self.radius * np.cos(angle))
            y1 = int(self.center[1] + self.radius * np.sin(angle))
            cv2.line(frame, self.center, (x1, y1), (200, 200, 200), 1)

    def draw_interface(self, frame):
        """Рисование интерфейса счета"""
        # Фон для текста
        cv2.rectangle(frame, (10, 10), (350, 180), (0, 0, 0), -1)

        # Заголовок
        cv2.putText(frame, "DARTS SCORE TRACKER", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        # Счет команд
        cv2.putText(frame, f"TEAM 1: {self.team1_score}", (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS['team1'], 2)
        cv2.putText(frame, f"TEAM 2: {self.team2_score}", (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS['team2'], 2)

        # Очередь
        current_color = COLORS['team1'] if self.current_team == 1 else COLORS['team2']
        cv2.putText(frame, f"NEXT: TEAM {self.current_team}", (20, 160),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, current_color, 2)

        # Инструкция
        cv2.putText(frame, "Press SPACE to add dart | R to reset | Q to quit",
                    (20, 480), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS['text'], 1)


def main():
    print("=== DARTS SCORE TRACKER ===")
    print("Instructions:")
    print("1. Make sure dartboard is visible")
    print("2. Press SPACE when dart lands")
    print("3. System will detect dart and calculate score")
    print("4. Teams alternate automatically")
    print("5. Press R to reset game")
    print("6. Press Q to quit\n")

    # Инициализация
    detector = DartBoardDetector()
    cap = cv2.VideoCapture(0)
    previous_frame = None
    last_dart_time = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Зеркальное отражение
        frame = cv2.flip(frame, 1)

        # Детекция мишени
        if not detector.detect_board(frame):
            print("Dartboard not detected! Adjust camera position.")

        # Рисуем мишень
        detector.draw_board(frame)

        # Рисуем интерфейс
        detector.draw_interface(frame)

        # Показываем кадр
        cv2.imshow('Darts Score Tracker', frame)

        # Обработка клавиш
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        elif key == ord('r'):
            # Сброс игры
            detector.team1_score = 0
            detector.team2_score = 0
            detector.current_team = 1
            detector.darts = []
            print("\nGame reset!")
        elif key == 32:  # Пробел - добавление дротика
            # Вместо автоматического детекта, используем клик мыши для простоты
            print(f"\nTeam {detector.current_team} throw!")
            print("Click on the dart position and press ENTER...")

            # Создаем копию кадра для выбора точки
            select_frame = frame.copy()
            cv2.putText(select_frame, "Click on dart position", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Функция обработки клика мыши
            dart_position = None

            def mouse_callback(event, x, y, flags, param):
                nonlocal dart_position
                if event == cv2.EVENT_LBUTTONDOWN:
                    dart_position = (x, y)
                    cv2.circle(select_frame, (x, y), 5, (0, 0, 255), -1)
                    cv2.imshow('Darts Score Tracker', select_frame)

            cv2.imshow('Darts Score Tracker', select_frame)
            cv2.setMouseCallback('Darts Score Tracker', mouse_callback)

            # Ждем нажатия Enter
            while True:
                key2 = cv2.waitKey(1) & 0xFF
                if key2 == 13 and dart_position:  # Enter
                    break
                elif key2 == 27:  # Esc - отмена
                    dart_position = None
                    break

            cv2.setMouseCallback('Darts Score Tracker', lambda *args: None)

            # Если выбрана позиция, вычисляем баллы
            if dart_position:
                x, y = dart_position
                points, sector, zone = detector.calculate_score(x, y)

                # Добавляем очки команде
                if detector.current_team == 1:
                    detector.team1_score += points
                else:
                    detector.team2_score += points

                # Сохраняем дротик
                color = COLORS['team1'] if detector.current_team == 1 else COLORS['team2']
                detector.darts.append((x, y, color, points))

                print(f"  Sector: {sector}, Zone: {zone}, Points: {points}")
                print(
                    f"  Team {detector.current_team} total: {detector.team1_score if detector.current_team == 1 else detector.team2_score}")

                # Меняем команду
                detector.current_team = 2 if detector.current_team == 1 else 1

        # Рисуем все дротики
        for x, y, color, points in detector.darts:
            cv2.circle(frame, (x, y), 8, color, -1)
            cv2.putText(frame, f"{points}", (x + 10, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # Обновляем предыдущий кадр
        previous_frame = frame.copy()

    # Завершение
    cap.release()
    cv2.destroyAllWindows()

    print("\n=== FINAL SCORE ===")
    print(f"Team 1: {detector.team1_score}")
    print(f"Team 2: {detector.team2_score}")

    if detector.team1_score > detector.team2_score:
        print("Team 1 WINS!")
    elif detector.team2_score > detector.team1_score:
        print("Team 2 WINS!")
    else:
        print("DRAW!")


if __name__ == "__main__":
    main()