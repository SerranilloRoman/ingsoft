import customtkinter as ctk
from tkinter import *
from tkinter import ttk
from tkinter import Scrollbar, IntVar, StringVar
from conexion import ConexionDB
from PIL import Image, ImageTk


class TicketVentaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana principal
        self.title("Ticket de Venta")
        self.geometry("1440x800")
        self.configure(bg_color="#556483")

        # Conexión a la base de datos
        conexion_db = ConexionDB()
        self.conexion = conexion_db.conectar()

        if self.conexion:
            self.cursor = self.conexion.cursor()
        else:
            print("Error al conectar a la base de datos")
            self.cursor = None

        # Frame de fondo
        background_frame = ctk.CTkFrame(self, width=1440, height=1024, corner_radius=0)
        background_frame.place(relx=0.5, rely=0.5, anchor="center")
        background_frame.configure(fg_color="#556483")

        # Frame formulario
        form_frame = ctk.CTkFrame(self, width=1000, height=700, corner_radius=20, fg_color="#D6CDC6")
        form_frame.place(relx=0.5, rely=0.1, anchor="n")

        # Combobox de clientes
        client_label = ctk.CTkLabel(form_frame, text="Cliente", font=("Arial", 18), text_color="#000000")
        client_label.place(x=50, y=30)

        self.client_combobox = ttk.Combobox(form_frame, width=50)
        self.populate_combobox("cliente", "nombre", self.client_combobox)
        self.client_combobox.place(x=150, y=30)

        # Combobox de servicios y productos
        services_label = ctk.CTkLabel(form_frame, text="Servicios/Productos", font=("Arial", 18), text_color="#000000")
        services_label.place(x=50, y=90)

        self.services_combobox = ttk.Combobox(form_frame, width=50)
        self.populate_combobox("producto", "nombre", self.services_combobox)
        self.populate_combobox("procedimiento", "nombre", self.services_combobox, append=True)
        self.services_combobox.place(x=250, y=90)

        # Selección de cantidad
        quantity_label = ctk.CTkLabel(form_frame, text="Cantidad", font=("Arial", 18), text_color="#000000")
        quantity_label.place(x=600, y=90)

        self.quantity_var = IntVar(value=1)
        self.quantity_spinbox = ttk.Spinbox(form_frame, from_=1, to=100, width=5, textvariable=self.quantity_var)
        self.quantity_spinbox.place(x=700, y=90)

        # Botón de confirmar servicios/productos
        try:
            confirm_img = Image.open("yes.png").resize((30, 30))
            confirm_tk = ImageTk.PhotoImage(confirm_img)
        except FileNotFoundError:
            print("Error: No se encontró la imagen yes.png")
            confirm_tk = None

        confirm_button = ctk.CTkButton(form_frame, text="", image=confirm_tk, width=50, height=50, fg_color="#D6CDC6",
                                       command=self.add_service_to_list)
        confirm_button.image = confirm_tk
        confirm_button.place(x=800, y=85)

        # Listado de servicios/productos seleccionados
        list_frame = ctk.CTkFrame(form_frame, width=900, height=500, fg_color="#FFFFFF")
        list_frame.place(relx=0.5, rely=0.3, anchor="n")

        # Tabla de productos/servicios seleccionados
        self.table = ttk.Treeview(list_frame, columns=("Servicio/Producto", "Cantidad", "Acciones"), show="headings", height=20)
        self.table.heading("Servicio/Producto", text="Servicio/Producto")
        self.table.heading("Cantidad", text="Cantidad")
        self.table.heading("Acciones", text="Acciones")
        self.table.column("Servicio/Producto", width=400)
        self.table.column("Cantidad", width=150)
        self.table.column("Acciones", width=150)

        # Barra de desplazamiento
        scrollbar = Scrollbar(list_frame, orient="vertical", command=self.table.yview)
        scrollbar.pack(side="right", fill="y")
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.pack(side="left", expand=True, fill="both")

        # Botón de confirmar venta fuera del list_frame
        confirm_sale_button = ctk.CTkButton(
            form_frame,
            text="", 
            image=confirm_tk, 
            width=50, 
            height=50, 
            fg_color="#FFFFFF", 
            command=self.confirm_sale
        )
        confirm_sale_button.image = confirm_tk
        confirm_sale_button.place(relx=0.5, rely=0.85, anchor="n")

    def populate_combobox(self, table_name, column_name, combobox, append=False):
        """Llena el combobox con datos de la tabla especificada."""
        if not self.cursor:
            print("Error: No hay conexión activa a la base de datos.")
            return

        query = f"SELECT {column_name} FROM {table_name}"
        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()

            if not append:
                combobox['values'] = [row[0] for row in rows]
            else:
                existing_values = combobox['values']
                combobox['values'] = list(existing_values) + [row[0] for row in rows]
        except Exception as e:
            print(f"Error al llenar el combobox: {e}")

    def add_service_to_list(self):
        """Agrega el servicio o producto seleccionado a la tabla."""
        selected_item = self.services_combobox.get()
        quantity = self.quantity_var.get()
        if selected_item:
            self.table.insert("", "end", values=(selected_item, quantity, "Eliminar"))
            self.services_combobox.set("")
            self.quantity_var.set(1)

    def confirm_sale(self):
        """Confirma la venta y procede al pago."""
        print("Confirmar venta presionado")
        for item in self.table.get_children():
            service, quantity, _ = self.table.item(item)["values"]
            print(f"Servicio/Producto: {service}, Cantidad: {quantity}")


if __name__ == "__main__":
    app = TicketVentaApp()
    app.mainloop()

