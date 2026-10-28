import { config } from '@grafana/runtime';

import { MediaType } from './types';

/** Site-root path served by Grafana from the host-mounted directory (see scripts/custom-images-index.py). */
export const CUSTOM_IMAGES_ROOT = '/public/img/custom';

/** index.json written by scripts/custom-images-index.py: { folders: { common: ['a.png'], 'org-1': [...] } } */
export interface CustomIndex {
  folders: Record<string, string[]>;
}

export interface CustomFolder {
  /** Stored in the dashboard as `${value}/${filename}` (site-root path, resolved by getPublicOrAbsoluteUrl). */
  value: string;
  label: string;
  files: string[];
}

const IMAGE_EXT = /\.(png|jpe?g|gif|webp|svg)$/i;

export async function fetchCustomIndex(): Promise<CustomIndex | undefined> {
  try {
    const res = await fetch(`${config.appSubUrl}${CUSTOM_IMAGES_ROOT}/index.json`, { cache: 'no-store' });
    return res.ok ? ((await res.json()) as CustomIndex) : undefined;
  } catch {
    return undefined;
  }
}

/**
 * Folders the current org may see: `common` plus `org-<orgId>` or `org-<orgId>-<slug>` (the slug is cosmetic,
 * the id is what matches). This only filters the picker: files under /public are readable by anyone who knows the URL.
 */
export function getCustomFolders(
  index: CustomIndex | undefined,
  orgId: number | undefined,
  mediaType: MediaType,
  orgName?: string
) {
  const accept = (f: string) => (mediaType === MediaType.Icon ? /\.svg$/i.test(f) : IMAGE_EXT.test(f));
  const isOrg = (k: string) => orgId !== undefined && (k === `org-${orgId}` || k.startsWith(`org-${orgId}-`));
  return Object.keys(index?.folders ?? {})
    .filter((k) => k === 'common' || isOrg(k))
    .sort((a, b) => (a === 'common' ? -1 : b === 'common' ? 1 : a.localeCompare(b)))
    .map<CustomFolder>((k) => ({
      value: `${CUSTOM_IMAGES_ROOT}/${k}`,
      label: k === 'common' ? 'Shared (common)' : `This organization (${orgName || k})`,
      files: index!.folders[k].filter(accept).sort(),
    }));
}
