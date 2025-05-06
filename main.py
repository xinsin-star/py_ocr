import logging
import time

import easyocr
from flask import Flask, request, redirect, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

# 配置日志记录到文件
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='ocr.log'  # 指定日志文件的名称
)
app = Flask(__name__)
# 设置代理服务器的数量
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)
# 允许上传的文件类型
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ocr', methods=['POST'])
def upload_file():
    ip = request.remote_addr
    # 检查是否有文件上传
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    # 如果用户没有选择文件，浏览器也会提交一个空的文件
    if file.filename == '':
        return redirect(request.url)
    # 检查文件类型是否允许
    if file and allowed_file(file.filename):
        ocr_res = ocr(file.read())
        print_log(ocr_res, ip)
        return {
            'code': 200,
            'data': ocr_res
        }
    else:
        res_data = '不允许的文件类型!'
        print_log(f'{res_data}-文件名: {file.filename}', ip)
        return {
            'code': 500,
            'data': res_data
        }


def print_log(message, ip):
    logging.info(f'{message}-客户端IP: {ip}')


def ocr(file):
    result = reader.readtext(file, detail=0, paragraph=True)
    return result


if __name__ == '__main__':
    # reader = easyocr.Reader(['ch_sim', 'en'], model_storage_directory='./model',
    #                         user_network_directory='./user_network')  # this needs to run only once to load the model into memory
    app.run(host='0.0.0.0', port=5001)
