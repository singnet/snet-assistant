!(import! &self motto.llm_gate)
!(import! &self prototyping.assistant_utils.data_getters.data_getter_extension)
!(import! &service-finder-template prototyping/metta_llm/metta_guidance/templates/service_finder_template.msa)

!(let $question (new-state "[some question about service]")
     (add-atom &self (= (user-question) $question)))

(= (messages)
   (let $messages (collapse (get-atoms &service-finder-template))
        (cons-atom Messages $messages)))

!(change-state! (user-question) ("I have wav audio file, which contains some speech in Russian language. I would like to recognize emotions of the speaker in this file . Suggest some services for tis task."))
(= (user-query)
   (get-state (user-question)))
!(llm (messages))
