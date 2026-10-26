"""Master a Remotion render for delivery: two-pass EBU R128 loudness to YouTube's -14 LUFS with
peaks under -1.5 dBTP, and a broadly compatible H.264 (yuv420p, TV range, faststart).

  python3 tools/master.py out/v1_cold_open_pilot.mp4 out/v1_cold_open_pilot_master.mp4
"""
import json, re, subprocess, sys

try:
    import imageio_ffmpeg
    FF = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    FF = "ffmpeg"

src, dst = sys.argv[1], sys.argv[2]
target = "I=-14:TP=-1.5:LRA=11"
p = subprocess.run([FF, "-hide_banner", "-i", src, "-af", f"loudnorm={target}:print_format=json", "-f", "null", "-"],
                   capture_output=True, text=True)
m = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", p.stderr).group(0))
af = (f"loudnorm={target}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
      f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,"
      # linear loudnorm can't always hold the peak target on its own; a gentle limiter guarantees it
      "alimiter=limit=-1.5dB:level=false,aresample=48000")
subprocess.run([FF, "-hide_banner", "-y", "-i", src, "-af", af,
                "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
                "-vf", "scale=in_range=full:out_range=tv", "-color_range", "tv", "-movflags", "+faststart",
                "-c:a", "aac", "-b:a", "192k", dst], check=True, capture_output=True)
print(f"mastered {dst}  (input {m['input_i']} LUFS, {m['input_tp']} dBTP)")
