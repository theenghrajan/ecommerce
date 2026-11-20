# Builds the AC 510599 review/import workbook from the client CSVs + live storefront snapshot.
# Run: python build_sheet.py  (from _data-510599). Output: esimnow-unlimited-import-review.xlsx
import csv, json, re, collections as C
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

live = json.loads(json.load(open('live-products-2026-11-18.json', encoding='utf-8')))
cols = json.loads(json.load(open('live-collections-2026-11-18.json', encoding='utf-8')))['map']
rd = lambda f: [r for r in csv.DictReader(open('client/' + f, encoding='utf-8-sig')) if r['Variant SKU']]
U, P = rd('shopifyCSV_Daily_unlimited.csv'), rd('shopifyCSV_prepaid.csv')
# Charlie #12: the 5 split products stay one product; fix the typo option names
SPLIT_MAIN = {'china-nonhkip-unlimited-esim': 'china-unlimited-esim', 'macao-nonhkip-unlimited-esim': 'macao-unlimited-esim',
              'thailand-nonhkip-unlimited-esim': 'thailand-unlimited-esim', 'cayman-lslands-unlimited-esim': 'cayman-islands-unlimited-esim',
              'philippine-unlimited-esim': 'philippines-unlimited-esim'}
for r in U + P:
    r['_h'], r['_o1'] = r['Handle'], r['Option1 Value']  # originals (Sep 4 lookup uses _o1)
for r in U:
    r['Handle'] = SPLIT_MAIN.get(r['Handle'], r['Handle'])
    r['Option1 Value'] = re.sub(r'^Philippine ', 'Philippines ', r['Option1 Value']).replace('Cayman lslands', 'Cayman Islands')
is_unl = lambda p: 'unlimited' in p['tags'] or 'unlimited' in p['handle']
LU = [p for p in live if is_unl(p)]
LP = [p for p in live if not is_unl(p)]
byh = {p['handle']: p for p in live}
pre = lambda s: s.split('_')[0]

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
for r in U + P:
    if r['_h'] == r['Handle']: first.setdefault(r['Handle'], r)

UPD_H = ['ID', 'Handle', 'Title', 'Variant ID', 'Variant Command', 'Option1 Name', 'Option1 Value', 'Option2 Name',
         'Option2 Value', 'Variant SKU', 'Variant Price', 'Variant Compare At Price',
         'Metafield: title_tag [string]', 'Metafield: description_tag [string]', 'Old Handle', 'Old Price', 'Aug 19 Price (if different)', 'Review Note']
NEWV_H = ['ID', 'Handle', 'Variant Command', 'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value',
          'Variant SKU', 'Variant Price', 'Variant Cost', 'Variant Inventory Policy', 'Variant Fulfillment Service',
          'Variant Requires Shipping', 'Variant Taxable', 'Variant Grams', 'Variant Weight Unit', 'Plan', 'Aug 19 Price (if different)', 'Review Note']
NEWP_H = ['Handle', 'Command', 'Title', 'Body HTML', 'Vendor', 'Type', 'Tags', 'Status', 'Published',
          'Image Src', 'Image Alt Text', 'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value',
          'Variant SKU', 'Variant Price', 'Variant Cost', 'Variant Inventory Policy', 'Variant Fulfillment Service',
          'Variant Requires Shipping', 'Variant Taxable', 'Variant Grams', 'Variant Weight Unit',
          'Metafield: title_tag [string]', 'Metafield: description_tag [string]',
          'Custom Collections', 'Plan', 'Collection copied from', 'Aug 19 Price (if different)', 'Review Note']

# --- backup export (today): manual collections + redirects
from openpyxl import load_workbook as _lw
_bk = _lw('backups/Export-2026-11-18-031049.xlsx', read_only=True)
def _rows(n):
    it = _bk[n].iter_rows(values_only=True); h = list(next(it)); return [dict(zip(h, r)) for r in it]
custom = C.defaultdict(list)  # product handle -> manual collections
for r in _rows('Custom Collections'):
    if r['Product: Handle'] and r['Handle'] != 'popular': custom[r['Product: Handle']].append(r['Handle'])
REDIRECTS = _rows('Redirects')

# --- Prices (Charlie #12): Sep 4 "Plan 1" list is final; Aug 19 CSV price only where Sep 4 has no row.
# Sep 4 names differ: "China mainland" = "China", "Hong Kong (China)" = "Hong Kong"; it names both Central Asia
# products "Central Asia" - the 2nd block is "Central Asia (4 areas)" (matches its pre-Oct 6 prices).
s4name = lambda n: n.replace('China mainland', 'China').replace('Hong Kong (China)', 'Hong Kong')
_g1, _g2 = C.defaultdict(list), C.defaultdict(list)
for r in U: _g1[r['_o1']].append(r)
for d in csv.DictReader(open('client/esimnow_Daily_Plan_1.csv', encoding='utf-8-sig')): _g2[s4name(d['Option1 Value'])].append(d)
for k in list(_g2):
    if k.startswith('Central Asia ') and len(_g2[k]) == 2 * len(_g1.get(k, [])):
        n = len(_g2[k]) // 2; _g2['Central Asia (4 areas) ' + k[13:]] = _g2[k][n:]; _g2[k] = _g2[k][:n]
SEP4 = {}  # Daily rows have no days column: matched by position within each Option1 group (both lists are 1 -> 30 days)
for k, rr in _g1.items():
    if len(rr) == len(_g2.get(k, [])):
        for r, d in zip(rr, _g2[k]): SEP4[('U', r['Variant SKU'], r['Option2 Value'])] = d
_ca4 = False
for d in csv.DictReader(open('client/esimnow_Prepaid_Plan_1.csv', encoding='utf-8-sig')):
    n = s4name(d['Option1 Value'])
    if n.startswith('Central Asia ') and ('P', n) in SEP4: _ca4 = True
    if _ca4 and n.startswith('Central Asia '): n = 'Central Asia (4 areas) ' + n[13:]
    SEP4[('P', n)] = d
s4key = lambda r, plan: ('U', r['Variant SKU'], r['Option2 Value']) if plan == 'Unlimited' else ('P', r['_o1'])
PRICE_DIFF = []  # rows where the two lists differ (tab 8)
for plan, rows in (('Unlimited', U), ('Prepaid', P)):
    for r in rows:
        r['_aug'] = r['Variant Price']; d = SEP4.get(s4key(r, plan))
        r['_src'] = 'Sep 4' if d else 'Aug 19'
        if d:
            if abs(float(d['Selling Price']) - float(r['Variant Price'])) > .001: PRICE_DIFF.append((plan, r, d['Selling Price']))
            r['Variant Price'], r['Cost per Item'] = d['Selling Price'], d['Cost per Item']
def aug(r, plan=None):
    return r['_aug'] if abs(float(r['_aug']) - float(r['Variant Price'])) > .001 else ''

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
                    aug(r), ''])
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
                    r['Variant Taxable'], r['Variant Grams'], r['Variant Weight Unit'], plan, aug(r),
                    'New variant on existing product (live: %s)' % lh])
    return out

ukey = lambda r: (r['Variant SKU'], r['Option2 Value'])
pkey = lambda r: r['Variant SKU']
unl_upd = upd_rows(U, ULV, ukey, {OCEANIA}, 'Unlimited')
unl_newv = newv_rows(U, ULV, ukey, {OCEANIA}, 'Unlimited')
# prepaid: the 4 products still on old URLs (tab 4); price-only changes on the rest go to tab 7 (rollback) or tab 9 (review)
handle_of = {p['id']: p['handle'] for p in LP}
_pre_all = upd_rows(P, PLV, pkey, set(), 'Prepaid')
pre_upd = [x for x in _pre_all if handle_of[x[0]] in PREPAID_TODO]
pre_newv = newv_rows(P, PLV, pkey, set(), 'Prepaid')

# --- Samoa (Charlie #12): flag both plans for a quick check before import
is_samoa = lambda o1: str(o1).startswith('Samoa ')
byh_id = {p['id']: p['handle'] for p in live}

# --- prepaid price changes on products already updated Oct 6 (Charlie #12)
from openpyxl import load_workbook as _lw2
_ws = _lw2('backups/Export-2026-10-06-015327.xlsx', read_only=True)['Products']
_it = _ws.iter_rows(values_only=True); _hd = list(next(_it))
PRE_OCT6 = {r[_hd.index('Variant SKU')]: r[_hd.index('Variant Price')] for r in _it if r[_hd.index('Variant SKU')]}
ROLL_H = ['ID', 'Handle', 'Variant ID', 'Variant Command', 'Variant SKU', 'Variant Price', 'Plan Name', 'Live Price',
          'Price before Oct 6', 'Aug 19 Price', 'Review Note']
roll, review = [], []
_prow = {r['Variant SKU']: r for r in P}
for x in _pre_all:
    if handle_of[x[0]] in PREPAID_TODO or x[15] == '': continue  # tab 4, or no price change
    sku, new, live_p = x[9], x[10], x[15]
    before = PRE_OCT6.get(sku)
    row = [x[0], handle_of[x[0]], x[3], 'MERGE', sku, new, x[6], live_p, before if before is not None else '', _prow[sku]['_aug']]
    if is_samoa(x[6]):
        review.append(['Prepaid'] + row + ['SAMOA - Sep 4 price is much higher than live. Check before import (Charlie #12).'])
    elif sku.startswith('CA-4_'):
        review.append(['Prepaid'] + row + ['Was this Sep 4 price before Oct 6, same as tab 7. The Sep 4 file names this product just "Central Asia".'])
    elif before is not None and abs(float(before) - float(new)) < .001:
        roll.append(row + ['Back to Sep 4 price (was this price before the Oct 6 update).'])
    else:
        review.append(['Prepaid'] + row + ['Sep 4 price was never live (live and pre-Oct 6 prices differ from it).'])
for x in unl_upd:
    if is_samoa(x[6]) and x[15] != '':
        review.append(['Unlimited', x[0], x[1], x[3], 'MERGE', x[9], x[10], '%s / %s days' % (x[6], x[8]), x[15], '',
                       {ukey(r): r for r in U}[(x[9], x[8])]['_aug'], 'SAMOA - in tab 1 import.'])
for plan, rows in (('Unlimited', unl_newv), ('Prepaid', pre_newv)):
    for x in rows:
        if is_samoa(x[4]):
            name = x[4] + (' / %s days' % x[6] if plan == 'Unlimited' else '')
            review.append([plan, x[0], byh_id[x[0]], '', 'NEW', x[7], x[8], name, '', '', x[8],
                           'SAMOA - new plan, only in the Aug 19 CSV (no Sep 4 price). Held out of tab 2 until approved.'])
unl_newv = [x for x in unl_newv if not is_samoa(x[4])]
pre_newv = [x for x in pre_newv if not is_samoa(x[4])]
REVIEW_H = ['Plan'] + ROLL_H

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
                         (src or 'NEEDS PICK') if t else '', aug(r), note if t else ''])

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
_s4p = {k[1] for k in SEP4 if k[0] == 'P'}
for s, (p, v) in sorted(PLV.items()):
    if s not in {r['Variant SKU'] for r in P}:
        if s4name(re.sub(r'^Philippine ', 'Philippines ', v['o1'])) in _s4p:
            raise SystemExit('Prepaid %s is in Sep 4 list - keep at Sep 4 price (Charlie #12), handle manually' % s)
        rem.append([p['id'], p['handle'], '', v['id'], 'DELETE', v['sku'], v['o1'], v['o2'], '', '',
                    'Not in either price list (Aug 19 or Sep 4), so removed (Charlie #12).'])

# --- redirects: repoint existing redirects whose target is a handle we are changing (avoid chains)
RED_H = ['ID', 'Path', 'Command', 'Target', 'Old Target', 'Review Note']
new_of = {old: new for new, old in csv_to_live.items() if list(csv_to_live.values()).count(old) == 1}
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

# --- price check: every variant where the Aug 19 and Sep 4 lists differ (Sep 4 used)
PC_H = ['Plan', 'Option1 Value', 'Days', 'Live Price', 'Aug 19 CSV Price', 'Sep 4 Price (used)']
pc = []
for plan, r, s4p in PRICE_DIFF:
    lv = ULV.get(ukey(r)) if plan == 'Unlimited' else PLV.get(r['Variant SKU'])
    pc.append([plan, r['Option1 Value'], r['Option2 Value'] if plan == 'Unlimited' else '', lv[1]['price'] if lv else '', r['_aug'], s4p])

# --- write
wb = Workbook(); wb.remove(wb.active)
readme = [
    ['eSIMnow - Daily Unlimited CSV + remaining Prepaid items (AC #133 / 510599)'],
    ['Rebuilt 2026-11-20 per Charlie #12 from client CSVs (Aug 19 + Sep 4 price lists) and the live store. Nothing has been imported yet.'],
    [''],
    ['Tab', 'Rows', 'What it does'],
    ['1 Unlimited Update', len(unl_upd), 'Existing unlimited products: new URL, title, SEO title, meta description, prices. Old URL redirects automatically (Matrixify). Includes the 5 products the CSV split in two (kept as one product, typos fixed: "Philippine", "Cayman lslands").'],
    ['2 New Variants', len(unl_newv) + len(pre_newv), 'New plans added to existing products (unlimited + prepaid).'],
    ['3 New Products', len(newp), '15 unlimited + 15 prepaid new products. Description/image/tags from client CSV; collection copied from closest product (column).'],
    ['4 Prepaid Remaining', len(pre_upd), 'China, Hong Kong, North Macedonia, Vietnam prepaid: new URLs + old prices fixed.'],
    ['5 Removals', len(rem), 'Oceania Orange + 8 Vietnam unlimited variants + Prepaid Philippines 3GB 30Days (in neither price list, Charlie #12).'],
    ['6 Redirects', len(red), 'Existing redirects that point to a URL we are changing, repointed to the new URL so there are no redirect chains. Plus Oceania Orange.'],
    ['7 Prepaid Back to Sep 4', len(roll), 'Prepaid variants lowered by the Oct 6 update, back to their Sep 4 price (= their price before Oct 6).'],
    ['8 Price Check Sep 4', len(pc), 'Every variant where the Aug 19 and Sep 4 lists differ. Sep 4 price is used.'],
    ['9 Review Before Import', len(review), 'NOT in import until approved: the other 8 Prepaid price changes, and Samoa (both plans, Charlie #12).'],
    [''],
    ['PRICES: Sep 4 list is final (Charlie #12). Variant Price = Sep 4 price; Aug 19 CSV price only where the Sep 4 list has no row. Column "Aug 19 Price (if different)" shows the old CSV price for reference.'],
    ['Sep 4 names matched: "China mainland" = "China", "Hong Kong (China)" = "Hong Kong"; the 2nd "Central Asia" block in the Sep 4 files = "Central Asia (4 areas)".'],
    [''],
    ['Import order: 1 -> 4 -> 2 -> 3 -> 7 -> 5 -> 6 (+ approved rows from 9). Take a fresh full backup right before import.'],
]
for name, head, rows in [('README', None, readme), ('1 Unlimited Update', UPD_H, unl_upd), ('2 New Variants', NEWV_H, unl_newv + pre_newv),
                         ('3 New Products', NEWP_H, newp), ('4 Prepaid Remaining', UPD_H, pre_upd), ('5 Removals', REM_H, rem), ('6 Redirects', RED_H, red),
                         ('7 Prepaid Back to Sep 4', ROLL_H, roll), ('8 Price Check Sep 4', PC_H, pc), ('9 Review Before Import', REVIEW_H, review)]:
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
print('rem', len(rem), 'red', len(red), 'roll', len(roll), 'review', len(review), 'pricecheck', len(pc))
print('price source', C.Counter((pl, r['_src']) for pl, rows in (('U', U), ('P', P)) for r in rows))
for x in review: print('  REVIEW', x[0], x[7], 'live', x[8], 'pre-Oct6', x[9], 'aug', x[10], '-> new', x[6])
print('MISSING closest:', missing)
