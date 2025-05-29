from flask import Flask
from database import close_db, init_db
from routes import main_bp, tree_bp, habit_bp

def create_app():
    """Application factory function"""
    app = Flask(__name__)
    
    # Register template filter
    from routes.main import state_to_text
    app.jinja_env.filters['state_text'] = state_to_text
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(tree_bp)
    app.register_blueprint(habit_bp)
    
    # Register teardown handler
    app.teardown_appcontext(close_db)
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        init_db()
    app.run(debug=True)