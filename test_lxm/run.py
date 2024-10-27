import os  
import sys  
import time  
import requests  
from multiprocessing import Process, Queue  
import json
# import pandas as pd

# 引入的包需要安装的, 请在requirements.txt里列明, 并列明版本  
# requests==2.31.0 (举例)  
  
# 配置参数：最大并行数为10，选手可根据API承载能力调整（1~10）  
MAX_PROCESS = 50
  
# =-=-=-=-==-=-=-=-==-=-=-=-==-=-=-=-==-=-=-=-==-=-=-=-==-=-=-=-==  
# 以下区域为选手编写接口调用代码部分  
# 大模型接口服务的URL  
URL = "http://36.133.8.100:11171"  # 修正了URL中的错误字符  
  
def get_completion(prompt):  
    headers = {'Content-Type': 'application/json'}  
    data = {"prompt": prompt}  
    response = requests.post(url=URL, headers=headers, data=json.dumps(data))  
    response.raise_for_status()  # 检查请求是否成功  
    return response.json().get('response', {})  # 返回可能的响应，如果没有'response'键，则返回空字典  
  
def api_request(url, data):  
    """  
    （保留原函数，用于其他可能的API调用，如果需要的话）  
    调用API接口并返回响应结果  
    Args:  
        url (str): API服务的URL  
        data (dict): 要传递给API的数据  
    Returns:  
        dict: API响应结果的字典形式  
    """  
    try:  
        response = requests.post(url, json=data)  
        response.raise_for_status()  # 检查请求是否成功  
        return response.json()  # 返回API的JSON格式响应  
    except requests.exceptions.HTTPError as errh:  
        return {"error": "HTTP Error", "message": str(errh)}  
    except requests.exceptions.ConnectionError as errc:  
        return {"error": "Error Connecting", "message": str(errc)}  
    except requests.exceptions.Timeout as errt:  
        return {"error": "Timeout Error", "message": str(errt)}  
    except requests.exceptions.RequestException as err:  
        return {"error": "Request Error", "message": str(err)}  
  
def process_text_input(text_input):  
    """  
    处理输入文本并调用API返回结果  
    Args:  
        text_input (str): 输入的文本  
    Returns:  
        dict: 输入文本及其API响应结果的字典  
    """  
    # 使用get_completion函数来获取API响应  
    api_output = get_completion(text_input)  
  
    # 返回输入输出的字典，格式不可修改  
    return {  
        "input": text_input,  
        "output": api_output  # 这里假设API返回的是可以直接使用的字典格式  
    }  
  
# 以上区域为选手编写接口调用代码部分  
# =-=-=-=-==-=-=-=-==-=-=-=-==-=-=-=-==-=-=-=-==-=-=-=-==-=-=-=-==  
  
# 以下为并行处理部分, 请选手不要修改
def return_from_queue(input_text, q):
    """
    从输入队列中获取数据并进行处理
    Args:
        input_text (str): 输入文本
        q (multiprocessing.Queue): 共享队列
    """
    output = process_text_input(input_text)
    q.put(output)

def job(inputs, q):
    """
    工作进程，处理输入数据
    Args:
        inputs (list): 输入的文本列表
        q (multiprocessing.Queue): 共享队列
    """
    for input_text in inputs:
        return_from_queue(input_text, q)
# 以上为并行处理部分, 请选手不要修改
# =-=-=-=-==-=-=-=-==-=-=-=-==-=-=-=-==-=-=-=-==-=-=-=-==-=-=-=-==

# =-=-=-=-==-=-=-=-==-=-=-=-==-=-=-=-==-=-=-=-==-=-=-=-==-=-=-=-==
# 以下为逻辑函数, 请选手按需修改, main函数的入参和最终的结果输出不可修改

def main(to_pred_dir, result_save_path):
    """
    主函数，负责读取输入文件并处理，支持多进程与单进程模式
    Args:
        to_pred_dir (str): 输入文件所在目录
        result_save_path (str): 结果保存路径
    """
    # 获取运行脚本路径和当前目录
    run_py = os.path.abspath(__file__)
    model_dir = os.path.dirname(run_py)

    # 打开输入文件，请不要修改"test.txt"字段
    text_path = os.path.join(to_pred_dir, "test.txt")
    with open(text_path, "r", encoding="utf-8") as f:
        lines = f.read().strip().split("\n")  # 读取所有行

    num = len(lines)
    # 创建队列用于进程间通信
    q = Queue()

    num_process = MAX_PROCESS

    if num_process > 1:  # 多进程模式
        # 设置每个进程处理的任务数量
        num_per_process = num // num_process + 1
        processes = []
        for i in range(0, num, num_per_process):
            # 创建进程处理数据
            p = Process(target=job, args=(lines[i:i+num_per_process], q))
            processes.append(p)
            p.start()

        # 打开结果文件并等待所有进程结果
        with open(result_save_path, "w") as fw:
            return_num = 0

            while return_num < num:
                if not q.empty():
                    output = q.get()
                    return_num += 1
                    # 按格式写入输入输出对
                    
                    fw.write("%s\t%s\n" % (output["input"], output["output"].replace("\\n", "").replace("\\t", "").replace("\\r", "").replace("\n", "").replace("\t", "").replace("\r", "")))
                    fw.flush()

                else:
                    time.sleep(1)  # 等待进程返回结果

            # 等待所有进程结束
            for p in processes:
                p.join()

    else:
        # 单进程模式
        # 选手选择单进程模式时运行以下代码
        # 若使用单进程模式，导致作答时间超时，成绩无效由选手自负
        with open(result_save_path, "w") as fw:
            for line in lines:
                output = process_text_input(line)  # 逐行处理数据
                cleaned_output = pd.DataFrame(output["output"]).to_string(index=False, header=False).replace("\n", "")
                
                cleaned_output = output["output"].replace("\\n", "").replace("\\t", "").replace("\\r", "").replace("\n", "").replace("\t", "").replace("\r", "")
                fw.write("%s\t%s\n" % (output["input"], cleaned_output))
                fw.flush()

# =-=-=-=-==-=-=-=-==-=-=-=-==-=-=-=-==-=-=-=-==-=-=-=-==-=-=-=-==
# 以下代码请勿修改, 若因此造成的提交失败由选手自负  
if __name__ == "__main__":  
    # 获取命令行参数  
    to_pred_dir = sys.argv[1]  
    result_save_path = sys.argv[2]  
    main(to_pred_dir, result_save_path)  
# 以上代码请勿修改, 若因此造成的提交失败由选手自负  
# =-=-=-=-==-=-=-=-==-=-=-=-==-=-=-=-==-=-=-=-==-=-=-=-==-=-=-=-==