from tkinter import Tk, Frame

from cargo_client.ui.frames.navbar import Navbar
from cargo_client.ui.frames.login_frame import LoginFrame
from cargo_client.ui.frames.register_frame import RegisterFrame
from cargo_client.ui.frame_factory import FrameFactory
from cargo_client.ui.api_client import APIClient
from cargo_client.models import User
from cargo_client.enums import UserRole
from cargo_client.events import EventBus, Event

class ViewContainer(Tk):
    def __init__(self, api_client: APIClient):
        super().__init__()

        self.api_client = api_client

        self.current_user: User = None

        self.title("Cargo Transfer")
        self.geometry('1000x900')

        self.frame_container = Frame(self)
        self.frame_container.pack(expand=True)

        self.frames: dict[str, Frame] = {
            'login': None,
            'register': None,
            'cargo_request': None,
            'cargo_offer': None,
            'navbar': None
        }

        self.add_frames()
        self.subscribe_events()
        self.show_frame('login')

    def subscribe_events(self):
        """Observer: subscribe to events published by frames."""
        EventBus.subscribe(Event.LOGIN_SUCCEEDED, self.on_login)
        EventBus.subscribe(Event.LOGOUT, self.on_logout)
        EventBus.subscribe(Event.GO_TO_REGISTER, lambda _: self.show_frame('register'))
        EventBus.subscribe(Event.GO_TO_LOGIN, lambda _: self.show_frame('login'))

    def add_frames(self):
        login_frame = LoginFrame(self.frame_container, self.api_client)
        self.frames['login'] = login_frame

        register_frame = RegisterFrame(self.frame_container, self.api_client)
        self.frames['register'] = register_frame

    def show_frame(self, frm_name: str):
        frame = self.frames[frm_name]
        frame.pack(expand=True)

    def on_login(self, user):
        self.current_user = user
        self.open_navbar()
        self.open_role_frame()

    def on_logout(self, _=None):
        self.logout()

    def open_navbar(self):
        navbar = Navbar(self.frame_container)
        navbar.pack(expand=True)
        navbar.set_current_user(self.current_user)
        self.frames['navbar'] = navbar

    def open_role_frame(self):
        """بعد از لاگین موفق، فرم مناسب نقش کاربر را می‌سازد و نمایش می‌دهد."""
        role = UserRole(self.current_user.role)
        if role == UserRole.CARGO_OWNER:
            key = 'cargo_request'
        else:
            key = 'cargo_offer'

        frame = FrameFactory.create_role_frame(
            role, self.frame_container, self.api_client, self.current_user
        )
        self.frames[key] = frame

        frame.pack(expand=True)

    def logout(self):
        self.api_client.logout()
        self.current_user = None

        self.destroy_frame('navbar')
        self.destroy_frame('cargo_request')
        self.destroy_frame('cargo_offer')
            
        self.show_frame('login')

    def destroy_frame(self, page_name: str):
        frame = self.frames.get(page_name)
        if frame:
            frame.destroy()
        self.frames[page_name] = None