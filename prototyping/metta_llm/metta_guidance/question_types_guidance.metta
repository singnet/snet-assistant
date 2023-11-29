;!(extend-py! prototyping.assistant_utils.llm_gate_temp)
!(extend-py! llm_gate)
!(extend-py! prototyping.assistant_utils.data_getters.data_getter_extension)
!(import! &service-finder-template prototyping/metta_llm/metta_guidance/templates/service_finder_template.metta)
!(import! &question-type-template prototyping/metta_llm/metta_guidance/templates/question_type_selector_template.metta)
!(import! &platform-assistant-template prototyping/metta_llm/metta_guidance/templates/platform_assistant_template.metta)
!(import! &specific-service-template prototyping/metta_llm/metta_guidance/templates/specific_service_template.metta)
!(import! &random-question-template prototyping/metta_llm/metta_guidance/templates/random_question_template.metta)


!(bind! &messages (new-space))
(: system! (-> Atom Atom))
(: user! (-> Atom Atom))
(: assistant! (-> Atom Atom))
(= (system! $msg) (add-atom &messages (system $msg)))
(= (user! $msg) (add-atom &messages (user $msg)))
(= (assistant! $msg) (add-atom &messages (assistant $msg)))

!(let $question (new-state "[some question about service]")
     (add-atom &self (= (user-question) $question)))


(= (messages)
   (let $messages (collapse (get-atoms &messages))
        (cons-atom Messages $messages)))

(= (question-type $user-msg)
   (superpose
    (
        (change-state! (user-question) ( $user-msg))
         (llm &question-type-template)
    ))
    )

(= (user-query)
   (get-state (user-question)))

(= (add_question_context)
   ( get_question_context (get-state (user-question)) )

)

(= (get_prompt_for_service)
    (let $t (get-state (user-question)) (
    (get_service_prompt $t)))
)

(= (answer_question $type)
    (if (== $type "Services")
    (llm  &service-finder-template)
    (if (== $type "SNET Platform")  (llm  &platform-assistant-template)
    (if  (== $type "SpecificService") (llm &specific-service-template) (llm &random-question-template))
 ))
 )

(= (respond $user-msg)
    (superpose
    (
        (change-state! (user-question) ( $user-msg))
        (let $type ( llm &question-type-template)
        (answer_question $type)
        )
        )
    ))

;!(question-type "I have wav audio file, which contains some speech in Russian language. I would like to recognize emotions of the speaker in this file . Suggest some services for tis task")
;!(question-type "What is the price of Speech Emotion Recognition")
;!(question-type "How to create AI Marketplace account?")
;!(respond "I have wav audio file, which contains some speech in Russian language. I would like to recognize emotions of the speaker in this file . Suggest some services for tis task.")
;!(question-type "How to use Speech Emotion Recognition service")
;!(respond   "How to use Speech Emotion Recognition")
;!(question-type "Please list supported service types for snet daemon")
!(question-type "What is the type repository?")
!(respond   "What is the type repository?")

