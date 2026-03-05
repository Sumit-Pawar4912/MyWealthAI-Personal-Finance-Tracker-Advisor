from app.database import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
import hmac
import binascii
import base64
class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Verify password"""
        # Support legacy scrypt hashes stored in the DB with format:
        # scrypt:<n>:<r>:<p>$<salt>$<hash>
        if isinstance(self.password_hash, str) and self.password_hash.startswith('scrypt:'):
            try:
                print(f"Auth: attempting scrypt verification for user {self.email}")
            except Exception:
                pass
            try:
                parts = self.password_hash.split('$')
                if len(parts) < 3:
                    raise ValueError('invalid scrypt hash format')
                params = parts[0].split(':')  # ['scrypt', n, r, p]
                if len(params) < 4:
                    raise ValueError('invalid scrypt params')
                n = int(params[1])
                r = int(params[2])
                p = int(params[3])
                salt_raw = parts[1]
                hash_raw = parts[2]

                def try_decode_hex_or_b64(s):
                    """Try to decode base64 first (for salt), then hex (for hash)"""
                    # try base64 with padding first (salt is usually base64)
                    try:
                        pad = '=' * (-len(s) % 4)
                        return base64.b64decode(s + pad)
                    except Exception:
                        pass
                    # try hex (hash is usually hex)
                    try:
                        if len(s) % 2 == 0:
                            return binascii.unhexlify(s)
                    except Exception:
                        pass
                    # fallback to raw bytes
                    return s.encode()
                
                def try_decode_b64_first(s):
                    """Try base64 first"""
                    try:
                        pad = '=' * (-len(s) % 4)
                        return base64.b64decode(s + pad)
                    except Exception:
                        pass
                    try:
                        if len(s) % 2 == 0:
                            return binascii.unhexlify(s)
                    except Exception:
                        pass
                    return s.encode()
                
                def try_decode_hex_only(s):
                    """Try hex only"""
                    try:
                        if len(s) % 2 == 0:
                            return binascii.unhexlify(s)
                    except Exception:
                        pass
                    try:
                        pad = '=' * (-len(s) % 4)
                        return base64.b64decode(s + pad)
                    except Exception:
                        pass
                    return s.encode()

                salt = try_decode_b64_first(salt_raw)  # Salt is base64
                stored = try_decode_hex_only(hash_raw)  # Hash is hex

                dklen = len(stored)
                try:
                    derived = hashlib.scrypt(password.encode('utf-8'), salt=salt, n=n, r=r, p=p, dklen=dklen)
                except Exception as e:
                    # Memory-related scrypt errors surface as OpenSSL errors or ValueError
                    msg = str(e)
                    print(f"Auth: scrypt derive error for {self.email}: {msg}")
                    # If it's a memory limit issue, retry with a bounded maxmem to allow lower-memory hosts to attempt derivation
                    if 'memory' in msg.lower() or 'memory limit' in msg.lower() or 'DIGEST' in msg:
                        try:
                            maxmem = 128 * 1024 * 1024  # 128 MB
                            derived = hashlib.scrypt(password.encode('utf-8'), salt=salt, n=n, r=r, p=p, dklen=dklen, maxmem=maxmem)
                            print(f"Auth: scrypt retry with maxmem={maxmem} succeeded for {self.email}")
                        except Exception as e2:
                            print(f"Auth: scrypt retry (maxmem) failed for {self.email}: {e2}")
                            return False
                    else:
                        return False

                ok = hmac.compare_digest(derived, stored)
                try:
                    print(f"Auth: scrypt verification for {self.email} returned {ok} (salt_len={len(salt)}, dklen={dklen})")
                except Exception:
                    pass
                return ok
            except Exception as e:
                try:
                    print(f"Auth: scrypt verification for {self.email} failed during parsing/verification: {e}")
                except Exception:
                    pass
                return False

        try:
            print(f"Auth: attempting werkzeug verification for user {self.email}")
        except Exception:
            pass
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat(),
        }


class Transaction(db.Model):
    """Transaction model for income and expenses"""
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'
    category = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert transaction to dictionary"""
        return {
            'id': self.id,
            'type': self.type,
            'category': self.category,
            'description': self.description,
            'amount': self.amount,
            'date': self.date.isoformat(),
            'created_at': self.created_at.isoformat(),
        }
