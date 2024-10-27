from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "/root/llm_cache/qwen/Qwen2___5-7B-Instruct"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

prompts = ["Give me a short introduction to large language model.",'hi']
messages = [{"role": "system", "content": "You are a helpful assistant."}] + \
               [{"role": "user", "content": prompt} for prompt in prompts]
print(messages)
input_ids = tokenizer(messages, padding=True, truncation=True, return_tensors="pt").input_ids

# 调用模型进行批量对话生成
model_inputs = input_ids.to('cuda')
generated_ids = model.generate(model_inputs, max_new_tokens=512)

# 解码生成的ID并构建响应
responses = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)

print(responses)