Planetary Build System
======================

[![Build Status](https://travis-ci.org/NacionLumpen/pbs.svg)](https://travis-ci.org/NacionLumpen/pbs)

The Planetary Build System (PBS) is a build system that looks up any function
or method that you have implemented in software community websites before
building the source code into machine code. PBS looks up the documentation
comments that you have supplied with your implementation, and shows to you on
build how the community answer to that development task would look like. You
can mark your implementation as 'reviewed' if you have already integrated the
suggestions in your code, or do not care.

The Planetary Build System is called as it is because, if an equivalent
infrastructure was in place and used by every software project, all developers
working on an Internet-connected computer would effectively be working on the
same library of functions.

The Planetary Build System is at a (very early) proof of concept stage.
Currently, it only supports building C projects, written in K&R style,
docummented with doxygen syntax, and implemented in a single directory.

## Installation

You can download this repository, and then issue:

    $ python setup.py install

## Usage

After installation, you will have a new command, `pbs`, which can be used from
any directory where your project to be built resides. There is an example
project in this repository, under `pbs/tests/example/`.

    $ cd pbs/tests/example/simple/
    $ pbs
    INFO:root:Found this answer for procedure int main(int argc, const char *argv[])
     described as 'How to make a no-op':
     #include <iostream>
    
    #ifdef NOOP
        #define conditional_noop(x)
    #else
        #define conditional_noop(x) std::cout << (x)

Notice that the exact output may vary, depending on the available answers on
community websites.

If you have already reviewed the community answers for one of your functions,
and have either integrated the answer or rejected it as irrelevant to your
case, you can avoid `pbs` from repeating the lookup by marking the function as
reviewed. This is done by adding `@pbs: reviewed` to the doxygen comment on any
function.

```c
/**
 * How to make a no-op
 *
 * @pbs: reviewed
 */
int main(int argc, const char *argv[])
{
    return 0;
}
```

## License

The MIT License (MIT)

Copyright (c) 2015 Luis Osa

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
