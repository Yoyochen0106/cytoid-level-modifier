#!/usr/bin/env python3

import math
import itertools
import json
import collections
import os
import zipfile
import io
import shutil

import pydub
import pygame as pg


export_dir = 'build'
# fn = 'ebony.extreme.txt'

os.makedirs(export_dir, exist_ok = True)

def format_json(in_fname, out_fname):
    with open(in_fname, 'r') as f:
        obj = json.load(f)
    with open(out_fname, 'w') as f:
        json.dump(obj, f, indent = 2)

# format_json('charthard.txt', 'fmtchart.txt')

# with open(fn, 'r') as f:
#     lines = f.readlines()


class Namespace():
    pass

def change_level_speed(level_fname, out_level_fname, speed_factor, new_music_fname):

    lvl_dir = os.path.join(export_dir, 'lvl')
    os.makedirs(lvl_dir, exist_ok = True)

    def lvl_file(fname):
        return os.path.join(lvl_dir, fname)

    # shutil.copy(level_fname, out_level_fname)
    with zipfile.ZipFile(level_fname, 'r') as f:
        f.extractall(lvl_dir)

    with zipfile.ZipFile(level_fname, 'r') as in_f:
        lvl_obj = json.loads(in_f.read('level.json'))

        music_path_z = lvl_obj['music']['path']
        shutil.copy(new_music_fname, lvl_file(music_path_z))

        spd_text = f'x{speed_factor:.2f}'
        lvl_obj['id'] = f'yoyochen.spdmod.{spd_text}.' + lvl_obj['id']
        lvl_obj['title'] = lvl_obj['title'] + f' {spd_text}'

        for chart_obj in lvl_obj['charts']:

            chart_obj['difficulty'] = 0

            chart_path = chart_obj['path']
            with \
                    in_f.open(chart_path, 'r') as in_chart_b, \
                    io.TextIOWrapper(in_chart_b, encoding = 'utf-8-sig') as in_chart:

                lines = in_chart.readlines()
                chart = parse_cytus_chart(lines)
                change_chart_speed(chart, speed_factor)
                lines = format_cytus_chart(chart)
                with open(lvl_file(chart_path), 'w') as f:
                    for line in lines:
                        f.write(line)
                        f.write('\n')

        with open(lvl_file('level.json'), 'w') as f:
            json.dump(lvl_obj, f, indent = 2)

    fname = shutil.make_archive(out_level_fname, 'zip', lvl_dir)
    if fname != out_level_fname:
        os.rename(fname, out_level_fname)


    # zipfile.ZipFile(out_level_fname, 'w') as out_f

def parse_cytus_chart(lines):
    chart = Namespace()
    chart.version = None
    chart.bpm = None
    chart.page_shift = None
    chart.page_size = None
    chart.notes = []
    chart.links = []
    for line in lines:
        items = line.split()
        if len(items) == 0:
            continue
        head = items[0]
        if head == 'VERSION':
            chart.version = int(items[1])
        if head == 'BPM':
            chart.bpm = float(items[1])
        if head == 'PAGE_SHIFT':
            chart.page_shift = float(items[1])
        if head == 'PAGE_SIZE':
            chart.page_size = float(items[1])
        if head == 'NOTE':
            chart.notes.append(note_t(
                int(items[1]),
                float(items[2]),
                float(items[3]),
                float(items[4]),
            ))
        if head == 'LINK':
            chart.links.append([int(i) for i in items[1:]])
    return chart


note_t = collections.namedtuple('note_t', 'id timing x duration')

# chart = parse_cytus_chart(lines)

def change_chart_speed(chart, factor):

    chart.bpm *= factor
    chart.page_shift /= factor
    chart.page_size /= factor
    chart.notes = [
        note_t(
            note.id,
            note.timing / factor,
            note.x,
            note.duration / factor,
        )
        for note in chart.notes
    ]

# Just play
class ListInsert(list):
    def __lshift__(self, item):
        self.append(item)
        return self

def format_cytus_chart(chart):
    lines = ListInsert()
    lines << f'VERSION {chart.version}'
    lines << f'BPM {chart.bpm}'
    lines << f'PAGE_SHIFT {chart.page_shift}'
    lines << f'PAGE_SIZE {chart.page_size}'
    for note in chart.notes:
        lines << f'NOTE\t{note.id}\t{note.timing}\t{note.x}\t{note.duration}'
    for link in chart.links:
        ids = ' '.join(str(n) for n in link)
        lines << f'LINK {ids}'
    return lines

# lines = format_cytus_chart(chart)

# with open('outchart.txt', 'w', newline = '\n') as f:
#     for line in lines:
#         f.write(line)

change_level_speed(
    './fwapy.ebonyi.cytoidlevel',
    './build/yoyochen.spdmod.0.80.fwapy.ebonyi.cytoidlevel',
    0.8,
    './ebony-spd0.8.mp3'
)

change_level_speed(
    './fwapy.ebonyi.cytoidlevel',
    './build/yoyochen.spdmod.0.70.fwapy.ebonyi.cytoidlevel',
    0.7,
    './ebony-spd0.7.mp3'
)

change_level_speed(
    './fwapy.ebonyi.cytoidlevel',
    './build/yoyochen.spdmod.0.60.fwapy.ebonyi.cytoidlevel',
    0.6,
    './ebony-spd0.6.mp3'
)

change_level_speed(
    './fwapy.ebonyi.cytoidlevel',
    './build/yoyochen.spdmod.0.50.fwapy.ebonyi.cytoidlevel',
    0.5,
    './ebony-spd0.5.mp3'
)

change_level_speed(
    './fwapy.ebonyi.cytoidlevel',
    './build/yoyochen.spdmod.0.40.fwapy.ebonyi.cytoidlevel',
    0.4,
    './ebony-spd0.4.mp3'
)

exit(0)


BPM = 150
BPS = BPM / 60.0
one_beat_sec = 60.0 / BPM
page_size_sec = one_beat_sec * 4
shift = page_size_sec * 2

chart = Namespace()

c = itertools.count()

class Helper():
    def __init__(self):
        self.beat = 0
    def full(self):
        b = self.beat
        self.beat += 2
        return b / 2
    def half(self):
        b = self.beat
        self.beat += 1
        return b / 2
    # Same as following note
    def same(self):
        return self.beat / 2

h = Helper()

chart.version = 2
chart.bpm = BPM
chart.page_shift = shift
chart.page_size = page_size_sec


def page_2hhh2():
    L, M, R = 0.4, 0.5, 0.6
    return [
        [h.same(), L, 0],
        [h.full(), R, 0],
        [h.half(), L, 0],
        [h.half(), M, 0],
        [h.full(), L, 0],
        [h.same(), L, 0],
        [h.full(), R, 0],
    ]
def page_8x4():
    L, M, R = 0.4, 0.5, 0.6
    return [
        [h.half(), L, 0],
        [h.half(), R, 0],
        [h.half(), L, 0],
        [h.half(), R, 0],
        [h.half(), L, 0],
        [h.half(), R, 0],
        [h.half(), L, 0],
        [h.half(), R, 0],
    ]
def page_4():
    L, M, R = 0.4, 0.5, 0.6
    return [
        [h.full(), R, 0],
        [h.full(), R, 0],
        [h.full(), R, 0],
        [h.full(), R, 0],
        [h.full(), M, 0],
        [h.full(), M, 0],
        [h.full(), M, 0],
        [h.full(), M, 0],
    ]
def page_3_3():
    L, R = 0.6, 0.8
    return [
        [h.half(), R, 0],
        [h.half(), L, 0],
        [h.full(), R, 0],
        [h.half(), L, 0],
        [h.half(), R, 0],
        [h.full(), L, 0],
    ]

page = page_3_3

chart.notes = [
    *page(),
    *page(),
    *page(),
    *page(),
]
chart.links = [
]

# Convert beat number to second
for note in chart.notes:
    note[0] *= one_beat_sec

# Shift process
for note in chart.notes:
    note[0] += shift

def generate_chart(out):
    out.write(f'VERSION {chart.version}\n')
    out.write(f'BPM {chart.bpm}\n')
    out.write(f'PAGE_SHIFT {chart.page_shift}\n')
    out.write(f'PAGE_SIZE {chart.page_size}\n')
    for id_, note in enumerate(chart.notes):
        out.write(
            f'NOTE\t{id_}\t{note[0]}\t{note[1]}\t{note[2]}\n'
        )
    for link in chart.links:
        # print(link)
        id_list_str = ' '.join(f'{id_:d}' for id_ in link)
        out.write(
            f'LINK {id_list_str}\n'
        )

def export_fn(fn):
    return os.path.join(export_dir, fn)



import numpy as np

sample_rate = 44100

def generate_t(duration):
    ticks = np.arange(int(sample_rate * duration))
    t = ticks / sample_rate # in seconds
    return t
freq = 442 / 2

def generate_tap():
    # Base
    total_time = 0.5
    t = generate_t(total_time)
    tap = np.cos(2*np.pi * freq * t)

    def interp(t, duration):
        # t/duration: normalize to [0 ~ 1]
        return 3*(t/duration)**2 - 2*(t/duration)**3

    # # Decay
    k = -5
    gain = np.exp(k * generate_t(total_time))
    # gain = np.exp(k * generate_t(0.5))[::-1]
    # gain = interp(generate_t(0.5), 0.5)
    mx = gain.max(); mn = gain.min()
    gain -= mn
    gain /= mx - mn
    L = len(gain)

    # tap[:L] *= gain
    # tap[L:] *= gain[::-1]
    tap *= gain

    # Linear decay
    decay_time = 0.3
    gain = generate_t(total_time) / decay_time
    gain[gain > 1] = 1
    gain = 1 - gain
    # tap *= gain ** 0.5

    # Linear ramp up
    ramp_time = 0.05
    gain = generate_t(total_time) / ramp_time
    gain[gain > 1] = 1
    # tap *= gain

    # Fade in & Fade out
    # fade_time = 0.1
    # t = np.arange(int(sample_rate * fade_time)) / sample_rate
    # gain = t / fade_time
    # L = len(gain)
    # tap[:L] = gain
    # tap[-L:] = gain[::-1]

    # Scale from -1 ~ 1 to fit 0~255
    tap *= 127
    tap += 128

    return tap

tap = generate_tap()

import matplotlib.pyplot as plot

def f():
    # t = generate_t(1)
    # t = 3*t**2 - 2*t**3
    plot.plot(tap)
    plot.show()
# f()

data = tap
tap_segm = pydub.AudioSegment(
    data.astype(np.uint8),
    frame_rate = sample_rate,
    sample_width = 1, # bytes 
    channels = 1
)

tap_segm.export(export_fn('tap.mp3'), format = 'mp3')

# exit(0)

def make_audio_obj():
    total_time = 10 # seconds
    segm = pydub.AudioSegment.silent(1000 * (shift + total_time), sample_rate)
    for i in range(int(total_time / one_beat_sec)):
        sec = shift + i * one_beat_sec
        segm = segm.overlay(tap_segm, position = 1000 * sec)
    return segm

obj = make_audio_obj()
obj.export(export_fn('full.mp3'))
# obj.export(export_fn('tap.mp3'), format = 'mp3')

def speeddown(seg, playback_speed=1.5, chunk_size=150, crossfade=25):
    # we will keep audio in 150ms chunks since one waveform at 20Hz is 50ms long
    # (20 Hz is the lowest frequency audible to humans)

    # portion of AUDIO TO KEEP. if playback speed is 1.25 we keep 80% (0.8) and
    # discard 20% (0.2)
    atk = 1.0 / playback_speed

    if playback_speed < 2.0:
        # throwing out more than half the audio - keep 50ms chunks
        ms_to_remove_per_chunk = int(chunk_size * (1 - atk) / atk)
    else:
        # throwing out less than half the audio - throw out 50ms chunks
        ms_to_remove_per_chunk = int(chunk_size)
        chunk_size = int(atk * chunk_size / (1 - atk))

    # the crossfade cannot be longer than the amount of audio we're removing
    crossfade = min(crossfade, ms_to_remove_per_chunk - 1)

    # DEBUG
    #print("chunk: {0}, rm: {1}".format(chunk_size, ms_to_remove_per_chunk))

    chunks = make_chunks(seg, chunk_size + ms_to_remove_per_chunk)
    if len(chunks) < 2:
        raise Exception("Could not speed up AudioSegment, it was too short {2:0.2f}s for the current settings:\n{0}ms chunks at {1:0.1f}x speedup".format(
            chunk_size, playback_speed, seg.duration_seconds))

    # we'll actually truncate a bit less than we calculated to make up for the
    # crossfade between chunks
    ms_to_remove_per_chunk -= crossfade

    # we don't want to truncate the last chunk since it is not guaranteed to be
    # the full chunk length
    last_chunk = chunks[-1]
    chunks = [chunk[:-ms_to_remove_per_chunk] for chunk in chunks[:-1]]

    out = chunks[0]
    for chunk in chunks[1:]:
        out = out.append(chunk, crossfade=crossfade)

    out += last_chunk
    return out

audio = pydub.AudioSegment.from_file('./audio.mp3', format = 'mp3')
audio = audio[:5000]
import pydub.effects
def speeddown(spd, frame_size_ms = 200):
    canvas = pydub.AudioSegment.silent(int(len(audio) * spd))
    canvas.overlay()
    return canvas

audio = speeddown(audio, 0.5)
audio.export(export_fn('spd.mp3'))

exit(0)

# from pydub.playback import play
# play(obj)
# exit(0)

def generate_audio(stream):
    segm = make_audio_obj()
    segm.export(stream, format = 'mp3')


def generate_bg(stream):
    # Generate image
    image = pg.Surface((200, 200))
    image.fill((255, 255, 000), [000, 000, 100, 100])
    image.fill((000, 255, 255), [100, 000, 100, 100])
    image.fill((255, 000, 255), [000, 100, 100, 100])
    image.fill((000, 000, 000), [100, 100, 100, 100])
    pg.image.save(image, stream)


def generate_leveljson(stream):
    level_obj = {
        "version": 1,
        "schema_version": 2,
        "id": level_id,
        "title": "TEST",
        "artist": "Fallen Shepherd ft. RabbiTon Strings",
        "artist_source": "https:\/\/www.iosysos.com\/",
        "illustrator": "amirulhafiz",
        "illustrator_source": "https:\/\/www.deviantart.com\/amirulhafiz",
        "charter": "mekko",
        "music": {
            "path": "audio.mp3"
        },
        "music_preview": {
            "path": "audio.mp3"
        },
        "background": {
            "path": "bg.png"
        },
        "charts": [
            {
                "type": "extreme",
                "difficulty": 16,
                "path": "chart.txt"
            }
        ],
        "title_localized": None,
        "artist_localized": None
    }

    json.dump(level_obj, stream)

level_id = 'yoyochen-test'
def generate_cytoidlevel():
    filename = export_fn(f'{level_id}.zip')
    os.remove(filename)
    with zipfile.ZipFile(filename, 'w') as zf:
        with zf.open('audio.mp3', 'w') as f:
            stream = io.BytesIO()
            generate_audio(stream)
            f.write(stream.getvalue())
        with zf.open('bg.png', 'w') as f:
            stream = io.BytesIO()
            generate_bg(stream)
            f.write(stream.getvalue())
        with zf.open('chart.txt', 'w') as f, \
                io.TextIOWrapper(f, encoding = 'utf-8') as stream:
            generate_chart(stream)
        with zf.open('level.json', 'w') as f, \
                io.TextIOWrapper(f, encoding = 'utf-8') as stream:
            generate_leveljson(stream)
    print(f'Wrote to {filename}')

generate_cytoidlevel()
