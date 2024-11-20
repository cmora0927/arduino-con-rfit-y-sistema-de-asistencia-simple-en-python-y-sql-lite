import sqlite3
import serial
from datetime import datetime


"cambiar arduino por alguno que este conectado y ajustar los bau =__="
try:
    arduino = serial.Serial(port='COM7', baudrate=9600, timeout=1)
    print("Conexión con Arduino establecida.")
except serial.SerialException as e:
    print(f"Error al conectar con Arduino: {e}")
    exit()


"base de datosss"
try:
    conexion = sqlite3.connect("asistencia.db")
    cursor = conexion.cursor()
    print("Conexión con la base de datos establecida.")
except sqlite3.Error as e:
    print(f"Error al conectar con la base de datos: {e}")
    exit()


def registrar_asistencia(uid):
    """
    Registra la asistencia de un usuario con el UID recibido.

    :param uid: UID leído por el lector RFID.
    """
    try:
        # Buscar el usuario en la base de datos
        cursor.execute("SELECT id, nombre FROM usuarios WHERE uid = ?", (uid,))
        usuario = cursor.fetchone()
        if usuario:
            usuario_id, nombre = usuario
            fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Registrar asistencia
            cursor.execute(
                "INSERT INTO asistencias (usuario_id, fecha_hora) "
                "VALUES (?, ?)",
                (usuario_id, fecha_hora)
            )
            conexion.commit()
            print(
                f"Asistencia registrada para '{nombre}' a las {fecha_hora}."
            )
        else:
            print(f"UID '{uid}' no registrado en la base de datos.")
    except sqlite3.Error as e:
        print(f"Error al registrar asistencia: {e}")


def leer_rfid():
    """
    Lee datos del arduino :0
    """
    try:
        while True:
            if arduino.in_waiting > 0:  # Verifica si hay datos en el buffer
                uid = arduino.readline().decode('utf-8').strip()
                if uid:
                    print(f"UID recibido: {uid}")
                    registrar_asistencia(uid)
    except serial.SerialException as e:
        print(f"Error en la lectura desde el puerto serial: {e}")
    except KeyboardInterrupt:
        print("\nPrograma interrumpido manualmente.")
        cerrar_conexiones()


def cerrar_conexiones():
    """
    Cierra las conexiones Con el arduino y la db
    """
    try:
        if arduino.is_open:
            arduino.close()
            print("Conexión con Arduino cerrada.")
        if conexion:
            conexion.close()
            print("Conexión con la base de datos cerrada.")
    except Exception as e:
        print(f"Error al cerrar las conexiones: {e}")


"la ejecucion"
if __name__ == "__main__":
    try:
        print("Esperando datos del Arduino...")
        leer_rfid()
    except Exception as e:
        print(f"Error inesperado: {e}")
        cerrar_conexiones()
