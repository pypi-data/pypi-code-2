#encoding:utf-8
from copy import deepcopy
from django.utils.datastructures import SortedDict
from django.shortcuts import render_to_response
from django.db.models import Q
from django.views.generic.list_detail import object_list
from helmholtz.core.schema import cast_queryset
from helmholtz.core.shortcuts import cast_object_to_leaf_class
from helmholtz.core.decorators import memorise_last_page,memorise_last_rendered_page
from helmholtz.experiment.models import Experiment
from helmholtz.recording.tools.filters import get_available_methods,get_available_preparations,get_available_protocols
from helmholtz.recording.models import RecordingBlock,ProtocolRecording
from helmholtz.drug_applications.models import Injection,Perfusion
from helmholtz.people.models import Researcher,ScientificStructure
from helmholtz.signals.models import Signal
from helmholtz.storage.models import File
from helmholtz.preparations.models import Animal,EyeCorrection,AreaCentralis
from helmholtz.species.models import Species

def get_recording_methods(experiments):
    all_methods = SortedDict()
    exp_methods = get_available_methods(experiments,'recordingblock__recordingconfiguration__configuration')
    blocks = RecordingBlock.objects.filter(experiment__in=experiments)
    blk_methods = get_available_methods(blocks,'recordingconfiguration__configuration')
    protocols = ProtocolRecording.objects.filter(block__in=blocks)
    ptc_methods = get_available_methods(protocols,'signal__configuration__configuration')
    signals = Signal.objects.filter(protocol__in=protocols)
    trc_methods = get_available_methods(signals,'configuration__configuration')
    for exp_method,exp_count in exp_methods['names'].items() :
        all_methods[exp_method] = SortedDict()
        all_methods[exp_method]['experiments'] = exp_count
        blk_count = blk_methods['names'][exp_method]
        all_methods[exp_method]['blocks'] = blk_count
        if ptc_methods['names'].has_key(exp_method) :
            ptc_count = ptc_methods['names'][exp_method]
        else :
            ptc_count = 0
        all_methods[exp_method]['protocols'] = ptc_count
        if trc_methods['names'].has_key(exp_method) :
            trc_count = trc_methods['names'][exp_method]
        else :
            trc_count = 0
        all_methods[exp_method]['traces'] = trc_count
    return all_methods

def compute_animal_statistics(experiments,animals,statistics):
    statistics['quantity'] = animals.count()
    statistics['male'] = animals.filter(sex='M').count()
    statistics['female'] = animals.filter(sex='F').count()
    species = Species.objects.filter(strain__animal__preparation__experiment__in=experiments).distinct()
    statistics['species'] = SortedDict()
    for sp in species :
        statistics['species'][sp] = animals.filter(strain__species=sp).distinct().count()

def get_protocols(experiments):
    all_stim = SortedDict()
    exp_stim = get_available_protocols(experiments,'recordingblock__protocolrecording__stimulus')
    blocks = RecordingBlock.objects.filter(experiment__in=experiments)
    blk_stim = get_available_protocols(blocks,'protocolrecording__stimulus')
    protocols = ProtocolRecording.objects.filter(block__in=blocks)
    ptc_stim = get_available_protocols(protocols,'stimulus') 
    for exp_stim,exp_count in exp_stim['names'].items() :
        all_stim[exp_stim] = SortedDict()
        all_stim[exp_stim]['experiments'] = exp_count
        blk_count = blk_stim['names'][exp_stim]
        all_stim[exp_stim]['blocks'] = blk_count
        ptc_count = ptc_stim['names'][exp_stim]
        all_stim[exp_stim]['protocols'] = ptc_count
    return all_stim

def get_experiment_preparation_statistics(experiments):
    #preparations = Preparation.objects.filter(experiment__in=experiments).distinct()
    statistics = get_available_preparations(experiments,'preparation')
    return statistics

def get_experiment_animal_statistics(experiments):
    statistics = SortedDict()
    animals = Animal.objects.filter(preparation__experiment__in=experiments).distinct()
    compute_animal_statistics(experiments,animals,statistics)
    return statistics

def get_experiments_statistics(experiments):
    #statistics
    statistics = SortedDict()
    statistics['experimenters'] = Researcher.objects.filter(experiment__in=experiments).distinct().count()
    statistics['files'] = File.objects.filter(signal__protocol__block__experiment__in=experiments).distinct().count()
    statistics['traces'] = Signal.objects.filter(protocol__block__experiment__in=experiments).distinct().count()
    statistics['methods'] = get_recording_methods(experiments)
    statistics['stim_protocols'] = get_protocols(experiments)
    #experiments
    statistics['experiments'] = experiments.count()
    blocks = RecordingBlock.objects.filter(experiment__in=experiments)
    statistics['blocks'] = blocks.count()
    protocols = ProtocolRecording.objects.filter(block__in=blocks)
    statistics['protocols'] = protocols.count()
    statistics['animals'] = get_experiment_animal_statistics(experiments)
    statistics['preparations'] = get_experiment_preparation_statistics(experiments)
    return statistics

def get_experiment_statistics(experiment):
    statistics = SortedDict()
    qset = Experiment.objects.filter(pk=experiment.pk)
    statistics['methods'] = get_recording_methods(qset)
    statistics['stim_protocols'] = get_protocols(qset)
    blocks = RecordingBlock.objects.filter(experiment__in=qset)
    statistics['blocks'] = blocks.count()
    protocols = ProtocolRecording.objects.filter(block__in=blocks)
    statistics['protocols'] = protocols.count()
    return statistics

@memorise_last_page
@memorise_last_rendered_page
def experiment_list(request,lab,*args,**kwargs):
    laboratory = ScientificStructure.objects.get(diminutive=lab)
    #filtering the queryset to keep experiments done by lab and teams
    q1 = Q(setup__place__parent__diminutive=lab)
    q2 = Q(setup__place__diminutive=lab)
    kw = deepcopy(kwargs)
    kw['queryset'] = kw['queryset'].filter(q1|q2).distinct() 
    context = {'lab':laboratory,'user':request.user}
    if kw.has_key('get_statistics') and kw['get_statistics'] :
        kw.pop('get_statistics')
        statistics = get_experiments_statistics(kw['queryset'])
        context['statistics'] = statistics
    kw['extra_context'].update(context)
    return object_list(request,*args,**kw) 

@memorise_last_page
@memorise_last_rendered_page
def experiment_detail(request,lab,expt,*args,**kwargs):
    laboratory = ScientificStructure.objects.get(diminutive=lab) 
    experiment = Experiment.objects.get(label=expt)
    all_eye_corrections = EyeCorrection.objects.filter(preparation=experiment.preparation)
    all_area_centralis = AreaCentralis.objects.filter(preparation=experiment.preparation)
    perfusions = Perfusion.objects.filter(experiment=experiment)
    injections = Injection.objects.filter(experiment=experiment)
    preparation_experiments = experiment.preparation.experiment_set.exclude(pk=experiment.pk)
    animal_experiments = Experiment.objects.filter(preparation__animal=experiment.preparation.animal).exclude(pk=experiment.pk).distinct()
    context = {'experiment':experiment,
               'lab':laboratory,
               'all_eye_corrections':all_eye_corrections,
               'all_area_centralis':all_area_centralis,
               'perfusions':perfusions,
               'injections':injections,
               'user':request.user,
               'preparation_experiments':preparation_experiments,
               'animal_experiments':animal_experiments,
               'observations':cast_queryset(cast_object_to_leaf_class(experiment.preparation).observations.all(),'FloatMeasurement'),#filter(preparation__experiment=experiment).distinct(),
    }
    if kwargs.has_key('get_statistics') and kwargs['get_statistics'] :
        statistics = get_experiment_statistics(experiment)
        context['statistics'] = statistics
    return render_to_response(kwargs['template'],context)