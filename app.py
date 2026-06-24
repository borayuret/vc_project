from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError


app = Flask(__name__)

# PostgreSQL bağlantısı
# Format:
# postgresql+psycopg://kullanici:sifre@host:port/veritabani
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Personel(db.Model):
    __tablename__ = "personel"

    no = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(100), nullable=False)
    soyad = db.Column(db.String(100), nullable=False)
    mail_adresi = db.Column(db.String(150), nullable=False, unique=True)
    telefon = db.Column(db.String(30), nullable=True)

    def to_dict(self):
        return {
            "no": self.no,
            "ad": self.ad,
            "soyad": self.soyad,
            "mail_adresi": self.mail_adresi,
            "telefon": self.telefon,
        }


@app.route("/")
def home():
    return jsonify({
        "message": "Personel CRUD API çalışıyor",
        "endpoints": {
            "GET /personeller": "Tüm personelleri listeler",
            "GET /personeller/<no>": "Tek personel getirir",
            "POST /personeller": "Yeni personel ekler",
            "PUT /personeller/<no>": "Personel günceller",
            "DELETE /personeller/<no>": "Personel siler",
        }
    })


@app.route("/personeller", methods=["GET"])
def personelleri_listele():
    personeller = Personel.query.order_by(Personel.no.asc()).all()
    return jsonify([personel.to_dict() for personel in personeller]), 200


@app.route("/personeller/<int:no>", methods=["GET"])
def personel_getir(no):
    personel = Personel.query.get(no)

    if personel is None:
        return jsonify({"error": "Personel bulunamadı"}), 404

    return jsonify(personel.to_dict()), 200


@app.route("/personeller", methods=["POST"])
def personel_ekle():
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON body gönderilmedi"}), 400

    zorunlu_alanlar = ["ad", "soyad", "mail_adresi"]

    for alan in zorunlu_alanlar:
        if alan not in data or not str(data[alan]).strip():
            return jsonify({"error": f"{alan} alanı zorunludur"}), 400

    yeni_personel = Personel(
        ad=data["ad"].strip(),
        soyad=data["soyad"].strip(),
        mail_adresi=data["mail_adresi"].strip(),
        telefon=data.get("telefon")
    )

    try:
        db.session.add(yeni_personel)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Bu mail adresi zaten kayıtlı"}), 409

    return jsonify(yeni_personel.to_dict()), 201


@app.route("/personeller/<int:no>", methods=["PUT"])
def personel_guncelle(no):
    personel = Personel.query.get(no)

    if personel is None:
        return jsonify({"error": "Personel bulunamadı"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON body gönderilmedi"}), 400

    if "ad" in data:
        personel.ad = data["ad"].strip()

    if "soyad" in data:
        personel.soyad = data["soyad"].strip()

    if "mail_adresi" in data:
        personel.mail_adresi = data["mail_adresi"].strip()

    if "telefon" in data:
        personel.telefon = data["telefon"]

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Bu mail adresi zaten kayıtlı"}), 409

    return jsonify(personel.to_dict()), 200


@app.route("/personeller/<int:no>", methods=["DELETE"])
def personel_sil(no):
    personel = Personel.query.get(no)

    if personel is None:
        return jsonify({"error": "Personel bulunamadı"}), 404

    db.session.delete(personel)
    db.session.commit()

    return jsonify({"message": "Personel silindi"}), 200


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
