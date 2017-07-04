#!/usr/bin/python
import logging
import libmu.util
from libmu import tracker, TerminalState, CommandListState, ForLoopState, OnePassState, ErrorState
from stages.util import default_trace_func


class FinalState(TerminalState):
    extra = "(finished)"


class EmitState(CommandListState):
    extra = "(emit output)"
    nextState = FinalState
    commandlist = [ (None, "quit:")
                  ]

    def __init__(self, prevState):
        super(EmitState, self).__init__(prevState, trace_func=default_trace_func)
        out_queue = prevState.out_queue
        out_key = prevState.out_key

        out_event = {'key': out_key}
        out_queue['chunks'].put({'lineage': self.in_events['lineage'], 'chunks': out_event, 'pipe_id': self.in_events['pipe_id']})


class RunState(CommandListState):
    extra = "(run)"
    nextState = EmitState
    commandlist = [ (None, 'run:mkdir -p ##TMPDIR##/in_0/')
                  , ('OK:RETVAL(0)', 'collect:{in_key} ##TMPDIR##/in_0')
                  , ('OK:COLLECT', 'run:mkdir -p ##TMPDIR##/out_0/')
                  , ('OK:RETVAL(0)', 'run:./ffmpeg -framerate 24 -start_number 1 -i ##TMPDIR##/in_0/%08d.png '
                                   '-c:v libx264 -pix_fmt yuv420p ##TMPDIR##/out_0/{lineage}.mp4')
                  , ('OK:RETVAL(0)', 'emit:##TMPDIR##/out_0 {out_key}')
                  , ('OK:EMIT', None)
                    ]

    def __init__(self, prevState):
        super(RunState, self).__init__(prevState, trace_func=default_trace_func)
        self.out_queue = prevState.out_queue
        self.out_key = prevState.out_key

        params = {'in_key': self.in_events['frames']['key'], 'lineage': '%08d'%int(self.in_events['lineage']), 'out_key': self.out_key}
        logging.debug('params: '+str(params))
        self.commands = [ s.format(**params) if s is not None else None for s in self.commands ]


class InitState(CommandListState):
    extra = "(init)"
    nextState = RunState
    commandlist = [ ("OK:HELLO", "seti:nonblock:0")
                  , "run:rm -rf /tmp/*"
                  , "run:mkdir -p ##TMPDIR##"
                  , None
                  ]

    def __init__(self, prevState, in_events, out_queue):
        super(InitState, self).__init__(prevState, in_events=in_events, trace_func=default_trace_func)
        self.out_queue = out_queue
        self.out_key = 's3://lixiang-pipeline/'+in_events['pipe_id']+'/encode/'+libmu.util.rand_str(16)+'/'
        logging.debug('in_events: '+str(in_events)+', out_queue: '+str(out_queue))