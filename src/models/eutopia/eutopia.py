#!/usr/bin/env python2
# this program requires python2 because GDAL requires python2

# system libs
import os, warnings

import random
import json

# third party
import dataset

# local libs
from simulationlog import *
import pygdal
from util import *

# eutopia files
import activity
import intervention

HERE = os.path.abspath(os.path.dirname(__file__))


#######################
## Model Overview
#
#
# state:
#  Farms - a set of georeferenced polygons containing (id, soil_type, county, activity, {some other stuff that we ignore})
#        MAP_CODE is the type of farming done on that land (which might not strictly be farming. Activities like lying fallow or running a jungle gym are possible) 
#  FarmFamily - an agent which has (bank_account, preferences)
#  
#  
# interventions:
# Upon the substrate of model state, Eutopia gives the user the power to
# manipulate things like tax rates, new farming (or otherwise) activities, new equipment
# We call these "interventions" and they operate by
# (TODO: this part hasn't actually been properly spec'd yet; there are arguments to have)
# 
# logged state:
#  - every Farm's (activity, soil status, ...?)
#  - every FarmFamily (bank account, farms <-- requires a separate table...)
#  - the current value of aggregate_measures (TODO: doing this cleanly requires cleaning up Activity first and dealing with the Normal()s in there which are in the wrong place)
#  - activity counts
#
# future plans:
# Farms will grow SOIL_TYPE
# A Farmer class, which is born into a FarmFamily, moves, perhaps inherits farms from their parents, dies
#
#
#
#
#######################

#######################
## Exports

# from ourselves
__all__ = ['Farm', 'FarmFamily', 'Eutopia'] #XXX should we maybe only export "Eutopia" and just ask users to access Farms via Eutopia?
__all__ += ['create_demo_model']            #for testing (only(?))

# from intervention.py
from intervention import *    # put into local namespace for reexport
                              # users of Eutopia need to be able to create Interventions that Eutopia understands,
                              # so they need to have these symbols available.
__all__ += ['PriceIntervention', 'NewActivityIntervention'] 

# from activity.py
from activity import Activity  #ditto #XXX this is probably not super well designed.
__all__ += ['Activity']


#######################
## eutopia

MAP_SHAPEFILE = os.path.join(HERE, "Elora_esque.shp.zip") #not in the repo due to copyright; ask a team member
# TODO: test with passing a folder instead

AGRICULTURE_CODES = { #hardcoded out of the ARI dataset
   #non-agriculture features are commented out
   'C': 'CORN SYSTEM',
   #'B': 'BUILT UP',
   'G': 'GRAZING SYSTEM',
   'PC': 'PEACHES-CHERRIES',
   'H': 'HAY SYSTEM',
   'M': 'MIXED SYSTEM',
   'MG': 'GRAIN SYSTEM',
   'KM': 'MARKET GARDENS/TRUCK FARMS',
   'KN': 'NURSERY',
   'P': 'CONTINUOUS ROW CROP',
   #'A1': 'IDLE AGRICULTURAL LAND (5-10 YEARS)',
   #'A2': 'IDLE AGRICULTURAL LAND (OVER 10 YEARS)',
   #'W': 'WATER',
   #'X': 'SWAMP, MARSH OR BOG',
   #'R': 'RECREATION',
   #'Z': 'WOODLAND',
   #'E1': 'EXTRACTION PITS AND QUARRIES',
   #'HG': 'PASTURE SYSTEM',
   #'ZR': 'REFORESTATION'
}

SOIL_TYPES = [ #more than you ever wanted to know at http://sis.agr.gc.ca/cansis/taxa/cssc3/index.html
    "CLAY",
    "PEAT",
    "LOAM",
    "CHRERNOZEM", #aka "black earth" e.g. Holland Landing
    "SAND"
]

class Farm: #(pygdal.Feature): #inheritence commented out until we determine if it's a good idea or not
                               #the trouble comes down to that I want to have a copy constructor:
                               # I want to say Farm(map.getsomefeature())
                               # but a native ogr.Feature needs to be ogr.Feature(ogr.FeatureDefn(...)) which is all sorts of pain
                               # For now, we clone only the given feature's geometry, which is all we are using at the moment
    def __init__(self, feature):
        #pygdal.Feature.__init__(self, feature)
        self.geometry = feature.GetGeometryRef() #instead of trying to muck with inheritence, just use get a pointer to the geometry and ignore the columns
        
        self.soil_type = random.choice(SOIL_TYPES) #TODO: pull from a real dataset
        self.county = "BestCountyInTheWorldIsMyCountyAndNotYours"
        self._activity = self.last_activity = None
        
        (self.long, self.lat) #..uh oh. for some reason we need to access (and memoize) these here, or else gdal segfaults
        #print(self.lat, self.long)
    
    def get_activity(self):
        return self._activity;
    
    def set_activity(self, value):
        self.last_activity, self._activity = self._activity, value;
    
    activity = property(get_activity, set_activity)
    
    @property
    @memoize
    def lat(self):
        return self.geometry.Centroid().GetY() 

    @property
    @memoize #fun fact: memoizing this function saves 700 times the calls
             #          --nearly 3 orders of magnitude-- as of this commit.
    def long(self):
        return self.geometry.Centroid().GetX()

    @property
    def area(self): return self.geometry.Area()
    
    def ExportToJSON(self):
        # hand-rolled export function
        # Until we figure out a consistent and efficient way to handle time-varying shapefiles,
        # this will do to only export the properties which are actual geofeature properties (as distinct from the helpers that make the model easier to write)
        
        return json.dumps(
        {"type": "Feature",
         "geometry": json.loads(self.geometry.ExportToJSON()), #XXX ridiculously inefficient
         "properties":
            {"activity": self.activity,
             "soil_type": self.soil_type,
             "county": self.county}})

class FarmFamily:
    def __init__(self, eutopia):
        self.eutopia = eutopia
        self.farms = []
        self.bank_balance = 1000000.00
        self.equipment = []
        self.preferences = {'money': 1.0, 
                            'follow_society':0.1,  # how important is following what everyone else is doing
                            'follow_local':0.2,    # how important is doing what my neighbours are doing
                            }

    def add_farm(self, farm):
        self.farms.append(farm)
        farm.family = self

    def make_planting_decision(self, activities, farm):
        all_activities = dict(self.eutopia.latest_activity_count)
        total_activities = float(sum(all_activities.values()))
        if total_activities > 0:
            for k,v in all_activities.items():
                all_activities[k]/=total_activities

        if self.preferences.get('follow_local', 0) != 0:
            local_activities = self.eutopia.get_activity_count(farm.neighbours)
            total_activities = float(sum(local_activities.values()))
            if total_activities > 0:
                for k,v in local_activities.items():
                    local_activities[k]/=total_activities


        


        best = None
        for activity in activities:
            total = 0
            for pref, weight in self.preferences.items():
                if pref=='follow_society':
                    total += all_activities.get(activity.name,0) * weight
                elif pref=='follow_local':
                    if weight != 0:
                        total += local_activities.get(activity.name,0) * weight
                else:
                    total += activity.get_product(pref, farm) * weight
                # TODO: improve choice algorithm
                #    - maybe by allowing different sensitivities to risk
                #      on different income dimensions

            
            if best is None or total > best_total:
                best = activity
                best_total = total

        return best


    def step(self):
        for farm in self.farms:
            # changed to self.eutopia to make it work with the sim version that is passed to Family21
            activity = self.make_planting_decision(self.eutopia.activities.activities, farm)

            money = activity.get_product('money', farm)
            self.bank_balance += money

            farm.last_activity = activity



class Eutopia:
    """
    The Eutopic World
    The main simulation class
    There is an API here for controlling and querying the model state
    """
    def __init__(self, log = None):
        self.log = log
        if self.log is None:
            self.log = "sqlite://" #creates an in-memory database object
        if isinstance(self.log, str):
            self.log = dataset.connect(self.log)
        else:
            if not isinstance(self.log, dataset.Database):
               warnings.warn("Eutopia log should be a dataset.Database object.") #only warn, don't crash, to allow for users doing funky mocking stuff that an explicit type check would miss; What I really want here is to assert on an Interface, like Java/C# or Twisted.
        
        try:
            shapefile = pygdal.Shapefile(MAP_SHAPEFILE)
        except IOError:       #py2.7
            #except FileNotFoundError: #py3k
            raise RuntimeError("No shapefile `%s` found; you may need to download it from a team member (privately)" % MAP_SHAPEFILE)

        self.map = shapefile[0] #cheating: assume the only layer we care about is this one
        assert self.map.GetGeomType() == pygdal.wkbPolygon, "Farm boundaries layer is not a Polygon; it is a" + str.join(" or ", pygdal.invertOGRConstants(self.map.GetGeomType()))
        #assert isinstance(self.map, pygdal.PolygonLayer), "Farm boundaries layer is not a Polygon; it is a " + str(type(self.map))

        #########################
        # modelling begins here
        self.time = 0
        self.activities = activity.Activities()
        self.interventions = []

        #XXX should we write this as literally constructing a new Layer?
        # for now, a List is alright, but it's worth thinking about doing that and about what pygdal requires to support doing that
        self.farms = [Farm(f) for f in self.map if f.MAP_CODE in AGRICULTURE_CODES.keys()]
        print("Constructed", len(self.farms), "farms", "out of", len(self.map), "features")

        self.families = []
        # for now, every Family goes with one single Farm on it
        for farm in self.farms:
            family = FarmFamily(self)
            family.add_farm(farm)
            self.families.append(family)

        for farm in self.farms:
            farm.neighbours = self.get_local_farms(farm.lat, farm.long, count=10)

    def dumpsMap(self):
        "convert the map data to a GeoJSON string"
        "meant to be used in a ModelExplorer endpoint"
        return self.map.dumps()
    
    def dumpMap(self, fname):
        "write the loaded map data to a file"
        "this function is cruft, but very useful cruft"
        with open(fname,"w") as mapjson:
            mapjson.write(self.dumpsMap())
    
    def __next__(self):
        # apply interventions
        for intervention in self.interventions:
            if self.time >= intervention.time:
                intervention.apply(self, self.time)

        # run model
        self.latest_activity_count = self.get_activity_count()
        for family in self.families:
            family.step()
        self.time += 1

        # log metrics
        self.record("activities", **self.get_activity_count()) #XXX this will flop across allllll the columns; is that what we want?
        #self.record("activities", [{"activity": a, "value": v} for a,v in self.get_activity_count().iteritems()]) #this rearranges the dictionary into two columns, which is more SQLish; dataset makes either one transparent to us, though
        
    def record(self, table, many=None, **state):
        "log model 'state' into 'table' in database self.log"
        "if many is given, state should be empty"
        #XXX 'many' is sketchy! It only really exists because of table layout "version 2";
        # I can't make up my mind to keep it or not.
        
        table = self.log[table] #dataset constructs a new table here for us if needed
                
        def labelit(d): #XXX bad name
            "label a row of state with the current run ID and the current time"
            d = d.copy() #XXX this copy is a safety measure, but it is wasteful for this particular use case
            d.update({"runID": -1}) #TODO: this should be outside of the model, like say in the Simulation class? hm. awkward!
            d.update({"time": self.time}) #TODO: make some uber update method which logs every piece of "current" state and then incremements the timestep 
            return d
            
        if many is None:
            table.insert(labelit(state))
        else:
            assert not state, "`many` and `**state` are mutually exclusive" #XXX sketchy
            assert all(isinstance(e, dict) for e in many)
            table.insert_many([labelit(e) for e in many])
    
    next = __next__ #backwards compatibility with python2
    step = __next__ #backwards compat with ourselves

    def intervene(self, intervention):
        self.interventions.append(intervention)

    def __iter__(self):
        "convenience method"
        while True:
            next(self)
            yield self.get_activity_count() #hardcode model output, for now #XXX this is senseless now that we have a database in place

    def get_activity_count(self, farms = None):
        "return a dictionary containing the current value of each economic activitiy"
        if farms is None: farms = self.farms
        activities = {}
        for farm in farms:
            if farm.last_activity is not None:
                name = farm.last_activity.name
                if name not in activities:
                    activities[name] = 1
                else:
                    activities[name] += 1
        return activities

    def get_local_farms(self, lat, long, count):
        "collect the 'count' closest farms to coordinates (lat, long)"
        dist = [((lat-f.lat)**2 + (long-f.long)**2, f) for f in self.farms]
        dist.sort()
        return [d[1] for d in dist][:count]

    def get_local_activity_count(self, farm, count):
        return self.get_activity_count(self.get_local_farms(farm.lat, farm.long, count))


def create_demo_model():
    """
    Construct Eutopia under a specific scenario.
    
    This subroutine is useful as a benchmark for using Eutopia under different hosts.
    """
    eutopia = Eutopia()
    
    eutopia.intervene(intervention.PriceIntervention(5, 'duramSeed', 10))
    eutopia.intervene(intervention.PriceIntervention(7, 'duramSeedOrganic', 0.001))

    """
    magic_activity = {
        'equipment': ['tractor', 'wheelbarrow'],
        'products': {
            'duramSeed': -5,
            'nitrogen': -10,
            'carbon': 20,
            'soil': -5,
            'labour': -2000,
            'certification': 0,
            'duram': 42,
            'dolphin': -87,
            }
        }
    eutopia.intervene(intervention.NewActivityIntervention(7, 'magic', magic_activity))
    """
    return eutopia


def main(n=20, dumpMap=False):
    """
    Run Eutopia with some default interventions, and plot the results if matplotlib is installed.
    
    args:
      n: number of timesteps to run
      dumpMap: whether to export the map to a topojson file
    
    TODO:
      [ ] make __main__ parse command line params and pass them as the args to main()
        [ ] Then, document how to use --dumpMap to reconstruct /assets/maps/elora.topo.json from this Elora_esque.shp.zip.real
    """
    
    eutopia = create_demo_model()

    if dumpMap:
        #write the map data from GDAL out to topojson
        # TODO: move this to the `scripts/` folder
        eutopia.dumpMap("elora.geo.json")
        os.system("topojson elora.geo.json -o elora.topo.json")
        print("Finished exporting map data to elora.topo.json")
    
    #run the model
    print("Simulating Eutopia:")
    for t in range(n):
        print ("Timestep %d" % (t,))
        next(eutopia)

    #version 1: flopping activities across columns; so the list of distinct activities is the list of columns minus the metadata columns
    activities = [act for act in eutopia.log['activities'].columns if act not in ["id", "runID", "time"]]
    #version 2: using one column "activity" to store the activities
    #activities = list(e['activity'] for e in eutopia.log['activities'].distinct("activity"))
    

    # display results
    print("Farm activities over time:")
    #print(list(eutopia.log['activities'].all()))
    #print(eutopia.log['activities'].columns)
    #import IPython; IPython.embed()
    # Now, reading the data is awkward because we use raw Python
    # If we installed Pandas (which is not unreasonable, given that we care about stats and dataset manipulation)
    # the cruft would get hidden (and probably run faster too, since Pandas has been tuned)
    for act in activities:

        # (version 1 is in some ways "ugly sql" but it makes very pretty tables and is actually easier to work with! )
        # Version 1: flopping activities across columns
        timeseries = [r[act] for r in eutopia.log['activities'].find(order_by="time")]
        # Version 2: a more normalized sql form, where we essentially embed a dictionary into a table
        #timeseries = [r["value"] for r in eutopia.log['activities'].find(activity=act, order_by="time")]
        
        print(act, ":", timeseries)
        
    
    
    # optional: display summary of model outputs
    # automatically kicks in if matplotlib is installed
    try:
        import pylab
        print("Plotting activities with matplotlib:")
        for act in activities:
            
            # (version 1 is in some ways "ugly sql" but it makes very pretty tables and is actually easier to work with! )
            # Version 1: flopping activities across columns
            timeseries = [r[act] for r in eutopia.log['activities'].find(order_by="time")]
            # Version 2: a more normalized sql form, where we essentially embed a dictionary into a table
            #timeseries = [r["value"] for r in eutopia.log['activities'].find(activity=act, order_by="time")]
            
            pylab.plot(range(len(timeseries)), timeseries, label=act)
            pylab.xlabel("time")
            pylab.ylabel("activity")
        
        pylab.legend(loc='best')
        pylab.show()   #block here until the user closes the plot    
    except ImportError:
        print "It appears you do not have scipy's matplotlib installed. Though the simulation has run I cannot show you the plots."
    except RuntimeError, e: #this crashes on the off chance you're not running X; not a big deal, but notable, so a less-scary warning to the user
        print e.message, "=> unable to show plots."
        
    print("good bye!")

if __name__=='__main__':
    main()
