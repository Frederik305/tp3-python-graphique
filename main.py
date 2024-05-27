from tkinter import ttk
from tkinter import filedialog
from tkinter import *
import base64
import sqlite3
from tkinter import messagebox
from ttkbootstrap import Style

def messagebox_confirmation(message):
    # Fonction pour afficher une boîte de message de confirmation avec le message spécifié
    confirmation = messagebox.askyesno("Confirmation", message)
    return confirmation

def center_window(window):
    # Fonction pour centrer la fenêtre sur l'écran
    window.update_idletasks()

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calcul des coordonnées pour centrer la fenêtre
    x = (screen_width - window.winfo_width()) // 2
    y = round(((screen_height - window.winfo_height()) // 2) / 1.5)

    window.geometry(f"+{x}+{y}")

def image_to_base64(image_path):
    # Fonction pour convertir une image en format base64
    global image
    with open(image_path, "rb") as img_file:
        img_data = img_file.read()
        base64_str = base64.b64encode(img_data)
        image = base64_str.decode('utf-8')
    # Activer les boutons après avoir chargé l'image
    button_add.config(state=NORMAL)
    button_save.config(state=NORMAL)

def select_image():
    # Fonction pour sélectionner une image à partir d'un navigateur de fichiers
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        image_to_base64(file_path)

def connection():
    # Fonction pour établir une connexion à la base de données SQLite
    database_name = "database.db"
    try:
        conn = sqlite3.connect(database_name)
        c = conn.cursor()
        # Créer une table pour stocker les informations sur les planètes si elle n'existe pas déjà
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
    # Fonction pour exécuter une requête SQL sur la base de données
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
                # Si la requête n'est pas une sélection, alors on commit les changements
                conn.commit()
                return None
        except sqlite3.Error as e:
            print("Error executing SQL query:", e)
            return None
        finally:
            # Fermer la connexion après exécution de la requête
            conn.close()
    else:
        return None

def ReadDB():
    # Fonction pour lire les données depuis la base de données et les afficher dans le Treeview
    # Effacer le Treeview
    for item in my_tree.get_children():
        my_tree.delete(item)
    # Récupérer les données depuis la base de données
    Resultat = SQLRequest("SELECT * FROM Planets")
    if Resultat:
        for record in Resultat:
            # S'assurer que le nombre d'éléments correspond au nombre de colonnes
            if len(record) == 7:
                my_tree.insert(parent='', index='end', values=record)
            else:
                print("Incomplete record:", record)

def addToDB(Nom, Type, Distance, Temperature, Atmosphere, Satellites, Image):
    global image, window_add
    if image is None:
        # Afficher un avertissement si aucune image n'a été sélectionnée
        messagebox.showwarning("Warning", "SVP choisire une image avant d'ajouter.")
        return
    if window_add:
        window_add.destroy()
    # Requête pour ajouter un enregistrement à la base de données
    query = """
    INSERT INTO Planets (Nom, Type, Distance, Temperature, Atmosphere, Satellites, Image)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    params = (Nom, Type, Distance, Temperature, Atmosphere, Satellites, Image)
    SQLRequest(query, params)
    # Rafraîchir le contenu du Treeview
    ReadDB()
    image = None

def modifyToDB(Nom, Type, Distance, Temperature, Atmosphere, Satellites, Image, old_Nom, old_Type, old_Distance, old_Temperature, old_Atmosphere, old_Satellites, old_Image):
    global image, window_modify
    if image is None:
        # Afficher un avertissement si aucune image n'a été sélectionnée
        messagebox.showwarning("Warning", "Please select an image before saving.")
        return
    if window_modify:
        window_modify.destroy()
    # Requête pour modifier un enregistrement dans la base de données
    query = """
    UPDATE Planets
    SET Nom = ?, Type = ?, Distance = ?, Temperature = ?, Atmosphere = ?, Satellites = ?, Image = ?
    WHERE Nom = ? AND Type = ? AND Distance = ? AND Temperature = ? AND Atmosphere = ? AND Satellites = ? AND Image = ?
    """
    params = (Nom, Type, Distance, Temperature, Atmosphere, Satellites, Image, old_Nom, old_Type, old_Distance, old_Temperature, old_Atmosphere, old_Satellites, old_Image)
    SQLRequest(query, params)
    # Rafraîchir le contenu du Treeview
    ReadDB()
    image = None
    my_tree.config(selectmode='extended')


def deleteFromDB():
    # Fonction pour supprimer un enregistrement de la base de données
    confirmation = messagebox_confirmation("Are you sure you want to delete?")
    if confirmation:
        global selected_item_list
        if not selected_item_list:
            return

        # Requête pour supprimer l'enregistrement sélectionné de la base de données
        query = """
        DELETE FROM Planets
        WHERE Nom = ? AND Type = ? AND Distance = ? AND Temperature = ? AND Atmosphere = ? AND Satellites = ? AND Image = ?
        """
        params = tuple(selected_item_list)
        SQLRequest(query, params)
        # Rafraîchir le contenu du Treeview
        ReadDB()
        selected_item_list.clear()
    else:
        return

def searchFromDB(search_term):
    # Fonction pour rechercher des enregistrements correspondant à un terme de recherche dans la base de données
    for item in my_tree.get_children():
        my_tree.delete(item)
    
    # Requête de recherche dans la base de données
    query = """
    SELECT Nom, Type, Distance, Temperature, Atmosphere, Satellites, Image
    FROM Planets 
    WHERE Nom LIKE ? OR Type LIKE ? OR Distance LIKE ? OR Temperature LIKE ? OR Atmosphere LIKE ? OR Satellites LIKE ?
    """
    params = (f"%{search_term}%",) * 6
    Resultat = SQLRequest(query, params)
    if Resultat:
        for record in Resultat:
            my_tree.insert(parent='', index='end', values=record)

def add_Toplevel():
    # Fonction pour afficher une fenêtre pour ajouter un enregistrement à la base de données
    global window_add, window_modify, button_add

    # Fermer la fenêtre d'ajout si elle est déjà ouverte
    if 'window_add' in globals():
        window_add.destroy()

    # Fermer la fenêtre de modification si elle est ouverte
    try:
        if window_modify:
            window_modify.destroy()
    except NameError:
        pass

    # Créer une nouvelle fenêtre pour ajouter un enregistrement
    window_add = Toplevel()
    window_add.title("Ajouter une planète")
    window_add.resizable(False, False)

    # Positionner la fenêtre d'ajout à côté de la fenêtre principale
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    window_add_width = 400
    window_add_height = 300
    window_add_x = root_x + root_width + 2
    window_add_y = root_y + (root_height - window_add_height) // 2
    window_add.geometry(f"{window_add_width}x{window_add_height}+{window_add_x}+{window_add_y}")

    # Créer un canvas et un scrollbar pour la fenêtre d'ajout
    canvas = Canvas(window_add)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar = ttk.Scrollbar(window_add, orient=VERTICAL, command=canvas.yview, style="Vertical.TScrollbar")
    scrollbar.pack(side=RIGHT, fill=Y)
    canvas.configure(yscrollcommand=scrollbar.set)
    frame = Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor='nw')

    # Mettre à jour la région de défilement du canvas
    def update_scroll_region(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    frame.bind("<Configure>", update_scroll_region)

    # Activer le défilement avec la molette de la souris
    def on_mouse_wheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", on_mouse_wheel)

    # Ajouter des étiquettes et des champs de saisie pour les données de la planète
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

    # Ajouter des boutons pour annuler et ajouter la planète
    button_cancel = Button(frame, text="Annuler", command=window_add.destroy)
    button_cancel.grid(row=7, column=0, padx=10, pady=10, sticky='e')
    button_add = Button(frame, text="Ajouter", state=DISABLED, command=lambda: addToDB(textBox_nom.get(), textBox_Type.get(), textBox_Distance.get(), textBox_Temperature.get(), textBox_Atmosphere.get(), textBox_Satellites.get(), image))
    button_add.grid(row=7, column=1, padx=10, pady=10, sticky='w')
    update_scroll_region(None)


def check_modify_Toplevel():
    # Fonction pour vérifier si un élément est sélectionné pour modification
    global selected_item_list
    try:
        # Vérifier si un élément est sélectionné
        if selected_item_list:
            # Appeler la fonction de modification si un élément est sélectionné
            modify_Toplevel()
    except NameError:
        # Afficher un message si aucune sélection n'est trouvée
        print("Aucune sélection n'est trouvée")

def modify_Toplevel():
    # Fonction pour afficher une fenêtre pour modifier un enregistrement de la base de données
    global selected_item_list, window_modify, window_add, button_save

    # Fermer la fenêtre de modification si elle est déjà ouverte
    if 'window_modify' in globals():
        window_modify.destroy()
    try:
        # Fermer la fenêtre d'ajout si elle est ouverte
        if window_add:
            window_add.destroy()
    except NameError:
        pass

    # Créer une nouvelle fenêtre pour la modification
    window_modify = Toplevel()
    window_modify.title("Modifier une planète")
    window_modify.resizable(False, False)

    # Positionner la fenêtre de modification à côté de la fenêtre principale
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    window_modify_width = 400
    window_modify_height = 300
    window_modify_x = root_x + root_width + 2
    window_modify_y = root_y + (root_height - window_modify_height) // 2
    window_modify.geometry(f"{window_modify_width}x{window_modify_height}+{window_modify_x}+{window_modify_y}")

    # Créer un canvas et un scrollbar pour la fenêtre de modification
    canvas = Canvas(window_modify)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar = ttk.Scrollbar(window_modify, orient=VERTICAL, command=canvas.yview, style="Vertical.TScrollbar")
    scrollbar.pack(side=RIGHT, fill=Y)
    canvas.configure(yscrollcommand=scrollbar.set)
    frame = Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor='nw')

    # Mettre à jour la région de défilement du canvas
    def update_scroll_region(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    frame.bind("<Configure>", update_scroll_region)

    # Activer le défilement avec la molette de la souris
    def on_mouse_wheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", on_mouse_wheel)

    # Ajouter des étiquettes et des champs de saisie pour les données de la planète à modifier
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

    # Ajouter des boutons pour annuler et sauvegarder les modifications
    button_cancel = Button(frame, text="Annuler", command=window_modify.destroy)
    button_cancel.grid(row=7, column=0, padx=10, pady=10, sticky='e')
    button_save = Button(frame, text="Sauvegarder", state=DISABLED, command=lambda: modifyToDB(textBox_nom.get(), textBox_Type.get(), textBox_Distance.get(), textBox_Temperature.get(), textBox_Atmosphere.get(), textBox_Satellites.get(), image, selected_item_list[0], selected_item_list[1], selected_item_list[2], selected_item_list[3], selected_item_list[4], selected_item_list[5], selected_item_list[6]))
    button_save.grid(row=7, column=1, padx=10, pady=10, sticky='w')

    textBox_nom.insert(0, selected_item_list[0])
    textBox_Type.insert(0, selected_item_list[1])
    textBox_Distance.insert(0, selected_item_list[2])
    textBox_Temperature.insert(0, selected_item_list[3])
    textBox_Atmosphere.insert(0, selected_item_list[4])
    textBox_Satellites.insert(0, selected_item_list[5])
    update_scroll_region(None)

# Création de la fenêtre principale de l'application
root = Tk()
root.iconbitmap("application.ico")
root.resizable(False, False)
root.title("Planetes")
# Application du thème "darkly" à l'ensemble de l'interface graphique
style = Style("darkly")
style.master = root
# Créer un frame pour le treeview
tree_frame = Frame(root)
tree_frame.pack(pady=10, padx=10)
# Créer une barre de défilement
tree_scroll = ttk.Scrollbar(tree_frame)
tree_scroll.pack(side=RIGHT, fill=Y)
# Créer le widget Treeview
my_tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, selectmode="extended")
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
# Créer l'entête
my_tree.heading("#0", text="", anchor=W) #Cacher la première colonne
my_tree.heading("Nom", text="Nom", anchor=W)

def item_selected(event):
    # Fonction appelée lorsqu'un élément est sélectionné dans le Treeview
    global selected_item_list

    # Fermer la fenêtre de modification si elle est ouverte
    try:
        if window_modify.winfo_exists():
            window_modify.destroy()
    except NameError:
        pass
    
    # Fermer la fenêtre d'affichage si elle est ouverte
    try:
        if window_display:
            window_display.destroy()
    except NameError:
        print("No existing window")

    try:
        # Récupérer les valeurs de l'élément sélectionné dans le Treeview
        if my_tree.selection():
            for selected_item in my_tree.selection():
                selected_item_list = my_tree.item(selected_item)['values']
            # Afficher les détails de l'élément sélectionné
            display_selected_item(selected_item_list)
        else:
            pass
    except NameError:
        pass

def display_selected_item(selected_item_list):
    # Fonction pour afficher les détails de l'élément sélectionné
    global window_display
    window_display = Toplevel()

    # Configuration de la fenêtre d'affichage des détails de l'élément sélectionné
    window_display.title(f"Planète {selected_item_list[0]}")
    window_display.resizable(False, False)
    
    # Positionnement de la fenêtre d'affichage à côté de la fenêtre principale
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    window_display_width = 400
    window_display_height = 300
    window_display_x = root_x - root_width - 15
    window_display_y = root_y + (root_height - window_display_height) // 2
    window_display.geometry(f"{window_display_width}x{window_display_height}+{window_display_x}+{window_display_y}")

    # Création d'un canvas pour la fenêtre d'affichage
    canvas = Canvas(window_display)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)

    # Ajout d'une scrollbar pour le canvas
    scrollbar = ttk.Scrollbar(window_display, orient=VERTICAL, command=canvas.yview, style="Vertical.TScrollbar")
    scrollbar.pack(side=RIGHT, fill=Y)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Création d'un frame pour le canvas
    frame = Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor='nw')

    # Fonction pour mettre à jour la région de défilement du canvas
    def update_scroll_region(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    frame.bind("<Configure>", update_scroll_region)

    # Fonction pour permettre le défilement avec la molette de la souris
    def on_mouse_wheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", on_mouse_wheel)

    # Affichage de l'image de la planète
    image1 = PhotoImage(data=selected_item_list[6])
    img_label = Label(frame, image=image1)
    img_label.image = image1
    img_label.pack(pady=10, padx=80)

    # Affichage des détails de la planète
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

    # Mettre à jour la région de défilement du canvas
    update_scroll_region(None)


# Attacher un évènement à une action (clic = sélection) sur le Treeview
my_tree.bind("<ButtonRelease-1>", item_selected)

# Créer un frame pour les boutons
buttons_frame = Frame(root)
# Centrer la fenêtre principale
center_window(root)
buttons_frame.pack(padx=10, pady=10)

# Créer les boutons
button_add = Button(buttons_frame, text="Ajouter", command=add_Toplevel)
button_add.grid(row=0, column=0)

button_modify = Button(buttons_frame, text="Modifier", command=check_modify_Toplevel)
button_modify.grid(row=0, column=1)

button_delete = Button(buttons_frame, text="Supprimer", command=deleteFromDB)
button_delete.grid(row=0, column=2)

# Créer un label pour la zone de recherche
label_search = Label(buttons_frame, text="Rechercher : ", padx=10)
label_search.grid(row=0, column=3)

# Créer une zone de texte pour la recherche
textBox_search = Entry(buttons_frame, width=16)
# Associer un évènement à la recherche à chaque fois que le texte change
textBox_search.bind("<KeyRelease>", lambda event: searchFromDB(textBox_search.get()))
textBox_search.grid(row=0, column=4)


# Lire les données de la base de données et afficher dans le Treeview
ReadDB()

# Empêcher la fenêtre principale de changer de taille en fonction de son contenu
root.grid_propagate(0)

# Lancer la boucle principale de l'application
root.mainloop()