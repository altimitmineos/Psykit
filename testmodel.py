from llama_cpp import Llama

model = Llama(model_path="model/unsloth.Q4_K_M.gguf")
print(model)