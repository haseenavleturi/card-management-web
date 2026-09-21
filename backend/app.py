from flask import Flask, request, jsonify, send_from_directory
from pathlib import Path
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / 'frontend'
DB_PATH = Path('/app/data/cards.db')
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, static_folder=None)

def db():
    c = sqlite3.connect(DB_PATH); c.row_factory = sqlite3.Row; return c

def init_db():
    c=db(); c.executescript('''
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,password TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS folders(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,name TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS cards(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,folder_id INTEGER,title TEXT NOT NULL,card_holder TEXT NOT NULL,card_number TEXT NOT NULL,expiry TEXT,cvv TEXT,notes TEXT);
    '''); c.commit(); c.close()

@app.get('/')
def index(): return send_from_directory(FRONTEND_DIR,'index.html')
@app.get('/<path:path>')
def static(path):
    p=FRONTEND_DIR/path
    return send_from_directory(FRONTEND_DIR,path) if p.is_file() else send_from_directory(FRONTEND_DIR,'index.html')

@app.post('/api/register')
def register():
    d=request.get_json() or {}; name=d.get('name','').strip(); email=d.get('email','').strip().lower(); password=d.get('password','')
    if not name or not email or not password: return jsonify(error='Name, email and password are required.'),400
    if len(password)<6: return jsonify(error='Password must be at least 6 characters.'),400
    c=db()
    try:
        cur=c.execute('INSERT INTO users(name,email,password) VALUES(?,?,?)',(name,email,generate_password_hash(password))); c.commit(); uid=cur.lastrowid
    except sqlite3.IntegrityError: c.close(); return jsonify(error='Email is already registered.'),409
    c.close(); return jsonify(message='Registration successful.',user={'id':uid,'name':name,'email':email}),201
@app.delete('/api/users/<int:uid>/folders/<int:fid>')
def delete_folder(uid, fid):
    c = db()

    # Folder lo cards unnaya check
    count = c.execute(
        'SELECT COUNT(*) FROM cards WHERE folder_id=? AND user_id=?',
        (fid, uid)
    ).fetchone()[0]

    if count > 0:
        c.close()
        return jsonify(error='Folder contains cards. Delete or move the cards first.'), 400

    cur = c.execute(
        'DELETE FROM folders WHERE id=? AND user_id=?',
        (fid, uid)
    )

    c.commit()
    deleted = cur.rowcount
    c.close()

    if deleted:
        return jsonify(message='Folder deleted.')

    return jsonify(error='Folder not found.'), 404
@app.post('/api/login')
def login():
    d=request.get_json() or {}; c=db(); u=c.execute('SELECT * FROM users WHERE email=?',(d.get('email','').strip().lower(),)).fetchone(); c.close()
    if not u or not check_password_hash(u['password'],d.get('password','')): return jsonify(error='Invalid email or password.'),401
    return jsonify(message='Login successful.',user={'id':u['id'],'name':u['name'],'email':u['email']})

@app.get('/api/users/<int:uid>/folders')
def folders(uid):
    c=db(); rows=c.execute('SELECT id,name FROM folders WHERE user_id=? ORDER BY id DESC',(uid,)).fetchall(); c.close(); return jsonify([dict(x) for x in rows])
@app.post('/api/users/<int:uid>/folders')
def add_folder(uid):
    name=(request.get_json() or {}).get('name','').strip()
    if not name:return jsonify(error='Folder name is required.'),400
    c=db(); cur=c.execute('INSERT INTO folders(user_id,name) VALUES(?,?)',(uid,name)); c.commit(); fid=cur.lastrowid; c.close(); return jsonify(id=fid,name=name),201

@app.get('/api/users/<int:uid>/cards')
def cards(uid):
    c=db(); rows=c.execute('''SELECT cards.*,COALESCE(folders.name,'Unfiled') folder_name FROM cards LEFT JOIN folders ON folders.id=cards.folder_id WHERE cards.user_id=? ORDER BY cards.id DESC''',(uid,)).fetchall(); c.close(); return jsonify([dict(x) for x in rows])
@app.post('/api/users/<int:uid>/cards')
def add_card(uid):
    d = request.get_json() or {}
    title = d.get('title', '').strip()
    holder = d.get('card_holder', '').strip()
    number = d.get('card_number', '').strip()

    if not title or not holder or not number:
        return jsonify(error='Card title, card holder and card number are required.'), 400

    c = db()

    cur = c.execute(
        'INSERT INTO cards(user_id,folder_id,title,card_holder,card_number,expiry,cvv,notes) VALUES(?,?,?,?,?,?,?,?)',
        (
            uid,
            d.get('folder_id') or None,
            title,
            holder,
            number,
            d.get('expiry', ''),
            d.get('cvv', ''),
            d.get('notes', '')
        )
    )

    c.commit()
    cid = cur.lastrowid
    c.close()

    return jsonify(message='Card added.', id=cid), 201
    
@app.delete('/api/users/<int:uid>/cards/<int:cid>')
def delete_card(uid,cid):
    c=db(); cur=c.execute('DELETE FROM cards WHERE id=? AND user_id=?',(cid,uid)); c.commit(); n=cur.rowcount; c.close(); return (jsonify(message='Card deleted.') if n else (jsonify(error='Card not found.'),404))
@app.get('/api/users/<int:uid>')
def profile(uid):
    c=db(); u=c.execute('SELECT id,name,email FROM users WHERE id=?',(uid,)).fetchone(); c.close(); return (jsonify(dict(u)) if u else (jsonify(error='User not found.'),404))

if __name__=='__main__': init_db(); app.run(host='0.0.0.0',port=5030,debug=True)
