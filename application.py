# Webscrapper project

from flask import Flask, render_template,request, jsonify
from flask_cors import CORS, cross_origin
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
import pymongo

app = Flask(__name__)


@app.route('/', methods = ['GET'])
@cross_origin()
def home():
    return render_template('index.html')


@app.route('/review', methods = ['POST', 'GET'])
@cross_origin()
def computation():
    if (request.method == 'POST'):
        try:
            searchbar = request.form['content'].replace(" ", "")
            flipkart_search = 'https://www.flipkart.com/search?q=' + searchbar
            url_client = urlopen(flipkart_search)
            flipkart_link = url_client.read()
            url_client.close()
            flipkart_html = bs(flipkart_link,'html.parser')
            bigbox = flipkart_html.findAll("div",{"class":"_1AtVbE col-12-12"})
            del bigbox[0:3]
            box = bigbox[0]
            product_link = 'https://www.flipkart.com' + box.div.div.a['href'] 
            product_details = requests.get(product_link)
            product_details.encoding = 'utf-8'
            product_html = bs(product_details.text, 'html.parser')
            print(product_html)
            comment_box = product_html.find_all("div", {"class":"_16PBlm"})

            filename = searchbar + ".csv"
            fs = open(filename, "w")
            header = "Product, Customer Name, Rating, Heading, Comment \n"
            fs.write(header)
            reviews = []

            for i in comment_box:
                try:
                    # for extracting the names
                    name = i.div.div.find_all("p", {"class":"_2sc7ZR _2V5EHH"})[0].text 
                    
                except:
                    name = "No name"
                
                try:
                    # for extracting the rating
                    rating = i.div.div.div.find_all("div",{"class":"_3LWZlK _1BLPMq"})[0].text

                except:
                    rating = "No rating"

                try:
                    # for extracting the rating
                    commentHead = i.div.div.p.text

                except:
                    commentHead = "No comment head"

                try:
                    # for extracting the detail comment
                    detailcomment = i.div.div.find_all("div", {"class":""})[0].text   

                except:
                    detailcomment = "No detail comment" 

                mydict = {"Product": searchbar, "Name": name, "Rating": rating, "CommentHead":commentHead, "Comment":detailcomment}
                reviews.append(mydict)  
            
            client = pymongo.MongoClient("mongodb+srv://ketan_03:Ketan9856trader@cluster0.9epk8xo.mongodb.net/?retryWrites=true&w=majority")
            db = client["Webscrapper2"]
            coll_rec = db["Coll2_scrapper"]
            coll_rec.insert_many(reviews)

            return render_template('results.html', reviews = reviews[0:(len(reviews)-1)])

        except Exception as e:
            return "Something went wrong"

    else:
        return render_template('index.html')
            



if __name__ == "__main__":
    app.run(host= "127.0.0.1", port= 8000, debug=True)