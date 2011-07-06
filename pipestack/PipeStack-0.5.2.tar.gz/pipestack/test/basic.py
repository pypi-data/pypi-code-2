#
# These tests are written without TestPipe because we need to know the test
# infrastucture works.
#

import os
import sys
from unittest import TestCase, main
from getopt import GetoptError
from commandtool import Cmd as Command
from pipestack.pipe import Pipe, Marble
from pipestack.app import App, DuplicatePipeNameError, DuplicateCommandNameError, ReservedPipeNameError, reserved, pipe, command, Bag, AppCmd, PipeError

# For the tests we don't want logging and warning output printed to the console
import logging
logging.disable(logging.error)
import warnings
warnings.filterwarnings("ignore")

#
# Basic test pipe and command
#

from conversionkit import Field
from stringconvert import unicodeToUnicode

class TestPipe(Pipe):
    pass

class TestPipeWithOptions(Pipe):
    options = {
        'key': Field(
            unicodeToUnicode(),
            missing_or_empty_error = 'The key field wasn\'t specified'
        )
    }

class TestPipeWithOptionsAndRequiredSection(Pipe):
    required_section_error_message = 'You must specify the %(name)s.key field'
    options = {
        'key': Field(
            unicodeToUnicode(),
            missing_or_empty_error = 'The key field wasn\'t specified'
        )
    }

class TestCommand(Command):
    def on_run(self, app, args, opts):
        # The app object doesn't have a results attribute, we are creating it purely for ease of test writing, this is not the way to do this in normal code
        app.start_flow(ensure=['pipe1'])
        app.results = [self.name, self.aliases, args, opts]

class TestCommandWithPipes(Command):
    def on_run(self, app, args, opts):
        # The app object doesn't have a results attribute, we are creating it purely for ease of test writing, this is not the way to do this in normal code
        app.start_flow(ensure=['pipe1', 'pipe2'])
        app.results = [self.name, self.aliases, args, opts]

#
# Test Pipe and Command Names
#

class TestDuplicates(TestCase):
    def test_duplicate_pipe_name(self):
        class DuplicatePipeName(App):
            pipes = [
                pipe('pipe1', 'pipestack.test.basic:TestPipe'),
                pipe('pipe1', 'pipestack.test.basic:TestPipe'),
            ]
        self.assertRaises(DuplicatePipeNameError, DuplicatePipeName, ())

    def test_duplicate_command_name(self):
        class DuplicateCommandName(App):
            commands = [
                command('cmd1', 'pipestack.test.basic:TestCommand'),
                command('cmd1', 'pipestack.test.basic:TestCommand'),
            ]
        self.assertRaises(DuplicateCommandNameError, DuplicateCommandName, ())

class TestReservedPipeNames(TestCase):
    def test_reserved_pipe_names(self):
        self.assertEqual(reserved, ['command', 'enter', 'app', 'interrupt_flow', 'pipe', 'aliases', 'default_aliases', 'name'])
        for name in reserved:
            class ReservedPipeName(App):
                pipes = [
                    pipe(name, 'pipestack.test.basic:TestPipe'),
                ]
            self.assertRaises(ReservedPipeNameError, ReservedPipeName, ())

#
# Test pipeline formation and custom bag options
#

class TestPipeStackApp(App):
    pipes = [
        pipe('pipe1', 'pipestack.test.basic:TestPipe'),
        pipe('pipe2', 'pipestack.test.basic:TestPipe'),
        pipe('pipe3', 'pipestack.test.basic:TestPipe'),
    ]

class TestPipeStackAppWithExclude(App):
    pipes = [
        pipe('pipe1', 'pipestack.test.basic:TestPipe'),
        pipe('pipe2', 'pipestack.test.basic:TestPipe'),
        pipe('pipe3', 'pipestack.test.basic:TestPipe'),
        pipe('pipe4', 'pipestack.test.basic:TestPipe'),
        pipe('pipe5', 'pipestack.test.basic:TestPipe'),
        pipe('pipe6', 'pipestack.test.basic:TestPipe'),
    ]
    exclude = ['pipe4', 'pipe5', 'pipe6']

class TestPipeStackAppWithCommands(App):
    pipes = [
        pipe('pipe1', 'pipestack.test.basic:TestPipe'),
        pipe('pipe2', 'pipestack.test.basic:TestPipe'),
        pipe('pipe3', 'pipestack.test.basic:TestPipe'),
    ]
    commands = [
        command('cmd1', 'pipestack.test.basic:TestCommand', aliases=dict(cmd='cmd2')),
        command('cmd2', TestCommandWithPipes),
    ]

class TestPipeStackAppWithCommandsAndOptions(App):
    pipes = [
        pipe('pipe1', 'pipestack.test.basic:TestPipeWithOptions'),
        pipe('pipe2', 'pipestack.test.basic:TestPipeWithOptionsAndRequiredSection'),
        pipe('pipe3', 'pipestack.test.basic:TestPipe'),
    ]
    commands = [
        command('cmd1', 'pipestack.test.basic:TestCommand', aliases=dict(cmd='cmd2')),
        command('cmd2', TestCommandWithPipes),
    ]

class TestBadExclude(TestCase):

    def test_bad_exclude(self):
        class TestPipeStackAppWithBadExclude(App):
            pipes = [
                pipe('pipe1', 'pipestack.test.basic:TestPipe'),
                pipe('pipe2', 'pipestack.test.basic:TestPipe'),
                pipe('pipe3', 'pipestack.test.basic:TestPipe'),
                pipe('pipe4', 'pipestack.test.basic:TestPipe'),
                pipe('pipe5', 'pipestack.test.basic:TestPipe'),
                pipe('pipe6', 'pipestack.test.basic:TestPipe'),
            ]
            exclude = ['pipe4', 'pipe5', 'does_not_exist']
        app = TestPipeStackAppWithBadExclude()
        #app.default_pipeline
        self.assertRaises(PipeError, app._get_default_pipeline)

class TestStartFlow(TestCase):
    def setUp(self):
        self.app = TestPipeStackApp()
        self.exclude_app = TestPipeStackAppWithExclude()

    def test_default_pipeline(self):
        self.assertEqual(
            self.app.default_pipeline, 
            self.exclude_app.default_pipeline, 
            ['pipe1', 'pipe2', 'pipe3'],
        )

    def test_run(self):
        was_run = []
        def run(bag):
            was_run.append(True)
        self.app.start_flow(run=run)
        self.assertEqual(was_run, [True])
        # Test that running it again adds another True:
        self.app.start_flow(run=run)
        self.assertEqual(was_run, [True, True])

    def test_default_bag(self):
        def run(bag):
            self.assertEqual(isinstance(bag, Bag), True)
        self.app.start_flow(run=run)

    def test_custom_bag(self):
        class CustomBag(Bag):
            pass
        def run(bag):
            self.assertEqual(isinstance(bag, CustomBag), True)
        self.app.start_flow(CustomBag(), run=run)

    def test_reserved_bag_key(self):
        self.assertRaises(ReservedPipeNameError, self.app.start_flow, dict(enter='enter'))
        class CustomBag(dict):
            enter = 'enter'
        self.assertRaises(ReservedPipeNameError, self.app.start_flow, CustomBag())

    def test_ensure(self):
        def run(bag):
            # Note this isn't testing the order the pipes are entered
            for name in ['pipe2', 'pipe6', 'pipe4']:
                self.assertEqual(name in bag, True)
        self.exclude_app.start_flow(
            ensure=['pipe2', 'pipe6', 'pipe4'], 
            run=run,
        )

    def test_ensure_no_duplicates(self):
        self.assertRaises(
            DuplicatePipeNameError, 
            self.exclude_app.start_flow, 
            None, 
            ['pipe2', 'pipe2'],
        )

    def test_no_commands_specifed_error(self):
        self.assertRaises(Exception, self.app.handle_command_line)

class TestBag(TestCase):

    def setUp(self):
        self.app = TestPipeStackAppWithExclude()

    def test_bag(self):
        def run(bag):
            should_be_there = ['app', 'interrupt_flow', 'enter']
            for name in should_be_there:
                self.assertEqual(name in bag, True)
            self.assertEqual(len(should_be_there), len(bag.keys()))
            self.assertEqual(isinstance(bag.app, App), True)
            # More specifically in this case:
            self.assertEqual(bag.app is self.app, True)
        self.app.start_flow(run=run)

class TestFlow(TestCase):

    def test_flow(self):
        results = []

        class LoggingPipe(Pipe):
            def enter(self, bag):
                results.append(self.name+' enter')
                Pipe.enter(self, bag)
            def leave(self, bag, error=None):
                results.append(self.name+' leave '+str(error))
                Pipe.leave(self, bag, error)

        class TestPipeStackApp(App):
            pipes = [
                pipe('pipe1', LoggingPipe),
                pipe('pipe2', LoggingPipe),
                pipe('pipe3', LoggingPipe),
            ]
        app = TestPipeStackApp()
        def run(bag):

            self.assertEqual(results, [])
            results.append('run enter')
            self.assertEqual(len(bag), 3)

            bag.enter('pipe1')
            self.assertEqual(
                results, 
                ['run enter', 'pipe1 enter'],
            )
            self.assertEqual(bag.pipe1, None)
            self.assertEqual(len(bag), 4)

            bag.enter('pipe2')
            self.assertEqual(
                results, 
                ['run enter', 'pipe1 enter', 'pipe2 enter']
            )
            self.assertEqual(bag.pipe2, None)
            self.assertEqual(len(bag), 5)

            # Try putting in some nonsense
            self.assertRaises(Exception, bag.enter, dict())
            self.assertRaises(Exception, bag.enter, 'pipe2')
            self.assertRaises(Exception, bag.enter, 'no_such_pipe')

            results.append('run leave')
        app.start_flow(run=run)
        self.assertEqual(
            results,
            [
                'run enter', 
                'pipe1 enter', 
                'pipe2 enter', 
                'run leave', 
                'pipe2 leave False', 
                'pipe1 leave False',
            ],
        )
        # Check it all works on the subsequent flow too.
        for i in range(len(results)):
            results.pop()
        app.start_flow(run=run)

    def test_interrupt_flow_pipe_application_handled(self):
        results = []

        class LoggingPipe(Pipe):
            def enter(self, bag):
                results.append(self.name+' enter')
                Pipe.enter(self, bag)
            def leave(self, bag, error=False):
                results.append(self.name+' leave '+str(error))
                Pipe.leave(self, bag, error)

        class LoggingAppHandlerPipe(Pipe):
            def enter(self, bag):
                results.append(self.name+' enter')
                Pipe.enter(self, bag)
                bag.interrupt_flow()
            def leave(self, bag, error=False):
                results.append(self.name+' leave '+str(error))
                Pipe.leave(self, bag, error)

        class TestPipeStackApp(App):
            pipes = [
                pipe('pipe1', LoggingPipe),
                pipe('pipe2', LoggingAppHandlerPipe),
                pipe('pipe3', LoggingPipe),
            ]

        app = TestPipeStackApp()

        app.start_flow(ensure=app.default_pipeline)

        self.assertEqual(
            results, 
            [
                'pipe1 enter', 
                'pipe2 enter', 
                'pipe2 leave False',
                'pipe1 leave False',
            ]
        )

    def test_flow_error(self):
        results = []

        class LoggingPipe(Pipe):
            def enter(pself, bag):
                results.append(pself.name+' enter')
                Pipe.enter(pself, bag)
            def leave(pself, bag, error=False):
                results.append(pself.name+' leave '+str(error))
                Pipe.leave(pself, bag, error)

        class LoggingErrorHandlerPipe(Pipe):
            def enter(pself, bag):
                results.append(pself.name+' enter')
                Pipe.enter(pself, bag)
                self.assertRaises(Exception, bag.interrupt_flow, True)
            def leave(pself, bag, error=False):
                results.append(pself.name+' leave '+str(error))
                Pipe.leave(pself, bag, error)

        class TestPipeStackApp(App):
            pipes = [
                pipe('pipe1', LoggingPipe),
                pipe('pipe2', LoggingErrorHandlerPipe),
                pipe('pipe3', LoggingPipe),
            ]

        app = TestPipeStackApp()

        def run(bag):
            results.append('run enter')
            raise Exception('This is a test error from run()')
        self.assertRaises(Exception, app.start_flow, None, app.default_pipeline, run)
        self.assertEqual(
            results, 
            [
                'pipe1 enter', 
                'pipe2 enter', 
                'pipe3 enter', 
                'run enter', 
                # No run leave because the error occurred before it, 
                'pipe3 leave True',
                'pipe2 leave True', 
                'pipe1 leave True',
            ]
        )

    def test_interrupt_flow_pipe_error_handled_no_error(self):
        results = []

        class LoggingPipe(Pipe):
            def enter(pself, bag):
                results.append(pself.name+' enter')
                Pipe.enter(pself, bag)
            def leave(pself, bag, error=False):
                results.append(pself.name+' leave '+str(error))
                Pipe.leave(pself, bag, error)

        class LoggingErrorHandlerPipe(Pipe):
            def enter(pself, bag):
                results.append(pself.name+' enter')
                Pipe.enter(pself, bag)
                self.assertRaises(Exception, bag.interrupt_flow, True)
            def leave(pself, bag, error=False):
                results.append(pself.name+' leave '+str(error))
                Pipe.leave(pself, bag, error)
                bag.interrupt_flow(True)

        class TestPipeStackApp(App):
            pipes = [
                pipe('pipe1', LoggingPipe),
                pipe('pipe2', LoggingErrorHandlerPipe),
                pipe('pipe3', LoggingPipe),
            ]

        app = TestPipeStackApp()

        def run(bag):
            results.append('run enter')
            raise Exception('This is a test error from run()')
        app.start_flow(None, app.default_pipeline, run)
        self.assertEqual(
            results, 
            [
                'pipe1 enter', 
                'pipe2 enter', 
                'pipe3 enter', 
                'run enter', 
                # No run leave because the error occurred before it, 
                'pipe3 leave True',
                'pipe2 leave True', 
                'pipe1 leave True',
            ]
        )


    def test_interrupt_flow_run_application_handled(self):
        results = []

        class LoggingPipe(Pipe):
            def enter(self, bag):
                results.append(self.name+' enter')
                Pipe.enter(self, bag)
            def leave(self, bag, error=False):
                results.append(self.name+' leave '+str(error))
                Pipe.leave(self, bag, error)

        class TestPipeStackApp(App):
            pipes = [
                pipe('pipe1', LoggingPipe),
                pipe('pipe2', LoggingPipe),
                pipe('pipe3', LoggingPipe),
            ]

        app = TestPipeStackApp()

        def run(bag):
            results.append('run enter')
            bag.interrupt_flow()
            results.append('run leave')
        app.start_flow(ensure=app.default_pipeline, run=run)
        self.assertEqual(
            results, 
            [
                'pipe1 enter', 
                'pipe2 enter', 
                'pipe3 enter', 
                'run enter', 
                'run leave',
                'pipe3 leave False', 
                'pipe2 leave False',
                'pipe1 leave False',
            ]
        )

    def test_bad_pipe_handled(self):
        results = []

        class LoggingErrorHandlerPipe(Pipe):
            def enter(self, bag):
                results.append(self.name+' enter')
                Pipe.enter(self, bag)
            def leave(self, bag, error=False):
                bag.interrupt_flow(error_handled=True)
                results.append(self.name+' leave '+str(error))
                Pipe.leave(self, bag, error)

        class LoggingPipe(Pipe):
            def enter(self, bag):
                results.append(self.name+' enter')
                Pipe.enter(self, bag)
            def leave(self, bag, error=False):
                results.append(self.name+' leave '+str(error))
                Pipe.leave(self, bag, error)

        class LoggingErrorPipe(Pipe):
            def enter(self, bag):
                results.append(self.name+' enter')
                raise Exception('Bad pipe')

            def leave(self, bag, error=False):
                # This doesn't get run
                results.append(self.name+' leave '+str(error))
                Pipe.leave(self, bag, error)

        class TestPipeStackApp(App):
            pipes = [
                pipe('pipe1', LoggingPipe),
                pipe('pipe2', LoggingErrorHandlerPipe),
                pipe('pipe3', LoggingErrorPipe),
            ]

        app = TestPipeStackApp()

        def run(bag):
            results.append('run enter')
        app.start_flow(None, app.default_pipeline, run)
        self.assertEqual(
            results, 
            [
                'pipe1 enter', 
                'pipe2 enter', 
                'pipe3 enter', 
                # Actually, we don't leave the pipe that caused the error, it is in a weird state, we don't want more things to break
                # 'pipe2 leave True', 
                'pipe2 leave True',
                'pipe1 leave True',
            ]
        )

    def test_bad_pipe(self):
        results = []

        class LoggingPipe(Pipe):
            def enter(self, bag):
                results.append(self.name+' enter')
                Pipe.enter(self, bag)
            def leave(self, bag, error=False):
                results.append(self.name+' leave '+str(error))
                Pipe.leave(self, bag, error)

        class LoggingErrorPipe(Pipe):
            def enter(self, bag):
                results.append(self.name+' enter')
                raise Exception('Bad pipe')

            def leave(self, bag, error=False):
                # This doesn't get run
                results.append(self.name+' leave '+str(error))
                Pipe.leave(self, bag, error)

        class TestPipeStackApp(App):
            pipes = [
                pipe('pipe1', LoggingPipe),
                pipe('pipe2', LoggingErrorPipe),
                pipe('pipe3', LoggingPipe),
            ]

        app = TestPipeStackApp()

        def run(bag):
            results.append('run enter')
        self.assertRaises(Exception, app.start_flow, None, app.default_pipeline, run)
        self.assertEqual(
            results, 
            [
                'pipe1 enter', 
                'pipe2 enter', 
                # Actually, we don't leave the pipe that caused the error, it is in a weird state, we don't want more things to break
                # 'pipe2 leave True', 
                'pipe1 leave True',
            ]
        )

    def test_interrupt_flow_run_error_handled(self):
        results = []

        class LoggingPipe(Pipe):
            def enter(self, bag):
                results.append(self.name+' enter')
                Pipe.enter(self, bag)
            def leave(self, bag, error=False):
                results.append(self.name+' leave '+str(error))
                Pipe.leave(self, bag, error)

        class TestPipeStackApp(App):
            pipes = [
                pipe('pipe1', LoggingPipe),
                pipe('pipe2', LoggingPipe),
                pipe('pipe3', LoggingPipe),
            ]

        app = TestPipeStackApp()

        def run(bag):
            results.append('run enter')
            self.assertRaises(Exception, bag.interrupt_flow, True)
            results.append('run leave')
        app.start_flow(ensure=app.default_pipeline, run=run)
	# In a real case, this would never get here because the exception would
	# have been raised, but the correct behviour if someone caught that
	# exception as we have would be this because the error would never have
	# been specified
        self.assertEqual(
            results, 
            [
                'pipe1 enter', 
                'pipe2 enter', 
                'pipe3 enter', 
                'run enter', 
                'run leave', 
                'pipe3 leave False', 
                'pipe2 leave False', 
                'pipe1 leave False',
            ]
        )

class TestApp(TestCase):

    def setUp(self):
        self.app = TestPipeStackAppWithCommands()

    def test_app(self):
        def run(bag):
            should_be_there = [
                'api_version', 
                'commands', 
                'config', 
                'config_file', 
                'default_pipeline', 
                'exclude', 
                'handle_command_line', 
                'option', 
                'pipes', 
                'start_flow',
            ]
            for name in should_be_there:
                self.assertEqual(name in dir(bag.app), True)
            # Now test each of these attributes
            self.assertEqual(bag.app.api_version, (0,8,0))
            self.assertEqual(
                bag.app.commands, 
                [
                    {'class_': 'pipestack.test.basic:TestCommand', 'extras': {}, 'name': 'cmd1', 'aliases': {'cmd': 'cmd2'}}, 
                    {'class_': TestCommandWithPipes, 'extras': {}, 'name': 'cmd2', 'aliases': None},
                ]
            )
            # Default pipeline was tested earlier, skipping
            self.assertEqual(bag.app.exclude, [])
            self.assertEqual(bag.app.config_file, None)
            self.assertEqual(bag.app.option, None)
            self.assertEqual(
                bag.app.pipes,
                [
                    {'class_': 'pipestack.test.basic:TestPipe', 'extras': {}, 'name': 'pipe1', 'aliases': None}, 
                    {'class_': 'pipestack.test.basic:TestPipe', 'extras': {}, 'name': 'pipe2', 'aliases': None}, 
                    {'class_': 'pipestack.test.basic:TestPipe', 'extras': {}, 'name': 'pipe3', 'aliases': None},
                ]
            )
            # Start flow tested earlier
            # parse_config and handle_command_line tested next
        self.app.start_flow(run=run)

    def test_handle_command_line(self):
        # Note: CommandTool has its own tests so we don't need to test it here, just that it works in the way we want it to.
        exited = []
        def exit(num):
            exited.append(num)
        self.app.handle_command_line(['cmd1'], exit=exit)
        self.assertEqual(exited, [0])
        self.assertEqual(self.app.results, ['cmd1', {'cmd': 'cmd2'}, [], {'help': False}])
        self.app.handle_command_line(['cmd2'], exit=exit)
        self.assertEqual(exited, [0, 0])
        self.assertEqual(self.app.results, ['cmd2', {}, [], {'help': False}])

class TestConfig(TestCase):
    def setUp(self):
        self.app = TestPipeStackAppWithCommandsAndOptions()

    def test_no_config(self):
        from StringIO import StringIO
        stdout = StringIO()
        a = sys.stdout
        sys.stdout = stdout
        exited = []
        def exit(num):
            exited.append(num)
        self.app.handle_command_line(['cmd2'], exit=exit)
        self.assertEqual(exited, [1])
        sys.stdout = a
        self.assertEqual(stdout.getvalue(), "Error: No config file specified\nTry `basic.py cmd2 --help' for more information.\n")

    def test_parse_config(self):
        dir_ = os.path.join(os.sep.join(__file__.split(os.sep)[:-1]), 'files')
        config_file = os.path.abspath(os.path.join(dir_, 'test.conf'))
        exited = []
        def exit(num):
            exited.append(num)
        self.app.handle_command_line(['--config', config_file, 'cmd2'], exit=exit)
        self.assertEqual(exited, [0])
        self.assertEqual(self.app.results, ['cmd2', {}, [], {'help': False}])
        # @@@ Not sure this should include the pipe
        self.assertEqual(self.app.config, {'pipe': {}, 'pipe1': {'key': u'value'}, 'pipe2': {'key': u'value'}})
        self.assertEqual(self.app.option, {'pipe1': {'key': u'value'}, 'pipe2': {'key': u'value'}})
        self.assertEqual(self.app.config_file, config_file)
        # The directory is set to the directory the config file is in
        # XXX Check this
        # self.assertEqual(os.path.abspath(os.getcwd()), os.path.abspath(dir_))

    # XXX Not implemented
    # Need to test that if the pipes don't have any options, the config file isn't
    # needed but that if one of them does, it is.
    def test_config_requirements(self):
        pass

# Then need to test aliases on pipes and commands
class TestAliases(TestCase):

    def test_pipe_aliases(self):
        pass

    def test_command_aliases(self):
        pass

    # Marble aliases are tested below

# Then need to test marbles and their behaviour
class TestMarble(TestCase):

    def test_marble(self):
        results = []

        class MyMarble(Marble):
            def __init__(marble, *k, **p):
                Marble.__init__(marble, *k, **p)
                marble.vars = 'Hello'

        class AliasPipe(Pipe):
            marble_class = MyMarble
            default_aliases = dict(core='core', second='second')
            def enter(self, bag):
                results.append(self.name+' enter')
                Pipe.enter(self, bag)
            def leave(self, bag, error=False):
                results.append(self.name+' leave '+str(error))
                Pipe.leave(self, bag, error)

        class NoAliasPipe(Pipe):
            marble_class = MyMarble
            def enter(self, bag):
                results.append(self.name+' enter')
                Pipe.enter(self, bag)
            def leave(self, bag, error=False):
                results.append(self.name+' leave '+str(error))
                Pipe.leave(self, bag, error)

        class TestPipeStackApp(App):
            pipes = [
                pipe('pipe1', AliasPipe, aliases=dict(core='pipe2')),
                pipe('pipe2', NoAliasPipe),
            ]

        app = TestPipeStackApp()

        def run(bag):
            results.append('run enter')
            self.assertEqual(isinstance(bag.pipe1, MyMarble), True)
            self.assertEqual(bag.pipe1.vars, 'Hello')
            self.assertEqual(bag.pipe1.default_aliases, dict(core='core', second='second'))
            self.assertEqual(bag.pipe1.aliases, dict(core='pipe2', second='second'))
            self.assertEqual(bag.pipe1.core is bag['pipe2'] is getattr(bag.pipe1, 'core'), True)
            self.assertEqual(bag['pipe2'].aliases, {})
            self.assertEqual(bag['pipe2'].default_aliases, {})
            results.append('run leave')
        app.start_flow(None, app.default_pipeline, run)
        self.assertEqual(
            results, 
            [
                'pipe1 enter', 
                'pipe2 enter', 
                'run enter', 
                'run leave', 
                'pipe2 leave False', 
                'pipe1 leave False', 
            ]
        )

if __name__ == '__main__':
    main()

