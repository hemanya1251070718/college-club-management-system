import sys
sys.path.insert(0, '.')
from app.auth import ROLE_METADATA

for r in ['president', 'lead', 'coordinator', 'secretary', 'member', 'admin', 'guest']:
    meta = ROLE_METADATA[r]
    print(f"Role: {r:12} | Events: {str(meta.get('can_events')):5} | Memberships: {str(meta.get('can_memberships')):5} | Lead: {str(meta.get('can_leads')):5} | Triggers: {meta.get('allowed_triggers')} | Procs: {meta.get('allowed_procs')[:4]}")
