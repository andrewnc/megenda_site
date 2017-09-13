import os
from flask import render_template
from app import create_app

config_name = os.getenv("FLASK_CONFIG")
app = create_app(config_name)


# error page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

if __name__ == "__main__":
	app.run()