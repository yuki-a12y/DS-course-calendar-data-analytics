from typing import Any
import numpy as np
import matplotlib.pyplot as plt
import cv2
import settings

class Preprocessing:
    def __init__(self, original_calendar: str):
        self.ORIGINAL_CALENDAR = original_calendar
        self.resized_calendar = None
        self.homography_transformed_calendar = None
        self.threshold_calendar = None
        self.calendar_element_dict = {}

    def main(self):
        calendar = self.ORIGINAL_CALENDAR
        calendar = self.resize_calendar_1197_900(calendar)
        calendar = self.detect_calendar_area(calendar, settings.TEMPLATE_PATH)
        calendar = self.bgr_to_gray(calendar)
        calendar = self.adaptive_threshold(calendar)
        self.divide_calendar(calendar)
        self.divide_per_character()

        return self.calendar_element_dict

    def resize_calendar_1197_900(self, calendar):
        self.resized_calendar = cv2.resize(calendar, dsize=(1197, 900))
        return self.resized_calendar

    def detect_calendar_area(self, calendar, template_path):
        vertices_list = self.template_match(calendar=calendar, template_path=template_path)
        self.homography_transformed_calendar = self.homography_transform(calendar=calendar, vertices_list=vertices_list)
        return self.homography_transformed_calendar

    def template_match(self, calendar, template_path):
        template = cv2.imread(template_path)
        template_one_edge_length = template.shape[0]  #一辺の長さ
        vertices_list = []  #頂点の座標リスト
        i = 0
        for i in range(4):
            #カレンダー画像を４分割　0→左上　1→右上　2→左下　3右下
            if i == 0 or i == 1:
                a = 0
            else:
                a = 1
            if i == 0 or i == 2:
                b = 0
            else:
                b = 1

            #切り取る範囲
            top = int((calendar.shape[0] / 2) * a)
            bottom = int((calendar.shape[0] / 2) * (a + 1))
            left = int((calendar.shape[1] / 2) * b)
            right = int((calendar.shape[1] / 2) * (b + 1))

            #切り取り→テンプレートマッチング
            calendar_crop = calendar[top: bottom, left: right]
            result = cv2.matchTemplate(calendar_crop, template, cv2.TM_CCOEFF_NORMED)
            # 最も類似度が高い位置を取得する。
            minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(result)

            #もとのカレンダーでのx,y座標
            tl_x = maxLoc[0] + left  #左上のx座標
            tl_y = maxLoc[1] + top  #左上のy座標
            #リストに追加
            vertices_list.append([tl_x, tl_y])

        #座標はテンプレートの左上の位置になっているので、カレンダー画像の1番外側の座標にする
        vertices_list = [vertices_list[0],
                        [vertices_list[1][0] +template_one_edge_length, vertices_list[1][1]],
                        [vertices_list[2][0], vertices_list[2][1] + template_one_edge_length],
                        [vertices_list[3][0] + template_one_edge_length, vertices_list[3][1] + template_one_edge_length]]

        return vertices_list

    def homography_transform(self, calendar, vertices_list):
        src_pts = np.array(vertices_list, dtype=np.float32)
        dst_pts = np.array([[0, 0], [calendar.shape[1], 0], [0, calendar.shape[0]], [calendar.shape[1], calendar.shape[0]]], dtype=np.float32)
        mat_i = cv2.getPerspectiveTransform(src_pts, dst_pts)
        return cv2.warpPerspective(calendar, mat_i, (1200, 900))

    def bgr_to_gray(self, calendar):
        calendar = cv2.cvtColor(calendar, cv2.COLOR_BGR2GRAY)
        return calendar

    def threshold(self, calendar):
        th, self.threshold_calendar = cv2.threshold(calendar, 128, 255, cv2.THRESH_OTSU)
        return self.threshold_calendar

    def adaptive_threshold(self, calendar):
        self.threshold_calendar = cv2.adaptiveThreshold(calendar, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 101, 20)
        return self.threshold_calendar

    def divide_calendar(self, calendar) -> dict:
        '''
        (900, 1197)専用
        '''
        self.calendar_element_dict['year'] = calendar[50:90, 0:90]
        self.calendar_element_dict['month'] = calendar[35:95, 570:630]
        for i in range(5):
            for j in range(7):
                day = calendar[185 + 137 * i:228 + 137 * i, 2 + 171 * j:163 + 171 * j]
                self.calendar_element_dict[j + 1 + 7 * i] = day

        return self.calendar_element_dict

    def divide_per_character(self):
        for day_num in range(35):
            day_array = cv2.resize(self.calendar_element_dict[day_num + 1], (112, 28))  #リサイズ
            brightness_0_list = self.create_brightness_0_list(day_array)  #輝度0のピクセルがある行の番号を抽出
            #分割に必要な文字の左端と右端の座標を求める→リストに格納する
            #この方法なら1pxの領域は文字領域と判定されない
            is_brightness_0_in_column = False
            consecutive_column_first_list = []
            consecutive_column_last_list = []
            for i, b in enumerate(brightness_0_list):
                if i != len(brightness_0_list) - 1:
                    if b == brightness_0_list[i + 1] - 1:
                        if is_brightness_0_in_column == False:
                            consecutive_column_first_list.append(b)
                            is_brightness_0_in_column = True
                    else:
                        if is_brightness_0_in_column == True:
                            consecutive_column_last_list.append(b)
                            is_brightness_0_in_column = False
                else:
                    if b == brightness_0_list[i - 1] + 1:
                        consecutive_column_last_list.append(b)
            #5文字以上になることはないので、5文字以上のときは、文字領域の小さいものを削除する→ノイズ除去
            '''
            if len(consecutive_column_first_list) >= 5:
                len_consecutive_columns_list = []
                for i in range(len(consecutive_column_first_list)):
                    len_consecutive_columns_list.append(consecutive_column_last_list[i] - consecutive_column_first_list[i])
                len_consecutive_columns_list.sort(reverse=True)
                len_consecutive_columns_list = len_consecutive_columns_list[4]
            '''
            #日にちごとの画像を1文字ずつに分割し、day_characters_listに追加、また28*28になるように255パディング
            day_characters_list = []
            for c in range(len(consecutive_column_first_list)):
                one_of_day_characters = day_array[:, consecutive_column_first_list[c]: consecutive_column_last_list[c] + 1]
                x_length = one_of_day_characters.shape[1]  #横の長さ
                #横の長さが28以下の場合は255パディング
                if x_length < 28:
                    #横の長さが偶数の場合
                    if x_length % 2 == 0:
                        one_of_day_characters = np.pad(one_of_day_characters, [(0, 0), (int((28 - x_length) / 2), int((28 - x_length) / 2))], 'maximum')
                        day_characters_list.append(one_of_day_characters)
                    #横の長さが奇数の場合
                    else:
                        one_of_day_characters = np.pad(one_of_day_characters, [(0, 0), (int((28 - x_length) // 2 + 1), int((28 - x_length) // 2))], 'maximum')
                        day_characters_list.append(one_of_day_characters)
                #横の長さが28以上42以下のときは、(28, 28)にリサイズ
                elif x_length > 28 and x_length < 42:
                    one_of_day_characters = cv2.resize(one_of_day_characters, (28, 28))
                    day_characters_list.append(one_of_day_characters)
                #横の長さが28のときは、そのままリストに追加
                elif x_length == 28:
                    day_characters_list.append(one_of_day_characters)
                #横の長さが42以上は異常なので追加しない
                elif x_length >= 42:
                    pass

            #day_characters_listをself.calendar_element_dictに代入
            self.calendar_element_dict[day_num] = day_characters_list

        return self.calendar_element_dict

    def create_brightness_0_list(self, day_array) -> list:
        where_arr = np.where(day_array == 0)[1]  #輝度が0の行、列の番号を抽出
        where_list = list(where_arr)  #列のみを抽出し、リストに変換
        brightness_0_list = list(set(where_list))  #重複するものを削除している、set型をリストに変換

        return brightness_0_list