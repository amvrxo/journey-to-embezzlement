import math, time, pygame
from pygame import Rect

# Canvas & style
WIDTH, HEIGHT, FPS = 960, 600, 120
CLICK_THRESHOLD = 5
BG = (18,18,18); WHITE=(255,255,255); TEXT=(220,220,220); GRAY=(150,150,150)
DARK=(32,32,32); ACCENT=(90,140,255); RED=(210,50,50); RED_H=(255,80,80)

clamp = lambda v,a,b: max(a,min(b,v))
def sqrlen(a,b): return a*a+b*b

# ui
class Button:
    def __init__(self, offset_rect: Rect, text: str, font):
        self.off = Rect(offset_rect); self.text=text; self.font=font
        self.abs = Rect(0,0,0,0); self.hover=False
    def place(self, client: Rect):
        self.abs = Rect(client.x+self.off.x, client.y+self.off.y, self.off.w, self.off.h)
    def draw(self, screen):
        pygame.draw.rect(screen,(45,45,45),self.abs,border_radius=6)
        pygame.draw.rect(screen,WHITE if self.hover else GRAY,self.abs,1,border_radius=6)
        t=self.font.render(self.text,True,TEXT)
        screen.blit(t,(self.abs.centerx-t.get_width()//2,self.abs.centery-t.get_height()//2))
    def handle(self,pos,down=False):
        self.hover=self.abs.collidepoint(pos); return self.hover and down
    def on_moved(self,dx,dy): self.abs.move_ip(dx,dy)

class BaseWindow:
    TITLE_H, RADIUS, BORDER, RESIZE_PAD, MIN_W, MIN_H = 28, 8, 1, 14, 160, 120
    def __init__(self, rect: Rect, title: str, font, font_small):
        self.rect=Rect(rect); self.title=title; self.font=font; self.font_small=font_small
        self.drag_title=False; self.drag_off=(0,0); self.resizing=False; self.selected=False
        self.close_rect=Rect(0,0,self.TITLE_H-8,self.TITLE_H-8); self.hover_close=False
    def client_rect(self):
        r=self.rect.copy(); r.y+=self.TITLE_H; r.h-=self.TITLE_H; return r
    # hooks
    def on_close_request(self): pass
    def on_moved(self,dx,dy): pass
    def on_resized(self,old_c,new_c): pass
    def on_client_mouse_down(self,pos,btn): return False
    def on_client_mouse_up(self,pos,btn): pass
    def on_client_mouse_move(self,pos,buttons): pass
    def on_client_key(self,e): pass
    def draw_client(self,screen,client): pass
    # internals
    def _update_close(self):
        self.close_rect.size=(self.TITLE_H-8,self.TITLE_H-8)
        self.close_rect.x=self.rect.right-self.close_rect.w-6
        self.close_rect.y=self.rect.y+(self.TITLE_H-self.close_rect.h)//2
    def _over_title(self,pos): return Rect(self.rect.x,self.rect.y,self.rect.w,self.TITLE_H).collidepoint(pos)
    def _over_resize(self,pos):
        return Rect(self.rect.right-self.RESIZE_PAD,self.rect.bottom-self.RESIZE_PAD,
                    self.RESIZE_PAD,self.RESIZE_PAD).collidepoint(pos)
    # events
    def handle_mouse_down(self,pos,btn):
        if not self.rect.collidepoint(pos): return False
        self._update_close()
        if btn==1 and self.close_rect.collidepoint(pos): self.on_close_request(); return True
        if btn==1 and self._over_resize(pos):
            self.resizing=True; self._rs=(pos[0],pos[1],self.rect.w,self.rect.h); self.selected=True; return True
        if btn==1 and self._over_title(pos):
            self.drag_title=True; self.drag_off=(pos[0]-self.rect.x,pos[1]-self.rect.y); self.selected=True; return True
        if self.client_rect().collidepoint(pos):
            self.selected=True; return self.on_client_mouse_down(pos,btn)
        self.selected=True; return True
    def handle_mouse_up(self,pos,btn):
        self.drag_title=False; self.resizing=False; self.on_client_mouse_up(pos,btn)
    def handle_mouse_move(self,pos,buttons):
        self._update_close(); self.hover_close=self.close_rect.collidepoint(pos)
        if self.drag_title and buttons[0]:
            old=self.rect.topleft; nx=clamp(pos[0]-self.drag_off[0],0,WIDTH-self.rect.w)
            ny=clamp(pos[1]-self.drag_off[1],0,HEIGHT-self.rect.h); self.rect.topleft=(nx,ny)
            dx,dy=self.rect.x-old[0],self.rect.y-old[1]; (dx or dy) and self.on_moved(dx,dy)
        if self.resizing and buttons[0]:
            old_c=self.client_rect().copy()
            sx,sy,sw,sh=self._rs; nw=clamp(sw+(pos[0]-sx),self.MIN_W,WIDTH-self.rect.x)
            nh=clamp(sh+(pos[1]-sy),self.MIN_H,HEIGHT-self.rect.y); self.rect.size=(nw,nh)
            self.on_resized(old_c,self.client_rect().copy())
        self.on_client_mouse_move(pos,buttons)
    def handle_key(self,e): self.on_client_key(e)
    def draw(self,screen):
        pygame.draw.rect(screen,DARK,self.rect,border_radius=self.RADIUS)
        pygame.draw.rect(screen,GRAY if self.selected else (70,70,70),self.rect,self.BORDER,border_radius=self.RADIUS)
        tr=Rect(self.rect.x,self.rect.y,self.rect.w,self.TITLE_H)
        pygame.draw.rect(screen,(40,40,40),tr,border_radius=self.RADIUS)
        pygame.draw.line(screen,(70,70,70),(self.rect.x,self.rect.y+self.TITLE_H),(self.rect.right,self.rect.y+self.TITLE_H))
        ts=self.font.render(self.title,True,TEXT); screen.blit(ts,(self.rect.x+10,self.rect.y+(self.TITLE_H-ts.get_height())//2))
        self._update_close(); pygame.draw.rect(screen,RED_H if self.hover_close else RED,self.close_rect,border_radius=6)
        x=self.font_small.render("X",True,WHITE)
        screen.blit(x,(self.close_rect.centerx-x.get_width()//2,self.close_rect.centery-x.get_height()//2))
        rh=Rect(self.rect.right-14,self.rect.bottom-14,14,14); pygame.draw.rect(screen,(70,70,70),rh); pygame.draw.rect(screen,(110,110,110),rh,1)
        self.draw_client(screen,self.client_rect())

# ---------- Apps ----------
class BoxWindow(BaseWindow):
    def __init__(self,rect,font,small,on_close):
        super().__init__(rect,"box ting",font,small); self.on_close=on_close
        c=self.client_rect(); self.box_off=Rect(20,20,140,120); self.box_abs=Rect(c.x+20,c.y+20,140,120)
        self.drag=False; self.resz=False; self.drag_off=(0,0); self.pressed=False; self.pad=16
    def on_close_request(self): self.on_close(self)
    def on_moved(self,dx,dy): self.box_abs.move_ip(dx,dy)
    def on_resized(self,oc,nc):
        self.box_off.x=clamp(self.box_off.x,0,max(0,nc.w-self.box_off.w))
        self.box_off.y=clamp(self.box_off.y,0,max(0,nc.h-self.box_off.h))
        self.box_abs=Rect(nc.x+self.box_off.x,nc.y+self.box_off.y,self.box_off.w,self.box_off.h)
    def _over_handle(self,p): return Rect(self.box_abs.right-self.pad,self.box_abs.bottom-self.pad,self.pad,self.pad).collidepoint(p)
    def on_client_mouse_down(self,pos,btn):
        if btn!=1: return False
        if self._over_handle(pos): self.resz=True; return True
        if self.box_abs.collidepoint(pos):
            self.drag=True; self.drag_off=(pos[0]-self.box_abs.x,pos[1]-self.box_abs.y); self.pressed=not self.pressed; return True
        return False
    def on_client_mouse_up(self,pos,btn):
        self.drag=False; self.resz=False
        c=self.client_rect(); self.box_off.x=self.box_abs.x-c.x; self.box_off.y=self.box_abs.y-c.y
    def on_client_mouse_move(self,pos,buttons):
        c=self.client_rect()
        if self.drag and buttons[0]:
            nx=clamp(pos[0]-self.drag_off[0],c.x,c.right-self.box_abs.w)
            ny=clamp(pos[1]-self.drag_off[1],c.y,c.bottom-self.box_abs.h); self.box_abs.topleft=(nx,ny)
        if self.resz and buttons[0]:
            nw=clamp(pos[0]-self.box_abs.x,60,c.right-self.box_abs.x)
            nh=clamp(pos[1]-self.box_abs.y,50,c.bottom-self.box_abs.y); self.box_abs.size=(nw,nh); self.box_off.w,self.box_off.h=nw,nh
    def draw_client(self,screen,client):
        pygame.draw.rect(screen,(28,28,28),client,border_radius=6); pygame.draw.rect(screen,(65,65,65),client,1,border_radius=6)
        col=(120,180,255) if self.pressed else (90,140,255)
        pygame.draw.rect(screen,col,self.box_abs,border_radius=10); pygame.draw.rect(screen,WHITE,self.box_abs,2,border_radius=10)
        rh=Rect(self.box_abs.right-self.pad,self.box_abs.bottom-self.pad,self.pad,self.pad)
        pygame.draw.rect(screen,(240,240,240),rh); pygame.draw.rect(screen,(110,110,110),rh,1)

class KnobWindow(BaseWindow):
    def __init__(self,rect,font,small,on_close):
        super().__init__(rect,"knob ting",font,small); self.on_close=on_close
        c=self.client_rect(); self.center_off=[c.w//2,c.h//2+10]; self.center_abs=[c.x+self.center_off[0],c.y+self.center_off[1]]
        self.radius=60; self.drag=False; self.angle=0.0; self.value=0.0
    def on_close_request(self): self.on_close(self)
    def on_moved(self,dx,dy): self.center_abs[0]+=dx; self.center_abs[1]+=dy
    def on_resized(self,oc,nc):
        self.center_off[0]=clamp(self.center_off[0],40,max(40,nc.w-40))
        self.center_off[1]=clamp(self.center_off[1],40,max(40,nc.h-40))
        self.center_abs=[nc.x+self.center_off[0],nc.y+self.center_off[1]]
        self.radius=clamp(min(nc.w,nc.h)//3,30,120)
    def _ang2val(self,ang):
        deg=math.degrees(ang); 
        while deg<=-180: deg+=360
        while deg>180: deg-=360
        deg=clamp(deg,-150,150); return (deg+150)/300.0
    def on_client_mouse_down(self,pos,btn):
        if btn!=1: return False
        dx,dy=pos[0]-self.center_abs[0],pos[1]-self.center_abs[1]
        if dx*dx+dy*dy<=(self.radius+10)**2: self.drag=True; self._upd(pos); return True
        return False
    def on_client_mouse_up(self,pos,btn):
        self.drag=False; c=self.client_rect(); self.center_off=[self.center_abs[0]-c.x,self.center_abs[1]-c.y]
    def on_client_mouse_move(self,pos,buttons):
        if self.drag and buttons[0]: self._upd(pos)
    def _upd(self,pos):
        dx,dy=pos[0]-self.center_abs[0],pos[1]-self.center_abs[1]
        ang=math.atan2(dy,dx); self.value=self._ang2val(ang); self.angle=math.radians(self.value*300-150)
    def draw_client(self,screen,client):
        pygame.draw.rect(screen,(28,28,28),client,border_radius=6); pygame.draw.rect(screen,(65,65,65),client,1,border_radius=6)
        pygame.draw.circle(screen,(60,60,60),self.center_abs,self.radius+8,8)
        pygame.draw.circle(screen,(110,110,110),self.center_abs,self.radius); pygame.draw.circle(screen,(160,160,160),self.center_abs,self.radius,3)
        end=(int(self.center_abs[0]+math.cos(self.angle)*(self.radius-10)),
             int(self.center_abs[1]+math.sin(self.angle)*(self.radius-10)))
        pygame.draw.line(screen,ACCENT,self.center_abs,end,6)

class BallWindow(BaseWindow):
    def __init__(self,rect,font,small,on_close):
        super().__init__(rect,"ball ting",font,small); self.on_close=on_close
        c=self.client_rect(); self.ball=[c.centerx,c.centery]; self.r=18; self.vel=[0.0,0.0]
        self.g=900.0; self.rest=0.65; self.drag=False; self.drag_off=(0,0); self.last=self.ball[:]; self.last_t=time.time()
    def on_close_request(self): self.on_close(self)
    def on_moved(self,dx,dy): self.ball[0]+=dx; self.ball[1]+=dy
    def on_resized(self,oc,nc):
        self.ball[0]=clamp(self.ball[0],nc.x+self.r,nc.right-self.r)
        self.ball[1]=clamp(self.ball[1],nc.y+self.r,nc.bottom-self.r)
    def _in(self,p): dx,dy=p[0]-self.ball[0],p[1]-self.ball[1]; return dx*dx+dy*dy<=self.r*self.r
    def on_client_mouse_down(self,pos,btn):
        if btn!=1: return False
        if self._in(pos): self.drag=True; self.drag_off=(pos[0]-self.ball[0],pos[1]-self.ball[1]); self.vel=[0,0]; return True
        return False
    def on_client_mouse_up(self,pos,btn):
        if self.drag:
            dt=max(1e-3,time.time()-self.last_t); self.vel=[(self.ball[0]-self.last[0])/dt,(self.ball[1]-self.last[1])/dt]
        self.drag=False
    def on_client_mouse_move(self,pos,buttons):
        c=self.client_rect(); self.last=self.ball[:]; self.last_t=time.time()
        if self.drag and buttons[0]:
            nx=clamp(pos[0]-self.drag_off[0],c.x+self.r,c.right-self.r)
            ny=clamp(pos[1]-self.drag_off[1],c.y+self.r,c.bottom-self.r); self.ball=[nx,ny]
    def step(self,dt):
        if self.drag: return
        c=self.client_rect(); self.vel[1]+=self.g*dt; self.ball[0]+=self.vel[0]*dt; self.ball[1]+=self.vel[1]*dt
        L,T,R,B=c.x+self.r,c.y+self.r,c.right-self.r,c.bottom-self.r
        if self.ball[0]<L: self.ball[0]=L; self.vel[0]*=-self.rest
        elif self.ball[0]>R: self.ball[0]=R; self.vel[0]*=-self.rest
        if self.ball[1]<T: self.ball[1]=T; self.vel[1]*=-self.rest
        elif self.ball[1]>B: self.ball[1]=B; self.vel[1]*=-self.rest
        self.vel[0]*=0.995; self.vel[1]*=0.995
    def draw_client(self,screen,client):
        pygame.draw.rect(screen,(26,26,26),client,border_radius=6); pygame.draw.rect(screen,(65,65,65),client,1,border_radius=6)
        pygame.draw.circle(screen,(230,230,230),(int(self.ball[0]),int(self.ball[1])),self.r)
        pygame.draw.circle(screen,(120,120,120),(int(self.ball[0]),int(self.ball[1])),self.r,2)

# ---------- Main window ----------
class MainWindow(BaseWindow):
    def __init__(self, rect, font, small, open_box, open_knob, open_ball, close_main):
        super().__init__(rect,"adhd n dat",font,small)
        pad,bw,bh=12,180,44
        self.btn_box=Button(Rect(pad,pad,bw,bh),"box ting",font)
        self.btn_knob=Button(Rect(pad,pad+bh+pad,bw,bh),"knob ting",font)
        self.btn_ball=Button(Rect(pad,pad+2*(bh+pad),bw,bh),"ball ting",font)
        self.open_box=open_box; self.open_knob=open_knob; self.open_ball=open_ball; self.close_main=close_main
    def on_close_request(self): self.close_main()  
    def on_moved(self,dx,dy):
        self.btn_box.on_moved(dx,dy); self.btn_knob.on_moved(dx,dy); self.btn_ball.on_moved(dx,dy)
    def on_resized(self,oc,nc):
        for b in (self.btn_box,self.btn_knob,self.btn_ball): b.place(nc)
    def on_client_mouse_down(self,pos,btn):
        if btn!=1: return False
        if self.btn_box.handle(pos,True): self.open_box(); return True
        if self.btn_knob.handle(pos,True): self.open_knob(); return True
        if self.btn_ball.handle(pos,True): self.open_ball(); return True
        return False
    def on_client_mouse_move(self,pos,buttons):
        self.btn_box.handle(pos,False); self.btn_knob.handle(pos,False); self.btn_ball.handle(pos,False)
    def draw_client(self,screen,client):
        pygame.draw.rect(screen,(28,28,28),client,border_radius=6); pygame.draw.rect(screen,(65,65,65),client,1,border_radius=6)
        self.btn_box.place(client); self.btn_knob.place(client); self.btn_ball.place(client)
        self.btn_box.draw(screen); self.btn_knob.draw(screen); self.btn_ball.draw(screen)

# ---------- Manager (icon + overlay windows) ----------
class FidgetTing:
    def __init__(self):
        self.icon=self._load_icon("fidget-icon.png"); self.icon_rect=self.icon.get_rect(topleft=(96,16))
        self.hover_icon=False; self.drag_icon=False; self.drag_off=(0,0); self.drag_start=None
        self.font=pygame.font.SysFont(None,22); self.small=pygame.font.SysFont(None,18)
        self.windows=[]; self.main=None; self.visible=False
    def _load_icon(self,path):
        try: return pygame.image.load(path).convert_alpha()
        except: 
            surf=pygame.Surface((64,64),pygame.SRCALPHA)
            pygame.draw.rect(surf,GRAY,surf.get_rect(),2,border_radius=12)
            pygame.draw.circle(surf,GRAY,(32,24),10,2); pygame.draw.circle(surf,GRAY,(20,42),6,2); pygame.draw.circle(surf,GRAY,(44,42),6,2)
            return surf
    # window management
    def _front(self,w): self.windows.remove(w); self.windows.append(w)
    def _remove(self,w):
        if w in self.windows: self.windows.remove(w)
        if w is self.main: self.main=None; self.visible=False
    def _ensure_main(self):
        if not self.main:
            self.main=MainWindow(Rect(260,120,260,220),self.font,self.small,
                                 self.open_box,self.open_knob,self.open_ball,self.close_main)
            self.windows.append(self.main)
    def close_main(self):
        # red X from main window
        if self.main in self.windows: self.windows.remove(self.main)
        self.main=None; self.visible=False
    # open apps
    def open_box(self):
        w=BoxWindow(Rect(540,120,320,260),self.font,self.small,self._remove); self.windows.append(w); self._front(w)
    def open_knob(self):
        w=KnobWindow(Rect(480,180,320,300),self.font,self.small,self._remove); self.windows.append(w); self._front(w)
    def open_ball(self):
        w=BallWindow(Rect(420,80,360,300),self.font,self.small,self._remove); self.windows.append(w); self._front(w)
    # events
    def on_mouse_down(self,pos,button=1):
        if self.icon_rect.collidepoint(pos):
            self.drag_icon=True; ix,iy=self.icon_rect.topleft; self.drag_off=(pos[0]-ix,pos[1]-iy); self.drag_start=pos; return
        if not self.visible: return
        for w in reversed(self.windows):
            if w.rect.collidepoint(pos):
                self._front(w)
                for z in self.windows: z.selected=(z is w)
                if w.handle_mouse_down(pos,button): return
    def on_mouse_up(self,pos,button=1):
        if self.drag_icon:
            self.drag_icon=False; sx,sy=self.drag_start
            if sqrlen(pos[0]-sx,pos[1]-sy)<=CLICK_THRESHOLD*CLICK_THRESHOLD and self.icon_rect.collidepoint(pos):
                self.visible=not self.visible
                if self.visible: self._ensure_main()
                else: self.windows.clear(); self.main=None
            return
        if not self.visible: return
        for w in reversed(self.windows): w.handle_mouse_up(pos,button)
    def on_mouse_move(self,pos):
        self.hover_icon=self.icon_rect.collidepoint(pos)
        if self.drag_icon and pygame.mouse.get_pressed(num_buttons=3)[0]:
            nx=clamp(pos[0]-self.drag_off[0],0,WIDTH-self.icon_rect.width)
            ny=clamp(pos[1]-self.drag_off[1],0,HEIGHT-self.icon_rect.height); self.icon_rect.topleft=(nx,ny)
        if not self.visible: return
        buttons=pygame.mouse.get_pressed(num_buttons=3)
        for w in self.windows: w.handle_mouse_move(pos,buttons)
    def on_key(self,event):
        if not self.visible: return
        sel=next((w for w in self.windows if w.selected),None)
        sel and sel.handle_key(event)
    def update(self,dt):
        if not self.visible: return
        for w in self.windows:
            if isinstance(w,BallWindow): w.step(dt)
    # drawing
    def draw_icon(self,screen):
        screen.blit(self.icon,self.icon_rect.topleft)
        if self.hover_icon and not self.drag_icon:
            t=self.small.render("adhd n dat",True,TEXT); screen.blit(t,(self.icon_rect.left,self.icon_rect.bottom+2))
    def draw_overlay(self,screen):
        if not self.visible: return
        for w in self.windows: w.draw(screen)
