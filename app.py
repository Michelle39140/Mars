# import dependencies
from flask import Flask, render_template, redirect
import pymongo
from scrape_mars import scrape
import os
# create Flask app
app = Flask(__name__)

conn = os.environ.get('MONGO_URL')
if not conn:
    conn = "mongodb://localhost:27017"
#conn = "mongodb://localhost:27017"
client = pymongo.MongoClient(conn)

db = client.mars_db
collection = db.info


# routes-------------------------------------------------------
@app.route("/")
def render():
    data = collection.find_one()
    return render_template("index.html",data=data)


@app.route("/scrape")
def scraping():
    data = scrape() # call scrape fucntion; store data returned from scraping
    collection.remove({}) # remove exsiting document in the collection
    collection.insert_one(data) # store retrived data into database as python dictionary
    return redirect("/") # redirect to be home page

# run the app
if __name__ == "__main__":
    app.run(debug=True)

