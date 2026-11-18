# Reads today's Matrixify backup: smart collection rules, custom collection membership, redirect chains, activity around bulk touches.
from openpyxl import load_workbook
import json,collections as C
wb=load_workbook('backups/Export-2026-11-18-031049.xlsx',read_only=True)
def rows(n):
  it=wb[n].iter_rows(values_only=True); h=list(next(it)); return [dict(zip(h,r)) for r in it]
sc=rows('Smart Collections'); cc=rows('Custom Collections'); rd=rows('Redirects'); act=rows('Activity'); pr=rows('Products')
print('SMART:'); [print(' ',r['Handle'],r['Must Match'],r['Rule: Product Column'],r['Rule: Relation'],r['Rule: Condition']) for r in sc]
cm=C.defaultdict(list)
for r in cc: cm[r['Handle']].append(r['Product: Handle'])
print('CUSTOM:',{k:len(v) for k,v in cm.items()})
for k,v in cm.items(): print('  ',k,[x for x in v if x and 'unlimited' in x][:8])
# products not on storefront
live=json.loads(json.load(open('live-products-2026-11-18.json',encoding='utf-8'))); lh={p['handle'] for p in live}
tops=[r for r in pr if r.get('Top Row')]
print('products',len(tops),'not on storefront:',[(r['Handle'],r['Status']) for r in tops if r['Handle'] not in lh])
print('=== REDIRECTS')
exec(open('build_sheet.py').read().split('# --- write')[0].replace("live = json","_l = json") if False else '')
import csv
U=[r for r in csv.DictReader(open('client/shopifyCSV_Daily_unlimited.csv',encoding='utf-8-sig')) if r['Variant SKU']]
oldh={p['handle'] for p in live if 'unlimited' in p['tags'] or 'unlimited' in p['handle']} | {'cn_package','hk_package','mk_package','vn_package'}
tgt=C.Counter(); ex=C.defaultdict(list)
for r in rd:
  t=(r['Target'] or '').split('?')[0].rstrip('/')
  h=t.split('/products/')[-1] if '/products/' in t else None
  if h in oldh: tgt[h]+=1; ex[h].append(r['Path'])
print('redirects pointing at handles that will change:',sum(tgt.values()),'across',len(tgt),'products')
print(' sample',list(ex.items())[:3])
src=[r for r in rd if any((r['Path'] or '').rstrip('/').endswith('/products/'+h) for h in oldh)]
print('existing redirects FROM an old handle path (would conflict with auto-redirect):',len(src),[(r['Path'],r['Target']) for r in src[:5]])
print('=== ACTIVITY')
ts=C.Counter(str(r['Created At'])[:13] for r in act)
print('busiest hours',ts.most_common(8))
for r in act:
  s=str(r['Created At'])
  if s.startswith('2026-11-12') or s.startswith('2026-11-13') or s.startswith('2026-11-18'):
    pass
near=[r for r in act if str(r['Created At'])[:10] in ('2026-11-12','2026-11-13','2026-11-18')]
print('events Nov12/13/18:',len(near)); 
for r in near[:25]: print('  ',r['Created At'],r['Subject Type'],r['Verb'],r['Author'],str(r['Message'])[:90])
print('date range',min(str(r['Created At']) for r in act),max(str(r['Created At']) for r in act))
print('authors',C.Counter(r['Author'] for r in act).most_common(10))
