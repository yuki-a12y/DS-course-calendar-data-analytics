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
        self.preprocessed_calendar_for_nn = None
        self.calendar_element_dict = {}

    def main(self):
        calendar = self.ORIGINAL_CALENDAR
        calendar = self.resize_calendar_1200_900(calendar)
        calendar = self.detect_calendar_area(calendar, settings.TEMPLATE_PATH)
        calendar = PreProcessForNN(calendar)
        self.calendar_element_list = divide_calendar(calendar)

        return self.calendar_element_dict

    def visualize_intermediate_img(self):
        print('original')
        plt.imshow(self.ORIGINAL_CALENDAR)
        plt.show()
        print('----------------------')
        print('resized')
        plt.imshow(self.resize_calendar)
        plt.show()
        print('----------------------')
        print('area detected')
        plt.imshow(self.homography_transformed_calendar)
        plt.show()
        print('----------------------')
        print('processed for NN')
        plt.imshow(self.preprocessed_calendar_for_nn)
        plt.show()
        self.visualize_result_imgs

    def visualize_result_imgs(self):
        print('----------------------')
        print('year')
        plt.imshow(self.calendar_element_dict['year'])
        plt.gray()
        plt.show()
        print('----------------------')
        print('year')
        plt.imshow(self.calendar_element_dict['month'])
        plt.gray()
        plt.show()
        for element in self.calendar_element_dict['day']:
            plt.imshow(element)
            plt.gray()
            plt.show()

    def resize_calendar_1200_900(self, calendar):
        self.resized_calendar = cv2.resize(calendar, dsize=(1200, 900))
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
                        [vertices_list[2][0], vertices_list[2][1] + template],
                        [vertices_list[3][0] + template_one_edge_length, vertices_list[3][1] + template_one_edge_length]]

        return vertices_list

    def homography_transform(self, calendar, vertices_list):
        src_pts = np.array(vertices_list, dtype=np.float32)
        dst_pts = np.array([[0, 0], [calendar.shape[0], 0], [0, calendar.shape[1]], [calendar.shape[0], calendar.shape[1]]], dtype=np.float32)
        mat_i = cv2.getPerspectiveTransform(src_pts, dst_pts)
        return cv2.warpPerspective(calendar, mat_i, (1200, 900))

def divide_calendar(self):
    return None
def PreProcessForNN(self):
    return None