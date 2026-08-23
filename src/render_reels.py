import json, subprocess
from pathlib import Path
from PIL import Image

def make_vertical(src,dst):
    im=Image.open(src).convert("RGB"); W,H=1080,1920
    scale=max(W/im.width,H/im.height)
    im=im.resize((int(im.width*scale),int(im.height*scale)),Image.Resampling.LANCZOS)
    x=(im.width-W)//2; y=(im.height-H)//2
    im.crop((x,y,x+W,y+H)).save(dst,"JPEG",quality=93)

def render(car, base):
    tmp=base/"reel_frames"; tmp.mkdir(parents=True,exist_ok=True)
    slides=sorted((base/"carousel").glob("*.jpg"))[:6]
    frames=[]
    for i,p in enumerate(slides):
        out=tmp/f"{i:02d}.jpg"; make_vertical(p,out); frames.append(out)
    clips=[]
    for i,p in enumerate(frames):
        clip=tmp/f"clip_{i:02d}.mp4"
        z="min(zoom+0.0012,1.12)" if i%2==0 else "if(lte(zoom,1.0),1.12,max(1.0,zoom-0.0012))"
        vf=("zoompan=z='"+z+"':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=90:s=1080x1920:fps=30,fade=t=in:st=0:d=0.25,fade=t=out:st=2.7:d=0.3")
        cmd=["ffmpeg","-y","-loop","1","-i",str(p),"-vf",vf,"-t","3","-r","30","-c:v","libx264","-pix_fmt","yuv420p","-preset","veryfast","-crf","20",str(clip)]
        subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); clips.append(clip)
    listfile=tmp/"concat.txt"
    listfile.write_text("\n".join([f"file '{c.resolve()}'" for c in clips]),encoding="utf-8")
    final=base/f"{car['slug']}_reel.mp4"
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(listfile),"-c:v","libx264","-pix_fmt","yuv420p","-movflags","+faststart","-preset","veryfast","-crf","20",str(final)],check=True)
    return final

if __name__=="__main__":
    cars=json.loads(Path("data/cars.json").read_text(encoding="utf-8"))
    for car in cars: render(car,Path("work")/car["slug"])
