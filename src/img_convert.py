# 必要なライブラリをインポート
import os  # ディレクトリ操作
import glob
from posixpath import basename  # ファイルパスを取得
from PIL import Image  # 画像操作


class ImgConvert:
    '''
    to_jpg_quality(default:50):jpgに変換するときの質
    resize(default:True):リサイズする
    convert_size(default:(256, 64)):リサイズしたあとの画像の大きさ
    exist_ok:デフォルトTrue。Trueなら、すでにoutput_pathが存在していなければ作成、存在していれば何もしない

    png_to_jpg_resize→png→jpgに変換＋リサイズ
    resize_jpg→jpgのりサイズ
    '''

    def __init__(self, to_jpg_quality=50, resize=True, convert_size=(256, 64), exist_ok=True):
        self.to_jpeg_quality = to_jpg_quality
        self.resize = resize
        self.convert_size = convert_size
        self.exist_ok = exist_ok

    def png_to_jpg_resize(self, input_path, output_path):  # ディレクトリまるごと変換
        '''
        png→jpgに変換＋リサイズ
        input_path:オリジナルの画像のあるディレクトリ
        output_path:保存するディレクトリ
        '''
        os.makedirs(output_path, exist_ok=self.exist_ok)  # エクスポートするディレクトリを作成する、既にある場合は何もしない
        file_path_list = glob.glob(input_path + '/*.png')  # ファイルパスリストの取得
        for file_path in file_path_list:
            img = Image.open(file_path)
            img = img.convert('RGB')  # RGBA(png)→RGB(jpg)へ変換
            if self.resize:
                img = img.resize(self.convert_size)
            basename = os.path.basename(file_path)
            save_file_path = os.path.join(output_path, basename[:-4] + '.jpg')
            img.save(save_file_path, "JPEG", quality=self.to_jpeg_quality)
            print(file_path, '->', save_file_path)

    def resize_jpg(self, input_path, output_path):
        '''
        jpgのりサイズ
        input_path:オリジナルの画像のあるディレクトリ
        output_path:保存するディレクトリ
        '''
        os.makedirs(output_path, exist_ok=self.exist_ok)  # エクスポートするディレクトリを作成する、既にある場合は何もしない
        file_path_list = glob.glob(input_path + '/*.jpg')
        for file_path in file_path_list:
            img = Image.open(file_path)
            img_resize = img.resize(self.convert_size)
            basename = os.path.basename(file_path)
            save_file_path = os.path.join(output_path, basename[:-4] + '.jpg')
            img_resize.save(save_file_path)
            print(file_path, '->', save_file_path)
