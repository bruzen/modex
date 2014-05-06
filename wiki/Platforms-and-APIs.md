Here we list all the APIs and platforms we have considered. It is a serious time sink to research the suitability of a platform, so with the reasons we have kept or rejected, or put  each on hold.


# Frontend

HTML5 is extremely powerful. It has a lot of new widgets (under form elements: sliders, numbers, dates, file uploaders, also <progress> and <meter> which lists). We can probably build most of our widgets direct in HTML.

* LessCSS
* craftyjs?
* [TogetherJS](https://togetherjs.com/) by Mozilla for adding commenting throughout a site
* [Modernizr](http://modernizr.com/) to let us write one codebase against HTML5

* Promises: [overview of some of the better implementations](http://www.promisejs.org/implementations/) / [a different site??](http://promisesaplus.com/implementations)
  * ayepromise (**<-- current**)
  * when.js
  * promise.js
  * ....

**Layout Templates**
* [Boilerplate](http://html5boilerplate.com/)
* [Bootstrap](http://getbootstrap.com/)

## Visualization

* d3js
* Square's [cubism.js](http://square.github.io/cubism/) for visualizing live time series data
* Square's [cube](http://square.github.io/cube/)
* [graphite](http://graphite.wikidot.com/)
* Native HTML5 (e.g. see [our html5 widget demo](../../scratch/html5/widgets))
* Spreadsheet widgets (more [@](http://plugins.jquery.com/tag/spreadsheet/))
    * [Handsontable](http://handsontable.com/)

### Encapsulated Visualization Libraries

* [Mike Bostock's Reusable d3 chart spec](http://bost.ocks.org/mike/chart/)
  * and the [official results](https://github.com/d3/d3-plugins), so far 
  * 
* [dimplejs](http://dimplejs.org/) - _this looks pretty underpowered_
* [Vega](https://github.com/trifacta/vega)
  * [Vincent](https://github.com/wrobstory/vincent) - _A Python to Vega translator_
* [NVD3](http://nvd3.org/)
* [Miso](http://misoproject.com/)   - _this one looks super promising_
* [DexCharts](https://github.com/PatMartin/DexCharts)
* [Flot](http://www.flotcharts.org/)
* [Chart.JS](http://www.chartjs.org/)
* Scrap reusable d3 examples:
  * http://jsfiddle.net/johnwun/8hSGP/
  * [textrotate()](http://bl.ocks.org/ezyang/4236639)
  * [pie-chart](https://github.com/gajus/pie-chart)
  * [interactive histograms](https://github.com/gajus/interdependent-interactive-histograms)
  * ["slopegraph"](http://bl.ocks.org/biovisualize/4348024) (actually a very basic network visualization)
  * [demo of building a reusable component from a nonreusable one](http://bl.ocks.org/milroc/5519642)
  * [messy errorbar scatterplot](http://bl.ocks.org/chrisbrich/5044999)
  * ["hello world" in reusable d3](http://bl.ocks.org/cpbotha/5073718)
  * [simple bar chart](http://jsfiddle.net/johnwun/8hSGP/)


### Maps

* OpenLayers: [2](http://openlayers.org) and [3](http://ol3js.org)
  * we should see if we can divert some part of our budget to them: http://www.indiegogo.com/ol3
* http://tilestache.org/
* http://polymaps.org/
* [ModestMaps](http://modestmaps.com/examples/)
(_these all seem like they overlap a bit; what's the deal?_)

**Map Data** _is complicated_
* TopoJSON
* GeoJSON
* [MapFish](http://trac.mapfish.org/trac/mapfish/wiki/MapFishProtocol), for [CRUD](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete) operations.
* [OpenLayers' Discussion on approaches to giving different results at different zoom levels](https://github.com/openlayers/ol3/pull/1812) (and [related PR](https://github.com/openlayers/ol3/pull/1744)


## Networking

* [WebSockets](http://www.websocket.org/quantum.html)
  * Autobahn
    * Tutorials do not work at this time. Re-evaluating our use of Autobahn.
  * [SockJS-twisted](https://github.com/DesertBus/sockjs-twisted/); see also [SockJS-client](https://github.com/sockjs/sockjs-client) for drop-in websocket support for older browsers
  * [twisted.web.websockets](https://twistedmatrix.com/trac/ticket/4173) is in [the works](http://twistedmatrix.com/trac/attachment/ticket/4173/4173-5.patch), but not ready yet
  * [ws4py](https://github.com/Lawouach/WebSocket-for-Python)
  * [cherrypy](http://www.cherrypy.org/)
  * [txWS](https://github.com/MostAwesomeDude/txWS)
  * [socket.io](http://socket.io/)
      * [python API](http://gevent-socketio.readthedocs.org/)
      * [other python API](https://github.com/MrJoes/tornadio2)
  * [JSON-RPC](https://en.wikipedia.org/wiki/JSON-RPC) is dead simple and worth investigatign

* [EventSource](http://stackoverflow.com/questions/8499142/html5-server-side-event-eventsource-vs-wrapped-websocket)
* jsonp



## Javascript Data View/Flow/Binding Libraries  (an obscene number of them)

Since our problem is so data-centric, not using data-binding will be a giant pain of always writing new update handlers. 

A data bind and a data flow are related problems, and several of these libraries solve them together. A data _bind_ is when some object (something in-memory or output like a visualization widget or a slider) is marked as being a consumer of some other object, and they are kept in sync. A data _flow_ is a chain of dependent computations; most useful of all is a flow over a series of binds (_think: Microsoft Excel, which lets you edit any non-formula cell and then reupdated all dependent cells automatically; and that is **really, really useful**_)

**Question**: do we support bidirectional binds? Bidirectional binds are much much much harder than unidirectional; the alternative is to manually expose an API for everything modifiable (and this is safer, because is gaurds against accidentally making a model--which is more likely than not written quick-and-dirty--inconsistent)

* [LavaJS](http://lava.codeplex.com/) - _this one is promising; it is small and claims to be unobtrusive
* http://jqxb.codeplex.com/
* [Knockout](http://knockoutjs.com/); 
  * rave reviews [here](http://blog.stevensanderson.com/2010/07/05/introducing-knockout-a-ui-library-for-javascript/) and [here](http://visualstudiomagazine.com/articles/2012/02/01/2-great-javascript-data-binding-libraries.aspx)
  * supports functional definitions of quantities--quantities that get recomputed as the underlying data updates
* [jsViews](https://github.com/BorisMoore/jsviews) seems to be jQuery's official plugin to do this 
* [simpli5](https://github.com/jacwright/simpli5) is a bigger thing, but it [features data-binding](http://jacwright.com/438/javascript-data-binding/). It hasn't had an update in 4 years, though (perhaps jQuery superseded it?). Regardless, we can pick through it (and the others) for ideas.; [its magic](https://github.com/jacwright/simpli5/blob/master/src/binding.js) is mostly done with js's built in ```__lookupSetter__```
* Square's [Crossfilter](http://square.github.io/crossfilter/)
* Miso's [Dataset](http://misoproject.com/dataset/)
* Vega's [Triflow](https://github.com/trifacta/triflow/tree/master/test) - _not actually sure if this is a dataflow library; it seems to too tiny to do anything; maybe it's just clever - nick_
* [AngularJS](https://docs.angularjs.org/guide/databinding) includes databinding as a feature
* [BackboneJS](http://backbonejs.org/)
* [Model.JS](https://github.com/curran/model) (new, but written by someone with extensive d3 experience; he even wrote [an intro to AngularJS](http://curran.github.io/screencasts/introToAngular/exampleViewer/#/)
* [BaconJS](http://baconforme.com/) (clear tutorial [here](http://blog.flowdock.com/2013/01/22/functional-reactive-programming-with-bacon-js/))



# Backend


### Servers


* Twisted
* Django?
* flask
  * klein

### Webby stuff:

* Jinja2==2.7.1
* MarkupSafe==0.18
* Werkzeug==0.9.4
* klein==0.2.1

### Utils

* [PIL](http://pillow.readthedocs.org/) for generating and working with rasters

### Video??

* ??? ?? ? ? ?

### Databases

* Python APIs: [Overview](https://wiki.python.org/moin/DatabaseInterfaces), [SQL](https://wiki.python.org/moin/DbApiModuleComparison) which conform to [PEP 249](http://legacy.python.org/dev/peps/pep-0249/), [ORMs &c](https://wiki.python.org/moin/HigherLevelDatabaseProgramming) of which [SQLAlchemy](http://www.sqlalchemy.org/) is head of the pack.
* [Dee](http://www.quicksort.co.uk/DeeDoc.html) which overloads python operators to create a superset of SQL directly in Python
* postgres with the postgis extension
* [PyTables](http://www.pytables.org/moin) which eschews SQL in favour of hdf5's optimized idea of what a database is.
* [Cubes](http://cubes.databrewery.org/) which wraps SQL into OLAP _**pay attention** to this one_

### Interfaces

* [RPy](http://rpy.sourceforge.net/rpy2.html) and its child [rmagic](http://ipython.org/ipython-doc/dev/config/extensions/rmagic.html) to hook out
* Jython to wrap java code??




## Patterns
* REST
* Pub/Sub
* Events
* Declarative (e.g. d3)

## Modelling
* Repast
* GarlicSIM
* [SimPy](http://simpy.readthedocs.org/)
* [PyABM](http://www-rohan.sdsu.edu/~zvoleff/research/pyabm/) (canonical usage example [here](https://github.com/azvoleff/chitwanabm/blob/master/chitwanabm/agents.py))
  * check out [what wikipedia thinks](http://en.wikipedia.org/wiki/Comparison_of_agent-based_modeling_software) to be bored to tears
* [ABCE](https://github.com/DavoudTaghawiNejad/abce) _Agent Based Complete Economy_ (python); [paper](http://jasss.soc.surrey.ac.uk/16/3/1.html)
* http://insightmaker.com/
* [Liam2](http://liam2.plan.be/pages/about.html)

## Packaging

* [py2exe](http://www.py2exe.org/) - _specialized for Windows, runs as a distutils extension_
* [freeze.py](https://wiki.python.org/moin/Freeze) - _specialized for Unix; not used that much anymore, since most Unices have good package managers these days_
* [PyInstaller](http://pyinstaller.org/)  - _cross-platform python packaging_

(nick thinks we should rely on system-specific packaging conventions as much as possible, e.g. try to get our work into brew, pacman, aptitude and the Windows 8 and OS X App Stores)

## Tools

* [GeoHack](https://tools.wmflabs.org/geohack/) (all lat/lon coordinates on Wikipedia link to GeoHack)
* [MapBox Collaboratory](https://www.mapbox.com/)

## Collaboratories 

Collaboraties (laboratories for collaboration) are our key to reproducible science.

* [StackExchange](http://stackoverflow.com/) - _they've thought long and hard -- and have measured -- about the right way to do comment systems; the link escapes me right now, though -kousu_

* [DIY.org](http://diy.org/)
* [jsFiddle](http://jsfiddle.net) -- [example](http://jsfiddle.net/sharavsambuu/s7QjN/9/light/)
* [Tributary.IO](https://github.com/enjalot/tributary.io): Rapid Collaborative D3 Prototyping
* [SSVD](https://www.icpsr.umich.edu/icpsrweb/ICPSR/ssvd/index.jsp) - _this is both a data archive and a great example of including tools (in this case crosstabs) online and in the browser__

* asana.com -- project management
* github
* academia.edu??
* 

* [nbviewer](http://nbviewer.ipython.org/) which lets scientific people show off their [ipython notebooks](http://ipython.org/notebook.html), like [this one](http://nbviewer.ipython.org/urls/raw2.github.com/damontallen/Orbitals/master/Hydrogen%20Orbitals%20-%20working.ipynb)

### Dataset Management

* http://dat-data.com 
* http://datahub.io
* (there's at least two other dataset-version-control/archival sites; what are they?)
* https://exversion.com
* [FigShare](http://figshare.com/)

### Citation Management
* http://www.zotero.org/
* http://www.mendeley.com/


## Blogs
* wordpress
* mezzanine (on django)
