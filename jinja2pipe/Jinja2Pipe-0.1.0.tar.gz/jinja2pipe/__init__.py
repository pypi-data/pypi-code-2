from pipestack.pipe import Marble, MarblePipe
from jinja2 import Environment, FileSystemLoader, FileSystemBytecodeCache
from bn import AttributeDict
from conversionkit import Field
from configconvert import existingDirectory

class Jinja2Marble(Marble):
    def on_set_persistent_state(self, persistent_state):
        self.persistent_state = persistent_state

    def render(self, templatename, **kwargs):
        template = self.persistent_state.env.get_template(templatename)
        return template.render(**kwargs)

class Jinja2Pipe(MarblePipe):
    marble_class = Jinja2Marble
    options = dict(
        template_dir = Field(
            existingDirectory(),
            missing_or_empty_error = "Please enter a value for '%(name)s.template_dir'",
        ),
        cache_dir = Field(
            existingDirectory(),
            missing_or_empty_error = "Please enter a value for '%(name)s.cache_dir'",
        ),
    )

    def on_parse_options(self, bag):
        MarblePipe.on_parse_options(self, bag)
        self.persistent_state = AttributeDict(
            env = Environment(
                loader = FileSystemLoader([self.config.template_dir]),
                bytecode_cache = FileSystemBytecodeCache(self.config.cache_dir, '%s.cache')
            )
        )

