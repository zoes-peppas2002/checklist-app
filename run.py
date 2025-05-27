from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from fpdf import FPDF
from flask import send_from_directory

from extensions import db, login_manager
from models_def import User, Checklist
import json



STORE_FILE = os.path.join("static", "store_map.json")

def load_store_map():
    if os.path.exists(STORE_FILE):
        with open(STORE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_store_map(store_map):
    with open(STORE_FILE, 'w', encoding='utf-8') as f:
        json.dump(store_map, f, ensure_ascii=False, indent=2)


# --- Flask setup ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database.db')

# --- Init Extensions ---
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- User loader ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Routes ---

@app.route('/')
def home():
    return redirect(url_for('login'))
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Λάθος στοιχεία σύνδεσης')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username, role=current_user.role)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_panel():
    if current_user.role != 'admin':
        return "Απαγορεύεται η πρόσβαση", 403

    if request.method == 'POST':
        # ➤ Reset password
        if 'reset_password' in request.form:
            user_id = request.form.get('user_id')
            new_password = request.form.get('new_password')
            user = User.query.get(user_id)
            if user:
                user.password = generate_password_hash(new_password)
                db.session.commit()
                flash(f"Ο κωδικός του χρήστη {user.username} άλλαξε επιτυχώς.")
            return redirect(url_for('admin_panel'))

        # ➤ Delete user
        if 'delete_user' in request.form:
            user_id = request.form.get('delete_user_id')
            user = User.query.get(user_id)
            if user and user.role != 'admin':
                db.session.delete(user)
                db.session.commit()
                flash(f"Ο χρήστης {user.username} διαγράφηκε.")
            return redirect(url_for('admin_panel'))

        # ➤ Add new user
        if 'add_user' in request.form:
            username = request.form['username']
            password = request.form['password']
            role = request.form['role']

            if User.query.filter_by(username=username).first():
                flash('Υπάρχει ήδη αυτό το username.')
                return redirect(url_for('admin_panel'))

            new_user = User(
                username=username,
                password=generate_password_hash(password),
                role=role
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Ο χρήστης δημιουργήθηκε επιτυχώς.')
            return redirect(url_for('admin_panel'))

    users = User.query.all()
    return render_template('admin.html', users=users)
    
@app.route('/admin_reports', methods=['GET'])
@login_required
def admin_reports():
    if current_user.role not in ['admin']:
        return "Απαγορεύεται", 403

    consultant = request.args.get('consultant')
    selected_date = request.args.get('date')

    reports_root = os.path.join('static', 'reports')
    consultants = []
    available_dates = set()
    reports_map = {}

    if os.path.exists(reports_root):
        for name in os.listdir(reports_root):
            consultant_path = os.path.join(reports_root, name)
            if os.path.isdir(consultant_path):
                consultants.append(name)
                if name == consultant:
                    for store in os.listdir(consultant_path):
                        store_path = os.path.join(consultant_path, store)
                        if os.path.isdir(store_path):
                            for filename in os.listdir(store_path):
                                if filename.endswith(".pdf"):
                                    # Extract date from filename
                                    if "_" in filename:
                                        date_part = filename.split("_")[0]
                                        available_dates.add(date_part)

                                        if date_part == selected_date:
                                            if selected_date not in reports_map:
                                                reports_map[selected_date] = []
                                            reports_map[selected_date].append({
                                                "store": store,
                                                "filename": filename,
                                                "path": f"/static/reports/{consultant}/{store}/{filename}"
                                            })

    return render_template(
        "admin_reports.html",
        consultants=sorted(consultants),
        selected_consultant=consultant,
        selected_date=selected_date,
        available_dates=sorted(available_dates),
        reports=reports_map.get(selected_date, [])
    )
                           
@app.route('/checklist_form', methods=['GET'])
@login_required
def checklist_form():
    if current_user.role != 'consultant':
        return "Απαγορεύεται η πρόσβαση", 403

    store_map = load_store_map()
    user_stores = store_map.get(current_user.username, [])
    current_date = datetime.now().strftime('%Y-%m-%d')
    current_time = datetime.now().strftime('%H:%M')

    return render_template('checklist_form.html',
        date=current_date,
        time=current_time,
        username=current_user.username,
        stores=user_stores
    )




@app.route('/submit_checklist', methods=['POST'])
@login_required
def submit_checklist():
    if current_user.role != 'consultant':
        return "Απαγορεύεται η πρόσβαση", 403

    from fpdf import FPDF

    store_name = request.form.get('store_name')
    consultant_name = current_user.username
    date_created = datetime.now()

    # Όλα τα κριτήρια
    field_names = [
        # ΠΡΟΣΩΠΙΚΟ
        'prosopiko_1', 'prosopiko_2', 'prosopiko_3',

        # ΕΞΩΤΕΡΙΚΟΣ ΧΩΡΟΣ
        'exwterikos_1','exwterikos_2','exwterikos_3',

        # ΕΣΩΤΕΡΙΚΟ ΚΑΘΙΣΤΙΚΟ
        'eswteriko_1', 'eswteriko_2', 'eswteriko_3', 'eswteriko_4',

        # ΚΑΦΕΚΟΠΤΕΙΟ
        'kafekopteio_1', 'kafekopteio_2', 'kafekopteio_3', 'kafekopteio_4', 'kafekopteio_5', 'kafekopteio_6',

        # ΖΕΣΤΗ ΒΙΤΡΙΝΑ
        'zesth_1', 'zesth_2', 'zesth_3', 'zesth_4', 'zesth_5', 'zesth_6', 'zesth_7', 'zesth_8', 'zesth_9',

        # ΚΡΥΑ ΒΙΤΡΙΝΑ
        'krya_1', 'krya_2', 'krya_3', 'krya_4', 'krya_5', 'krya_6', 'krya_7', 'krya_8', 'krya_9',

        # ΟΥΔΕΤΕΡΗ ΒΙΤΡΙΝΑ
        'oudet_1', 'oudet_2', 'oudet_3', 'oudet_4', 'oudet_5', 'oudet_6', 'oudet_7', 'oudet_8', 

        # ΠΡΟΪΟΝΤΑ ΑΥΘΑΙΡΕΤΗΣ ΠΩΛΗΣΗΣ
        'ayth_1', 'ayth_2', 'ayth_3', 'ayth_4', 'ayth_5', 'ayth_6',

        # ΨΥΓΕΙΑ
        'psygeia_1', 'psygeia_2', 'psygeia_3', 'psygeia_4', 'psygeia_5', 'psygeia_6', 'psygeia_7',

        # ΔΙΑΦΗΜΙΣΤΙΚΟ ΥΛΙΚΟ - ΣΗΜΑΝΣΕΙΣ
        'diaf_1', 'diaf_2', 'diaf_3', 'diaf_4',

        # ΑΠΟΘΗΚΗ
        'apoth_1', 'apoth_2', 'apoth_3', 'apoth_4', 'apoth_5', 'apoth_6', 'apoth_7', 'apoth_8',

        # ΠΟΣΤΟ ΚΑΦΕ
        'posto_1', 'posto_2', 'posto_3', 'posto_4', 'posto_5', 'posto_6', 'posto_7',
        'posto_8', 'posto_9', 'posto_10', 'posto_11', 'posto_12', 'posto_13', 'posto_14', 'posto_15',

        # ΕΞΟΠΛΙΣΜΟΣ
        'exopl_1', 'exopl_2', 'exopl_3', 'exopl_4',

        # ΥΠΟΧΡΕΩΤΙΚΑ ΕΓΓΡΑΦΑ
        'eggrafa_1', 'eggrafa_2'
    ]


    cutoff_fields = [
        'kafekopteio_5', 'kafekopteio_6', 'zesth_8', 'zesth_9',
        'krya_8', 'krya_9', 'oudet_8', 'ayth_5', 'ayth_6',
        'psygeia_6', 'psygeia_7', 'apoth_7', 'posto_8', 'posto_9', 'posto_14', 'posto_15'
    ]

    CATEGORY_WEIGHTS = {
        "prosopiko": 0.05,
        "exwterikos": 0.05,
        "eswteriko": 0.05,
        "kafekopteio": 0.1,
        "zesth": 0.08,
        "krya": 0.08,
        "oudet": 0.08,
        "ayth": 0.07,
        "psygeia": 0.07,
        "diaf": 0.05,
        "apoth": 0.07,
        "posto": 0.15,
        "exopl": 0.07,
        "eggrafa": 0.03
    }

    data = {}
    has_zero_cutoff = False

    for field in field_names:
        val = int(request.form.get(field, 0))
        data[field] = val
        if field in cutoff_fields and val == 0:
            has_zero_cutoff = True

    if has_zero_cutoff:
        total_score = 0
    else:
        weighted_score = 0
        debug_info = []  # Συλλογή πληροφοριών για εκτύπωση

    for prefix, weight in CATEGORY_WEIGHTS.items():
        relevant = [v for k, v in data.items() if k.startswith(prefix)]
        max_score = len(relevant) * 4
        actual_score = sum(relevant)

        if max_score > 0:
            contribution = (actual_score / max_score) * weight
            weighted_score += contribution

            debug_info.append(
                f"[{prefix}] {len(relevant)} πεδία, "
                f"Βαρύτητα: {weight}, "
                f"Score: {actual_score}/{max_score}, "
                f"Συνεισφορά: {round(contribution*100, 2)}%"
            )

    total_score = round(weighted_score * 100, 2)

    print("\nDEBUG ΕΛΕΓΧΟΣ ΒΑΡΥΤΗΤΩΝ:")
    for line in debug_info:
        print(line)
    print(f"--> Τελικό σκορ: {total_score}%\n")

    # Αποθήκευση στο DB
    checklist = Checklist(
        store_name=store_name,
        consultant_name=consultant_name,
        date_created=date_created,
        total_score=total_score,
        has_zero_cutoff=has_zero_cutoff,
        **data
    )
    db.session.add(checklist)
    db.session.commit()

    # Αποθήκευση PDF σε σωστό path
    folder_path = os.path.join("static", "reports", consultant_name, store_name)
    os.makedirs(folder_path, exist_ok=True)
    filename = f"{date_created.strftime('%Y-%m-%d_%H-%M')}_report.pdf"
    pdf_path = os.path.join(folder_path, filename)

    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'static/fonts/DejaVuSans.ttf', uni=True)
    pdf.set_font('DejaVu', '', 12)
    pdf.cell(200, 10, txt="Αναφορά Checklist", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Κατάστημα: {store_name}", ln=True)
    pdf.cell(200, 10, txt=f"Σύμβουλος: {consultant_name}", ln=True)
    pdf.cell(200, 10, txt=f"Ημερομηνία: {date_created.strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.cell(200, 10, txt=f"Σκορ: {total_score}%", ln=True)
    pdf.cell(200, 10, txt=f"Κόφτης: {'ΝΑΙ' if has_zero_cutoff else 'ΟΧΙ'}", ln=True)
    pdf.ln(10)

    for key, value in data.items():
        pdf.cell(200, 8, txt=f"{key}: {value}", ln=True)

    pdf.output(pdf_path)

    return render_template("checklist_result.html", score=total_score, cutoff=has_zero_cutoff)


    
@app.route('/reports')
@login_required
def view_reports():
    if current_user.role not in ['admin']:
        return "Απαγορεύεται η πρόσβαση", 403


    base_path = os.path.join('static', 'reports')
    reports = {}

    if os.path.exists(base_path):
        for consultant in os.listdir(base_path):
            consultant_path = os.path.join(base_path, consultant)
            if os.path.isdir(consultant_path):
                reports[consultant] = {}
                for date_folder in os.listdir(consultant_path):
                    date_path = os.path.join(consultant_path, date_folder)
                    if os.path.isdir(date_path):
                        files = []
                        for file in os.listdir(date_path):
                            if file.endswith('.pdf'):
                                rel_path = os.path.join('/static/reports', consultant, date_folder, file)
                                files.append(rel_path)
                        if files:
                            reports[consultant][date_folder] = files

    return render_template('manager_reports.html', reports=reports)


@app.route('/manage_stores', methods=['GET', 'POST'])
@login_required
def manage_stores():
    if current_user.role not in ['admin']:
        return "Απαγορεύεται η πρόσβαση", 403

    consultants = User.query.filter_by(role='consultant').all()
    store_map = load_store_map()

    # Βρες τον επιλεγμένο σύμβουλο
    selected = request.args.get('selected')
    if not selected and consultants:
        selected = consultants[0].username

    if request.method == 'POST':
        username = request.form.get('username')
        action = request.form.get('action')

        if username not in store_map:
            store_map[username] = []

        if action == 'add':
            city = request.form.get('new_city', '').strip()
            address = request.form.get('new_address', '').strip()
            if city and address:
                store_entry = f"{city.upper()} — {address}"
                if store_entry not in store_map[username]:
                    store_map[username].append(store_entry)
                    flash(f"Το κατάστημα '{store_entry}' προστέθηκε.")
                else:
                    flash("Το κατάστημα υπάρχει ήδη σε αυτόν τον σύμβουλο.", "error")
            else:
                flash("Συμπλήρωσε και πόλη και διεύθυνση.", "error")

        elif action == 'delete':
            to_delete = request.form.get('delete_store')
            if to_delete in store_map[username]:
                store_map[username].remove(to_delete)

        save_store_map(store_map)
        return redirect(url_for('manage_stores', selected=username))

    return render_template(
        'manage_stores.html',
        consultants=consultants,
        consultant_stores=store_map,
        selected=selected
    )

@app.route('/my_reports', methods=['GET', 'POST'])
@login_required
def my_reports():
    if current_user.role != 'consultant':
        return "Απαγορεύεται η πρόσβαση", 403

    store_map_path = os.path.join("static", "store_map.json")
    selected_store = None
    reports = []

    if not os.path.exists(store_map_path):
        return "Το αρχείο store_map.json δεν βρέθηκε."

    with open(store_map_path, 'r', encoding='utf-8') as f:
        store_map = json.load(f)

    consultant_stores = store_map.get(current_user.username, [])

    if request.method == 'POST':
        selected_store = request.form.get('store_name')
        if selected_store and selected_store in consultant_stores:
            report_dir = os.path.join('static', 'reports', current_user.username, selected_store)
            if os.path.exists(report_dir):
                for file in os.listdir(report_dir):
                    if file.endswith('.pdf'):
                        rel_path = os.path.join('/static/reports', current_user.username, selected_store, file)
                        reports.append(rel_path)
                reports.sort()

    return render_template(
        'consultant_reports.html',
        stores=consultant_stores,
        selected_store=selected_store,
        reports=reports
    )






    
    






@app.route('/consultant_reports')
@login_required
def consultant_reports():
    if current_user.role != 'consultant':
        return "Απαγορεύεται η πρόσβαση", 403

    user_folder = os.path.join("static", "reports_by_store", current_user.username)
    stores = sorted(os.listdir(user_folder)) if os.path.exists(user_folder) else []
    selected = request.args.get('store_name', stores[0] if stores else None)

    reports = []
    if selected:
        path = os.path.join(user_folder, selected)
        if os.path.exists(path):
            for f in sorted(os.listdir(path)):
                if f.endswith(".pdf"):
                    reports.append(f"/{path}/{f}".replace("\\", "/"))

    return render_template("consultant_reports.html", stores=stores, selected=selected, reports=reports)


    
@app.route('/manage_reports', methods=['GET', 'POST'])
@login_required
def manage_reports():
    if current_user.role != 'admin':
        return "Απαγορεύεται η πρόσβαση", 403

    base_path = os.path.join('static', 'reports')
    consultants = sorted(os.listdir(base_path)) if os.path.exists(base_path) else []

    selected_consultant = request.args.get('consultant')
    selected_date = request.args.get('date')

    available_dates = []
    reports = []

    if selected_consultant:
        consultant_path = os.path.join(base_path, selected_consultant)
        if os.path.exists(consultant_path):
            available_dates = sorted(os.listdir(consultant_path))

            if selected_date:
                date_path = os.path.join(consultant_path, selected_date)
                if os.path.exists(date_path):
                    for file in sorted(os.listdir(date_path)):
                        if file.endswith('.pdf'):
                            file_path = os.path.join(date_path, file)
                            is_hidden = file.startswith("_HIDDEN_")
                            reports.append({
                                'filename': file,
                                'url': os.path.join('/static/reports', selected_consultant, selected_date, file),
                                'hidden': is_hidden
                            })

    return render_template('manage_reports.html',
        consultants=consultants,
        selected_consultant=selected_consultant,
        available_dates=available_dates,
        selected_date=selected_date,
        reports=reports
    )
    
@app.route('/toggle_report_visibility', methods=['POST'])
@login_required
def toggle_report_visibility():
    if current_user.role != 'admin':
        return "Απαγορεύεται η πρόσβαση", 403

    file_path = request.form.get('file_path')
    if file_path:
        full_path = file_path.replace("/static", "static")
        abs_path = os.path.join(os.getcwd(), full_path)

        if os.path.exists(abs_path):
            if "_hidden" in abs_path:
                new_path = abs_path.replace("_hidden", "")
            else:
                new_path = abs_path.replace(".pdf", "_hidden.pdf")
            os.rename(abs_path, new_path)

    return redirect(request.referrer or url_for('admin_reports'))
    
@app.route('/delete_report', methods=['POST'])
@login_required
def delete_report():
    if current_user.role != 'admin':
        return "Απαγορεύεται η πρόσβαση", 403

    file_path = request.form.get('file_path')
    if file_path:
        full_path = file_path.replace("/static", "static")
        abs_path = os.path.join(os.getcwd(), full_path)
        if os.path.exists(abs_path):
            os.remove(abs_path)
    return redirect(request.referrer or url_for('admin_reports'))
    
import os
from flask import send_from_directory



# --- Εκκίνηση ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
