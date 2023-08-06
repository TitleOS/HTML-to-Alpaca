import openai
import os
import argparse

parser = argparse.ArgumentParser(description='Training script')
parser.add_argument('--apikey', type=str, help='Your OpenAI API Key')
parser.add_argument('--txt', type=str, help='Set Path to HTML processed text files')
parser.add_argument('--output', type=str, help='Set the output file name for the alpaca dataset.')
parser.add_argument('--num_questions', type=int, help='Set the number of questions to generate.')
args = parser.parse_args()

if args.apikey:
    api_key = args.apikey
    print(f"OpenAI API Key: {api_key}")
else:
    print("No OpenAI API Key provided, exiting.")
    exit()
if args.txt:
    text_files = args.txt
    print(f"Using text files: {text_files}")
else:
    print("No text files provided, exiting.")
    exit()
if args.output:
    OUTPUT_PATH = args.output
    print(f"Using output path: {OUTPUT_PATH}")
else:
    OUTPUT_PATH = "alpaca.json"
    print("No output path provided, defaulting to alpaca.json")
if args.num_questions:
    NUM_QUESTIONS = args.num_questions
    print(f"Number of questions to generate: {NUM_QUESTIONS}")
else:
    NUM_QUESTIONS = 10
    print("No number of questions provided, defaulting to 10")

# Initialize OpenAI API
openai.api_key = api_key

def generate_questions(text, num_questions=NUM_QUESTIONS):
    prompt = f"Based on the following text generate {num_questions} instructions with their responses:\n\n{text}\n. Please include the instruction prefix and response suffix. Do not include numbers or count. For example, Instruction: Obama as born in 1961 in Hawaii.\n When was Obama born? Response: 1961\n"
    print("Prompt: " + prompt)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048
    )
    print(response) 
    ir_pairs = response.choices[0].message.content.strip().split('\n\n')
    
    # Only keep pairs that can be split into an instruction and a response
    valid_pairs = [ir for ir in ir_pairs if len(ir.split('\n')) == 2]
    
    return [{"instruction": ir.split('\n')[0], "response": ir.split('\n')[1]} for ir in valid_pairs]

def process_text_files(directory_path):
    alpaca_data = []
    
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as text_file:
                    try:
                        text_content = text_file.read()
                        ir_pairs = generate_questions(text_content)
                        alpaca_data.extend(ir_pairs)
                    except:
                        print("Unable to process file: " + file_path)
    

                    
                    
    # Output in modified Alpaca format
    with open(OUTPUT_PATH, "w", encoding="utf-8") as outfile:
        import json
        json.dump(alpaca_data, outfile, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    process_text_files(text_files)