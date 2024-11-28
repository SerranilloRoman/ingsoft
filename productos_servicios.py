import customtkinter as ctk
from tkinter import messagebox
from tkinter import ttk
from conexion import ConexionDB
import mysql.connector

class ProductosServiciosApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana principal
        self.title("Gestión de Productos/Servicios")
        self.geometry("800x600")

        # Conexión a la base de datos
        conexion_db = ConexionDB()
        self.conexion = conexion_db.conectar()

        if self.conexion:
            self.cursor = self.conexion.cursor()
        else:
            print("Error al conectar a la base de datos")
            self.cursor = None

        # Configuración de la tabla en la base de datos
        self.create_table()

        # Frame para los botones
        self.frame = ctk.CTkFrame(self, width=600, height=250, corner_radius=20, fg_color="#D6CDC6")
        self.frame.pack(padx=20, pady=20)

        # Agregar botón
        self.add_button = ctk.CTkButton(self.frame, text="Agregar", command=self.agregar_producto_servicio)
        self.add_button.place(x=50, y=50)

        # Editar botón
        self.edit_button = ctk.CTkButton(self.frame, text="Editar", command=self.editar_producto_servicio)
        self.edit_button.place(x=200, y=50)

        # Eliminar botón
        self.delete_button = ctk.CTkButton(self.frame, text="Eliminar", command=self.eliminar_producto_servicio)
        self.delete_button.place(x=350, y=50)

        # Input fields
        self.nombre_var = ctk.StringVar()
        self.descripcion_var = ctk.StringVar()
        self.precio_var = ctk.DoubleVar()

        ctk.CTkLabel(self.frame, text="Nombre:").place(x=50, y=120)
        self.nombre_entry = ctk.CTkEntry(self.frame, textvariable=self.nombre_var)
        self.nombre_entry.place(x=150, y=120)

        ctk.CTkLabel(self.frame, text="Descripción:").place(x=50, y=160)
        self.descripcion_entry = ctk.CTkEntry(self.frame, textvariable=self.descripcion_var)
        self.descripcion_entry.place(x=150, y=160)

        ctk.CTkLabel(self.frame, text="Precio:").place(x=50, y=200)
        self.precio_entry = ctk.CTkEntry(self.frame, textvariable=self.precio_var)
        self.precio_entry.place(x=150, y=200)

        # Frame para la tabla
        self.table_frame = ctk.CTkFrame(self, width=760, height=250, corner_radius=20, fg_color="#E3E1D5")
        self.table_frame.pack(padx=20, pady=20, fill="both")

        # Configuración de la tabla
        self.tree = ttk.Treeview(self.table_frame, columns=("ID", "Nombre", "Descripción", "Precio", "Fecha Creación"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Descripción", text="Descripción")
        self.tree.heading("Precio", text="Precio")
        self.tree.heading("Fecha Creación", text="Fecha Creación")

        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 10))
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Cargar los datos de la base de datos
        self.cargar_tabla()

    def create_table(self):
        """Crea la tabla productos_servicios si no existe"""
        query = """CREATE TABLE IF NOT EXISTS productos_servicios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(255) NOT NULL,
                    descripcion TEXT,
                    precio DECIMAL(10, 2) NOT NULL,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)"""
        self.cursor.execute(query)
        self.conexion.commit()

    def cargar_tabla(self):
        """Carga los datos de la base de datos en la tabla"""
        for row in self.tree.get_children():
            self.tree.delete(row)

        query = "SELECT * FROM productos_servicios"
        self.cursor.execute(query)
        productos = self.cursor.fetchall()

        for producto in productos:
            self.tree.insert("", "end", values=producto)

    def agregar_producto_servicio(self):
        """Agrega un nuevo producto/servicio"""
        nombre = self.nombre_var.get()
        descripcion = self.descripcion_var.get()
        precio = self.precio_var.get()

        if not nombre or not precio:
            messagebox.showerror("Error", "Por favor ingrese todos los campos obligatorios.")
            return

        query = "INSERT INTO productos_servicios (nombre, descripcion, precio) VALUES (%s, %s, %s)"
        try:
            self.cursor.execute(query, (nombre, descripcion, precio))
            self.conexion.commit()
            messagebox.showinfo("Éxito", "Producto/Servicio agregado correctamente.")
            self.clear_fields()
            self.cargar_tabla()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error al agregar el producto/servicio: {err}")

    def editar_producto_servicio(self):
        """Edita un producto/servicio seleccionado en la tabla"""
        seleccionado = self.tree.selection()

        if not seleccionado:
            messagebox.showerror("Error", "Por favor seleccione un producto/servicio para editar.")
            return  # Si no se seleccionó nada, salimos de la función

        item = seleccionado[0]
        producto_id = self.tree.item(item, "values")[0]  # El ID está en la primera columna
        nombre = self.nombre_var.get()
        descripcion = self.descripcion_var.get()
        precio = self.precio_var.get()

        if not nombre or not precio:
            messagebox.showerror("Error", "Por favor ingrese todos los campos obligatorios.")
            return  # Si no se ingresan datos, salimos de la función

        query = "UPDATE productos_servicios SET nombre = %s, descripcion = %s, precio = %s WHERE id = %s"
        try:
            self.cursor.execute(query, (nombre, descripcion, precio, producto_id))
            self.conexion.commit()

            if self.cursor.rowcount > 0:
                messagebox.showinfo("Éxito", "Producto/Servicio actualizado correctamente.")
            else:
                messagebox.showwarning("Advertencia", "No se encontró un producto/servicio con ese ID.")

            self.cargar_tabla()  # Recargamos la tabla después de editar
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error al actualizar el producto/servicio: {err}")

    def eliminar_producto_servicio(self):
        """Elimina un producto/servicio seleccionado en la tabla"""
        seleccionado = self.tree.selection()

        if not seleccionado:
            messagebox.showerror("Error", "Por favor seleccione un producto/servicio para eliminar.")
            return  # Si no se seleccionó nada, salimos de la función

        item = seleccionado[0]
        producto_id = self.tree.item(item, "values")[0]  # El ID está en la primera columna

        query = "DELETE FROM productos_servicios WHERE id = %s"
        try:
            self.cursor.execute(query, (producto_id,))
            self.conexion.commit()

            if self.cursor.rowcount > 0:
                messagebox.showinfo("Éxito", "Producto/Servicio eliminado correctamente.")
            else:
                messagebox.showwarning("Advertencia", "No se encontró un producto/servicio con ese ID.")

            self.cargar_tabla()  # Recargamos la tabla después de eliminar
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error al eliminar el producto/servicio: {err}")

    def clear_fields(self):
        """Limpia los campos del formulario"""
        self.nombre_var.set("")
        self.descripcion_var.set("")
        self.precio_var.set(0.0)

if __name__ == "__main__":
    app = ProductosServiciosApp()
    app.mainloop()
