from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, URL
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
db = SQLAlchemy()
db.init_app(app)

#API Key
API_KEY = "funWITHapiCODE"

##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)
    
    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

with app.app_context():
    db.create_all()
    
#create form
class CafeForm(FlaskForm):
    name = StringField('Cafe Name', validators=[DataRequired()])
    map_url = StringField('Cafe Location (Google Maps URL)', validators=[DataRequired(), URL()])
    img_url = StringField('Image URL', validators=[DataRequired(), URL()])
    location = StringField('Location', validators=[DataRequired()])
    seats = StringField('Number Of Seats', validators=[DataRequired()])
    has_toilet = BooleanField('Bathroom Available', validators=[DataRequired()])
    has_wifi = BooleanField('WiFi Available', validators=[DataRequired()])
    has_sockets = BooleanField('Power Outlets', validators=[DataRequired()])
    can_take_calls = BooleanField('Phone Call ', validators=[DataRequired()])
    coffee_price = StringField('Coffee Price', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/cafes')
def cafes():
    cafes = db.session.query(Cafe).all()
    list_of_rows = []
    for row in cafes:
        list_of_rows.append(row)
    return render_template('cafes.html', cafes=list_of_rows)


## HTTP GET - Read Record
@app.route("/random", methods=["GET"])
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe_json = jsonify(random.choice(cafes).to_dict())
    return random_cafe_json

@app.route("/all", methods=["GET"])
def get_all_cafes():
    cafes = db.session.query(Cafe).all()
    cafes_json = jsonify({cafe.id: cafe.to_dict() for cafe in cafes})
    return cafes_json

@app.route("/search", methods=["GET"])
def get_cafe_by_location():
    loc_to_search = request.args.get("loc")
    cafe = db.session.query(Cafe).filter_by(location=loc_to_search).first()
    if cafe:
        cafe_json = jsonify(cafe.to_dict())
        return cafe_json
    else:
        return jsonify({"error": {"Not Found": "We do not have a record at that location."}})

@app.route("/new", methods=["GET", "POST"])
def new_cafe():
    form = CafeForm()
    cafe_to_add = Cafe(
        name = request.form.get('name'), 
        map_url = request.form.get('map_url'), 
        img_url = request.form.get('img_url'), 
        location = request.form.get('location'), 
        seats = request.form.get('seats'), 
        has_toilet = bool(request.form.get('has_toilet')), 
        has_wifi = bool(request.form.get('has_wifi')), 
        has_sockets = bool(request.form.get('has_sockets')), 
        can_take_calls = bool(request.form.get('can_take_calls')), 
        coffee_price = request.form.get('coffee_price')
    )
    try:
        db.session.add(cafe_to_add)
        db.session.commit()
        print(cafe_to_add.to_dict())
        return redirect(url_for('cafes'))
    except exc.IntegrityError:
        print('No')
        render_template('add.html', form=form, error = "Something went wrong.")   
    return render_template('add.html', form=form, error = None)

@app.route("/cafes/remove/<int:cafe_id>", methods=["GET", "POST"])
def remove(cafe_id):
    print(cafe_id)
    with app.app_context():
        cafe = Cafe.query.get(cafe_id)
    if cafe:
        with app.app_context():
            db.session.delete(cafe)
            db.session.commit()
    return redirect(url_for('cafes'))

## HTTP POST - Create Record
@app.route("/add", methods=["GET", "POST"])
def add_a_cafe():
    cafe_to_add = Cafe(
        name = request.form.get('name'), 
        map_url = request.form.get('map_url'), 
        img_url = request.form.get('img_url'), 
        location = request.form.get('location'), 
        seats = request.form.get('seats'), 
        has_toilet = bool(request.form.get('has_toilet')), 
        has_wifi = bool(request.form.get('has_wifi')), 
        has_sockets = bool(request.form.get('has_sockets')), 
        can_take_calls = bool(request.form.get('can_take_calls')), 
        coffee_price = request.form.get('coffee_price')
    )
    try:
        db.session.add(cafe_to_add)
        db.session.commit()
        response = jsonify(response={"success": "Cafe was successfully added."})
    except exc.IntegrityError:
        response = jsonify(response={"record not added": "Duplicate Record or incorrect field."})
    return response
    

## HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    new_price = request.args.get("new_price")
    try:
        with app.app_context():
            cafe = Cafe.query.get(cafe_id)
            cafe.coffee_price = new_price
            db.session.commit()
        if cafe:  
            response = jsonify(response={"success": "Price was updated."})    
        else:
            response = jsonify(error={"Cafe not found": "Something went wrong."})    
    except AttributeError:
        response = jsonify(error={"Cafe not found": "Something went wrong."})
    return response

## HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    request_api_key = request.args.get("api-key")
    if request_api_key == API_KEY:
        with app.app_context():
            cafe = Cafe.query.get(cafe_id)
        if cafe:
            with app.app_context():
                db.session.delete(cafe)
                db.session.commit()
            response = jsonify(response={"success": "Cafe was removed."})  
        else:
            response = jsonify(error={"Cafe not found": "Something went wrong."})
    else:
        response = jsonify(error={"Cafe not removed": "incorrect api key"})
    return response
    

if __name__ == '__main__':
    app.run(debug=True)
