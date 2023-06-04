<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

## RAlchemist (Recipe Alchemist)
A toolset for digital recipe management and meal planning.
- organize a digital recipe collection, 
- import recipes
- simplify your meal plans
- and more!


### Getting Started
1. Clone the repo | ```git clone git@github.com:jessex7/Ralchemist.git```
2. Build the container | ```sudo docker build -t ralchemist .```
3. Run the container | ```sudo docker run -p 80:80 -t ralchemist```
4. Confirm that 127.0.0.1:80/recipes returns a json list of recipes