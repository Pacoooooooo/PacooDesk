from PIL import ImageGrab
import requests
import os
import re
import json
import base64
import pyperclip
from playsound import playsound


class ImageProcessor:
    def __init__(self):
        pass

    def upload_img(self, img_name):
        '''
        将图片转换成链接
        :param img_name:
        :return:
        '''
        is_upload = False
        try:
            image_data = open(img_name, "rb").read()
        except:
            is_upload = False
            img_url = ""
        else:
            is_upload = True
            img_url = "data:image/jpg;base64," + base64.b64encode(image_data).decode()
        return is_upload, img_url

    def save_image_from_cut(self, img_name):
        is_saved = False
        try:
            im = ImageGrab.grabclipboard()
            im.save(img_name, 'PNG')
        except:
            is_saved = False
        else:
            is_saved = True
        return is_saved

class OcrProcessor:
    def __init__(self):
        pass

    def play_sound(self, str):
        try:
            if str == "success":
                playsound('PacooData/asserts/success.mp3')
            if str == "welcome":
                playsound('PacooData/asserts/welcome_pacoo.mp3')
            if str == "failed":
                playsound('PacooData/asserts/failed.mp3')
        except:
            pass


    def push_results_to_clipboard(self, string):
        string = str(string)
        pyperclip.copy(string)

    def ocr_by_post(self, settings, data):
        try:
            uid = re.findall(r".*=(.*)&", settings['link'])
            ukey = re.findall(r".*=(.*)", settings['link'])
            image = data.split(",")[1]
            url = 'http://123.56.90.52:8016/webocr'
            d = {'uid': uid[0], 'ukey': ukey[0],
                 'image': image}
            r = requests.post(url, data=d)
            ocr_results = json.loads(r.text)
            ocr_results['latex_stl'] = "$$\n" + ocr_results['latex_stl'] + "\n$$"
            return ocr_results['err_msg']=="OK", ocr_results
        except:
            return False, {'err_msg': "error"}

    def latex(self, settings, args, timeout=6):
        env = os.environ
        headers = {
            'app_id': env.get('APP_ID', settings['account']),
            'app_key': env.get('APP_KEY', settings['passwd']),
            'Content-type': 'application/json'
        }
        service = ''
        r = requests.post(service, data=json.dumps(args), headers=headers, timeout=timeout)
        return json.loads(r.text)

    def request_ocr(self, settings, img_url):
        is_rcged = False
        ocrRespond = {}
        ocrRespond['left_times'] = "000"
        try:
            mathpixRespond = self.latex(settings, {
                'src': img_url,
                'formats': ['mathml', "latex_styled"]
            })
            # print(mathpixRespond)
            mathmlstr = mathpixRespond['mathml'][0:5] + \
                        ' xmlns="http://www.w3.org/1998/Math/MathML" display="block"' + \
                        mathpixRespond['mathml'][5:]
        except:
            is_rcged = False
            ocrRespond['err_msg'] = 'error'
        else:
            is_rcged = True
            ocrRespond['err_msg'] = 'success'
            ocrRespond['latex_stl'] = "$$\n"+mathpixRespond['latex_styled']+"\n$$"
            ocrRespond['mathml_wd'] = mathmlstr
        return is_rcged, ocrRespond

if __name__ == '__main__':
    pass
