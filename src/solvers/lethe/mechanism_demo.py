"""Demonstrate reused rowids inheriting dangling associations, entirely in memory."""
import sqlite3


def database(protected=False):
    db = sqlite3.connect(':memory:')
    db.execute('PRAGMA foreign_keys=ON')
    db.execute('CREATE TABLE memories(id INTEGER PRIMARY KEY, owner TEXT)')
    foreign_key = ' REFERENCES memories(id) ON DELETE CASCADE' if protected else ''
    db.execute(f'CREATE TABLE echoes(memory_id INTEGER{foreign_key}, body TEXT)')
    db.executemany('INSERT INTO memories VALUES (?, ?)',
                   [(i, 'sealed') for i in (1, 2, 3, 4, 5, 6, 9)])
    db.executemany('INSERT INTO echoes VALUES (?, ?)',
                   [(3, 'DEMO_ONLY old three'), (9, 'DEMO_ONLY old nine')])
    db.execute('DELETE FROM memories WHERE id IN (3,9)')
    db.executemany('INSERT INTO memories VALUES (?, ?)', [(i, 'owned') for i in (10, 11, 12)])
    return db


def exercise(protected):
    with database(protected) as db:
        db.execute("DELETE FROM memories WHERE owner='owned'")
        ids = [db.execute("INSERT INTO memories(owner) VALUES ('owned')").lastrowid
               for _ in range(3)]
        assert ids == [7, 8, 9]  # A vacant 3 does not take precedence over max(id)+1.
        inherited = db.execute('SELECT e.body FROM memories m JOIN echoes e ON e.memory_id=m.id WHERE m.id=9').fetchall()
        assert inherited == ([] if protected else [('DEMO_ONLY old nine',)])
        return ids, inherited


if __name__ == '__main__':
    ids, inherited = exercise(False)
    print('Allocated:', ids)
    print('Reused 9 inherits:', inherited[0][0])
    exercise(True)
    print('Foreign keys plus cascading deletion: no stale echo inherited')
