from cargo_client.ui.api_client import APIClient
from tkinter import Frame, Label, Entry, Button, Listbox, messagebox, END

from cargo_client.ui.frames.base_frame import BaseFrame
from cargo_client.models import Response
from cargo_client.models import Cargo

class CargoOffersFrame(BaseFrame):
    """مشاهده بارها و ثبت پیشنهاد قیمت - مخصوص حمل کننده"""

    def __init__(self, container, api_client: APIClient, current_user):
        super().__init__(container)
        
        self.api_client = api_client
        self.current_user = current_user
        self.cargos: list[Cargo] = []
        self.selected_cargo: Cargo = None

        Label(self, text='Available cargos list', font=("Segoe UI", 14, "bold"),
              bg=self["bg"]).pack(pady=10)

        self.cargo_listbox = Listbox(self, font=("Segoe UI", 10), width=90, height=8)
        self.cargo_listbox.pack(pady=5)
        self.cargo_listbox.bind("<<ListboxSelect>>", self.on_cargo_select)

        self.detail_label = Label(self, text="Select a cargo to view details.",
                                  font=("Segoe UI", 10), bg=self["bg"], justify="right", wraplength=800)
        self.detail_label.pack(pady=5)

        offer_frame = Frame(self, bg=self["bg"])
        offer_frame.pack(pady=10)

        Label(offer_frame, text="Price offer (تومان):", font=("Segoe UI", 11),
              bg=self["bg"]).grid(row=0, column=0, padx=10)
        self.price_entry = Entry(offer_frame, font=("Segoe UI", 11), bg="#FFFFFF",
                                 relief="solid", borderwidth=1, width=20)
        self.price_entry.grid(row=0, column=1, padx=10)

        submit_btn = Button(offer_frame, text="Submit Price Offer", command=self.submit_offer,
                            font=("Segoe UI", 11, "bold"), bg="#4682B4", fg="#FFFFFF",
                            activebackground="#4169E1", activeforeground="#FFFFFF",
                            relief="raised", borderwidth=0)
        submit_btn.grid(row=0, column=2, padx=10)

        self.refresh_cargo_list()

    def refresh_cargo_list(self):
        response: Response = self.api_client.get_all_cargos()

        if not response.success:
            messagebox.showerror("Error", response.message)
            return

        self.cargos = response.data
        self.cargos.sort(key=lambda x: x.cargo_id)     
        self.cargo_listbox.delete(0, END)
        for cargo in self.cargos:
            self.cargo_listbox.insert(END, f"#{cargo.cargo_id} | {cargo.title} | {cargo.origin} ← {cargo.destination} | {cargo.transport_type}")

    def on_cargo_select(self, event=None):
        selection = self.cargo_listbox.curselection()
        if not selection:
            return
        self.selected_cargo = self.cargos[selection[0]]     
        details = (f"Cargo #{self.selected_cargo.cargo_id}: {self.selected_cargo.title}\n"
                   f"Description: {self.selected_cargo.description or '-'}\n"
                   f"Weight: {self.selected_cargo.weight} kg | Origin: {self.selected_cargo.origin} | Destination: {self.selected_cargo.destination}\n"
                   f"Shipping Method: {self.selected_cargo.transport_type} | Registration date: {self.selected_cargo.created_at}")
        self.detail_label.config(text=details)

    def submit_offer(self):
        if self.selected_cargo is None:
            messagebox.showwarning("Wraning", "Choose one first.")
            return
        try:
            price = float(self.price_entry.get().strip())
            if price <= 0:
                raise ValueError("Price must be greater than zero.")
            response: Response = self.api_client.submit_price_offer(self.selected_cargo.cargo_id, price)
            if response.success:
                messagebox.showinfo("Success", f"Your bid for the {self.selected_cargo.title} has been registered."                                    )
                self.price_entry.delete(0, END)
            else:
                messagebox.showerror('Error', response.message)
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
        except Exception as e:
            messagebox.showerror("Error", getattr(e, "message", str(e)))
