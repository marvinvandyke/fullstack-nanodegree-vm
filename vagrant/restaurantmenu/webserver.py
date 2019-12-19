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
        output+='''<a href='/restaurants/%s/edit'>Edit</a>''' % restaurantItem.id
        output+="<br>"
        output+='''<a href='/restaurants/%s/delete'>Delete</a>''' % restaurantItem.id

    output+="<br>"
    output+='''<a href='/restaurants/new'><h1>Create new restaurant...</h1></a>'''
    output+="</body></html>"
    self.wfile.write(output)
    print(output)
    return

def deleteRestaurant(self):
    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()

    arguments = str.split(self.path, "/")
    restaurantid = int
    for arg in arguments:
        if arg.isdigit():
            restaurantid=int(arg)

    restaurantName = session.query(Restaurant).get(restaurantid).name

    output = ""
    output+="<html><body>"
    output+='''<form method="POST" action="/restaurants/%s/delete" enctype="multipart/form-data"> 
                     Really delete %s?<br>
                    <input type="submit" value="Confirm">
                </form>''' % (restaurantid, restaurantName)
    output+="</body></html>"
    self.wfile.write(output)

    return

def editRestaurant(self):
    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()

    print(self.path)
    arguments = str.split(self.path, "/")
    restaurantid = int
    for arg in arguments:
        if arg.isdigit():
            restaurantid=int(arg)

    print(restaurantid)
    restaurantName = session.query(Restaurant).get(restaurantid).name
    
    output = ""
    output+="<html><body>"
    output+='''<form method="POST" action="/restaurants/%s/edit" enctype="multipart/form-data"> 
                     Change %s to new name:<br>
                    <input type="text" name="newRestaurantName">
                    <br>
                    <input type="submit" value="Change">
                </form>''' % (restaurantid, restaurantName)
    output+="</body></html>"
    self.wfile.write(output)

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

            if self.path.endswith("/edit"):
                editRestaurant(self)
                return

            if self.path.endswith("/delete"):
                deleteRestaurant(self)
                return

        except IOError:
            self.send_error(404, "File not found %s" % self.path)

    def do_POST(self):
        try:
            self.send_response(301)
            self.send_header('Content-type', 'text/html')
            self.send_header('Location', '/restaurants')
            self.end_headers()

            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                fields=cgi.parse_multipart(self.rfile, pdict)

                restaurantcontent=fields.get('restaurant')
                print(restaurantcontent)
                if restaurantcontent != None:
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

                newRestaurantNameContent=fields.get('newRestaurantName')
                print(newRestaurantNameContent)
                if newRestaurantNameContent != None:
                    print("newRestaurantName")

                    arguments = str.split(self.path, "/")
                    restaurantid = int
                    for arg in arguments:
                        if arg.isdigit():
                            restaurantid=int(arg)

                    print(restaurantid)

                    output = ""
                    output+="<html><body>"
                    output+='''<form method="POST" action="/restaurants/%s/edit" enctype="multipart/form-data"> 
                                    Change %s to new name:<br>
                                    <input type="text" name="newRestaurantName">
                                    <br>
                                    <input type="submit" value="Change">
                                </form>''' % (restaurantid, newRestaurantNameContent[0])
                    output+="</body></html>"

                    rtc = session.query(Restaurant).get(restaurantid)
                    rtc.name = newRestaurantNameContent[0]
                    session.commit()

                    self.wfile.write(output)
                    print(output)
                    return

                arguments = str.split(self.path, "/")
                restaurantid = int
                for arg in arguments:
                    if arg.isdigit():
                        restaurantid=int(arg)

                if self.path.endswith("/delete"):
                    print("inside")
                    rtc = session.query(Restaurant).get(restaurantid)
                    print(rtc.name)
                    session.delete(rtc)
                    session.commit()
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