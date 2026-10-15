# Nadco ecommerce

Shopify theme for Nadco Tapes & Labels. Repo: github.com/theenghrajan/ecommerce.

- `shopnadco.com/nadco-theme/` — the theme (one folder per site, named by its URL). Base: **Hyper 1.3.2 by FoxEcom** (docs: https://docs.foxecom.com/hyper-theme), heavily customized.

## Commands (run inside `shopnadco.com/nadco-theme/`)

- `shopify theme dev --store <store>` — local preview with hot reload
- `shopify theme check` — lint Liquid before pushing
- `shopify theme push --unpublished` — upload as a new theme; never push to the live theme without asking
- `shopify theme pull` — sync admin edits (templates/*.json, config/settings_data.json) before editing them

## Conventions

- Before writing a new section/snippet/JS, look for an existing one in `sections/`, `snippets/`, `assets/` — Hyper ships ~110 sections.
- Custom (non-Hyper) sections: `custom-*.liquid`, `foil-tapes`, `vinyl-material`, `ebook-download-section`, `environmental-certification`, etc. They keep CSS inline (`{% style %}`/`<style>`) scoped by `section.id`, wrap content in `page-width`, and expose everything via `{% schema %}` settings/blocks.
- JS is vanilla custom elements guarded by `if (!customElements.get('x'))`. No frameworks, no jQuery.
- Load assets with `{{ 'file.css' | asset_url | stylesheet_tag }}`; JS with `defer`.
- Schema labels in Hyper use `t:` translation keys (locales/*.schema.json); custom sections use plain strings — fine either way.
- `templates/page.*.json` are mostly content pages (blogs/landing pages) created in the admin — prefer editing sections over hand-editing these JSONs; the admin overwrites them.
- Don't edit `config/settings_data.json` by hand unless asked; it's store state.

## Other sites

Per-site notes live in `<site>/CLAUDE.md` (loaded when working in that folder).
