

import code
from telnetlib import XAUTH
from werkzeug.utils import secure_filename
import jinja_partials
from flask import Flask, abort, redirect, render_template, request, url_for, jsonify, send_from_directory, flash
import pybase64
import uuid
import os
import time
import json

from .ImageAI import createImage, getPrompt_from_GeminiAI, getImage_from_openai

UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


feeds = {
    "https://blog.teclado.com/rss/": {"title": "The Teclado Blog", "href": "https://blog.teclado.com/rss/", "show_images": True, "entries": {}}
}

# def create_login(app):
#     @app.route("/login")
#     def render_login(feed_url: str = None):
#         return render_template("login.html")

path_cache = "static/cache"
# path_cache = "app/static/uploads"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_images(request):
    files = request.files.getlist("file") 
    
    # Iterate for each file in the files List, and Save them 
    temp = ""
    data = []
    for file in files: 

        temp += f"{file.filename} " 
        content = pybase64.b64encode(file.read())
        data.append(content.decode("utf-8"))

        # save images temporarily
        file.save(f'{path_cache}/{file.filename}') 

    return data, temp

def get_images(request, my_uuid):
    files = request.files.getlist("file") 
    
    # Iterate for each file in the files List, and Save them 
    temp = ""
    data = []
    for file in files: 

        temp += f"{file.filename} " 
        content = pybase64.b64encode(file.read())
        data.append(content.decode("utf-8"))

        # save images temporarily
        wkdir = os.path.join(path_cache, str(my_uuid))
        os.mkdir(wkdir)         
        # f2s = os.path.join(wkdir,file.filename)
        f2s = os.path.join(wkdir,"wrong.png")
        print(f"wkdir: {wkdir}")
        print(f"filedir: {f2s}")

        file.save(f2s) 

        # os.mkdir(f'{path_cache}/{my_uuid}')         
        # file.save(f'{path_cache}/{my_uuid}/{file.filename}') 

    return data, temp


def get_images2(files, my_uuid):
    # wkdir = os.path.join(path_cache, str(my_uuid))
    wkdir = f"app/{path_cache}/{str(my_uuid)}"
    wkdir_display = f"{path_cache}/{str(my_uuid)}"
    os.mkdir(wkdir)

    data = []
    image_info = []
    
    for file in files: 
        filename = secure_filename(file.filename)
        fdata = file.read()
        content = pybase64.b64encode(fdata)
        data.append(content)

        print(f"get image: {filename} {len(content)}")

        # save images
        # f2s = os.path.join(wkdir,filename)
        f2s = f"{wkdir}/{filename}"
        with open(f2s, 'wb') as x:
            # Write content to the file
            x.write(fdata)

        # render templating
        image_info.append({
            "image_save": f2s,
            "image_loc": f"{wkdir_display}/{filename}", # diregard app/
            "image_filename": filename,
            "content_base64": content
        })

    return data, image_info

def display_get_imageresponsive(image_info):
    # split images into iflag columns
    imagelen = len(image_info)
    row_responsive = "w3-third" 
    iflag = 3
    if imagelen < 6:
        row_responsive = "w3-half"
        iflag = 2

    tempf = []
    image_categ = [ [] for x in range(iflag) ]
    for i in range(imagelen):
        tempf = image_categ[i % iflag]
        tempf.append(image_info[i])

    return image_categ, row_responsive

def create_app():
    # app = Flask(__name__)
    app = Flask(__name__)    
    # app.config['UPLOAD_FOLDER'] = path_cache


    jinja_partials.register_extensions(app)

    # modified
    @app.route('/') 
    def main3(): 
        return render_template("upload3.html") 


    @app.route("/login")
    def render_login(feed_url: str = None):
        return render_template("login.html")

    @app.route('/generate') 
    def main(): 
        return render_template("upload.html") 

    @app.route('/upload', methods=['POST']) 
    def upload(): 
        if request.method == 'POST': 
    
            # Get the list of files from webpage 
            files = request.files.getlist("file") 

            temp = ""
            data = []
            for file in files: 

                temp += f"{file.filename} " 
                fdata = file.read()
                print(f"filelen: {len(fdata)}")
                content = pybase64.b64encode(fdata)
                data.append(content.decode("utf-8"))
                

            res = getPrompt_from_GeminiAI(data)
            image_final = getImage_from_openai(res)

            return f"<h1>Files Uploaded Successfully.! {temp}</h1><br><p>{len(data)} / {res}<br><img src='{image_final['data'][0]['url']}' alt='Image'></p>"



    @app.route('/error', methods=['GET']) 
    def error(): 
        return f"<h1>Error Found!</h1>"


    @app.route('/generate2') 
    def main2(): 
        return render_template("upload2.html") 

    @app.route('/upload2', methods=['POST']) 
    def upload2(): 
        error_url = "/error"
        if request.method == 'POST': 

            if 'file' not in request.files:
                # flash('No file part')
                return redirect(error_url)

            files = request.files.getlist("file") 
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            for file in files: 
                print(f"precheck: {file.filename}")
                if file.filename == '' or not allowed_file(file.filename):
                    # if file.filename == '':
                    #     flash('No selected file')
                    # else:
                    #     flash(f'Wrong file format: {file.filename}')
                    return redirect(error_url)

            
            my_uuid = uuid.uuid1()        
            data, image_info =  get_images2(files, my_uuid)
            image_categ, row_responsive = display_get_imageresponsive(image_info)
            
            ii = {
                "uuid": my_uuid,
                "row_responsive": row_responsive
            }
            return render_template("output2.html", image_info=ii, image_categ=image_categ)


    @app.route('/uploads/<path:uuid>/<path:filename>')
    def download_file(uuid, filename):
        # xx = "../../cache"
        # xx = "C:\\Users\\felix.m.jusay\\Desktop\\brave\\github\\bravetailoring\\app\\cache"
        xx = "C:/Users/felix.m.jusay/Desktop/brave/github/bravetailoring/app/cache"
        cpath = f"{xx}/{uuid}/{filename}"
        print(f"download_file: {cpath}")
        return send_from_directory(cpath, filename, as_attachment=True)


    @app.route('/loading/<path:my_uuid>')
    def loading(my_uuid):
        print(f"myuuid: {my_uuid}")

        files = os.listdir(f"app/{path_cache}/{my_uuid}")
        data = []
        for f in files:
            fp = f"app/{path_cache}/{my_uuid}/{f}"
            with open(fp, "rb") as fimage: 
                xd = fimage.read()
                xd = pybase64.b64encode(xd)
                data.append(xd.decode("utf-8"))
                print(f"{f}: {len(xd)}")

        res = getPrompt_from_GeminiAI(data)
        image_final = getImage_from_openai(res)
        
        return f"<p>Prompt: {res}<br><img src='{image_final['data'][0]['url']}' alt='{image_final['data'][0]['url']}'></p>"

    return app



    # reference
    # https://www.geeksforgeeks.org/upload-multiple-files-with-flask/