import customtkinter as ctk
from PIL import Image, ImageTk

class MenuPosApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana principal
        self.title("Menu POS")
        self.geometry("1440x1024")
        self.configure(bg_color="#D6CDC6")  # Fondo color #D6CDC6

        # Crear el frame de fondo (color #D6CDC6)
        background_frame = ctk.CTkFrame(self, width=1440, height=1024, corner_radius=0)
        background_frame.place(relx=0.5, rely=0.5, anchor="center")
        background_frame.configure(fg_color="#D6CDC6")

        # Barra superior (con bordes inferiores redondeados)
        top_bar = ctk.CTkFrame(self, width=1440, height=170, corner_radius=75, fg_color="#556483")
        top_bar.place(relx=0.5, rely=-0.05, anchor="n")

        # Logo en la esquina izquierda
        try:
            logo_image = Image.open("completespa_isologo.png").resize((100, 100))  # Ajustar el tamaño de la imagen
            logo_tk = ImageTk.PhotoImage(logo_image)
            logo_label = ctk.CTkLabel(top_bar, image=logo_tk, text="")
            logo_label.image = logo_tk  # Para evitar que se elimine la imagen
            logo_label.place(x=40, y=45)
        except FileNotFoundError:
            print("Error: No se encontró la imagen logo.png")

        # Botones circulares en la parte derecha
        button1 = ctk.CTkButton(top_bar, text="", width=80, height=80, corner_radius=40, fg_color="#FFFFFF", command=self.button_action)
        button1.place(x=1100, y=60)

        button2 = ctk.CTkButton(top_bar, text="", width=80, height=80, corner_radius=40, fg_color="#FFFFFF", command=self.button_action)
        button2.place(x=1250, y=60)

        # Botones en zigzag o W en el frame de fondo
        button_positions = [
            (250, 400), (450, 600), (650, 400), (850, 600), (1050, 400)
        ]
        button_images = ["cashier.png", "registry.png", "expense.png", "registry.png", "report.png"]
        button_labels = [
            "Ticket de Venta", "Registro de Ventas", "Ticket Gasto", "Registro Gastos", "Reporte"
        ]

        for index, (pos, img_path, label_text) in enumerate(zip(button_positions, button_images, button_labels)):
            # Determinar si el label va arriba o abajo
            label_y_offset = -30 if index % 2 == 0 else 170

            try:
                # Cargar y redimensionar la imagen
                img = Image.open(img_path).resize((100, 100))  # Ajusta el tamaño si es necesario
                img_tk = ImageTk.PhotoImage(img)

                # Crear el botón con la imagen
                button = ctk.CTkButton(background_frame, text="", image=img_tk, width=140, height=140, corner_radius=70, fg_color="#FFFFFF", command=self.button_action)
                button.image = img_tk  # Evitar que el recolector de basura elimine la imagen
                button.place(x=pos[0], y=pos[1])

                # Crear el label correspondiente
                label = ctk.CTkLabel(background_frame, text=label_text, font=("Arial", 23, "bold"), text_color="#FFFFFF")
                label.place(x=pos[0] + 125, y=pos[1] + label_y_offset, anchor="center")

            except FileNotFoundError:
                print(f"Error: No se encontró la imagen {img_path}")

    def button_action(self):
        print("Botón presionado")

if __name__ == "__main__":
    app = MenuPosApp()
    app.mainloop()
