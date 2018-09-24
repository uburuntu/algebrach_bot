# Algebrach Bot on Aiogram

Реализация [@algebrach_bot](https://t.me/algebrach_bot) на модуле aiogram.

Написан на Python 3.6, установка всех необходимых модулей осуществляется командой
```sh
pip3 install -r --user requirements.txt
```

### Доступные команды (WIP)
* `/start` — приветствие при первом запуске
* `/help` — список команд и описание их использования
* `/links` — список полезных мехматовских ссылок
* `/wifi` — список доступных Wi-Fi сетей на мехмате
* `/chats` — список связанных с мехматом чатов
* `/channels` — список некоторых каналов
* `/rules` — правила чата
* `/wiki` — краткий вариант вики-статьи по запросу
* `/wolfram` (`/wf`) — вычисления [WolframAlpha](https://www.wolframalpha.com/) по запросу
* `/arxiv` — либо случайная статья с [arXiv](https://arxiv.org/), либо поиск статьи по запросу
* `/roll` — рандомное число от 00 до 100
* `/d6` — бросить шестигранные кости, можно указать количество
* `/dn 'N' 'M'` — бросить M N-гранных костей
* `/truth` — истина в последней инстанции
* `/gender` — определяет гендерную пренадлежность
* `/me` — дань соответствующей команде эпохи IRC
* `/kek` — кек пек

### Контрибьюторы
[![](https://img.shields.io/badge/Стасик-%40django__python-blue.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAEbklEQVQ4y62US2xUdRjFf%2F%2F%2FfUynnXaGKW15FHnVKm8SRCFB3ZhYRVQSISHKBhKjK2JiTIyuXJC40oUrY%2BJGTZSABomiC0kUFYEIFRWrQi1tmXb6mE7be%2BfOvf%2F7%2F1z0Ydh71t93vpPz5RxlUoujFSOB4dxQQGKFUs2AFRIr9%2FRVzdO%2FVZNVvqPsjqL31%2BYl3icNjh4dDAyNrsPzm%2FL4riZOhRbfwWUeAohAe9ZhrG6af6mYF27X0gPVRHZ6jsYquDxpGAjSJ7rz3om2jHqv2VOLuwtQCwpHA8NvExEXx6JnTg6Eb0%2FU7UpPK3Kewp3bI05hOrEIkHPV1aPduRePbStesAKhseQ8B63V3HRHk8t3o9HLx3unTlRju7KjQVPwFM68chHwNLRlNB0NmtlEtr%2FZO%2FXjlwNBj1aKxM4rjJKUjKv5ZijY2%2FPF8JmuvE%2Fe%2B29gAVqBo6CeCkOBoT3rkFgo14y8%2B%2FCy9bs6sv2rci66HCZcG69lX%2Fq%2B%2FEGrr2lxFbERxAoiggY0Qjk0XB6NGJpN2NORZU3Oo8lRiBX14Z%2FVjypROnc46zqcvRUe7avEhVVNLnVjAcHVEBnL9cmIa%2BMRSzzNqzuWcvrxTk49tpINBZ8%2FKnW6WjzOl2q7LowEewDci6Nh57nh4Lmcq0itRaMYDQ3DMwltjR777sqxv6uFA13Nd1jQOx6R1aAEYmO5Ol5%2FFjjvfnZz5sDgdPJAq68RC4OzCe1ZhyP3t3Ho7jwbij4ApUrITJKybmmOSpRyqxpT8B2SVCj6Dr3j9e0A7ve3wy6FwtOKG1N1jm1v5Y3d7YtKarHhymCVfKPHpuUtAFwZrzMwk7A%2B72OskPcUlZopzHnoaJOKYK2lkHG4NBJy%2FKcxfh2LCGoxlwerrCg0LJIB9FfrRIkFmXtcnFpEJAXQPaubfnQgmK6nFD3FlXLEa%2BdK7Pn4Jt%2FerLCxNcua1qY7%2FLtYqqERsIISYSwwrGh0RwD00c3Fk1taM1%2BVZhJiKyzJaDYub6CaCH8HQjBW4cyv5TsIf5%2BIaHQUqVhEhGpk6Mr75wF0aTZJugv%2Bu1YEY4XUWlIrNHmKn8s1zo7E7Ds1yJMn%2BxcJ%2ByYjChmNFZiqGVobHJ5Y1%2Fw%2BgDsaGnrWNn91qRRe%2BLp%2Feld3a5bEWFY0aM4N1zg9AJ3LGvm8b4pHT9xkdYsHVshqhSPC7Yk6h7YW3%2BlZ2zwAoH4ph6xo9vhhKOg8cmbgulEq197kYUWI5%2BPna%2FAcRX81JjLChmIGC%2FSVa%2BzszPV9un%2FNFoRkZbOHrqfCWJiitRp6ZH1%2Bj68YuTFVJ04FX4GrhNQKUWLpzHl0F3wmaoYbkxH3Lm24%2Bvru9gcLvpPUzHz0FoI%2FW7fE1vYe3lK8b%2B%2FalhNBnFIOEyZDgxXBpEJ5NqE0m5BxVPpQZ%2B6tV3a17xAYGw0NC621WLBKwXQ9pcV3hw9vzh3M%2BWr74ExyMDGy7XaQLHM1srUt2681l5%2Fqyn9shH8mohTf0TgK0vmWVSLC%2F4l%2FAXWxRtaDbtHIAAAAAElFTkSuQmCC)](https://t.me/django_python)

[![](https://img.shields.io/badge/OG-%40arv__ego-blue.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAEbklEQVQ4y62US2xUdRjFf%2F%2F%2FfUynnXaGKW15FHnVKm8SRCFB3ZhYRVQSISHKBhKjK2JiTIyuXJC40oUrY%2BJGTZSABomiC0kUFYEIFRWrQi1tmXb6mE7be%2BfOvf%2F7%2F1z0Ydh71t93vpPz5RxlUoujFSOB4dxQQGKFUs2AFRIr9%2FRVzdO%2FVZNVvqPsjqL31%2BYl3icNjh4dDAyNrsPzm%2FL4riZOhRbfwWUeAohAe9ZhrG6af6mYF27X0gPVRHZ6jsYquDxpGAjSJ7rz3om2jHqv2VOLuwtQCwpHA8NvExEXx6JnTg6Eb0%2FU7UpPK3Kewp3bI05hOrEIkHPV1aPduRePbStesAKhseQ8B63V3HRHk8t3o9HLx3unTlRju7KjQVPwFM68chHwNLRlNB0NmtlEtr%2FZO%2FXjlwNBj1aKxM4rjJKUjKv5ZijY2%2FPF8JmuvE%2Fe%2B29gAVqBo6CeCkOBoT3rkFgo14y8%2B%2FCy9bs6sv2rci66HCZcG69lX%2Fq%2B%2FEGrr2lxFbERxAoiggY0Qjk0XB6NGJpN2NORZU3Oo8lRiBX14Z%2FVjypROnc46zqcvRUe7avEhVVNLnVjAcHVEBnL9cmIa%2BMRSzzNqzuWcvrxTk49tpINBZ8%2FKnW6WjzOl2q7LowEewDci6Nh57nh4Lmcq0itRaMYDQ3DMwltjR777sqxv6uFA13Nd1jQOx6R1aAEYmO5Ol5%2FFjjvfnZz5sDgdPJAq68RC4OzCe1ZhyP3t3Ho7jwbij4ApUrITJKybmmOSpRyqxpT8B2SVCj6Dr3j9e0A7ve3wy6FwtOKG1N1jm1v5Y3d7YtKarHhymCVfKPHpuUtAFwZrzMwk7A%2B72OskPcUlZopzHnoaJOKYK2lkHG4NBJy%2FKcxfh2LCGoxlwerrCg0LJIB9FfrRIkFmXtcnFpEJAXQPaubfnQgmK6nFD3FlXLEa%2BdK7Pn4Jt%2FerLCxNcua1qY7%2FLtYqqERsIISYSwwrGh0RwD00c3Fk1taM1%2BVZhJiKyzJaDYub6CaCH8HQjBW4cyv5TsIf5%2BIaHQUqVhEhGpk6Mr75wF0aTZJugv%2Bu1YEY4XUWlIrNHmKn8s1zo7E7Ds1yJMn%2BxcJ%2ByYjChmNFZiqGVobHJ5Y1%2Fw%2BgDsaGnrWNn91qRRe%2BLp%2Feld3a5bEWFY0aM4N1zg9AJ3LGvm8b4pHT9xkdYsHVshqhSPC7Yk6h7YW3%2BlZ2zwAoH4ph6xo9vhhKOg8cmbgulEq197kYUWI5%2BPna%2FAcRX81JjLChmIGC%2FSVa%2BzszPV9un%2FNFoRkZbOHrqfCWJiitRp6ZH1%2Bj68YuTFVJ04FX4GrhNQKUWLpzHl0F3wmaoYbkxH3Lm24%2Bvru9gcLvpPUzHz0FoI%2FW7fE1vYe3lK8b%2B%2FalhNBnFIOEyZDgxXBpEJ5NqE0m5BxVPpQZ%2B6tV3a17xAYGw0NC621WLBKwXQ9pcV3hw9vzh3M%2BWr74ExyMDGy7XaQLHM1srUt2681l5%2Fqyn9shH8mohTf0TgK0vmWVSLC%2F4l%2FAXWxRtaDbtHIAAAAAElFTkSuQmCC)](https://t.me/arv_ego)