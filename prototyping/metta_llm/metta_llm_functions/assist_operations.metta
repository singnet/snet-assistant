!(extend-py!  llm_gate)
!(extend-py! prototyping.assistant_utils.data_getters.data_getter_extension)

(= (append-expr $xs $x)
   (collapse (superpose ((superpose $xs) $x))))

; We could use $_, so this message would be automatically added to any prompt,
; but in this case it would be difficult to avoid its duplication
(= (message init)
   (system "You are the SingularityNet AI platform and marketplace assistant"))

(= (message service-list)
   (system ("There are next services in snet platform:" (get_service_descriptions) )))

(= (message reply-relevant)
   (system "Reply something relevant to user"))

(= (function init)
   find_service_names)



 (= (add_message_for_user (user $msg1) $msg2)
               (user (concat_strings $msg1 $msg2)))

(= (find_service_names ("True") (Messages $history $prev-state-msg $user-msg))
   (let $msg (add_message_for_user $user-msg "Your reply should be very short and have a format [a, b,...], where 'a', 'b' are relevant services")
   (llm
     (compose-prompt service-list $history $msg )
   )
   )
 )

(= (find_service_names (False) (Messages $history $prev-state-msg $user-msg))
   (llm
     (compose-prompt reply-relevant $history $user-msg)
   )
 )

(= (doc find_service_names)
 (let $services (get_service_names)
   (Doc
     (description "You should call this function if user asks to suggest a services")
     (parameters
      (call "boolean parameter which is True if user asks about services and False if user asks about something else" (True False) )
     ))
     )
)

(= (compose-prompt $state $history $new-msg)
   (let $msgs-state (collapse (message $state))
     (Messages
       $history
       (cons-atom Messages $msgs-state)
       $new-msg)))

(= (compose-functions $state)
   (let $fn-calls (collapse (function $state))
     (cons-atom Functions $fn-calls)))

; TODO? Assuming that $user-msg is not wrapped into (user ...) is convenient
; for the first call, but not convenient for using `respond` from functional calls
(= (respond $state $history $user-msg)
   (llm
     (compose-prompt $state $history (user $user-msg))
     (compose-functions $state)
    ))

;!(compose-prompt init () (user "What services do you have on the platform?"))
;!(compose-functions init)
;!(respond init () "What services do you have on the platform?")
;!(respond init  () "I have wav audio file, which contains some speech in Russian language. I would like to recognize emotions of the speaker in this file . Suggest some services for tis task.")
;!(respond init () "Hello. What can you do?")
