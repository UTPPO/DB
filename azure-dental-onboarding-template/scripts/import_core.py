import json, re, sqlite3
from pathlib import Path
class DB: 
    def __init__(self): self.conn=sqlite3.connect(':memory:'); self.cur=self.conn.cursor(); self.cur.execute('PRAGMA foreign_keys=ON;')
    def exec(self,sql,p=None): self.cur.execute(sql,p or []); return self.cur
    def commit(self): self.conn.commit()
    def close(self): self.conn.close()

def parse_date(s):
    import re
    if not s: return None
    m=re.match(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',str(s))
    if not m: return None
    mm,dd,yy=int(m.group(1)),int(m.group(2)),int(m.group(3)); yy=yy+2000 if yy<100 else yy
    return f'{yy:04d}-{mm:02d}-{dd:02d}'

def run_folder(folder: Path):
    db=DB()
    db.exec('CREATE TABLE forms(id INTEGER PRIMARY KEY, title TEXT)')
    db.exec('CREATE TABLE submissions(id INTEGER PRIMARY KEY, form_id INT, entry_id TEXT)')
    db.exec('CREATE TABLE dentists(id INTEGER PRIMARY KEY, first TEXT, last TEXT, gender TEXT, dob TEXT)')
    db.exec('CREATE TABLE licenses(id INTEGER PRIMARY KEY, dentist_id INT, type TEXT, state TEXT, number TEXT, exp TEXT)')
    report={'summary':{},'reports':[]}
    for p in sorted(folder.glob('*.json')):
        obj=json.loads(p.read_text())
        form=obj['forms'][0]; entry=form['entries'][0]
        db.exec('INSERT INTO forms(title) VALUES(?)',(form.get('title'),))
        form_id=db.exec('SELECT last_insert_rowid()').fetchone()[0]
        db.exec('INSERT INTO submissions(form_id,entry_id) VALUES(?,?)',(form_id,entry.get('entry_id')))
        first=entry.get('101.3') or 'Unknown'; last=entry.get('101.6') or 'Unknown'
        gender=entry.get('102'); dob=parse_date(entry.get('103'))
        db.exec('INSERT INTO dentists(first,last,gender,dob) VALUES(?,?,?,?)',(first,last,gender,dob))
        did=db.exec('SELECT last_insert_rowid()').fetchone()[0]
        db.exec('INSERT INTO licenses(dentist_id,type,state,number,exp) VALUES(?,?,?,?,?)',(did,entry.get('201') or 'Dental',entry.get('202'),entry.get('203'),parse_date(entry.get('205'))))
        report['reports'].append({'file':p.name,'status':'ok','dentist_id':did})
    dentists=db.exec('SELECT COUNT(*) FROM dentists').fetchone()[0]
    licenses=db.exec('SELECT COUNT(*) FROM licenses').fetchone()[0]
    report['summary']={'dentists':dentists,'licenses':licenses}
    return report
