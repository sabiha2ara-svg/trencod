# Trencod 0.16.1 — Public documentation

## Deploy
Upload the contents of this trencod-app folder into the existing GitHub trencod-app folder. Keep Render Root Directory as trencod-app. Deploy the latest commit. Do not upload database dumps, passwords or environment files.

## Check the release
Open /status and press Check now. It should report 0.16.1 after deployment. This is an on-demand app/database check, not independent uptime monitoring. External monitoring should check /healthz. Public documentation and health checks do not need a working login session, including during a database outage.

## Public pages
/about, /getting-started, /security, /privacy, /market-guide, /community, /changelog and /help are publicly readable. Help contains private feedback after login. The app footer links to the pages in new tabs to preserve the active editor. The docs include a public GitHub link without claiming any external audit or invented credentials.

## Google Search Console
1. Set TRENCOD_PUBLIC_URL to your actual public origin, such as https://trencod.onrender.com (no trailing path). On Render, RENDER_EXTERNAL_URL is the default if you omit it. Do not use an example domain.
2. Deploy; open /sitemap.xml. It should list the public home, Help and documentation URLs. If no public URL is configured, the sitemap deliberately returns 503 rather than inventing an address.
3. Open your verified Search Console property → Sitemaps → enter sitemap.xml and submit.
4. Use URL Inspection for /about, /security or /help → Test live URL → Request indexing if eligible.
5. Indexing is Google's decision and may take time. This app does not submit to Google automatically.

Private account/API URLs are excluded from the sitemap. robots.txt discourages API crawling; it is NOT an access-control mechanism. Authentication remains necessary. On Render free hosting, a sleeping service can receive Render's own robots response; this code cannot override that while asleep.

## Domain and infrastructure
A new domain needs DNS and Render custom-domain setup, HTTPS verification, then the correct public URL and Search Console property. Merely editing this variable does not provision a domain or certificate. CDN, paid hosting, automated backups and independent monitoring must be configured separately; none are purchased by this update. Do not cache authenticated API responses or private project data at a CDN. The default response cache policy remains no-store; a future static-asset caching change should be scoped and tested separately.

## Privacy notes for the owner
The privacy page describes current data handling and limitations. It does not invent a deletion workflow, guarantee backup retention or constitute legal compliance certification. Configure support reviewers (SUPPORT-AND-SECURITY.md), establish retention/deletion and backup procedures, then keep the public text synchronized with those practices. Do not publish private identity documents, personal addresses or credentials as proof of trust.
