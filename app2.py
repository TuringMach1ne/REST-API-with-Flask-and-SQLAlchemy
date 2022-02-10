'''
    A simple Rest API demonstration coded from scratch using Flask, Restx and SQLAlchemy
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
app.config["SQLALCHEMY_DATABASE_URI"]='sqlite:///'+os.path.join(basedir, 'recipes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SQLALCHEMY_ECHO']=True


#Initiate API, add title and description to the webpage
api=Api(app,doc='/',title="A Recipe API",description='A simple REST API for stroing,accessing and modifying Recipes')

#Initiate Database, and build upon Flask instance
db=SQLAlchemy(app)
class Recipe(db.Model):
    '''Model for recipe instances in the DataBase'''
    id=db.Column(db.Integer(),primary_key=True) # Primary Key ID will be assigned automatically
    title=db.Column(db.String(90),nullable=False) #Title of the recipe must be String
    ingredients=db.Column(db.Text(),nullable=False)
    dates_made=db.Column(db.Text(),
    default=str(datetime.utcnow))
    
    #Function for the string representation of the object, otherwise it's a DB Object
    def __repr__(self):
        return self.title

#Model skeleton for the RESTx
recipe_model=api.model(
    'Recipe',
    {
        'id':fields.Integer(),
        'title':fields.String(),
        'ingredients':fields.String(),
        'dates_made':fields.String()
    }
)


#API Route Decorator for the webpage
@api.route('/recipes')
class Recipes(Resource):
    '''Class for the Recipes page, which contains all information altogether.'''

    #This swagger decoration helps with documenting
    #Code 200 (okay) will be returned with recipes envelope
    @api.marshal_list_with(recipe_model,code=200,envelope='recipes')
    def get(self):
        '''Get all Recipes'''
        recipes=Recipe.query.all() #Basic query that 'GET's everything
        return recipes
    
    @api.marshal_with(recipe_model,code=201,envelope='recipe')
    #Another Swagger decoration below for improving the UI/UX
    @api.expect(recipe_model)
    def post(self):
        '''Create a new recipe'''
        data=request.get_json() #User will be asked to provide JSON
        title=data.get('title') #User will be asked to provide a title
        ingredients=data.get('ingredients') #User will be asked to provide a title

        #Creating the recipe instance upon user input
        new_recipe=Recipe(title=title,ingredients=ingredients)

        db.session.add(new_recipe) #adding to existing DB
        db.session.commit()     #committing the changes to the DB

        return new_recipe


#Dynamic route decorator, the page will have unique branches for each recipe created.
@api.route('/recipe/<int:id>')
class RecipeResource(Resource):
    '''Each individual recipe entry to DB'''
    @api.marshal_with(recipe_model,code=200,envelope='recipe')
    def get(self,id):
        '''Get a Recipe by id'''
        recipe=Recipe.query.get_or_404(id) #if not found, will return HTTP 404
        return recipe
    
    @api.marshal_with(recipe_model, code=200,envelope='recipe')
    def put(self,id):
        '''Update a recipe'''
        recipe_to_update = Recipe.query.get_or_404(id) #GET by id, if not found, will return HTTP 404

        data=request.get_json() # user will be asked to provide JSON

        recipe_to_update.title=data.get('title') #changing respective recipe's title
        recipe_to_update.ingredients=data.get('ingredients') #changing respective recipe's ingredients
        db.session.commit() #committing the changes to the DB
        return recipe_to_update,200 #Return 200 Okay so the user knows it's updated.
    
    @api.marshal_with(recipe_model, code=200, envelope='recipe_deleted')
    def delete(self,id):
        '''Delete a recipe'''
        recipe_to_delete=Recipe.query.get_or_404(id)
        db.session.delete(recipe_to_delete)
        db.session.commit()

        return recipe_to_delete,200 #Return 200 Okay so the user knows it's deleted.


#Decorator and Function for testing/experimenting on IPython Shell
@app.shell_context_processor
def make_shell_context():
    return {
        'db':db,
        'Recipe':Recipe
    }

if __name__ == "__main__":
    app.run(debug=True) # Debug mode must be off when deployed!