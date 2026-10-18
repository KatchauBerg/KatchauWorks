-- Cores e aparência do tema ativo: ~/dotfiles/themes/current/hypr.lua
-- (themes/current é um link trocado pelo `ktheme`; cada tema define a tabela THEME)

THEME = {
    active_border = { "rgba(ffffffff)" }, border_angle = 45, inactive_border = "rgba(444444cc)",
    group_active = "rgba(ffffffff)", group_locked = "rgba(aaaaaaff)", groupbar_active = "rgba(ffffffff)",
    splash = "rgba(ffffffff)", border_size = 2, rounding = 10, gaps_in = 5, gaps_out = 10,
    active_opacity = 0.95, inactive_opacity = 0.85, blur_size = 5, blur_passes = 3, blur_vibrancy = 0.2,
    shadow_range = 12, shadow = "rgba(00000088)", shadow_inactive = "rgba(00000066)",
}

local ok, err = pcall(dofile, os.getenv("HOME") .. "/dotfiles/themes/current/hypr.lua")
if not ok then
    hl.exec_cmd("notify-send 'ktheme' 'Falha ao carregar o tema do Hyprland: " .. tostring(err):gsub("'", "") .. "'")
end
