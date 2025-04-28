import argparse
import os
import subprocess
from pathlib import Path

import pandas as pd
import srt

MAX_T = 30_000
MAX_DIFF = 3_000


def parse_args():
    """
    Creates an argparse parser
    """
    parser = argparse.ArgumentParser(
        description="Segment .mp3 files according to a provided .srt closed caption file",
        prog="srt-parse",
    )

    parser.add_argument("audio_input", type=str, help="Location of .mp3 file to be processed")
    parser.add_argument("srt_input", type=str, help="Location of .srt file to be processed")
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Directory for processed files to be saved to",
        default="processed_data",
    )
    args = parser.parse_args()
    assert args.audio_input.endswith(".mp3")
    assert args.srt_input.endswith(".srt")

    # Check if output path exists and is a directory
    try:
        if not os.path.exists(args.output_dir):
            Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        parser.error(f"Output path {args.output_dir} is not a directory.\nsrt-parse will now exit.")

    print(args.audio_input)
    return args


def get_subs(srt_input):
    """
    Returns a generator yielding parsed captions from the .srt
    """
    try:
        with open(srt_input, "r", encoding="utf-8") as f:
            str_sub = "".join(f.readlines())
            return (sub for sub in srt.parse(str_sub))
    except FileNotFoundError:
        print("ERROR, no srt file found")


def get_times_conent(sub):
    """
    Returns the indexes used to slice the corresponding audio from the subtitle
    and its content

    Keyword arguments:
    sub - a srt subtitle
    """
    content = sub.content.replace("\n", " ").strip()

    # filter songs and names of chapters
    if "#" in content or content.isupper():
        content = ""

    start = int(sub.start.total_seconds() * 1000)
    end = int(sub.end.total_seconds() * 1000)
    return start, end, content


def time_format(t):
    hours = t // 3_600_000
    minutes = (t % 3_600_000) // 60_000
    seconds = t / 1_000 % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:05.2f}"


def escape(s):
    return (
        s.replace("(", "\\(")
        .replace(")", "\\)")
        .replace("[", "\\[")
        .replace("]", "\\]")
        .replace("|", "\\|")
    )


def ffmpeg_command(audio_input, t0, t1, clip_name):
    """ffmpeg command to split audio by time"""
    command = (
        f"ffmpeg -i {escape(audio_input)} "
        f"-ss {time_format(t0)} -to {time_format(t1)} "
        f"-ar 16000 -ac 1 -codec:a libmp3lame -qscale:a 7 {escape(clip_name)} -y"
    )
    subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def text_block(csv_output, text, t0, t1, audio_idx, folder):
    clip_name = os.path.join(folder, f"{audio_idx:03d}.mp3")
    ffmpeg_command(args.audio_input, t0, t1, clip_name)
    csv_output.append([clip_name, text, time_format(t0), time_format(t1)])
    return csv_output


def should_split(start, end, t0, times):
    if end - t0 > MAX_T:
        return True
    if (len(times) > 1) and (start - times[-2] > MAX_DIFF):
        return True
    return False


def write_csv(args, subs):
    """
    Write data in .csv format
    """

    folder = os.path.join(args.output_dir, os.path.basename(args.audio_input[:-4]))
    Path(folder).mkdir(parents=True, exist_ok=True)
    csv_output = []
    audio_idx, t0, t1 = 0, 0, 0
    texts, times_start, times_end = [], [], []
    text_idx = 0
    for sub in subs:
        start, end, content = get_times_conent(sub)
        # print("---", start, end, t0, t1, content)
        if t0 == 0:
            t0 = start

        if content == "":
            if not texts:
                t0 = 0
                t1 = end
                continue

            text = " ".join(texts)
            texts = []
            times_start = []
            times_end = []
            text_idx = 0
            if text == "" or t1 < t0:
                t0 = 0
                t1 = end
                continue

            # print(text, t0, t1)
            csv_output = text_block(csv_output, text, t0, t1, audio_idx, folder)
            t0 = 0
            t1 = end
            audio_idx += 1
            continue

        texts.append(content)
        times_start.append(start)
        times_end.append(end)

        if should_split(start, end, t0, times_end):
            if t1 <= t0:
                # print("T1 < T0")
                t1 = times_end[-1]
                text_idx = len(texts) - 1

            text = " ".join(texts[:text_idx])
            texts = texts[text_idx:]
            times_start = times_start[text_idx:]
            times_end = times_end[text_idx:]
            text_idx = len(texts)
            # print(text, t0, t1)
            csv_output = text_block(csv_output, text, t0, t1, audio_idx, folder)

            # ERROR no ha de ser 0, ha de ser el temps del primer texts
            t0 = times_start[0]
            audio_idx += 1

        elif content[-1] in ".!?":
            t1 = end
            text_idx = len(texts)

    if texts:
        text = " ".join(texts)
        csv_output = text_block(csv_output, text, t0, times_end[-1], audio_idx, folder)

    df = pd.DataFrame(csv_output, columns=["audio", "sentence", "start_time", "end_time"])
    df = df[df.sentence != ""]
    df.to_csv(folder + ".csv", index=False)


if __name__ == "__main__":
    args = parse_args()
    subs = get_subs(args.srt_input)
    try:
        write_csv(args, subs)
    except srt.SRTParseError:
        print("ERROR Corrupted SRT")
