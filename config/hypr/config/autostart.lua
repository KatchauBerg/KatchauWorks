-- Auto-start config
-- if you dont use UWSM add your auto start programs here, otherwise use XDG autostart https://wiki.archlinux.org/title/XDG_Autostart

hl.on("hyprland.start", function ()
    hl.exec_cmd("dbus-update-activation-environment --systemd --all")
    hl.exec_cmd("noctalia")
    -- reaplica o último wallpaper (inclusive animado) depois que o Noctalia sobe
    hl.exec_cmd("sh -c 'sleep 3; $HOME/dotfiles/scripts/kwall restore'")
    hl.exec_cmd("xhost +SI:localuser:root")
end)
