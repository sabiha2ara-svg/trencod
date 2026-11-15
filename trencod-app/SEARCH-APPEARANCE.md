# Trencod 0.12.1 — Search appearance

The homepage now includes one descriptive title, one meta description, a canonical homepage URL, Open Graph metadata and WebSite structured data naming Trencod. Google verification is preserved. The first HTML response contains an actual introduction rather than “Connecting to Trencod…”. Login text, footer boilerplate and loading messages are excluded from snippets using data-nosnippet wrappers.

After uploading this complete update and deploying the latest commit, check /healthz for 0.12.1. In Google Search Console inspect https://trencod.onrender.com/ and request indexing once. Google must recrawl/reprocess the page before its search result can change. It may choose different titles, snippets or site names; no instant change or ranking is promised.

The canonical and structured-data URL use the current trencod.onrender.com address. Update these if the site moves to a custom domain. This update includes the preceding My projects and music changes. No database reset or environment-variable change is needed.
