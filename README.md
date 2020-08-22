# pager
Pager take home


Setup instructions:

This assumes you already have a Selenium standalone Chrome docker container
running and available on port `4444`. If you don't, you can spin one up with
this command:

```
docker run -d -p 4444:4444 -v /dev/shm:/dev/shm -e TZ=America/New_York selenium/standalone-chrome:4.0.0-alpha-6-20200730
```

The `-e TZ=America/New_York` is essential so the times are rendered in sync
with the host machine's timezone. If you aren't in that timezone, you can find
the complete list
[here](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

Python dependencies are managed by `poetry`. Once you have poetry installed, you
can use it to create the virtual environment and to install the dependencies
like so (assumes python 3.8 is installed, but I believe it can be substituted
with 3.6):

```
# create a python 3.8 environment
poetry env use python3.8
# install the dependencies
poetry install
# run the tests
poetry run python -m pytest
```

Several design decisions were made while writing these tests, and unfortunately,
several sacrifices had to be made, so my ideal testing approach was not
attainable in the time alloted, and likely not possible due to numerous
constraints (e.g. minified JS on the frontend).

In general, I had the following motivations:
* Involve the browser as little as possible to reduce confounding variables and speed up
  executionn time
* Build out comprehensive, and proper abstractions to speed up development
  * I had already made `PyPCOM` myself some years ago, which is a form of
    composition/facade pattern, and it was immeasurably useful for this
    (especially considering the advanced iterable example I laid out in its
    documentation
    [here](https://pypcom.readthedocs.io/en/latest/advanced/iterables.html))
* Only test state-changing actions. Non-state-changing queries have no behaviors
  tied to them, and are to only used as a means of introspection the resulting
  state in order to evaluate whether or not its as expected.

Some tests were marked with `refined` while others were marked with `unrefined`.
Those marked as `refined` were fairly lean and fairly strict with their pass
conditions, even though they could probably be optimized much further. But those
marked as `unrefined` made excuses so they could pass and involved far more than
they needed to to test the core behavior they were meant to (browsers are
incredibly expensive).

I also tried to follow the Law of Demeter for the most part.

Regarding the style and structure of my tests, a comprehensive writeup for why
exactly I laid them out this way can be found
[here](https://salmonmode.github.io/2019/03/29/building-good-tests.html).

Pytest specifically was used because of it's incredibly powerful fixture system.

A docker-compose file was not included because the above docker command and
subsequent poetry commands are all that is necessary to run this, so the
docker-compose file would be pretty bare, and the docker file for the tests
would more or less be copying and pasting those poetry commands.
