import { getCustomFolders } from './customFolders';
import { MediaType } from './types';

const index = {
  folders: {
    common: ['logo.png', 'arrow.svg', 'notes.txt'],
    'org-1-maric-automation-srl': ['plan.jpg'],
    'org-10-other': ['ten.png'],
    'org-2': ['secret.png'],
  },
};

describe('getCustomFolders', () => {
  it('returns common plus the current org only', () => {
    const folders = getCustomFolders(index, 1, MediaType.Image);
    expect(folders.map((f) => f.value)).toEqual([
      '/public/img/custom/common',
      '/public/img/custom/org-1-maric-automation-srl',
    ]);
  });

  it('never exposes another org folder', () => {
    const all = getCustomFolders(index, 1, MediaType.Image).flatMap((f) => f.files);
    expect(all).not.toContain('secret.png');
    expect(all).not.toContain('ten.png'); // org-10 must not match org 1
  });

  it('filters non-images, and keeps only svg for icons', () => {
    expect(getCustomFolders(index, 3, MediaType.Image)[0].files).toEqual(['arrow.svg', 'logo.png']);
    expect(getCustomFolders(index, 3, MediaType.Icon)[0].files).toEqual(['arrow.svg']);
  });

  it('labels the org folder with the org name', () => {
    expect(getCustomFolders(index, 1, MediaType.Image, 'Maric Automation Srl')[1].label).toEqual(
      'This organization (Maric Automation Srl)'
    );
  });

  it('skips folders missing from the index and tolerates no index', () => {
    expect(getCustomFolders(index, 9, MediaType.Image).map((f) => f.label)).toEqual(['Shared (common)']);
    expect(getCustomFolders(undefined, 1, MediaType.Image)).toEqual([]);
  });
});
