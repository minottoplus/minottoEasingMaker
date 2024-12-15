from datetime import timedelta

def seconds_to_hhmmss(seconds):
    # timedeltaオブジェクトに変換
    time_obj = timedelta(seconds=seconds)
    # フォーマットで文字列に変換
    time_str = str(time_obj)
    # 時間部分が "0:" の場合に "00:" に置換
    if time_str.startswith("0:"):
        time_str = "00:" + time_str[2:]
    return time_str

def hhmmss_to_seconds(time_str):
    # HH:MM:SS.ffffffを分解
    hours, minutes, seconds = map(float, time_str.split(":"))
    # 秒数を計算
    total_seconds = hours * 3600 + minutes * 60 + seconds
    return total_seconds

