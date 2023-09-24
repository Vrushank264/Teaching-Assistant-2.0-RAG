# cloud-project

- Steps:

    Data Processing (if mp3):

        1. Get transcripts (AWS Transcribe directly gives .srt files.)
        2. Convert those srt files into chunks of 5 minutes using `process_srt.py`.
    
    VectorDB Generation:

        1. run `embedding/embed.py`
    
    Inference:

        1. Run `infer.py`


- TODOs:

1. Add S3 output bucket names in lambda/mp3.py
2. Create a similar lambda to convert srt files into 5 minute chunks.

