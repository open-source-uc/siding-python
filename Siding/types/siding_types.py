import re 

NEW_FORM_TYPES = (
                  None,               # Self
                  (str,),             # Course_id
                  (str,),             # Name
                  (str,),             # Start date
                  (str,),             # Start time
                  (str,),             # End date
                  (str,),             # End time
                  (str,['SI','NO']))  # Resend

NEW_FORM_FORMAT = (
                    None,
                    lambda course: len(course) >= 4,
                    lambda name: True,
                    lambda start: re.match('\d{2}-\d{2}-\d{4}',start),
                    )