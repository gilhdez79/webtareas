# -*- coding: utf-8 -*-

from flask   import Flask, render_template, url_for, redirect, request, flash
import requests
import json
import ast
from flask_bootstrap import Bootstrap
import secrets
import arrow
import time
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
import numpy as np
import pandas as  pd
from pandas import DataFrame, Series
from pandas.io.json import json_normalize
from jinja2 import Environment, PackageLoader, select_autoescape
import jinja2
from config import Config



app = Flask(__name__)
Bootstrap(app)

def datetimeformat(value, format= '%H:%M / %d-%m-%Y'):
    return value.strftime(format)

#env.filters["datetimeformat"]= datetimeformat
#jinja2.filters.FILTERS['datetimeformat'] = datetimeformat

context={
    'now':int(time.time()),
    'strftime': time.strftime,
    'arrowget': arrow.get
}

# urlAPI  = 'http://localhost:5001/api/tarea/'

configuracion = Config()
urlAPI = configuracion.UrlApIProd();
secret = secrets.token_urlsafe(32)

app.secret_key = secret

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/blogs', methods=['POST','GET'])
def blogs():
    id_tarea = request.args.get('id_tarea', default='', type=str)
    print(id_tarea)
    _data ={"id_tarea":"T01"}
    response= requests.get(urlAPI, data=_data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    if request.method == 'GET':
        print(response.json())
    return render_template('blogs.html', blog_id=id)

@app.route('/register', methods=["GET", "POST"])
def register():
    return render_template('register.html')

@app.route('/viewtable', methods=["GET"])
def viewtable():
    response= requests.get(urlAPI + 'all')
    data = response.json();


    # flash('Ejemplo de Mensajes',"danger")
    return render_template('viewtable.html', rows= data,  tituloTarea = "Todas las Tareas" ,**context)
# Obteneer las tareas compleadas
@app.route('/getstatus/<status>', methods=["GET", "POST"])
def getstatus(status):
    # flash('Ejemplo de Mensajes',"danger")
    _data = status
    response= requests.get(urlAPI + 'getstatus/'+_data, headers={"Content-Type": "application/json"})
    data = response.json();

    titulo = ""
    if status == "1":
        titulo= "Tareas Completadas"
    if status == "0":
        titulo = "Tareas Pendiendes"
    # flash('Ejemplo de Mensajes',"danger")
    return render_template('viewtable.html', rows= data,tituloTarea = titulo, **context)
# Obteneer las tareas compleadas

@app.route('/editar/<item>', methods=["GET", "POST"])
def editar(item):
# flash('Ejemplo de Mensajes',"danger")

     data= json.dumps(item)
     data2 = ast.literal_eval(item)
     ffecha =  arrow.get(data2['fecha'])
     data2['fecha'] = ffecha.format('YYYY/MM/DD')
     print(data2['id_tarea'])
     print( data2['fecha'])
     print(data2)
     print("Type of deserialized data: ", type(data2))
    # print(data)
     return render_template('editar.html', id_tarea = data2, **context)

 # Eliminar
@app.route('/eliminar/<item>', methods=["GET", "POST"])
def eliminar(item):
 # flash('Ejemplo de Mensajes',"danger")

      data= json.dumps(item)
      data2 = ast.literal_eval(item)
      ffecha =  arrow.get(data2['fecha'])
      data2['fecha'] = ffecha.format('YYYY/MM/DD')
      print(data2['id_tarea'])
      print( data2['fecha'])
      print(data2)
      print("Type of deserialized data: ", type(data2))

      response= requests.delete(urlAPI + "delete", data=data2, headers={"Content-Type": "application/x-www-form-urlencoded"})
     # print(data)
      return render_template('editar.html', id_tarea = data2, **context)

 # Guardar en la BD
@app.route('/update_data', methods=['POST'])
def update_data():
    print('-----------Editar---------');
    projectpath = request.form["txtTarea"]
    print(projectpath)
    print(request.form['txtDescipcion'])
    print(request.form['txtFecha'])
    print(request.form['txtHora'])
    completo=0
    if  request.form['chkCompletado'] == 'on':
        completo=1

    _data = {
        'id_tarea':request.form["txtTarea"],
        'descripcion':request.form['txtDescipcion'],
        'fecha': request.form['txtFecha'],
        'duracion': request.form['txtHora'],
        'completo': completo
    }

    # Actualizamos los datos
    response= requests.put(urlAPI, data=_data, headers={"Content-Type": "application/x-www-form-urlencoded"})

    return render_template('index.html')
# Guardar en la BD
@app.route('/insert_data', methods=['POST'])
def insert_data():
   print('-----------Editar---------');
   projectpath = request.form["txtTarea"]
   print(projectpath)
   print(request.form['txtDescipcion'])
   print(request.form['txtFecha'])
   print(request.form['txtHora'])

   _data = {
       'id_tarea':request.form["txtTarea"],
       'descripcion':request.form['txtDescipcion'],
       'fecha': request.form['txtFecha'],
       'duracion': request.form['txtHora']
   }
   # Actualizamos los datos
   response= requests.post(urlAPI+ 'registra', data=_data, headers={"Content-Type": "application/x-www-form-urlencoded"})
   return render_template('index.html')

# Graficar
@app.route('/graficas')
def graficas():
    #Traer Todos los Datos

    response= requests.get(urlAPI + 'all')
    data = response.json();

    df = DataFrame.from_dict(data)
    z = df.query('completo == 1' )[['tiempocomp','id_tarea']]

    yvalue = z["tiempocomp"].head()
    ymap=yvalue.map(lambda x: int(x))
    yl = list(set(ymap))

    auxData = z['id_tarea'].head()
    x= auxData.map(lambda x: str(x))
    xl=  list(set(x.sort_values(ascending=True)))
    x =xl
    colors = ["#c9d9d3", "#718dbf", "#e84d60"]
    fig = figure(x_range=x, plot_width=900, plot_height=600,
                 x_axis_label='Tareas', y_axis_label='Tiempo',
                 title="Tareas Completadas",toolbar_location=None, tools="")
    fig.vbar(
        x= x,
        width=0.7,
        bottom=0,
        top=yl,
        color=colors

    )

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    script, div = components(fig)
    html = render_template(
        'grafica.html',
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,
    )
    return (html)

if __name__ == '__main__':
    app.run(debug=True)
