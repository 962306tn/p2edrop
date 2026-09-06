#!/usr/bin/env python3
"""Inline the page's CSS and JS into one self-contained file.

index.html loads four stylesheets and a script by path, which is right for
development and useless for handing someone a single file. This folds them in,
keeping the ids and the media="not all" parking so the skin switcher and the
pre-paint script keep working untouched.

    python3 build-standalone.py     # writes velahush-standalone.html
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = 'velahush-standalone.html'

# (link tag to replace, file to inline, extra attributes to keep on the <style>)
SHEETS = [
    ('<link id="skin-modernist-tokens" rel="stylesheet" href="ds-modernist.css">',
     'ds-modernist.css', 'id="skin-modernist-tokens"'),
    ('<link id="skin-modernist" rel="stylesheet" href="velahush.css">',
     'velahush.css', 'id="skin-modernist"'),
    ('<link id="skin-cupertino-tokens" rel="stylesheet" href="../../design-system/dist/cupertino.css" media="not all">',
     '../../design-system/dist/cupertino.css', 'id="skin-cupertino-tokens" media="not all"'),
    ('<link id="skin-cupertino" rel="stylesheet" href="velahush-cupertino.css" media="not all">',
     'velahush-cupertino.css', 'id="skin-cupertino" media="not all"'),
]
SCRIPT = ('<script src="velahush.js"></script>', 'velahush.js')


def read(path):
    return io.open(os.path.join(HERE, path), encoding='utf-8').read()


def main():
    page = read('index.html')
    for tag, path, attrs in SHEETS:
        if tag not in page:
            raise SystemExit('index.html no longer contains: %s' % tag)
        page = page.replace(tag, '<style %s>\n%s\n</style>' % (attrs, read(path)))
    tag, path = SCRIPT
    if tag not in page:
        raise SystemExit('index.html no longer contains: %s' % tag)
    page = page.replace(tag, '<script>\n%s\n</script>' % read(path))

    io.open(os.path.join(HERE, OUT), 'w', encoding='utf-8').write(page)
    print('%s — %d bytes' % (OUT, len(page.encode('utf-8'))))


if __name__ == '__main__':
    main()
