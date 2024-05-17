from tkinter import ttk
from tkinter import filedialog

from tkinter import *
import os
from PIL import Image
import base64
import sqlite3

def center_window(window):
    window.update_idletasks()

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - window.winfo_width()) // 2
    y = round(((screen_height - window.winfo_height()) // 2) / 1.5)

    window.geometry(f"+{x}+{y}")

def image_to_base64(image_path):
    global image
    with open(image_path, "rb") as img_file:
        img_data = img_file.read()
        base64_str = base64.b64encode(img_data)
        image = base64_str.decode('utf-8')

def select_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        image_to_base64(file_path)

def connection():
    database_name = "database.db"
    try:
        # Connect to the database or create it if it doesn't exist
        conn = sqlite3.connect(database_name)
        c = conn.cursor()

        # Create the table if it doesn't exist
        c.execute('''CREATE TABLE IF NOT EXISTS Planets (
                        Nom TEXT,
                        Type TEXT,
                        Distance DOUBLE,
                        Temperature DOUBLE,
                        Atmosphere TEXT,
                        Satellites TEXT,
                        Image TEXT
                    )''')

        conn.commit()
        return conn
    except sqlite3.Error as e:
        print("Error connecting to the database:", e)
        return None
    
def SQLRequest(query, params=None):
    conn = connection()
    if conn is not None:
        try:
            c = conn.cursor()
            if params:
                c.execute(query, params)
            else:
                c.execute(query)
            if query.strip().upper().startswith('SELECT'):
                result = c.fetchall()
                return result
            else:
                conn.commit()
                return None
        except sqlite3.Error as e:
            print("Error executing SQL query:", e)
            return None
        finally:
            conn.close()
    else:
        return None

def ReadDB():
    # Clear the Treeview
    for item in my_tree.get_children():
        my_tree.delete(item)
    # Fetch data from the database
    Resultat = SQLRequest("SELECT * FROM Planets")
    if Resultat:
        for record in Resultat:
            # Ensure the number of elements matches the number of columns
            if len(record) == 7:
                my_tree.insert(parent='', index='end', values=record)
            else:
                print("Incomplete record:", record)

def addToDB(Nom, Type, Distance, Temperature, Atmosphere, Satellites, Image):
    global image, window_add
    if(window_add):
        window_add.destroy()
    query = """
    INSERT INTO Planets (Nom, Type, Distance, Temperature, Atmosphere, Satellites, Image)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    params = (Nom, Type, Distance, Temperature, Atmosphere, Satellites, Image)
    SQLRequest(query, params)
    ReadDB()
    image = NONE
    if window_add:
        window_add.destroy()

def modifyToDB(Nom, Type, Distance, Temperature, Atmosphere, Satellites, Image, old_Nom, old_Type, old_Distance, old_Temperature, old_Atmosphere, old_Satellites, old_Image):
    global image, window_modify
    if(window_modify):
        window_modify.destroy()
    query = """
    UPDATE Planets
    SET Nom = ?, Type = ?, Distance = ?, Temperature = ?, Atmosphere = ?, Satellites = ?, Image = ?
    WHERE Nom = ? AND Type = ? AND Distance = ? AND Temperature = ? AND Atmosphere = ? AND Satellites = ? AND Image = ?
    """
    params = (Nom, Type, Distance, Temperature, Atmosphere, Satellites, Image, old_Nom, old_Type, old_Distance, old_Temperature, old_Atmosphere, old_Satellites, old_Image)
    SQLRequest(query, params)
    ReadDB()
    image = NONE
    if window_modify:
        window_modify.destroy()

def deleteFromDB():
    global selected_item_list
    if not selected_item_list:
        return
    
    query = """
    DELETE FROM Planets
    WHERE Nom = ? AND Type = ? AND Distance = ? AND Temperature = ? AND Atmosphere = ? AND Satellites = ? AND Image = ?
    """
    params = tuple(selected_item_list)
    SQLRequest(query, params)
    ReadDB()
    selected_item_list.clear()

def searchFromDB(search_term):
    for item in my_tree.get_children():
        my_tree.delete(item)
    
    query = """
    SELECT Nom, Type, Distance, Temperature, Satellites
    FROM Planets 
    WHERE Nom LIKE ? OR Type LIKE ? OR Distance LIKE ? OR Temperature LIKE ? OR Satellites LIKE ?
    """
    params = (f"%{search_term}%",) * 5
    Resultat = SQLRequest(query, params)
    if Resultat:
        for record in Resultat:
            my_tree.insert(parent='', index='end', values=record)

def add_Toplevel():
    global window_add, window_modify

    if 'window_add' in globals():
        window_add.destroy()

    try:
        if window_modify:
            window_modify.destroy()
    except NameError:
        pass

    window_add = Toplevel()
    window_add.title("Ajouter une planète")
    window_add.resizable(False, False)

    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    window_add_width = 400
    window_add_height = 300
    window_add_x = root_x + root_width + 4
    window_add_y = root_y + (root_height - window_add_height) // 2

    window_add.geometry(f"{window_add_width}x{window_add_height}+{window_add_x}+{window_add_y}")

    canvas = Canvas(window_add)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)

    scrollbar = Scrollbar(window_add, orient=VERTICAL, command=canvas.yview)
    scrollbar.pack(side=RIGHT, fill=Y)

    canvas.configure(yscrollcommand=scrollbar.set)

    frame = Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor='nw')

    def update_scroll_region(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    frame.bind("<Configure>", update_scroll_region)

    def on_mouse_wheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", on_mouse_wheel)

    label_nom = Label(frame, text="Nom :")
    label_nom.grid(row=0, column=0, padx=10, pady=10, sticky='w')
    textBox_nom = Entry(frame, width=32)
    textBox_nom.grid(row=0, column=1, padx=10, pady=10)

    label_Type = Label(frame, text="Type :")
    label_Type.grid(row=1, column=0, padx=10, pady=10, sticky='w')
    textBox_Type = Entry(frame, width=32)
    textBox_Type.grid(row=1, column=1, padx=10, pady=10)

    label_Distance = Label(frame, text="Distance :")
    label_Distance.grid(row=2, column=0, padx=10, pady=10, sticky='w')
    textBox_Distance = Entry(frame, width=32)
    textBox_Distance.grid(row=2, column=1, padx=10, pady=10)

    label_Temperature = Label(frame, text="Temperature :")
    label_Temperature.grid(row=3, column=0, padx=10, pady=10, sticky='w')
    textBox_Temperature = Entry(frame, width=32)
    textBox_Temperature.grid(row=3, column=1, padx=10, pady=10)

    label_Atmosphere = Label(frame, text="Atmosphere :")
    label_Atmosphere.grid(row=4, column=0, padx=10, pady=10, sticky='w')
    textBox_Atmosphere = Entry(frame, width=32)
    textBox_Atmosphere.grid(row=4, column=1, padx=10, pady=10)

    label_Satellites = Label(frame, text="Satellites :")
    label_Satellites.grid(row=5, column=0, padx=10, pady=10, sticky='w')
    textBox_Satellites = Entry(frame, width=32)
    textBox_Satellites.grid(row=5, column=1, padx=10, pady=10)

    label_Image = Label(frame, text="Image :")
    label_Image.grid(row=6, column=0, padx=10, pady=10, sticky='w')
    button_Image = Button(frame, text="Choisir une image", command=select_image)
    button_Image.grid(row=6, column=1, padx=10, pady=10, sticky='w')

    button_cancel = Button(frame, text="Annuler", command=window_add.destroy)
    button_cancel.grid(row=7, column=0, padx=10, pady=10, sticky='e')
    button_add = Button(frame, text="Ajouter", command=lambda: addToDB(textBox_nom.get(), textBox_Type.get(), textBox_Distance.get(), textBox_Temperature.get(), textBox_Atmosphere.get(), textBox_Satellites.get(), image))
    button_add.grid(row=7, column=1, padx=10, pady=10, sticky='w')
    update_scroll_region(None)

def check_modify_Toplevel():
    global selected_item_list
    try:
        if selected_item_list:
            modify_Toplevel()
    except NameError:
        print("aucun item selectionner")

def modify_Toplevel():
    global selected_item_list, window_modify, window_add

    if 'window_modify' in globals():
        window_modify.destroy()
    try:
        if window_add:
            window_add.destroy()
    except NameError:
        pass
    
    old_image = selected_item_list[6]

    window_modify = Toplevel()
    window_modify.title("Modifier une planète")
    window_modify.resizable(False, False)

    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    window_modify_width = 400
    window_modify_height = 300
    window_modify_x = root_x + root_width + 4
    window_modify_y = root_y + (root_height - window_modify_height) // 2

    window_modify.geometry(f"{window_modify_width}x{window_modify_height}+{window_modify_x}+{window_modify_y}")

    canvas = Canvas(window_modify)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)

    scrollbar = Scrollbar(window_modify, orient=VERTICAL, command=canvas.yview)
    scrollbar.pack(side=RIGHT, fill=Y)

    canvas.configure(yscrollcommand=scrollbar.set)

    frame = Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor='nw')

    def update_scroll_region(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    frame.bind("<Configure>", update_scroll_region)

    def on_mouse_wheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", on_mouse_wheel)

    label_nom = Label(frame, text="Nom :")
    label_nom.grid(row=0, column=0, padx=10, pady=10, sticky='w')
    textBox_nom = Entry(frame, width=32)
    textBox_nom.insert(0, selected_item_list[0])
    textBox_nom.grid(row=0, column=1, padx=10, pady=10)

    label_Type = Label(frame, text="Type :")
    label_Type.grid(row=1, column=0, padx=10, pady=10, sticky='w')
    textBox_Type = Entry(frame, width=32)
    textBox_Type.insert(0, selected_item_list[1])
    textBox_Type.grid(row=1, column=1, padx=10, pady=10)

    label_Distance = Label(frame, text="Distance :")
    label_Distance.grid(row=2, column=0, padx=10, pady=10, sticky='w')
    textBox_Distance = Entry(frame, width=32)
    textBox_Distance.insert(0, selected_item_list[2])
    textBox_Distance.grid(row=2, column=1, padx=10, pady=10)

    label_Temperature = Label(frame, text="Temperature :")
    label_Temperature.grid(row=3, column=0, padx=10, pady=10, sticky='w')
    textBox_Temperature = Entry(frame, width=32)
    textBox_Temperature.insert(0, selected_item_list[3])
    textBox_Temperature.grid(row=3, column=1, padx=10, pady=10)

    label_Atmosphere = Label(frame, text="Atmosphere :")
    label_Atmosphere.grid(row=4, column=0, padx=10, pady=10, sticky='w')
    textBox_Atmosphere = Entry(frame, width=32)
    textBox_Atmosphere.insert(0, selected_item_list[4])
    textBox_Atmosphere.grid(row=4, column=1, padx=10, pady=10)

    label_Satellites = Label(frame, text="Satellites :")
    label_Satellites.grid(row=5, column=0, padx=10, pady=10, sticky='w')
    textBox_Satellites = Entry(frame, width=32)
    textBox_Satellites.insert(0, selected_item_list[5])
    textBox_Satellites.grid(row=5, column=1, padx=10, pady=10)

    label_Image = Label(frame, text="Image :")
    label_Image.grid(row=6, column=0, padx=10, pady=10, sticky='w')
    button_Image = Button(frame, text="Choisir une image", command=select_image)
    button_Image.grid(row=6, column=1, padx=10, pady=10, sticky='w')

    button_cancel = Button(frame, text="Annuler", command=window_modify.destroy)
    button_cancel.grid(row=7, column=0, padx=10, pady=10, sticky='e')
    button_add = Button(frame, text="Sauvegarder", command=lambda: modifyToDB(textBox_nom.get(), textBox_Type.get(), textBox_Distance.get(), textBox_Temperature.get(), textBox_Atmosphere.get(), textBox_Satellites.get(), image, selected_item_list[0], selected_item_list[1], selected_item_list[2], selected_item_list[3], selected_item_list[4], selected_item_list[5], old_image))
    button_add.grid(row=7, column=1, padx=10, pady=10, sticky='w')
    update_scroll_region(None)


root = Tk()
root.resizable(False, False)
# Créer un frame pour le treeview
tree_frame = Frame(root)
tree_frame.pack(pady=10, padx=10)
# Créer une barre de défilement
tree_scroll = Scrollbar(tree_frame)
tree_scroll.pack(side=RIGHT, fill=Y)
# Créer le widget Treeview
my_tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set,
selectmode="extended")
my_tree.pack()
# Configurer la barre de défilement
tree_scroll.config(command=my_tree.yview)
# Definir les Colonnes
my_tree['columns'] = ("Nom"
                      #, "Type", "Distance", "Temperature", "Atmosphere", "Satellites"
                      )
# Formater les colonnes
my_tree.column("#0", width=0, stretch=NO) #Cacher la première colonne
my_tree.column("Nom", anchor=W, width=350)
#my_tree.column("Type", anchor=CENTER, width=100)
#my_tree.column("Distance", anchor=CENTER, width=260)
#my_tree.column("Temperature", anchor=CENTER, width=200)
#my_tree.column("Atmosphere", anchor=CENTER, width=230)
#my_tree.column("Satellites", anchor=CENTER, width=110)
# Créer l'entête
my_tree.heading("#0", text="", anchor=W) #Cacher la première colonne
my_tree.heading("Nom", text="Nom", anchor=W)
#my_tree.heading("Type", text="Type", anchor=CENTER)
#my_tree.heading("Distance", text="Distance moyenne du Soleil en millions de km", anchor=CENTER)
#my_tree.heading("Temperature", text="Température moyenne en Celcius", anchor=CENTER)
#my_tree.heading("Atmosphere", text="Composante principale de l'atmosphère", anchor=CENTER)
#my_tree.heading("Satellites", text="Satellites naturels", anchor=CENTER)

def item_selected(event):
    global selected_item_list

    try:
        if window_display:
            window_display.destroy()
    except NameError:
        print("aucun window existant")

    try:
        if my_tree.selection():
            for selected_item in my_tree.selection():
                selected_item_list = my_tree.item(selected_item)['values']
            display_selected_item(selected_item_list)
        else:
            pass
    except NameError:
        pass


def display_selected_item(selected_item_list):
    global window_display
    window_display = Toplevel()
    window_display.title(f"Planète {selected_item_list[0]}")
    window_display.resizable(False, False)
    
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    window_display_width = 400
    window_display_height = 300
    window_display_x = root_x - root_width - 15
    window_display_y = root_y + (root_height - window_display_height) // 2

    window_display.geometry(f"{window_display_width}x{window_display_height}+{window_display_x}+{window_display_y}")

    canvas = Canvas(window_display)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)

    scrollbar = Scrollbar(window_display, orient=VERTICAL, command=canvas.yview)
    scrollbar.pack(side=RIGHT, fill=Y)

    canvas.configure(yscrollcommand=scrollbar.set)

    frame = Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor='nw')

    def update_scroll_region(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    frame.bind("<Configure>", update_scroll_region)

    def on_mouse_wheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", on_mouse_wheel)

    image1 = PhotoImage(data=selected_item_list[6])
    img_label = Label(frame, image=image1)
    img_label.image = image1
    img_label.pack(pady=10, padx=80)

    label_nom = Label(frame, text=f"Nom : {selected_item_list[0]}")
    label_nom.pack(pady=2)
    label_type = Label(frame, text=f"Type : {selected_item_list[1]}")
    label_type.pack(pady=2)
    label_distance = Label(frame, text=f"Distance moyenne du Soleil en M de km : {selected_item_list[2]}")
    label_distance.pack(pady=2)
    label_temperature = Label(frame, text=f"Température moyenne en Celcius : {selected_item_list[3]}")
    label_temperature.pack(pady=2)
    label_atmosphere = Label(frame, text=f"Composante principale de l'atmosphère : {selected_item_list[4]}")
    label_atmosphere.pack(pady=2)
    label_satellites = Label(frame, text=f"Satellites naturels : {selected_item_list[5]}")
    label_satellites.pack(pady=2)

    update_scroll_region(None)


# attacher un évènement à une action (clic = sélection)
my_tree.bind("<ButtonRelease-1>", item_selected)
# Créer un frame pour les boutons
buttons_frame = Frame(root)
center_window(root)
buttons_frame.pack(padx=10, pady=10)
# Créer les boutons
button_add = Button(buttons_frame, text="Add", command=add_Toplevel)
button_add.grid(row=0, column=0)
button_modify = Button(buttons_frame, text="Modify", command=check_modify_Toplevel)
button_modify.grid(row=0, column=1)
button_delete = Button(buttons_frame, text="Delete", command=deleteFromDB)
button_delete.grid(row=0, column=2)
textBox_search = Entry(buttons_frame, width=32)
textBox_search.bind("<KeyRelease>", lambda event: searchFromDB(textBox_search.get()))
textBox_search.grid(row=0, column=3)


ReadDB()

root.grid_propagate(0)

root.mainloop()