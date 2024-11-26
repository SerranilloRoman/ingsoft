import customtkinter as ctk
from PIL import Image, ImageTk, ImageFilter

ctk.set_appearance_mode("light")  # Opcional: apariencia oscura
ctk.set_default_color_theme("dark-blue")  # Tema base

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

        username_entry = ctk.CTkEntry(login_frame, width=300, height=40, corner_radius=10, fg_color="#FFFFFF")
        username_entry.pack(pady=(0, 20))  # Espaciado entre elementos

        # Campo de contraseña
        password_label = ctk.CTkLabel(login_frame, text="Contraseña", font=("Arial", 18), text_color="#FFFFFF")
        password_label.pack(pady=(0, 10))

        password_entry = ctk.CTkEntry(login_frame, width=300, height=40, corner_radius=10, fg_color="#FFFFFF", show="*")
        password_entry.pack(pady=(0, 30))

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
        print("Botón de ingreso presionado")

if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()
