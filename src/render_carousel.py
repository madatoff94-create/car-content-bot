import json, zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

W,H=3840,4800
FONT_BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def fit_cover(img,w,h):
    img=img.convert("RGB")
    scale=max(w/img.width,h/img.height)
    nw,nh=int(img.width*scale),int(img.height*scale)
    img=img.resize((nw,nh),Image.Resampling.LANCZOS)
    x=(nw-w)//2; y=(nh-h)//2
    return img.crop((x,y,x+w,y+h))

def wrap(draw, text, font, max_width):
    words=text.split(); lines=[]; line=""
    for word in words:
        test=(line+" "+word).strip()
        if draw.textbbox((0,0),test,font=font)[2] <= max_width:
            line=test
        else:
            if line: lines.append(line)
            line=word
    if line: lines.append(line)
    return lines

def render(car, rawdir, outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    imgs=sorted(rawdir.glob("*.jpg"))[:12]
    title_font=ImageFont.truetype(FONT_BOLD,150)
    label_font=ImageFont.truetype(FONT_BOLD,70)
    body_font=ImageFont.truetype(FONT,62)
    small_font=ImageFont.truetype(FONT,44)
    for i in range(12):
        base=fit_cover(Image.open(imgs[i]),W,H)
        base=ImageEnhance.Contrast(base).enhance(1.06)
        overlay=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(overlay)
        od.rectangle((0,0,W,620),fill=(0,0,0,135))
        od.rounded_rectangle((170,3100,W-170,H-180),radius=70,fill=(5,5,8,210))
        canvas=Image.alpha_composite(base.convert("RGBA"),overlay); d=ImageDraw.Draw(canvas)
        d.text((190,150),car["name"],font=title_font,fill="white")
        d.text((190,390),f"{i+1:02d} / 12",font=small_font,fill=(230,230,230))
        y=3260
        for label,text in [("UZ",car["slides"]["uz"][i]),("RU",car["slides"]["ru"][i]),("EN",car["slides"]["en"][i])]:
            d.text((250,y),label,font=label_font,fill=(255,255,255))
            lines=wrap(d,text,body_font,W-750); yy=y
            for line in lines[:2]:
                d.text((570,yy),line,font=body_font,fill=(245,245,245)); yy+=82
            y=max(y+245,yy+55)
        fp=outdir/f"{i+1:02d}_{car['slug']}.jpg"
        canvas.convert("RGB").save(fp,"JPEG",quality=94,subsampling=0,optimize=True)
    s=car["specs"]
    caption=f"""🚘 {car['name']}

🇺🇿
Quvvat: {s['power']}
Moment: {s['torque']}
0–100 km/soat: {s['zero_100']}
Maksimal tezlik: {s['top_speed']}
Dvigatel: {s['engine']}
Uzatma: {s['transmission']}
Tortish: {s['drivetrain']}

🇷🇺
Мощность: {s['power']}
Крутящий момент: {s['torque']}
0–100 км/ч: {s['zero_100']}
Макс. скорость: {s['top_speed']}
Силовая установка: {s['engine']}
Коробка: {s['transmission']}
Привод: {s['drivetrain']}

🇬🇧
Power: {s['power']}
Torque: {s['torque']}
0–100 km/h: {s['zero_100']}
Top speed: {s['top_speed']}
Powertrain: {s['engine']}
Transmission: {s['transmission']}
Drivetrain: {s['drivetrain']}

Source for technical data: {car['source']}

#cars #carsofinstagram #automotive #4kcars #supercars #luxurycars #avtomobil #авто
"""
    (outdir.parent/f"{car['slug']}_caption.txt").write_text(caption,encoding="utf-8")
    cr=rawdir/"credits.txt"
    if cr.exists():
        (outdir.parent/f"{car['slug']}_image_credits.txt").write_text(cr.read_text(encoding="utf-8"),encoding="utf-8")
    zip_path=outdir.parent/f"{car['slug']}_carousel.zip"
    with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as z:
        for p in sorted(outdir.glob("*.jpg")): z.write(p,p.name)
        if cr.exists(): z.write(cr,"credits.txt")
    return zip_path

if __name__=="__main__":
    cars=json.loads(Path("data/cars.json").read_text(encoding="utf-8"))
    for car in cars:
        base=Path("work")/car["slug"]
        render(car,base/"raw",base/"carousel")
