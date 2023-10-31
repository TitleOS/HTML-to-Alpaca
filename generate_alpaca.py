import openai
import os
import argparse

parser = argparse.ArgumentParser(description='Training script')
parser.add_argument('--apikey', type=str, help='Your OpenAI API Key')
parser.add_argument('--txt', type=str, help='Set Path to HTML processed text files')
parser.add_argument('--output', type=str, help='Set the output file name for the alpaca dataset.')
parser.add_argument('--num_questions', type=int, help='Set the number of questions to generate.')
parser.add_argument('--eval', action='store_true', help='Set to split the dataset into train and test sets.')
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
if args.eval:
    EVAL = True
    print(f"Splitting dataset into train and test sets.")
else:
    EVAL = False
    print("Not splitting dataset into train and test sets.")

# Initialize OpenAI API
openai.api_key = api_key

def generate_questions(text, num_questions=NUM_QUESTIONS):
    prompt = f"Based on the following text generate {num_questions} instructions with their responses:\n\n{text}\n. Please include the instruction prefix and response suffix. Do not include numbers or count. Ignore irrelevant content from the text, and instead focus on providing high quality, dense, yet concise questions and responses that summarize the majority of the text. For example, Instruction: Former President Barack Obama as born in 1961 in Hawaii.\n When was Obama born? Response: 1961\n"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048
    )
    ir_pairs = response.choices[0].message.content.strip().split('\n\n')
    
    # Only keep pairs that can be split into an instruction and a response
    valid_pairs = [ir for ir in ir_pairs if len(ir.split('\n')) == 2]
    print([{"instruction": ir.split('\n')[0], "response": ir.split('\n')[1]} for ir in valid_pairs]) 
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
    import json
    if(EVAL):
        alpaca_eval = alpaca_data[:len(alpaca_data)//2]
        alpaca_train = alpaca_data[len(alpaca_data)//2:]

        alpaca_eval_output = OUTPUT_PATH.split(".")[0] + "_eval.json"
        alpaca_train_output = OUTPUT_PATH.split(".")[0] + "_train.json"


        with open(alpaca_eval_output, "w", encoding="utf-8") as outfile:
            json.dump(alpaca_eval, outfile, ensure_ascii=False, indent=4)
            print("Wrote " + str(len(alpaca_eval)) + " pairs to " + alpaca_eval_output)

        with open(alpaca_train_output, "w", encoding="utf-8") as outfile:
            json.dump(alpaca_train, outfile, ensure_ascii=False, indent=4)
            print("Wrote " + str(len(alpaca_train)) + " pairs to " + alpaca_train_output)

    else:
        with open(alpaca_data, "w", encoding="utf-8") as outfile:
            json.dump(alpaca_data, outfile, ensure_ascii=False, indent=4)
            print("Wrote " + str(len(alpaca_data)) + " pairs to " + alpaca_data)

        

    with open(OUTPUT_PATH, "w", encoding="utf-8") as outfile:
        import json
        json.dump(alpaca_data, outfile, ensure_ascii=False, indent=4)
        print("Wrote " + str(len(alpaca_data)) + " pairs to " + OUTPUT_PATH)

if __name__ == "__main__":
    process_text_files(text_files)