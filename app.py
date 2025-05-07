from flask import Flask, redirect, url_for
from blueprints.auth import auth_bp
from blueprints.home import home_bp
from blueprints.studio import studio_bp
from blueprints.furniture import furniture_bp
from blueprints.designs import designs_bp
from blueprints.checkout import checkout_bp
from blueprints.profile import profile_bp
from blueprints.testing import testing_bp
from blueprints.catalog import catalog_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = "super-secret-key"

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(studio_bp)
    app.register_blueprint(furniture_bp)
    app.register_blueprint(designs_bp)
    app.register_blueprint(checkout_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(testing_bp)
    app.register_blueprint(catalog_bp)

    # Fallback root redirect to home
    @app.route("/")
    def root():
        return redirect(url_for("home_bp.home"))

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)