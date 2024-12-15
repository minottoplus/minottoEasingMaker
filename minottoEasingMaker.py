import numpy as np
import matplotlib.pyplot as plt
import PySimpleGUI as sg
import os
from datetime import timedelta
import json
from pathlib import Path
import convertSec as cs
import copy
import zipfile





def get_user_documents_folder():
    """
        ユーザーのダウンロードフォルダを取得するための関数
    Returns:
        str: フォルダパス
    """

    folder= "C:/"
    
    return folder







try:
    ymmtDir = os.path.join(get_user_documents_folder(), "MinottoEasingYMMT")
    os.mkdir(ymmtDir)
except FileExistsError:
    print("")





sg.theme("Default1")

text_box_size_long = (50, 1)
button_size = (10, 1)

layout = [
    [sg.Text("動画ファイル:", size=(10,1)),
        sg.Input(size=text_box_size_long, key="-FILE-", enable_events=True),
        sg.FileBrowse(size=button_size, key="-BROWSE-", file_types=(("動画ファイル", "*.mp4;*.avi;*.mov;*.mkv"),))],
    [sg.Text("名前:", size=(10,1)), sg.Input(size=text_box_size_long, key="-NAME-")],
    [sg.Text("最初の値:", size=(10,1)), sg.Input(size=text_box_size_long, key="-START-")],
    [sg.Text("最後の値:", size=(10,1)), sg.Input(size=text_box_size_long, key="-END-")],
    [sg.Text("フレーム数:", size=(10,1)), sg.Input(size=text_box_size_long, key="-FRAMES-")],
    [sg.Button("OK"), sg.Button("キャンセル")]
]


"""メイン関数。UIの表示とイベント処理を行います。"""
window = sg.Window("動画情報入力", layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == "キャンセル":
        break
    elif event == "OK":
        videoPath = os.path.normpath(values["-FILE-"])
        templateName = values["-NAME-"]
        startValue = values["-START-"]
        endValue = values["-END-"]
        frame = int(values["-FRAMES-"])
        break
    elif event == "-BROWSE-":
        # ファイルが選択されたらテキストボックスに表示
        if values["-FILE-"]:
            window["-FILE-"].update(values["-FILE-"])

window.close()








startSec = cs.hhmmss_to_seconds(startValue)
endSec = cs.hhmmss_to_seconds(endValue)



# OutExpo イージング関数
def out_expo(t, b, c, d):
    """
    OutExpoイージング関数
    t: 現在の時間（進行状況）
    b: 開始値
    c: 変化量
    d: 総時間
    """
    if t == d:
        return b + c
    return c * (-2 ** (-10 * t / d) + 1) + b

# 変数の設定
b = startSec  # 開始値
c = endSec  # 変化量
d = frame  # 繰り返し回数（30回）
times = np.arange(0, d)  # 0から29までの整数（進行状況）

# StartTimeの値をOutExpoで計算
StartTime_values = []
for t in times:
    value_hhmmss = out_expo(t, b, c, d)
    value = cs.seconds_to_hhmmss(value_hhmmss)
    StartTime_values.append(value)



# 出力の確認
print(StartTime_values)







def parse_catalog(catalog_path):
    """
    JSONファイルを読み込み、指定された値を抽出して変数に格納し、
    変更したJSONデータを戻り値として返します。

    Args:
        catalog_path (str): JSONファイルのパス。
    
    Returns:
        dict: 変更後のJSONデータ。
        None: エラー発生時
    """
    global templateFilePath, templateName, videoPath

    try:
        with open(catalog_path, 'r', encoding='utf-8') as f:
            data = json.load(f)


        #JSONの値を変更
        if data:
             data["FilePath"] = templateFilePath
             data["ItemTemplates"][0]["Name"] = templateName
             data["ItemTemplates"][0]["Path"] = templateName

        return data

    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません: {catalog_path}")
        return None
       
    except json.JSONDecodeError:
        print(f"エラー: JSONファイルの解析に失敗しました: {catalog_path}")
        return None
       
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
        return None



templateFileName = templateName + ".ymmt"
templateFilePath = os.path.join(ymmtDir, templateFileName)


parent = Path(__file__).resolve().parent
catalogDir = parent.joinpath("catalog.json")
print(parse_catalog(catalogDir))
editedJSON = parse_catalog(catalogDir)



items = editedJSON["ItemTemplates"][0]["Items"]

original_item = items[0]

i = 0
for startTime_Value in StartTime_values:
    i += 1
    copied_item = copy.deepcopy(original_item)
    copied_item["FilePath"] = videoPath
    copied_item["ContentOffset"] = startTime_Value
    copied_item["Frame"] = i
    items.append(copied_item)

del items[0]

print()
print()
print()


print(items)


editedJSON.update(Items = items)
print()
print()
print()
print (editedJSON)

dir = os.path.join(ymmtDir, "catalog.json")
with open(dir, mode="wt", encoding="utf-8") as f:
	json.dump(editedJSON, f, ensure_ascii=False, indent=2)


print (dir)

# 圧縮したいファイルのパス
input_file = os.path.join(ymmtDir, "catalog.json")

# 出力先のファイルパス（.ymmt拡張子）
output_file = templateFilePath

with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.write(input_file, os.path.basename(input_file))
print(f"ファイルが {output_file} に保存されました。")
os.remove(input_file) # 作成したサンプルファイルを削除