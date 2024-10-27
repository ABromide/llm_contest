from fastapi import FastAPI, Request  
import uvicorn  
import json  
import datetime  
import torch  
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer

# 设置设备参数  
DEVICE = "cuda"  # 使用CUDA  
  
# 清理GPU内存函数  
def torch_gc():  
    if torch.cuda.is_available():  # 检查是否可用CUDA  
        torch.cuda.empty_cache()  # 清空CUDA缓存  
  
# 创建FastAPI应用  
app = FastAPI()  
  
# 加载预训练的分词器和模型  
model_name_or_path = '/root/llm_cache/qwen/Qwen2___5-7B-Instruct'  # 假设这是vllm兼容的模型路径  
stop_token_ids = [151329, 151336, 151338]
# 创建采样参数。temperature 控制生成文本的多样性，top_p 控制核心采样的概率
max_tokens=512
temperature=0.8
top_p=0.95
max_model_len=1024
sampling_params = SamplingParams(temperature=temperature, top_p=top_p, max_tokens=max_tokens, stop_token_ids=stop_token_ids)
# 初始化 vLLM 推理引擎
llm = LLM(model=model_name_or_path, tokenizer_mode="auto", dtype=torch.bfloat16, gpu_memory_utilization=0.7, enforce_eager=True, tensor_parallel_size=4)

# 处理POST请求的端点  
@app.post("/")  
async def create_item(request: Request): 
    global llm
    json_post_raw = await request.json()  # 获取POST请求的JSON数据  
    prompts = json_post_raw.get('prompts')  # 获取请求中的提示列表  
    print(prompts)


    responses = llm.generate(prompts, sampling_params)
    answer_text = []
    for output in responses:
        prompt = output.prompt
        generated_text = output.outputs[0].text
        answer_text.append(generated_text)
        now = datetime.datetime.now()  # 获取当前时间  
        time = now.strftime("%Y-%m-%d %H:%M:%S")  # 格式化时间为字符串  
        log = "[" + time + "] " + '", prompts:' + json.dumps(prompt,ensure_ascii=False) + '", responses:' + json.dumps(generated_text,ensure_ascii=False) + '"'  
        print(log)  # 打印日志  
    # 构建响应JSON  
    answer = {  
        "responses": answer_text,  
        "status": 200,  
        "time": time  
    }  

    # 构建日志信息  
    
    torch_gc()  # 执行GPU内存清理  
    return answer  # 返回响应  
  
# 主函数入口  
if __name__ == '__main__':  
    # 启动FastAPI应用  
    # uvicorn.run(app, host='0.0.0.0', port=8804, workers=1)  # 在指定端口和主机上启动应用
    uvicorn.run(app, host='0.0.0.0', port=8805, workers=1)  # 在指定端口和主机上启动应用