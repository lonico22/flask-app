from flask import Flask, render_template, request
import folium
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import pandas as pd


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

data_file = "flaskr/static/data/Meteorite_Landings_20240429.csv"
meteorite_df = pd.read_csv(data_file)

class LocationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    year = StringField('Year', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    submit = SubmitField('Show Map')

@app.route('/',methods=['GET', 'POST'])
def index():
    form = LocationForm()
    if form.validate_on_submit():
        location = form.location.data
        name = form.name.data
        year = form.year.data
        map = folium.Map(location=[0, 0], zoom_start=2)
        folium.Marker([0, 0], popup=location).add_to(map)
        map = map._repr_html_()
        existing_locations = meteorite_df[['reclat', 'reclong']].apply(lambda x: ','.join(x.dropna().astype(str)), axis=1).tolist()
        return render_template('index.html', form=form, map=map, existing_locations=existing_locations, location=location, name=name, year=year)
    existing_locations = meteorite_df[['reclat', 'reclong']].apply(lambda x: ','.join(x.dropna().astype(str)), axis=1).tolist()
    return render_map(form, existing_locations)

def render_map(form, existing_locations):
    # Create a map with existing markers from the dataframe
    map = folium.Map(location=[0, 0], zoom_start=2)
    for location in existing_locations:
        spot = location.split(',')
        folium.Marker([float(spot[0]), float(spot[1])]).add_to(map)
    map_html = map._repr_html_()  # Get the map as HTML
    return render_template('index.html', form=form, map=map_html, existing_locations=existing_locations, location=None)

@app.route('/add_data_point', methods=['POST'])
def add_data_point():
    name = request.form['name']
    year = request.form['year']
    location = request.form['location']
    lat, lng = location.split(',')
    lat, lng = float(lat), float(lng)
    new_row = {'name': name, 'year': year, 'reclat': lat, 'reclong': lng}
    meteorite_df = meteorite_df = pd.concat([meteorite_df, new_row], axis=0)

    return 'Data point added to the dataframe'

# @app.route('/map', methods=['POST'])
# def show_map():
#     location = request.form['location']
#     map = folium.Map(location=[0, 0], zoom_start=2)
#     folium.Marker([0, 0], popup=location).add_to(map)
#     map.save('templates/map.html')
#     return render_template('map.html')
if __name__ == '__main__':
    app.run(debug=True)