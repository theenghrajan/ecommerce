# Builds the AC 510599 review/import workbook from the client CSVs + live storefront snapshot.
# Run: python build_sheet.py  (from _data-510599). Output: esimnow-unlimited-import-review.xlsx
import csv, json, collections as C
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

live = json.loads(json.load(open('live-products-2026-11-18.json', encoding='utf-8')))
cols = json.loads(json.load(open('live-collections-2026-11-18.json', encoding='utf-8')))['map']
rd = lambda f: [r for r in csv.DictReader(open('client/' + f, encoding='utf-8-sig')) if r['Variant SKU']]
U, P = rd('shopifyCSV_Daily_unlimited.csv'), rd('shopifyCSV_prepaid.csv')
is_unl = lambda p: 'unlimited' in p['tags'] or 'unlimited' in p['handle']
LU = [p for p in live if is_unl(p)]
LP = [p for p in live if not is_unl(p)]
byh = {p['handle']: p for p in live}
pre = lambda s: s.split('_')[0]

HELD_SPLIT = ['cn_unlimited', 'ky_unlimited', 'mo_unlimited', 'ph_unlimited', 'th_unlimited']
OCEANIA = 'o-oc-3_unlimited'
PREPAID_TODO = ['cn_package', 'hk_package', 'mk_package', 'vn_package']

# --- unlimited: map csv handle -> live product (via SKU prefix)
lpre = C.defaultdict(set)
for p in LU:
    for v in p['variants']: lpre[pre(v['sku'])].add(p['handle'])
csv_to_live = {}
for r in U:
    hs = lpre.get(pre(r['Variant SKU']))
    if hs: csv_to_live[r['Handle']] = next(iter(hs))
ULV = {(v['sku'], str(v['o2'])): (p, v) for p in LU for v in p['variants']}
PLV = {v['sku']: (p, v) for p in LP for v in p['variants']}
first = {}  # first csv row per handle (product-level fields)
for r in U + P: first.setdefault(r['Handle'], r)

UPD_H = ['ID', 'Handle', 'Title', 'Variant ID', 'Variant Command', 'Option1 Name', 'Option1 Value', 'Option2 Name',
         'Option2 Value', 'Variant SKU', 'Variant Price', 'Variant Compare At Price',
         'Metafield: title_tag [string]', 'Metafield: description_tag [string]', 'Old Handle', 'Old Price', 'Sep 4 Price (if different)', 'Review Note']
NEWV_H = ['ID', 'Handle', 'Variant Command', 'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value',
          'Variant SKU', 'Variant Price', 'Variant Cost', 'Variant Inventory Policy', 'Variant Fulfillment Service',
          'Variant Requires Shipping', 'Variant Taxable', 'Variant Grams', 'Variant Weight Unit', 'Plan', 'Sep 4 Price (if different)', 'Review Note']
NEWP_H = ['Handle', 'Command', 'Title', 'Body HTML', 'Vendor', 'Type', 'Tags', 'Status', 'Published',
          'Image Src', 'Image Alt Text', 'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value',
          'Variant SKU', 'Variant Price', 'Variant Cost', 'Variant Inventory Policy', 'Variant Fulfillment Service',
          'Variant Requires Shipping', 'Variant Taxable', 'Variant Grams', 'Variant Weight Unit',
          'Metafield: title_tag [string]', 'Metafield: description_tag [string]',
          'Custom Collections', 'Plan', 'Collection copied from', 'Sep 4 Price (if different)', 'Review Note']

# --- backup export (today): manual collections + redirects
from openpyxl import load_workbook as _lw
_bk = _lw('backups/Export-2026-11-18-031049.xlsx', read_only=True)
def _rows(n):
    it = _bk[n].iter_rows(values_only=True); h = list(next(it)); return [dict(zip(h, r)) for r in it]
custom = C.defaultdict(list)  # product handle -> manual collections
for r in _rows('Custom Collections'):
    if r['Product: Handle'] and r['Handle'] != 'popular': custom[r['Product: Handle']].append(r['Handle'])
REDIRECTS = _rows('Redirects')

# --- Sep 4 "Plan 1" price lookups (pending client confirmation of which list is final)
_dp = list(csv.DictReader(open('client/esimnow_Daily_Plan_1.csv', encoding='utf-8-sig')))
_g1, _g2 = C.defaultdict(list), C.defaultdict(list)
for r in U: _g1[r['Option1 Value']].append(r)
for r in _dp: _g2[r['Option1 Value']].append(r)
SEP4 = {}
for k in _g1:
    if len(_g1[k]) == len(_g2.get(k, [])):
        for r, d in zip(_g1[k], _g2[k]): SEP4[('U', r['Variant SKU'], r['Option2 Value'])] = d['Selling Price']
for r in csv.DictReader(open('client/esimnow_Prepaid_Plan_1.csv', encoding='utf-8-sig')):
    SEP4[('P', r['Option1 Value'])] = r['Selling Price']
def sep4(r, plan):
    v = SEP4.get(('U', r['Variant SKU'], r['Option2 Value'])) if plan == 'Unlimited' else SEP4.get(('P', r['Option1 Value']))
    return v if v is not None and abs(float(v) - float(r['Variant Price'])) > .001 else ''

def upd_rows(rows, live_lookup, key, skip_live, plan):
    out, seen = [], set()
    for r in rows:
        k = key(r)
        if k not in live_lookup: continue
        p, v = live_lookup[k]
        if p['handle'] in skip_live: continue
        top = p['id'] not in seen; seen.add(p['id'])
        old = v['price']; new = r['Variant Price']
        out.append([p['id'], r['Handle'], first[r['Handle']]['Title'], v['id'], 'MERGE', r['Option1 Name'], r['Option1 Value'],
                    r['Option2 Name'], r['Option2 Value'], v['sku'], new, '',
                    first[r['Handle']]['SEO Title'] if top else '', first[r['Handle']]['SEO Description'] if top else '',
                    p['handle'] if top else '', old if abs(float(old) - float(new)) > .001 else '',
                    sep4(r, plan), ''])
    return out

def newv_rows(rows, live_lookup, key, skip_live, plan):
    out = []
    for r in rows:
        if key(r) in live_lookup: continue
        lh = csv_to_live.get(r['Handle']) if plan == 'Unlimited' else None
        if plan == 'Prepaid':
            # existing prepaid product = any live product holding another sku of this csv handle
            hs = {live_lookup[key(x)][0]['handle'] for x in P if x['Handle'] == r['Handle'] and key(x) in live_lookup}
            lh = next(iter(hs)) if hs else None
        if not lh or lh in skip_live: continue
        out.append([byh[lh]['id'], r['Handle'], 'MERGE', r['Option1 Name'], r['Option1 Value'], r['Option2 Name'],
                    r['Option2 Value'], r['Variant SKU'], r['Variant Price'], r['Cost per Item'],
                    r['Variant Inventory Policy'], r['Variant Fulfillment Service'], r['Variant Requires Shipping'],
                    r['Variant Taxable'], r['Variant Grams'], r['Variant Weight Unit'], plan, sep4(r, plan),
                    'New variant on existing product (live: %s)' % lh])
    return out

ukey = lambda r: (r['Variant SKU'], r['Option2 Value'])
pkey = lambda r: r['Variant SKU']
unl_upd = upd_rows(U, ULV, ukey, set(HELD_SPLIT) | {OCEANIA}, 'Unlimited')
unl_newv = newv_rows(U, ULV, ukey, set(HELD_SPLIT) | {OCEANIA}, 'Unlimited')
# prepaid: only the 4 held products + price fixes (rest already imported Oct 6)
pre_upd = [x for x in upd_rows(P, PLV, pkey, set(), 'Prepaid') if next(p['handle'] for p in LP if p['id'] == x[0]) in PREPAID_TODO]
pre_newv = newv_rows(P, PLV, pkey, set(), 'Prepaid')

# --- new products (no live sku for the whole handle)
CLOSEST = {
    'aruba': 'cw', 'saint-barthelemy': 'gp', 'saint-martin': 'gp', 'martinique': 'gp', 'mayotte': 're',
    'ethiopia': 'ke', 'mauritania': 'sn', 'liechtenstein': 'ch', 'san-marino': 'it', 'vatican-city': 'it',
    'venezuela': 'co', 'south-america-6-areas': 'co', 'south-america': 'co', 'europe-33-areas': 'eu-30',
    'europe-35-areas': 'eu-30', 'kosovo': 'rs', 'vanuatu': 'fj'}
PRE_CLOSEST = {'aruba': 'curacao-esim', 'south-america-6-areas': 'south-america-esim', 'europe-33-areas': 'europe-30-areas-esim',
               'europe-35-areas': 'europe-30-areas-esim'}
NO_EXACT = {'south-america-6-areas', 'south-america', 'europe-33-areas', 'europe-35-areas'}
sku_live_u = {pre(v['sku']) for p in LU for v in p['variants']}
sku_live_p = set(PLV)
lp_by_pre = {}
for p in LP:
    for v in p['variants']: lp_by_pre.setdefault(pre(v['sku']), p['handle'])
newp = []
missing = []
for plan, rows in (('Unlimited', U), ('Prepaid', P)):
    hs = C.OrderedDict()
    for r in rows: hs.setdefault(r['Handle'], []).append(r)
    for h, rr in hs.items():
        if plan == 'Unlimited' and h in csv_to_live: continue
        if plan == 'Prepaid' and any(x['Variant SKU'] in sku_live_p for x in rr): continue
        base = h.replace('-unlimited-esim', '').replace('-esim', '')
        cc = CLOSEST.get(base)
        if plan == 'Unlimited':
            src = (cc + '_unlimited') if cc else None
        else:
            src = PRE_CLOSEST.get(base) or (lp_by_pre.get(cc.upper()) if cc else None)
        if not src or src not in byh: missing.append((plan, h, src)); src_cols = ''
        else: src_cols = ', '.join(custom.get(src, []))
        note = 'Description, image and tags from client CSV. Region collections follow the tags automatically; Custom Collections copied from the closest product.'
        if not src_cols:
            src_cols = 'daypass-plans' if plan == 'Unlimited' else 'country'
            note += ' Closest product is in no manual collection, so the usual one for this plan type is used.'
        if base in NO_EXACT: note += ' No exact regional match on the site; closest used.'
        for i, r in enumerate(rr):
            t = i == 0
            newp.append([h, 'NEW' if t else '', r['Title'] if t else '', r['Body (HTML)'] if t else '', r['Vendor'] if t else '',
                         r['Type'] if t else '', r['Tags'] if t else '', r['Status'] if t else '', r['Published'] if t else '',
                         r['Image Src'] if t else '', r['Image Alt Text'] if t else '', r['Option1 Name'], r['Option1 Value'],
                         r['Option2 Name'], r['Option2 Value'], r['Variant SKU'], r['Variant Price'], r['Cost per Item'],
                         r['Variant Inventory Policy'], r['Variant Fulfillment Service'], r['Variant Requires Shipping'],
                         r['Variant Taxable'], r['Variant Grams'], r['Variant Weight Unit'],
                         r['SEO Title'] if t else '', r['SEO Description'] if t else '', src_cols if t else '', plan,
                         (src or 'NEEDS PICK') if t else '', sep4(r, plan), note if t else ''])

# --- removals
REM_H = ['ID', 'Handle', 'Command', 'Variant ID', 'Variant Command', 'Variant SKU', 'Option1 Value', 'Option2 Value',
         'Redirect From', 'Redirect To', 'Review Note']
rem = []
oc = byh[OCEANIA]
rem.append([oc['id'], OCEANIA, 'DELETE', '', '', '', '', '', '/products/' + OCEANIA, '/collections/oceania',
            'Oceania Orange removed (Charlie #9). Redirect to Oceania collection (no single matching product), see tab 6.'])
for k, (p, v) in sorted(ULV.items()):
    if p['handle'] == 'vn_unlimited' and k not in {ukey(r) for r in U}:
        rem.append([p['id'], p['handle'], '', v['id'], 'DELETE', v['sku'], v['o1'], v['o2'], '', '',
                    'Variant not in client CSV. Page stays, no redirect needed.'])
for s, (p, v) in sorted(PLV.items()):
    if s not in {r['Variant SKU'] for r in P}:
        rem.append([p['id'], p['handle'], '', v['id'], 'DELETE', v['sku'], v['o1'], v['o2'], '', '',
                    'Prepaid variant not in client CSV (not in IBM list) - CONFIRM before removing.'])

# --- redirects: repoint existing redirects whose target is a handle we are changing (avoid chains)
RED_H = ['ID', 'Path', 'Command', 'Target', 'Old Target', 'Review Note']
new_of = {old: new for new, old in csv_to_live.items() if old not in HELD_SPLIT and list(csv_to_live.values()).count(old) == 1}
new_of.update({x[14]: x[1] for x in pre_upd if x[14]})
red = []
for r in REDIRECTS:
    t = r['Target'] or ''
    base, _, q = t.partition('?')
    h = base.rstrip('/').split('/products/')[-1] if '/products/' in base else None
    if h in new_of:
        nt = base[:base.rindex('/products/')] + '/products/' + new_of[h] + ('?' + q if q else '')
        red.append([r['ID'], r['Path'], 'UPDATE', nt, t, 'Old redirect pointed to a URL that is changing; repointed to the new URL.'])
    elif h == OCEANIA:
        red.append([r['ID'], r['Path'], 'UPDATE', '/collections/oceania', t, 'Old redirect pointed to Oceania Orange (being removed).'])
red.append(['', '/products/' + OCEANIA, 'NEW', '/collections/oceania', '', 'Oceania Orange removed (Charlie #9).'])

# --- held splits
HELD_H = ['Live Handle', 'Live Title', 'Live Variants', 'CSV Handle', 'CSV Title', 'CSV Variants', 'CSV Option1 values', 'Question']
held = []
for lh in HELD_SPLIT:
    p = byh[lh]
    for h in [h for h, v in csv_to_live.items() if v == lh]:
        rr = [r for r in U if r['Handle'] == h]
        held.append([lh, p['title'], len(p['variants']), h, rr[0]['Title'], len(rr), ', '.join(sorted({r['Option1 Value'] for r in rr})),
                     'CSV splits this product in two. Keep as one product, or create the second product?'])

# --- Sep 4 Plan 1 price check
PC_H = ['Plan', 'Option1 Value', 'Days', 'Live Price', 'Aug 19 CSV Price (used)', 'Sep 4 Plan 1 Price']
pc = []
dp = list(csv.DictReader(open('client/esimnow_Daily_Plan_1.csv', encoding='utf-8-sig')))
g1, g2 = C.defaultdict(list), C.defaultdict(list)
for r in U: g1[r['Option1 Value']].append(r)
for r in dp: g2[r['Option1 Value']].append(r)
for k in g1:
    if len(g1[k]) != len(g2.get(k, [])): continue
    for r, d in zip(g1[k], g2[k]):
        if abs(float(r['Variant Price']) - float(d['Selling Price'])) > .001:
            lv = ULV.get(ukey(r)); pc.append(['Unlimited', k, r['Option2 Value'], lv[1]['price'] if lv else '', r['Variant Price'], d['Selling Price']])
pp = list(csv.DictReader(open('client/esimnow_Prepaid_Plan_1.csv', encoding='utf-8-sig')))
pcsv = {r['Option1 Value']: r['Variant Price'] for r in P}
plive = {v['o1']: v['price'] for p in LP for v in p['variants']}
for r in pp:
    k = r['Option1 Value']
    if k in pcsv and abs(float(pcsv[k]) - float(r['Selling Price'])) > .001:
        pc.append(['Prepaid', k, '', plive.get(k, ''), pcsv[k], r['Selling Price']])

# --- write
wb = Workbook(); wb.remove(wb.active)
readme = [
    ['eSIMnow - Daily Unlimited CSV + remaining Prepaid items (AC #133 / 510599)'],
    ['Built 2026-11-18 from client CSVs (Aug 19) and the live store. Nothing has been imported yet.'],
    [''],
    ['Tab', 'Rows', 'What it does'],
    ['1 Unlimited Update', len(unl_upd), 'Existing unlimited products: new URL, title, SEO title, meta description, prices. Old URL redirects automatically (Matrixify).'],
    ['2 New Variants', len(unl_newv) + len(pre_newv), 'New plans added to existing products (unlimited + prepaid).'],
    ['3 New Products', len(newp), '15 unlimited + 15 prepaid new products. Description/image/tags from client CSV; collection copied from closest product (column).'],
    ['4 Prepaid Remaining', len(pre_upd), 'China, Hong Kong, North Macedonia, Vietnam prepaid: new URLs + old prices fixed.'],
    ['5 Removals', len(rem), 'Oceania Orange + 8 Vietnam unlimited variants. 1 prepaid Philippines variant needs confirmation.'],
    ['6 Redirects', len(red), 'Existing redirects that point to a URL we are changing, repointed to the new URL so there are no redirect chains. Plus Oceania Orange.'],
    ['7 HOLD - Split Products', len(held), 'NOT in import. Client CSV splits 5 products in two (2 with typo names). Needs a decision.'],
    ['8 Price Check Sep 4', len(pc), 'Prices that differ between the Aug 19 CSVs and the Sep 4 "Plan 1" files.'],
    [''],
    ['PRICES PENDING: Variant Price = Aug 19 CSV. Column "Sep 4 Price (if different)" shows the Sep 4 list. Waiting for the client to confirm which list is final (asked in AC comment). Do not import until confirmed.'],
    [''],
    ['Import order: 1 -> 4 -> 2 -> 3 -> 5 -> 6. Full backup export taken 2026-11-18 (Matrixify job #786095078); take a fresh one right before import.'],
]
for name, head, rows in [('README', None, readme), ('1 Unlimited Update', UPD_H, unl_upd), ('2 New Variants', NEWV_H, unl_newv + pre_newv),
                         ('3 New Products', NEWP_H, newp), ('4 Prepaid Remaining', UPD_H, pre_upd), ('5 Removals', REM_H, rem), ('6 Redirects', RED_H, red),
                         ('7 HOLD - Split Products', HELD_H, held), ('8 Price Check Sep 4', PC_H, pc)]:
    ws = wb.create_sheet(name[:31])
    if head:
        ws.append(head)
        for c in ws[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='2E3D66')
        ws.freeze_panes = 'A2'
    for r in rows: ws.append([str(x) if isinstance(x, int) and x > 10**9 else x for x in r])
wb.save('esimnow-unlimited-import-review.xlsx')

print('unl_upd', len(unl_upd), 'products', len({r[0] for r in unl_upd}), 'price changes', sum(1 for r in unl_upd if r[15] != ''))
print('unl_newv', len(unl_newv), 'pre_newv', len(pre_newv))
print('newp rows', len(newp), 'products', sum(1 for r in newp if r[1] == 'NEW'))
print('pre_upd', len(pre_upd), 'price fixes', sum(1 for r in pre_upd if r[15] != ''))
print('rem', len(rem), 'red', len(red), 'held', len(held), 'pricecheck', len(pc))
print('MISSING closest:', missing)
