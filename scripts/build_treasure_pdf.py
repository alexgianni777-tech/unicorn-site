"""Optional asset builder: requires reportlab; not part of the HTML build."""
from pathlib import Path
from math import sin, cos, pi
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

DEST=Path(__file__).resolve().parents[1]/'assets/downloads/unicorn-treasure-hunt.pdf'
NAMES=['Star','Heart','Moon','Rainbow','Cloud','Crystal']
W,H=A4
c=canvas.Canvas(str(DEST),pagesize=A4,invariant=1)
c.setTitle('Free Unicorn Treasure Hunt - Cards and Player Sheet')
c.setAuthor('Unicorn Finds')

def icon(name,x,y,size):
 c.saveState();c.translate(x,y);c.scale(size/100,size/100);c.setFillColorRGB(.16,.12,.2);c.setStrokeColorRGB(.16,.12,.2)
 p=c.beginPath()
 if name=='Star':
  for i in range(10):
   a=pi/2+i*pi/5;r=43 if i%2==0 else 20;px=50+cos(a)*r;py=50+sin(a)*r
   if i==0:p.moveTo(px,py)
   else:p.lineTo(px,py)
  p.close();c.drawPath(p,fill=1,stroke=0)
 elif name=='Heart':
  p.moveTo(50,10);p.curveTo(30,27,7,42,8,65);p.curveTo(9,91,37,98,50,77);p.curveTo(63,98,91,91,92,65);p.curveTo(93,42,70,27,50,10);c.drawPath(p,fill=1,stroke=0)
 elif name=='Moon':
  c.circle(48,50,41,fill=1,stroke=0);c.setFillColorRGB(1,1,1);c.circle(68,64,36,fill=1,stroke=0)
 elif name=='Rainbow':
  c.setLineWidth(9)
  for r in [37,23,9]:c.arc(50-r,45-r,50+r,45+r,0,180);c.line(50-r,45,50-r,17);c.line(50+r,45,50+r,17)
 elif name=='Cloud':
  for cx,cy,r in [(25,39,19),(41,57,25),(67,47,22),(79,35,14)]:c.circle(cx,cy,r,fill=1,stroke=0)
  c.rect(24,21,55,20,fill=1,stroke=0)
 else:
  for i,(px,py) in enumerate([(50,94),(77,72),(77,29),(50,6),(23,29),(23,72)]):
   if i==0:p.moveTo(px,py)
   else:p.lineTo(px,py)
  p.close();c.drawPath(p,fill=1,stroke=0);c.setStrokeColorRGB(1,1,1);c.setLineWidth(2);c.line(23,72,77,72);c.line(23,72,50,6);c.line(77,72,50,6);c.line(50,94,50,6)
 c.restoreState()

def text(x,y,value,size=11,bold=False):
 c.setFillColorRGB(.16,.12,.2);c.setFont('Helvetica-Bold' if bold else 'Helvetica',size);c.drawString(x,y,value)
def footer(n):
 text(40,30,'Free for personal party use | unicornsite.online',9)
 c.linkURL('https://unicornsite.online/tools/unicorn-treasure-hunt.html',(40,27,330,42),relative=0)
 text(W-70,30,str(n),9)
# Enough margin for both A4 and fit-to-page Letter printing.
text(40,H-48,'UNICORN TREASURE HUNT',24,True)
text(40,H-72,'Six hiding cards',14,True)
text(40,H-93,'Adult: cut along the dotted borders. Hide cards in easy-to-reach places.',10)
text(40,H-109,'Players find the pictures and tick their sheet. Leave hiding cards in place.',10)
cw=(W-94)/2;ch=194
for i,name in enumerate(NAMES):
 x=40+(i%2)*(cw+14);y=H-137-(i//2+1)*ch
 c.setStrokeColorRGB(.55,.5,.57);c.setDash(3,3);c.roundRect(x,y,cw,ch-12,8,stroke=1,fill=0);c.setDash()
 icon(name,x+(cw-83)/2,y+70,83)
 c.setFont('Helvetica-Bold',16);c.drawCentredString(x+cw/2,y+45,name)
 c.setFont('Helvetica',9);c.drawCentredString(x+cw/2,y+25,'Unicorn hunt - leave this card here')
footer(1);c.showPage()
text(40,H-48,'MY UNICORN TREASURE HUNT',23,True)
text(40,H-83,'Name / team: ______________________________________',12)
text(40,H-111,'Find each picture and tick its box. Leave the hiding cards where they are.',10)
for i,name in enumerate(NAMES):
 x=40+(i%2)*(cw+14);y=H-144-(i//2+1)*164
 c.setStrokeColorRGB(.65,.61,.67);c.roundRect(x,y,cw,148,8,stroke=1,fill=0)
 c.rect(x+16,y+64,17,17,stroke=1,fill=0);icon(name,x+52,y+49,76)
 text(x+52,y+25,name,14,True)
text(40,145,'I found all six magical symbols!',20,True)
text(40,117,'Play together, help each other and celebrate when everyone finishes.',10)
text(40,91,'More free games: unicornsite.online/tools/free-unicorn-games.html',9)
footer(2);c.save()
print(DEST)
