-- Atalhos no padrão do HyDE (https://github.com/HyDE-Project/HyDE), adaptados
-- para Noctalia (no lugar de rofi/waybar/swaync), kwall e ktheme.

local mainMod = "SUPER"
local noctCall = "noctalia msg "
local launchPrefix = "uwsm app -- " -- if you are not using UWSM, make this empty (e.g. "")

-- AZERTY fix: the number-row keys emit symbols (& é " ' ...) without Shift, so
-- binding to the digit characters fails. Bind by physical keycode instead.
-- Digit d -> evdev keycode: 1..9 => 10..18, 0 => 19
local function digitCode(d)
    return "code:" .. (d == 0 and 19 or (9 + d))
end

---------------------------
---- WINDOW MANAGEMENT ----
---------------------------

hl.bind(mainMod .. " + Q",                 hl.dsp.window.close())
hl.bind("ALT + F4",                        hl.dsp.window.close())
hl.bind(mainMod .. " + Delete",            hl.dsp.exit())
hl.bind(mainMod .. " + W",                 hl.dsp.window.float({ action = "toggle" }))
hl.bind(mainMod .. " + G",                 hl.dsp.group.toggle())
hl.bind("SHIFT + F11",                     hl.dsp.window.fullscreen())
hl.bind(mainMod .. " + L",                 hl.dsp.exec_cmd(noctCall .. "session lock"))
hl.bind(mainMod .. " + SHIFT + F",         hl.dsp.window.pin())
hl.bind("CONTROL + ALT + Delete",          hl.dsp.exec_cmd(noctCall .. "panel-toggle session"))
hl.bind(mainMod .. " + J",                 hl.dsp.layout("togglesplit"))

-- Extras (não conflitam com o HyDE)
hl.bind(mainMod .. " + Escape",      hl.dsp.exec_cmd("hyprctl kill"))
hl.bind(mainMod .. " + ALT + Space", hl.dsp.window.float({ action = "toggle" }))
hl.bind(mainMod .. " + F",           hl.dsp.window.fullscreen())
hl.bind(mainMod .. " + D",           hl.dsp.window.fullscreen({ mode = 1 }))

-- Group navigation
hl.bind(mainMod .. " + CONTROL + H", hl.dsp.group.prev())
hl.bind(mainMod .. " + CONTROL + L", hl.dsp.group.next())

-- Change focus
hl.bind(mainMod .. " + Left",  hl.dsp.focus({ direction = "left" }))
hl.bind(mainMod .. " + Right", hl.dsp.focus({ direction = "right" }))
hl.bind(mainMod .. " + Up",    hl.dsp.focus({ direction = "up" }))
hl.bind(mainMod .. " + Down",  hl.dsp.focus({ direction = "down" }))
hl.bind("ALT + Tab",           hl.dsp.window.cycle_next())

-- Resize windows
hl.bind(mainMod .. " + SHIFT + Right", hl.dsp.window.resize({ x = 30,  y = 0,   relative = true }), { repeating = true })
hl.bind(mainMod .. " + SHIFT + Left",  hl.dsp.window.resize({ x = -30, y = 0,   relative = true }), { repeating = true })
hl.bind(mainMod .. " + SHIFT + Up",    hl.dsp.window.resize({ x = 0,   y = -30, relative = true }), { repeating = true })
hl.bind(mainMod .. " + SHIFT + Down",  hl.dsp.window.resize({ x = 0,   y = 30,  relative = true }), { repeating = true })

-- Move windows
hl.bind(mainMod .. " + SHIFT + CONTROL + Left",  hl.dsp.window.move({ direction = "l" }))
hl.bind(mainMod .. " + SHIFT + CONTROL + Right", hl.dsp.window.move({ direction = "r" }))
hl.bind(mainMod .. " + SHIFT + CONTROL + Up",    hl.dsp.window.move({ direction = "u" }))
hl.bind(mainMod .. " + SHIFT + CONTROL + Down",  hl.dsp.window.move({ direction = "d" }))

-- Move window to another monitor with the mouse wheel
hl.bind(mainMod .. " + SHIFT + mouse_up",   hl.dsp.window.move({ monitor = "-1" }))
hl.bind(mainMod .. " + SHIFT + mouse_down", hl.dsp.window.move({ monitor = "+1" }))

-- Move & Resize with mouse
hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag())
hl.bind(mainMod .. " + mouse:273", hl.dsp.window.resize())

-- Zoom
local function zoomfunction(value)
    local zoomvalue = hl.get_config("cursor:zoom_factor")
    if (zoomvalue + value) > 3.0 then
        hl.config({ cursor = { zoom_factor = 3.0 } })
    elseif (zoomvalue + value) < 1.0 then
        hl.config({ cursor = { zoom_factor = 1.0 } })
    else
        hl.config({ cursor = { zoom_factor = zoomvalue + value } })
    end
end
hl.bind(mainMod .. " + Minus", function() zoomfunction(-0.3) end, { repeating = true})
hl.bind(mainMod .. " + Plus", function() zoomfunction(0.3) end, { repeating = true })

--# Zoom with keypad
hl.bind(mainMod .. " + code:82", function() zoomfunction(-0.3) end, { repeating = true })
hl.bind(mainMod .. " + code:86", function() zoomfunction(0.3) end, { repeating = true })


------------------
---- LAUNCHER ----
------------------

hl.bind(mainMod .. " + T",          hl.dsp.exec_cmd(launchPrefix .. TERMINAL))
hl.bind(mainMod .. " + Return",     hl.dsp.exec_cmd(launchPrefix .. TERMINAL))
hl.bind(mainMod .. " + E",          hl.dsp.exec_cmd(launchPrefix .. FILE_MANAGER))
hl.bind(mainMod .. " + C",          hl.dsp.exec_cmd(launchPrefix .. EDITOR))
hl.bind(mainMod .. " + B",          hl.dsp.exec_cmd(launchPrefix .. BROWSER))
hl.bind("XF86Calculator",           hl.dsp.exec_cmd(launchPrefix .. CALCULATOR))
hl.bind("CONTROL + SHIFT + Escape", hl.dsp.exec_cmd(launchPrefix .. TERMINAL .. " -e btop"))

-- Rofi menus do HyDE -> painéis do Noctalia
hl.bind(mainMod .. " + A",          hl.dsp.exec_cmd(noctCall .. "panel-toggle launcher"))
hl.bind(mainMod .. " + Space",      hl.dsp.exec_cmd(noctCall .. "panel-toggle launcher"))
hl.bind(mainMod .. " + Tab",        hl.dsp.exec_cmd(noctCall .. "window-switcher"))
hl.bind(mainMod .. " + comma",      hl.dsp.exec_cmd(noctCall .. "panel-toggle launcher /emo"))
hl.bind(mainMod .. " + period",     hl.dsp.exec_cmd(noctCall .. "panel-toggle launcher /emo"))
hl.bind(mainMod .. " + V",          hl.dsp.exec_cmd(noctCall .. "panel-toggle clipboard"))
hl.bind(mainMod .. " + SHIFT + V",  hl.dsp.exec_cmd(noctCall .. "panel-toggle clipboard"))

-- Noctalia (sem equivalente no HyDE)
hl.bind(mainMod .. " + N",          hl.dsp.exec_cmd(noctCall .. "panel-toggle control-center notifications"))
hl.bind(mainMod .. " + X",          hl.dsp.exec_cmd(noctCall .. "panel-toggle control-center"))
hl.bind(mainMod .. " + Z",          hl.dsp.exec_cmd(noctCall .. "settings-toggle"))

---------------------------
---- HARDWARE CONTROLS ----
---------------------------

-- Audio
hl.bind("F10",                  hl.dsp.exec_cmd(noctCall .. "volume-mute"), { locked = true })
hl.bind("F11",                  hl.dsp.exec_cmd(noctCall .. "volume-down"), { locked = true, repeating = true })
hl.bind("F12",                  hl.dsp.exec_cmd(noctCall .. "volume-up"),   { locked = true, repeating = true })
hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd(noctCall .. "volume-up"),   { locked = true, repeating = true })
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd(noctCall .. "volume-down"), { locked = true, repeating = true })
hl.bind("XF86AudioMute",        hl.dsp.exec_cmd(noctCall .. "volume-mute"), { locked = true })
hl.bind("XF86AudioMicMute",     hl.dsp.exec_cmd(noctCall .. "mic-mute"),    { locked = true })

-- Media
hl.bind("XF86AudioPlay",  hl.dsp.exec_cmd(noctCall .. "media toggle"),   { locked = true })
hl.bind("XF86AudioPause", hl.dsp.exec_cmd(noctCall .. "media toggle"),   { locked = true })
hl.bind("XF86AudioNext",  hl.dsp.exec_cmd(noctCall .. "media next"),     { locked = true })
hl.bind("XF86AudioPrev",  hl.dsp.exec_cmd(noctCall .. "media previous"), { locked = true })

-- Brightness
hl.bind("XF86MonBrightnessUp",   hl.dsp.exec_cmd(noctCall .. "brightness-up"),   { locked = true, repeating = true })
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd(noctCall .. "brightness-down"), { locked = true, repeating = true })

-------------------
---- UTILITIES ----
-------------------

-- Keyboard layout
hl.bind(mainMod .. " + K", hl.dsp.exec_cmd("hyprctl switchxkblayout all next"))

-- Screen Capture
hl.bind(mainMod .. " + P",             hl.dsp.exec_cmd(noctCall .. "screenshot-region"))
hl.bind(mainMod .. " + CONTROL + P",   hl.dsp.exec_cmd(noctCall .. "screenshot-region"))
hl.bind(mainMod .. " + ALT + P",       hl.dsp.exec_cmd(noctCall .. "screenshot-fullscreen"))
hl.bind("Print",                       hl.dsp.exec_cmd(noctCall .. "screenshot-fullscreen"))
hl.bind(mainMod .. " + SHIFT + P",     hl.dsp.exec_cmd("hyprpicker -a -n"))

-- Wallpapers (kwall) e temas (ktheme)
local kwall = os.getenv("HOME") .. "/dotfiles/scripts/kwall "
local ktheme = os.getenv("HOME") .. "/dotfiles/scripts/ktheme "

hl.bind(mainMod .. " + SHIFT + W",           hl.dsp.exec_cmd(kwall .. "pick"))            -- seletor de wallpaper
hl.bind(mainMod .. " + ALT + Right",         hl.dsp.exec_cmd(kwall .. "next"))            -- próximo wallpaper
hl.bind(mainMod .. " + ALT + Left",          hl.dsp.exec_cmd(kwall .. "random"))          -- (kwall não tem "anterior")
hl.bind(mainMod .. " + CONTROL + W",         hl.dsp.exec_cmd(kwall .. "random"))
hl.bind(mainMod .. " + SHIFT + ALT + W",     hl.dsp.exec_cmd(kwall .. "random animated"))
hl.bind(mainMod .. " + SHIFT + CONTROL + W", hl.dsp.exec_cmd(kwall .. "stop"))            -- parar animação
hl.bind(mainMod .. " + ALT + W",             hl.dsp.exec_cmd(noctCall .. "panel-toggle wallpaper"))
hl.bind(mainMod .. " + SHIFT + T",           hl.dsp.exec_cmd(ktheme .. "pick"))           -- seletor de temas
hl.bind(mainMod .. " + ALT + T",             hl.dsp.exec_cmd(ktheme .. "next"))           -- próximo tema

-------------------------------
---- WORKSPACES & MONITORS ----
-------------------------------

for i = 1, 10 do
    local key = digitCode(i % 10)
    hl.bind(mainMod .. " + " .. key,           hl.dsp.focus({ workspace = i }))
    hl.bind(mainMod .. " + SHIFT + " .. key,   hl.dsp.window.move({ workspace = i }))
    hl.bind(mainMod .. " + ALT + " .. key,     hl.dsp.window.move({ workspace = i, follow = false }))
end

-- Relative workspaces and first empty
hl.bind(mainMod .. " + CONTROL + Right", hl.dsp.focus({ workspace = "r+1" }))
hl.bind(mainMod .. " + CONTROL + Left",  hl.dsp.focus({ workspace = "r-1" }))
hl.bind(mainMod .. " + CONTROL + Down",  hl.dsp.focus({ workspace = "empty" }))

-- Move window to relative workspace
hl.bind(mainMod .. " + CONTROL + ALT + Right", hl.dsp.window.move({ workspace = "r+1" }))
hl.bind(mainMod .. " + CONTROL + ALT + Left",  hl.dsp.window.move({ workspace = "r-1" }))

-- Scroll through existing workspaces
hl.bind(mainMod .. " + mouse_down", hl.dsp.focus({ workspace = "e+1" }))
hl.bind(mainMod .. " + mouse_up",   hl.dsp.focus({ workspace = "e-1" }))

-- Special workspace (scratchpad)
hl.bind(mainMod .. " + SHIFT + S", hl.dsp.window.move({ workspace = "special" }))
hl.bind(mainMod .. " + ALT + S",   hl.dsp.window.move({ workspace = "special", follow = false }))
hl.bind(mainMod .. " + S",         hl.dsp.workspace.toggle_special())
