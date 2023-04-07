import tkinter as tk
from tkinter import ttk
import mysql.connector
import csv

boutique = mysql.connector.connect(
    host="localhost", user="root",
    password="N1610J2803C2912s?", database="boutique")

cursor = boutique.cursor()

class Main:

    def __init__(self):

        self.root = tk.Tk()
        self.root.title("Gestion de stocks")
        self.root.geometry("800x500")
        self.root.configure(bg="#5e5e5e")

        style=ttk.Style()
        style.theme_use('clam')


        self.interface()

    def refresh(self):

        self.tree.delete(*self.tree.get_children())
        for produit in self.liste_produits():
            self.tree.insert("", "end", text=produit[0], values=(produit[1], produit[2], produit[3], produit[4], self.nom_categorie(produit[5])))


        self.category_cbox = ttk.Combobox(self.root, values=self.liste_categories())

    def filtrer_categories(self):

        self.tree.delete(*self.tree.get_children())
        self.info_label.config(text="Aucun produit ne correspond", fg="red")
        for produit in self.liste_produits():
            if self.nom_categorie(produit[5]) == self.category_cbox.get():
                self.tree.insert("", "end", text=produit[0], values=(produit[1], produit[2], produit[3], produit[4], self.nom_categorie(produit[5])))
                self.info_label.config(text="Filre appliqué", fg="green")

    def reset_filtres(self):

        self.refresh()
        self.info_label.config(text="Filtre réinitialisé", fg="white", bg="#5e5e5e", font=("Arial", 14))

    def interface(self):

        self.tree = ttk.Treeview(self.root, columns=("Nom", "Description", "Prix", "Quantite", "Categorie"))
        self.tree.heading("#0", text="ID")
        self.tree.column("#0", minwidth=0, width=30)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=145, anchor="center")

        self.refresh()

        self.tree.grid(row=0, column=0, columnspan=5, padx=20, pady=20)


        self.info_label = tk.Label(self.root, text="")
        self.info_label.grid(row=9, column=0, columnspan=5, sticky="NSEW", pady=5)


        self.btn_ajouter = tk.Button(self.root, text="Ajouter produit", command=self.ajouter_produit, bg="green", fg="white")
        self.btn_ajouter.grid(row=1, column=3, sticky="NSEW", padx=20)

        self.btn_modifier = tk.Button(self.root, text="Modifier produit", command=self.modifier_produit, bg="orange", fg="white")
        self.btn_modifier.grid(row=2, column=3, sticky="NSEW", padx=20)

        self.btn_supprimer = tk.Button(self.root, text="Supprimer produit", command=self.supprimer_produit, bg="red", fg="white")
        self.btn_supprimer.grid(row=3, column=3, sticky="NSEW", padx=20)

        self.btn_exporter = tk.Button(self.root, text="Exporter en CSV", command=self.export_csv, bg="blue", fg="white")
        self.btn_exporter.grid(row=4, column=3, sticky="NSEW", padx=20)

        self.btn_filtrer = tk.Button(self.root, text="Filtrer par catégorie", command=self.filtrer_categories, bg="blue", fg="white")
        self.btn_filtrer.grid(row=5, column=3, sticky="NSEW", padx=20)

        self.btn_reset = tk.Button(self.root, text="Réinitialiser les filtres", command=self.reset_filtres, bg="blue", fg="white")
        self.btn_reset.grid(row=6, column=3, sticky="NSEW", padx=20)


        tk.Label(self.root, text="Nom", bg="#5e5e5e", fg="white", font=11).grid(row=1, column=0)
        self.name_entry = tk.Entry(self.root)
        self.name_entry.grid(row=1, column=1, sticky="NSEW", pady=5)

        tk.Label(self.root, text="Description", bg="#5e5e5e", fg="white", font=11).grid(row=2, column=0)
        self.description_entry = tk.Entry(self.root)
        self.description_entry.grid(row=2, column=1, sticky="NSEW", pady=5)

        tk.Label(self.root, text="Prix", bg="#5e5e5e", fg="white", font=11).grid(row=3, column=0)
        self.price_entry = tk.Entry(self.root)
        self.price_entry.grid(row=3, column=1, sticky="NSEW", pady=5)

        tk.Label(self.root, text="Quantite", bg="#5e5e5e", fg="white", font=11).grid(row=4, column=0)
        self.quantity_entry = tk.Entry(self.root)
        self.quantity_entry.grid(row=4, column=1, sticky="NSEW", pady=5)

        tk.Label(self.root, text="Categorie", bg="#5e5e5e", fg="white", font=11).grid(row=5, column=0)
        self.category_cbox = ttk.Combobox(self.root, values=self.liste_categories())
        self.category_cbox.grid(row=5, column=1, sticky="NSEW", pady=5)

        self.root.mainloop()

    def check_produit(self):
        
        self.nom = self.name_entry.get()
        self.description = self.description_entry.get()
        self.prix = self.price_entry.get()
        self.quantite = self.quantity_entry.get()
        self.categorie = self.category_cbox.get()

        if self.nom == "" or self.description == "" or self.prix == "" or self.quantite == "" or self.categorie == "":
            self.info_label.config(text="Veuillez remplir tous les champs", fg="red")
            return False
        
        if not self.prix.isdigit():
            self.info_label.config(text="Le prix doit être un nombre", fg="red")
            return False
        
        if not self.quantite.isdigit():
            self.info_label.config(text="La quantité doit être un nombre", fg="red")
            return False
        
        if (self.categorie,) not in self.liste_categories():
            self.ajouter_categorie()
            self.info_label.config(text="La catégorie a été ajoutée", fg="green")
        
        return True
    
    def check_selection(self):

        if self.tree.selection() == ():
            self.info_label.config(text="Veuillez sélectionner un produit", fg="red")
            return False
        self.id = self.tree.item(self.tree.selection())["text"]
        return True            

    def ajouter_produit(self):

        if self.check_produit():

            query = "INSERT INTO produit (nom, description, prix, quantite, id_categorie) VALUES (%s, %s, %s, %s, %s)"
            values = (self.nom, self.description, self.prix, self.quantite, self.id_categorie(self.categorie))
            cursor.execute(query, values)
            boutique.commit()
            self.refresh()
            self.info_label.config(text="Le produit a été ajouté", fg="green")

    def modifier_produit(self):

        if self.check_produit():

            if self.check_selection():

                query = "UPDATE produit SET nom=%s, description=%s, prix=%s, quantite=%s, id_categorie=%s WHERE id=%s"
                values = (self.nom, self.description, self.prix, self.quantite, self.id_categorie(self.categorie), self.id)
                cursor.execute(query, values)
                boutique.commit()
                self.refresh()
                self.info_label.config(text="Le produit a été modifié", fg="green")

    def supprimer_produit(self):

        if self.check_selection():

            cursor.execute("DELETE FROM produit WHERE id=%s", (self.id,))
            boutique.commit()
            self.refresh()
            self.info_label.config(text="Le produit a été supprimé", fg="green")

    def liste_categories(self):

        cursor.execute("SELECT nom FROM categorie")
        categorie = cursor.fetchall()
        return categorie
    
    def nom_categorie(self, id):

        cursor.execute("SELECT nom FROM categorie WHERE id=%s", (id,))
        categorie = cursor.fetchone()
        return categorie[0]
    
    def id_categorie(self, nom):

        cursor.execute("SELECT id FROM categorie WHERE nom=%s", (nom,))
        categorie = cursor.fetchone()
        return categorie[0]
    
    def ajouter_categorie(self):

        cursor.execute("INSERT INTO categorie (nom) VALUES (%s)", (self.categorie,))
        boutique.commit()

    def liste_produits(self):

        query = "SELECT * FROM produit"
        cursor.execute(query)
        produits = cursor.fetchall()
        return produits
    
    def export_csv(self):

        with open("produits.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Nom", "Description", "Prix", "Quantite", "Categorie"])
            for produit in self.liste_produits():
                writer.writerow(produit)
        self.info_label.config(text="La liste des produits a été exportée", fg="white")

Main()