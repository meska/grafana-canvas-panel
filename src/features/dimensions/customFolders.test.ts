import { getCustomFolders } from './customFolders';
import { MediaType } from './types';

const index = {
  folders: {
    common: ['logo.png', 'arrow.svg', 'notes.txt'],
    'org-1': ['plan.jpg'],
    'org-2': ['secret.png'],
  },
};

describe('getCustomFolders', () => {
  it('returns common plus the current org only', () => {
    const folders = getCustomFolders(index, 1, MediaType.Image);
    expect(folders.map((f) => f.value)).toEqual(['/public/img/custom/common', '/public/img/custom/org-1']);
  });

  it('never exposes another org folder', () => {
    const all = getCustomFolders(index, 1, MediaType.Image).flatMap((f) => f.files);
    expect(all).not.toContain('secret.png');
  });

  it('filters non-images, and keeps only svg for icons', () => {
    expect(getCustomFolders(index, 3, MediaType.Image)[0].files).toEqual(['arrow.svg', 'logo.png']);
    expect(getCustomFolders(index, 3, MediaType.Icon)[0].files).toEqual(['arrow.svg']);
  });

  it('skips folders missing from the index and tolerates no index', () => {
    expect(getCustomFolders(index, 9, MediaType.Image).map((f) => f.label)).toEqual(['Shared (common)']);
    expect(getCustomFolders(undefined, 1, MediaType.Image)).toEqual([]);
  });
});
