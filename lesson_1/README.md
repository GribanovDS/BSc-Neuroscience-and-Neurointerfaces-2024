# Курс "Нейронауки и нейроинтерфейсы" – Неделя 12

## 🧠 Проектное занятие №1
Добро пожаловать на первое проектное занятие по курсу Центрального Университета "Нейронауки и нейроинтерфейсы" в 2025 году! Сегодня мы познакомимся с нейроинтерфейсом Neiry HeadBand и научимся получать данные, используя Python и CapsuleSDK

---

### Цель занятия

Научиться подключаться к устройству, получать ЭЭГ, PSD и другие данные в реальном времени и визуализировать их.

---

### По итогам занятия вы сможете:

1. Подключаться к устройству Neiry HeadBand
2. Считывать EEG, MEMS, PPG и PSD данные 
3. Отрисовывать графики EEG и PSD в реальном времени
4. Понимать разницу между монополярным и биполярным режимом  
4. Проходить калибровку с закрытыми глазами и собирать бейслайны  

---

## Требования перед стартом

- Python 3.11+  
- `CapsuleClient.dll` (Windows) или `libCapsuleClient.dylib` (macOS) в папке с кодом  
- Подключенное устройство Neiry HeadBand по Bluetooth  
- Установленные зависимости:
```bash
pip install numpy matplotlib
```

## Импорт необходимых библиотек

```python
# Инициализация и управление основной библиотекой CapsuleSDK, загрузка нативных библиотек.
from CapsuleSDK.Capsule import Capsule

# Класс для поиска (сканирования) доступных устройств Neiry по Bluetooth.
from CapsuleSDK.DeviceLocator import DeviceLocator

# Перечисление типов устройств, с которыми можно взаимодействовать (например, Neiry Band).
from CapsuleSDK.DeviceType import DeviceType

# Основной класс, представляющий подключенное устройство Neiry. Используется для подключения, отключения, получения данных и управления потоками данных.
from CapsuleSDK.Device import Device

# Класс, содержащий временные метки и значения ЭЭГ, полученные от устройства.
from CapsuleSDK.EEGTimedData import EEGTimedData

# Класс, предоставляющий значения сопротивления (импеданса) между электродами и кожей головы.
from CapsuleSDK.Resistances import Resistances

# Класс, содержащий данные спектральной плотности мощности (PSD) ЭЭГ.
from CapsuleSDK.PSDData import PSDData, PSDData_Band

# Классы для работы с датчиками MEMS (акселерометр, гироскоп) на устройстве.
from CapsuleSDK.MEMS import MEMS, MEMSTimedData

# Класс, содержащий данные фотоплетизмографии (PPG) и сердечного ритма.
from CapsuleSDK.PPGTimedData import PPGTimedData

# Классы для работы с оценками эмоций
from CapsuleSDK.Emotions import Emotions, Emotions_States

# Классы для работы с данными кардио (пульс, вариабельность ритма и т.д.).
from CapsuleSDK.Cardio import Cardio, Cardio_Data

# Классы для выполнения калибровки устройства (например, для определения индивидуального альфа-ритма).
from CapsuleSDK.Calibrator import Calibrator, IndividualNFBData
```

---
## 1. Подключение к устройству

- Локатор (DeviceLocator) — это специальный объект, предназначенный для поиска (сканирования) доступных устройств Neiry поблизости (обычно по Bluetooth)
- Колбэк (от англ. callback) — это функция, которая передаётся в другую функцию или метод в качестве аргумента и вызывается (или "срабатывает") в определённый момент выполнения программы, обычно когда происходит какое-то событие

#### Импорт библиотек
```python
import time
# import sys, os
# sys.path.append(os.path.join(os.getcwd(), "CapsuleSDK"))

PLATFORM = 'mac'  # 'mac' or 'win'

from CapsuleSDK.Capsule import Capsule
from CapsuleSDK.DeviceLocator import DeviceLocator
from CapsuleSDK.DeviceType import DeviceType
from CapsuleSDK.Device import Device
```
#### Функция ожидания события с таймаутом, обновляющая состояние локатора
```python
# Класс для для синхронизации основного потока с событиями, происходящими в колбэках.
class EventFiredState:
    # Инициализация состояния: _awake = False означает, что событие ещё не произошло
    def __init__(self): self._awake = False
    # Проверка, было ли событие: возвращает True, если set_awake() был вызван
    def is_awake(self): return self._awake
    # Установка флага: событие произошло
    def set_awake(self): self._awake = True
    # Сброс флага: событие не произошло
    def sleep(self): self._awake = False

# Глобальные переменные для хранения экземпляров локатора и устройства.
device_locator = None
device = None
# Экземпляры класса EventFiredState для отслеживания событий
device_list_event = EventFiredState()
device_conn_event = EventFiredState()
```

#### Обработчик списка событий
```python
def non_blocking_cond_wait(wake_event: EventFiredState, name: str, total_sleep_time: int):
    print(f"Waiting {name} up to {total_sleep_time}s...")
    steps = int(total_sleep_time * 50) # Разбиваем время на интервалы (0.02с каждый)
    for _ in range(steps):
        # Периодически обновляем состояние локатора, чтобы получать колбэки
        if device_locator is not None:
            try:
                device_locator.update()
            except Exception:
                pass
        # Проверяем, произошло ли ожидаемое событие
        if wake_event.is_awake():
            return True # Событие произошло, выходим из ожидания
        time.sleep(0.02) # Небольшая задержка
    return False # Таймаут истёк, событие не произошло
```

#### Обработчик списка найденных устройств
```python
# Обработчик получения списка найденных устройств
# Вызывается автоматически SDK после сканирования
def on_device_list(locator, info, fail_reason):
    global device
    if len(info) == 0:
        print("No devices found in this scan.")
        return
    print(f"Found {len(info)} device(s). Using first device:")
    info0 = info[0]
    print("Serial:", info0.get_serial())
    #TO DO

    #TO DO
    # Создаём экземпляр Device для первого найденного устройства
    device = Device(locator, info0.get_serial(), locator.get_lib())
    # Сообщаем, что событие "устройство найдено" произошло
    device_list_event.set_awake()
```

#### Обработчик изменения статуса подключения
```python
# Обработчик изменения статуса подключения устройства
# Вызывается автоматически SDK при изменении статуса
def on_connection_status_changed(dev, status):
    print("Connection status changed:", status)
    device_conn_event.set_awake()
```

#### Основная функция подключения и получения информации
```python
def main():
    global device_locator, device

    # Загружаем нативную библиотеку Capsule в зависимости от платформы
    if PLATFORM == 'win':
        capsuleLib = Capsule('./CapsuleClient.dll')
    else:
        capsuleLib = Capsule('./libCapsuleClient.dylib')

    # Создаём локатор устройств
    device_locator = DeviceLocator(capsuleLib.get_lib())

    # Устанавливаем обработчик для события получения списка устройств
    device_locator.set_on_devices_list(on_device_list)

    # Запрашиваем поиск устройств типа Band в течение 10 секунд
    device_locator.request_devices(device_type=DeviceType.Band, seconds_to_search=10)

    # Ждём, пока не будет найдено устройство (с таймаутом 12 секунд)
    if not non_blocking_cond_wait(device_list_event, 'device list', 12):
        print("No device discovered. Exiting.")
        return

    # Устанавливаем обработчик для события изменения статуса подключения
    device.set_on_connection_status_changed(on_connection_status_changed)
    device.connect(bipolarChannels=False) # монополярный режим

    # Ждём, пока подключение не будет установлено (с таймаутом 20 секунд)
    if not non_blocking_cond_wait(device_conn_event, 'device connection', 20):
        print("Device failed to connect.")
        return

    # Запускаем передачу данных с устройства
    device.start()

    # Считываем и печатаем основную информацию
    try:
        info = device.get_info()
        print("Device info:")
        print("serial:", info.get_serial())
        #TO DO

        #TO DO
    except Exception as e:
        print("Failed to get device info:", e)

    # Определяем внутреннюю функцию-обработчик для получения уровня батареи
    def on_battery(d, charge):
        print("Battery:", charge, "%")
    # Устанавливаем обработчик для события изменения уровня заряда батареи
    device.set_on_battery_charge_changed(on_battery)

    print("Letting callbacks run for 5 seconds to receive battery etc...")
    non_blocking_cond_wait(EventFiredState(), 'wait callbacks', 5)

    print("Stopping and disconnecting...")
    # Останавливаем передачу данных
    device.stop()
    # Отключаемся от устройства
    device.disconnect()
    print("Done.")

if __name__ == "__main__":
    main()
```

--- 
### Задание 1.1

Выведите еще такие характеристики устройства, как его название, прошивка, и тип: `info.get_firmware()`, `info.get_name()`, `info.get_type()`

--- 

## 2. Считываем и выводим сопротивление (импеданс) электродов

```python
# Импорт библиотек
from CapsuleSDK.Resistances import Resistances

# Функция-обработчик для передачи о сопротивлениях (импедансах) электродов
def on_resistances(resistances_obj: Resistances):
    # Получаем значения импеданса для каждого канала, преобразуем в Ом
    values = [resistances_obj.get_value(i) for i in range(len(resistances_obj))] # Ом
    print("Resistances:", values)

# Регистрация обработчика, чтобы, когда поступают данные импеданса, вызывалась наша функция
device.set_on_resistances(lambda dev, res: on_resistances(res))

print("Listening resistances for 10 seconds...")
# Ожидание 10 секунд, чтобы колбэки (включая on_resistances) могли быть вызваны
for _ in range(100):
    time.sleep(0.1)
    device_locator.update()

print("Stopping and disconnecting...")
# Останавливаем передачу данных
device.stop()
# Отключаемся от устройства
device.disconnect()
print("Done.")
```

--- 
### Задание 2.1

Сейчас сопротивление (импеданс) расчитано в Ом, рассчитайте его в кОм.

--- 

## 3. Считываем и выводим ЭЭГ в реал-тайме

```python
from CapsuleSDK.EEGTimedData import EEGTimedData

# Функция-обработчик для передачи данных ЭЭГ
def on_eeg(dev, eeg: EEGTimedData):
    # Получаем количество сэмплов (точек данных) в этом блоке
    samples = eeg.get_samples_count()
    # Получаем количество каналов ЭЭГ
    ch = eeg.get_channels_count()
    # Получаем временную метку первого сэмпла в блоке
    ts0 = eeg.get_timestamp(0) if samples>0 else None
    print(f"EEG block samples={samples}, channels={ch}, ts0={ts0}")
    # Если в блоке есть данные:
    if samples>0:
        # TO DO

        # TO DO
        # Получаем обработанные значения первого сэмпла для всех каналов
        vals = [eeg.get_processed_value(c, 0) for c in range(ch)]
        print(" first processed sample:", vals)
    # Сообщаем, что событие "получен первый блок ЭЭГ" произошло
    device_eeg_event.set_awake()

# Регистрация обработчика on_eeg в объекте device
device.set_on_eeg(on_eeg)

# device.start()

print("Listening for EEG for 15 seconds...")
# Ждём, пока не будет получен первый блок ЭЭГ (с таймаутом 10 секунд)
non_blocking_cond_wait(device_eeg_event, 'first eeg', 10)
# Дополнительное ожидание 15 секунд для продолжения получения и обработки данных ЭЭГ
non_blocking_cond_wait(EventFiredState(), 'streaming', 15)

#print("Stopping and disconnecting...")...
```

### Считываем MEMS
```python
# Импорт классов для работы с датчиками движения на устройстве (MEMS - Micro-Electro-Mechanical Systems)
from CapsuleSDK.MEMS import MEMS, MEMSTimedData

# MEMS - это акселерометр (измеряет линейное ускорение) и гироскоп (измеряет угловую скорость)
def on_mems(mems: MEMS, md: MEMSTimedData):
    cnt = len(md)
    if cnt>0:
        ts = md.get_timestamp(0)
        acc = md.get_accelerometer(0)
        gyro = md.get_gyroscope(0)
        # Получаем вектор ускорения (x, y, z) от акселерометра и вектор угловой скорости (x, y, z) от гироскопа
        print(f"MEMS sample ts={ts} acc=({acc.x:.3f},{acc.y:.3f},{acc.z:.3f}) gyro=({gyro.x:.3f},{gyro.y:.3f},{gyro.z:.3f})")
    mems_event.set_awake()

mems = MEMS(device, capsuleLib.get_lib())
mems.set_on_update(on_mems)

print("Listening MEMS for 15 seconds...")
non_blocking_cond_wait(mems_event, 'first mems', 10)
non_blocking_cond_wait(EventFiredState(), 'streaming mems', 15)
```

### Считываем PPG
```python
# Импорт класса для работы с данными фотоплетизмографии (PPG) и сердечного ритма.
# PPG (Photoplethysmography) - метод, измеряющий изменение объема крови в тканях,
# обычно используется для определения пульса и получения формы пульсовой волны.
from CapsuleSDK.PPGTimedData import PPGTimedData
from CapsuleSDK.Cardio import Cardio, Cardio_Data

def on_ppg(cardio: Cardio, ppg: PPGTimedData):
    cnt = len(ppg)
    if cnt > 0:
        ts = ppg.get_timestamp(0)
        # Получаем значение PPG (интенсивность света после прохождения через ткань) для первого сэмпла
        value = ppg.get_value(0)
        print(f"PPG sample ts={ts} value={value}")
    ppg_event.set_awake()

def on_cardio_indexes(cardio: Cardio, idx: Cardio_Data):
    # Выводим основные кардио-индексы
    print("Cardio: HR=", idx.heartRate, "stress=", idx.stressIndex)
    cardio_event.set_awake()

try:
    cardio = Cardio(device, capsuleLib.get_lib())
    cardio.set_on_ppg(on_ppg)
    cardio.set_on_indexes_update(on_cardio_indexes)
except Exception as e:
    print("Cardio not available:", e)

print("Listening PPG/Cardio for 15s...")
non_blocking_cond_wait(ppg_event, 'first ppg', 8)
non_blocking_cond_wait(cardio_event, 'first cardio', 12)
```

--- 
### Задание 3.1

Попробуйте отрисовать ЭЭГ в реальном времени для одного канала, используя `matplotlib`

### Задание 3.2

Попробуйте отрисовать ЭЭГ в реальном времени для нескольких каналов, используя `matplotlib`

--- 

### 4. Считываем и выводим PSD в реал-тайме

#### Импорт библиотек для обработки PSD и определение вспомогательной функции
```python
import numpy as np

def integrate_band(freqs, psd, low, hi):
    mask = (freqs>=low) & (freqs<=hi)
    if not np.any(mask): return 0.0
    return float(np.trapz(psd[mask], freqs[mask]))
```
#### Определение глобальных переменных и обработчика PSD
```python
psd_freqs = None
psd_vals = None
alpha_low = None
alpha_high = None
last_psd_vals = None

def on_psd(d, psd: PSDData):
    global psd_freqs, psd_vals, psd_event, alpha_low, alpha_high, last_psd_vals

    # Считываем значения частот
    freqs = np.array([psd.get_frequency(i) for i in range(psd.get_frequencies_count())])
    # # Получаем массив значений PSD
    vals = np.array([psd.get_psd(0, i) for i in range(psd.get_frequencies_count())])

    psd_freqs = freqs
    psd_vals = vals
    last_psd_vals = vals

    # Пытаемся получить индивидуальные границы альфа-диапазона, если калибровка была выполнена
    try:
        if psd.has_individual_alpha():
            alpha_low = psd.get_alpha_lower()
            alpha_high = psd.get_alpha_upper()
    # Если не удалось (например, калибровка не проводилась), используем стандартный диапазон
    except:
        alpha_low, alpha_high = 8.0, 13.0

    # Вывод в консоль
    print("PSD (канал 0) частоты 0-40 Гц:")
    for f,v in zip(freqs[freqs<=40], vals[freqs<=40]):
        if f % 10 ==0:
            print(f"{f:.1f}Hz: {v:.3e}")

    # Сообщаем, что событие "получен первый блок PSD" произошло
    psd_event.set_awake()

# Теперь, когда поступают данные PSD, будет вызываться наша функция
device.set_on_psd(on_psd)

print("Started. Listening PSD for 15s...")
# Ждём, пока не будет получен первый блок данных PSD (с таймаутом 12 секунд)
non_blocking_cond_wait(psd_event, 'first psd', 12)
# Дополнительное ожидание 15 секунд для продолжения получения и обработки данных PSD
non_blocking_cond_wait(EventFiredState(), 'streaming', 15)
```
--- 
### Задание 4.1

Реализуйте визуализацию PSD в реальном времени для одного канала, используя `matplotlib`

### Задание 4.2

Реализуйте визуализацию PSD в реальном времени для нескольких каналов, используя `matplotlib`

--- 
## 5. Калибровка с закрытыми глазами и сбор бейслайнов

### Зачем нужна калибровка
После калибровки можно получать индивидуальные пики, альфа/бета ритмы, стресс, концентрацию и другие метрики через соответствующие переменные:
`device.set_on_psd_data_received`, `device.set_on_eeg_data_received`, `device.set_on_cardio_data_received` и т.д.

```python
# Запуск быстрой калибровки. Устройство начнёт анализировать сигнал
# в течение заданного времени (обычно 25-35 секунд с закрытыми глазами)
# для определения индивидуальных характеристик мозговой активности (например, пика альфа-ритма)

def on_calibrated(calibrator: Calibrator, data: IndividualNFBData):
    print("Calibration finished. IndividualNFBData:")
    print(" timestamp:", data.timestampMilli)
    print(" lowerFrequency:", data.lowerFrequency)
    print(" upperFrequency:", data.upperFrequency)
    print(" individualFrequency:", data.individualFrequency)
    calibrated_event.set_awake()

calibrator = Calibrator(device, capsuleLib.get_lib())
calibrator.set_on_calibration_finished(on_calibrated)

print("Start QUICK closed-eye calibration")
print("Please close your eyes for 25-35 seconds")
calibrator.calibrate_quick()

if not non_blocking_cond_wait(calibrated_event, 'calibration finished', 40):
    print("Calibration did not finish or failed.")
else:
    try:
        data = calibrator.get_individual_nfb()
        print("Got Individual NFB data:")
        # Выводим границы индивидуального диапазона альфа-ритма
        print(" lower/upper:", data.lowerFrequency, data.upperFrequency)
        # Выводим индивидуальную частоту пик альфа-ритма
        print(" individualFrequency:", data.individualFrequency)
    except Exception as e:
        print("Cannot read individual NFB data:", e)
```
--- 
### Задание 5.1

Перейдите в файл `CapsuleSDK/Calibrator.py` и на основе информации оттуда реализуйте вывод мощности альфа-пика после калибровки

--- 

## Итоги
- Подключились к устройству Neiry HeadBand
- Разобрали, как получать и выводить EEG, MEMS, PPG и PSD
- Научились визуализировать EEG и PSD
- Пробовали калибровку и определение альфа-пика

## Что будет на следующем занятии
- Фильтрация сигналов
- Выделение альфа/бета диапазонов
- Простой классификатор ментальных состояний

## Попробуйте дома
- Запрограммировать отрисовку ЭЭГ, PSD нескольких каналов в графическом интерфейсе
- Запрограммировать считывание мощностей альфа, бета ритмов
- Придумать алгоритм на основе альфа/бета ритмов для управления устройствами (алгоритм выдает 0/1 или go/no go)

