# Express_Audit

This little tool came to life during a random free afternoon when I had nothing better to do. The idea behind it was simple: create something quick and dirty that could help the non-tech-savvy members of my team when they visit clients or prospects. It’s meant to give them a way to walk into an office, take a quick look at the IT setup, and leave with a clear sense of how things are functioning — without needing deep technical knowledge.

# Purpose:
The software is designed to give a super fast, no-fuss assessment of a client’s IT infrastructure. It allows non-technicians to gather basic, yet important, information about a client’s setup and generate a clean PDF report right there on the spot. The PDF includes a quick breakdown of the state of servers, backups, and network security, along with our company's contact details for follow-ups.

It’s perfect for leaving behind a professional document after a quick look, without anyone needing to dig into complicated tools or manuals. This way, when our technicians come in later, they have a head start with a basic view of what’s going on.

# How It Works:

The software is built using Python and has a simple graphical interface powered by Tkinter. 

Users can input some basic details like the client’s name, auditor name, and even upload the company’s logo for a custom touch on the final report.

As the user runs through its checks, the graph displays the status of each component, providing a live view of the systems that are being reviewed.

After the audit is complete, the software spits out a neat PDF report with the company logo, contact details, and a breakdown of the systems' health. 
The report can be handed over to the client instantly, making them feel like we’ve left something useful behind.
