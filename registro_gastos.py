import customtkinter as ctk
from customtkinter import CTkImage
from tkinter import *
from tkinter import ttk
from conexion import ConexionDB
from PIL import Image, ImageTk
from searchable_combobox import SearchableCombobox
from directorio_imagen import find_directory


class GastoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana principal
        self.title("Gastos")
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

        # Frame formulario
        form_frame = ctk.CTkFrame(self, width=1000, height=700, corner_radius=20, fg_color="#D6CDC6")
        form_frame.place(relx=0.5, rely=0.1, anchor="n")

        # Label titulo
        title_label = ctk.CTkLabel(form_frame, text="GASTOS", font=("Arial", 48), text_color="#FFFFFF")
        title_label.place(relx=.4, y=30)

        # Combobox de busqueda (especificar atributo)
        attrib_label = ctk.CTkLabel(form_frame, text="Columna", font=("Arial", 18), text_color="#000000")
        attrib_label.place(x=30+50, y=90)

        self.attrib_combobox = SearchableCombobox(form_frame, width=30)
        self.attrib_combobox.place(x=150+50, y=120)
        # Lista de opciones
        options = ["Fecha", "Hora", "Motivo"]
        # Popular el combobox con las opciones
        self.attrib_combobox.set_completion_list(options)

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

            # Obtener la opción seleccionada del attrib_combobox
            selected_option = self.attrib_combobox.get()

            # Switch para determinar tabla y atributo
            match selected_option:
                case "Fecha":
                    tabla = "transaccion"
                    atributo = "fecha"
                case "Hora":
                    tabla = "transaccion"
                    atributo = "hora"
                case "Motivo":
                    tabla = "egreso"
                    atributo = "motivo"
                case _:
                    tabla = None
                    atributo = None

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
        self.table = ttk.Treeview(list_frame, columns=("Fecha", "Hora", "Motivo","Monto Total", "Metodo de Pago", "Notas"), show="headings", height=20)
        self.table.heading("Fecha", text="Fecha")
        self.table.heading("Hora", text="Hora")
        self.table.heading("Motivo", text="Motivo")
        self.table.heading("Monto Total", text="Monto Total")
        self.table.heading("Metodo de Pago", text="Metodo de Pago")
        self.table.heading("Notas", text="Notas")
        self.table.column("Fecha", width=70)
        self.table.column("Hora", width=70)
        self.table.column("Motivo", width=150)
        self.table.column("Monto Total", width=100)
        self.table.column("Metodo de Pago", width=100)
        self.table.column("Notas", width=250)

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
                t.fecha, 
                t.hora, 
                t.montoTotal, 
                t.metodoPago, 
                e.motivo, 
                t.notas
            FROM transaccion t
            LEFT JOIN egreso e ON t.id = e.idTransaccion
        """
        # Condición de búsqueda
        if search_value:
            if search_value == "show_aux": 
                query += " WHERE t.metodoPago IN ('Efectivo', 'Tarjeta de Crédito', 'Transferencia', 'Tarjeta de Débito')"
            else:   
                query += f" WHERE {column_name} LIKE %s"
                search_value = f"%{search_value}%"

        # Filtro por tipo
        query += " AND t.tipo = 1"

        # Agrupar resultados
        query += " GROUP BY t.id"

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

    def show_all(self):
        """Muestra todos los registros en el Treeview."""
        self.services_combobox.set("")  # Vaciar el combobox de búsqueda
        self.fill_treeview("metodoPago", "show_aux")  # Mostrar todos los registros sin filtro



if __name__ == "__main__":
    app = GastoApp()
    app.mainloop()

