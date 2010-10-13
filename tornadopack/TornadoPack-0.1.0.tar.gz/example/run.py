from serviceprovider import prepareFlow, helloService
from serviceprovider.cmd import bootFromCmdLine, MainCmd
from tornadopack.cmd import ServeTornado

prepareFlow(
    available_services = {
        'hello': helloService(),
    },
    boot =  bootFromCmdLine(
        commands={
            None: MainCmd(),
            'serve': ServeTornado(
                [
                    'hello'
                ],
            ),
        },
    )
)
