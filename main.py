import PySimpleGUI as sg
from psgtray import SystemTray
from datetime import datetime

steps = {
    0: ('Концентрация', 60, sg.SYSTEM_TRAY_MESSAGE_ICON_INFORMATION),
    1: ('Сопутствующая работа', 30, sg.EMOJI_BASE64_FACEPALM),
    2: ('Отдых', 30, sg.SYSTEM_TRAY_MESSAGE_ICON_CRITICAL),
}

PAUSE = 'Пауза/Пуск'
NEXT = 'Следующий этап'
EXIT = 'Выход'


def get_minute():
    return datetime.now().minute

def change_flag(flag, tray):
    flag = (flag + 1) % 3
    timer = steps[flag][1]
    tray.change_icon(steps[flag][2])
    tray.set_tooltip(f"{steps[flag][0]} {timer}")
    tray.show_message('Новый статус', steps[flag][0])
    return flag, timer

def loop(window, tray):
    flag = 0
    timer = steps[flag][1]
    last_minute = get_minute()
    pause = False

    while True:
        event, values = window.read(timeout=1000)

        if event == tray.key:
            event = values[event]

        if event in (sg.WIN_CLOSED, EXIT):
            tray.show_message('Выходим', 'Хорошего дня!')
            break

        if event in (PAUSE, sg.EVENT_SYSTEM_TRAY_ICON_ACTIVATED):
            pause = not pause
            if pause:
                tray.change_icon(sg.ICON_BUY_ME_A_COFFEE)
                tray.set_tooltip("Пауза")
                tray.show_message('Пауза', f"{steps[flag][0]} {timer}")
            else:
                tray.change_icon(steps[flag][2])
                tray.show_message('Пуск', f"{steps[flag][0]} {timer}")

        elif event == NEXT:
            flag, timer = change_flag(flag, tray)
            pause = False

        if pause:
            continue

        if (cur_minute := get_minute()) != last_minute:
            last_minute = cur_minute
            timer -= 1
            tray.set_tooltip(f"{steps[flag][0]} {timer}")
            if timer == 0:
                flag, timer = change_flag(flag, tray)


def main():
    tooltip = 'Supodoro'
    menu = ['', [PAUSE, NEXT, '---', EXIT]]

    layout = [[sg.T('Empty Window', key='-T-')]]
    window = sg.Window(tooltip, layout, finalize=True, enable_close_attempted_event=True, alpha_channel=0)
    window.hide()

    tray = SystemTray(
        menu, single_click_events=True, window=window,
        tooltip=f"{steps[0][0]} {steps[0][1]}", icon=steps[0][2], key='-TRAY-'
    )
    tray.show_message(tooltip, 'Приступаем к работе!')

    loop(window, tray)

    tray.close()
    window.close()


if __name__ == "__main__":
    main()
