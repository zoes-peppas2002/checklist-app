from flask_login import UserMixin
from extensions import db, login_manager
from run import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    
from datetime import datetime
from extensions import db

class Checklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_name = db.Column(db.String(100), nullable=False)
    consultant_name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    # ΠΡΟΣΩΠΙΚΟ
    prosopiko_1 = db.Column(db.Integer, nullable=False)
    prosopiko_2 = db.Column(db.Integer, nullable=False)
    prosopiko_3 = db.Column(db.Integer, nullable=False)

    # ΕΞΩΤΕΡΙΚΟΣ ΧΩΡΟΣ
    exwterikos_1 = db.Column(db.Integer, nullable=False)
    exwterikos_2 = db.Column(db.Integer, nullable=False)
    exwterikos_3 = db.Column(db.Integer, nullable=False)

    # ΕΣΩΤΕΡΙΚΟ ΚΑΘΙΣΤΙΚΟ
    eswteriko_1 = db.Column(db.Integer, nullable=False)
    eswteriko_2 = db.Column(db.Integer, nullable=False)
    eswteriko_3 = db.Column(db.Integer, nullable=False)
    eswteriko_4 = db.Column(db.Integer, nullable=False)

    # ΚΑΦΕΚΟΠΤΕΙΟ
    kafekopteio_1 = db.Column(db.Integer, nullable=False)
    kafekopteio_2 = db.Column(db.Integer, nullable=False)
    kafekopteio_3 = db.Column(db.Integer, nullable=False)
    kafekopteio_4 = db.Column(db.Integer, nullable=False)
    kafekopteio_5 = db.Column(db.Integer, nullable=False)  # Κόφτης
    kafekopteio_6 = db.Column(db.Integer, nullable=False)  # Κόφτης

    # ΖΕΣΤΗ ΒΙΤΡΙΝΑ
    zesth_1 = db.Column(db.Integer, nullable=False)
    zesth_2 = db.Column(db.Integer, nullable=False)
    zesth_3 = db.Column(db.Integer, nullable=False)
    zesth_4 = db.Column(db.Integer, nullable=False)
    zesth_5 = db.Column(db.Integer, nullable=False)
    zesth_6 = db.Column(db.Integer, nullable=False)
    zesth_7 = db.Column(db.Integer, nullable=False)
    zesth_8 = db.Column(db.Integer, nullable=False)  # Κόφτης
    zesth_9 = db.Column(db.Integer, nullable=False)  # Κόφτης

    # ΚΡΥΑ ΒΙΤΡΙΝΑ
    krya_1 = db.Column(db.Integer, nullable=False)
    krya_2 = db.Column(db.Integer, nullable=False)
    krya_3 = db.Column(db.Integer, nullable=False)
    krya_4 = db.Column(db.Integer, nullable=False)
    krya_5 = db.Column(db.Integer, nullable=False)
    krya_6 = db.Column(db.Integer, nullable=False)
    krya_7 = db.Column(db.Integer, nullable=False)
    krya_8 = db.Column(db.Integer, nullable=False)  # Κόφτης
    krya_9 = db.Column(db.Integer, nullable=False)  # Κόφτης

    # ΟΥΔΕΤΕΡΗ ΒΙΤΡΙΝΑ
    oudet_1 = db.Column(db.Integer, nullable=False)
    oudet_2 = db.Column(db.Integer, nullable=False)
    oudet_3 = db.Column(db.Integer, nullable=False)
    oudet_4 = db.Column(db.Integer, nullable=False)
    oudet_5 = db.Column(db.Integer, nullable=False)
    oudet_6 = db.Column(db.Integer, nullable=False)
    oudet_7 = db.Column(db.Integer, nullable=False)
    oudet_8 = db.Column(db.Integer, nullable=False)  # Κόφτης

    # ΑΥΘΑΙΡΕΤΗΣ ΠΩΛΗΣΗΣ
    ayth_1 = db.Column(db.Integer, nullable=False)
    ayth_2 = db.Column(db.Integer, nullable=False)
    ayth_3 = db.Column(db.Integer, nullable=False)
    ayth_4 = db.Column(db.Integer, nullable=False)
    ayth_5 = db.Column(db.Integer, nullable=False)  # Κόφτης
    ayth_6 = db.Column(db.Integer, nullable=False)  # Κόφτης

    # ΨΥΓΕΙΑ
    psygeia_1 = db.Column(db.Integer, nullable=False)
    psygeia_2 = db.Column(db.Integer, nullable=False)
    psygeia_3 = db.Column(db.Integer, nullable=False)
    psygeia_4 = db.Column(db.Integer, nullable=False)
    psygeia_5 = db.Column(db.Integer, nullable=False)
    psygeia_6 = db.Column(db.Integer, nullable=False)  # Κόφτης
    psygeia_7 = db.Column(db.Integer, nullable=False)  # Κόφτης

    # ΔΙΑΦΗΜΙΣΤΙΚΟ ΥΛΙΚΟ
    diaf_1 = db.Column(db.Integer, nullable=False)
    diaf_2 = db.Column(db.Integer, nullable=False)
    diaf_3 = db.Column(db.Integer, nullable=False)
    diaf_4 = db.Column(db.Integer, nullable=False)

    # ΑΠΟΘΗΚΗ
    apoth_1 = db.Column(db.Integer, nullable=False)
    apoth_2 = db.Column(db.Integer, nullable=False)
    apoth_3 = db.Column(db.Integer, nullable=False)
    apoth_4 = db.Column(db.Integer, nullable=False)
    apoth_5 = db.Column(db.Integer, nullable=False)
    apoth_6 = db.Column(db.Integer, nullable=False)
    apoth_7 = db.Column(db.Integer, nullable=False)  # Κόφτης
    apoth_8 = db.Column(db.Integer, nullable=False)

    # ΠΟΣΤΟ ΚΑΦΕ
    posto_1 = db.Column(db.Integer, nullable=False)
    posto_2 = db.Column(db.Integer, nullable=False)
    posto_3 = db.Column(db.Integer, nullable=False)
    posto_4 = db.Column(db.Integer, nullable=False)
    posto_5 = db.Column(db.Integer, nullable=False)
    posto_6 = db.Column(db.Integer, nullable=False)
    posto_7 = db.Column(db.Integer, nullable=False)
    posto_8 = db.Column(db.Integer, nullable=False)  # Κόφτης
    posto_9 = db.Column(db.Integer, nullable=False)  # Κόφτης
    posto_10 = db.Column(db.Integer, nullable=False)
    posto_11 = db.Column(db.Integer, nullable=False)
    posto_12 = db.Column(db.Integer, nullable=False)
    posto_13 = db.Column(db.Integer, nullable=False)
    posto_14 = db.Column(db.Integer, nullable=False)  # Κόφτης
    posto_15 = db.Column(db.Integer, nullable=False)  # Κόφτης

    # ΕΞΟΠΛΙΣΜΟΣ
    exopl_1 = db.Column(db.Integer, nullable=False)
    exopl_2 = db.Column(db.Integer, nullable=False)
    exopl_3 = db.Column(db.Integer, nullable=False)
    exopl_4 = db.Column(db.Integer, nullable=False)

    # ΥΠΟΧΡΕΩΤΙΚΑ ΕΓΓΡΑΦΑ
    eggrafa_1 = db.Column(db.Integer, nullable=False)
    eggrafa_2 = db.Column(db.Integer, nullable=False)

    # Τελικά πεδία
    total_score = db.Column(db.Float, nullable=False)
    has_zero_cutoff = db.Column(db.Boolean, default=False)
    pdf_url = db.Column(db.String(500))

class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    consultant_username = db.Column(db.String(150), db.ForeignKey('user.username'), nullable=False)

    def __repr__(self):
        return f"{self.name} - {self.address}"
