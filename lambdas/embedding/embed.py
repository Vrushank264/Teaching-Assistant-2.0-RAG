import argparse
from langchain.document_loaders import TextLoader
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from InstructorEmbedding import INSTRUCTOR
from langchain.embeddings import HuggingFaceInstructEmbeddings


def load_documents(root, ext = "txt"):

    loader = DirectoryLoader(root, glob = f"**/*.{ext}", loader_cls = TextLoader, show_progress = True)
    docs = loader.load()
    if (len(docs) > 0):
        print(f"Total Documents: {len(docs)}")
        return docs
    else:
        return None


def split_text(docs, chunk_size, chunk_overlap):

    text_splitter = RecursiveCharacterTextSplitter(chunk_size = chunk_size, chunk_overlap = chunk_overlap)
    text = text_splitter.split_documents(docs)
    return text


def embed_text(text, db_dir):

    instructor_embedding = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl",
                                                      model_kwargs={"device": "cuda"})
    vector_db = Chroma.from_documents(documents = text,
                                      embedding = instructor_embedding,
                                      persist_directory = db_dir)
    
    return vector_db


def get_embedding(root, chunk_size, chunk_overlap, dir):

    docs = load_documents(root)
    text = split_text(docs, chunk_size, chunk_overlap)
    vector_db = embed_text(text, dir)

    return vector_db


def parse_arguments():

    parser = argparse.ArgumentParser()
    parser.add_argument("--docs_dir", type = str, required = True)
    parser.add_argument("--out_dir", type = str, required = True)
    parser.add_argument("--chunk_size", type = int, default = 500)
    parser.add_argument("--chunk_overlap", type = int, default = 200)

    args = parser.parse_args()
    return args


def main():

    args = parse_arguments()
    vector_db = get_embedding(args.docs_dir, args.chunk_size, args.chunk_overlap, args.out_dir)
    vector_db.persist()


if __name__ == "__main__":

    main()
    