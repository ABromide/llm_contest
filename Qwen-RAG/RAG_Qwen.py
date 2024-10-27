import torch
from llama_index.core import Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Set prompt template for generation (optional)
from llama_index.core import PromptTemplate
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.readers.web import SimpleWebPageReader
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

def completion_to_prompt(completion):
   return f"<|im_start|>system\n<|im_end|>\n<|im_start|>user\n{completion}<|im_end|>\n<|im_start|>assistant\n"

def messages_to_prompt(messages):
    prompt = ""
    for message in messages:
        if message.role == "system":
            prompt += f"<|im_start|>system\n{message.content}<|im_end|>\n"
        elif message.role == "user":
            prompt += f"<|im_start|>user\n{message.content}<|im_end|>\n"
        elif message.role == "assistant":
            prompt += f"<|im_start|>assistant\n{message.content}<|im_end|>\n"

    if not prompt.startswith("<|im_start|>system"):
        prompt = "<|im_start|>system\n" + prompt

    prompt = prompt + "<|im_start|>assistant\n"

    return prompt

def set_RAG_model_beg():
    # Set Qwen2 as the language model and set generation config
    Settings.llm = HuggingFaceLLM(
        model_name="/root/llm_cache/qwen/Qwen2___5-7B-Instruct",
        tokenizer_name="/root/llm_cache/qwen/Qwen2___5-7B-Instruct",
        #model_name="Qwen/Qwen2-7B-Instruct",
        #tokenizer_name="Qwen/Qwen2-7B-Instruct",
        context_window=30000,
        max_new_tokens=2000,
        generate_kwargs={"temperature": 0.7, "top_k": 50, "top_p": 0.95},
        messages_to_prompt=messages_to_prompt,
        completion_to_prompt=completion_to_prompt,
        device_map="auto",
    )

    # Set embedding model
    Settings.embed_model = HuggingFaceEmbedding(
        model_name = "/root/llm_cache/AI-ModelScope/bge-base-zh-v1___5"
    )
    # Set the size of the text chunk for retrieval
    Settings.transformations = [SentenceSplitter(chunk_size=1024)]


    # documents = SimpleDirectoryReader("./document").load_data()
    # index = VectorStoreIndex.from_documents(
    #     documents,
    #     embed_model=Settings.embed_model,
    #     transformations=Settings.transformations
    # )

    documents = SimpleWebPageReader(html_to_text=True).load_data(
        ["https://qwen.readthedocs.io/zh-cn/latest/"]
    )
    index = VectorStoreIndex.from_documents(
        documents,
        embed_model=Settings.embed_model,
        transformations=Settings.transformations
    )

    query_engine = index.as_query_engine()
    your_query = "什么是蚂蚁森林？"
    print(query_engine.query(your_query).response)


set_RAG_model_beg()