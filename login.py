import customtkinter as ctk
from PIL import Image, ImageTk, ImageFilter
from conexion import ConexionDB
from menu_pos import MenuPosApp

ctk.set_appearance_mode("light")  # Opcional: apariencia oscura
ctk.set_default_color_theme("dark-blue")  # Tema base

class ErrorPopup(ctk.CTkToplevel):
    def __init__(self, parent, mensaje):
        super().__init__(parent)

        self.geometry("400x200")
        self.title("Error")
        self.configure(fg_color="#D9534F")
        self.resizable(False, False)
        self.grab_set()

        message_label = ctk.CTkLabel(
            self,
            text=mensaje,
            font=("Arial", 18),
            text_color="white",
            anchor="center"
        )
        message_label.pack(pady=(40, 20), padx=20)

        close_button = ctk.CTkButton(
            self,
            text="Cerrar",
            width=100,
            height=40,
            corner_radius=10,
            fg_color="#FFFFFF",
            text_color="#000000",
            command=self.destroy
        )
        close_button.pack(pady=(20, 0))

        self.center_window(parent)

    def center_window(self, parent):
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        x = parent_x + (parent_width // 2) - (400 // 2)
        y = parent_y + (parent_height // 2) - (200 // 2)
        self.geometry(f"+{x}+{y}")

class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana principal
        self.title("Login")
        self.geometry("1440x1024")
        self.configure(bg_color="#556483")  # Color del frame principal

        background_frame = ctk.CTkFrame(self, width=1440, height=1024, corner_radius=0)
        background_frame.place(relx=0.5, rely=0.5, anchor="center")
        background_frame.configure(fg_color="#556483")

        # Cargar y añadir los círculos decorativos
        self.add_decorative_circle("pack_cositas.png", 100, 50)  # Ajusta la posición según sea necesario
        self.add_decorative_circle("masage_piedras.png", 1200, 200)  # Otro círculo en el lado opuesto

        # Crear el rectángulo central
        login_frame = ctk.CTkFrame(self, width=485, height=671, corner_radius=20, fg_color="#D6CDC6")
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Agregar contenido al rectángulo
        logo_label = ctk.CTkLabel(login_frame, text="LOGO", font=("Arial", 32, "bold"), text_color="#FFFFFF")
        logo_label.pack(pady=(30, 20))  # Espaciado superior

        title_label = ctk.CTkLabel(login_frame, text="INGRESO", font=("Arial", 28, "bold"), text_color="#FFFFFF")
        title_label.pack(pady=(0, 30))  # Espaciado entre elementos

        # Campo de usuario
        username_label = ctk.CTkLabel(login_frame, text="Usuario", font=("Arial", 18), text_color="#FFFFFF")
        username_label.pack(pady=(0, 10))  # Espaciado superior

        self.username_entry = ctk.CTkEntry(login_frame, width=300, height=40, corner_radius=10, fg_color="#FFFFFF")
        self.username_entry.pack(pady=(0, 20))  # Espaciado entre elementos
        
        # Campo de contraseña
        password_label = ctk.CTkLabel(login_frame, text="Contraseña", font=("Arial", 18), text_color="#FFFFFF")
        password_label.pack(pady=(0, 10))

        self.password_entry = ctk.CTkEntry(login_frame, width=300, height=40, corner_radius=10, fg_color="#FFFFFF", show="*")
        self.password_entry.pack(pady=(0, 30))

        # Botón de ingreso
        login_button = ctk.CTkButton(login_frame, text="Ingresar", text_color= "#000000", width=200, height=40, corner_radius=10, fg_color="#FFFFFF", 
                                     command=self.login_action)
        login_button.pack(pady=(10, 30))

    def add_decorative_circle(self, image_path, x, y):
        """Agregar un círculo decorativo con blur"""
        try:
            # Cargar la imagen, aplicar el blur, y ajustarla al tamaño deseado
            img = Image.open(image_path).resize((882, 882)).filter(ImageFilter.GaussianBlur(5))
            img_tk = ImageTk.PhotoImage(img)

            # Crear etiqueta para mostrar la imagen
            circle_label = ctk.CTkLabel(self, image=img_tk, text="")
            circle_label.image = img_tk  # Evitar que el recolector de basura elimine la imagen
            circle_label.place(x=x, y=y)
        except FileNotFoundError:
            print(f"Error: No se encontró la imagen en {image_path}")

    def login_action(self):
        db = ConexionDB()
        conexion = db.conectar()
        user = self.username_entry.get()
        password = self.password_entry.get()

        if conexion is None:
            print("No se pudo establecer la conexión con la base de datos.")
            return 
        try:
            with conexion.cursor() as cursor:
                # Consulta SQL para verificar usuario y contraseña
                query = "SELECT * FROM Usuario WHERE contacto = %s AND contacto = %s"
                cursor.execute(query, (user, password))
                resultado = cursor.fetchone()

                if resultado:
                    print("Login exitoso. ¡Bienvenido!")
                    self.open_menu(conexion)
                else:
                    ErrorPopup(self, "Usuario o contraseña incorrectos.")
        except Exception as e:
            print(f"Error durante la consulta: {e}")
            return False
        finally:
            conexion.close()
    
        print("Botón de ingreso presionado")

    def open_menu(self, conexion):
        self.destroy()  # Cierra la ventana actual
        menu_app = MenuPosApp(conexion)  # Pasa la conexión al menú
        menu_app.mainloop()

if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()


