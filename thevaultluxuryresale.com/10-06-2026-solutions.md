# 10-06-2026 — Solutions — thevaultluxuryresale.com

Store: Shopify `vault-luxury-resale.myshopify.com` on `shop.thevaultluxuryresale.com`. Root and www use GoDaddy forwarding (homepage only). Details: [10-06-2026-log.md](10-06-2026-log.md).

## Access required
1. **Google Sheet:** share the redirect sheet with web@smartsites.com (Viewer is enough). It's private right now.
2. **Shopify:** a collaborator or staff account on `vault-luxury-resale.myshopify.com` with:
   - **Online Store → Navigation**: this is where URL redirects live (Content → Menus → URL redirects; bulk CSV import with "Redirect from" and "Redirect to" columns).
   - **Products, Collections and Pages (view)**: to confirm each target URL exists.
   - **Domains** (Settings → Domains): only if the root domain is connected (item 3).
3. **GoDaddy (domain and DNS):** Delegate Access for web@smartsites.com, "Products, Domains & DNS" level. Needed **only if** the sheet's old URLs are on `thevaultluxuryresale.com` / `www`:
   - Turn off GoDaddy forwarding.
   - Connect the root and www to Shopify as extra domains: A `@` → `23.227.38.65`, CNAME `www` → `shops.myshopify.com`.
   - Shopify then sends every root/www path to `shop.` with the path kept, and the URL redirects work on them.
   - Keep the Proofpoint MX and all other records unchanged.
4. **Google Search Console (optional):** the root and shop properties, to check old URLs after launch and submit the sitemap.

## Notes on the fix
- Shopify URL redirects only fire when the old path returns 404 on the store. They can't override a live product, collection or page URL.
- Shopify redirects are path-only (`/old-path` → `/new-path` or a full URL). Strip the domain from the "from" column before importing.
- Which access items apply depends on which domain the sheet's "from" URLs use. Review the sheet once it's shared.

## Comment
[10-06-2026-comment.txt](10-06-2026-comment.txt)
