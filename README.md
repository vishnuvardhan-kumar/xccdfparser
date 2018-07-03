# xccdfparser

Extensible parser for [XCCDF](https://en.wikipedia.org/wiki/XCCDF) Benchmark/Result XML files.

`pip install xccdfparser`

Produces a human-readable JSON from an incomprehensible XCCDF schema/result file:

For every TestResult tag in the input file,

- Benchmark Details
    - Benchmark ID
    - Rule ID
    - Title/Description
    - Fixtext

- Dictionary
    - Metadata
        - Timestamp
        - Target Machine
        - IP address(es)
        - XCCDF Domain
    - Results
        - Rule ID
        - Value
  
To run the parser on a file input.xml, just use:

`xccdfparser -o output.json input.xml`

OR

`xccdfparser input.xml`


### Testing xccdfparser

To test the pre-built tox environments:

First, install tox if you don't have it:

`pip install tox`

Then in the package directory:

`tox`

Or for a specific environment:

`tox -e py36`

