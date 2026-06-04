from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path

W = H = 1024
img = Image.new('RGB', (W, H), '#f7efe5')
d = ImageDraw.Draw(img)

# soft background gradient
for y in range(H):
    r = int(247 - y * 0.03)
    g = int(239 - y * 0.04)
    b = int(229 - y * 0.02)
    d.line([(0, y), (W, y)], fill=(max(r,220), max(g,205), max(b,195)))

# window light glow
for radius, alpha in [(360, 45), (280, 55), (200, 70)]:
    glow = Image.new('RGBA', (W, H), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((120-radius//2, 70-radius//2, 120+radius//2, 70+radius//2), fill=(255,245,210,alpha))
    img = Image.alpha_composite(img.convert('RGBA'), glow)

# shadow
shadow = Image.new('RGBA', (W, H), (0,0,0,0))
sd = ImageDraw.Draw(shadow)
sd.ellipse((240, 740, 790, 890), fill=(80,55,45,55))
shadow = shadow.filter(ImageFilter.GaussianBlur(28))
img = Image.alpha_composite(img, shadow)

d = ImageDraw.Draw(img)

# cat body and head
fur = '#d98742'
fur_dark = '#9c5426'
fur_light = '#efb36e'
cream = '#ffe2bd'
outline = '#5b321f'

d.ellipse((315, 430, 730, 850), fill=fur, outline=outline, width=7)
d.ellipse((280, 220, 760, 665), fill=fur, outline=outline, width=8)

# ears
d.polygon([(340, 285), (405, 95), (490, 305)], fill=fur, outline=outline)
d.line([(340,285),(405,95),(490,305)], fill=outline, width=8, joint='curve')
d.polygon([(550, 305), (635, 95), (710, 285)], fill=fur, outline=outline)
d.line([(550,305),(635,95),(710,285)], fill=outline, width=8, joint='curve')
d.polygon([(392, 255), (412, 155), (462, 285)], fill='#f2a0a8')
d.polygon([(588, 285), (628, 155), (653, 255)], fill='#f2a0a8')

# muzzle/chest
d.ellipse((405, 420, 635, 610), fill=cream, outline=None)
d.ellipse((415, 585, 650, 820), fill=cream, outline=None)

# stripes
for box in [(355,285,455,315),(585,285,685,315),(330,365,430,395),(610,365,720,395)]:
    d.arc(box, 190, 345, fill=fur_dark, width=9)
for x in [470, 510, 550]:
    d.line([(x,235),(x-20,325)], fill=fur_dark, width=8)
# cheek stripes
for yy in [455, 495, 535]:
    d.line([(380, yy), (300, yy-25)], fill=fur_dark, width=7)
    d.line([(660, yy), (740, yy-25)], fill=fur_dark, width=7)

# eyes
d.ellipse((395, 355, 485, 450), fill='#77c66e', outline=outline, width=5)
d.ellipse((555, 355, 645, 450), fill='#77c66e', outline=outline, width=5)
d.ellipse((430, 365, 455, 445), fill='#172018')
d.ellipse((590, 365, 615, 445), fill='#172018')
d.ellipse((438, 373, 448, 386), fill='white')
d.ellipse((598, 373, 608, 386), fill='white')

# nose/mouth
d.polygon([(510,470),(535,470),(522,488)], fill='#d76f7b', outline=outline)
d.line([(522,488),(522,515)], fill=outline, width=4)
d.arc((485,500,522,535), 0, 160, fill=outline, width=4)
d.arc((522,500,560,535), 20, 180, fill=outline, width=4)

# whiskers
for yy in [475, 505, 535]:
    d.line([(500, yy), (295, yy-35)], fill=outline, width=3)
    d.line([(545, yy), (750, yy-35)], fill=outline, width=3)

# paws
for box in [(370,735,500,875),(555,735,685,875)]:
    d.ellipse(box, fill=fur_light, outline=outline, width=5)

# tail
d.arc((610, 455, 920, 825), 75, 260, fill=outline, width=54)
d.arc((610, 455, 920, 825), 75, 260, fill=fur, width=42)

# highlights
highlight = Image.new('RGBA', (W,H), (0,0,0,0))
hd = ImageDraw.Draw(highlight)
hd.ellipse((365,260,460,350), fill=(255,220,155,40))
hd.ellipse((465,610,575,760), fill=(255,255,255,35))
highlight = highlight.filter(ImageFilter.GaussianBlur(14))
img = Image.alpha_composite(img, highlight)

out = Path('/Users/advaithbharadwaj/PythonProjects/Pythios/cat.png')
img.convert('RGB').save(out, quality=95)
print(out)
