import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# Variable para guardar el nombre de la base de datos seleccionada
nombre_bd_seleccionada = ""

# Estilos
STYLE_COLOR = "#4A90E2"  # Color primario
BACKGROUND_COLOR = "#F4F6F8"  # Fondopyinstaller --version

BUTTON_COLOR = "#5DADE2"  # Color de botón
BUTTON_HOVER_COLOR = "#2980B9"  # Color de botón al pasar el ratón
FONT = ("Arial", 12)

# Función para mostrar todas las bases de datos
def mostrar_bases_datos():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password=""
    )
    cursor = conexion.cursor()

    cursor.execute("SHOW DATABASES")
    bases_datos = cursor.fetchall()

    for widget in panel_bases_datos.winfo_children():
        widget.destroy()

    for base_dato in bases_datos:
        nombre_bd = base_dato[0]
        frame_bd = tk.Frame(panel_bases_datos, background=BACKGROUND_COLOR)
        frame_bd.pack(pady=5, fill=tk.X)

        boton_mostrar = tk.Button(frame_bd, text=nombre_bd, command=lambda bd=nombre_bd: mostrar_tablas(bd), bg=BUTTON_COLOR, fg="white", font=FONT)
        boton_mostrar.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    conexion.close()

# Función para mostrar las tablas de una base de datos seleccionada
def mostrar_tablas(nombre_bd):
    global nombre_bd_seleccionada
    nombre_bd_seleccionada = nombre_bd  # Guardar la base de datos seleccionada
    label_bd.config(text=f"Base de Datos: {nombre_bd_seleccionada}")  # Actualizar el label

    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database=nombre_bd
    )
    cursor = conexion.cursor()

    cursor.execute("SHOW TABLES")
    tablas = cursor.fetchall()

    limpiar_panel_contenido()

    boton_eliminar_bd = tk.Button(panel_contenido, text="Borrar base de datos", command=lambda: eliminar_base_datos(nombre_bd), bg="red", fg="white", font=FONT)
    boton_eliminar_bd.pack(pady=10, fill=tk.X)

    boton_crear_tabla = tk.Button(panel_contenido, text="Crear nueva tabla", command=lambda: crear_tabla(nombre_bd), bg=BUTTON_COLOR, fg="white", font=FONT)
    boton_crear_tabla.pack(pady=10, fill=tk.X)

    for tabla in tablas:
        nombre_tabla = tabla[0]
        frame_tabla = tk.Frame(panel_contenido, background=BACKGROUND_COLOR)
        frame_tabla.pack(pady=5, fill=tk.X)

        boton_mostrar = tk.Button(frame_tabla, text=nombre_tabla, command=lambda t=nombre_tabla: mostrar_contenido(nombre_bd, t), bg=BUTTON_COLOR, fg="white", font=FONT)
        boton_mostrar.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        boton_eliminar_tabla = tk.Button(frame_tabla, text="Eliminar tabla", command=lambda t=nombre_tabla: eliminar_tabla(nombre_bd, t), bg="red", fg="white", font=FONT)
        boton_eliminar_tabla.pack(side=tk.RIGHT, padx=5)

    conexion.close()

# Función para limpiar el panel de contenido
def limpiar_panel_contenido():
    for widget in panel_contenido.winfo_children():
        widget.destroy()

# Función para mostrar el contenido de una tabla con opciones de agregar, editar y eliminar
def mostrar_contenido(nombre_bd, nombre_tabla):
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database=nombre_bd
    )
    cursor = conexion.cursor()

    cursor.execute(f"SELECT * FROM {nombre_tabla}")
    filas = cursor.fetchall()

    columnas = [i[0] for i in cursor.description]

    ventana_contenido = tk.Toplevel(ventana)
    ventana_contenido.title(f"Contenido de la tabla '{nombre_tabla}'")
    ventana_contenido.configure(background=BACKGROUND_COLOR)

    # Crear un árbol para mostrar los datos
    tree = ttk.Treeview(ventana_contenido, columns=columnas, show="headings")
    tree.pack(fill=tk.BOTH, expand=True)

    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    for fila in filas:
        tree.insert("", "end", values=fila)

   # Función para agregar una fila
    def agregar_fila():
        valores = [entradas[col].get() for col in columnas]
        try:
            cursor.execute(
                f"INSERT INTO {nombre_tabla} ({', '.join(columnas)}) VALUES ({', '.join(['%s'] * len(valores))})",
                valores,
            )
            conexion.commit()
            messagebox.showinfo("Éxito", "Fila agregada correctamente.")
            actualizar_contenido()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudo agregar la fila: {err}")


        # Función para actualizar el contenido del árbol
    def actualizar_contenido():
        tree.delete(*tree.get_children())
        cursor.execute(f"SELECT * FROM {nombre_tabla}")
        for fila in cursor.fetchall():
            tree.insert("", "end", values=fila)

      # Función para eliminar una fila seleccionada
    def eliminar_fila():
        item_seleccionado = tree.selection()
        if not item_seleccionado:
            messagebox.showwarning("Atención", "Seleccione una fila para eliminar.")
            return
        valores = tree.item(item_seleccionado)["values"]
        condicion = " AND ".join(
            f"{col} = '{val}'" for col, val in zip(columnas, valores)
        )
        try:
            cursor.execute(f"DELETE FROM {nombre_tabla} WHERE {condicion}")
            conexion.commit()
            tree.delete(item_seleccionado)
            messagebox.showinfo("Éxito", "Fila eliminada correctamente.")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudo eliminar la fila: {err}")

       # Función para editar una fila seleccionada
    def editar_fila():
        item_seleccionado = tree.selection()
        if not item_seleccionado:
            messagebox.showwarning("Atención", "Seleccione una fila para editar.")
            return
        valores_antiguos = tree.item(item_seleccionado)["values"]
        valores_nuevos = [entradas[col].get() for col in columnas]

        condicion = " AND ".join(
            f"{col} = '{val}'" for col, val in zip(columnas, valores_antiguos)
        )
        actualizaciones = ", ".join(
            f"{col} = '{val}'" for col, val in zip(columnas, valores_nuevos)
        )

        try:
            cursor.execute(f"UPDATE {nombre_tabla} SET {actualizaciones} WHERE {condicion}")
            conexion.commit()
            actualizar_contenido()
            messagebox.showinfo("Éxito", "Fila actualizada correctamente.")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudo editar la fila: {err}")

    # Panel de formularios para agregar o editar filas
    frame_formulario = tk.Frame(ventana_contenido, bg=BACKGROUND_COLOR)
    frame_formulario.pack(fill=tk.X, pady=10)

    entradas = {}
    for col in columnas:
        tk.Label(frame_formulario, text=col, background=BACKGROUND_COLOR, font=FONT).pack(side=tk.LEFT, padx=5)
        entrada = tk.Entry(frame_formulario)
        entrada.pack(side=tk.LEFT, padx=5)
        entradas[col] = entrada

    tk.Button(
        ventana_contenido,
        text="Agregar Fila",
        command=agregar_fila,
        bg=BUTTON_COLOR,
        fg="white",
        font=FONT,
    ).pack(side=tk.LEFT, padx=10)

    tk.Button(
        ventana_contenido,
        text="Editar Fila",
        command=editar_fila,
        bg=BUTTON_COLOR,
        fg="white",
        font=FONT,
    ).pack(side=tk.LEFT, padx=10)

    tk.Button(
        ventana_contenido,
        text="Eliminar Fila",
        command=eliminar_fila,
        bg="red",
        fg="white",
        font=FONT,
    ).pack(side=tk.LEFT, padx=10)

    tk.Button(
        ventana_contenido,
        text="Cerrar",
        command=ventana_contenido.destroy,
        bg=BUTTON_COLOR,
        fg="white",
        font=FONT,
    ).pack(side=tk.BOTTOM, pady=10)

    actualizar_contenido()

    conexion.close()

# Función para eliminar una tabla
def eliminar_tabla(nombre_bd, nombre_tabla):
    confirmacion = messagebox.askyesno("Confirmar", f"¿Estás seguro de que deseas eliminar la tabla '{nombre_tabla}'?")
    if confirmacion:
        try:
            conexion = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database=nombre_bd
            )
            cursor = conexion.cursor()
            cursor.execute(f"DROP TABLE {nombre_tabla}")
            conexion.commit()
            conexion.close()
            messagebox.showinfo("Éxito", f"La tabla '{nombre_tabla}' ha sido eliminada.")
            mostrar_tablas(nombre_bd)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error al eliminar la tabla: {err}")

# Función para eliminar una base de datos
def eliminar_base_datos(nombre_bd):
    confirmacion = messagebox.askyesno("Confirmar", f"¿Estás seguro de que deseas eliminar la base de datos '{nombre_bd}'?")
    if confirmacion:
        try:
            conexion = mysql.connector.connect(
                host="localhost",
                user="root",
                password=""
            )
            cursor = conexion.cursor()
            cursor.execute(f"DROP DATABASE {nombre_bd}")
            conexion.close()
            messagebox.showinfo("Éxito", f"La base de datos '{nombre_bd}' ha sido eliminada.")
            mostrar_bases_datos()
            limpiar_panel_contenido()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error al eliminar la base de datos: {err}")

# Función para crear una nueva base de datos
def crear_base_datos():
    ventana_crear_bd = tk.Toplevel(ventana)
    ventana_crear_bd.title("Crear nueva base de datos")
    ventana_crear_bd.configure(background=BACKGROUND_COLOR)

    tk.Label(ventana_crear_bd, text="Nombre de la base de datos:", background=BACKGROUND_COLOR, font=FONT).pack(pady=5)
    entrada_nombre_bd = tk.Entry(ventana_crear_bd)
    entrada_nombre_bd.pack(pady=5)

    def siguiente():
        nombre_bd = entrada_nombre_bd.get()
        if not nombre_bd:
            messagebox.showerror("Error", "Debe ingresar un nombre para la base de datos.")
            return

        try:
            conexion = mysql.connector.connect(
                host="localhost",
                user="root",
                password=""
            )
            cursor = conexion.cursor()
            cursor.execute(f"CREATE DATABASE {nombre_bd}")
            conexion.close()
            messagebox.showinfo("Éxito", f"Base de datos '{nombre_bd}' creada.")
            ventana_crear_bd.destroy()
            mostrar_bases_datos()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error al crear la base de datos: {err}")

    tk.Button(ventana_crear_bd, text="Siguiente", command=siguiente, bg=BUTTON_COLOR, fg="white", font=FONT).pack(pady=10)

# Función para abrir el formulario de creación de tablas
def crear_tabla(nombre_bd):
    ventana_crear_tabla = tk.Toplevel(ventana)
    ventana_crear_tabla.title(f"Crear nueva tabla en '{nombre_bd}'")
    ventana_crear_tabla.configure(background=BACKGROUND_COLOR)

    tk.Label(ventana_crear_tabla, text="Nombre de la tabla:", background=BACKGROUND_COLOR, font=FONT).pack(pady=5)
    entrada_nombre_tabla = tk.Entry(ventana_crear_tabla)
    entrada_nombre_tabla.pack(pady=5)

    frame_campos = tk.Frame(ventana_crear_tabla, background=BACKGROUND_COLOR)
    frame_campos.pack(pady=10)

    campos = []

    def agregar_campo():
        frame_campo = tk.Frame(frame_campos, background=BACKGROUND_COLOR)
        frame_campo.pack(pady=5)

        entrada_nombre_campo = tk.Entry(frame_campo)
        entrada_nombre_campo.pack(side=tk.LEFT, padx=5)
        entrada_tipo_campo = ttk.Combobox(frame_campo, values=["INT", "VARCHAR(255)", "TEXT", "DATE", "FLOAT", "PRIMARY KEY", "FOREIGN KEY"])
        entrada_tipo_campo.pack(side=tk.LEFT, padx=5)

        campos.append((entrada_nombre_campo, entrada_tipo_campo))

    def crear():
        nombre_tabla = entrada_nombre_tabla.get()
        if not nombre_tabla:
            messagebox.showerror("Error", "Debe ingresar un nombre para la tabla.")
            return

        campos_definicion = []
        for campo in campos:
            nombre_campo = campo[0].get()
            tipo_campo = campo[1].get()
            if nombre_campo and tipo_campo:
                campos_definicion.append(f"{nombre_campo} {tipo_campo}")

        if not campos_definicion:
            messagebox.showerror("Error", "Debe agregar al menos un campo a la tabla.")
            return

        try:
            conexion = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database=nombre_bd
            )
            cursor = conexion.cursor()
            cursor.execute(f"CREATE TABLE {nombre_tabla} ({', '.join(campos_definicion)})")
            conexion.commit()
            conexion.close()
            messagebox.showinfo("Éxito", f"Tabla '{nombre_tabla}' creada.")
            ventana_crear_tabla.destroy()
            mostrar_tablas(nombre_bd)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error al crear la tabla: {err}")

    tk.Button(ventana_crear_tabla, text="Agregar campo", command=agregar_campo, bg=BUTTON_COLOR, fg="white", font=FONT).pack(pady=5)
    tk.Button(ventana_crear_tabla, text="Crear", command=crear, bg=BUTTON_COLOR, fg="white", font=FONT).pack(pady=5)

# Función para actualizar las bases de datos periódicamente
def actualizar_bases_datos():
    mostrar_bases_datos()  # Actualiza la lista de bases de datos
    ventana.after(5000, actualizar_bases_datos)  # Programa la siguiente actualización en 5 segundos


# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Gestor de Bases de Datos")
ventana.configure(background=BACKGROUND_COLOR)

# Panel de bases de datos
panel_bases_datos = tk.Frame(ventana, background=BACKGROUND_COLOR)
panel_bases_datos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

# Panel de contenido
panel_contenido = tk.Frame(ventana, background=BACKGROUND_COLOR)
panel_contenido.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

# Label de base de datos seleccionada
label_bd = tk.Label(panel_contenido, text="Base de Datos: Ninguna", background=BACKGROUND_COLOR, font=FONT)
label_bd.pack(pady=10)

# Botón para crear base de datos
boton_crear_bd = tk.Button(ventana, text="Crear Base de Datos", command=crear_base_datos, bg=BUTTON_COLOR, fg="white", font=FONT)
boton_crear_bd.pack(pady=10)

# Mostrar bases de datos
mostrar_bases_datos()

# Iniciar la aplicación
ventana.mainloop()
