import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector

# --- Funciones de Conexión y CRUD ---

def get_connection():
    """Establece la conexión con la base de datos MySQL."""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="pikaso1234",
        database="LAB4_TP"
    )

def create_user(nombre, apellido, dni, fecha_nacimiento, telefono, domicilio):
    """Crea un nuevo usuario en la base de datos."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """INSERT INTO usuarios (nombre, apellido, dni, fecha_nacimiento, telefono, domicilio) 
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, (nombre, apellido, dni, fecha_nacimiento, telefono, domicilio))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def read_users(order_by="id"):
    """Lee todos los usuarios de la base de datos, con opción de ordenar."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if order_by == "edad":
            query = """
                SELECT id, nombre, apellido, dni, fecha_nacimiento, telefono, domicilio,
                       TIMESTAMPDIFF(YEAR, fecha_nacimiento, CURDATE()) AS edad
                FROM usuarios
                ORDER BY edad DESC
            """
        else:
            query = f"SELECT * FROM usuarios ORDER BY {order_by}"

        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def delete_user(id_usuario):
    """Elimina un usuario de la base de datos."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "DELETE FROM usuarios WHERE id=%s"
        cursor.execute(query, (id_usuario,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def sort_data(criteria):
    """Ordena los datos según el criterio dado (alfabético, numérico por ID, edad)."""
    if criteria == "alfabetico":
        return read_users(order_by="nombre")
    elif criteria == "id":
        return read_users(order_by="id")
    elif criteria == "edad":
        return read_users(order_by="edad")

# --- Funciones CRUD Cursos ---

def create_course(nombre_curso, descripcion, fecha_inicio, fecha_fin, usuario_id):
    """Crea un nuevo curso en la base de datos vinculado a un usuario."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """INSERT INTO cursos (nombre_curso, descripcion, fecha_inicio, fecha_fin, usuario_id)
                   VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(query, (nombre_curso, descripcion, fecha_inicio, fecha_fin, usuario_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def read_courses_by_user(usuario_id):
    """Lee todos los cursos asociados a un usuario."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """SELECT * FROM cursos WHERE usuario_id = %s"""
        cursor.execute(query, (usuario_id,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# --- Clases de GUI ---

class IngresoDatos(tk.Frame):
    """Formulario para ingresar nuevos usuarios."""
    def __init__(self, parent):
        super().__init__(parent, bg="#2E2E2E")

        tk.Label(self, text="Nombre:", fg="white", bg="#2E2E2E").grid(row=0, column=0, padx=10, pady=10)
        tk.Label(self, text="Apellido:", fg="white", bg="#2E2E2E").grid(row=1, column=0, padx=10, pady=10)
        tk.Label(self, text="DNI:", fg="white", bg="#2E2E2E").grid(row=2, column=0, padx=10, pady=10)
        tk.Label(self, text="Fecha de Nacimiento:", fg="white", bg="#2E2E2E").grid(row=3, column=0, padx=10, pady=10)
        tk.Label(self, text="Teléfono:", fg="white", bg="#2E2E2E").grid(row=4, column=0, padx=10, pady=10)
        tk.Label(self, text="Domicilio:", fg="white", bg="#2E2E2E").grid(row=5, column=0, padx=10, pady=10)

        self.entry_nombre = tk.Entry(self)
        self.entry_apellido = tk.Entry(self)
        self.entry_dni = tk.Entry(self)
        self.entry_fecha_nacimiento = tk.Entry(self)
        self.entry_telefono = tk.Entry(self)
        self.entry_domicilio = tk.Entry(self)

        self.entry_nombre.grid(row=0, column=1, padx=10, pady=10)
        self.entry_apellido.grid(row=1, column=1, padx=10, pady=10)
        self.entry_dni.grid(row=2, column=1, padx=10, pady=10)
        self.entry_fecha_nacimiento.grid(row=3, column=1, padx=10, pady=10)
        self.entry_telefono.grid(row=4, column=1, padx=10, pady=10)
        self.entry_domicilio.grid(row=5, column=1, padx=10, pady=10)

        self.btn_guardar = tk.Button(self, text="Guardar", command=self.guardar_datos, bg="#4CAF50", fg="white")
        self.btn_guardar.grid(row=6, column=0, columnspan=2, pady=20)

    def guardar_datos(self):
        nombre = self.entry_nombre.get()
        apellido = self.entry_apellido.get()
        dni = self.entry_dni.get()
        fecha_nacimiento = self.entry_fecha_nacimiento.get()
        telefono = self.entry_telefono.get()
        domicilio = self.entry_domicilio.get()

        if create_user(nombre, apellido, dni, fecha_nacimiento, telefono, domicilio):
            messagebox.showinfo("Éxito", "Usuario guardado correctamente")
        else:
            messagebox.showerror("Error", "No se pudo guardar el usuario")

class ConsultaDatos(tk.Frame):
    """Vista para consultar y eliminar usuarios, y ver los cursos asociados."""
    def __init__(self, parent):
        super().__init__(parent, bg="#2E2E2E")
        
        self.treeview = None
        self.selected_user_id = None

        self.container = tk.Frame(self, bg="#2E2E2E")
        self.container.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.mostrar_datos()

    def mostrar_datos(self, users=None):
        """Muestra los datos en un Treeview.
        Si no se proporcionan usuarios, los carga desde la base de datos."""
        if self.treeview is not None:
            self.treeview.destroy()

        if users is None:
            users = read_users()

        self.treeview = ttk.Treeview(
            self.container,
            columns=("ID", "Nombre", "Apellido", "DNI", "Fecha Nacimiento", "Teléfono", "Domicilio"),
            show="headings"
        )

        self.treeview.heading("ID", text="ID", anchor=tk.W, command=lambda: self.ordenar_columnas("id"))
        self.treeview.heading("Nombre", text="Nombre", anchor=tk.W, command=lambda: self.ordenar_columnas("nombre"))
        self.treeview.heading("Apellido", text="Apellido", anchor=tk.W, command=lambda: self.ordenar_columnas("apellido"))
        self.treeview.heading("DNI", text="DNI", anchor=tk.W, command=lambda: self.ordenar_columnas("dni"))
        self.treeview.heading("Fecha Nacimiento", text="Fecha Nacimiento", anchor=tk.W, command=lambda: self.ordenar_columnas("fecha_nacimiento"))
        self.treeview.heading("Teléfono", text="Teléfono", anchor=tk.W, command=lambda: self.ordenar_columnas("telefono"))
        self.treeview.heading("Domicilio", text="Domicilio", anchor=tk.W, command=lambda: self.ordenar_columnas("domicilio"))

        self.treeview.column("ID", width=50, anchor=tk.W)
        self.treeview.column("Nombre", width=150, anchor=tk.W)
        self.treeview.column("Apellido", width=150, anchor=tk.W)
        self.treeview.column("DNI", width=100, anchor=tk.W)
        self.treeview.column("Fecha Nacimiento", width=120, anchor=tk.W)
        self.treeview.column("Teléfono", width=100, anchor=tk.W)
        self.treeview.column("Domicilio", width=200, anchor=tk.W)

        for user in users:
            self.treeview.insert("", "end", values=(user[0], user[1], user[2], user[3], user[4], user[5], user[6]))

        self.treeview.grid(row=0, column=0, sticky="nsew")

        # Enlazar el evento de clic derecho
        self.treeview.bind("<Button-3>", self.clic_derecho)

           # Enlazar el evento de selección de fila
        self.treeview.bind("<ButtonRelease-1>", self.seleccionar_usuario)

        # Botón para eliminar usuario
        self.eliminar_btn = tk.Button(self.container, text="Eliminar Usuario", command=self.eliminar_usuario, bg="#FF6347", fg="white")
        self.eliminar_btn.grid(row=1, column=0, pady=10, sticky="ew")

        # Boton para editar

        self.editar_btn = tk.Button(self.container, text="Editar Usuario", command=self.editar_usuario, bg="#FFA500", fg="white")
        self.editar_btn.grid(row=2, column=0, pady=10, sticky="ew")
       

    def ordenar_columnas(self, columna):
        """Ordena los datos en la tabla según la columna seleccionada."""
        datos_ordenados = read_users(order_by=columna)
        self.mostrar_datos(users=datos_ordenados)

    def clic_derecho(self, event):
        """Maneja el evento de clic derecho en un usuario."""
        item = self.treeview.identify_row(event.y)
        if item:  # Si se hizo clic en un elemento válido
            self.selected_user_id = self.treeview.item(item)["values"][0]
            self.mostrar_cursos()

    def mostrar_cursos(self):
        """Muestra los cursos asociados al usuario seleccionado."""
        if self.selected_user_id:
            cursos = read_courses_by_user(self.selected_user_id)
            if cursos:
                # Crear un mensaje con los cursos
                mensaje = "Cursos del Usuario:\n\n"
                for curso in cursos:
                    mensaje += f"- {curso[1]}: {curso[2]}\n"  # Nombre del curso y descripción
                messagebox.showinfo("Cursos Asociados", mensaje)
            else:
                messagebox.showinfo("Cursos Asociados", "Este usuario no tiene cursos asociados.")

    def seleccionar_usuario(self, event):
        """Selecciona un usuario de la tabla cuando se hace clic en una fila."""
        item = self.treeview.selection()  # Obtiene el ID del elemento seleccionado
        if item:
            self.selected_user_id = self.treeview.item(item)["values"][0]  # Obtener el ID de la fila seleccionada
        else:
            self.selected_user_id = None

    def eliminar_usuario(self):
        """Elimina el usuario seleccionado de la base de datos."""
        if self.selected_user_id is not None:
            # Confirmar la eliminación
            respuesta = messagebox.askyesno("Confirmación", f"¿Estás seguro de que deseas eliminar el usuario con ID {self.selected_user_id}?")
            if respuesta:
                if delete_user(self.selected_user_id):
                    messagebox.showinfo("Éxito", "Usuario eliminado correctamente.")
                    self.mostrar_datos()  # Recargar los datos después de eliminar el usuario
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el usuario.")
        else:
            messagebox.showerror("Error", "No se ha seleccionado ningún usuario para eliminar.")  

    def editar_usuario(self):
            """Abre el formulario para editar el usuario seleccionado."""
            if self.selected_user_id is not None:
                EditarUsuario(self, self.selected_user_id).grab_set()
            else:
                messagebox.showerror("Error", "No se ha seleccionado ningún usuario para editar.")



class EditarUsuario(tk.Toplevel):
    """Ventana para editar un usuario."""
    def __init__(self, parent, user_id):
        super().__init__(parent)
        self.user_id = user_id
        self.title("Editar Usuario")
        self.geometry("400x400")
        self.configure(bg="#2E2E2E")

        # Cargar datos del usuario
        user_data = read_users(order_by="id")
        user_data = [user for user in user_data if user[0] == user_id][0]  # Filtrar por ID

        tk.Label(self, text="Nombre:", fg="white", bg="#2E2E2E").grid(row=0, column=0, padx=10, pady=10)
        tk.Label(self, text="Apellido:", fg="white", bg="#2E2E2E").grid(row=1, column=0, padx=10, pady=10)
        tk.Label(self, text="DNI:", fg="white", bg="#2E2E2E").grid(row=2, column=0, padx=10, pady=10)
        tk.Label(self, text="Fecha Nacimiento:", fg="white", bg="#2E2E2E").grid(row=3, column=0, padx=10, pady=10)
        tk.Label(self, text="Teléfono:", fg="white", bg="#2E2E2E").grid(row=4, column=0, padx=10, pady=10)
        tk.Label(self, text="Domicilio:", fg="white", bg="#2E2E2E").grid(row=5, column=0, padx=10, pady=10)

        self.entry_nombre = tk.Entry(self)
        self.entry_nombre.insert(0, user_data[1])  # Cargar nombre
        self.entry_apellido = tk.Entry(self)
        self.entry_apellido.insert(0, user_data[2])  # Cargar apellido
        self.entry_dni = tk.Entry(self)
        self.entry_dni.insert(0, user_data[3])  # Cargar DNI
        self.entry_fecha_nacimiento = tk.Entry(self)
        self.entry_fecha_nacimiento.insert(0, user_data[4])  # Cargar fecha de nacimiento
        self.entry_telefono = tk.Entry(self)
        self.entry_telefono.insert(0, user_data[5])  # Cargar teléfono
        self.entry_domicilio = tk.Entry(self)
        self.entry_domicilio.insert(0, user_data[6])  # Cargar domicilio

        self.entry_nombre.grid(row=0, column=1, padx=10, pady=10)
        self.entry_apellido.grid(row=1, column=1, padx=10, pady=10)
        self.entry_dni.grid(row=2, column=1, padx=10, pady=10)
        self.entry_fecha_nacimiento.grid(row=3, column=1, padx=10, pady=10)
        self.entry_telefono.grid(row=4, column=1, padx=10, pady=10)
        self.entry_domicilio.grid(row=5, column=1, padx=10, pady=10)

        self.btn_guardar = tk.Button(self, text="Guardar Cambios", command=self.guardar_cambios, bg="#4CAF50", fg="white")
        self.btn_guardar.grid(row=6, column=0, columnspan=2, pady=20)

    def guardar_cambios(self):
        nombre = self.entry_nombre.get()
        apellido = self.entry_apellido.get()
        dni = self.entry_dni.get()
        fecha_nacimiento = self.entry_fecha_nacimiento.get()
        telefono = self.entry_telefono.get()
        domicilio = self.entry_domicilio.get()

        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = """UPDATE usuarios SET nombre=%s, apellido=%s, dni=%s, fecha_nacimiento=%s, telefono=%s, domicilio=%s 
                       WHERE id=%s"""
            cursor.execute(query, (nombre, apellido, dni, fecha_nacimiento, telefono, domicilio, self.user_id))
            conn.commit()
            messagebox.showinfo("Éxito", "Usuario actualizado correctamente")
            self.destroy()  # Cerrar la ventana
        except Exception as e:
            print(f"Error: {e}")
            messagebox.showerror("Error", "No se pudo actualizar el usuario")
        finally:
            cursor.close()
            conn.close()


class IngresoCurso(tk.Frame):
    """Formulario para ingresar nuevos cursos vinculados a usuarios."""
    def __init__(self, parent):
        super().__init__(parent, bg="#2E2E2E")

        tk.Label(self, text="Nombre del Curso:", fg="white", bg="#2E2E2E").grid(row=0, column=0, padx=10, pady=10)
        tk.Label(self, text="Descripción:", fg="white", bg="#2E2E2E").grid(row=1, column=0, padx=10, pady=10)
        tk.Label(self, text="Fecha de Inicio:", fg="white", bg="#2E2E2E").grid(row=2, column=0, padx=10, pady=10)
        tk.Label(self, text="Fecha de Fin:", fg="white", bg="#2E2E2E").grid(row=3, column=0, padx=10, pady=10)
        tk.Label(self, text="ID de Usuario:", fg="white", bg="#2E2E2E").grid(row=4, column=0, padx=10, pady=10)

        self.entry_nombre_curso = tk.Entry(self)
        self.entry_descripcion = tk.Entry(self)
        self.entry_fecha_inicio = tk.Entry(self)
        self.entry_fecha_fin = tk.Entry(self)
        self.entry_usuario_id = tk.Entry(self)

        self.entry_nombre_curso.grid(row=0, column=1, padx=10, pady=10)
        self.entry_descripcion.grid(row=1, column=1, padx=10, pady=10)
        self.entry_fecha_inicio.grid(row=2, column=1, padx=10, pady=10)
        self.entry_fecha_fin.grid(row=3, column=1, padx=10, pady=10)
        self.entry_usuario_id.grid(row=4, column=1, padx=10, pady=10)

        self.btn_guardar = tk.Button(self, text="Guardar Curso", command=self.guardar_curso, bg="#4CAF50", fg="white")
        self.btn_guardar.grid(row=5, column=0, columnspan=2, pady=20)

    def guardar_curso(self):
        nombre_curso = self.entry_nombre_curso.get()
        descripcion = self.entry_descripcion.get()
        fecha_inicio = self.entry_fecha_inicio.get()
        fecha_fin = self.entry_fecha_fin.get()
        usuario_id = self.entry_usuario_id.get()

        if create_course(nombre_curso, descripcion, fecha_inicio, fecha_fin, usuario_id):
            messagebox.showinfo("Éxito", "Curso guardado correctamente")
        else:
            messagebox.showerror("Error", "No se pudo guardar el curso")
            
# --- Interfaz Principal ---

def main():
    root = tk.Tk()
    root.title("Sistema de Gestión de Usuarios")
    root.geometry("800x600")
    root.configure(bg="#2E2E2E")  # Fondo oscuro personalizado

    content_frame = tk.Frame(root, bg="#2E2E2E")
    content_frame.pack(fill="both", expand=True)

    def cargar_ingreso_datos():
        for widget in content_frame.winfo_children():
            widget.destroy()
        ingreso_form = IngresoDatos(content_frame)
        ingreso_form.pack(padx=10, pady=10)

    def cargar_consulta_datos():
        for widget in content_frame.winfo_children():
            widget.destroy()
        consulta_form = ConsultaDatos(content_frame)
        consulta_form.pack(padx=10, pady=10)

    def cargar_ingreso_curso():
        for widget in content_frame.winfo_children():
            widget.destroy()
        curso_form = IngresoCurso(content_frame)
        curso_form.pack(padx=10, pady=10)

    # Botones de navegación
    btn_ingreso = tk.Button(root, text="Ingreso Usuario", command=cargar_ingreso_datos, bg="#4CAF50", fg="white")
    btn_ingreso.pack(fill="x", padx=10, pady=5)

    btn_consulta = tk.Button(root, text="Consulta Usuario", command=cargar_consulta_datos, bg="#4CAF50", fg="white")
    btn_consulta.pack(fill="x", padx=10, pady=5)

    btn_curso = tk.Button(root, text="Ingreso Curso", command=cargar_ingreso_curso, bg="#4CAF50", fg="white")
    btn_curso.pack(fill="x", padx=10, pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()

