from typing_extensions import IntVar
from PIL import Image, ImageDraw
import numpy as np
import matplotlib.pyplot as plt
import os
import copy


class CreateSampleData:
    def __init__(self, label_list: list, convert_size: tuple, thresh: int, x_step: int):
        self.label_list = label_list  # 指定するラベルのリスト
        self.convert_size = convert_size  # リサイズするサイズ
        self.thresh = thresh  # 2値化のしきい値
        self.x_step = x_step  # バッチを移動する距離
        self.data_dict = {}

    def convert_img(self, input_file_path: str):
        img = Image.open(input_file_path)  # 読み込み
        img = img.resize(self.convert_size)  # リサイズ
        img = img.convert("L")                     # グレイスケールに変換
        img = img.point(lambda x: 0 if x < self.thresh else 256)   # 2値化。値がthresh以下は0になる、ほかは256
        plt.figure(figsize=(100, 25))
        plt.imshow(img)
        return img

    def generate_data_automatically(self, img) -> dict:
        self.data_dict = {label: [] for label in self.label_list}

        #輝度0の列のリストを作る
        brightness_0_list = self.create_brightness_0_list(img)

        for x_num in range(0, self.convert_size[0] - self.convert_size[1], self.x_step):
            img_crop = img.crop(
                (x_num, 0, x_num + self.convert_size[1], self.convert_size[1]))  # 切り取る

        # データラベルを書き込み
            data_label = self.generate_data_label_automatically(x_axis=x_num + self.convert_size[1] / 2, brightness_0_list=brightness_0_list)
            self.data_dict[data_label].append(img_crop)

        return self.data_dict


    def generate_data_by_manual(self, img) -> dict:
        self.data_dict = {label: [] for label in self.label_list}

        #輝度0の列のリストを作る
        brightness_0_list = self.create_brightness_0_list(img)
        auto_loop_counter = 0

        for x_num in range(0, self.convert_size[0] - self.convert_size[1], self.x_step):
            img_crop = img.crop(
                (x_num, 0, x_num + self.convert_size[1], self.convert_size[1]))  # 切り取る

            if auto_loop_counter >= 2 and auto_loop_counter <= 10:
                auto_loop_counter += 1
                data_label = self.generate_data_label_automatically(x_axis=x_num + self.convert_size[1] / 2, brightness_0_list=brightness_0_list)
            else:
                img_draw = copy.deepcopy(img_crop)
                draw = ImageDraw.Draw(img_draw)  # Drawオブジェクトの作成
                # 真ん中に線を引く
                draw.line(((self.convert_size[1] / 2, 0),
                          (self.convert_size[1] / 2, self.convert_size[1])))
                plt.imshow(img_draw)
                plt.gray()
                plt.show()

                # データラベルの入力させる
                data_label = ''
                while data_label not in self.label_list and data_label != 'a':
                    print('{}の中から選択してください'.format(self.label_list))
                    data_label = input()
                else:
                    pass
                if data_label == 'a':
                    data_label = self.generate_data_label_automatically(x_axis=x_num + self.convert_size[1] / 2, brightness_0_list=brightness_0_list)
                    auto_loop_counter = 2
                else:
                    pass
            self.data_dict[data_label].append(img_crop)

        return self.data_dict

    def create_brightness_0_list(self, img) -> list:
        img_arr = np.array(img)  #numpyに変換
        where_arr = np.where(img_arr == 0)[1]  #輝度が0の行、列の番号を抽出
        where_list = list(where_arr)  #列のみを抽出し、リストに変換
        brightness_0_list = list(set(where_list))  #重複するものを削除している、set型をリストに変換

        return brightness_0_list

    #データラベルの自動生成→輝度が0のピクセルがある列は1、ない列は0とする。
    def generate_data_label_automatically(self, x_axis: int, brightness_0_list: list) -> str:
        if x_axis in brightness_0_list:
                data_label = '1'
        else:
                data_label = '0'

        return data_label

    def save_data(self, output_path: str):
        # ラベルごとのファイルの数を数える
        # ../data/label/name.jpg→name.jpgのファイルの数を数える→辞書に格納する
        label_file_num_dict = {}
        for label in self.label_list:
            output_label_path = os.path.join(output_path, label)
            os.makedirs(output_label_path, exist_ok=True)  # エクスポートするディレクトリを作成する、既にある場合は何もしない
            label_file_num_dict[label] = sum(os.path.isfile(os.path.join(
                output_label_path, name)) for name in os.listdir(output_label_path))  # ラベルディレクトリごとのファイル数を数え、辞書に格納

            for data in self.data_dict[label]:
                label_file_num_dict[label] += 1  # ラベルのファイル数を一つ増やす
                data.save(os.path.join(output_path, label + '/' + label +
                                       '-' + str(label_file_num_dict[label]).zfill(4) + '.jpg'))  # 保存

        self.data_dict.clear()
