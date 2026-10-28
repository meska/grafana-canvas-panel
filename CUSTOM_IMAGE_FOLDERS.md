# Custom image folders (fork)

The resource picker's **Folder** tab also lists folders from a host directory, so users pick images instead of pasting URLs.

## Layout

Mount a host directory into Grafana at `/usr/share/grafana/public/img/custom` (read-only):

```
<host dir>/common/        shared by every organization
<host dir>/org-<orgId>-<slug>/   visible only when working in that organization (slug = org name, cosmetic; the id matches)
<host dir>/index.json     generated, read by the picker
```

Upload with SFTP/scp into `common/` or `org-<orgId>/`, mode `644` (Grafana runs as uid 472).

## Index

`scripts/custom-images-index.py <host dir> --grafana-db <grafana.db>` creates a folder for every organization (read-only access to the Grafana database, no credentials), renames bare `org-<id>` folders to `org-<id>-<slug>`, never deletes anything, and writes `index.json` (atomic, skips if unchanged). New organizations get their folder within a minute. Run it from cron every minute:

```
* * * * * /usr/bin/python3 /usr/local/bin/custom-images-index.py /srv/grafana-images --grafana-db /srv/grafana/grafana.db
```

## Notes

- The picker shows `common` plus the current org's folder only. This is a UI filter: files under `/public` are readable by anyone who knows the URL.
- Stored value is a site-root path (`/public/img/custom/org-1/x.png`); `getPublicOrAbsoluteUrl` resolves `/public/...` against Grafana's sub url.
- Icons: only `.svg`. Backgrounds/images: png, jpg, gif, webp, svg.
- Loading this fork in Grafana: unsigned plugin, so `GF_PLUGINS_ALLOW_LOADING_UNSIGNED_PLUGINS=canvas` and `GF_PLUGIN_CANVAS_AS_EXTERNAL=true`; put the built `dist/` in `<grafana data>/plugins/canvas`.
