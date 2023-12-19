!(import! &service-finder-template prototyping/metta_llm/metta_guidance/templates/service_finder_template_for_tests.msa)
!(import! &question-type-template prototyping/metta_llm/metta_guidance/templates/question_type_selector_template.msa)
!(import! &platform-assistant-template prototyping/metta_llm/metta_guidance/templates/platform_assistant_template.msa)
!(import! &specific-service-template prototyping/metta_llm/metta_guidance/templates/specific_service_template.msa)
!(import! &random-question-template prototyping/metta_llm/metta_guidance/templates/random_question_template.msa)
!(extend-py! motto.llm_gate)
;!(extend-py! prototyping.metta_llm.metta_guidance.motto1.llm_gate)
!(extend-py! prototyping.assistant_utils.data_getters.data_getter_extension)
!(bind! &Agent (Agent (chat-gpt "gpt-3.5-turbo-0613")))
!(bind! &platform_retrieval (Agent (retrieval-agent  (get-platform-docs-folder) 200 10 (get-data-dir))))
!(bind! &service_retrieval (retrieval-agent  (get-service-docs-folder) 200 10 (get-data-dir)))



!(let $question (new-state "[some question about service]")
    ( let () (add-atom &self (= (user-question) $question)) (empty))
 )
!(let $service_file (new-state "[the name of the file with information about service]")
    ( let () (add-atom &self (= (current-service-file) $service_file)) (empty))
)

(= (question-type $user-msg)
   (superpose
        (
            (change-state! (user-question) ( $user-msg))
             (llm &Agent &question-type-template)
        )
   )
)
(= (service-descriptions)
    (get-service-descriptions)
)
(= (user-query)
   (get-state (user-question))
)

(= (add-platform-question-context)
   (llm  &platform_retrieval (user (user-query)))
)

(= (get-prompt-for-service)
    (let $question (user-query)
        (llm  (Agent &service_retrieval (doc_name (get-state (current-service-file))))
            (user $question)
        )
    )
)


(= (answer_question $type)
    (case $type (
        ("Services" (let $prompt &service-finder-template  (llm &Agent  $prompt)))
        ("SNET Platform" (let $prompt &platform-assistant-template (llm &Agent $prompt)))
        ("SpecificService"
                (superpose
                   (
                    (let $service_name (extract-service-file-name ((history) (user-query)))
                        (if ( == $service_name (%void)) (empty) (let () (change-state! (current-service-file) $service_name) (empty)))
                     )
                    (let $prompt &specific-service-template (llm &Agent  $prompt))
                   )
                ))
        ($_ (let $prompt &random-question-template (llm &Agent $prompt)))
    ))
)

(= (respond $user-msg $type)
    (superpose
    (
        (change-state! (user-question) ( $user-msg))
        (answer_question $type)
    )
    ))

;!(question-type "I have wav audio file, which contains some speech in Russian language. I would like to recognize emotions of the speaker in this file . Suggest some services for tis task")
;!(question-type "What is the price of Speech Emotion Recognition")
;!(question-type "How to create AI Marketplace account?")
;!(respond "I have wav audio file, which contains some speech in Russian language. I would like to recognize emotions of the speaker in this file . Suggest some services for tis task.")
;!(question-type "How to use Speech Emotion Recognition service")
;!(respond   "How to use Speech Emotion Recognition")
;!(question-type "Please list supported service types for snet daemon")
;!(question-type "What is the type repository?")
;!(respond   "What is the type repository?")

