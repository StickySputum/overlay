import tkinter as tk
import ctypes
import keyboard
import pygame
import psutil
import sys
import os

class TimerOverlay:
    def __init__(self, root, x, y):
        self.root = root
        self.root.title("Таймер")
        self.root.attributes('-topmost', True)
        self.root.geometry(f'300x200+{x}+{y}')

        self.label = tk.Label(root, text='08:00', font=('Helvetica', 48), fg='white', bg='black')
        self.label.pack(expand=True)

        self.entry_label = tk.Label(root, text='Введите время (мин):', bg='black', fg='white')
        self.entry_label.pack()

        self.time_entry = tk.Entry(root, font=('Helvetica', 24))
        self.time_entry.pack()

        self.start_button = tk.Button(root, text='Начать', command=self.set_timer)
        self.start_button.pack()

        self.total_time = 0
        self.remaining_time = 0
        self.running = False
        self.can_toggle = True  # Флаг для блокировки нажатий

        # Инициализация pygame и загрузка звуков
        pygame.mixer.init()
        try:
            self.start_sound = pygame.mixer.Sound('start_sound.wav')
            self.end_sound = pygame.mixer.Sound('end_sound.wav')
        except pygame.error as e:
            print(f"Ошибка загрузки звука: {e}")

        # Настройка горячей клавиши
        keyboard.add_hotkey('shift+.', self.toggle_timer)

    def set_timer(self):
        """Устанавливает таймер на введенное пользователем количество минут."""
        try:
            minutes = int(self.time_entry.get())
            self.total_time = minutes * 60  # Конвертация в секунды
            self.remaining_time = self.total_time
            self.label.config(text=f'{minutes:02d}:00')  # Обновление метки
            self.time_entry.delete(0, tk.END)  # Очистка поля ввода
        except ValueError:
            self.label.config(text='Ошибка ввода!')  # Сообщение об ошибке

    def toggle_timer(self):
        if self.can_toggle:
            self.can_toggle = False  # Блокировка нажатий
            if not self.running:
                self.start_timer()
            else:
                self.reset_timer()

            # Сбрасываем флаг can_toggle через 200 мс
            self.root.after(200, self.reset_toggle_flag)

    def reset_toggle_flag(self):
        self.can_toggle = True  # Разрешаем повторные нажатия

    def start_timer(self):
        self.running = True
        self.update_timer()
        try:
            self.start_sound.play()
        except pygame.error as e:
            print(f"Ошибка воспроизведения стартового звука: {e}")

    def reset_timer(self):
        self.running = False
        self.remaining_time = 0
        self.label.config(text='08:00')

    def update_timer(self):
        if self.remaining_time > 0 and self.running:
            minutes, seconds = divmod(self.remaining_time, 60)
            self.label.config(text=f'{minutes:02d}:{seconds:02d}')
            self.remaining_time -= 1
            self.root.after(1000, self.update_timer)
        elif self.remaining_time <= 0:
            self.label.config(text='Время вышло!')
            try:
                self.end_sound.play()
            except pygame.error as e:
                print(f"Ошибка воспроизведения звука окончания таймера: {e}")
            self.reset_timer()

def get_second_monitor_position():
    user32 = ctypes.windll.user32
    primary_width = user32.GetSystemMetrics(0)
    primary_height = user32.GetSystemMetrics(1)
    monitor_count = user32.GetSystemMetrics(80)
    if monitor_count > 1:
        return -primary_width, 0
    return 0, 0

if __name__ == '__main__':
    root = tk.Tk()
    x, y = get_second_monitor_position()
    timer = TimerOverlay(root, x, y)

    root.mainloop()
