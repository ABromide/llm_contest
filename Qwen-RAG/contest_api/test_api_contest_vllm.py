import os  
import sys  
import time  
import requests  
from multiprocessing import Process, Queue  
import json

# 引入的包需要安装的, 请在requirements.txt里列明, 并列明版本  
# requests==2.31.0 (举例)  

# 配置参数：最大并行数为10，选手可根据API承载能力调整（1~10）  
MAX_PROCESS = 10  

# 大模型接口服务的URL  
URL = "http://0.0.0.0:8805"  


def get_completion(prompts):  
    headers = {'Content-Type': 'application/json'}   
    data = {"prompts": prompts}
    response = requests.post(url=URL, headers=headers, data=json.dumps(data))  
    response.raise_for_status()  # 检查请求是否成功  
    return response.json().get('responses', [])  # 返回可能的响应，如果没有'response'键，则返回空列表  
  
  
def process_text_input(text_inputs):  
    """  
    处理输入文本列表并调用API返回结果  
    Args:  
        text_inputs (list): 输入的文本列表  
    Returns:  
        list: 输入文本及其API响应结果的字典列表  
    """  
    # 使用get_completion函数来获取API响应  
    api_outputs = get_completion(text_inputs)  
    # 返回输入输出的字典列表，格式不可修改  
    return [{"input": text, "output": output} for text, output in zip(text_inputs, api_outputs)]  
  

def job(inputs, q):
    """
    工作进程，处理输入数据
    Args:
        inputs (list): 输入的文本列表
        q (multiprocessing.Queue): 共享队列
    """
    
    outputs = process_text_input(inputs)
    for item in outputs:
        print(item)
        q.put(item)


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
                    item = q.get()
                    return_num += 1
                    # 按格式写入输入输出对
                    fw.write("%s\t%s\n" % (item["input"], json.dumps(item["output"],ensure_ascii=False).replace("\\n", "").replace("\\t", "").replace("\\r", "").replace("\n", "").replace("\t", "").replace("\r", "")))
                    
                    fw.flush()
                else:
                    time.sleep(1)  # 等待进程返回结果
            # 等待所有进程结束
            for p in processes:
                p.join()

    else:
        # 单进程模式
        with open(result_save_path, "w") as fw:
            outputs = process_text_input(lines)
            for item in outputs:
                fw.write("%s\t%s\n" % (item["input"], json.dumps(item["output"]).replace("\\n", "").replace("\\t", "").replace("\\r", "").replace("\n", "").replace("\t", "").replace("\r", "")))
                fw.flush()

if __name__ == "__main__":  
    # 获取命令行参数  
    to_pred_dir = sys.argv[1]  
    result_save_path = sys.argv[2]  
    st = time.time()
    main(to_pred_dir, result_save_path)
    print('200promt耗时')
    print(time.time()-st)