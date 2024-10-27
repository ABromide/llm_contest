from modelscope import snapshot_download

# model_dir = snapshot_download('qwen/Qwen2.5-7B-Instruct', cache_dir='/root/llm_cache', revision='master')
model_dir = snapshot_download('qwen/Qwen2.5-72B-Instruct', cache_dir='/home/vipuser/my mount', revision='master')
# model_dir = snapshot_download('AI-ModelScope/bge-base-zh-v1.5', cache_dir='/root/llm_cache', revision='master')

# from transformers import AutoModelForCausalLM, AutoTokenizer
# model_name = 'Qwen/Qwen2.5-72B-Instruct'

# model = AutoModelForCausalLM.from_pretrained(model_name)
# tokenizer = AutoTokenizer.from_pretrained(model_name)

# model_name = "Qwen/Qwen2.5-7B-Instruct"
# model = AutoModelForCausalLM.from_pretrained(model_name)
# tokenizer = AutoTokenizer.from_pretrained(model_name)
