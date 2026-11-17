import sqlite3
import json

conn = sqlite3.connect('database/clubhub_app.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""
    SELECT s.student_id, s.prn_number, s.name, s.email, m.club_id, c.club_name, m.role
    FROM Students s
    LEFT JOIN Memberships m ON s.student_id = m.student_id
    LEFT JOIN Clubs c ON m.club_id = c.club_id
    ORDER BY s.student_id
""")
rows = cursor.fetchall()

# Group by student_id
students_dict = {}
for r in rows:
    sid = r['student_id']
    if sid not in students_dict:
        students_dict[sid] = {
            'student_id': sid,
            'prn': r['prn_number'],
            'name': r['name'],
            'email': r['email'],
            'memberships': []
        }
    if r['club_id']:
        students_dict[sid]['memberships'].append({
            'club_id': r['club_id'],
            'club_name': r['club_name'],
            'role': r['role']
        })

# Principal account
seed_users = [{
    'student_id': 'FAC-001',
    'prn': '1210000001',
    'name': 'Prof. D. K. Sharma (Principal)',
    'email': 'sharma.principal@vit.edu',
    'role': 'admin',
    'role_title': 'Super Admin / Principal',
    'club_id': 'ALL',
    'club_role': 'Principal',
    'aliases': ['sharma.principal@vit.edu', 'principal@vit.edu']
}]

for sid, s in students_dict.items():
    prn = s['prn']
    clean_name = s['name'].split()[0].lower()
    mems = s['memberships']
    
    # Sort memberships by priority: President > Lead > Secretary > Event Coordinator > Core Member > Member
    def prio(role):
        r = role.lower()
        if 'president' in r: return 1
        if 'lead' in r: return 2
        if 'secretary' in r: return 3
        if 'event' in r or 'coordinator' in r: return 4
        if 'core' in r: return 5
        return 6
        
    mems.sort(key=lambda m: prio(m['role']))
    
    primary_mem = mems[0] if mems else None
    
    aliases = [s['email'].lower()]
    
    if primary_mem:
        role_name = primary_mem['role']
        club_id = primary_mem['club_id']
        r_low = role_name.lower()
        
        if 'president' in r_low:
            role = 'president'
            role_title = f"Club President ({club_id})"
            aliases.append(f"{clean_name}.{prn}.president@vit.edu")
        elif 'lead' in r_low:
            role = 'lead'
            role_title = f"Club Lead ({club_id})"
            aliases.append(f"{clean_name}.{prn}.lead@vit.edu")
        elif 'event' in r_low or 'coordinator' in r_low:
            role = 'coordinator'
            role_title = f"Event Coordinator ({club_id})"
            aliases.append(f"{clean_name}.{prn}.coordinator@vit.edu")
        elif 'secretary' in r_low:
            role = 'secretary'
            role_title = f"Club Secretary ({club_id})"
            aliases.append(f"{clean_name}.{prn}.secretary@vit.edu")
        elif 'treasurer' in r_low:
            role = 'secretary'
            role_title = f"Club Treasurer ({club_id})"
            aliases.append(f"{clean_name}.{prn}.secretary@vit.edu")
            aliases.append(f"{clean_name}.{prn}.treasurer@vit.edu")
        elif 'core' in r_low:
            role = 'member'
            role_title = f"Core Member ({club_id})"
            aliases.append(f"{clean_name}.{prn}.coremember@vit.edu")
        else:
            role = 'member'
            role_title = f"Student Member ({club_id})"
            
        # Also add aliases for other memberships if multi-role
        for other in mems[1:]:
            or_low = other['role'].lower()
            if 'president' in or_low and f"{clean_name}.{prn}.president@vit.edu" not in aliases:
                aliases.append(f"{clean_name}.{prn}.president@vit.edu")
            elif 'lead' in or_low and f"{clean_name}.{prn}.lead@vit.edu" not in aliases:
                aliases.append(f"{clean_name}.{prn}.lead@vit.edu")
            elif ('event' in or_low or 'coordinator' in or_low) and f"{clean_name}.{prn}.coordinator@vit.edu" not in aliases:
                aliases.append(f"{clean_name}.{prn}.coordinator@vit.edu")
            elif 'secretary' in or_low and f"{clean_name}.{prn}.secretary@vit.edu" not in aliases:
                aliases.append(f"{clean_name}.{prn}.secretary@vit.edu")

        club_role = role_name
    else:
        role = 'member'
        role_title = 'Student (No Club)'
        club_id = ''
        club_role = 'None'

    seed_users.append({
        'student_id': sid,
        'prn': prn,
        'name': s['name'],
        'email': s['email'],
        'role': role,
        'role_title': role_title,
        'club_id': club_id,
        'club_role': club_role,
        'aliases': list(dict.fromkeys(aliases))
    })

print(f"Generated {len(seed_users)} seed users.")

with open('app/seed_users.py', 'w', encoding='utf-8') as f:
    f.write('"""\nAutomatically Generated Seed Users Catalog\nContains all 75 students + Principal with role mappings and credentials.\n"""\n\n')
    f.write(f"SEED_USERS = {json.dumps(seed_users, indent=2)}\n")

print("Updated app/seed_users.py successfully.")
conn.close()
