
variable_start_delimiter = "# /*---- VARIABLE DEFINITION ----*\\"
variable_end_delimiter = "# /*---- END VARIABLE DEFINITION ----*\\"

class MailerAction(object):
    
    to_ = None
    from_ = None
    cc = None
    subject = "{{object_title}} -> {{transition}}"
    body = """{{object_title}} at {{object_url}} has been transitioned from {{previous_state}} to {{new_state}} on {{formatted_datetime}}"""
    
    def __init__(self, script=None):
        self.script = script
        self.parse_script()
            
            
    def parse_script(self):
        if self.script:
            
            reading = False
            current_value = None
            current_name = None

            for line in self.script.body().splitlines():
                
                if line.startswith(variable_end_delimiter):
                    setattr(self, current_name, current_value)
                    reading = False
                
                if reading:
                    if current_value is None:
                        current_value = line.lstrip('# ')
                    else:
                        current_value += "\n" + line.lstrip('# ')
                        
                if line.startswith(variable_start_delimiter):
                    current_name = line.lstrip(variable_start_delimiter).strip()
                    current_value = None
                    reading = True
            
        