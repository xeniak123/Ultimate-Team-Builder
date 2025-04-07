# ⚽ FIFA Ultimate Team Builder (Python + CustomTkinter)

![Made with ChatGPT](https://img.shields.io/badge/Made%20with-ChatGPT-ffbf00?logo=openai&logoColor=black&style=for-the-badge)

A modern desktop application that lets you build your own football team just like in FIFA Ultimate Team — built with `customtkinter` in Python.

---

### 🛠️ Features

- 🔍 Search and select exactly **11 players** and **1 manager** from a JSON database
- 📜 Scrollable, filterable player list with smooth toggle selection
- 🧠 Smart chemistry and rating system based on **position, nationality, league, and manager**
- ⚙️ Realistic **4-4-2 pitch layout** with players assigned to specific field zones (ST, CM, GK, etc.)
- 💾 Save and load your squads from files
- 🎲 Randomize entire squad or just auto-assign players to positions
- 🖥️ Responsive, modern GUI using `customtkinter`

---

### 🚀 How to Run

1. 📦 Make sure you have Python 3.10+ installed.
2. 🔧 Install required library:

```bash
pip install customtkinter
📁 Clone the repository or download the files:


git clone https://github.com/xeniak123/fifa-team-builder.git
cd fifa-team-builder
▶️ Run the app:


python main.py
Or just double-click run.bat (Windows only).

🧠 Chemistry & Rating System
✔️ +1 Chemistry: if player's nationality matches manager

✔️ +1 Chemistry: if player's league matches manager

❌ -3 to rating if player is in the wrong position

✅ Final average rating and chemistry are shown in-app

✍️ Add Your Own Players
You can add new footballers or managers directly in players.json.
Use the same format as the other entries, like this:

json
{
  "name": "Zinedine Zidane",
  "position": "CM",
  "rating": 91,
  "nationality": "France",
  "league": "La Liga"
}
For managers:


{
  "name": "Didier Deschamps",
  "type": "manager",
  "nationality": "France",
  "league": "International"
}
Then just save the file and restart the app — your custom players will appear in the list!

👶 Author
Made with 💙 by Xeniak

💡 I'm still very young and this is my first ever project on GitHub.
I'm learning Python and GUI development — and I hope this project helps others who are just starting too! 😊
Feel free to share feedback, ideas, or contribute!
