import subprocess
import sys
from tkinter import filedialog
from PIL import Image

# Function to install missing dependencies
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Check for necessary dependencies
required_packages = ["tkinter", "matplotlib", "numpy", "datetime", "Pillow"]

for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        print(f"Installing missing package: {package}")
        install(package)

# Now import the modules
import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

# Main window configuration
root = tk.Tk()
root.title("Infrastructure Audit Express")
root.geometry("1400x800")  # Increase window size for more space

# Initialize logo path variable after creating the root window
logo_path_var = tk.StringVar()

# Function to open file dialog for selecting logo
def select_logo():
    file_path = filedialog.askopenfilename(
        title="Select Logo",
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")]
    )
    logo_path_var.set(file_path)

# Function to calculate the scores for each category and the overall score
def calculate_scores():
    global_score = 0
    total_possible_score = 0
    categories_scores = []
    
    for category, vars in score_vars.items():
        category_score = 0
        category_possible_score = 0
        na_count = 0
        
        for question, (var, na_var) in vars.items():
            if na_var.get():  # If N/A is selected
                na_count += 1
            else:
                category_score += var.get()
                category_possible_score += 5  # Maximum possible for each question is 5

        # If all lines are N/A, give the maximum score for this category
        if na_count == len(vars):
            categories_scores.append(5)  # Maximum score
        else:
            # Calculate category score
            if category_possible_score > 0:
                categories_scores.append(category_score / category_possible_score * 5)
            else:
                categories_scores.append(0)

        global_score += category_score
        total_possible_score += category_possible_score

    # Calculate the overall score based on the total possible score
    if total_possible_score > 0:
        global_score = (global_score / total_possible_score) * 100
    else:
        global_score = 0
    
    update_radar_chart(categories_scores)
    global_score_label.config(text=f"Overall Score: {global_score:.2f}/100")

# Function to update the radar chart
def update_radar_chart(scores):
    angles = np.linspace(0, 2 * np.pi, len(scores), endpoint=False).tolist()
    scores += scores[:1]
    angles += angles[:1]
    
    radar_ax.clear()

    # Color the concentric circles with corresponding risk colors
    for i in range(1, 6):
        radar_ax.fill_between(angles, i, i-1, color=risk_colors[i], alpha=0.1)

    radar_ax.plot(angles, scores, color='b', linewidth=2)
    radar_ax.fill(angles, scores, color='b', alpha=0.25)
    
    radar_ax.set_yticks([1, 2, 3, 4, 5])
    radar_ax.set_yticklabels([])
    radar_ax.set_xticks(angles[:-1])
    radar_ax.set_xticklabels(['        Server', 'Client Systems', 'Backup             ', 'Network'], fontsize=10, ha='center', va='center')

    # Update the legend
    radar_ax.legend(handles=legend_handles, loc='lower center', bbox_to_anchor=(0.5, -0.15), ncol=5)

    radar_canvas.draw()

# Function to export data and the graph to a PDF
def export_to_pdf():
    client_name = client_name_var.get()
    auditor_name = auditor_name_var.get()
    current_date = datetime.now().strftime("%Y-%m-%d")
    logo_path = logo_path_var.get()

    with PdfPages('audit_report.pdf') as pdf:
        # First page for the title and basic information
        fig_title = Figure(figsize=(8.27, 11.69), dpi=100)  # A4 size in inches (8.27x11.69)
        title_ax = fig_title.add_subplot(111)
        title_ax.axis('off')

        # Title block at the top of the page with company information
        title_text = (
            f"Audit Report\n"
            f"Client: {client_name}\n"
            f"Auditor: {auditor_name}\n"
            f"Date: {current_date}\n\n"
            f"Company Name: XXXXXXXXXX | Network System Security\n"
            f"Address: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n"
            f"Phone: XX XX XX XX XX\n"
            f"Emails: support@XXXXXXX.fr, contact@XXXXXXX.fr"
        )

        # Add the main title and header information
        title_ax.text(0.5, 0.8, title_text, ha='center', va='top', fontsize=14, weight='bold', wrap=True)

        # Add the logo, scale it to fit below the main text
        if logo_path:
            logo = Image.open(logo_path)
            # Keep aspect ratio and limit the size to 500x500
            logo.thumbnail((500, 500), Image.Resampling.LANCZOS)
            
            # Convert the PIL image to a NumPy array so it can be plotted
            logo_np = np.array(logo)
            ax_img = fig_title.add_axes([0.35, 0.1, 0.3, 0.3])  # Position and size for centering
            ax_img.imshow(logo_np)
            ax_img.axis('off')

        # Save the title page to the PDF
        pdf.savefig(fig_title)
        plt.close(fig_title)

        # Second page for the radar chart (with background color and legend)
        fig_pdf = Figure(figsize=(8.27, 11.69), dpi=100, facecolor='lightblue')  # Add background color
        radar_ax_pdf = fig_pdf.add_subplot(111, polar=True)

        # Get the scores for the radar chart
        scores = [score_vars[cat][list(vars.keys())[0]][0].get() for cat, vars in score_vars.items()]
        angles = np.linspace(0, 2 * np.pi, len(scores), endpoint=False).tolist()
        scores += scores[:1]
        angles += angles[:1]

        # Reproduce the radar chart
        for i in range(1, 6):
            radar_ax_pdf.fill_between(angles, i, i-1, color=risk_colors[i], alpha=0.1)  # Color concentric circles

        radar_ax_pdf.plot(angles, scores, color='b', linewidth=2)
        radar_ax_pdf.fill(angles, scores, color='b', alpha=0.25)
        radar_ax_pdf.set_yticks([1, 2, 3, 4, 5])
        radar_ax_pdf.set_yticklabels([])
        radar_ax_pdf.set_xticks(angles[:-1])
        radar_ax_pdf.set_xticklabels(['        Server', 'Client Systems', 'Backup             ', 'Network'], fontsize=10, ha='center', va='center')

        # Add the same legend under the radar chart as in the GUI
        radar_ax_pdf.legend(handles=legend_handles, loc='lower center', bbox_to_anchor=(0.5, -0.15), ncol=5)

        # Save the radar chart page to the PDF
        pdf.savefig(fig_pdf)
        plt.close(fig_pdf)

        # Third page for textual data (answers with scores only)
        fig_text = Figure(figsize=(8.27, 11.69), dpi=100)
        ax_text = fig_text.add_subplot(111)
        ax_text.axis('off')

        # Format the text block with structure
        text = f"Client: {client_name}\nAuditor: {auditor_name}\nDate: {current_date}\n\nAnswers:\n"
        for category, vars in score_vars.items():
            text += f"\n{category}:\n"
            for question, (var, na_var) in vars.items():
                text += f"  - {question}: {var.get()} (N/A: {'Yes' if na_var.get() else 'No'})\n"

        # Add the structured text with a margin
        ax_text.text(0, 1, text, ha='left', va='top', fontsize=10, wrap=True)

        # Save the text block in the PDF with margins
        pdf.savefig(fig_text, bbox_inches='tight', pad_inches=1)
        plt.close(fig_text)

# Function to toggle the N/A selection and enable/disable radio buttons
def toggle_na(var, na_var, frame, is_radio):
    if is_radio and na_var.get():
        na_var.set(0)
    elif not is_radio:
        if na_var.get():
            var.set(0)  # Reset the radio selection
            for child in frame.winfo_children():
                if isinstance(child, ttk.Radiobutton):
                    child.config(state=tk.DISABLED)
        else:
            for child in frame.winfo_children():
                if isinstance(child, ttk.Radiobutton):
                    child.config(state=tk.NORMAL)
    calculate_scores()

# Create tabs
notebook = ttk.Notebook(root)
notebook.pack(expand=1, fill='both')

# Dictionary to store the score variables
score_vars = {
    'Server': {},
    'Client Systems': {},
    'Backup': {},
    'Network': {}
}

# Data for each category
categories_data = {
    'Server': [
        ('System up to date', 'Ensure the operating system and software are regularly updated to fix vulnerabilities.'),
        ('Antivirus / EDR installed and operational', 'An antivirus or EDR must be installed to protect against malware.'),
        ('Strong authentication', 'Use strong passwords and additional authentication methods.'),
        ('Physical security', 'Servers must be located in a physically secure and protected location.'),
        ('Redundancy and fault tolerance', 'Hardware and software redundancy reduces downtime in case of failure.')
    ],
    'Client Systems': [
        ('System up to date', 'The operating system of client systems must be up to date.'),
        ('Antivirus installed and operational', 'Each client system must have active antivirus software.'),
        ('Strong authentication', 'Use strong passwords to access client systems.'),
        ('Named account/session', 'Each user must have a named account to track activity.'),
        ('Client systems encryption', 'Data on client systems must be encrypted.')
    ],
    'Backup': [
        ('Detailed and up-to-date backup plan', 'A well-defined and regularly updated backup plan is essential.'),
        ('Regular data backup', 'Backups must be performed regularly.'),
        ('Critical backup retention', 'Retain critical backups for a sufficient period.'),
        ('3-2-1 backup strategy', 'Use the 3-2-1 backup strategy to ensure data security.'),
        ('Backup system updates', 'The backup system must be regularly updated.')
    ],
    'Network': [
        ('Network segmentation', 'Segmenting the network limits the spread of security incidents.'),
        ('Firewall installed and maintained', 'A properly configured firewall protects the network.'),
        ('Relevant firewall rules', 'Firewall rules must be adapted to security needs.'),
        ('Guest WIFI separated from internal network', 'The guest network must be separated from the internal network.'),
        ('Wi-Fi security', 'Wi-Fi must be secured with modern protocols.')
    ]
}

# Colors for risk levels
risk_colors = {
    1: '#ff0000',  # Critical
    2: '#ff8000',  # High
    3: '#ffff00',  # Medium
    4: '#80ff00',  # Low
    5: '#00ff00'   # Very Low
}

# Create tabs for each category
for category, questions in categories_data.items():
    frame = ttk.Frame(notebook)
    notebook.add(frame, text=category)
    
    # Tab title
    category_label = tk.Label(frame, text=category, font=("Arial", 16, 'bold'))
    category_label.pack(pady=10)

    # Table for each question with score
    for question, explanation in questions:
        question_frame = ttk.Frame(frame)
        question_frame.pack(fill='x', padx=10, pady=5)

        question_label = ttk.Label(question_frame, text=question)
        question_label.pack(side='left', padx=(0, 10))

        # Scoring system from 1 to 5
        var = tk.IntVar(value=5)  # Default value 5 (Very low risk)
        na_var = tk.IntVar(value=0)  # Variable for N/A choice
        score_vars[category][question] = (var, na_var)
        
        for i in range(1, 6):
            rb = ttk.Radiobutton(
                question_frame, text=str(i), variable=var, value=i,
                command=lambda v=var, na=na_var, f=question_frame: toggle_na(v, na, f, True),
                state=tk.NORMAL if not na_var.get() else tk.DISABLED
            )
            rb.pack(side='left', padx=5)

        # N/A option
        na_checkbox = ttk.Checkbutton(
            question_frame, text="N/A", variable=na_var, 
            command=lambda v=var, na=na_var, f=question_frame: toggle_na(v, na, f, False)
        )
        na_checkbox.pack(side='left', padx=5)

        # Explanation for each question
        explanation_label = tk.Label(frame, text=explanation, font=("Arial", 9), fg="gray")
        explanation_label.pack(anchor='w', padx=20, pady=(0, 10))

# Summary tab
recap_frame = ttk.Frame(notebook)
notebook.add(recap_frame, text="Summary")

# Summary title related to risks
recap_title = tk.Label(recap_frame, text="Risk Assessment", font=("Arial", 18, 'bold'))
recap_title.pack(pady=10)

global_score_label = ttk.Label(recap_frame, text="Overall Score: 0/100", font=("Arial", 16))
global_score_label.pack(pady=10)

# Create radar chart
fig = Figure(figsize=(8, 6), dpi=100)  # Adjust for a rectangular canvas
radar_ax = fig.add_subplot(111, polar=True)
radar_canvas = FigureCanvasTkAgg(fig, master=recap_frame)
radar_canvas.get_tk_widget().pack(pady=20)

# Create the legend
legend_labels = ["Critical", "High", "Medium", "Low", "Very Low"]
legend_handles = [radar_ax.plot([], [], color=risk_colors[i], label=legend_labels[i-1])[0] for i in range(1, 6)]

# Initialize the radar chart
update_radar_chart([0, 0, 0, 0])

# Settings tab
parameters_frame = ttk.Frame(notebook)
notebook.add(parameters_frame, text="Settings")

# Variables for client and auditor names
client_name_var = tk.StringVar()
auditor_name_var = tk.StringVar()

# Input for client name
client_label = ttk.Label(parameters_frame, text="Client Name:")
client_label.pack(pady=(10, 0))
client_entry = ttk.Entry(parameters_frame, textvariable=client_name_var)
client_entry.pack(pady=(0, 10))

# Input for auditor name
auditor_label = ttk.Label(parameters_frame, text="Auditor Name:")
auditor_label.pack(pady=(10, 0))
auditor_entry = ttk.Entry(parameters_frame, textvariable=auditor_name_var)
auditor_entry.pack(pady=(0, 10))

# Logo selection
logo_button = ttk.Button(parameters_frame, text="Select Logo", command=select_logo)
logo_button.pack(pady=(10, 10))

# Display current date
date_label = ttk.Label(parameters_frame, text=f"Date: {datetime.now().strftime('%Y-%m-%d')}", font=("Arial", 12))
date_label.pack(pady=(10, 0))

# Button to export data and the chart to a PDF
export_button = ttk.Button(parameters_frame, text="Export to PDF", command=export_to_pdf)
export_button.pack(pady=(20, 10))

# Adding the new line in the parameters tab at the bottom
credits_label = ttk.Label(parameters_frame, text="Created by Clément GHANEME, based on the work of Mathis SALVADOR", font=("Arial", 8), foreground="gray")
credits_label.pack(side='bottom', pady=(10, 0))

# Main loop
root.mainloop()
