from recomendations.recomendator import Recomendator
from flask import Flask, request, jsonify,render_template,Response,json
import pandas as pd
import pickle
import ssl,os
MAL_CLIENT_ID = ""
with open(".env","r") as f:
    for line in f:
        key,value = line.split("=")
        os.environ[key] = value.strip()

        MAL_CLIENT_ID = value.strip()
        


context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)


context.load_cert_chain(r'C:\Certbot\live\ian.ibalton.com\fullchain.pem',r'C:\Certbot\live\ian.ibalton.com\privkey.pem')




app = Flask(__name__)
with open("recomendator.pkl","rb") as f:
    recomendator:Recomendator = pickle.load(f)
@app.route("/api/recommendations/user/<user>", methods=["GET"])
def get_recommendations(user):
    
    recommendations = recomendator.get_recommendations_with_info(user)
    response = Response(
        response=json.dumps({"res": recommendations}, ensure_ascii=False),
        status=200,
        mimetype='application/json'
    )
    response.headers["Content-Type"] = "application/json; charset=utf-8" 
    return response

@app.route("/api/recommendations/manga/<manga>", methods=["GET"])
def get_manga_recommendations(manga):
    recommendations: pd.DataFrame = recomendator.recommend_by_genres.get_recommendations(manga, n=10, include_series=False)
    recommendations = recommendations.where(pd.notnull(recommendations), None)
    
    response = Response(
        response=json.dumps({"res": recommendations.to_dict(orient="records")}, ensure_ascii=False),
        status=200,
        mimetype='application/json'
    )
    response.headers["Content-Type"] = "application/json; charset=utf-8"  # Specify the encoding here
    return response

@app.route("/api/manga-thumbnail/<mangaId>", methods=["GET"])
def get_manga_thumbnail(mangaId):

    url = getMangaUrl(mangaId)
    recomendator.set_manga_thumnail(mangaId, url)
    response = Response(
        response=json.dumps({"res": url}, ensure_ascii=False),
        status=200,
        mimetype='application/json'
    )
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@app.route("/")
def main():
    return render_template("./index.html")

import requests
from lxml import html

def getMangaUrl(mangaId):
    url = f"https://api.myanimelist.net/v2/manga/{mangaId}"
    
    # Send a GET request to the URL
    response = requests.get(url,headers={"X-MAL-CLIENT-ID":MAL_CLIENT_ID})
    
    res = response.json()
    url = res["main_picture"]["medium"]
    return url

if __name__ == '__main__':  
     print("mal key:",MAL_CLIENT_ID)
     app.run(host='0.0.0.0', debug=True, ssl_context=context)