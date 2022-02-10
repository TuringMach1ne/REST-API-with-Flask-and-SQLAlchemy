'''
    A simple Rest API demonstration coded from scratch using Flask and Restx
    @author:TuringMach1ne
'''

#Importing the required libraries
from flask import Flask, jsonify, request
from flask_restx import Api, Resource, fields
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

#define basedir for linking SQL Achemy DB URI
basedir=os.path.dirname(os.path.realpath(__file__))
#print(basedir)

#initiate the Flask instance
app = Flask(__name__)

#Establish SQL Alchemy connections
app.config["SQLALCHEMY_DATABASE_URI"]=\
    'sqlite:///'+os.path.join(basedir, 'books.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SQLALCHEMY_ECHO']=True


#Initiate API, add title and description to the webpage
api=Api(app,doc='/',title="A book API",description='A simple REST API for books')

#Initiate Database, and build upon Flask instance
db=SQLAlchemy(app)
class Book(db.Model):
    '''Model for Book instances in the DataBase'''
    id=db.Column(db.Integer(),primary_key=True)
    title=db.Column(db.String(90),nullable=False)
    author=db.Column(db.String(75),nullable=False)
    date_added=db.Column(db.DateTime(),
    default=datetime.utcnow)
    
    #Function for the string representation of the objent, otherwise it's a DB Object
    def __repr__(self):
        return self.title

#Model skeleton for the RESTx
book_model=api.model(
    'Book',
    {
        'id':fields.Integer(),
        'title':fields.String(),
        'author':fields.String(),
        'date_joined':fields.String()
    }
)


#API Route Decorator for the webpage
@api.route('/books')
class Books(Resource):
    '''Class for the Books page, which contains all information altogether.'''

    #This swagger decoration helps with documenting
    #Code 200 (okay) will be returned with books envelope
    @api.marshal_list_with(book_model,code=200,envelope='books')
    def get(self):
        '''Get all Books'''
        books=Book.query.all() #Basic query that 'GET's everything
        return books
    
    @api.marshal_with(book_model,code=201,envelope='book')
    #Another Swagger decoration below for improving the UI/UX
    @api.expect(book_model)
    def post(self):
        '''Create a new Book'''
        data=request.get_json() #User will be asked to provide JSON
        title=data.get('title') #User will be asked to provide a title
        author=data.get('author') #User will be asked to provide a title

        #Creating the Book instance upon user input
        new_book=Book(title=title,author=author)

        db.session.add(new_book) #adding to existing DB
        db.session.commit()     #committing the changes to the DB

        return new_book


#Dynamic route decorator, the page will have unique branches for each book created.
@api.route('/book/<int:id>')
class BookResource(Resource):
    '''Each individual book entry to DB'''
    @api.marshal_with(book_model,code=200,envelope='book')
    def get(self,id):
        '''Get one Book by id'''
        book=Book.query.get_or_404(id) #if not found, will return HTTP 404
        return book
    
    @api.marshal_with(book_model, code=200,envelope='book')
    def put(self,id):
        '''Update a book'''
        book_to_update = Book.query.get_or_404(id) #GET by id, if not found, will return HTTP 404

        data=request.get_json() # user will be asked to provide JSON

        book_to_update.title=data.get('title') #changing respective book's title
        book_to_update.author=data.get('author') #changing respective book's author
        db.session.commit() #committing the changesw to the DB
        return book_to_update,200 #Return 200 Okay so the user knows it's updated.
    
    @api.marshal_with(book_model, code=200, envelope='bookdeleted')
    def delete(self,id):
        '''Delete a book'''
        book_to_delete=Book.query.get_or_404(id)
        db.session.delete(book_to_delete)
        db.session.commit()

        return book_to_delete,200 #Return 200 Okay so the user knows it's deleted.


#Decorator and Function for testing/experimenting on IPython Shell
@app.shell_context_processor
def make_shell_context():
    return {
        'db':db,
        'Book':Book
    }

if __name__ == "__main__":
    app.run(debug=True) # Debug mode must be off when deployed!
