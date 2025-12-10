import cv2
import mediapipe as mp
import pygame
import sys
import random

def get_hand_positions_with_debug():
    """Получает позиции рук с отладочной визуализацией"""
    success, image = cap.read()
    if not success:
        return None, None

    image_rgb = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    left_hand_y = None
    right_hand_y = None

    # Отрисовка landmarks для отладки
    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            mp_drawing.draw_landmarks(
                image_bgr, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            wrist_y = hand_landmarks.landmark[0].y
            hand_label = handedness.classification[0].label
            screen_y = int(wrist_y * HEIGHT)

            # Добавляем текст с информацией о руке
            cv2.putText(image_bgr, f"{hand_label}: {screen_y}",
                        (10, 30 if hand_label == "Left" else 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            if hand_label == "Left":
                left_hand_y = screen_y
            elif hand_label == "Right":
                right_hand_y = screen_y

    # Показываем отладочное окно
    cv2.imshow('Hand Tracking Debug', image_bgr)

    return left_hand_y, right_hand_y


def smooth_movement(current_pos, target_pos, smoothing=0.2):
    """Сглаживание движения ракеток"""
    if target_pos is None:
        return current_pos
    return int(current_pos * (1 - smoothing) + target_pos * smoothing)


def game_loop_enhanced():
    global left_score, right_score

    running = True
    left_target_y = HEIGHT // 2
    right_target_y = HEIGHT // 2

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:  # Сброс игры
                    left_score = 0
                    right_score = 0
                    ball.reset()

        # Получаем позиции рук
        left_hand_y, right_hand_y = get_hand_positions_with_debug()

        # Сглаживаем движение
        if left_hand_y is not None:
            left_target_y = smooth_movement(left_target_y, left_hand_y - PADDLE_HEIGHT // 2)
            left_paddle.move(left_target_y)

        if right_hand_y is not None:
            right_target_y = smooth_movement(right_target_y, right_hand_y - PADDLE_HEIGHT // 2)
            right_paddle.move(right_target_y)

        # Логика игры...
        result = ball.update()
        if result == "left":
            right_score += 1
            ball.reset()
        elif result == "right":
            left_score += 1
            ball.reset()

        if ball.rect.colliderect(left_paddle.rect) and ball.dx < 0:
            ball.bounce()
            # Добавляем эффект в зависимости от места удара
            relative_intersect = (left_paddle.rect.centery - ball.rect.centery) / (PADDLE_HEIGHT / 2)
            ball.dy = -relative_intersect * 5

        if ball.rect.colliderect(right_paddle.rect) and ball.dx > 0:
            ball.bounce()
            relative_intersect = (right_paddle.rect.centery - ball.rect.centery) / (PADDLE_HEIGHT / 2)
            ball.dy = -relative_intersect * 5

        # Отрисовка
        screen.fill(BLACK)

        # Рисуем центральную линию
        for y in range(0, HEIGHT, 20):
            pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 2, y, 4, 10))

        left_paddle.draw()
        right_paddle.draw()
        ball.draw()
        draw_score()

        # Инструкции
        instructions = font.render("ESC - выход, R - сброс", True, WHITE)
        screen.blit(instructions, (10, HEIGHT - 30))

        pygame.display.flip()
        clock.tick(FPS)

        # Обработка клавиш OpenCV
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()
    sys.exit()


# Запускаем улучшенную версию
if __name__ == "__main__":
    game_loop_enhanced()