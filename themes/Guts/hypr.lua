-- Tema Guts ⚔ (Berserk) — carregado por config/hypr/config/colors.lua via themes/current
-- Visual mais duro que a Kuromi: cantos quase retos, borda de lâmina, brilho de sangue.

THEME = {
    -- bordas: lâmina vermelha escorrendo para o aço
    active_border   = { "rgba(c8102eff)", "rgba(5c0a14ff)", "rgba(8e9196ff)" },
    border_angle    = 135,
    inactive_border = "rgba(2a2727cc)",
    group_active    = "rgba(8e9196ff)",
    group_locked    = "rgba(c8102eff)",
    groupbar_active = "rgba(c8102eff)",
    splash          = "rgba(c8102eff)",

    -- forma
    border_size = 2,
    rounding    = 3,
    gaps_in     = 4,
    gaps_out    = 8,

    -- transparência / blur / sombra
    active_opacity   = 0.97,
    inactive_opacity = 0.88,
    blur_size        = 4,
    blur_passes      = 2,
    blur_vibrancy    = 0.1,
    shadow_range     = 24,
    shadow           = "rgba(c8102e66)", -- brilho de sangue na janela ativa
    shadow_inactive  = "rgba(000000aa)",
}
