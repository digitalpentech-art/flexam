import uuid
from datetime import datetime
from flask_login import UserMixin
from app.extensions import db, login_manager
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import generate_password_hash, check_password_hash

class Tenant(db.Model):
    __tablename__ = 'tenants'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(128), nullable=False)
    slug = db.Column(db.String(64), unique=True, nullable=False, index=True)
    allow_self_registration = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    users = db.relationship('User', backref='tenant', lazy='dynamic')
    roles = db.relationship('Role', backref='tenant', lazy='dynamic')

    def __repr__(self):
        return f'<Tenant {self.slug}>'

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(255))
    permissions = db.Column(db.JSON) # List of permission strings

    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'name', name='_tenant_role_uc'),
    )

    def __repr__(self):
        return f'<Role {self.name} (Tenant: {self.tenant_id})>'

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    is_active = db.Column(db.Boolean, default=True)
    is_superadmin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey('roles.id'))
    role = db.relationship('Role', backref=db.backref('users', lazy='dynamic'))

    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'email', name='_tenant_user_uc'),
    )

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email} (Tenant: {self.tenant_id})>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    action = db.Column(db.String(64), nullable=False)
    entity_type = db.Column(db.String(64))
    entity_id = db.Column(db.String(64))
    changes = db.Column(db.JSON) # Before/After values
    remote_addr = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AuditLog {self.action} by {self.user_id}>'
