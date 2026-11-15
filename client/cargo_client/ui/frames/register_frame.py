from tkinter import Frame, Label, Entry, Button, StringVar, Radiobutton, messagebox, END

from cargo_client.enums import UserRole
from cargo_client.models import Response
from cargo_client.ui.api_client import APIClient
from cargo_client.ui.frames.base_frame import BaseFrame
from cargo_client.events import EventBus, Event

class RegisterFrame(BaseFrame):
    def __init__(self, container: Frame, api_client: APIClient):
        super().__init__(container)

        self.api_client = api_client

        self.build_widgets()

    def build_widgets(self):
        self.user_info_frame = Frame(self)
        self.user_info_frame.pack()

        self.name_label = Label(self.user_info_frame, text="Name:", font=('Segoe UI', 11), bg='#F0F0F0')
        self.name_label.grid(row=0, column=0, pady=10)
        self.name_entry = Entry(self.user_info_frame, font=('Segoe UI', 11), bg='#FFFFFF', relief='solid', borderwidth=1)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)

        self.user_name_label = Label(self.user_info_frame, text="User name:", font=('Segoe UI', 11), bg='#F0F0F0')
        self.user_name_label.grid(row=1, column=0, pady=10)
        self.user_name_entry = Entry(self.user_info_frame, font=('Segoe UI', 11), bg='#FFFFFF', relief='solid', borderwidth=1)
        self.user_name_entry.grid(row=1, column=1, padx=10, pady=10)

        self.phone_number_label = Label(self.user_info_frame, text="Mobile phone:", font=('Segoe UI', 11), bg='#F0F0F0')
        self.phone_number_label.grid(row=2, column=0, pady=10)
        self.phone_number_entry = Entry(self.user_info_frame, font=('Segoe UI', 11), bg='#FFFFFF', relief='solid', borderwidth=1)
        self.phone_number_entry.grid(row=2, column=1, padx=10, pady=10)

        self.password_label = Label(self.user_info_frame, text="Password:", font=('Segoe UI', 11), bg='#F0F0F0')
        self.password_label.grid(row=3, column=0, pady=10)
        self.password_entry = Entry(self.user_info_frame, show="*", font=('Segoe UI', 11), bg='#FFFFFF', relief='solid', borderwidth=1)
        self.password_entry.grid(row=3, column=1, padx=10, pady=10)

        self.confirm_password_label = Label(self.user_info_frame, text="Confirm password:", font=('Segoe UI', 11), bg='#F0F0F0')
        self.confirm_password_label.grid(row=4, column=0, pady=10)
        self.confirm_password_entry = Entry(self.user_info_frame, show="*", font=('Segoe UI', 11), bg='#FFFFFF', relief='solid', borderwidth=1)
        self.confirm_password_entry.grid(row=4, column=1, padx=10, pady=10)

        self.user_role_label = Label(self.user_info_frame, text="User Role:", font=('Segoe UI', 11), bg='#F0F0F0')
        self.user_role_label.grid(row=5, column=0, pady=10)

        self.user_role = StringVar(self.user_info_frame, UserRole.CARGO_OWNER.value)
        values = {
            "Cargo Owner" : UserRole.CARGO_OWNER.value,
            "Cargo Carrier" : UserRole.CARGO_CARRIER.value
        }
        column = 1
        for (key, value) in values.items():
            Radiobutton(self.user_info_frame, text = key, variable = self.user_role,
                value = value).grid(row=5, column=column, pady=10)
            column += 1

        self.registe_button = Button(self.user_info_frame, text="Register",
            font=('Segoe UI', 11), bg='#4682B4', fg='#FFFFFF',
            activebackground='#4169E1', activeforeground='#FFFFFF',
            relief='raised', borderwidth=0, command=self.register)
        self.registe_button.grid(row=6, column=1, pady=10)

        self.show_login_label = Label(self.user_info_frame,
            text="Go to login", font=("Segoe UI", 11),
            bg="#F0F0F0", fg="blue", cursor="hand2")
        self.show_login_label.grid(row=7, column=1, pady=10)
        self.show_login_label.bind("<Button-1>", lambda e: self.go_to_login())

    def register(self):
        name = self.name_entry.get().strip()
        user_name = self.user_name_entry.get().strip()
        phone_number = self.phone_number_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()
        role = self.user_role.get()

        if not name or not user_name or not phone_number or not password or not confirm_password:
            messagebox.showerror('Error', 'Please enter the value of all fields.')
            return

        if password != confirm_password:
            messagebox.showerror('Error', 'The password and password confirmation values ​​must be the same..')
            return

        response: Response = self.api_client.register(
            name=name, user_name=user_name, password=password,
            confirm_password=confirm_password, phone_number=phone_number, role=role,
        )
        if not response.success:
            messagebox.showerror('Error', response.message)
            return

        messagebox.showinfo('Success', response.message)
        self.go_to_login()

    def go_to_login(self):
        self.clear_user_inputs()
        self.pack_forget()
        EventBus.publish(Event.GO_TO_LOGIN)

    def clear_user_inputs(self):
        self.name_entry.delete(0, END)
        self.user_name_entry.delete(0, END)
        self.phone_number_entry.delete(0, END)
        self.password_entry.delete(0, END)
        self.confirm_password_entry.delete(0, END)
        self.user_role.set(UserRole.CARGO_OWNER.value)