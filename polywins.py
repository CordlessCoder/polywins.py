#!/usr/bin/env python
import sys
import os

# import timeit

# BSPWINS.py

# SETTINGS

active_text_color = "#EB6572"
active_bg = "#24283B"
active_underline = "#EB6572"

inactive_text_color = "#C0CAF5"
inactive_bg = ""
inactive_underline = "#C0CAF5"

separator = ""
show = "window_classname"  # options: window_title, window_class, window_classname
forbidden_classes = "Polybar Conky Gmrun Pavucontrol".upper().split(" ")
show_unpopulated_desktops = False

char_limit = 10
max_windows = 5
add_spaces = "true"
resize_increment = 16
resize_offset = resize_increment / 2


# WINDOW LIST SETUP


active_left = "%{F" + active_text_color + "}"
active_right = "%{F-}"
inactive_left = "%{F" + inactive_text_color + "}"
inactive_right = "%{F-}"
separator = "%{F" + inactive_text_color + "}" + separator + "%{F-}"

wps_active_left = "%{F" + inactive_text_color + "}%{+u}%{u" + inactive_underline + "}"

wps_active_right = "%{u}%{F-}"
wps_inactive_left = "%{F" + inactive_text_color + "}"
wps_inactive_right = "%{F-}"

if active_underline is not None:
    active_left = active_left + "%{+u}%{u" + active_underline + "}"
    active_right = "%{-u}" + active_right


if inactive_underline is not None:
    inactive_left += "%{+u}%{u" + inactive_underline + "}"
    inactive_right = "%{-u}" + inactive_right


active_left += "%{B" + active_bg + "}"
active_right = "%{B-}" + active_right


on_click = " ".join(sys.argv[:2])
monitor = sys.argv[1]


printf = sys.stdout.write


def regen(windows, focused):
    lookup = os.popen("wmctrl -lx 2> /dev/null").readlines()
    wlist = {}
    # try:
    for line in lookup:
        wlist[line[:2] + line[3:10]] = (
            line.split(" ")[3].split(".")[0].upper(),
            int(line.split(" ")[2]),
        )
    workspaces, active_workspace = get_workspaces()
    if len(windows) == 1 and windows[0] == "":
        for i, workspace in enumerate(get_workspaces(monitor)):
            i != 0 and printf(separator)
            if workspace == workspaces[active_workspace]:
                printf(wps_active_left + " " + workspace)
            else:
                printf(
                    "%{A1:" + on_click + " switch_workspace " + workspace + ":}"
                    "%{A2:"
                    + on_click
                    + " swap_workspace "
                    + workspace
                    + ":}"
                    + wps_active_right
                    + active_right
                    + " "
                    + workspace
                )
            printf(" " + "%{A}%{A}")
        return
    window_workspace_pairs = {}
    for workspace in workspaces:
        window_workspace_pairs[workspace] = []
    for window in windows:
        try:
            window_workspace_pairs[workspaces[wlist[window][1]]].append(window)
        except KeyError:
            pass
    i = 0
    for workspace in get_workspaces(monitor):
        if len(window_workspace_pairs[workspace]) == show_unpopulated_desktops - 1:
            continue
        i != 0 and printf(separator)
        i += 1
        if workspace == workspaces[active_workspace]:
            printf(wps_active_left + " " + workspace)
        else:
            printf(
                "%{A1:" + on_click + " switch_workspace " + workspace + ":}"
                "%{A2:"
                + on_click
                + " swap_workspace "
                + workspace
                + ":}"
                + wps_active_right
                + active_right
                + " "
                + workspace
            )
        if len(window_workspace_pairs[workspace]) >= 1:
            printf(":" + "%{A}%{A}")
        else:
            printf(" " + "%{A}%{A}")
        for wid in window_workspace_pairs[workspace][:max_windows]:
            if wlist[wid][0] in forbidden_classes:
                continue
            window = wlist[wid][0][:char_limit]
            printf(
                "%{A1:"
                + on_click
                + " raise_or_minimize "
                + wid
                + ":}%{A2:"
                + on_click
                + " close "
                + wid
                + ":}%{A3:"
                + on_click
                + " slop_resize "
                + wid
                + ":}%{A4:"
                + on_click
                + " increment_size "
                + wid
                + ":}%{A5:"
                + on_click
                + " decrement_size "
                + wid
                + ":}"
            )
            if wid == focused:
                printf(active_left + " " + window + " " + active_right)
            else:
                printf(inactive_left + " " + window + " " + inactive_right)
            printf("%{A}%{A}%{A}%{A}%{A}")
        if len(window_workspace_pairs[workspace]) > max_windows:
            printf(f"+{len(window_workspace_pairs[workspace])-max_windows}")
    # except KeyError:
    # pass


def ensure_len(ID, length=10):
    while len(ID) < length - 1:
        ID = "0x0" + ID[2:]
    return ID


def wid_to_name(wid):
    if show == "class":
        return os.popen(f"xprop -id {wid} WM_CLASS").read().split('"')[:char_limit]
    if show == "window_classname":
        return (
            os.popen(f"xprop -id {wid} WM_CLASS")
            .read()
            .split('"')[:-1][-1][:char_limit]
        )
    if show == "window_title":
        return (
            os.popen(f"xprop -id {wid} _NET_WM_NAME").read().split('"')[1][:char_limit]
        )


def generate(workspaces):
    out = ""
    return out


def main():
    if len(sys.argv) <= 2:
        command = os.popen(
            "bspc subscribe desktop_focus desktop_add desktop_rename desktop_remove desktop_swap node_add node_remove node_swap node_transfer node_focus"
        )
        mon_id = os.popen(f"bspc query -M -m '{monitor}'").read()[:-1]
        workspaces = {}  # workspace ID and name pairs
        for workspace in [
            workspace[:-1]
            for workspace in os.popen(f"bspc query -D -m '{mon_id}'").readlines()
        ]:
            workspaces[workspace] = (
                [
                    window[:-1]
                    for window in os.popen(f"bspc query -N -d {workspace}").readlines()
                ],
                os.popen(f"bspc query -D -d {workspace} --names").read()[:-1],
            )

        focused_workspace = os.popen(f"bspc query -D -m {mon_id} -d .focused").read()[
            :-1
        ]  # ID of the currently focused workspace
        focused = os.popen(f"bspc query -N -m {mon_id} -n .focused").read()[
            :-1
        ]  # ID of the currently focused window
        while True:
            update = command.readline()[:-1]
            if mon_id in update:
                if "node" in update:
                    update = update[5:].split(" ")
                    if update[0] == "focus":
                        focused = update[-1]
                    elif update[0] == "add":
                        workspaces[update[2]][0].append(update[4])
                    elif update[0] == "remove":
                        workspaces[update[2]][0].remove(update[3])
                    elif update[0] == "swap":
                        if update[1] == mon_id:
                            workspaces[update[2]][0].remove(update[3])
                            workspaces[update[2]][0].append(update[6])
                        if update[4] == mon_id:
                            workspaces[update[5]][0].remove(update[6])
                            workspaces[update[5]][0].append(update[3])
                    else:
                        if update[1] == mon_id:
                            workspaces[update[2]][0].remove(update[3])
                        if update[4] == mon_id:
                            workspaces[update[5]][0].append(update[3])
                else:
                    update = update[8:].split(" ")
                    if update[0] == "focus":
                        focused_workspace = update[-1]
                    elif update[0] == "add":
                        workspaces[update[2]] = ([], update[-1])
                    elif update[0] == "rename":
                        workspaces[update[2]] = (
                            [
                                window[:-1]
                                for window in os.popen(
                                    f"bspc query -N -d {update[2]}"
                                ).readlines()
                            ],
                            update[-1],
                        )
                    elif update[0] == "remove":
                        workspaces.pop(update[-1])
                    else:
                        if update[1] == mon_id and update[3] == mon_id:
                            workspaces[update[2]], workspaces[update[4]] = (
                                workspaces[update[4]],
                                workspaces[update[2]],
                            )
                        else:
                            workspaces = {}  # workspace ID and name pairs
                            for workspace in [
                                workspace[:-1]
                                for workspace in os.popen(
                                    f"bspc query -D -m '{mon_id}'"
                                ).readlines()
                            ]:
                                workspaces[workspace] = (
                                    [
                                        window[:-1]
                                        for window in os.popen(
                                            f"bspc query -N -d {workspace}"
                                        ).readlines()
                                    ],
                                    os.popen(
                                        f"bspc query -D -d {workspace} --names"
                                    ).read()[:-1],
                                )

            print(wid_to_name())
            sys.stdout.flush()
            # break
    else:
        exec(sys.argv[2] + "(" + "'" + sys.argv[3] + "')")


def slop_resize(window):
    os.system(
        f"""bash -c 'bspc node "{window}" -g hidden=off &
bspc node "{window}" -g hidden=off &
xdo hide "{window}" &
pos="$(slop -b 2 -c 0.75,0.8,0.96.1 -f 0,%x,%y,%w,%h)"
xdo show "{window}"
bspc node "{window}" -t floating
wmctrl -ir "{window}" -e "$pos"
xdo activate "{window}"'"""
    )


def close(window):
    os.system("xdo close " + window)


def raise_or_minimize(window):
    if get_active_wid() == window:
        os.system("bspc node " + window + " -g hidden=on")
    else:
        os.system("bspc node " + window + " -g hidden=off")
        os.system("wmctrl -ia " + window)


def increment_size(window):
    os.system(f"xdo move -x -{resize_offset} -y -{resize_offset} {window}")
    os.system(f"xdo resize -w +{resize_increment} -h +{resize_increment} {window}")


def decrement_size(window):
    os.system(f"xdo move -x +{resize_offset} -y +{resize_offset} {window}")
    os.system(f"xdo resize -w -{resize_increment} -h -{resize_increment} {window}")


def switch_workspace(workspace):
    os.system(f"bspc desktop -f {workspace}")


def swap_workspace(workspace):
    os.system(f"bspc desktop -s {workspace}")


if __name__ == "__main__":
    # duration = timeit.Timer(main).timeit(number=20)
    # print(duration / 20)
    main()
