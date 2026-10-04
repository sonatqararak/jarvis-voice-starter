-- Load explicitly from your existing Hammerspoon init.lua; nothing overwrites it.
local M = {}
local home = os.getenv('HOME')
local base = home .. '/.local/share/headless-kit'
local python = base .. '/.venv/bin/python'
local cfg = hs.json.read(home .. '/.config/headless-kit/kit.json')
local orb, tasks, micBusy = nil, {}, false
local orbView = dofile(base .. '/mac/nebula.lua')
local function show(text)
  orbView.show(text)
end
local function exec(file,data,callback)
  local task
  task=hs.task.new(python,function(code,out,err)
    tasks[task]=nil
    local ok,r=pcall(hs.json.decode,out or '')
    if ok and type(r)=='table' then callback(r)
    else callback({error=true,message='Request failed. Check the kit Python environment and retry.'}) end
  end,{base..'/bin/'..file})
  tasks[task]=true
  if data then task:setInput(hs.json.encode(data)..'\n') end
  task:start()
end
local function reply(r)
  show(r.message or 'Done')
  if r.notify then hs.notify.new({title='Jarvis',informativeText=r.message or ''}):send() end
  if r.raise then hs.application.launchOrFocus(cfg.terminal or 'Terminal') end
end
local function dispatch(text)
  text=text:gsub('^[Hh]ey [Jj]arvis[, ]*','')
  if text:lower() == 'open guide' then
    hs.urlevent.openURL('file://' .. base .. '/docs/index.html')
    show('Opened your local welcome guide'); return
  end
  local app = text:match('^[Oo]pen app (.+)$')
  if app then
    local allowed = {safari='Safari', notes='Notes', terminal='Terminal'}
    if not allowed[app:lower()] then show('Starter allows Safari, Notes or Terminal'); return end
    hs.application.launchOrFocus(allowed[app:lower()]); show('Opened ' .. allowed[app:lower()]); return
  end
  show('Thinking…')
  exec('request.py',{text=text},function(r)
    if r.confirm then
      local b=hs.dialog.blockAlert('Send to '..r.label..'?',r.prompt,'Send','Cancel')
      if b=='Send' then exec('request.py',{text=text,confirmed=true},reply)
      else show('Cancelled — no prompt sent') end
    else reply(r) end
  end)
end
local function dictate()
  if micBusy then return end
  local destination=hs.application.frontmostApplication()
  if not destination or destination:name()=='Hammerspoon' then show('Focus your destination app first');return end
  micBusy=true;show('Listening locally…')
  exec('mic_once.py',nil,function(r)
    micBusy=false
    if r.error then reply(r);return end
    if not r.text or r.text=='' then show('No speech heard');return end
    local b,reviewed=hs.dialog.textPrompt('Paste into '..destination:name()..'?','Review dictation. Enter is not pressed.',r.text,'Paste','Cancel')
    if b~='Paste' then show('Cancelled');return end
    hs.pasteboard.setContents(reviewed);destination:activate()
    hs.timer.doAfter(.25,function() hs.eventtap.keyStroke({'cmd'},'v');show('Pasted — review before submitting') end)
  end)
end
local function command()
  local button,text=hs.dialog.textPrompt('Jarvis','go to LABEL · focus LABEL · unfocus · status · park LABEL · restore LABEL','','Run','Cancel')
  if button=='Run' and text~='' then dispatch(text) end
end
local function paste()
  local b,label=hs.dialog.textPrompt('Paste box','Exact pane label','','Next','Cancel')
  if b~='Next' or label=='' then return end
  local c,text=hs.dialog.textPrompt('Paste box','Review text. This pastes without pressing Enter.',hs.pasteboard.getContents() or '','Paste','Cancel')
  if c=='Paste' and text~='' then exec('request.py',{action='paste',label=label,text=text},reply) end
end
local function listen()
  if micBusy then return end
  micBusy=true;show('Listening locally…')
  exec('mic_once.py',nil,function(r)
    micBusy=false
    if r.error then reply(r);return end
    if r.text and r.text~='' then dispatch(r.text) else show('No speech heard') end
  end)
end
M.keys={hs.hotkey.bind({'ctrl','alt'},'J',command),hs.hotkey.bind({'ctrl','alt'},'P',paste),
  hs.hotkey.bind({'ctrl','alt'},'space',listen),hs.hotkey.bind({'ctrl','alt'},'D',dictate),hs.hotkey.bind({'ctrl','alt'},'escape',function() orbView.hide() end)}
function M.stop()
  for _,k in ipairs(M.keys) do k:delete() end
  for t,_ in pairs(tasks) do t:terminate() end
  orbView.stop()
end
return M
