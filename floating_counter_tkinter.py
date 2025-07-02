import tkinter as tk
from tkinter import font, colorchooser
import threading
from pynput import keyboard as pynput_keyboard  # For global hotkeys

class FloatingCounter:
    def __init__(self, root, label_text, font_family, font_size, font_color, track_attempts, key_inc_success, key_inc_attempt, key_dec_success, enable_hotkeys, show_buttons):
        self.root = root
        self.root.overrideredirect(True)  # Remove window borders
        self.root.attributes('-topmost', True)
        self.root.attributes('-transparentcolor', 'white')  # Make white transparent
        self.root.configure(bg='white')
        self.successes = 0
        self.attempts = 0
        self.label_text = label_text
        self.font_family = font_family
        self.font_size = font_size
        self.font_color = font_color
        self.track_attempts = track_attempts
        self.key_inc_success = key_inc_success
        self.key_inc_attempt = key_inc_attempt
        self.key_dec_success = key_dec_success
        self.enable_hotkeys = enable_hotkeys
        self.show_buttons = show_buttons

        # Main frame for label and buttons
        self.frame = tk.Frame(root, bg='white')
        self.frame.pack(padx=20, pady=20)

        # Counter label
        self.label = tk.Label(
            self.frame,
            text=self.get_display_text(),
            font=(self.font_family, self.font_size),
            fg=self.font_color,
            bg='white'
        )
        self.label.grid(row=0, column=0, columnspan=4, pady=(0, 2))

        # On-screen buttons
        self.create_buttons()

        # Bind hotkeys
        root.bind('<F2>', self.toggle_settings)
        root.bind('<Escape>', lambda e: root.destroy())

        # Drag window
        self.label.bind('<ButtonPress-1>', self.start_move)
        self.label.bind('<B1-Motion>', self.do_move)
        self._offsetx = 0
        self._offsety = 0

        self.settings_window = None

        # Start global hotkey listener in a thread if enabled
        self.listener_thread = None
        if self.enable_hotkeys:
            self.listener_thread = threading.Thread(target=self.listen_hotkeys, daemon=True)
            self.listener_thread.start()

    def get_display_text(self):
        if self.track_attempts:
            return f"{self.label_text} {self.successes}/{self.attempts}"
        else:
            return f"{self.label_text} {self.successes}"

    def create_buttons(self):
        # Remove old buttons if they exist
        for widget in self.frame.grid_slaves():
            if int(widget.grid_info()['row']) == 1:
                widget.destroy()
        if not self.show_buttons:
            return
        # Button font and sizing
        min_font_size = 10
        min_width = 8
        min_ipadx = 4
        min_ipady = 2
        btn_font_size = max(min_font_size, self.font_size // 3)
        btn_font = (self.font_family, btn_font_size)
        btn_width = max(min_width, len('Success +'))
        # Success buttons
        tk.Button(self.frame, text='Success +', width=btn_width, font=btn_font, fg='#176117', command=self.increment_success_and_attempt if self.track_attempts else self.increment_success_only).grid(row=1, column=0, padx=2, pady=(0, 2), ipadx=min_ipadx, ipady=min_ipady)
        tk.Button(self.frame, text='Success -', width=btn_width, font=btn_font, command=self.decrement_success_only).grid(row=1, column=1, padx=2, pady=(0, 2), ipadx=min_ipadx, ipady=min_ipady)
        # Attempt buttons (if enabled)
        if self.track_attempts:
            tk.Button(self.frame, text='Attempt +', width=btn_width, font=btn_font, fg='#a11a1a', command=self.increment_attempt_only).grid(row=1, column=2, padx=2, pady=(0, 2), ipadx=min_ipadx, ipady=min_ipady)
            tk.Button(self.frame, text='Attempt -', width=btn_width, font=btn_font, command=self.decrement_attempt_only).grid(row=1, column=3, padx=2, pady=(0, 2), ipadx=min_ipadx, ipady=min_ipady)

    def listen_hotkeys(self):
        def get_key(key_str):
            if not key_str:
                return None
            if len(key_str) == 1:
                return pynput_keyboard.KeyCode.from_char(key_str)
            try:
                return getattr(pynput_keyboard.Key, key_str)
            except AttributeError:
                return pynput_keyboard.KeyCode.from_char(key_str)
        inc_success_key = get_key(self.key_inc_success)
        inc_attempt_key = get_key(self.key_inc_attempt) if self.track_attempts else None
        dec_success_key = get_key(self.key_dec_success)
        def on_press(key):
            try:
                if key == inc_success_key:
                    if self.track_attempts:
                        self.increment_success_and_attempt()
                    else:
                        self.increment_success_only()
                elif self.track_attempts and key == inc_attempt_key:
                    self.increment_attempt_only()
                elif key == dec_success_key:
                    if self.track_attempts:
                        self.decrement_success_and_attempt()
                    else:
                        self.decrement_success_only()
            except Exception as e:
                print(f"Hotkey error: {e}")
        with pynput_keyboard.Listener(on_press=on_press) as listener:
            listener.join()

    def increment_success_and_attempt(self, event=None):
        self.successes += 1
        self.attempts += 1
        self.update_label()

    def increment_attempt_only(self, event=None):
        self.attempts += 1
        self.update_label()

    def decrement_success_and_attempt(self, event=None):
        if self.successes > 0:
            self.successes -= 1
        if self.attempts > 0:
            self.attempts -= 1
        self.update_label()

    def increment_success_only(self, event=None):
        self.successes += 1
        self.update_label()

    def decrement_success_only(self, event=None):
        if self.successes > 0:
            self.successes -= 1
        self.update_label()

    def decrement_attempt_only(self, event=None):
        if self.attempts > 0:
            self.attempts -= 1
        self.update_label()

    def update_label(self):
        self.label.config(
            text=self.get_display_text(),
            font=(self.font_family, self.font_size),
            fg=self.font_color
        )
        self.create_buttons()

    def toggle_settings(self, event=None):
        if self.settings_window and tk.Toplevel.winfo_exists(self.settings_window):
            self.settings_window.destroy()
            self.settings_window = None
        else:
            self.open_settings()

    def open_settings(self):
        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title('Font & Counter Settings')
        self.settings_window.geometry('+100+100')
        self.settings_window.attributes('-topmost', True)

        # Label text
        tk.Label(self.settings_window, text='Label Text:').pack()
        self.label_var = tk.StringVar(value=self.label_text)
        label_entry = tk.Entry(self.settings_window, textvariable=self.label_var)
        label_entry.pack()

        # Font family
        tk.Label(self.settings_window, text='Font Family:').pack()
        font_families = list(font.families())
        self.font_var = tk.StringVar(value=self.font_family)
        font_menu = tk.OptionMenu(self.settings_window, self.font_var, *font_families)
        font_menu.pack()

        # Font size
        tk.Label(self.settings_window, text='Font Size:').pack()
        self.size_var = tk.IntVar(value=self.font_size)
        size_entry = tk.Entry(self.settings_window, textvariable=self.size_var)
        size_entry.pack()

        # Font color
        tk.Label(self.settings_window, text='Font Color:').pack()
        color_btn = tk.Button(self.settings_window, text='Choose Color', command=self.choose_color)
        color_btn.pack()

        # Track attempts checkbox
        self.track_attempts_var = tk.BooleanVar(value=self.track_attempts)
        attempts_check = tk.Checkbutton(self.settings_window, text='Track Attempts (X/Y)', variable=self.track_attempts_var, command=self.update_hotkey_fields_settings)
        attempts_check.pack(pady=5)

        # Enable hotkeys checkbox
        self.enable_hotkeys_var = tk.BooleanVar(value=self.enable_hotkeys)
        hotkeys_check = tk.Checkbutton(self.settings_window, text='Enable global hotkeys', variable=self.enable_hotkeys_var)
        hotkeys_check.pack(pady=5)

        # Show buttons checkbox
        self.show_buttons_var = tk.BooleanVar(value=self.show_buttons)
        buttons_check = tk.Checkbutton(self.settings_window, text='Show on-screen buttons', variable=self.show_buttons_var)
        buttons_check.pack(pady=5)

        # Hotkey fields (dynamically shown/hidden)
        self.hotkey_frame = tk.Frame(self.settings_window)
        self.hotkey_frame.pack(pady=5)
        self.create_hotkey_fields_settings()

        # Note about Shift
        tk.Label(self.settings_window, text='If no hotkeys are selected, buttons will appear on screen to manage the counting.').pack(pady=(10, 0))
        tk.Label(self.settings_window, text='Note: +, _, and | require holding Shift').pack(pady=(0, 0))

        # Apply button
        apply_btn = tk.Button(self.settings_window, text='Apply', command=self.apply_settings)
        apply_btn.pack(pady=10)

    def create_hotkey_fields_settings(self):
        for widget in self.hotkey_frame.winfo_children():
            widget.destroy()
        if self.track_attempts_var.get():
            tk.Label(self.hotkey_frame, text='Increment Success & Attempt key:').pack()
            self.key_inc_success_var = tk.StringVar(value=self.key_inc_success)
            key_inc_success_entry = tk.Entry(self.hotkey_frame, textvariable=self.key_inc_success_var)
            key_inc_success_entry.pack()
            tk.Label(self.hotkey_frame, text='Increment Attempt Only key:').pack()
            self.key_inc_attempt_var = tk.StringVar(value=self.key_inc_attempt)
            key_inc_attempt_entry = tk.Entry(self.hotkey_frame, textvariable=self.key_inc_attempt_var)
            key_inc_attempt_entry.pack()
            tk.Label(self.hotkey_frame, text='Decrement Success & Attempt key:').pack()
            self.key_dec_success_var = tk.StringVar(value=self.key_dec_success)
            key_dec_success_entry = tk.Entry(self.hotkey_frame, textvariable=self.key_dec_success_var)
            key_dec_success_entry.pack()
        else:
            tk.Label(self.hotkey_frame, text='Increment Success key:').pack()
            self.key_inc_success_var = tk.StringVar(value=self.key_inc_success)
            key_inc_success_entry = tk.Entry(self.hotkey_frame, textvariable=self.key_inc_success_var)
            key_inc_success_entry.pack()
            tk.Label(self.hotkey_frame, text='Decrement Success key:').pack()
            self.key_dec_success_var = tk.StringVar(value=self.key_dec_success)
            key_dec_success_entry = tk.Entry(self.hotkey_frame, textvariable=self.key_dec_success_var)
            key_dec_success_entry.pack()

    def update_hotkey_fields_settings(self):
        self.create_hotkey_fields_settings()

    def choose_color(self):
        color = colorchooser.askcolor(initialcolor=self.font_color)[1]
        if color:
            self.font_color = color

    def apply_settings(self):
        self.label_text = self.label_var.get()
        self.font_family = self.font_var.get()
        self.font_size = self.size_var.get()
        self.track_attempts = self.track_attempts_var.get()
        self.enable_hotkeys = self.enable_hotkeys_var.get()
        self.show_buttons = self.show_buttons_var.get()
        self.key_inc_success = self.key_inc_success_var.get()
        if self.track_attempts:
            self.key_inc_attempt = self.key_inc_attempt_var.get()
        else:
            self.key_inc_attempt = ''
        self.key_dec_success = self.key_dec_success_var.get()
        # Rebind hotkeys if enabled
        if self.enable_hotkeys:
            if not self.listener_thread or not self.listener_thread.is_alive():
                self.listener_thread = threading.Thread(target=self.listen_hotkeys, daemon=True)
                self.listener_thread.start()
        self.update_label()
        if self.settings_window:
            self.settings_window.destroy()
            self.settings_window = None

    def start_move(self, event):
        self._offsetx = event.x
        self._offsety = event.y

    def do_move(self, event):
        x = self.root.winfo_pointerx() - self._offsetx
        y = self.root.winfo_pointery() - self._offsety
        self.root.geometry(f'+{x}+{y}')

# Note: The white border around the text is due to Tkinter's transparency and anti-aliasing. This is a known limitation and is difficult to avoid.

def launch_setup():
    setup = tk.Tk()
    setup.title('Floating Counter Setup')
    setup.geometry('400x620')
    setup.attributes('-topmost', True)

    # Label text
    tk.Label(setup, text='Label Text:').pack(pady=(20, 0))
    label_var = tk.StringVar(value='Mounts Dropped:')
    label_entry = tk.Entry(setup, textvariable=label_var)
    label_entry.pack()

    # Font family
    tk.Label(setup, text='Font Family:').pack(pady=(10, 0))
    font_families = list(font.families())
    font_var = tk.StringVar(value='Arial')
    font_menu = tk.OptionMenu(setup, font_var, *font_families)
    font_menu.pack()

    # Font size
    tk.Label(setup, text='Font Size:').pack(pady=(10, 0))
    size_var = tk.IntVar(value=48)
    size_entry = tk.Entry(setup, textvariable=size_var)
    size_entry.pack()

    # Font color
    tk.Label(setup, text='Font Color:').pack(pady=(10, 0))
    color_var = tk.StringVar(value='#FF0000')
    def choose_color():
        color = colorchooser.askcolor(initialcolor=color_var.get())[1]
        if color:
            color_var.set(color)
    color_btn = tk.Button(setup, text='Choose Color', command=choose_color)
    color_btn.pack()

    # Track attempts checkbox
    track_attempts_var = tk.BooleanVar(value=False)
    attempts_check = tk.Checkbutton(setup, text='Track Attempts (X/Y)', variable=track_attempts_var, command=lambda: update_hotkey_fields())
    attempts_check.pack(pady=10)

    # Enable hotkeys checkbox
    enable_hotkeys_var = tk.BooleanVar(value=True)
    hotkeys_check = tk.Checkbutton(setup, text='Enable global hotkeys', variable=enable_hotkeys_var)
    hotkeys_check.pack(pady=5)

    # Show buttons checkbox
    show_buttons_var = tk.BooleanVar(value=True)
    buttons_check = tk.Checkbutton(setup, text='Show on-screen buttons', variable=show_buttons_var)
    buttons_check.pack(pady=5)

    # Hotkey fields (dynamically shown/hidden)
    hotkey_frame = tk.Frame(setup)
    hotkey_frame.pack(pady=5)

    # Note about Shift
    tk.Label(setup, text='If no hotkeys are selected, buttons will appear on screen to manage the counting.').pack(pady=(10, 0))
    tk.Label(setup, text='Note: +, _, and | require holding Shift').pack(pady=(0, 0))

    def update_hotkey_fields():
        for widget in hotkey_frame.winfo_children():
            widget.destroy()
        if track_attempts_var.get():
            tk.Label(hotkey_frame, text='Increment Success & Attempt key:').pack()
            key_inc_success_var.set('+')
            key_inc_success_entry = tk.Entry(hotkey_frame, textvariable=key_inc_success_var)
            key_inc_success_entry.pack()
            tk.Label(hotkey_frame, text='Increment Attempt Only key:').pack()
            key_inc_attempt_var.set('|')
            key_inc_attempt_entry = tk.Entry(hotkey_frame, textvariable=key_inc_attempt_var)
            key_inc_attempt_entry.pack()
            tk.Label(hotkey_frame, text='Decrement Success & Attempt key:').pack()
            key_dec_success_var.set('_')
            key_dec_success_entry = tk.Entry(hotkey_frame, textvariable=key_dec_success_var)
            key_dec_success_entry.pack()
        else:
            tk.Label(hotkey_frame, text='Increment Success key:').pack()
            key_inc_success_var.set('+')
            key_inc_success_entry = tk.Entry(hotkey_frame, textvariable=key_inc_success_var)
            key_inc_success_entry.pack()
            tk.Label(hotkey_frame, text='Decrement Success key:').pack()
            key_dec_success_var.set('_')
            key_dec_success_entry = tk.Entry(hotkey_frame, textvariable=key_dec_success_var)
            key_dec_success_entry.pack()

    # Hotkey variables
    key_inc_success_var = tk.StringVar(value='+')
    key_inc_attempt_var = tk.StringVar(value='|')
    key_dec_success_var = tk.StringVar(value='_')
    update_hotkey_fields()

    def run_counter():
        setup.destroy()
        root = tk.Tk()
        app = FloatingCounter(
            root,
            label_var.get(),
            font_var.get(),
            size_var.get(),
            color_var.get(),
            track_attempts_var.get(),
            key_inc_success_var.get(),
            key_inc_attempt_var.get(),
            key_dec_success_var.get(),
            enable_hotkeys_var.get(),
            show_buttons_var.get()
        )
        root.mainloop()

    run_btn = tk.Button(setup, text='Run', command=run_counter)
    run_btn.pack(pady=20)

    setup.mainloop()

if __name__ == '__main__':
    launch_setup() 