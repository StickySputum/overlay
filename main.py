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
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.geometry(f'250x150+{x}+{y}')
        
        self.root.wm_attributes('-transparentcolor', 'black')
        self.root.config(bg='black')

        self.label = tk.Label(root, text='08:00', font=('Helvetica', 48), fg='white', bg='black')
        self.label.pack(expand=True)

        self.total_time = 480  # 8 минут
        self.remaining_time = self.total_time
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
        keyboard.add_hotkey('shift+caps lock', self.toggle_timer)

        # Скрываем окно таймера до тех пор, пока не запустится Dota 2
        self.root.withdraw()
        self.check_dota_running()  # Начинаем проверку процесса
    
    def check_dota_running(self):
        """Проверяет, запущен ли процесс Dota 2 и управляет видимостью таймера."""
        if any(proc.name() == "dota2.exe" for proc in psutil.process_iter()):
            self.root.deiconify()  # Показываем таймер
        else:
            self.root.withdraw()  # Скрываем таймер

        # Если таймер видим и Dota 2 закрыта, завершаем выполнение программы
        if self.root.winfo_viewable() and not any(proc.name() == "dota2.exe" for proc in psutil.process_iter()):
            self.root.destroy()  # Закрываем окно таймера
            os._exit(0)  # Завершаем выполнение скрипта
            sys.exit()
            

        # Проверка каждую секунду
        self.root.after(1000, self.check_dota_running)

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
        self.remaining_time = self.total_time
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

def make_window_clickthrough(hwnd):
    styles = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
    ctypes.windll.user32.SetWindowLongW(hwnd, -20, styles | 0x80000 | 0x20)
    ctypes.windll.user32.SetWindowPos(hwnd, None, 0, 0, 0, 0,
                                      0x0001 | 0x0002 | 0x0040)

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

    hwnd = ctypes.windll.user32.GetForegroundWindow()
    make_window_clickthrough(hwnd)

    root.mainloop()
