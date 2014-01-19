This project has people from all difference backgrounds, and hopefully even wider exposure than that. This glossary is to be kept up to date with any terms that anyone stumbles over in the course of working this out.

Use h3s (###) to mark words, so that GitHub linkifies them and we can easily reprocess this file into a sorted and publishable pdf or latex file.

### XYZ
Refers to the chunking used to make displaying webmaps tolerable: a raster is divied up into tiles covering the globe (or whatever other surface in whatever coordinate system you're in love with). Z is the zoom level, X and Y are the horizontal and vertical coordinates (usually corresponding to longitude and latitude)

For example of XYZ sources, try looking at:
* OSM:
  * http://b.tile.openstreetmap.org/4/9/7.png (**format**: Z/X/-Y)
  * http://b.tile.openstreetmap.org/4/9/8.png
  * http://b.tile.openstreetmap.org/4/9/9.png and
* MapQuest
  * http://otile3.mqcdn.com/tiles/1.0.0/osm/4/12/5.jpg (**format**: Z/X/Y)

### widget


### cadastral
 of issues of ownership, as in "cadastral data for the GTA"
 
### vector
  For our purposes, refers to the computer graphics meaning of vector, not the linear algebra one: a 'vector' is a data structure giving a piece of geometry: either a point, a line, or a polygon (which is a list of lines that circles back and connects to itself). Sometimes fonts come in a vector format, where other types of curves (eg bezier, spline, ...) are data options, but those types are not relevant for us. Vectors have the advantages of maintaining perfect location and shape at any zoom level, and that they give algorithms--like pathfinding--something meaningful to latch onto and work with, and the disadvantage that some objects, like roads or hospitals, are only approximately lines or points

### raster
  In contrast to vector data, rasters record information on a grid. Sometimes also called 'bitmap'; you probably know this type of data as 'tiff', 'jpg', 'png', where the grid units are called "pixels" (or px). For mapping purposes, GeoTIFF, which is .tiff augmented with latitude and longitude or something equivalent, is a common backend format, often produced from arial photographs or remote sensing satellites. For frontend rendering, all the online map services render their full datasets to several big global rasters, one for each zoom level, and provide them in small (~80x80px) chunks as the frontend needs them. Rasters have the advantage of being able to represent fields and gradients: there is no meaningful way to work out temperature, rainfall, or pollutant concentration with vectors.

### geodetic datum
 e.g. NAD83, UTM

### confidence
 See [[Confidence & Uncertainty]]