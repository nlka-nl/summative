import cv2
import numpy as np


class SimpleSmileEffect:
    def __init__(self):
        # Используем каскады Хаара для обнаружения лиц и улыбок
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.smile_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_smile.xml'
        )
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )

        self.smile_active = False
        self.stretch_intensity = 0

    def detect_smile(self, gray, face_roi):
        """Обнаружить улыбку в области лица"""
        smiles = self.smile_cascade.detectMultiScale(
            gray,
            scaleFactor=1.8,
            minNeighbors=20,
            minSize=(25, 25)
        )

        return len(smiles) > 0

    def apply_stretch_effect(self, frame, face):
        """Применить эффект растягивания улыбки"""
        x, y, w, h = face

        # Увеличиваем интенсивность при улыбке
        if self.smile_active:
            self.stretch_intensity = min(self.stretch_intensity + 10, 100)
        else:
            self.stretch_intensity = max(self.stretch_intensity - 5, 0)

        if self.stretch_intensity > 0:
            # Создаем копию области лица
            face_region = frame[y:y + h, x:x + w].copy()

            # Применяем аффинное преобразование для растягивания
            rows, cols = face_region.shape[:2]

            # Точки для преобразования
            src_points = np.float32([
                [0, 0],
                [cols - 1, 0],
                [0, rows - 1],
                [cols - 1, rows - 1]
            ])

            # Вычисляем степень растяжения
            stretch = self.stretch_intensity / 100.0 * 0.3

            dst_points = np.float32([
                [-cols * stretch, -rows * stretch * 0.5],
                [cols * (1 + stretch), -rows * stretch * 0.5],
                [0, rows - 1],
                [cols - 1, rows - 1]
            ])

            # Матрица преобразования
            matrix = cv2.getPerspectiveTransform(src_points, dst_points)

            # Применяем преобразование
            stretched_face = cv2.warpPerspective(
                face_region, matrix, (cols, rows),
                borderMode=cv2.BORDER_REFLECT
            )

            # Смешиваем с оригиналом
            alpha = min(self.stretch_intensity / 100.0, 0.7)
            frame[y:y + h, x:x + w] = cv2.addWeighted(
                frame[y:y + h, x:x + w], 1 - alpha,
                stretched_face, alpha, 0
            )

            



    def run(self):
        """Запуск приложения"""
        cap = cv2.VideoCapture(0)

        print("Запуск простой версии 'Расползающаяся улыбка'")
        print("Нажмите 'q' для выхода")
        print("Нажмите 's' для сохранения скриншота")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Обнаружение лиц
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(100, 100)
            )

            for (x, y, w, h) in faces:
                # Область лица
                roi_gray = gray[y:y + h, x:x + w]
                roi_color = frame[y:y + h, x:x + w]

                # Обнаружение улыбки
                self.smile_active = self.detect_smile(roi_gray, (x, y, w, h))

                # Применение эффекта
                self.apply_stretch_effect(frame, (x, y, w, h))

                # Рисуем прямоугольник вокруг лица
                color = (0, 255, 0) if not self.smile_active else (0, 0, 255)
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

                # Текст статуса
                status = "SMILING!" if self.smile_active else "Neutral"
                cv2.putText(frame, status, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                cv2.putText(frame, f"Intensity: {self.stretch_intensity}%",
                            (x, y + h + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

            # Отображаем
            cv2.imshow('Simple Smile Stretch Effect', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                cv2.imwrite('smile_effect_screenshot.jpg', frame)
                print("Скриншот сохранен!")

        cap.release()
        cv2.destroyAllWindows()


# Запуск простой версии
if __name__ == "__main__":
    effect = SimpleSmileEffect()
    effect.run()