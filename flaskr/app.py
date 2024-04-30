from flask import Flask, render_template, request
import folium
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

class LocationForm(FlaskForm):
    location = StringField('Location', validators=[DataRequired()])
    submit = SubmitField('Show Map')

@app.route('/',methods=['GET', 'POST'])
def index():
    form = LocationForm()
    if form.validate_on_submit():
        location = form.location.data
        map = folium.Map(location=[0, 0], zoom_start=2)
        folium.Marker([0, 0], popup=location).add_to(map)
        map = map._repr_html_()
        return render_template('index.html', form=form, map=map, location = location)
    return render_template('index.html', form=form, map=None, location = None)

# @app.route('/map', methods=['POST'])
# def show_map():
#     location = request.form['location']
#     map = folium.Map(location=[0, 0], zoom_start=2)
#     folium.Marker([0, 0], popup=location).add_to(map)
#     map.save('templates/map.html')
#     return render_template('map.html')
if __name__ == '__main__':
    app.run(debug=True)