import torch
import transformers
import json
from transformers import LlamaTokenizer, LlamaForCausalLM, pipeline
from langchain.llms import HuggingFacePipeline
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceInstructEmbeddings


def load_llm(model_name):

    """
    Loads the model from HuggingFace, and creates the pipeline.

    Arguments:
        model_name: str - Name of the huggingface card, 
        Ex: "TheBloke/wizardLM-7B-HF"

    Returns:
        HuggingFacePipeline: LangChain's HuggingFacePipeline object
    """     

    tokenzier = LlamaTokenizer.from_pretrained(model_name)
    model = LlamaForCausalLM.from_pretrained(model_name,
                                             load_in_8bit = True,
                                             device_map = 'auto',
                                             torch_dtype = torch.float16,
                                             low_cpu_mem_usage = True)

    pipe = pipeline("text-generation", 
                    model = model,
                    tokenizer = tokenzier,
                    max_length = 512,
                    temperature = 0,
                    top_p = 0.95,
                    repetition_penalty = 1.15,
                    return_full_text = True)
    
    local_llm = HuggingFacePipeline(pipeline = pipe)
    return local_llm

    

def create_chain(db_dir, llm):

    """
    Creates the "Langchain" of type "RetrievalQA"
    chain_type is set to "refine" because other types aren't giving meaningful answers.

    Arguments:
        db_dir:  str - Path to the generated vector database.
        llm:     HuggingFacePipeline object

    Returns:
        qa_chain: RetrievalQA object from which we can query.
    """    

    

    embedding = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl",
                                                      model_kwargs={"device": "cuda"})
    vector_db = Chroma(embedding_function=embedding,persist_directory = db_dir)
    retriever = vector_db.as_retriever(search_kwargs = {"k": 1})
    qa_chain = RetrievalQA.from_chain_type(llm = llm, 
                                           chain_type = "refine",
                                           retriever = retriever,
                                           return_source_documents = True)
    
    return qa_chain


def process_llm_response(llm_response):
    
    """
    This function creates a JSON object from the LLM response object.

    Returns:
        JSON: JSON with two fields "answer" and "sources"
    """    

    res = {}
    res["answer"] = llm_response["result"]
    res["sources"] = []

    for source in llm_response["source_documents"]:
        res["sources"].append(source.metadata['source'])

    json_resposne = json.dumps(res, indent = 4)
    return json_resposne

# llm_model_name = "TheBloke/wizardLM-7B-HF"
# db_dir = "/content/db"

# llm = load_llm(llm_model_name)
# qa_chain = create_chain(db_dir, llm)
# query = "What is the uptime of AWS?"
# print("Querying")
# llm_response = qa_chain(query)
# print(llm_response)
# process_llm_response(llm_response)


