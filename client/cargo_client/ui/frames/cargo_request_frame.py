from cargo_client.ui.api_client import APIClient
from tkinter import Frame, Label, Entry, Button, OptionMenu, StringVar, Listbox, messagebox, Text, END

from cargo_client.models import User
from cargo_client.models import Cargo
from cargo_client.enums import TransportType
from cargo_client.models import Response
from cargo_client.ui.frames.base_frame import BaseFrame

class CargoRequestFrame(BaseFrame):
    """فرم ثبت درخواست حمل بار - مخصوص صاحب بار"""

    def __init__(self, container, api_client: APIClient, current_user: User):
        super().__init__(container)

        self.api_client = api_client
        self.current_user = current_user

        self.cardo_requested_data: list[Cargo] = []

        self.transport_options = {
            "ground": TransportType.GROUND.value,
            "air": TransportType.AIR.value,
            "sea": TransportType.SEA.value,
        }

        self.build_form()
        self.build_cargo_list()
        self.build_offers_panel()

    def build_offers_panel(self):
        """پنل نمایش پیشنهادات قیمت بار انتخاب شده."""
        panel = Frame(self, bg=self["bg"])
        panel.pack(pady=10)

        Label(panel, text="Price offers for selected cargo", font=("Segoe UI", 12, "bold"),
              bg=self["bg"]).pack(pady=5)

        self.offers_listbox = Listbox(panel, font=("Segoe UI", 10), width=80, height=8)
        self.offers_listbox.pack(pady=5)

        self.offers_empty_label = Label(panel, text="Select a cargo to see its price offers.",
                                        font=("Segoe UI", 10), bg=self["bg"], fg="gray")
        self.offers_empty_label.pack(pady=2)

        # زمانی که کاربر بار را انتخاب می‌کند، پیشنهادات بارگذاری می‌شوند
        self.cargo_listbox.bind("<<ListboxSelect>>", self.on_cargo_select)

    def build_form(self):
        form = Frame(self, bg=self["bg"])
        form.pack(pady=10)

        Label(form, text='Submit a Cargo Shipping request', font=("Segoe UI", 14, "bold"),
              bg=self["bg"]).grid(row=0, column=0, columnspan=2, pady=10)

        self.title_entry = self._add_row(form, 1, "Cargo Title:")
        self.weight_entry = self._add_row(form, 2, "Weight:")
        self.origin_entry = self._add_row(form, 3, "Origin:")
        self.destination_entry = self._add_row(form, 4, "Destination:")

        Label(form, text="Shipping Method:", font=("Segoe UI", 11), bg=self["bg"]).grid(row=5, column=0, padx=10, pady=10, sticky="e")
        self.transport_var = StringVar(form, value=TransportType.GROUND.value)
        OptionMenu(form, self.transport_var, *self.transport_options.keys()).grid(row=5, column=1, padx=10, pady=10, sticky="w")

        Label(form, text="Description:", font=("Segoe UI", 11), bg=self["bg"]).grid(row=6, column=0, padx=10, pady=10, sticky="ne")
        self.description_text = Text(form, width=30, height=4, font=("Segoe UI", 11))
        self.description_text.grid(row=6, column=1, padx=10, pady=10)

        submit_btn = Button(self, text="Submit Request", command=self.submit,
                            font=("Segoe UI", 11, "bold"), bg="#4682B4", fg="#FFFFFF",
                            activebackground="#4169E1", activeforeground="#FFFFFF",
                            relief="raised", borderwidth=0)
        submit_btn.pack(pady=10)

    def _add_row(self, form, row, label_text):
        Label(form, text=label_text, font=("Segoe UI", 11), bg=self["bg"]).grid(row=row, column=0, padx=10, pady=6, sticky="e")
        entry = Entry(form, font=("Segoe UI", 11), bg="#FFFFFF", relief="solid", borderwidth=1, width=32)
        entry.grid(row=row, column=1, padx=10, pady=6, sticky="w")
        return entry

    def build_cargo_list(self):
        Label(self, text="Your registered cargos", font=("Segoe UI", 12, "bold"),
              bg=self["bg"]).pack(pady=5)
        self.cargo_listbox = Listbox(self, font=("Segoe UI", 10), width=80, height=8)
        self.cargo_listbox.pack(pady=5)
        self.refresh_cargo_list()

    def refresh_cargo_list(self, cargo: Cargo = None):
        if cargo is None or cargo.cargo_id is None:
            self.cargo_listbox.delete(0, END)

            response: Response = self.api_client.get_cargos_of_owner()

            if not response.success:
                messagebox.showerror(title="Error", message=response.message)
                return

            self.cardo_requested_data = response.data
            self.cardo_requested_data.sort(key=lambda x: x.cargo_id)
            for cargo in self.cardo_requested_data:
                self.cargo_listbox.insert(END, self._format(cargo))
        else:
            self.cardo_requested_data.append(cargo)
            self.cargo_listbox.insert(END, self._format(cargo))

    def on_cargo_select(self, event):
        selection = self.cargo_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        if index >= len(self.cardo_requested_data):
            return
        cargo = self.cardo_requested_data[index]
        self.load_offers(cargo.cargo_id)

    def load_offers(self, cargo_id: int):
        """لیست پیشنهادات قیمت بار انتخاب‌شده را از سرویس گرفته و نمایش می‌دهد."""
        self.offers_listbox.delete(0, END)
        response: Response = self.api_client.get_offers_for_cargo(cargo_id)
        if not response.success:
            messagebox.showerror(title="Error", message=response.message)
            return

        offers = response.data or []
        if not offers:
            self.offers_empty_label.config(text="No price offers yet for this cargo.")
            return

        self.offers_empty_label.config(text=f"{len(offers)} offer(s) found:")
        for offer in offers:
            self.offers_listbox.insert(END, self._format_offer(offer))

    @staticmethod
    def _format_offer(offer):
        msg = f" | {offer.message}" if offer.message else ""
        return f"Offer #{offer.offer_id} | {offer.price} | {offer.created_at}{msg}"

    @staticmethod
    def _format(cargo):
        return f"#{cargo.cargo_id} | {cargo.title} | {cargo.origin} ← {cargo.destination} | {cargo.transport_type} | {cargo.weight}kg"

    def submit(self):
        try:
            title = self.title_entry.get().strip()
            origin = self.origin_entry.get().strip()
            destination = self.destination_entry.get().strip()
            weight = float(self.weight_entry.get().strip())
            description = self.description_text.get("1.0", END).strip()
            transport_type = self.transport_options[self.transport_var.get()]

            if not title or not origin or not destination:
                raise ValueError("All fields must be completed.")

            response: Response = self.api_client.submit_cargo_request(
                title, description, weight,
                origin, destination, transport_type
            )

            if not response.success:
                messagebox.showerror('Error', response.message)
                return
            
            messagebox.showinfo("Success", "Cargo request successfully submitted.")
            self._clear_form()
            self.refresh_cargo_list(response.data)
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
        except Exception as e:
            messagebox.showerror("Error", getattr(e, "message", str(e)))

    def _clear_form(self):
        self.title_entry.delete(0, END)
        self.weight_entry.delete(0, END)
        self.origin_entry.delete(0, END)
        self.destination_entry.delete(0, END)
        self.description_text.delete("1.0", END)

