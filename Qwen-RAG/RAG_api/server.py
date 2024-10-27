from flask import Flask, request, jsonify
import torch
from llama_index.core import Settings
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import VectorStoreIndex
from llama_index.readers.web import SimpleWebPageReader
app = Flask(__name__)

# 初始化模型和索引
def init_model_and_index():
    Settings.llm = HuggingFaceLLM(
        model_name="/root/llm_cache/qwen/Qwen2___5-7B-Instruct",
        tokenizer_name="/root/llm_cache/qwen/Qwen2___5-7B-Instruct",
        context_window=30000,
        max_new_tokens=2000,
        generate_kwargs={"temperature": 0.7, "top_k": 50, "top_p": 0.95},
        device_map="auto",
    )

    Settings.embed_model = HuggingFaceEmbedding(
        model_name="/root/llm_cache/AI-ModelScope/bge-base-zh-v1___5"
    )
    Settings.transformations = [SentenceSplitter(chunk_size=1024)]
    #RAG的知识库，需要改为本地知识库
    documents = SimpleWebPageReader(html_to_text=True).load_data(
        ["https://qwen.readthedocs.io/zh-cn/latest/"]
    )

    index = VectorStoreIndex.from_documents(
        documents,
        embed_model=Settings.embed_model,
        transformations=Settings.transformations
    )
    return index

index = init_model_and_index()

# 定义 API 接口 to外部服务调用
@app.route('/query', methods=['POST'])
def query():
    data = request.json
    query_text = data.get('query')
    query_engine = index.as_query_engine()
    response = query_engine.query(query_text).response
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)