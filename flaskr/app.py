from flask import Flask, render_template, request,redirect, jsonify, request
import folium
from flask_wtf import FlaskForm
from wtforms import StringField,SelectField, SubmitField, TextAreaField, DateTimeField, HiddenField
from wtforms.validators import DataRequired, InputRequired
from wtforms.widgets import TextArea
import pandas as pd
from datetime import datetime
import pytz
from tzlocal import get_localzone
import logging



app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

data_file = "flaskr/static/data/Meteorite_Landings_20240429.csv"
meteorite_df = pd.read_csv(data_file)
mean_location = [meteorite_df.reclat.mean(), meteorite_df.reclong.mean()]
categories = ['all','aaaaa','bbb','ccc','dddd','eee','fff']
tz = get_localzone()

map = folium.Map(location = [0,0], zoom_start=10,tiles="cartodb positron")


class LocationForm(FlaskForm):
    datetime_field = HiddenField('Datetime', default = datetime.today, validators=[DataRequired()])
    timezone = SelectField('Timezone', choices=[(tz, tz) for tz in pytz.common_timezones], default=tz.key)
    location = StringField('Location', validators=[DataRequired()])
    # datetime_field = DateTimeField('Datetime (UTC)', validators=[DataRequired()], format='%Y-%m-%d %H:%M:%S %Z%z')
    itemone = StringField('Item 1', validators=[DataRequired()])
    itemtwo = StringField('Item 2', validators=[DataRequired()])
    itemthree = StringField('Item 3', validators=[DataRequired()])
    itemfour = StringField('Item 4')
    
    itemfive = TextAreaField('Item 5', widget=TextArea())
    itemsix = StringField('Item 6');
    new_input = StringField('New Input', render_kw={'multiple': True})
    submit = SubmitField('Submit')

@app.route('/',methods=['GET', 'POST'])
def index():
    global mean_location
    category = request.form.get('category')

    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    form = LocationForm()
    if form.validate_on_submit():

        print('here')
        # # Get the datetime object from the form
        # dt = form.datetime_field.data
        # # Set the timezone to UTC
        # dt_utc = dt.astimezone(pytz.UTC)
        # # Do something with the datetime object
        # print(dt_utc)

        timezone = form.timezone.data
        # Do something with the timezone
        print(f'Timezone: {timezone}')
        # Get the datetime and timezone from the form
        dt = form.datetime_field.data
        tz = form.timezone.data
        # Do something with the datetime and timezone
        print(dt, tz)

        # Process the form data
        itemtwo = form.itemtwo.data
        itemone = form.itemone.data
        new_inputs = request.form.getlist('new_input')  # Access the new input values here
        location = form.location.data
        lat, lng = location.split(',')
        lat, lng = float(lat), float(lng)
        app.logger.info(new_inputs)
		# Add the new data point to the DataFrame
        new_row = {'itemone': itemone, 'year': itemtwo, 'reclat': lat, 'reclong': lng}
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
        
        itemones = meteorite_df['name'].tolist()
        years = meteorite_df['year'].tolist()
        return render_template('index.html', categories =categories, curdatetime = current_datetime, itemones=itemones, year=itemtwo,form=form, map=map, existing_locations=existing_locations, mean_location = mean_location, location=location, itemone=itemone)

    # if request.method == 'POST':
    #     category = request.form['category']
    #     app.logger.info(category)
    #     map = update_map(category)
    # else:
    #     map = update_map('all')  # Default category

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
    #                   popup=f'itemone: {form.itemone.data} , Year: {form.year.data}',
    #                   icon=folium.Icon(color="red", icon="info-sign")).add_to(map)
    # map_html = map._repr_html_()  # Get the map as HTML
    
    itemones = meteorite_df['name'].tolist()
    itemtwo = meteorite_df['year'].tolist()
    return render_template('index.html', form=form, categories =categories, itemones=itemones, year=itemtwo,existing_locations=existing_locations, location=None, mean_location=center_point)
# Function to filter data and update Folium map
# def update_map(category):
#     if category == 'all':
#         filtered_data = meteorite_df
#     else:
#         filtered_data = meteorite_df[meteorite_df['category'] == category]
#     # map.clear_layers()
#     print(len(filtered_data))
#     map_data = filtered_data[['reclat', 'reclong', 'name']].to_dict(orient='records')
#     return jsonify(map_data)
def get_center_point(lat,lon):
    return [lat.mean(), lon.mean()]

@app.route('/update_map', methods=['POST'])
def update_map():
    category = request.form.get('category')
    if category == 'all':
        filtered_data = meteorite_df
    else:
        filtered_data = meteorite_df[meteorite_df['category'] == category]
    
    filtered_data.loc[:, 'name'] = filtered_data['name'].fillna('').astype(str)
    map_data = filtered_data[['reclat', 'reclong', 'name']].to_dict(orient='records')
    return jsonify(map_data)

@app.route('/submit_form', methods=['POST'])
def submit_form():
    # Process the form data
    itemtwo = request.form.get('itemtwo')
    itemone = request.form.get('itemone')
    new_inputs = request.form.getlist('new_input')
    location = request.form.get('location')
    lat, lng = location.split(',')
    lat, lng = float(lat), float(lng)

    # Add the new data point to the DataFrame
    new_row = {'itemone': itemone, 'year': itemtwo, 'reclat': lat, 'reclong': lng}
    global meteorite_df
    meteorite_df = pd.concat([meteorite_df, pd.DataFrame([new_row])], ignore_index=True)

    # Save the updated DataFrame to the CSV file
    meteorite_df.to_csv(data_file, index=False)

    # Filter the data frame based on the current category
    category = request.form.get('category', 'all')
    app.logger.info(request.form)
    if category == 'all':
        filtered_data = meteorite_df
    else:
        filtered_data = meteorite_df[meteorite_df['category'] == category]

    # Prepare the filtered data for the map
    map_data = filtered_data[['reclat', 'reclong', 'name']].to_dict(orient='records')
    app.logger.info(map_data)
    return jsonify(map_data)

@app.route('/get-timezones', methods=['GET'])
def get_timezones():
    # Return a list of timezones in JSON format
    timezones = pytz.common_timezones
    return jsonify(timezones)



if __name__ == '__main__':
    app.run(debug=True)