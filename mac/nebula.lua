-- Small animated galaxy shell. No microphone, accounts or network access.
local M = {}
local canvas,timer,text,state,phase=nil,nil,'Ready','idle',0
local stars={}
local seed=8848
local function random() seed=(seed*1664525+1013904223)%4294967296;return seed/4294967296 end
for j=1,132 do stars[j]={r=5+math.sqrt(random())*30,a=random()*math.pi*2,s=.36+random()*.67,alpha=.4+random()*.55} end
local function draw()
 if not canvas then return end
 phase=phase+.004
 local elements={}
 local function circle(x,y,r,red,green,blue,alpha,stroke)
  elements[#elements+1]={type='circle',action=stroke and 'stroke' or 'fill',center={x=80+x*1.4,y=78+y*1.4},radius=r*1.4,fillColor={red=red,green=green,blue=blue,alpha=alpha},strokeColor={red=red,green=green,blue=blue,alpha=alpha},strokeWidth=.8}
 end
 circle(0,0,49.5,.043,.075,.125,1)
 for j=0,35 do
  local lane=j%3;local q=math.floor(j/3);local x=(q-5.5)*4.55;local y=math.sin(q*.48+phase+lane*.65)*6+(lane-1)*6;local a=-.5
  circle(x*math.cos(a)-y*math.sin(a),x*math.sin(a)+y*math.cos(a),5.3+math.sin(q/11*math.pi)*2.5,.65,.57,.80,.075)
 end
 for _,s in ipairs(stars) do circle(math.cos(s.a+phase*.6)*s.r,math.sin(s.a+phase*.6)*s.r*.92,s.s,.82,.855,.97,s.alpha) end
 for j=5,1,-1 do circle(0,0,1.9+j*1.45,.94,.86,.85,.025+(6-j)*.014) end
 circle(0,0,2,.96,.97,1,.96)
 for k=0,2 do circle(0,0,41.1+k*2.45,.686,.788,.906,k==1 and .65 or .25,true) end
 if state=='thinking' then for j=0,2 do local a=phase*40-j*.14;circle(math.cos(a)*44.3,math.sin(a)*44.3,1.15-j*.22,.78,.73,.92,.9-j*.23) end end
 if state=='listening' then circle(0,0,47+math.sin(phase*30),.78,.73,.92,.6,true) end
 elements[#elements+1]={type='rectangle',action='fill',frame={x=163,y=22,w=280,h=110},roundedRectRadii={xRadius=12,yRadius=12},fillColor={red=.067,green=.102,blue=.149,alpha=.98}}
 elements[#elements+1]={type='text',text=text,textSize=14,textColor={white=.95},frame={x=177,y=34,w=250,h=85}}
 canvas:replaceElements(table.unpack(elements))
end
function M.show(message)
 text=message or 'Ready';state=text:match('Listening') and 'listening' or text:match('Thinking') and 'thinking' or 'idle'
 if not canvas then local f=hs.screen.mainScreen():frame();canvas=hs.canvas.new({x=f.x+f.w/2-230,y=f.y+f.h-190,w=460,h=155}) end
 draw();canvas:show()
 if not timer then timer=hs.timer.doEvery(.08,draw) end
end
function M.hide() if timer then timer:stop();timer=nil end;if canvas then canvas:delete();canvas=nil end end
M.stop=M.hide
return M
