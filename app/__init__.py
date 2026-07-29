from flask import Flask, request
from flask_login import current_user
from config.config import config
from app.extensions import db, migrate, login_manager, csrf, limiter, talisman, cache, csp
from app.celery_utils import make_celery
from app.core.tenancy import setup_tenancy_events

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Configure Limiter
    limiter.init_app(app)
    if app.config.get('CACHE_REDIS_URL'):
        limiter.storage_uri = app.config['CACHE_REDIS_URL']
        
    # Disable force_https if not in production to allow local HTTP testing
    force_https = app.config.get('ENV') == 'production'
    talisman.init_app(app, content_security_policy=csp, force_https=force_https)
    cache.init_app(app)
    
    # Initialize Celery
    make_celery(app)
    
    # Initialize tenancy events (Enforce isolation)
    setup_tenancy_events(db)

    # Set tenant context
    @app.before_request
    def set_tenant_context():
        from app.core.tenancy import set_current_tenant
        if current_user and current_user.is_authenticated:
            set_current_tenant(current_user.tenant_id)
        elif app.config.get('TESTING') and 'X-Tenant-ID' in request.headers:
            set_current_tenant(request.headers.get('X-Tenant-ID'))

    # Provide current year to all templates
    @app.context_processor
    def inject_now():
        from datetime import datetime, UTC
        return {'now': datetime.now(UTC)}

    # Register Blueprints
    from app.blueprints.superadmin import superadmin_bp
    app.register_blueprint(superadmin_bp, url_prefix='/superadmin')

    # Register CLI commands
    from app.commands import make_superadmin
    app.cli.add_command(make_superadmin)

    from app.blueprints.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from app.blueprints.metadata import metadata_bp
    app.register_blueprint(metadata_bp, url_prefix='/api/metadata')

    from app.blueprints.records import records_bp
    app.register_blueprint(records_bp, url_prefix='/api/records')

    from app.blueprints.questions import question_bp
    app.register_blueprint(question_bp, url_prefix='/api/questions')

    from app.blueprints.assessments import assessment_bp
    app.register_blueprint(assessment_bp, url_prefix='/api/assessments')

    from app.blueprints.components import components_bp
    app.register_blueprint(components_bp, url_prefix='/api/components')

    from app.blueprints.responses import responses_bp
    app.register_blueprint(responses_bp, url_prefix='/api/responses')

    from app.blueprints.simulations import simulations_bp
    app.register_blueprint(simulations_bp, url_prefix='/api/simulations')

    from app.blueprints.markings import markings_bp
    app.register_blueprint(markings_bp, url_prefix='/api/markings')

    from app.blueprints.uploads import uploads_bp
    app.register_blueprint(uploads_bp, url_prefix='/api/uploads')

    from app.blueprints.analytics import analytics_bp
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')

    from app.blueprints.results import results_bp
    app.register_blueprint(results_bp, url_prefix='/results')

    from app.blueprints.grading import grading_bp
    app.register_blueprint(grading_bp, url_prefix='/api')

    from app.blueprints.public import public_bp
    app.register_blueprint(public_bp, url_prefix='/')

    from app.core.ui_service import register_ui_context_processors
    register_ui_context_processors(app)

    from app.blueprints.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/')

    from app.blueprints.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/')

    from app.blueprints.admin_builder import admin_builder_bp
    app.register_blueprint(admin_builder_bp, url_prefix='/')

    from app.blueprints.dynamic_ui import dynamic_ui_bp
    app.register_blueprint(dynamic_ui_bp, url_prefix='/')

    from app.blueprints.api_crud import api_crud_bp
    app.register_blueprint(api_crud_bp, url_prefix='/')

    from app.blueprints.examiner import examiner_bp
    app.register_blueprint(examiner_bp, url_prefix='/')

    from app.blueprints.student import student_bp
    app.register_blueprint(student_bp, url_prefix='/')

    return app
