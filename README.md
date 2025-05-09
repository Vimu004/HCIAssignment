# FurniFlow Studio

FurniFlow Studio is a browser-based 3D interior design application that allows users to visualize room layouts by placing and manipulating furniture models. This application was developed for an HCI assignment and includes full backend/frontend integration, 3D rendering, and a simple state persistence mechanism.

---

## 🔧 Features

- Interactive 3D room with floor, walls, and ceiling.
- Realtime lighting and camera controls.
- Upload and render 3D furniture models (.glb format).
- Snap-to-grid movement & UI-based model manipulation (rotate, move).
- Save/load room designs using JSON.
- Color and size customization for walls, floor, and ceiling.
- Export screenshots of current design.
- Furniture catalog selector via popup.
- Basic user management system (register, login).
- Admin panel to manage uploaded designs and users.

---

## 📁 Project Structure


    HCIAssignment/
    │
    ├── app.py                      # Flask entry point
    ├── blueprints/                # Modularized routes (auth, studio, catalog, etc.)
    ├── data/                      # JSON-based storage for furniture, users, designs
    ├── frontend/                  # JS assets, package.json, vite config
    ├── static/                    # Static files: assets, CSS, uploaded .glb models
    ├── templates/                 # HTML pages using Jinja2 templating
    ├── utils/                     # Support functions like Trellis/GLB converters


---

## 🚀 Getting Started

Clone the repository the;

### 1. Install dependencies

bash
pip install flask
cd frontend
npm install


### 2. Run the app

bash
npm run build      # compile Vite frontend
cd ..
python app.py      # launch Flask backend


The app will be available at: http://localhost:5000/

---

## 📦 JSON-Based Storage

No SQL database is used in this version. Instead:

- data/users.json - stores user credentials
- data/designs.json - saved design metadata
- data/models.json - model info
- data/testing.json - sample records

These act as lightweight JSON-based flatfile databases.

---

## 🎨 UI/UX Stack

- Tailwind CSS for styling
- Heroicons for icons
- Three.js for 3D rendering
- Vite + Vanilla JS for frontend bundling

---

## 🧠 AI Integration Ready

Code structure anticipates AI extensions such as:

- Depth estimation using MiDaS
- 2D to 3D mesh generation with TripoSR or Trellis via utils/trellis_runner.py

---

## 📂 Sample Assets

- 3D .glb models stored in static/models/
- Catalog preview images in static/assets/catalog/

---

## 🔐 Authentication

- Registration and Login routes in blueprints/auth.py
- Session-based access to user-specific designs
- Admin permissions not enforced yet but hooks exist

---

## 📈 Future Improvements

- Integrate database for scalability (PostgreSQL)
- Add drag-and-drop UI in 3D space
- Improve model collision detection
- Role-based access controls (Admin, Designer)
- Convert JSON store to Supabase or Firebase backend

---

## 🧪 Testing

Run via:

bash
python app.py


Test views in blueprints/testing.py and templates/testing.html.

---

## 👨‍💻 Contributors
    
    | Index No. | Name                        | Role                        | Responsibilities                                                                                                                                                       |
    |-----------|-----------------------------|-----------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | 10899480  | Murukkuwadura S Mendis      | Backend Developer           | Implemented Flask routes, Supabase integration for a database, and Trellis API logic for 3D rendering, Created the Studio Feature, Furniture catalog and improved the user experience. And wrote the report. |
    | 10899502  | Don Wijesiriwardana         | Project Lead & Frontend Developer | Developed the design studio interface; integrated .glb viewer, and developed the User interfaces, Login, Register, Feedback and Furniture pages. Structure and writing the report and create the architectural designs |
    | 10899280  | Adikaram Adikaram           | UI/UX Designer              | Created the initial and the sketches of the UI UX design. Wrote the report.                                                                                             |
    | 10899197  | Vithjeshayan Sujanthan      | QA Engineer                 | Tested the FurniFlow and created the user cases and the test cases and then wrote the report                                                                            |



---
