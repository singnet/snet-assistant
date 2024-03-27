# SingularityNet AI platform and marketplace assistant
This is a prototype of the SingularityNet platform assistant. The assistant aims to help users answer questions about services on the SNET platform and other inquiries related to the platform. To try the assistant, you can use the Telegram bot "SingularityNet Platform Assistant" or run a Python file named [runner.py](prototyping/metta_llm/metta_guidance/runner.pymetta_guidance).  This assistant utilizes LLM (Large Language Model) to respond to user queries, here [metta-moto](https://github.com/zarqa-ai/metta-motto) library is used to make calls to LLM. 

## Data

In the prompt for LLM, we provide the following data:

-   General information about the platform.
-   A brief description of the services published on the SNET platform.
-   Detailed information about a specific service (in cases where the question pertains to a particular service).

For each service, we request a description from the [api](https://marketplace-mt-v2.singularitynet.io/contract-api/service) and write the received data into a separate JSON file, stored in the in `snet-assistant/json` folder.
Detailed information about services is loaded from `Readme.md` files located in the GitHub repository of the corresponding service (if the repository exists). We store this information in the `snet-assistant/prototyping/data/services_docs` folder, with a separate file for each service.
General information about the platform is loaded from the [dev-portal](https://github.com/singnet/dev-portal.git ) and stored in `snet-assistant/prototyping/data/dev_portal_md_docs` folder.
We use a retrieval-agent from [metta-moto](https://github.com/zarqa-ai/metta-motto) to select the most relevant information from `snet-assistant/prototyping/data/services_docs` or `snet-assistant/prototyping/data/dev_portal_md_docs` to answer the user's question. If a question is about a specific service, we extract the name of the service from the context and pass the corresponding document name to the retrieval-agent.

## Agents
Currently, there are two ways to run the SNET assistant: by processing one of the `metta` scripts:  [chat_process.msa](prototyping/metta_llm/metta_guidance/chat_process.msa) or [chat_process_one_agent.msa](prototyping/metta_llm/metta_guidance/chat_process_one_agent.msa). In `chat_process.msa`  we use 4 agents:
- the agent aswering questions about platform;
- the agent answering questions about specific service;
- the agent advising which service to use;
- the agent answering to random questions. 
 
With help of  [question_type_selector_template.msa](prototyping/metta_llm/metta_guidance/templates/question_type_selector_template.msa), the LLM agent (currently chat-gpt agent) is asked to define the type of question being asked: 
 - SNET Platform
 - SpecificService
 - Services
 - Random
 
 Depending on the type of question, one of the `metta` scripts is processed to answer the question:
 - [platform_assistant_template.msa](prototyping/metta_llm/metta_guidance/templates/platform_assistant_template.msa)
 - [specific_service_template.msa](prototyping/metta_llm/metta_guidance/templates/specific_service_template.msa)
 - [service_finder_template.msa](prototyping/metta_llm/metta_guidance/templates/service_finder_template.msa)
 - [random_question_template.msa](prototyping/metta_llm/metta_guidance/templates/random_question_template.msa).
 
In `chat_process_one_agent.msa`, we compose the system message for the LLM agent (currently chat-gpt agent), combining information about the platform, specific service (the name of the service is retrieved from the context), and service descriptions. The LLM agent is then asked to answer the question, taking into account the system message.
