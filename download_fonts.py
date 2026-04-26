import urllib.request, zipfile, os, io, shutil

fonts_dir = 'weighmaster/assets/fonts'
os.makedirs(fonts_dir, exist_ok=True)

def dl_zip(url, picks):
    try:
        print(f'Downloading {url.split("/")[-1]} ...')
        with urllib.request.urlopen(url, timeout=30) as r:
            data = r.read()
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            for name in z.namelist():
                base = os.path.basename(name)
                if base in picks:
                    dest = os.path.join(fonts_dir, base)
                    with z.open(name) as src, open(dest, 'wb') as dst:
                        shutil.copyfileobj(src, dst)
                    print(f'  + {base}')
    except Exception as e:
        print(f'  WARNING: {e}')

dl_zip(
    'https://github.com/JetBrains/JetBrainsMono/releases/download/v2.304/JetBrainsMono-2.304.zip',
    {'JetBrainsMono-Regular.ttf', 'JetBrainsMono-Bold.ttf'}
)
dl_zip(
    'https://github.com/googlefonts/dm-fonts/releases/download/v1.100/fonts-dm-sans.zip',
    {'DMSans-Regular.ttf', 'DMSans-SemiBold.ttf', 'DMSans-Bold.ttf'}
)
print('Fonts done.')
