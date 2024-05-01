from flask import Flask, render_template, request,redirect
import folium
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import pandas as pd


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

data_file = "flaskr/static/data/Meteorite_Landings_20240429.csv"
meteorite_df = pd.read_csv(data_file)
mean_location = [meteorite_df.reclat.mean(), meteorite_df.reclong.mean()]
class LocationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    year = StringField('Year', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    submit = SubmitField('Show Map')

@app.route('/',methods=['GET', 'POST'])
def index():
    global mean_location
    form = LocationForm()
    if form.validate_on_submit():
        print('here')
        # Process the form data
        name = form.name.data
        year = form.year.data
        location = form.location.data
        lat, lng = location.split(',')
        lat, lng = float(lat), float(lng)
        
		# Add the new data point to the DataFrame
        new_row = {'name': name, 'year': year, 'reclat': lat, 'reclong': lng}
        global meteorite_df
        meteorite_df = pd.concat([meteorite_df, pd.DataFrame([new_row])], ignore_index=True)
        
		# Save the updated DataFrame to the CSV file
        meteorite_df.to_csv(data_file, index=False)
        
		# Build map
        existing_locations = meteorite_df[['reclat', 'reclong']].apply(lambda x: ','.join(x.dropna().astype(str)), axis=1).tolist()
        mean_location = [meteorite_df.reclat.mean(), meteorite_df.reclong.mean()]
        map = folium.Map(location = mean_location, zoom_start=10,tiles="cartodb positron")
        # folium.Marker([0, 0], popup=location).add_to(map)
        map = map._repr_html_()
        
        names = meteorite_df['name'].tolist()
        years = meteorite_df['year'].tolist()
        return render_template('index.html',  names=names, years=years,form=form, map=map, existing_locations=existing_locations, mean_location = mean_location, location=location, name=name, year=year)

    existing_locations = meteorite_df[['reclat', 'reclong']].apply(lambda x: ','.join(x.dropna().astype(str)), axis=1).tolist()
    mean_location = [meteorite_df.reclat.mean(), meteorite_df.reclong.mean()]
    return render_map(form, existing_locations, mean_location)

# Update the render_map function in app.py
def render_map(form, existing_locations, center_point):
	
    # Create a map with existing markers from the dataframe
    # map = folium.Map(location=center_point, zoom_start=10, tiles="cartodb positron")
    # for location in existing_locations:
    #     spot = location.split(',')
    #     folium.Marker([float(spot[0]), float(spot[1])],
    #                   popup=f'Name: {form.name.data} , Year: {form.year.data}',
    #                   icon=folium.Icon(color="red", icon="info-sign")).add_to(map)
    # map_html = map._repr_html_()  # Get the map as HTML
    
    names = meteorite_df['name'].tolist()
    years = meteorite_df['year'].tolist()
    return render_template('index.html', form=form,  names=names, years=years,existing_locations=existing_locations, location=None, mean_location=center_point)

def get_center_point(lat,lon):
    return [lat.mean(), lon.mean()]
@app.route('/add_data_point', methods=['POST'])
def add_data_point():
    name = request.form['name']
    year = request.form['year']
    location = request.form['location']
    lat, lng = location.split(',')
    lat, lng = float(lat), float(lng)
    new_row = {'name': name, 'year': year, 'reclat': lat, 'reclong': lng}
    global meteorite_df
    meteorite_df = meteorite_df = pd.concat([meteorite_df, new_row], axis=0)
    
	 # Save the updated DataFrame to the CSV file
    meteorite_df.to_csv(data_file, index=False)

	# Redirect the user back to the main page
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)