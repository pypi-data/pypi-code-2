"""
:class:`CRAReader`
------------------
.. autoclass:: CRAReader

:class:`CRA2009`
----------------
.. autoclass:: CRA2009
    :show-inheritance:

:class:`CofogMapper`
--------------------
.. autoclass:: CofogMapper
"""
import os, sys, csv, re
from datetime import date, datetime
try: import json
except ImportError: import simplejson as json

import datapkg, datapkg.util
import pkg_resources
from ordf.command import Command

from wdmmg.vocab.cra import ProgrammeObjectGroups, ExpenditureTypes
from wdmmg.vocab.cra import CountryAndRegionalAnalysis
from wdmmg.vocab.entity import Entities

from unstats.cofog import Functions
from eurostat.nuts import Regions
from ukgov.reference.time import GovYear

from ordf.vocab.sdmx import DataSet, DataStructureDefinition, Observation, TimeSeries
from ordf.vocab.void import Dataset as VoidDataset
from ordf.graph import ConjunctiveGraph, Graph, ReadOnlyGraphAggregate
from ordf.namespace import Namespace
from ordf.namespace import DC, RDF, RDFS, FOAF, OWL, SKOS, SDMX, TIME, \
    SDMX, SDMXDIM, SDMXATTR, SDMXCODE, \
    GOVYEAR, PUB, ENT, UKCUR, \
    CRA, CRADSD, CRADATA, REGION, POG, COFOG
from ordf.term import BNode, Literal, URIRef
from ordf.collection import Collection
from telescope import Select, v
from ordf.handler import init_handler

log = __import__("logging").getLogger(__name__)

class CofogMapper(object):
    '''
    Constructs a COFOG mapper from a mappings object (which is usually loaded
    from a JSON file).

    In the published data, the "function" and "subfunction" columns are used
    inconsistently. This is partly because some departments continue to use a
    previous coding system, and partly because only two columns have been
    allowed for the three levels of the COFOG hierarchy.
    
    This class uses a mapping provided by William Waites to work out the
    correct COFOG code, given the published data.

    :param mappings:
        a list of triples. In each triple, the first element is the good
        code, and the second and third elements give the published values.
        If the first element (the good code) contains non-numerical suffix,
        it will be removed.

    .. automethod:: fix
    '''
    def __init__(self, mappings):
        '''
        
        '''
        self.mappings = {}
        for good, bad1, bad2 in mappings:
            good = re.match(r'([0-9]+(\.[0-9])*)', good).group(1)
            self.mappings[bad1, bad2] = good
    
    def fix(self, function, subfunction):
        '''
        Looks up the fixed COFOG code given the published values.
        
        Returns a list giving all available COFOG levels, e.g.
        `[u'01', u'01.1', u'01.1.1']`

        Returns an empty list if no COFOG mapping has been
        defined.

        :param function: 
            function as expressed by HMT
        :param subfunction:
            subfunction as expressed by HMT
        '''
        ans = self.mappings.get((function, subfunction))
        if ans is None:
            return []
        parts = ans.split('.')
        return ['.'.join(parts[:i+1]) for i, _ in enumerate(parts)]

class CRAReader(object):
    """
    A specialised CSV reader for the CRA that takes a datapkg dataset
    and datafile and yields dictionaries for each row with the values
    cleaned. Once initialised, this class is an iterable.

    At the time of writing this requires the current version of
    datapkg from the mercurial repository. The package metadata is
    included in this python module. You can see the available datasets
    by doing::

        % datapkg list egg://ukgov_treasury_cra
        cra2009 -- Country and Regional Analysis 2009 - CSV

    Example usage of this class:

    .. code-block:: python
    
        from pprint import pprint
        reader = CRAReader(cache_dir, "cra2009", "cra_2009_db.csv")
        for row in reader:
            pprint(row)
            ...

    output:

    .. code-block:: python

        {'body_type': u'CG',
         'cap_or_cur': u'CUR',
         'cofog_parts': [u'04', u'04.1', u'04.1.2'],
         'dept_code': u'Dept032',
         'dept_name': u'Department for Work and Pensions',
         'expenditures': [(u'2003-2004', 0.0),
                          (u'2004-2005', 0.0),
                          (u'2005-2006', 0.0),
                          (u'2006-2007', 0.0),
                          (u'2007-2008', 0.0),
                          (u'2008-2009', 12100000.0),
                          (u'2009-2010', 12100000.0),
                          (u'2010-2011', 12100000.0)],
          'pog_code': u'P37 S121211',
          'pog_name': u'ADMIN COSTS OF MEASURES TO HELP UNEMPL PEOPLE MOVE FROM WELFARE T...',
          'region': u'SCOTLAND'}

    :param cache_dir:
        Cache directory where the downloaded data will live. A datapkg
        filesystem index is created here
    :param dataset:
        The name of the dataset to be downloaded, e.g. "cra2009"
    :param datafile:
        The filename of the downloaded data within the dataset, e.g.
        "cra_2009_db.csv"
    :param year_col_start:
        The column in the datafile where the actual expenditures begin, 
        after the metadata columns.

    .. automethod:: getdata
    .. automethod:: header
    .. automethod:: cleandata
    .. automethod:: make_cofog_mapper
    .. automethod:: get_department
    .. automethod:: get_cofog_parts
    .. automethod:: get_pog
    .. automethod:: get_cap_or_cur
    .. automethod:: get_body_type
    .. automethod:: get_region
    .. automethod:: get_expenditures
    """
    # the name of the present python package, which is used as a datapkg
    # egg index for looking up the source of the data.
    index_name = "ukgov_treasury_cra"

    def __init__(self, cache_dir, dataset, datafile, year_col_start=10):
        self.cache_dir = cache_dir
        self.dataset = dataset
        self.datafile = datafile
        self.year_col_start = year_col_start
        self.cofog_mapper = self.make_cofog_mapper()

    def make_cofog_mapper(self):
        """
        Create a COFOG mapper used in cleaning the data. This is a method
        to provide for easy subclassing where a different mapper is required.
        """
        # Make a CofogMapper.
        fp = pkg_resources.resource_stream(__name__, os.path.join("data", "cofog_map.json"))
        mappings = json.load(fp)
        fp.close()
        return CofogMapper(mappings)

    def __iter__(self):
        # Get the CRA data package.
        source = "egg://%s" % os.path.join(self.index_name, self.dataset)
        cached = 'file://%s' % os.path.join(self.cache_dir, self.index_name, self.dataset)
        fp = self.getdata(source, cached, self.datafile)

        reader = csv.reader(fp)
        header = reader.next()
        self.header(header)

        for row in reader:
            if not row[0]:
                continue # Skip blank row.
            yield self.cleandata(row)

        fp.close()

    def getdata(self, source, cached, datafile):
        """
        Returns an open file handle pointing at the data file
        that we want to read. This copies perhaps too much
        from datapkg's "install" command implementation and
        should probably be part of the datapkg API.

        :param source:
            source index and dataset specification, e.g.
            *"egg://ukgov_treasury_cra/cra2009"*
        :param cached:
            destination to cache the data, also index and
            dataset specification, e.g.
            *"file:///tmp/ukgov_treasury_cra/2009"*
        :param datafile:
            filename within the dataset to open. e.g.
            *"cra_2009_db.csv"*
        """
        # slightly inefficient to initialise all of these here, but
        # it makes the code more readable even if they're not always
        # used
        cached_spec = datapkg.spec.Spec.parse_spec(cached)
        cached_index, dataset = cached_spec.index_from_spec()
        source_spec = datapkg.spec.Spec.parse_spec(source)
        source_index, dataset = source_spec.index_from_spec()
        
        # first step - try to pull the package from datapkg. if it
        # doesn't exist we'll get either a DatapkgException or an
        # I/O error here
        try:
            pkg = datapkg.load_package(cached)
        except Exception, e:
            if not isinstance(e, OSError) and not isinstance(e, datapkg.DatapkgException):
                raise # better syntax for this?
            pkg = source_index.get(dataset)
            cached_index.register(pkg)
            pkg = cached_index.get(dataset)

        # second step, open our file handle. if this fails with an
        # I/O error it means the file hasn't been downloaded yet
        # (or the disc has bad sectors)
        try:
            fp = pkg.stream(datafile)
        except IOError:
            install_path = os.path.join(cached_index.index_path, pkg.name)
            log.info("downloading %s to %s" % (dataset, install_path))
            downloader = datapkg.util.Downloader(install_path)
            downloader.download(pkg.download_url)
            fp = pkg.stream(datafile)

        return fp

    def header(self, header):
        """
        Extracts fiscal years from the header columns. Also sets an 
        instance property "year_col_start" that is used by the 
        :meth:`cleandata` meth to find the column where actual 
        expenditure data is kept.
        """
        # Utility function for formatting tax years.
        def to_year(s):
            y = int(s[:4])
            return u'%4d-%4d' % (y, y+1)
        self.years = [to_year(x) for x in header[self.year_col_start:]]
        
    def cleandata(self, row):
        """
        Cleans and normalises an input row, turns it into a dictionary.
        This uses the various :meth:`get_*` methods to extract individual
        parts for easy subclassing. This method starts out with an
        empty collector dictionary and looks for methods with names that begin
        with *get_* and calls them with the row as an argument. The
        return value of these functions is expected to be a dictionary
        that is used to update the collector.

        :returns:
            A dictionary representing the data in the row.
        """

        data = {}

        row = [unicode(x.strip()) for x in row]

        for attr in dir(self):
            if not attr.startswith("get_"):
                continue
            data.update(getattr(self, attr)(row))
        return data

    def get_department(self, row):
        """
        Extracts the department code and name from the first two columns
        of the row.

        :returns: 
           A dictionary with keys *"dept_code"* and *"dept_name"*
        """
        return {"dept_code": row[0], "dept_name": row[1]}

    def get_cofog_parts(self, row):
        """
        Extracts the COFOG from the function and subfunction fields,
        columns 2 and 3 in the 2009 data. Passes them through the 
        :class:`CofogMapper`.

        :returns:
            A dictionary with the key *"cofog_parts"* and value a list
            ordered from least to most specific classification.
        """
        function = row[2]
        subfunction = row[3]
        # Map 'function' and 'subfunction' to three levels of COFOG.
        cofog_parts = self.cofog_mapper.fix(function, subfunction)
        assert cofog_parts, 'COFOG code is missing for (%s, %s)' % (function, subfunction)
        assert len(cofog_parts) <= 3, 'COFOG code %r has too many levels' % cofog_parts
        assert len(cofog_parts) > 0, 'COFOG code not found for %s' % (function, subfunction)
        return {"cofog_parts": cofog_parts}

    def get_pog(self, row):
        """
        Extracts the Programme Object Group from the columns 4 and 5.

        :returns:
            A dictionary with keys *"pog_code"* and *"pog_name"*
        """
        pog_code = row[4]
        pog_name = row[5]
        if pog_name != pog_code and pog_name.startswith(pog_code):
            pog_name = pog_name[len(pog_code):].lstrip(" ")
        return {"pog_code": pog_code, "pog_name": pog_name}

    def get_cap_or_cur(self, row):
        """
        Extracts the flag indicating capital or current expenditure from
        column 7.

        :returns:
            A dictionary with the key *"cap_or_cur"* and the value either
            *"CAP"* or *"CUR"* as applicable.
        """
        cap_or_cur = row[7]
        assert cap_or_cur in ("CAP", "CUR"), "Unknown value for cap_or_cur: %s" % cap_or_cur
        return {"cap_or_cur": cap_or_cur}

    def get_body_type(self, row):
        """
        Extracts the type of reporting entity from column 8.

        :return:
           A dictionary with the key *"body_type"* and the value can be
           one of:

             * *"CG"* -- Central Government
             * *"LA"* -- Local Authority
             * *"PC"* -- Public Corporation
        """
        body_type = row[8]
        assert body_type in ("CG", "LA", "PC"), "Unknown body type: %s" % body_type
        return {"body_type": body_type}

    def get_region(self, row):
        """
        Extract the region from column 9 of the row.

        :returns:
            A dictionary with the key *"region"*.
        """
        return {"region": row[9]}

    def get_expenditures(self, row):
        """
        Extract the yearly expenditures from the row. This makes use of
        the :attr:`year_col_start` class attribute to determine at which
        column to begin.

        :returns:
            A dictionary with the key "expenditures and value a list of 
            two-tuples representing fiscal year and the reported expenditure
            value
        """
        # Utility function for parsing numbers.
        def to_float(s):
            if not s: return 0.0
            return float(s.replace(',', ''))
        expenditures = [round(1e6*to_float(x)) for x in row[self.year_col_start:]]
        return {"expenditures": zip(self.years, expenditures)}

        
class CRA2009(Command):
    """
    This class implements the :ref:`cra2009` command that loads the CSV
    file from the treasury and transforms it to RDF, placing the results
    in a triplestore managed by :mod:`ordf.handler.rdf`. See the documentation
    in the command-line utilities section of the manual for usage instructions.

    .. attribute:: edition

        This class attribute may be changed by subclasses implementing a command
        for other editions of the CRA data. The value here is the string "2009".
        This is used both to derive the dataset and datafile that will be used
        as well as to set the RDF namespace for the generated data. If the 2010
        data is made available in a file called 'cra_2010_db.csv' and has exactly
        the same form as the 2009 data, then creating a command for manipulating
        the new edition should be as simple as:

        .. code-block:: python

            class CRA2010(CRA2009):
                edition = "2010

        and adding the appropriate entry points and 'datapkg_sources' to the
        'setup.py' file.

    .. attribute:: store

        An RDFLib compatible store, gleaned from the :class:`ordf.handler.Handler`
        that will be used for saving the data.

    .. attribute:: entries

        This property is created by :meth:`create_sdmx_dataset` and contains
        the python object representing the sdmx:DataSet.

    .. attribute:: components

        This property is also created by :meth:`create_sdmx_dataset`. It 
        is a list of the types for each dimension that should be included when 
        constructing the URI for timeseries.

    .. automethod:: load_schema
    .. automethod:: create_sdmx_dataset
    .. automethod:: create_sdmx_timeseries
    """
    parser = Command.StandardParser()
    parser.add_option("-s", "--schema",
                      dest="load_schema",
                      action="store_true",
                      default=False,
                      help="Also load the schema")
    edition = "2009"

    def command(self):
        if hasattr(self.handler, "fourstore"):
            self.store = self.handler.fourstore.store
        elif hasattr(self.handler, "rdflib"):
            self.store = self.handler.rdflib.store
        else:
            raise AttributeError("Require either RDFLib of 4store configured")

        if self.options.load_schema:
            self.load_schema()

        # initialise the classes and concept schemes that we will
        # use to construct the entries dataset
        self.govyear = GovYear(Graph(self.store, identifier=GOVYEAR[""]), load=True)
        self.entities = Entities(graph=Graph(self.store, identifier=ENT[""]))
        self.regions = Regions(Graph(self.store, identifier=REGION[""]))
        self.functions = Functions(Graph(self.store, identifier=COFOG[""]))
        self.pogs = ProgrammeObjectGroups(Graph(self.store, identifier=POG[""]))
        self.exps = ExpenditureTypes()
        # don't need to specify the graph for these ones because we make a
        # new graph for each time series/row
        self.obs = Observation()
        self.timeseries = TimeSeries()

        # this is used to flag an observation as provisional (in the year
        # of publication of the CRA) or as future
        self.current_year = datetime(2009, 4, 1, 0, 0, 0)
        
        # create the container for the timeseries in this dataset
        self.create_sdmx_dataset()

        dataset = "cra%s" % self.edition
        datafile = "cra_%s_db.csv" % self.edition

        reader = CRAReader(self.config["cache_dir"], dataset, datafile)
        for row in reader:
            self.create_sdmx_timeseries(row)
            break

        print ConjunctiveGraph(self.store).serialize(format="n3")
        for x in self.store.contexts():
            print x

    def load_schema(self):
        """
        Load the CRA schema and supporting information into the RDF 
        datastore
        """
        def _load(func):
            for s in func():
                g = Graph(self.store, identifier=s.identifier)
                g += s
        from unstats import cofog
        from eurostat import nuts
        _load(nuts.rdf_data)
        _load(cofog.rdf_data)

    def create_sdmx_dataset(self):
        """
        Define the structure for the entries dataset, this is at the
        most granular level reflecting what data is directly in the
        cra CSV file. The result of calling this function is to create
        the following graphs in the RDF store:

          * a *sdmx:DataSet*
          * a *sdmx:DataStructureDefinition* describing the dimensions and
            attributes of the data in the daset

        This method sets the :attr:`entries` and :attr:`components` 
        properties on this class.
        """
        dsd = DataStructureDefinition()
        entriesdsd = dsd.get(CRADSD["%s/entries" % self.edition])
        entriesdsd.type = dsd.identifier
        entriesdsd.component = SDMXDIM.refPeriod
        entriesdsd.component = SDMXATTR.unitMeasure
        entriesdsd.component = CRA.entity
        entriesdsd.component = CRA.region
        entriesdsd.component = CRA.function
        entriesdsd.component = CRA.pog
        entriesdsd.component = CRA.expenditureType
        entriesdsd.component = CRA.obsStatus
        # collections not handled very prettily at the moment
        _head = BNode()
        entriesdsd.graph.add((entriesdsd.identifier, SDMX.componentOrder, _head))
        order = Collection(entriesdsd.graph, _head)
        order.append(CRA.entity)
        order.append(CRA.region)
        order.append(CRA.function)
        order.append(CRA.pog)
        order.append(SDMXDIM.refPeriod)
        # so needed to circumvent *delete* that the collection does, save
        # now to store fully constructed
        _dsd = Graph(self.store, identifier=entriesdsd.identifier)
        _dsd += entriesdsd.graph
    
        # create the SDMX dataset containing the entries, referencing the
        # structure
        dataset = DataSet()
        entries_ident = CRADATA["%s/entries" % self.edition]
        self.entries = dataset.get(entries_ident, Graph(self.store, identifier=entries_ident))
        self.entries.label = Literal("UK Country and Regional Analysis, %s Edition, Entries" % self.edition, 
                                     lang="en")
        self.entries.structure = entriesdsd

        # link it to the top dataset
        crads_ident = CRADATA[self.edition]
        crads = VoidDataset().get(crads_ident, Graph(self.store, identifier=crads_ident))
        crads.subset = self.entries

        # extract the key order for constructing the urls for individual
        # timeseries later
        self.components = []
        for component in Collection(entriesdsd.graph, order):
            q = Select([v.range], distinct=True).where(
                (component, RDFS.range, v.range)
                )
            self.components.extend(ConjunctiveGraph(self.store).query(q.compile()))

    def create_sdmx_timeseries(self, row):
        """
        Given a row in the form of a dictionary from :class:`CRAReader`, create
        a graph containing an *sdmx:TimeSeries* in the store.
        """
        from pprint import pprint
        #pprint(row)

def cra2009():
    cmd = CRA2009()
    cmd.command()

def drop():
    '''
    Drops from the database all records associated with slice 'cra'.
    
    XXX this will be hard to duplicate in the RDF version
    '''

def load_file(fileobj, cofog_mapper):
    '''
    Loads a file from `fileobj` into the RDF store.
    The file should be CSV formatted, with the same structure as the 
    Country Regional Analysis data.
    
    fileobj - an open, readable file-like object.
    '''
    # get a hold of the RDFLib store, we bypass most of the ORDF
    # machinery here
    handler = init_handler(config)
    if hasattr(handler, "fourstore"):
        store = handler.fourstore.store
    else:
        store = handler.rdflib.store

    # used for simple unoptimised queries over the entire store
    defaultgraph = ConjunctiveGraph(store)
    
    # For each line of the file...
    reader = csv.reader(fileobj)
    header = reader.next()
    year_col_start = 10
    years = [to_year(x) for x in header[year_col_start:]]

    # read through the input and construct the timeseries
    for row in reader:

        #
        # ROW PARSED - NOW CONSTRUCT THE RDF
        #
        print dept_name, cofog_parts[-1], pog_code, expenditures
    
        # get handles for each of the dimensions in the row
        _region = regions.byName(region)
        if _region is None:
            raise KeyError("Missing Region: %s" % region)
        _function = functions.byFog(cofog_parts[-1])
        if _function is None:
            raise KeyError("Missing COFOG: %s" % cofog_parts)
        _ent = entities.byName(dept_name)
        if _ent is None: 
            raise KeyError("Missing Entity: %s" % dept_name)
        # pog will never be none since they are created 
        # on the fly as needed
        _pog = pogs.setdefault(pog_code, pog_name)
        # exp will raise a key error itself if cap_or_cur is invalid
        _exp = exps.byKey(cap_or_cur)

        # given the dimensions, calculate the path elements for the URI
        # of the series from our component list in the DSD
        def series_path(components):
            path = []
            for component in components:
                if component in _ent.cached_types:
                    path.append(_ent.notation[0])
                elif component in _region.cached_types:
                    path.append(_region.notation[0])
                elif component in _function.cached_types:
                    path.append(_function.notation[0])
                elif component in _pog.cached_types:
                    path.append(_pog.notation[0])
                elif component in _exp.cached_types:
                    path.append(_exp.notation[0])
            return "/".join(path).replace(" ", "")

        # make the time series, or slice
        series_id = URIRef(CRADATA["2009/entries/"] + series_path(components))
        series_ns = Namespace(series_id + "#")
        series = timeseries.get(identifier=series_id, graph=Graph(store, identifier=series_id))

        # add the dimensions present in the data, theoretically these
        # could go in a flattened way on the observation itself below,
        # bhtat that wouldn't be so efficient and we can always do that
        # later
        series.addDimension(CRA.region, _region.identifier)
        series.addDimension(CRA.entity, _ent.identifier)
        series.addDimension(CRA.pog, _pog.identifier)
        [series.addDimension(CRA.function, COFOG[x]) for x in cofog_parts if x]
        series.addDimension(CRA.expenditureType, _exp.identifier)
        series.graph.add((series.identifier, SDMX.dataSet, CRADATA["2009/entries"]))

        # special flag just in case
        if function.find("of which") >=0 or subfunction.find("of which") >= 0:
            series.graph.add((series.identifier, CRA.owf, CRA.OfWhich))

        print "Time Series:", series.identifier

        for yearSpec, amount in zip(years, expenditures):
            if amount == 0.0:
                continue
            datum = obs.get(identifier = series_ns[yearSpec], graph=series.graph)
            datum.addValue(Literal(amount), UKCUR.GBP)
            year = govyear.get(yearSpec)
            if year.start == current_year:
                datum.addDimension(SDMXATTR.obsStatus, SDMXCODE["obsStatus-P"]) # provisional
            elif year.end > current_year:
                datum.addDimension(SDMXATTR.obsStatus, SDMXCODE["obsStatus-F"]) # future
            datum.addDimension(SDMXDIM.refPeriod, year.identifier)
            series.observation = datum
            print "\tDatum:", datum.identifier

        entries.series = series

# testing output
#        entries.serialize(series.graph)
#        _region.serialize(series.graph)
#        _pog.serialize(series.graph)
#        _exp.serialize(series.graph)
#
#        print series.graph.serialize(format="n3")
#        break
