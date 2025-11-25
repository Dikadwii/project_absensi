from database import get_db_connection, delete_siswa_by_id

conn = get_db_connection()
rows = conn.execute("SELECT id,nama,nis,kelas_id FROM siswa WHERE nis = ? OR nama = ?", ('2','aa')).fetchall()
print('Found', len(rows))
for r in rows:
    print(dict(r))
for r in rows:
    print('Deleting', r['id'], delete_siswa_by_id(r['id']))

rows2 = conn.execute("SELECT id,nama,nis,kelas_id FROM siswa ORDER BY id").fetchall()
print('Remaining count:', len(rows2))
for r in rows2:
    print(dict(r))
conn.close()
