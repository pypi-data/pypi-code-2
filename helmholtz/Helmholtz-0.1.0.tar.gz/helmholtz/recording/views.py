#encoding:utf-8
from django.utils.datastructures import SortedDict
from django.shortcuts import render_to_response
from helmholtz.core.decorators import memorise_last_page, memorise_last_rendered_page
from helmholtz.access_control.conditions import is_accessible_by
from helmholtz.experiment.models import Experiment
from helmholtz.recording.tools.filters import get_available_methods, get_available_protocols
from helmholtz.recording.models import RecordingBlock, ProtocolRecording
from helmholtz.people.models import ScientificStructure
from helmholtz.storage.models import File
from helmholtz.signals.models import Signal
from helmholtz.analysis.models import Analysis

def get_recording_methods(blocks):
    all_methods = SortedDict()
    blk_methods = get_available_methods(blocks, 'recordingconfiguration__configuration')
    protocols = ProtocolRecording.objects.filter(block__in=blocks)
    ptc_methods = get_available_methods(protocols, 'signal__configuration__configuration')
    signals = Signal.objects.filter(protocol__in=protocols)
    trc_methods = get_available_methods(signals, 'configuration__configuration')
    for blk_method, blk_count in blk_methods['names'].items() :
        all_methods[blk_method] = SortedDict()
        all_methods[blk_method]['blocks'] = blk_count
        if ptc_methods['names'].has_key(blk_method) :
            ptc_count = ptc_methods['names'][blk_method]
        else :
            ptc_count = 0
        all_methods[blk_method]['protocols'] = ptc_count
        if trc_methods['names'].has_key(blk_method) :
            trc_count = trc_methods['names'][blk_method]
        else :
            trc_count = 0
        all_methods[blk_method]['traces'] = trc_count
    return all_methods

def get_block_protocols(block):
    all_stim = SortedDict()
    blocks = RecordingBlock.objects.filter(pk=block.pk)
    blk_stim = get_available_protocols(blocks, 'protocolrecording__stimulus')
    protocols = ProtocolRecording.objects.filter(block__in=blocks)
    ptc_stim = get_available_protocols(protocols, 'stimulus') 
    for blk_stim, blk_count in blk_stim['names'].items() :
        all_stim[blk_stim] = SortedDict()
        all_stim[blk_stim]['experiments'] = blk_count
        ptc_count = ptc_stim['names'][blk_stim]
        all_stim[blk_stim]['protocols'] = ptc_count
    return all_stim

def get_block_statistics(block):
    statistics = SortedDict()
    statistics['stim_protocols'] = get_block_protocols(block)
    qset = RecordingBlock.objects.filter(pk=block.pk)
    statistics['methods'] = get_recording_methods(qset)
    return statistics

@memorise_last_page
@memorise_last_rendered_page
def block_detail(request, lab, expt, block, *args, **kwargs):
    laboratory = ScientificStructure.objects.get(diminutive=lab)
    experiment = Experiment.objects.get(label=expt)
    blk = RecordingBlock.objects.get(experiment=experiment, label=block)
    files = blk.get_files_and_status_by_protocol_types(request.user)
    protocols = blk.get_protocols_by_type()
    configurations = blk.configurations
    context = {'experiment':experiment, 'lab':laboratory, 'blk':blk, 'protocols':protocols, 'files':files, 'configurations':configurations, 'user':request.user}
    if kwargs.has_key('get_statistics') and kwargs['get_statistics'] :
        statistics = get_block_statistics(blk)
        context['statistics'] = statistics
    return render_to_response(kwargs["template"], context)

def get_recording_methods_for_traces(protocol):
    all_methods = SortedDict()
    protocols = ProtocolRecording.objects.filter(pk=protocol.pk)
    ptc_methods = get_available_methods(protocols, 'signal__configuration__configuration')
    signals = Signal.objects.filter(protocol__in=protocols)
    trc_methods = get_available_methods(signals, 'configuration__configuration')
    for ptc_method, ptc_count in ptc_methods['names'].items() :
        all_methods[ptc_method] = SortedDict()
        all_methods[ptc_method]['protocols'] = ptc_count
        if trc_methods['names'].has_key(ptc_method) :
            trc_count = trc_methods['names'][ptc_method]
        else :
            trc_count = 0
        all_methods[ptc_method]['traces'] = trc_count
    return all_methods

@memorise_last_page
@memorise_last_rendered_page
def protocol_detail(request, lab, expt, block, protocol, *args, **kwargs):
    laboratory = ScientificStructure.objects.get(diminutive=lab)
    protocol = ProtocolRecording.objects.get(label=protocol, block__label=block, block__experiment__label=expt)
    status = protocol.file.download_status_key(request.user)
    is_accessible = is_accessible_by(protocol.file, request.user)
    context = {'lab':laboratory, 'protocol':protocol, 'user':request.user, 'status':status, 'is_accessible':is_accessible}
    statistics = SortedDict()
    statistics['methods'] = get_recording_methods_for_traces(protocol)
    context['statistics'] = statistics
    return render_to_response(kwargs["template"], context)

@memorise_last_page
@memorise_last_rendered_page
def signal_detail(request, lab, expt, block, protocol, file, episode, channel, *args, **kwargs):
    laboratory = ScientificStructure.objects.get(diminutive=lab)
    file = File.objects.get(name=file)
    signal = file.signal_set.get(electricalsignal__episode=int(episode), electricalsignal__channel__number=int(channel)).cast()
    context = {'lab':laboratory, 'signal':signal, 'user':request.user}
    if signal.analyses.count() :
        duration = signal.analyses.get(input_of__label__icontains="duration").input_of.get().outputs.get().cast().value
        minimum = signal.analyses.get(input_of__label__icontains="min").input_of.get().outputs.get().cast().value
        maximum = signal.analyses.get(input_of__label__icontains="max").input_of.get().outputs.get().cast().value
        peak_to_peak = signal.analyses.get(input_of__label__icontains="p2p").input_of.get().outputs.get().cast().value
        amplitude = signal.analyses.get(input_of__label__icontains="amplitude").input_of.get().outputs.get().cast().value
        mean = signal.analyses.get(input_of__label__icontains="mean").input_of.get().outputs.get().cast().value
        standard_deviation = signal.analyses.get(input_of__label__icontains="std").input_of.get().outputs.get().cast().value
        root_mean_squared = signal.analyses.get(input_of__label__icontains="rms").input_of.get().outputs.get().cast().value
        variance = signal.analyses.get(input_of__label__icontains="var").input_of.get().outputs.get().cast().value
        context["duration"] = duration
        context["minimum"] = minimum
        context["maximum"] = maximum
        context["peak_to_peak"] = peak_to_peak
        context["amplitude"] = amplitude
        context["mean"] = mean
        context["standard_deviation"] = standard_deviation
        context["root_mean_squared"] = root_mean_squared
        context["variance"] = variance
    return render_to_response(kwargs["template"], context)
