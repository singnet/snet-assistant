# Project QnA_Agent README

## Setting up OpenAI API Key

To get started, you'll need to set up your OpenAI API key. This key is essential for interacting with OpenAI's powerful language models.

### Step 1: Create a .env file

In order to keep your API key secure and separate from your code, we'll use a `.env` file. This file is used to store environment variables, including sensitive information like API keys.

1. Create a new file named `.env` in the root directory of your project.

### Step 2: Add your OpenAI API key

Open the `.env` file in a text editor and add the following line:

OPENAI_API_KEY="your_api_key_here"

Replace "your_api_key_here" with your actual OpenAI API key. Make sure not to include any extra spaces or characters.

### Step 3: Save the file
Save the .env file.

# Running the qna_Agent
To run the QnA Agent, execute the following command in your terminal:
`python3 ./prototyping/qna_Agent/main.py --question "how To get the metamask plugin install?"`

## Download, Generate Summary, Embed the Dataset, and ask Question 
To perform these operations, use the following command:
`python3 ./prototyping/qna_Agent/main.py --question "how To get the metamask plugin install?" --dataset --url "https://github.com/singnet/dev-portal/archive/refs/heads/master.zip"`

# Running Individual Modules
### If there is no dataset, follow this sequence:

    1.Run example_usage_dataprocess.py.
    2.Then, run example_usage_summary.py.
    3.Next, run example_usage_embed.py.
    4.Finally, run example_usage_QnA.py.

### If there is dataset:
run example_usage_QnA.py. 
<<<<<<< HEAD
    
=======
>>>>>>> 30817ba1ebcaa1308260dd294cb50bfe04592274
