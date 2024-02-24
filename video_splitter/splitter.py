import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
from typing import NamedTuple
import yaml

class Timestamp(NamedTuple):
    h: int
    m: int
    s: int

@dataclass
class Section:
    name: str
    start: Timestamp
    end: Timestamp | None

    @property
    def start_seconds(self):
        return self.start[0] * 3600 + self.start[1] * 60 + self.start[2]
    
    @property
    def duration(self):
        if self.end is None:
            return None
        end_seconds = self.end[0] * 3600 + self.end[1] * 60 + self.end[2]
        return end_seconds - self.start_seconds

    def to_string(self):
        return f'{self.name}:\n\t{self.start.h}h {self.start.m}m {self.start.s}s -> {self.end.h}h {self.end.m}m {self.end.s}s \n\t({self.duration} seconds)'

Cfg = list[Section]

def parse_time(t: str | float) -> Timestamp:
    """Parses time into tuple of [h,m,s].
    
    Float format is just minutes

    String formats are:
        * '[hh:]mm:ss'
        * '[XH][, ][YM][, ][ZS]'
            (where H, M, and S are literals, case-insensitive)
    All but the last component should be ints
    Smallest component can be a float

    """
    try:
        t = float(t)
    except ValueError:
        pass
    if isinstance(t, float):
        h = int(t // 60)
        m = int(t % 60)
        s = (t % 1) * 60
        return Timestamp(h, m, s)

    colon_re = r'(?P<hours>\d+)?:(?P<minutes>\d+):(?P<seconds>\d+)'
    match = re.match(colon_re, t)
    if match is not None:
        groups = match.groupdict()
        h = int(groups['hours']) if groups['hours'] is not None else 0
        m = int(groups['minutes'])
        s = float(groups['seconds'])
    else:
        letter_re = r'((?P<hours>\d+)[hH],?\s*)?((?P<minutes>\d+)[mM],?\s*)?((?P<seconds>\d+)[sS],?\s*)?'
        match = re.match(letter_re, t)
        assert match is not None, f'Invalid time format: {t}'
        groups = match.groupdict()
        h = int(groups['hours']) if groups['hours'] is not None else 0
        m = int(groups['minutes']) if groups['minutes'] is not None else 0
        s = float(groups['seconds']) if groups['seconds'] is not None else 0

    if s >= 60:
        m += s // 60
        s = s % 60
    if m >= 60:
        h += m // 60
        m = m % 60
    return Timestamp(h, m, s)


def extract_section(input: Path, out_dir: Path, section: Section):
    out_dir.mkdir(exist_ok=True, parents=True)
    duration_flag = []
    if section.end is not None:
        duration_flag = [
            "-t",
            str(section.duration)
        ]
    filename = out_dir / f'{section.name}{input.suffix}'

    # https://unix.stackexchange.com/a/1675
    args = [
        "ffmpeg",
        "-i",
        str(input),
        "-c",
        "copy",
        "-ss",
        str(section.start_seconds),
        *duration_flag,
        str(filename)
    ]
    print("Running " + " ".join(args))
    subprocess.check_call(args)

def load_config(file: Path) -> Cfg:
    with file.open() as f:
        contents = f.read()
        contents = contents.replace("\t", "    ")
        cfg = yaml.safe_load(contents)

    sections: list[Section] = []
    prev_start = (0,0,0)
    for k, v in cfg.items():
        section_cfg = Section(name=k, start=prev_start, end=-1)
        if isinstance(v, dict):
            if 'start' in v:
                section_cfg.start = parse_time(v['start'])
            if 'end' in v:
                section_cfg.end = parse_time(v['end'])
        elif isinstance(v, (float, int)):
            section_cfg['end'] = v
        else:
            raise ValueError(f'Invalid section config: {v}')
        sections.append(section_cfg)
    return sections

def split_file(file: Path, out_dir: Path, cfg: Cfg):
    for section in cfg:
        extract_section(file, out_dir, section)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=Path)
    parser.add_argument('config', type=Path)
    parser.add_argument('-o', '--output', type=Path, default=None)

    args = parser.parse_args()
    if args.output is None:
        args.output = args.input.with_name(f'{args.input.stem}_split')
    
    cfg = load_config(args.config)
    print("Config is: ")
    for section in cfg:
        print(section.to_string())
    split_file(args.input, args.output, cfg)

if __name__ == "__main__":
    main()