from langchain_text_splitters import RecursiveCharacterTextSplitter

with open("data/aws_s3.txt","r") as f:
    text=f.read()

print(f"original document length is : {len(text)} characters")
#RecursiveCharacterTextSplitter recursive splitter, splits based on the chunk size and chunk overlap it tries to split on paragraph breaks first, then sentences, then words
#chunk overlap is to have a buffer btwn the chunks so that there is awkward split btwn the sentences,so information near boundaries doesn't get isolated awkwardly in just one chunk.
splitter = RecursiveCharacterTextSplitter(
    chunk_size = 500, # roughly max characters per chunk
    chunk_overlap=50 # small overlap between chunks
)

chunks=splitter.split_text(text)

print(f"NUmber of chunks created: {len(chunks)} chunks")
for index, chunk in enumerate(chunks):
    print(f" chunk {index} {len(chunk)} characters")
    print(chunk)
    print()