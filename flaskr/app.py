from flask import Flask, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import folium
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

data_file = "flaskr/static/data/Meteorite_Landings_20240429.csv"
meteor_df = pd.read_csv(data_file)


# Define the form for submitting new locations
class LocationForm(FlaskForm):
	name = StringField('name') 
	year = StringField('year')
	location = StringField('location', validators=[DataRequired()])
	submit = SubmitField('Add Marker')

# Initialize the map
map = folium.Map(location=[meteor_df.reclat.mean(), meteor_df.reclong.mean()],zoom_start = 5, tiles="cartodb positron")

#add known data points
for index, location_info in meteor_df.iterrows():
	folium.Marker([location_info["reclat"], location_info["reclong"]], 
		popup=location_info["name"],
		icon=folium.Icon(color="red", icon="info-sign")
		).add_to(map)
# List to store submitted locations
locations = []


# Add the ClickForMarker plugin
click_for_marker = folium.ClickForMarker()
map.add_child(click_for_marker)
#User click to add marker to map and open form
mapJsVar = map.get_name()

map.get_root().html.add_child(folium.Element("""
<script type="text/javascript">
# $(document).ready(function() {
            

            {map}.on('click', function(e) {
                var lat = e.latlng.lat;
                var lon = e.latlng.lng;
				console.log(lat + ','+lon)
                $.ajax({
                    url: '/click_location',
                    type: 'POST',
                    data: {lat: lat, lon: lon},
                    success: function(data) {
						console.log(data.location+'sdjksjkdsjkhfsdjhdfs')
						console.log(document.getElementById('location-input'))
                        document.getElementById("location-input").value = data.location.toString();
                    }
                });
            });
        });
</script>
""".replace("{map}", mapJsVar)))


@app.route('/', methods=['GET', 'POST'])
def index():
	global meteor_df 
	form = LocationForm()

	#get map compenents to load
	map.get_root().render()
	header =  map.get_root().header.render()
	body_html = map.get_root().html.render()
	script = map.get_root().script.render()
	if form.validate_on_submit():
		location_str = form.location.data
		try:
			lat, lon = [float(x) for x in location_str.split(',')]
			if -90 <= lat <= 90 and -180 <= lon <= 180:
				location = (lat, lon)
				locations.append(location)
				form.location.data = ''  # Clear the form field

				# Add a marker for the new location
				folium.Marker(location=location, tooltip=location_str).add_to(map)
		except ValueError:
			# Handle invalid input format
			pass

	# Render the HTML template with the map and form
	map_html = map._repr_html_()
	return render_template('index.html', mapID=mapJsVar, form=form, map_html=map_html,header = header, body_html = body_html, script = script)

@app.route('/click_location', methods=['POST'])
def click_event():
    lat = float(request.form.get('lat'))
    lon = float(request.form.get('lon'))
    location_str = f"{lat},{lon}"
    print(location_str)
    return jsonify({'location': location_str})

if __name__ == '__main__':
	app.run(debug=True)
