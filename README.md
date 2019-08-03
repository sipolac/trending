# trending
A simple method for determining trending-ness. It's a problem I started thinking about when working at Zillow, where the "hotness" of neighborhoods was of interest. I realized there wasn't a simple, generalized way to detect recent growth in a time series that didn't involve a number of hand-chosen parameters. So I came up with this method, which has just one parameter that can be chosen intuitively based on how much weight you want to put on more recent observations.

The code for computing recent growth uses no libraries outside of the set of standard Python 3 libraries.

Please see [demo](https://github.com/sipolac/trending/demo.ipynb).
