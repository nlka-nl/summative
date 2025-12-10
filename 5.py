import cv2
import numpy as np
import mediapipe as mp
import time
import pygame
import math
import json
import os
from collections import deque
from enum import Enum


class DanceGame:
    def __init__(self):
        # Инициализация MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
            model_complexity=1
        )

        # Инициализация Pygame для звука и интерфейса
        pygame.init()
        pygame.mixer.init()

        # Константы игры
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720
        self.FPS = 30

        # Создание окна
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Dance Vision - Just Dance Clone")

        # Цвета
        self.COLORS = {
            'background': (25, 25, 40),
            'text': (255, 255, 255),
            'score': (255, 215, 0),
            'perfect': (0, 255, 127),
            'good': (30, 144, 255),
            'ok': (255, 165, 0),
            'miss': (220, 20, 60),
            'target': (50, 205, 50),
            'player': (255, 105, 180)
        }

        # Игровые переменные
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.health = 100
        self.multiplier = 1
        self.dance_moves = []
        self.current_move_index = 0
        self.move_start_time = 0
        self.game_state = "MENU"  # MENU, PLAYING, PAUSED, GAME_OVER
        self.difficulty = "MEDIUM"

        # Загрузка ресурсов
        self.load_resources()

        # Трекер скелета
        self.landmarks_history = deque(maxlen=10)
        self.current_pose = None

        # Камера
        self.cap = cv2.VideoCapture(0)
        self.camera_width = 640
        self.camera_height = 480

        # Шрифты
        self.font_large = pygame.font.SysFont('Arial', 48, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', 32)
        self.font_small = pygame.font.SysFont('Arial', 24)

        # Генерация танцевальных движений
        self.generate_dance_moves()

    def load_resources(self):
        """Загрузка звуков и изображений"""
        try:
            # Звуки (заменяем на системные, если файлы не найдены)
            self.sounds = {
                'perfect': pygame.mixer.Sound(self.generate_beep_sound(440, 0.1)),
                'good': pygame.mixer.Sound(self.generate_beep_sound(330, 0.1)),
                'ok': pygame.mixer.Sound(self.generate_beep_sound(220, 0.1)),
                'miss': pygame.mixer.Sound(self.generate_beep_sound(110, 0.1)),
                'combo': pygame.mixer.Sound(self.generate_beep_sound(880, 0.2))
            }

            # Фоновая музыка
            pygame.mixer.music.load(self.generate_background_music())

        except Exception as e:
            print(f"Ошибка загрузки ресурсов: {e}")

    def generate_beep_sound(self, frequency, duration):
        """Генерация простого звукового сигнала"""
        sample_rate = 22050
        n_samples = int(sample_rate * duration)

        buf = np.zeros((n_samples, 2), dtype=np.int16)
        max_sample = 2 ** (16 - 1) - 1

        for s in range(n_samples):
            t = float(s) / sample_rate
            buf[s][0] = int(max_sample * math.sin(2 * math.pi * frequency * t))
            buf[s][1] = int(max_sample * math.sin(2 * math.pi * frequency * t))

        return pygame.sndarray.make_sound(buf)

    def generate_background_music(self):
        """Генерация простой фоновой музыки"""
        sample_rate = 22050
        duration = 0.5
        n_samples = int(sample_rate * duration)

        notes = [262, 294, 330, 349, 392, 440, 494, 523]
        music_data = []

        for note in notes * 4:
            buf = np.zeros((n_samples, 2), dtype=np.int16)
            max_sample = 2 ** (16 - 1) - 1

            for s in range(n_samples):
                t = float(s) / sample_rate
                buf[s][0] = int(max_sample * 0.3 * math.sin(2 * math.pi * note * t))
                buf[s][1] = int(max_sample * 0.3 * math.sin(2 * math.pi * note * t))

            music_data.append(buf)

        full_music = np.vstack(music_data)
        return pygame.sndarray.make_sound(full_music)

    def generate_dance_moves(self):
        """Генерация танцевальных движений"""
        base_moves = [
            {
                "name": "Hands Up",
                "duration": 3.0,
                "target_angles": {
                    "left_shoulder": 170,  # градусы
                    "right_shoulder": 170,
                    "left_elbow": 160,
                    "right_elbow": 160
                },
                "target_positions": {
                    "left_wrist_y": 0.2,  # относительно высоты кадра (меньше = выше)
                    "right_wrist_y": 0.2
                }
            },
            {
                "name": "Hip Swing",
                "duration": 2.5,
                "target_angles": {
                    "left_hip": 80,
                    "right_hip": 100
                },
                "target_positions": {
                    "left_knee_x": 0.4,
                    "right_knee_x": 0.6
                }
            },
            {
                "name": "Star Jump",
                "duration": 3.0,
                "target_angles": {
                    "left_shoulder": 90,
                    "right_shoulder": 90,
                    "left_knee": 160,
                    "right_knee": 160
                },
                "target_positions": {
                    "left_wrist_x": 0.3,
                    "right_wrist_x": 0.7,
                    "left_ankle_x": 0.4,
                    "right_ankle_x": 0.6
                }
            },
            {
                "name": "Squat",
                "duration": 3.0,
                "target_angles": {
                    "left_knee": 90,
                    "right_knee": 90
                },
                "target_positions": {
                    "left_hip_y": 0.6,
                    "right_hip_y": 0.6
                }
            },
            {
                "name": "Wave",
                "duration": 4.0,
                "sequence": [
                    {"left_wrist_x": 0.3, "right_wrist_x": 0.7},
                    {"left_wrist_x": 0.4, "right_wrist_x": 0.6},
                    {"left_wrist_x": 0.5, "right_wrist_x": 0.5},
                    {"left_wrist_x": 0.6, "right_wrist_x": 0.4}
                ]
            }
        ]

        # Добавляем больше движений в зависимости от сложности
        for i in range(10):
            move = base_moves[i % len(base_moves)].copy()
            move["name"] = f"{move['name']} {i + 1}"
            move["points"] = (i + 1) * 100
            self.dance_moves.append(move)

    def calculate_angle(self, a, b, c):
        """Вычисление угла между тремя точками"""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)

        ba = a - b
        bc = c - b

        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))

        return np.degrees(angle)

    def get_landmark_position(self, landmarks, landmark_idx):
        """Получение позиции ориентира"""
        if landmarks and landmark_idx < len(landmarks.landmark):
            landmark = landmarks.landmark[landmark_idx]
            return (landmark.x, landmark.y, landmark.z)
        return None

    def extract_pose_features(self, landmarks):
        """Извлечение признаков позы"""
        if not landmarks:
            return None

        features = {}

        # Определение ключевых точек
        keypoints = {
            'nose': 0, 'left_eye': 1, 'right_eye': 2,
            'left_ear': 3, 'right_ear': 4,
            'left_shoulder': 11, 'right_shoulder': 12,
            'left_elbow': 13, 'right_elbow': 14,
            'left_wrist': 15, 'right_wrist': 16,
            'left_hip': 23, 'right_hip': 24,
            'left_knee': 25, 'right_knee': 26,
            'left_ankle': 27, 'right_ankle': 28
        }

        # Получение позиций всех точек
        positions = {}
        for name, idx in keypoints.items():
            pos = self.get_landmark_position(landmarks, idx)
            if pos:
                positions[name] = pos

        # Вычисление углов суставов
        if all(k in positions for k in ['left_shoulder', 'left_elbow', 'left_wrist']):
            features['left_elbow_angle'] = self.calculate_angle(
                positions['left_shoulder'],
                positions['left_elbow'],
                positions['left_wrist']
            )

        if all(k in positions for k in ['right_shoulder', 'right_elbow', 'right_wrist']):
            features['right_elbow_angle'] = self.calculate_angle(
                positions['right_shoulder'],
                positions['right_elbow'],
                positions['right_wrist']
            )

        if all(k in positions for k in ['left_hip', 'left_knee', 'left_ankle']):
            features['left_knee_angle'] = self.calculate_angle(
                positions['left_hip'],
                positions['left_knee'],
                positions['left_ankle']
            )

        if all(k in positions for k in ['right_hip', 'right_knee', 'right_ankle']):
            features['right_knee_angle'] = self.calculate_angle(
                positions['right_hip'],
                positions['right_knee'],
                positions['right_ankle']
            )

        # Позиции конечностей
        for name, pos in positions.items():
            features[f'{name}_x'] = pos[0]
            features[f'{name}_y'] = pos[1]

        return features

    def evaluate_move(self, player_features, target_move):
        """Оценка выполнения движения"""
        if not player_features:
            return "MISS", 0

        total_score = 0
        accuracy_count = 0

        # Проверка углов
        for angle_name, target_angle in target_move.get('target_angles', {}).items():
            player_angle = player_features.get(f'{angle_name}_angle')
            if player_angle:
                diff = abs(player_angle - target_angle)
                if diff < 15:
                    total_score += 50
                    accuracy_count += 1
                elif diff < 30:
                    total_score += 30
                    accuracy_count += 1
                elif diff < 45:
                    total_score += 10
                    accuracy_count += 1

        # Проверка позиций
        for pos_name, target_pos in target_move.get('target_positions', {}).items():
            player_pos = player_features.get(pos_name)
            if player_pos:
                diff = abs(player_pos - target_pos)
                if diff < 0.1:
                    total_score += 50
                    accuracy_count += 1
                elif diff < 0.2:
                    total_score += 30
                    accuracy_count += 1
                elif diff < 0.3:
                    total_score += 10
                    accuracy_count += 1

        # Определение оценки
        if accuracy_count > 0:
            avg_score = total_score / accuracy_count
            if avg_score >= 45:
                return "PERFECT", total_score * self.multiplier
            elif avg_score >= 25:
                return "GOOD", total_score * self.multiplier
            else:
                return "OK", total_score * self.multiplier

        return "MISS", 0

    def process_camera_frame(self):
        """Обработка кадра с камеры"""
        ret, frame = self.cap.read()
        if not ret:
            return None

        # Отражение по горизонтали для зеркального эффекта
        frame = cv2.flip(frame, 1)

        # Конвертация BGR в RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Обработка позы
        results = self.pose.process(rgb_frame)

        # Конвертация обратно в BGR для отображения
        display_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)

        # Отрисовка скелета
        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                display_frame,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
            )

            # Сохранение текущей позы
            self.current_pose = results.pose_landmarks
            self.landmarks_history.append(self.current_pose)

            # Извлечение признаков
            player_features = self.extract_pose_features(results.pose_landmarks)

            # В режиме игры оцениваем движение
            if self.game_state == "PLAYING" and self.current_move_index < len(self.dance_moves):
                current_move = self.dance_moves[self.current_move_index]

                # Проверяем, не истекло ли время на движение
                elapsed = time.time() - self.move_start_time
                if elapsed > current_move["duration"]:
                    rating, points = self.evaluate_move(player_features, current_move)

                    if rating == "MISS":
                        self.combo = 0
                        self.health -= 10
                        self.sounds['miss'].play()
                    else:
                        self.combo += 1
                        self.max_combo = max(self.max_combo, self.combo)
                        self.score += points

                        if rating == "PERFECT":
                            self.sounds['perfect'].play()
                        elif rating == "GOOD":
                            self.sounds['good'].play()
                        else:
                            self.sounds['ok'].play()

                        if self.combo % 5 == 0:
                            self.sounds['combo'].play()
                            self.multiplier = min(self.multiplier + 0.5, 4.0)

                    # Переход к следующему движению
                    self.current_move_index += 1
                    if self.current_move_index < len(self.dance_moves):
                        self.move_start_time = time.time()
                    else:
                        self.game_state = "GAME_OVER"

        # Добавление текста на кадр
        cv2.putText(display_frame, f"Score: {self.score}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(display_frame, f"Combo: {self.combo}x", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 215, 0), 2)

        return display_frame

    def draw_menu(self):
        """Отрисовка главного меню"""
        self.screen.fill(self.COLORS['background'])

        # Заголовок
        title = self.font_large.render("DANCE VISION", True, self.COLORS['text'])
        self.screen.blit(title, (self.SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        # Кнопки
        button_width = 300
        button_height = 60
        button_y_start = 250

        buttons = [
            ("START GAME", self.start_game),
            ("DIFFICULTY: " + self.difficulty, self.toggle_difficulty),
            ("EXIT", self.quit_game)
        ]

        for i, (text, action) in enumerate(buttons):
            button_rect = pygame.Rect(
                self.SCREEN_WIDTH // 2 - button_width // 2,
                button_y_start + i * 80,
                button_width,
                button_height
            )

            # Рисуем кнопку
            pygame.draw.rect(self.screen, (70, 70, 100), button_rect, border_radius=15)
            pygame.draw.rect(self.screen, (100, 100, 150), button_rect, 3, border_radius=15)

            # Текст кнопки
            button_text = self.font_medium.render(text, True, self.COLORS['text'])
            self.screen.blit(button_text,
                             (button_rect.centerx - button_text.get_width() // 2,
                              button_rect.centery - button_text.get_height() // 2))

            # Проверка нажатия
            mouse_pos = pygame.mouse.get_pos()
            if button_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, (120, 120, 180), button_rect, 3, border_radius=15)
                if pygame.mouse.get_pressed()[0]:
                    action()

        # Инструкция
        instruction = self.font_small.render("Use your webcam to dance! Follow the moves on screen.",
                                             True, self.COLORS['text'])
        self.screen.blit(instruction, (self.SCREEN_WIDTH // 2 - instruction.get_width() // 2, 500))

    def draw_game_ui(self):
        """Отрисовка игрового интерфейса"""
        # Фон
        self.screen.fill(self.COLORS['background'])

        # Левая панель - камера
        camera_surface = self.camera_to_surface()
        if camera_surface:
            self.screen.blit(camera_surface, (20, 20))

        # Правая панель - игровая информация
        panel_x = 700
        panel_y = 20

        # Счет
        score_text = self.font_large.render(f"SCORE: {self.score}", True, self.COLORS['score'])
        self.screen.blit(score_text, (panel_x, panel_y))

        # Комбо
        combo_text = self.font_medium.render(f"COMBO: {self.combo}x", True, self.COLORS['perfect'])
        self.screen.blit(combo_text, (panel_x, panel_y + 60))

        # Множитель
        multiplier_text = self.font_medium.render(f"MULTIPLIER: {self.multiplier}x",
                                                  True, self.COLORS['good'])
        self.screen.blit(multiplier_text, (panel_x, panel_y + 110))

        # Здоровье
        health_bar_width = 300
        health_bar_height = 30
        health_width = int(health_bar_width * (self.health / 100))

        pygame.draw.rect(self.screen, (100, 100, 100),
                         (panel_x, panel_y + 160, health_bar_width, health_bar_height))
        pygame.draw.rect(self.screen, self.COLORS['perfect'] if self.health > 50 else self.COLORS['miss'],
                         (panel_x, panel_y + 160, health_width, health_bar_height))

        health_text = self.font_small.render(f"HEALTH: {self.health}%", True, self.COLORS['text'])
        self.screen.blit(health_text, (panel_x, panel_y + 200))

        # Текущее движение
        if self.current_move_index < len(self.dance_moves):
            current_move = self.dance_moves[self.current_move_index]

            move_text = self.font_large.render(current_move["name"], True, self.COLORS['target'])
            self.screen.blit(move_text, (panel_x, panel_y + 250))

            # Таймер
            elapsed = time.time() - self.move_start_time
            time_left = max(0, current_move["duration"] - elapsed)

            timer_text = self.font_medium.render(f"TIME: {time_left:.1f}s", True, self.COLORS['text'])
            self.screen.blit(timer_text, (panel_x, panel_y + 310))

            # Подсказки для движения
            hints_y = panel_y + 360
            if 'target_angles' in current_move:
                for joint, angle in current_move['target_angles'].items():
                    hint = self.font_small.render(f"{joint}: {angle}°", True, self.COLORS['player'])
                    self.screen.blit(hint, (panel_x, hints_y))
                    hints_y += 30

        # Кнопка паузы
        pause_button = pygame.Rect(self.SCREEN_WIDTH - 100, 20, 80, 40)
        pygame.draw.rect(self.screen, (70, 70, 100), pause_button, border_radius=10)
        pause_text = self.font_small.render("PAUSE", True, self.COLORS['text'])
        self.screen.blit(pause_text,
                         (pause_button.centerx - pause_text.get_width() // 2,
                          pause_button.centery - pause_text.get_height() // 2))

    def draw_game_over(self):
        """Отрисовка экрана окончания игры"""
        self.screen.fill(self.COLORS['background'])

        # Заголовок
        title = self.font_large.render("GAME OVER", True, self.COLORS['text'])
        self.screen.blit(title, (self.SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        # Статистика
        stats = [
            f"FINAL SCORE: {self.score}",
            f"MAX COMBO: {self.max_combo}x",
            f"DANCE MOVES: {self.current_move_index}/{len(self.dance_moves)}",
            f"DIFFICULTY: {self.difficulty}"
        ]

        for i, stat in enumerate(stats):
            stat_text = self.font_medium.render(stat, True, self.COLORS['score'])
            self.screen.blit(stat_text,
                             (self.SCREEN_WIDTH // 2 - stat_text.get_width() // 2,
                              200 + i * 50))

        # Кнопка рестарта
        restart_button = pygame.Rect(self.SCREEN_WIDTH // 2 - 150, 450, 300, 60)
        pygame.draw.rect(self.screen, (70, 70, 100), restart_button, border_radius=15)
        restart_text = self.font_medium.render("PLAY AGAIN", True, self.COLORS['text'])
        self.screen.blit(restart_text,
                         (restart_button.centerx - restart_text.get_width() // 2,
                          restart_button.centery - restart_text.get_height() // 2))

        # Кнопка меню
        menu_button = pygame.Rect(self.SCREEN_WIDTH // 2 - 150, 530, 300, 60)
        pygame.draw.rect(self.screen, (70, 70, 100), menu_button, border_radius=15)
        menu_text = self.font_medium.render("MAIN MENU", True, self.COLORS['text'])
        self.screen.blit(menu_text,
                         (menu_button.centerx - menu_text.get_width() // 2,
                          menu_button.centery - menu_text.get_height() // 2))

        # Проверка нажатий
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        if restart_button.collidepoint(mouse_pos) and mouse_pressed:
            self.start_game()

        if menu_button.collidepoint(mouse_pos) and mouse_pressed:
            self.game_state = "MENU"
            self.reset_game()

    def camera_to_surface(self):
        """Конвертация кадра камеры в Pygame Surface"""
        frame = self.process_camera_frame()
        if frame is None:
            return None

        # Конвертация OpenCV BGR в RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = np.rot90(frame_rgb)
        frame_surface = pygame.surfarray.make_surface(frame_rgb)

        return pygame.transform.scale(frame_surface, (640, 480))

    def start_game(self):
        """Начать игру"""
        self.reset_game()
        self.game_state = "PLAYING"
        self.move_start_time = time.time()
        pygame.mixer.music.play(-1)  # Зациклить музыку

    def reset_game(self):
        """Сброс игровых переменных"""
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.health = 100
        self.multiplier = 1
        self.current_move_index = 0
        self.move_start_time = 0

    def toggle_difficulty(self):
        """Переключение сложности"""
        difficulties = ["EASY", "MEDIUM", "HARD"]
        current_idx = difficulties.index(self.difficulty)
        self.difficulty = difficulties[(current_idx + 1) % len(difficulties)]

    def quit_game(self):
        """Выход из игры"""
        self.game_state = "EXIT"

    def run(self):
        """Главный игровой цикл"""
        clock = pygame.time.Clock()

        while self.game_state != "EXIT":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.game_state == "PLAYING":
                            self.game_state = "PAUSED"
                        elif self.game_state == "PAUSED":
                            self.game_state = "PLAYING"
                    elif event.key == pygame.K_SPACE:
                        if self.game_state == "MENU":
                            self.start_game()
                    elif event.key == pygame.K_m:
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.music.pause()
                        else:
                            pygame.mixer.music.unpause()

            # Отрисовка в зависимости от состояния
            if self.game_state == "MENU":
                self.draw_menu()
            elif self.game_state == "PLAYING":
                self.draw_game_ui()
                # Проверка здоровья
                if self.health <= 0:
                    self.game_state = "GAME_OVER"
            elif self.game_state == "GAME_OVER":
                self.draw_game_over()
            elif self.game_state == "PAUSED":
                self.draw_game_ui()
                # Наложение паузы
                pause_overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
                pause_overlay.fill((0, 0, 0, 150))
                self.screen.blit(pause_overlay, (0, 0))

                pause_text = self.font_large.render("PAUSED", True, self.COLORS['text'])
                self.screen.blit(pause_text,
                                 (self.SCREEN_WIDTH // 2 - pause_text.get_width() // 2,
                                  self.SCREEN_HEIGHT // 2 - pause_text.get_height() // 2))

            pygame.display.flip()
            clock.tick(self.FPS)

        # Очистка
        self.cap.release()
        pygame.quit()
        cv2.destroyAllWindows()


# Упрощенная версия для быстрого запуска
class SimpleDanceGame:
    """Упрощенная версия без Pygame"""

    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.mp_drawing = mp.solutions.drawing_utils

        self.cap = cv2.VideoCapture(0)
        self.score = 0
        self.target_poses = []
        self.generate_target_poses()

    def generate_target_poses(self):
        """Генерация целевых поз"""
        self.target_poses = [
            {"name": "Hands Up", "key": "up"},
            {"name": "Hands Side", "key": "side"},
            {"name": "Squat", "key": "squat"},
            {"name": "Left Leg Up", "key": "left_leg"},
            {"name": "Right Leg Up", "key": "right_leg"}
        ]

    def check_pose(self, landmarks, target):
        """Проверка позы"""
        if not landmarks:
            return False

        # Упрощенная проверка поз
        if target["key"] == "up":
            # Руки подняты
            left_wrist = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_WRIST]
            right_wrist = landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST]
            nose = landmarks.landmark[self.mp_pose.PoseLandmark.NOSE]

            return left_wrist.y < nose.y and right_wrist.y < nose.y

        elif target["key"] == "side":
            # Руки в стороны
            left_wrist = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_WRIST]
            right_wrist = landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST]
            left_shoulder = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]

            return (left_wrist.x < left_shoulder.x and
                    right_wrist.x > right_shoulder.x)

        return False

    def run_simple(self):
        """Запуск упрощенной версии"""
        target_index = 0
        last_change = time.time()

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)

            # Отрисовка скелета
            if results.pose_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS
                )

                # Проверка позы
                if time.time() - last_change > 5:  # Меняем позу каждые 5 секунд
                    if self.check_pose(results.pose_landmarks, self.target_poses[target_index]):
                        self.score += 100
                        print(f"Good! Score: {self.score}")

                    target_index = (target_index + 1) % len(self.target_poses)
                    last_change = time.time()

            # Отображение информации
            target_pose = self.target_poses[target_index]
            cv2.putText(frame, f"Target: {target_pose['name']}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Score: {self.score}", (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 215, 0), 2)
            cv2.putText(frame, f"Time: {5 - int(time.time() - last_change)}s", (10, 110),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 100, 100), 2)

            cv2.imshow('Simple Dance Game', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    print("Выберите режим:")
    print("1. Полная версия с интерфейсом (Pygame)")
    print("2. Упрощенная версия (OpenCV только)")

    choice = input("Введите 1 или 2: ")

    if choice == "1":
        # Установите необходимые библиотеки:
        # pip install opencv-python mediapipe pygame numpy
        game = DanceGame()
        game.run()
    else:
        # Упрощенная версия
        # pip install opencv-python mediapipe
        game = SimpleDanceGame()
        game.run_simple()