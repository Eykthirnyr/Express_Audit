import subprocess
import sys
from tkinter import filedialog
from PIL import Image

# Fonction pour installer les dépendances manquantes
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Vérification des dépendances nécessaires
required_packages = ["tkinter", "matplotlib", "numpy", "datetime", "Pillow"]

for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        print(f"Installation du package manquant : {package}")
        install(package)

# Importation des modules
import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

# Configuration de la fenêtre principale
root = tk.Tk()
root.title("Audit Express d'Infrastructure")
root.geometry("1400x800")  # Augmenter la taille de la fenêtre pour plus d'espace

# Initialisation de la variable de chemin du logo après la création de la fenêtre principale
logo_path_var = tk.StringVar()

# Fonction pour ouvrir la boîte de dialogue et sélectionner un logo
def select_logo():
    file_path = filedialog.askopenfilename(
        title="Sélectionner un Logo",
        filetypes=[("Fichiers image", "*.jpg *.jpeg *.png *.gif")]
    )
    logo_path_var.set(file_path)

# Fonction pour calculer les scores pour chaque catégorie et le score global
def calculate_scores():
    global_score = 0
    total_possible_score = 0
    categories_scores = []
    
    for category, vars in score_vars.items():
        category_score = 0
        category_possible_score = 0
        na_count = 0
        
        for question, (var, na_var) in vars.items():
            if na_var.get():  # Si N/A est sélectionné
                na_count += 1
            else:
                category_score += var.get()
                category_possible_score += 5  # Score maximum pour chaque question est 5

        # Si toutes les lignes sont N/A, attribuer le score maximum à cette catégorie
        if na_count == len(vars):
            categories_scores.append(5)  # Score maximum
        else:
            # Calculer le score de la catégorie
            if category_possible_score > 0:
                categories_scores.append(category_score / category_possible_score * 5)
            else:
                categories_scores.append(0)

        global_score += category_score
        total_possible_score += category_possible_score

    # Calculer le score global basé sur le score total possible
    if total_possible_score > 0:
        global_score = (global_score / total_possible_score) * 100
    else:
        global_score = 0
    
    update_radar_chart(categories_scores)
    global_score_label.config(text=f"Score global : {global_score:.2f}/100")

# Fonction pour mettre à jour le graphique radar
def update_radar_chart(scores):
    angles = np.linspace(0, 2 * np.pi, len(scores), endpoint=False).tolist()
    scores += scores[:1]
    angles += angles[:1]
    
    radar_ax.clear()

    # Colorer les cercles concentriques avec les couleurs correspondant aux risques
    for i in range(1, 6):
        radar_ax.fill_between(angles, i, i-1, color=risk_colors[i], alpha=0.1)

    radar_ax.plot(angles, scores, color='b', linewidth=2)
    radar_ax.fill(angles, scores, color='b', alpha=0.25)
    
    radar_ax.set_yticks([1, 2, 3, 4, 5])
    radar_ax.set_yticklabels([])
    radar_ax.set_xticks(angles[:-1])
    radar_ax.set_xticklabels(['       Serveur', 'Systèmes Clients', 'Sauvegarde              ', 'Réseau'], fontsize=10, ha='center', va='center')

    # Mettre à jour la légende
    radar_ax.legend(handles=legend_handles, loc='lower center', bbox_to_anchor=(0.5, -0.15), ncol=5)

    radar_canvas.draw()

# Fonction pour exporter les données et le graphique dans un PDF
def export_to_pdf():
    client_name = client_name_var.get()
    auditor_name = auditor_name_var.get()
    current_date = datetime.now().strftime("%Y-%m-%d")
    logo_path = logo_path_var.get()

    with PdfPages('rapport_audit.pdf') as pdf:
        # Première page pour le titre et les informations de base
        fig_title = Figure(figsize=(8.27, 11.69), dpi=100)  # Taille A4 en pouces (8.27x11.69)
        title_ax = fig_title.add_subplot(111)
        title_ax.axis('off')

        # Bloc de titre en haut de la page avec les informations de l'entreprise
        title_text = (
            f"Rapport d'Audit\n"
            f"Client : {client_name}\n"
            f"Auditeur : {auditor_name}\n"
            f"Date : {current_date}\n\n"
            f"Nom de l'entreprise : XXXXXXXXXX | Sécurité Réseau Système\n"
            f"Adresse : XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n"
            f"Téléphone : XX XX XX XX XX\n"
            f"Emails : support@XXXXXXX.fr, contact@XXXXXXX.fr"
        )

        # Ajouter le titre principal et les informations d'en-tête
        title_ax.text(0.5, 0.8, title_text, ha='center', va='top', fontsize=14, weight='bold', wrap=True)

        # Ajouter le logo, le redimensionner pour qu'il s'adapte sous le texte principal
        if logo_path:
            logo = Image.open(logo_path)
            # Conserver les proportions et limiter la taille à 500x500
            logo.thumbnail((500, 500), Image.Resampling.LANCZOS)
            
            # Convertir l'image PIL en tableau NumPy pour l'afficher
            logo_np = np.array(logo)
            ax_img = fig_title.add_axes([0.35, 0.1, 0.3, 0.3])  # Position et taille pour centrage
            ax_img.imshow(logo_np)
            ax_img.axis('off')

        # Enregistrer la page de titre dans le PDF
        pdf.savefig(fig_title)
        plt.close(fig_title)

        # Deuxième page pour le graphique radar (avec couleur de fond et légende)
        fig_pdf = Figure(figsize=(8.27, 11.69), dpi=100, facecolor='lightblue')  # Ajouter couleur de fond
        radar_ax_pdf = fig_pdf.add_subplot(111, polar=True)

        # Obtenir les scores pour le graphique radar
        scores = [score_vars[cat][list(vars.keys())[0]][0].get() for cat, vars in score_vars.items()]
        angles = np.linspace(0, 2 * np.pi, len(scores), endpoint=False).tolist()
        scores += scores[:1]
        angles += angles[:1]

        # Reproduire le graphique radar
        for i in range(1, 6):
            radar_ax_pdf.fill_between(angles, i, i-1, color=risk_colors[i], alpha=0.1)  # Colorer les cercles concentriques

        radar_ax_pdf.plot(angles, scores, color='b', linewidth=2)
        radar_ax_pdf.fill(angles, scores, color='b', alpha=0.25)
        radar_ax_pdf.set_yticks([1, 2, 3, 4, 5])
        radar_ax_pdf.set_yticklabels([])
        radar_ax_pdf.set_xticks(angles[:-1])
        radar_ax_pdf.set_xticklabels(['       Serveur', 'Systèmes Clients', 'Sauvegarde              ', 'Réseau'], fontsize=10, ha='center', va='center')

        # Ajouter la même légende sous le graphique radar comme dans l'UI
        radar_ax_pdf.legend(handles=legend_handles, loc='lower center', bbox_to_anchor=(0.5, -0.15), ncol=5)

        # Enregistrer la page du graphique radar dans le PDF
        pdf.savefig(fig_pdf)
        plt.close(fig_pdf)

        # Troisième page pour les données textuelles (réponses avec scores seulement)
        fig_text = Figure(figsize=(8.27, 11.69), dpi=100)
        ax_text = fig_text.add_subplot(111)
        ax_text.axis('off')

        # Format du bloc de texte avec structure
        text = f"Client : {client_name}\nAuditeur : {auditor_name}\nDate : {current_date}\n\nRéponses :\n"
        for category, vars in score_vars.items():
            text += f"\n{category} :\n"
            for question, (var, na_var) in vars.items():
                text += f"  - {question} : {var.get()} (N/A : {'Oui' if na_var.get() else 'Non'})\n"

        # Ajouter le texte structuré avec une marge
        ax_text.text(0, 1, text, ha='left', va='top', fontsize=10, wrap=True)

        # Enregistrer le bloc de texte dans le PDF avec marges
        pdf.savefig(fig_text, bbox_inches='tight', pad_inches=1)
        plt.close(fig_text)

# Fonction pour basculer la sélection N/A et activer/désactiver les boutons radio
def toggle_na(var, na_var, frame, is_radio):
    if is_radio and na_var.get():
        na_var.set(0)
    elif not is_radio:
        if na_var.get():
            var.set(0)  # Réinitialiser la sélection radio
            for child in frame.winfo_children():
                if isinstance(child, ttk.Radiobutton):
                    child.config(state=tk.DISABLED)
        else:
            for child in frame.winfo_children():
                if isinstance(child, ttk.Radiobutton):
                    child.config(state=tk.NORMAL)
    calculate_scores()

# Créer les onglets
notebook = ttk.Notebook(root)
notebook.pack(expand=1, fill='both')

# Dictionnaire pour stocker les variables de score
score_vars = {
    'Serveur': {},
    'Systèmes Clients': {},
    'Sauvegarde': {},
    'Réseau': {}
}

# Données pour chaque catégorie
categories_data = {
    'Serveur': [
        ('Système à jour', 'Assurez-vous que le système d’exploitation et les logiciels sont régulièrement mis à jour pour corriger les vulnérabilités.'),
        ('Antivirus / EDR installé et opérationnel', 'Un antivirus ou un EDR doit être installé pour protéger contre les malwares.'),
        ('Authentification forte', 'Utilisez des mots de passe forts et des méthodes d’authentification supplémentaires.'),
        ('Sécurité physique', 'Les serveurs doivent être situés dans un lieu physiquement sécurisé et protégé.'),
        ('Redondance et tolérance aux pannes', 'La redondance matérielle et logicielle réduit les temps d’arrêt en cas de panne.')
    ],
    'Systèmes Clients': [
        ('Système à jour', 'Le système d’exploitation des systèmes clients doit être à jour.'),
        ('Antivirus installé et opérationnel', 'Chaque système client doit avoir un logiciel antivirus actif.'),
        ('Authentification forte', 'Utilisez des mots de passe forts pour accéder aux systèmes clients.'),
        ('Compte/séance nominatif(ve)', 'Chaque utilisateur doit avoir un compte nominatif pour suivre l’activité.'),
        ('Chiffrement des systèmes clients', 'Les données sur les systèmes clients doivent être chiffrées.')
    ],
    'Sauvegarde': [
        ('Plan de sauvegarde détaillé et à jour', 'Un plan de sauvegarde bien défini et régulièrement mis à jour est essentiel.'),
        ('Sauvegarde régulière des données', 'Les sauvegardes doivent être effectuées régulièrement.'),
        ('Rétention des sauvegardes critiques', 'Conservez les sauvegardes critiques pendant une période suffisante.'),
        ('Stratégie de sauvegarde 3-2-1', 'Utilisez la stratégie de sauvegarde 3-2-1 pour assurer la sécurité des données.'),
        ('Mises à jour du système de sauvegarde', 'Le système de sauvegarde doit être régulièrement mis à jour.')
    ],
    'Réseau': [
        ('Segmentation du réseau', 'Segmenter le réseau limite la propagation des incidents de sécurité.'),
        ('Pare-feu installé et maintenu', 'Un pare-feu correctement configuré protège le réseau.'),
        ('Règles de pare-feu pertinentes', 'Les règles du pare-feu doivent être adaptées aux besoins en sécurité.'),
        ('Wi-Fi invité séparé du réseau interne', 'Le réseau invité doit être séparé du réseau interne.'),
        ('Sécurité du Wi-Fi', 'Le Wi-Fi doit être sécurisé avec des protocoles modernes.')
    ]
}

# Couleurs pour les niveaux de risque
risk_colors = {
    1: '#ff0000',  # Critique
    2: '#ff8000',  # Élevé
    3: '#ffff00',  # Moyen
    4: '#80ff00',  # Faible
    5: '#00ff00'   # Très Faible
}

# Créer des onglets pour chaque catégorie
for category, questions in categories_data.items():
    frame = ttk.Frame(notebook)
    notebook.add(frame, text=category)
    
    # Titre de l'onglet
    category_label = tk.Label(frame, text=category, font=("Arial", 16, 'bold'))
    category_label.pack(pady=10)

    # Tableau pour chaque question avec score
    for question, explanation in questions:
        question_frame = ttk.Frame(frame)
        question_frame.pack(fill='x', padx=10, pady=5)

        question_label = ttk.Label(question_frame, text=question)
        question_label.pack(side='left', padx=(0, 10))

        # Système de notation de 1 à 5
        var = tk.IntVar(value=5)  # Valeur par défaut 5 (Risque très faible)
        na_var = tk.IntVar(value=0)  # Variable pour l'option N/A
        score_vars[category][question] = (var, na_var)
        
        for i in range(1, 6):
            rb = ttk.Radiobutton(
                question_frame, text=str(i), variable=var, value=i,
                command=lambda v=var, na=na_var, f=question_frame: toggle_na(v, na, f, True),
                state=tk.NORMAL if not na_var.get() else tk.DISABLED
            )
            rb.pack(side='left', padx=5)

        # Option N/A
        na_checkbox = ttk.Checkbutton(
            question_frame, text="N/A", variable=na_var, 
            command=lambda v=var, na=na_var, f=question_frame: toggle_na(v, na, f, False)
        )
        na_checkbox.pack(side='left', padx=5)

        # Explication pour chaque question
        explanation_label = tk.Label(frame, text=explanation, font=("Arial", 9), fg="gray")
        explanation_label.pack(anchor='w', padx=20, pady=(0, 10))

# Onglet récapitulatif
recap_frame = ttk.Frame(notebook)
notebook.add(recap_frame, text="Récapitulatif")

# Titre du récapitulatif lié aux risques
recap_title = tk.Label(recap_frame, text="Évaluation des Risques", font=("Arial", 18, 'bold'))
recap_title.pack(pady=10)

global_score_label = ttk.Label(recap_frame, text="Score global : 0/100", font=("Arial", 16))
global_score_label.pack(pady=10)

# Créer le graphique radar
fig = Figure(figsize=(8, 6), dpi=100)  # Ajuster pour un canvas rectangulaire
radar_ax = fig.add_subplot(111, polar=True)
radar_canvas = FigureCanvasTkAgg(fig, master=recap_frame)
radar_canvas.get_tk_widget().pack(pady=20)

# Créer la légende
legend_labels = ["Critique", "Élevé", "Moyen", "Faible", "Très Faible"]
legend_handles = [radar_ax.plot([], [], color=risk_colors[i], label=legend_labels[i-1])[0] for i in range(1, 6)]

# Initialiser le graphique radar
update_radar_chart([0, 0, 0, 0])

# Onglet paramètres
parameters_frame = ttk.Frame(notebook)
notebook.add(parameters_frame, text="Paramètres")

# Variables pour les noms du client et de l'auditeur
client_name_var = tk.StringVar()
auditor_name_var = tk.StringVar()

# Champ pour le nom du client
client_label = ttk.Label(parameters_frame, text="Nom du client :")
client_label.pack(pady=(10, 0))
client_entry = ttk.Entry(parameters_frame, textvariable=client_name_var)
client_entry.pack(pady=(0, 10))

# Champ pour le nom de l'auditeur
auditor_label = ttk.Label(parameters_frame, text="Nom de l'auditeur :")
auditor_label.pack(pady=(10, 0))
auditor_entry = ttk.Entry(parameters_frame, textvariable=auditor_name_var)
auditor_entry.pack(pady=(0, 10))

# Sélection du logo
logo_button = ttk.Button(parameters_frame, text="Sélectionner un Logo", command=select_logo)
logo_button.pack(pady=(10, 10))

# Affichage de la date actuelle
date_label = ttk.Label(parameters_frame, text=f"Date : {datetime.now().strftime('%Y-%m-%d')}", font=("Arial", 12))
date_label.pack(pady=(10, 0))

# Bouton pour exporter les données et le graphique dans un PDF
export_button = ttk.Button(parameters_frame, text="Exporter en PDF", command=export_to_pdf)
export_button.pack(pady=(20, 10))

# Ajout de la nouvelle ligne dans l'onglet des paramètres en bas
credits_label = ttk.Label(parameters_frame, text="Créé par Clément GHANEME, basé sur le travail de Mathis SALVADOR", font=("Arial", 8), foreground="gray")
credits_label.pack(side='bottom', pady=(10, 0))

# Boucle principale
root.mainloop()
