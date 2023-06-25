from flask import Flask


# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = "my secret key"

# Import blueprints
from views.main_table import main_table
from views.edit_table import edit_table
from error_handler.handlers import error_pages

# Register blueprints
app.register_blueprint(main_table)
app.register_blueprint(edit_table)
app.register_blueprint(error_pages)


if __name__ == "__main__":
    app.run(debug=True, port=8000)