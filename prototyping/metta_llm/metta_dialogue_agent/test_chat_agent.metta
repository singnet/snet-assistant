!(extend-py! motto.llm_gate)

!(bind! &chat (metta-chat prototyping/metta_llm/metta_dialogue_agent/chat_process.msa))
;!(respond "What is the Abstractive Question Answering service on the snet platform?")
!(llm (Agent &chat) (user "What is the Abstractive Question Answering service on the snet platform?"))
!(llm (Agent &chat) (user "What is the service input?"))