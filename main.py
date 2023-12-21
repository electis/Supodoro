import base64
import io

from PIL import Image, ImageDraw, ImageFont
import PySimpleGUI as sg
from psgtray import SystemTray
from datetime import datetime

steps = {
    0: ('Концентрация', 60, 'green'),
    1: ('Сопутствующая работа', 30, 'yellow'),
    2: ('Отдых', 30, 'red'),
}

B_PAUSE = 'Пауза/Пуск'
B_NEXT = 'Следующий этап'
B_EXIT = 'Выход'


def image_to_byte_array(image):
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format='PNG')
    return base64.b64encode(imgByteArr.getvalue())

def generate_icon(text, color):
    width, height = 32, 32
    text = str(text)
    img = Image.new('RGB', (width, height), color)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 24)
    length = draw.textlength(text, font)
    x = (width - length) / 2
    y = 2
    draw.text((x, y), text, fill='black', font=font)
    return image_to_byte_array(img)


def get_minute():
    return datetime.now().minute

def change_flag(flag, tray):
    flag = (flag + 1) % 3
    timer = steps[flag][1]
    status = steps[flag][0]
    tray.change_icon(generate_icon(timer, steps[flag][2]))
    tray.set_tooltip(f'{status} {timer}')
    tray.show_message('Новый статус', status)
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

        if event in (sg.WIN_CLOSED, B_EXIT):
            tray.show_message('Выходим', 'Хорошего дня!')
            break

        if event in (B_PAUSE, sg.EVENT_SYSTEM_TRAY_ICON_ACTIVATED):
            pause = not pause
            if pause:
                tray.change_icon(generate_icon('||', 'blue'))
                tray.set_tooltip('Пауза')
                tray.show_message('Пауза', f'{steps[flag][0]} {timer}')
            else:
                tray.change_icon(generate_icon(timer, steps[flag][2]))
                tray.show_message('Пуск', f'{steps[flag][0]} {timer}')

        elif event == B_NEXT:
            flag, timer = change_flag(flag, tray)
            pause = False

        if pause:
            continue

        if (cur_minute := get_minute()) != last_minute:
            last_minute = cur_minute
            timer -= 1
            tray.set_tooltip(f'{steps[flag][0]} {timer}')
            tray.change_icon(generate_icon(timer, steps[flag][2]))
            if timer == 0:
                flag, timer = change_flag(flag, tray)


def main():
    tooltip = 'Supodoro'
    menu = ['', [B_PAUSE, B_NEXT, '---', B_EXIT]]

    layout = [[sg.T('Empty Window', key='-T-')]]
    window = sg.Window(tooltip, layout, finalize=True, enable_close_attempted_event=True, alpha_channel=0)
    window.hide()

    tray = SystemTray(
        menu, single_click_events=True, window=window,
        tooltip=f'{steps[0][0]} {steps[0][1]}', icon=generate_icon(steps[0][1], steps[0][2]), key='-TRAY-'
    )
    tray.show_message(tooltip, 'Приступаем к работе!')

    loop(window, tray)

    tray.close()
    window.close()


if __name__ == '__main__':
    main()
