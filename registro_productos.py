import customtkinter as ctk
from customtkinter import CTkImage
from tkinter import *
from tkinter import ttk
from conexion import ConexionDB
from PIL import Image, ImageTk
from searchable_combobox import SearchableCombobox
from directorio_imagen import find_directory
from datetime import time

class FrameController(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana principal
        self.title("Productos")
        self.geometry("1440x800")
        self.configure(fg_color="#556483")

        # Conexión a la base de datos
        conexion_db = ConexionDB()
        self.conexion = conexion_db.conectar()

        if self.conexion:
            self.cursor = self.conexion.cursor()
        else:
            print("Error al conectar a la base de datos")
            self.cursor = None

        # Crear frames para cada pantalla
        self.frames = {}
        for FrameClass in (ProductApp, ProductAddApp):
            frame = FrameClass(parent=self, controller=self)
            self.frames[FrameClass.__name__] = frame
            frame.place(relwidth=1, relheight=1)

        # Mostrar el frame inicial
        self.show_frame("ProductApp")

    def show_frame(self, frame_name):
        """Muestra el frame especificado y oculta los demás."""
        frame = self.frames[frame_name]
        frame.tkraise()

class ProductApp(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#556483")
        self.controller = controller
        # Conexión a la base de datos
        conexion_db = ConexionDB()
        self.conexion = conexion_db.conectar()

        if self.conexion:
            self.cursor = self.conexion.cursor()
        else:
            print("Error al conectar a la base de datos")
            self.cursor = None

        # Frame formulario
        form_frame = ctk.CTkFrame(self, width=1000, height=700, corner_radius=20, fg_color="#D6CDC6")
        form_frame.place(relx=0.5, rely=0.1, anchor="n")

        # Label titulo
        title_label = ctk.CTkLabel(form_frame, text="PRODUCTOS", font=("Arial", 48), text_color="#FFFFFF")
        title_label.place(relx=.4, y=30)

        # Combobox de busqueda (especificar atributo)
        attrib_label = ctk.CTkLabel(form_frame, text="Columna", font=("Arial", 18), text_color="#000000")
        attrib_label.place(x=30+50, y=90)

        self.attrib_combobox = SearchableCombobox(form_frame, width=30)
        self.attrib_combobox.place(x=150+50, y=120)
        # Lista de opciones
        options = ["Selecciona", "Producto", "Procedimiento"]
        # Popular el combobox con las opciones
        self.attrib_combobox.set_completion_list(options)
        self.attrib_combobox.set('Selecciona')
        # Variables iniciales
        tabla = ""
        atributo = ""

        # Combobox de busqueda (coincidencias)
        search_label = ctk.CTkLabel(form_frame, text="Busqueda", font=("Arial", 18), text_color="#000000")
        search_label.place(x=300+50, y=90)

        self.services_combobox = SearchableCombobox(form_frame, width=70)
        self.services_combobox.place(x=500+50, y=120)
        self.populate_combobox(tabla, atributo, self.services_combobox, append=True)


        def update_services_combobox(event):
            # Limpiar combobox (comentar o descomentar segun se necesite)
            self.services_combobox.set_completion_list([])

            # Si tabla y atributo son válidos, actualizar el services_combobox
            if tabla and atributo:
                self.populate_combobox(tabla, atributo, self.services_combobox, append=True)
            else:
                # Limpiar el combobox si no hay una opción válida
                self.services_combobox.set_completion_list([])

        # Asociar el evento de cambio al attrib_combobox
        self.attrib_combobox.bind("<<ComboboxSelected>>", update_services_combobox)

        # Listado de servicios/productos seleccionados
        list_frame = ctk.CTkFrame(form_frame, width=900, height=500, fg_color="#FFFFFF")
        list_frame.place(relx=0.5, rely=0.3, anchor="n")

        # Tabla de productos/servicios seleccionados
        self.table = ttk.Treeview(list_frame, columns=("Nombre", "Tipo", "Precio"), show="headings", height=20)
        self.table.heading("Nombre", text="Nombre")
        self.table.heading("Tipo", text="Tipo")
        self.table.heading("Precio", text="Precio")

        # Barra de desplazamiento
        scrollbar = Scrollbar(list_frame, orient="vertical", command=self.table.yview)
        scrollbar.pack(side="right", fill="y")
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.pack(side="left", expand=True, fill="both")

        self.fill_treeview("metodoPago", "show_aux")

        # Función para actualizar el Treeview con los datos según la búsqueda
        self.services_combobox.bind("<<ComboboxSelected>>", self.update_treeview)

        # Botón para mostrar todos los registros
        self.show_all_button = ctk.CTkButton(form_frame, text="Mostrar Todos", font=("Arial", 16), command=self.show_all)
        self.show_all_button.place(x=720, y=170)

        add_tk = find_directory("plus.png", 30)

        add_product_button = ctk.CTkButton(
            form_frame,
            text="", 
            image=add_tk, 
            width=50, 
            height=50, 
            fg_color="#FFFFFF", 
            command=self.go_to_ProductAddFrame
        )
        add_product_button.image = add_tk
        add_product_button.place(x=825, y=225)

    def update_treeview(self, event):
        """Actualiza el Treeview según el valor de búsqueda seleccionado."""
        search_value = self.services_combobox.get()
        selected_option = self.attrib_combobox.get()

        # Mapea las columnas de la base de datos a las opciones seleccionadas
        if selected_option == "Fecha":
            column_name = "t.fecha"
        elif selected_option == "Hora":
            column_name = "t.hora"
        elif selected_option == "Motivo":
            column_name = "e.motivo"
        else:
            column_name = None

        self.fill_treeview(column_name, search_value)

    def populate_combobox(self, table_name, column_name, combobox, append=False):
        """Llena el combobox con datos de la tabla especificada."""
        if not self.cursor:
            print("Error: No hay conexión activa a la base de datos.")
            return

        query = f"SELECT DISTINCT {column_name} FROM {table_name}"
        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            new_values = [row[0] for row in rows]
            print("exito en popular el combobox")

            if append and hasattr(combobox, '_completion_list'):
                current_values = combobox._completion_list
                combobox.set_completion_list(current_values + new_values)
            else:
                combobox.set_completion_list(new_values)
        except Exception as e:  
            print(f"Error al llenar el combobox: {e}")

    def fill_treeview(self, column_name, search_value=None):
        """Llena el Treeview con los datos de ventas, considerando la búsqueda."""
        if not self.cursor:
            print("Error: No hay conexión activa a la base de datos.")
            return

        query = """
            SELECT 
                nombre, 
                precioUnitario AS precio,  -- Para los productos, se usa precioUnitario como 'precio'
                'Producto' AS Tipo  -- La columna 'Tipo' tendrá el valor 'Producto'
            FROM Producto

            UNION ALL

            SELECT 
                nombre, 
                costo AS precio,  -- Para los procedimientos, se usa costo como 'precio'
                'Procedimiento' AS Tipo  -- La columna 'Tipo' tendrá el valor 'Procedimiento'
            FROM Procedimiento;
        """
        selected_option = self.attrib_combobox.get()

        if selected_option == "Producto":
            query = """
                SELECT 
                    nombre, 
                    precioUnitario AS precio,  -- Para los productos, se usa precioUnitario como 'precio'
                    'Producto' AS Tipo  -- La columna 'Tipo' tendrá el valor 'Producto'
                FROM Producto
            """
        elif selected_option == "Procedimiento":
            query = """SELECT 
                nombre, 
                costo AS precio,  -- Para los procedimientos, se usa costo como 'precio'
                'Procedimiento' AS Tipo  -- La columna 'Tipo' tendrá el valor 'Procedimiento'
                FROM Procedimiento; 
            """
        
        try:
            if search_value and search_value != "show_aux":
                self.cursor.execute(query, (search_value,))
            else:
                self.cursor.execute(query)
            rows = self.cursor.fetchall()

            # Limpiar el Treeview antes de agregar nuevos registros
            for row in self.table.get_children():
                self.table.delete(row)

            # Insertar los datos en el Treeview
            for row in rows:
                self.table.insert("", "end", values=row)
        except Exception as e:
            print(f"Error al llenar el Treeview: {e}")

    def go_to_ProductAddFrame(self):
        self.controller.show_frame("ProductAddApp")

    def show_all(self):
        """Muestra todos los registros en el Treeview."""
        self.services_combobox.set("")  # Vaciar el combobox de búsqueda
        self.fill_treeview("metodoPago", "show_aux")  # Mostrar todos los registros sin filtro

    def add_product(self):
        print("")

class ProductAddApp(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#556483")

        self.controller = controller

        # Conexión a la base de datos
        conexion_db = ConexionDB()
        self.conexion = conexion_db.conectar()

        if self.conexion:
            self.cursor = self.conexion.cursor()
        else:
            print("Error al conectar a la base de datos")
            self.cursor = None

        # Frame formulario
        self.form_frame = ctk.CTkFrame(self, width=1000, height=700, corner_radius=20, fg_color="#D6CDC6")
        self.form_frame.place(relx=0.5, rely=0.1, anchor="n")

        self.categoria = StringVar(value="Producto")
        self.nombre = StringVar()
        self.precio = DoubleVar(value=0.0)
        self.personal = StringVar()
        self.duracion = time(00,00,00)

        duracion_str = str(self.duracion)  # Convertimos a string (e.g., '14:30:45')

        # Usamos StringVar para manejar la entrada de texto
        self.duracion_var = ctk.StringVar(value=duracion_str)
        
        # Labels y entradas
        labels_text = [
            "CATEGORIA", "NOMBRE", "PRECIO",
            "PERSONAL REQUERIDO", "DURACION"
        ]

        for idx, text in enumerate(labels_text):
            ctk.CTkLabel(self.form_frame, text=text, font=("Arial", 16), text_color="#000000").place(x=250, y=30 + idx * 60)
        
        self.tipo = ctk.CTkOptionMenu(self.form_frame, variable=self.categoria, 
                                                values=["Producto", "Procedimiento"], fg_color="#FFFFFF", command=self.actualizar_campos)  # Llamamos a actualizar_campos al cambiar la opción
        self.tipo.place(x=450, y=30)

        # Crear los CTkEntry para nombre, precio, personal, y duración
        nombre_entry = ctk.CTkEntry(self.form_frame, fg_color="#FFFFFF", text_color="#000000", textvariable=self.nombre, width=200)
        nombre_entry.place(x=450, y=90)

        precio_entry = ctk.CTkEntry(self.form_frame, fg_color="#FFFFFF", text_color="#000000", textvariable=self.precio, width=200)
        precio_entry.place(x=450, y=150)

        self.actualizar_campos()
        # Botones

        confirm_icon = ctk.CTkButton(self.form_frame, text="", width=50, height=50, fg_color="#FFFFFF", command=self.confirmar_pago)
        confirm_icon.place(x=700, y=500)

        return_tk = find_directory("return.png", 30)

        return_sale_button = ctk.CTkButton(
            self.form_frame,
            text="", 
            image=return_tk, 
            width=50, 
            height=50, 
            fg_color="#FFFFFF", 
            command=self.go_to_ProductApp
        )
        return_sale_button.image = return_tk
        return_sale_button.place(x=250, y=500)

    def go_to_ProductApp(self):
        self.controller.show_frame("ProductApp")

    def confirmar_pago(self):
            if self.categoria.get() == "Producto":
                try:
                    # Comprobar que los valores necesarios están disponibles
                    if self.nombre.get() and self.precio.get() and self.categoria.get():
                        # Consulta de inserción con placeholders
                        query = """
                            INSERT INTO Producto (nombre, precioUnitario, categoria)
                            VALUES (%s, %s, %s);
                        """
                        precio = float(self.precio.get())
                        self.cursor.execute(query, (self.nombre.get(), float(self.precio.get()), self.categoria.get()))
                        self.cursor.commit()
                        # Mensaje de éxito
                        print("Producto insertado correctamente.")
                    else:
                        print("Por favor, completa todos los campos antes de insertar.")
                except Exception as e:
                    # Manejo de errores
                    print(f"Error al insertar el producto: {e}")

            else:
                try:
                    # Comprobar que los valores necesarios están disponibles
                    if self.nombre.get() and self.precio.get() and self.categoria.get():
                        # Consulta de inserción con placeholders
                        query = """
                        INSERT INTO Procedimiento (nombre, personalrequerido, costo, duracion)
                        VALUES (%s, %s, %s, %s);
                        """
                        # Ejecutar la consulta con los valores
                        self.cursor.execute(query, (self.nombre.get(), self.personal.get(), float(self.precio.get()), time(self.duracion.get())))

                        # Mensaje de éxito
                        print("Producto insertado correctamente.")
                    else:
                        print("Por favor, completa todos los campos antes de insertar.")
                except Exception as e:
                    # Manejo de errores
                    print(f"Error al insertar el producto: {e}")
 
    def actualizar_campos(self, *args):
        # Comprobar si la categoría seleccionada es "Procedimiento"
        if self.categoria.get() == "Procedimiento":
            # Si es "Procedimiento", mostrar los campos adicionales
                self.personal_entry = ctk.CTkEntry(self.form_frame, fg_color="#FFFFFF", text_color="#000000", textvariable=self.personal, width=200)
                self.personal_entry.place(x=450, y=210)

                self.duracion_entry = ctk.CTkEntry(self.form_frame, fg_color="#FFFFFF", text_color="#000000", textvariable=self.duracion_var, width=200)
                self.duracion_entry.place(x=450, y=270)
        else:
            # Si no es "Procedimiento", ocultar los campos
            if hasattr(self, 'personal_entry'):
                self.personal_entry.place_forget()
                self.duracion_entry.place_forget()

if __name__ == "__main__":
    app = FrameController()
    app.mainloop()

