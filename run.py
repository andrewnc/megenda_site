import os
from flask import render_template
from app import create_app


config_name = os.getenv("FLASK_CONFIG")
app = create_app(config_name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
	app.run()