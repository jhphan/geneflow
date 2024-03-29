# GeneFlow

Version: 3.0.0-alpha.1

GeneFlow (GF) is a light-weight, extendable workflow engine for scientific computing.

## Requirements

At a minimum, GeneFlow requires a Linux environment with Python 3. The Python pip installer for GeneFlow handles all python dependencies.

## Quick Start

General installation instructions can be found in the [Additional Documentation](#additional-documentation).

### Install GeneFlow in a Python Virtual Environment

If you need to install GeneFlow, it is recommended to use a Python3 virtual environment. However, if you have root access and want to install GeneFlow system-wide, you may skip the virtual environment step.

1.  Create and activate a Python3 virtual environment:

    ```
    python3 -m venv gfpy
    source gfpy/bin/activate
    ```

2.  Clone the GeneFlow source repository:

    ```
    git clone https://github.com/jhphan/geneflow
    ```

3.  Install GeneFlow:

    ```
    pip3 install ./geneflow
    ```

4.  Test the installation by running the GeneFlow CLI:

    ```
    geneflow --help
    ```

## Additional Documentation

Additional documentation can be found [here](https://geneflow.gitlab.io/). Alternatively, it can be found in the docs folder of this source repository (or by following this link: [Additional Documentation](docs/index.rst)). 

## License

The repository utilizes code licensed under the terms of the Apache Software
License and therefore is licensed under ASL v2 or later.

This source code in this repository is free: you can redistribute it and/or modify it under
the terms of the Apache Software License version 2, or (at your option) any
later version.

This source code in this repository is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the Apache Software License for more details.

You should have received a copy of the Apache Software License along with this
program. If not, see http://www.apache.org/licenses/LICENSE-2.0.html

The source code forked from other open source projects will inherit its license.
