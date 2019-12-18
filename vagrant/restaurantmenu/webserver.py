from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
import cgi

engine=create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind=engine
DBSession=sessionmaker(bind=engine)
session = DBSession()

def listRestaurants(self):
    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()

    restaurantItems = session.query(Restaurant).all()
    output=""
    output+="<html><body>"

    for restaurantItem in restaurantItems:
        output+="<h1> %s </h1>" % restaurantItem.name
        output+='''<a href='/restaurants/edit'>Edit</a>'''
        output+="<br>"
        output+='''<a href='/restaurants/delete'>Delete</a>'''

    output+="<br>"
    output+='''<a href='/restaurants/new'><h1>Create new restaurant...</h1></a>'''
    output+="</body></html>"
    self.wfile.write(output)
    print(output)
    return

def createNewRestaurant(self):
    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()

    output = ""
    output+="<html><body>"
    output+='''<form method="POST" action="/restaurants/new" enctype="multipart/form-data">
                     Restaurant name:<br>
                    <input type="text" name="restaurant">
                    <br>
                    <input type="submit" value="Create new">
                </form>'''
    output+="</body></html>"
    self.wfile.write(output)
    print(output)

    return

class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:

            if self.path.endswith("/restaurants"):
                listRestaurants(self)
                return

            if self.path.endswith("/restaurants/new"):
                createNewRestaurant(self)
                return

        except IOError:
            self.send_error(404, "File not found %s" % self.path)

    def do_POST(self):
        try:
            self.send_response(301)
            self.end_headers()

            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                fields=cgi.parse_multipart(self.rfile, pdict)

                restaurantcontent=fields.get('restaurant')
                print(restaurantcontent)
                if len(restaurantcontent) > 0:
                    print("restaurant")
                    output = ""
                    output+="<html><body>"
                    output+='''<form method="POST" action="/restaurants/new" enctype="multipart/form-data">
                                    Restaurant name:<br>
                                    <input type="text" name="restaurant">
                                    <br>
                                    <input type="submit" value="Create new">
                                </form>'''
                    output+="</body></html>"

                    restaurant1 = Restaurant(name=restaurantcontent[0])
                    session.add(restaurant1)
                    session.commit()

                    self.wfile.write(output)
                    print(output)
                    return

        except:
            pass

def main():
    try:
        port=8080
        server = HTTPServer(('', port), webServerHandler)
        print ("Web server running on port %s" % port)
        server.serve_forever()

    except KeyboardInterrupt:
        print ("^C entered, stopping web server...")
        server.socket.close()

if __name__ == '__main__':
    main()