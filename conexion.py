import pymysql

class ConexionDB:
    def __init__(self):
        self.host = "localhost"  # Cambia si usas otro host
        self.user = "root"       # Cambia al usuario de tu base de datos
        self.password = ""       # Cambia a tu contraseña
        self.database = "completespa"  # Cambia al nombre de tu base de datos
        self.port = 3306         # Cambia si tu base de datos usa otro puerto

    def conectar(self):
        try:
            conexion = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            print("Conexión exitosa a la base de datos")
            return conexion
        except pymysql.MySQLError as e:
            print(f"Error al conectar a la base de datos: {e}")
            return None

