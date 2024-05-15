

import feedparser
import jinja_partials
from flask import Flask, abort, redirect, render_template, request, url_for, jsonify
import pybase64
import json
from .ImageAI import createImage, getPrompt_from_GeminiAI, getImage_from_openai


# feeds = {
#     "https://blog.teclado.com/rss/": {"title": "The Teclado Blog", "href": "https://blog.teclado.com/rss/", "show_images": True, "entries": {}},
#     "https://www.joshwcomeau.com/rss.xml": {"title": "Josh W. Comeau", "href": "https://www.joshwcomeau.com/rss.xml", "show_images": False, "entries": {}},
# }

feeds = {
    "https://blog.teclado.com/rss/": {"title": "The Teclado Blog", "href": "https://blog.teclado.com/rss/", "show_images": True, "entries": {}}
}

# def create_login(app):
#     @app.route("/login")
#     def render_login(feed_url: str = None):
#         return render_template("login.html")


def create_app():
    app = Flask(__name__)
    jinja_partials.register_extensions(app)


    # default configs
    @app.route("/feed/")
    @app.route("/feed/<path:feed_url>")
    def render_feed(feed_url: str = None):

        for url, feed_ in feeds.items():
            parsed_feed = feedparser.parse(url)
            for entry in parsed_feed.entries:
                if entry.link not in feed_["entries"]:
                    feed_["entries"][entry.link] = {**entry, "read": False}

        if feed_url is None:
            feed = list(feeds.values())[0]
        else:
            feed = feeds[feed_url]
        return render_template("feed.html", feed=feed, feeds=feeds)


    @app.route("/entries/<path:feed_url>")
    def render_feed_entries(feed_url: str):
        try:
            feed = feeds[feed_url]
        except KeyError:
            abort(400)
        page = int(request.args.get("page", 0))

        # Below we're paginating the entries even though
        # in this application it's not necessary, just to
        # show what it might look like if it were.
        return render_template(
            "partials/entry_page.html",
            entries=list(feed["entries"].values())[page*5:page*5+5],
            href=feed["href"],
            page=page,
            max_page=len(feed["entries"])//5
        )
    
    @app.route("/add_feed", methods=["POST"])
    def add_feed():
        feed = request.form.get("url")
        title = request.form.get("title")
        show_images = request.form.get("showImages")
        feeds[feed] = {"title": title, "href": feed, "show_images": show_images, "entries": {}}
        return redirect(url_for("render_feed", feed=feed))

    @app.route("/feed/<path:feed_url>/entry/<path:entry_url>")
    def read_entry(feed_url: str, entry_url: str):
        feed = feeds[feed_url]
        entry = feed["entries"][entry_url]
        entry["read"] = True
        return redirect(entry_url)


    # modified
    @app.route("/login")
    def render_login(feed_url: str = None):
        return render_template("login.html")

    # @app.route("/generate", methods=["POST"])
    # def generate():
    #     feed = request.form.get("url")
    #     title = request.form.get("title")
    #     show_images = request.form.get("showImages")
    #     feeds[feed] = {"title": title, "href": feed, "show_images": show_images, "entries": {}}
    #     return redirect(url_for("render_feed", feed=feed))

    @app.route('/generate') 
    def main(): 
        return render_template("upload.html") 

    @app.route('/upload', methods=['POST']) 
    def upload(): 
        if request.method == 'POST': 
    
            # Get the list of files from webpage 
            files = request.files.getlist("file") 
    
            # Iterate for each file in the files List, and Save them 
            temp = ""
            data = []
            for file in files: 

                temp += f"{file.filename} " 
                content = pybase64.b64encode(file.read())
                data.append(content.decode("utf-8"))
            
            res = getPrompt_from_GeminiAI(data)
            image_final = getImage_from_openai(res)

            # return f"<h1>Files Uploaded Successfully.! {temp}</h1><br><p>{res}</p><br>{image_final}"
            return f"<h1>Files Uploaded Successfully.! {temp}</h1><br><p>{len(data)} / {res}<br><img src='{image_final['data'][0]['url']}' alt='Image'></p>"

    # @app.route('/upload', methods=['POST'])
    # def upload_images():
    #     # Check if the POST request has the file part

    #     # print(f"request: {jsonify(request.form)}")

    #     if 'files[]' not in request.files:
    #         return jsonify({'error': 'No file part'}), 400

    #     files = request.files.getlist('files[]')

    #     if len(files) == 0:
    #         return jsonify({'error': 'No files selected for upload'}), 400

    #     # Save uploaded files to a folder or perform further processing
    #     # Example: Save uploaded files to the 'uploads' folder
    #     uploaded_filenames = []
    #     for file in files:
    #         filename = file.filename
    #         file.save(f'uploads/{filename}')
    #         uploaded_filenames.append(filename)

    #     return jsonify({'message': f'{len(uploaded_filenames)} file(s) uploaded successfully', 'files': uploaded_filenames}), 200

    return app



    # reference
    # https://www.geeksforgeeks.org/upload-multiple-files-with-flask/