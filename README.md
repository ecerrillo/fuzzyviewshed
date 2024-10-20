Fuzzy Viewshed Calculator
This project implements a Fuzzy Viewshed Calculator that uses a Digital Elevation Model (DEM) to calculate viewsheds with fuzzy logic principles. The calculation of fuzzy viewsheds follows the methodology proposed by Ogburn, D. E. (2006). Assessing the level of visibility of cultural objects in past landscapes. Journal of Archaeological Science, 33(3), 405-413. https://doi.org/10.1016/j.jas.2005.08.005

The program uses a DEM and a vector layer of polygons as input. The program iterates through each of the polygons in the vector file, calculating the fuzzy viewshed for each one. The maximum width of the polygon is extracted from the geometry of each polygon, and the observed position is taken from the centroid of the polygon. Additionally, a maximum visibility radius and the observer's height can be specified. By default, the calculation of the area of greatest clarity (b1) is set to 1000 meters, following Ogburn (2006).

Features

- Calculate fuzzy viewsheds based on a DEM
- Apply Euclidean distance masks for maximum viewshed extent
- Process polygon vector files for multiple viewpoint calculations, extracting from them the maximum width and the observed position.

Installation

Clone this repository:
git clone https://github.com/your-username/fuzzy-viewshed-calculator.git
cd fuzzy-viewshed-calculator

Install the required dependencies:
pip install -r requirements.txt

Usage
See examples/example_usage.py for a demonstration of how to use the FuzzyViewshedCalculator.

Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

License
This project is licensed under the MIT License - see the LICENSE file for details.
