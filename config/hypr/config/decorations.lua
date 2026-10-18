-- Look and feel configuration (valores vêm do tema ativo, ver colors.lua)

hl.config({
    general = {
        gaps_in = THEME.gaps_in,
        gaps_out = THEME.gaps_out,
        border_size = THEME.border_size,
        extend_border_grab_area = 10,
        resize_on_border = true,
        col = {
            active_border = {
                colors = THEME.active_border,
                angle = THEME.border_angle,
            },
            inactive_border = THEME.inactive_border,
        },
    },
    group = {
        col = {
            border_active = THEME.group_active,
            border_inactive = THEME.inactive_border,
            border_locked_active = THEME.group_locked,
            border_locked_inactive = THEME.inactive_border,
        },
        groupbar = {
            col = {
                active = THEME.groupbar_active,
                inactive = THEME.inactive_border,
                locked_active = THEME.group_locked,
                locked_inactive = THEME.inactive_border,
            },
        },
    },
    decoration = {
        dim_special = 0.3,
        rounding = THEME.rounding,
        active_opacity = THEME.active_opacity,
        inactive_opacity = THEME.inactive_opacity,
        fullscreen_opacity = 1,
        blur = {
            size = THEME.blur_size,
            passes = THEME.blur_passes,
            vibrancy = THEME.blur_vibrancy,
            special = true,
        },
        shadow = {
            enabled = true,
            range = THEME.shadow_range,
            render_power = 3,
            color = THEME.shadow,
            color_inactive = THEME.shadow_inactive,
        },
    },
})
