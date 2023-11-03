;!(extend-py! prototyping.assistant_utils.llm_gate_temp)
!(extend-py! llm_gate)
!(extend-py! prototyping.assistant_utils.descriptions_getters.data_getter_extension)
!(import! &service-finder-template prototyping/service_find/metta_guidance/templates/service_finder_template.metta)
!(import! &question-type-template prototyping/service_find/metta_guidance/templates/question_type_selector_template.metta)
!(import! &platform-assistant-template prototyping/service_find/metta_guidance/templates/platform_assistant_template.metta)
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

(= (service-messages)
   (let $messages (collapse (get-atoms &service-finder-template))
        (cons-atom Messages $messages)))

(= (platform-messages)
   (let $messages (collapse (get-atoms &platform-assistant-template ))
        (cons-atom Messages $messages)))

(= (question-type-messages)
   (let $messages (collapse (get-atoms &question-type-template))
        (cons-atom Messages $messages)))

(= (user-query)
   (get-state (user-question)))

(= (add_question_context)
   ( get_question_context (get-state (user-question)) )

)

(= (answer_question $type)
    (if (== $type "Services")
    (llm (service-messages)) (
    if (== $type "SNET Platform")  (llm (platform-messages)) (llm (messages)))
 ))

(= (respond $state $user-msg)
    (superpose
    (
        (change-state! (user-question) ( $user-msg))
        (let $type ( llm (question-type-messages))
        (answer_question $type)
        )
        )
    ))


;!(respond question "I have wav audio file, which contains some speech in Russian language. I would like to recognize emotions of the speaker in this file . Suggest some services for tis task.")
;!(respond question "How to create AI Marketplace account?")
