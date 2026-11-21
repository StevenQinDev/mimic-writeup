import sqlite3
c=sqlite3.connect(':memory:')
c.executescript("CREATE TABLE memories(id,title,date,snippet,sealed); INSERT INTO memories VALUES(1,'public','date','text',0); CREATE TABLE unsent_letters(id,addressed_to,body); INSERT INTO unsent_letters VALUES(1,'recipient','DEMO_ONLY');")
payload='0 UNION ALL SELECT id,addressed_to,body FROM unsent_letters--'
q='SELECT title,date,snippet FROM memories WHERE id = '+payload+' AND sealed = 0'
assert c.execute(q).fetchall()==[(1,'recipient','DEMO_ONLY')]
assert c.execute('SELECT title,date,snippet FROM memories WHERE id = ? AND sealed = 0',(payload,)).fetchall()==[]
print('Synthetic SQLite demonstration: vulnerable query exposes DEMO_ONLY; parameterized query does not')
